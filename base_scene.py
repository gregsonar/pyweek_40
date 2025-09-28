from ursina import Entity, destroy
from globals import change_scene

class BaseScene(Entity):
    def __init__(self, scene_id:str, **kwargs):
        super().__init__(**kwargs)
        self.is_initialised = False
        self.enabled = False  # сцена по умолчанию не активна
        self.scene_id = scene_id
        self.change_scene = change_scene

    def on_enable(self):
        """Включается при активации сцены"""
        self.is_initialised = True
        pass

    def on_disable(self):
        if not self.is_initialised:
            return
        # делаем копию списка потомков — нельзя итерироваться по .children во время удаления
        for child in list(self.children):
            destroy(child)
