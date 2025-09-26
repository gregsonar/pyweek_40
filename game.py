import json
import pathlib
import random

from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, look_at
from ursina import *
from ursina import Entity, Text, Ursina, camera
from ursina.prefabs.platformer_controller_2d import PlatformerController2d
from ursina.lights import PointLight, DirectionalLight, AmbientLight
from ursina.shaders import lit_with_shadows_shader

from handlers.sfx_handler import Sfx_handler  # todo: импортировать music_handler из pw_38
from spritesheet_loader import SpritesheetLoader

DEBUG_MODE = True  # Отключить перед сборкой
PRESSED_KEYS = False


class WindowCleanerPlayer(PlatformerController2d):
    """Расширенный контроллер для мойщика окон - унаследован от заготовки 2d актора для платформеров в Урсине"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.y = 1.5  # спавним чуть-чуть в воздухе, чтобы не проваливаться сквозь люльку
        # Настройки анимации:
        self.to_y_angle = 0 # поворот вокруг своей оси (лицом к камере)
        self.jump_height = 1.5
        self.jump_duration = 0.3
        self.currentanim = 'None'
        self.newanim = 'Idle'
        self.movepressed = 0
        self.move_locked = False # флаг для блокировки перемещений

        # UI элементы
        self.speech_bubble = Text()  # todo: перенести болталку из pw_38
        self.head_mark = Entity()
        self.current_interaction_object = False
        self.ready_to_interact = True

        # Для мытья окон
        self.cleaning_range = 2.0
        self.current_target_window = None

    def input(self, key):
        # системы управления из оригинального кода (СЛОМАНО, переделать!)
        if held_keys['d'] or held_keys['a']:
            self.newanim = 'Walk'
        else:
            self.newanim = 'Idle'

        if key == 'e':
            # Пробуем помыть окно
            self.to_y_angle = 180  # todo: дорабоать подробнее
            work_animations = ['Victory', 'Punch', 'SwordSlash']  # названия анимаций жестко записаны в .gltf модели
            self.newanim = random.choice(work_animations)
            self.try_clean_window()

        if key == 'space':
            self.jump()
            self.newanim = 'Jump'
            self.move_locked = True

        if key == 's':
            self.newanim = 'Idle'
            self.to_y_angle = 0
            self.movepressed = 0
            # self.move_locked = True

        if key == 'd' and not self.move_locked:
            self.velocity = .5
            self.to_y_angle = -90
            self.movepressed += 1

        if key == 'a' and not self.move_locked:
            self.velocity = -.5
            self.to_y_angle = 90
            self.movepressed += 1

        # todo: починить движение при нажатии нескольких клавиш
        if key == 'a up' and not self.move_locked:
            self.movepressed -= 1
        if key == 'd up' and not self.move_locked:
            self.movepressed -= 1
        if key == 's up':
            self.move_locked = False
            self.movepressed = 0

        if self.movepressed <= 0:
            self.velocity = 0

        if self.movepressed < 0:
            self.movepressed = 0

    def try_clean_window(self):
        """Попытка помыть окно"""
        if self.current_target_window and self.current_target_window.is_dirty:
            # Простая проверка расстояния
            distance = distance_2d(self.position, self.current_target_window.position)
            if distance <= self.cleaning_range:
                self.current_target_window.start_cleaning()
                return True
        return False

    def update(self):
        super().update()

        # ---- Блок запуска анимации ----
        if self.newanim == 'Jump':
            self.model.play('Jump', fromFrame=10)

            # Если уже приземлились — выбираем анимацию по удерживаемым клавишам
            if self.grounded:
                self.move_locked = False
                if held_keys['a'] or held_keys['d']:
                    self.currentanim = 'Walk'
                    self.newanim = 'Walk'
                else:
                    self.newanim = 'Idle'

        else:
            # Остальные состояния как раньше
            if self.currentanim != self.newanim:
                self.currentanim = self.newanim
                self.model.loop(self.newanim)

        # ---- Поворот ----
        if self.rotation_y < self.to_y_angle:
            self.rotation_y += 10
        elif self.rotation_y > self.to_y_angle:
            self.rotation_y -= 10


class Window(Entity):
    """Простое окно для мытья"""
    # todo: загружать спрайты для окон
    def __init__(self, floor_index, window_index, parent, **kwargs):
        # спрайт окна
        windows = ['Test_Spritesheet_1 (Glass t1).aseprite', 'Test_Spritesheet_1 (Glass t2).aseprite', 'Test_Spritesheet_1 (Glass t3).aseprite']
        current_variant = random.choice(windows)
        windows_sprites_data = parent.texture_docs["frames"][current_variant]['frame']
        windows_texture = parent.textures.get_sprite(windows_sprites_data['x'], windows_sprites_data['y'],
                                                     windows_sprites_data['w'], windows_sprites_data['h'])
        # windows_texture = parent.textures.get_sprite(0, 247, 32, 32)

        super().__init__(
            model="quad",
            scale=(1.5, 1.5),
            collider='box',
            texture=windows_texture,
            parent=parent,
            **kwargs
        )
        self.floor_index = floor_index
        self.window_index = window_index
        self.is_dirty = True  # окно по-умолчанию грязное, если не доказано обратное
        self.is_cleaning = False
        self.name = f"window_{floor_index}_{window_index}"

        # Грязное окно
        self.color = color.rgba(0.7, 0.7, 0.8, 0.8)

    def start_cleaning(self):
        if self.is_dirty and not self.is_cleaning:
            self.is_cleaning = True
            self.color = color.yellow
            invoke(self.finish_cleaning, delay=3.0)
            return True
        return False

    def finish_cleaning(self):
        self.is_dirty = False
        self.is_cleaning = False
        self.color = color.rgba(0.8, 0.9, 1.0, 0.9)  # Чистое окно


class WindowCleanerGame:
    """Основной класс игры"""

    def __init__(self):
        # загружаем спрайтшит и JSON с координатами из Aseprite
        textures_dir_path = pathlib.PurePath('assets','textures')
        spritesheet_filename = 'Test_Scene_1_trimmed_spritesheet'

        self.textures = SpritesheetLoader(pathlib.PurePath(textures_dir_path, spritesheet_filename + '.png'))
        with open(pathlib.PurePath(textures_dir_path, spritesheet_filename + '.json')) as file:
            doc = json.load(file)
        self.texture_docs = doc # aseprite умеет генерить json с данными о спрайтах, используем его

        self.setup_scene()
        self.setup_player()
        self.setup_building()
        self.setup_ui()

        # Игровые параметры
        self.current_level = 1
        self.score = 0
        self.lift_speed = 0.8  # скорость подъема люльки

        # Этажи и окна
        self.floors = []  # Список этажей (Entity объекты)
        self.all_windows = []  # Список всех окон

        # Логика движения люльки
        self.cradle_wait_time = 30.0  # Время ожидания на этаже
        self.current_wait_time = 0.0
        self.is_lifting = False
        self.current_floor_index = 0

        self.create_initial_floors()

        # Устанавливаем начальный текст
        self.update_ui()

    def setup_scene(self):
        """Настройка сцены"""
        window.color = color.black
        camera.orthographic = True
        camera.fov = 12

        # Фон неба
        self.background = Entity(
            model="quad",
            scale=(25, 20),
            color=color.light_gray,
            z=15,
            y=10
        )

        # Освещение
        # https://docs.panda3d.org/1.10/python/programming/render-attributes/lighting
        self.light_source = PointLight(
            position=(0, 1, -30),
            parent=camera,
            color=color.rgba(1, 1, 1, 1.0),
            shadows=False,
        )

        # self.light_source.rotation = (0, 0, 0)\

        self.directional_light = DirectionalLight(shadows=True)
        self.directional_light.update_bounds(self.player)
        self.directional_light.look_at(self.player)


    def setup_player(self):
        """Создание игрока и люльки"""
        # Контейнер люльки - всё что движется вместе с игроком
        self.cradle_container = Entity(name="cradle_system", textures=self.textures, texture_docs=self.texture_docs)

        # Игрок
        self.player = WindowCleanerPlayer()
        self.player.max_jumps = 1
        self.player.scale = 1
        # self.player.model = Actor(models="models/Ninja_Sand_Female2.gltf")
        self.player.model = Actor(models="models/Ninja_Male_Hair.gltf")
        self.player.color = color.white

        self.player.parent = self.cradle_container

        # Люлька (платформа под игроком)
        # todo: загружать спрайты для люльки
        self.cradle_platform = Entity(
            model="cube",
            scale=(4, 0.3, 1.5),
            color=color.orange,
            y=-0.6,
            parent=self.cradle_container
        )

        # Невидимая земля для коллизий (не факт, что действительно надо)
        self.cradle_ground = Entity(
            model='cube',
            color=color.hsv(0, 0, 1, .3),  # для тестов делаем землю чуточку видимой
            y=-1,
            scale=(15, 1, 3),
            collider='box',
            parent=self.cradle_container
        )

        # # Тросы (пока не надо)
        # for i in [-1, 1]:  # Два троса по бокам
        #     rope = Entity(
        #         model="cube",
        #         scale=(0.1, 15, 0.1),
        #         color=color.brown,
        #         x=i * 1.5,
        #         y=7,
        #         parent=self.cradle_container
        #     )


        # Камера плавно катается за игроком
        camera.add_script(SmoothFollow(target=self.player, offset=[0, 3, -35], speed=1))
        # ИЛИ камера следует за люлькой
        # camera.add_script(SmoothFollow(target=self.cradle_container, offset=[0, 4, -30], speed=3))

    def setup_building(self):
        """Создание системы здания"""
        # Контейнер здания - всё что статично относительно здания
        self.building_container = Entity(name="building_system", textures=self.textures, texture_docs=self.texture_docs)

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        font_path = 'assets/fonts/monogram-extended.ttf'
        custom_font = loader.loadFont(font_path)  # noqa <- так работает
        self.hud_text = OnscreenText(pos=(-1.5, 0.8), align=TextNode.ALeft)
        self.hud_text.font = custom_font
        self.hud_text.fg = color.white

    def create_initial_floors(self):
        """Создает начальные этажи"""
        for floor_index in range(12):
            self.create_floor(floor_index)

    def create_floor(self, floor_index):
        """Создает один этаж с окнами"""
        floor_y = floor_index * 4  # Каждый этаж на 4 единицы выше

        # Этаж (стена здания)
        wall_data = self.texture_docs["frames"]['Test_Scene_1 (Layer 1).aseprite']['frame']
        wall_texture = self.textures.get_sprite(wall_data['x'], wall_data['y'], wall_data['w'], wall_data['h'])

        floor_entity = Entity(
            model="quad",
            scale=(15, 4),
            y=floor_y,
            z=2,
            color=color.brown,
            texture=wall_texture,
            parent=self.building_container,
            shadows=True
        )
        self.floors.append(floor_entity)

        # Окна на этаже
        window_count = 3 # пока что неизменное количество окон
        for i in range(window_count):
            window_x = -5 + i * 5 + random.uniform(-1, 1)
            window = Window(
                floor_index=floor_index,
                window_index=i,
                x=window_x,
                y=floor_y + 0.5,
                z=1,
                parent=self.building_container
            )
            self.all_windows.append(window)

    def get_current_floor_windows(self):
        """Получает окна текущего этажа"""
        windows_list = [w for w in self.all_windows
         if w.floor_index == self.current_floor_index and w.is_dirty]

        # if DEBUG_MODE:
        #     print(f'[get_current_floor_windows] {windows_list}')

        return windows_list

    def find_nearest_dirty_window(self):
        """Находит ближайшее грязное окно"""
        # todo: выбирать только грязные окна
        current_floor_windows = self.get_current_floor_windows()

        # if DEBUG_MODE:
        #     if current_floor_windows:
        #         print(f"[find_nearest_dirty_window] {current_floor_windows[0].position}")
        #     else:
        #         print(f"[find_nearest_dirty_window] None")

        if not current_floor_windows:
            return None

        nearest_window = None
        min_distance = float('inf')

        for window in current_floor_windows:
            dist = distance_2d(self.player.position, window.position)
            if dist < min_distance:
                min_distance = dist
                nearest_window = window

        return nearest_window if min_distance <= self.player.cleaning_range else None

    def all_current_floor_clean(self):
        """Проверяет, все ли окна на текущем этаже чистые"""
        current_floor_windows = [w for w in self.all_windows
                                 if w.floor_index == self.current_floor_index]
        return all(not w.is_dirty for w in current_floor_windows)

    def move_to_next_floor(self):
        """Переход к следующему этажу"""
        self.current_floor_index += 1
        self.is_lifting = True
        self.current_wait_time = 0.0

        # Добавляем новые этажи если нужно
        if self.current_floor_index >= len(self.floors) - 3:
            for i in range(3):
                self.create_floor(len(self.floors))

    def update_cradle_movement(self):
        """Обновляет движение люльки"""
        if self.is_lifting:
            # Поднимаем люльку (опускаем здание)
            lift_distance = self.lift_speed * time.dt
            self.building_container.y -= lift_distance

            # Проверяем, достигли ли нужной высоты
            target_y = -self.current_floor_index * 4
            if self.building_container.y <= target_y:
                self.building_container.y = target_y
                self.is_lifting = False
        else:
            # Ждем на этаже
            if self.all_current_floor_clean():
                self.move_to_next_floor()
            else:
                self.current_wait_time += time.dt
                if self.current_wait_time >= self.cradle_wait_time:
                    # Время вышло - принудительно поднимаемся
                    self.move_to_next_floor()

    def update_ui(self):
        """Обновляет интерфейс"""
        global PRESSED_KEYS
        current_floor_windows = self.get_current_floor_windows()
        dirty_count = len(current_floor_windows)
        # if DEBUG_MODE:
        #     print(f'DIRTY COUNT: {dirty_count}')

        if self.is_lifting:
            self.hud_text.text = f'Уровень {self.current_level} | Поднимаемся на этаж {self.current_floor_index + 1}...'
        else:
            time_left = max(0, self.cradle_wait_time - self.current_wait_time)
            if self.player.current_target_window:
                self.hud_text.text = f'Уровень {self.current_level} | Этаж {self.current_floor_index + 1} | Окон: {dirty_count} | Время: {time_left:.1f}с | [E] - мыть!'
            else:
                self.hud_text.text = f'Уровень {self.current_level} | Этаж {self.current_floor_index + 1} | Окон: {dirty_count} | Время: {time_left:.1f}с | Подойдите к окну'

        if DEBUG_MODE:
            self.hud_text.text += (f'\nGrounded: {self.player.grounded}, Vel.:{self.player.velocity}, current_anim: {self.player.currentanim}, new:{self.player.newanim}, Move locked: {self.player.move_locked}'
                                   f'\nHeld keys: {list(held_keys)}'
                                   f'\nmovepressed: {self.player.movepressed}')

            res = dict(filter(lambda item: not (isinstance(item[1], int) and item[1] <= 0), held_keys.items()))
            if res:
                if PRESSED_KEYS:
                    if PRESSED_KEYS != res:
                        print(res)
                        PRESSED_KEYS = res
                else:
                    PRESSED_KEYS = res

    def update(self):
        """Основной цикл обновления"""
        self.update_cradle_movement() # Обновляем движение люльки
        self.player.current_target_window = self.find_nearest_dirty_window() # Обновляем цель игрока
        self.light_source.look_at(self.player)
        self.update_ui() # Обновляем UI


# === ЗАПУСК ИГРЫ ===

# Инициализация Ursina
icon_path = 'assets/knotty_kaa_32_favicon.ico'  # todo: разобраться, почему не загружает иконку
app = Ursina(title='PyWeek 40 - Game by Knotty Kaa', icon=icon_path)
Entity.default_shader = lit_with_shadows_shader
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = True

# Земля для физики
ground = Entity(model='cube', color=color.black, z=-.1, y=-1, origin_y=.5, scale=(1000, 100, 10), collider='box',
                ignore=True)


def main_input(key):
    """Глобальная обработка клавиш"""
    if key == 'tab':
        editor_camera.enabled = not editor_camera.enabled
    if key == 'escape':
        quit()


# Создание игры
game = WindowCleanerGame()

# Обработчики ввода
debug_handler = Entity(input=main_input)
editor_camera = EditorCamera(enabled=False, ignore_paused=True)


# Основной цикл
def update():
    game.update()


if __name__ == "__main__":

    app.run()