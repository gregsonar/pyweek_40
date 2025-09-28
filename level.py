from ursina import Entity, Text, invoke, EditorCamera, color, destroy
from base_scene import BaseScene
from globals import scene_manager, clear_all_invokes, stop_all_animations_and_invokes


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
            print(f"Ошибка импорта: {e}")
        except Exception as e:
            print(f"Ошибка создания игры: {e}")

    def update(self):
        """Основной цикл обновления"""
        if self.game and hasattr(self.game, 'update'):
            try:
                self.game.update()
            except Exception as e:
                print(f"Ошибка в игровом цикле: {e}")

    def on_disable(self):
        """Отключается при деактивации сцены"""
        if not self.is_initialised:
            return
        print("Выключаем уровень...")

        clear_all_invokes()
        stop_all_animations_and_invokes()

        # делаем копию списка потомков — нельзя итерироваться по .children во время удаления
        for child in list(self.children):
            print(f"DESTROY {child}")
            destroy(child)

        # Очищаем ресурсы только если они существуют
        if hasattr(self, 'debug_handler') and self.debug_handler:
            destroy(self.debug_handler)
            self.debug_handler = None

        if hasattr(self, 'editor_camera') and self.editor_camera:
            destroy(self.editor_camera)
            self.editor_camera = None

        if hasattr(self, 'game') and self.game:
            # Если у игры есть метод очистки - вызываем его
            if hasattr(self.game, 'cleanup'):
                self.game.cleanup()
            self.game = None

        # Уничтожаем дочерние объекты
        for child in list(self.children):
            print(f"DESTROY {child}")
            destroy(child)