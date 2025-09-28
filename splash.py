from ursina import Entity, Text, invoke, color, destroy
from base_scene import BaseScene
import pathlib


class SplashScene(BaseScene):
    def __init__(self):
        super().__init__(scene_id='splash')
        self.logo_texture = str(pathlib.Path('assets', 'textures', 'knotty_kaa_pw40_logo.png'))
        self.enabled=False

    def on_enable(self):
        self.is_initialised = True
        self.splash_background = Entity(name='menu_background', model="quad", parent=self)
        self.splash_background.scale = (24, 14)
        self.splash_background.texture_scale = (1, 1),
        self.splash_background.z += 1
        self.splash_background.color = color.rgb32(191, 176, 155)

        self.splash_logo = Entity(name='KnottyKaaLogo', model="quad", parent=self)
        self.splash_logo.texture = self.logo_texture
        self.splash_logo.scale = (4,2)

        invoke(self.change_scene, 'menu', delay=4)

    def on_disable(self):
        if not self.is_initialised:
            return
        print('''УНИЧТОЖАЕМ СЦЕНУ splash''')
        # делаем копию списка потомков — нельзя итерироваться по .children во время удаления
        for child in list(self.children):
            print(f"\tDESTROY {child}")
            destroy(child)
