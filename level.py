from ursina import Entity, Text, invoke, EditorCamera, color, destroy, camera
from base_scene import BaseScene
from globals import scene_manager, clear_all_invokes, stop_all_animations_and_invokes, cleanup_and_reset_camera_for_scene


class MainGameplay(BaseScene):
    def __init__(self):
        # Инициализируем атрибуты до вызова super().__init__
        self.game = None
        self.editor_camera = None
        self.debug_handler = None
        super().__init__(scene_id='level')

    def on_enable(self):
        """Включается при активации сцены"""
        self.is_initialised = True
        try:
            from game import WindowCleanerGame, crossfade_sky

            # Земля для физики
            ground = Entity(model='cube', z=-.1, y=-1, origin_y=.5, scale=(1000, 100, 10), collider='box',
                            ignore=True, parent=self)
            ground.color = color.rgba(0.7, 0.7, 0.8, 0.0)  # земля прозрачная, чтобы видеть этажи ниже

            def main_input(key):
                """Глобальная обработка клавиш"""
                if key == 'escape':
                    scene_manager.switch('menu') # Возвращаемся в меню вместо выхода
                    # quit()

            # Создание игры
            self.game = WindowCleanerGame()

            # Обработчики ввода
            self.debug_handler = Entity(input=main_input, parent=self)
            # self.editor_camera = EditorCamera(enabled=False, ignore_paused=True)

        except ImportError as e:
            print(f"ImportError: {e}")
        except Exception as e:
            print(f"Game creation error: {e}")

    def update(self):
        """Основной цикл обновления"""
        if self.game and hasattr(self.game, 'update'):
            try:
                self.game.update()
            except Exception as e:
                print(f"Game loop error: {e}")

    def on_disable(self):
        if not self.is_initialised:
            return

        # Останавливаем все анимации и invoke до удаления объектов
        clear_all_invokes()
        stop_all_animations_and_invokes()

        if hasattr(self, 'game') and self.game:
            # Очищаем UI элементы игры
            if hasattr(self.game, 'hud_text') and self.game.hud_text:
                self.game.hud_text.removeNode()
                self.game.hud_text = None

            # Удаляем освещение
            if hasattr(self.game, 'light_source') and self.game.light_source:
                destroy(self.game.light_source)
                self.game.light_source = None

            if hasattr(self.game, 'directional_light') and self.game.directional_light:
                destroy(self.game.directional_light)
                self.game.directional_light = None

            # Удаляем фоны
            if hasattr(self.game, 'background') and self.game.background:
                destroy(self.game.background)
                self.game.background = None

            if hasattr(self.game, 'night_background') and self.game.night_background:
                destroy(self.game.night_background)
                self.game.night_background = None

            # Очищаем контейнеры здания и люльки
            if hasattr(self.game, 'building_container') and self.game.building_container:
                for element in list(self.game.building_container.children):
                    destroy(element)
                destroy(self.game.building_container)
                self.game.building_container = None

            if hasattr(self.game, 'cradle_container') and self.game.cradle_container:
                for element in list(self.game.cradle_container.children):
                    destroy(element)
                destroy(self.game.cradle_container)
                self.game.cradle_container = None

            # Очищаем списки объектов
            if hasattr(self.game, 'floors'):
                self.game.floors.clear()
            if hasattr(self.game, 'all_windows'):
                self.game.all_windows.clear()

            # Очищаем текстуры
            if hasattr(self.game, 'textures'):
                self.game.textures = None
            if hasattr(self.game, 'texture_docs'):
                self.game.texture_docs = None

            # Если у игры есть метод очистки - вызываем его
            if hasattr(self.game, 'cleanup'):
                self.game.cleanup()
            self.game = None

        # Очищаем камеру от всех дочерних объектов и скриптов
        if camera:
            # Удаляем все скрипты камеры (включая SmoothFollow)
            if hasattr(camera, 'scripts'):
                camera.scripts.clear()

            # Удаляем дочерние объекты камеры
            for element in list(camera.children):
                destroy(element)

        # Очищаем ресурсы только если они существуют
        if hasattr(self, 'debug_handler') and self.debug_handler:
            destroy(self.debug_handler)
            self.debug_handler = None

        if hasattr(self, 'editor_camera') and self.editor_camera:
            destroy(self.editor_camera)
            self.editor_camera = None

        # Уничтожаем дочерние объекты сцены
        for element in list(self.children):
            destroy(element)

        cleanup_and_reset_camera_for_scene()