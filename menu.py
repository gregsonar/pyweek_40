# scenes/menu.py
from ursina import Button, Text, application, curve, Animation, window, color, Entity, invoke, destroy, camera, Sequence
from base_scene import BaseScene
import pathlib
from globals import stop_all_animations_and_invokes, clear_all_invokes

class MenuScene(BaseScene):
    def __init__(self):
        super().__init__(scene_id='menu')
        # self.enabled = False
        self.animations = []
        self.invoked_animations = []

        self.skyline_texture = str(pathlib.Path('assets', 'textures', 'background_panelki_RGB.png'))

    def on_enable(self):
        self.is_initialised = True
        def go_forward(background, animations, invoked_animations):
            animations = background.animate('z', 10, duration=5, curve=curve.in_out_quad)
            invoked_animations = invoke(go_backward, background, animations, invoked_animations, delay=5)  # вызвать возврат после завершения
            print(f"go_forward: {animations} \n\t {invoked_animations}")

        def go_backward(background, animations, invoked_animations):
            animations = background.animate('z', 0, duration=3, curve=curve.in_out_quad)
            invoked_animations = invoke(go_forward, background, animations, invoked_animations, delay=3)
            print(f"go_backward: {animations} \n\t {invoked_animations}")

        self.background = Entity(name='menu_background', model="quad", texture=self.skyline_texture, parent=self)
        # self.background.visible=True
        self.background.scale = (24,14)
        self.background.texture_scale = (1, 1),
        self.background.z += 1
        self.background.alpha=0.8

        go_forward(self.background, self.animations, self.invoked_animations)

        a = Animation('ursina_wink', parent=self)
        a.position = window.bottom_right
        a.x += 6
        a.y -= 3

        pw_text = Text("The Window Washing Game\nPyWeek 40", x=2, y=.4, scale=14, parent=self)
        pw_text.animate('rotation_z', pw_text.rotation_z + 360, duration=3, loop=True, curve=curve.linear)

        font_path = 'assets/fonts/monogram-extended.ttf'
        custom_font = loader.loadFont(font_path)  # noqa <- так работает
        Text.default_font = font_path

        start_button = (Button(text='Play!', x=-3, y=2, z=-1,
                               highlight_scale=1.05, highlight_color=color.rgb32(191, 176, 155),
                               on_click=lambda: self.change_scene('level'), parent=self))
        start_button.font = custom_font
        start_button.fit_to_text(padding=(5,1))

        exit_button = Button(text='Quit', x=-3, y=0, z=-1,
                             highlight_scale=1.05, highlight_color=color.rgb32(191, 176, 155),
                             on_click=application.quit, parent=self)
        exit_button.font = custom_font
        exit_button.fit_to_text(padding=(5, 1))

    def on_disable(self):
        # if not self.is_initialised:
        #     return
        # for animation in Sequence.sequences:
        #     animation.kill()
        # print(f"on_disable anims: {self.animations} \n\t {self.invoked_animations}")
        # print('''УНИЧТОЖАЕМ СЦЕНУ menu''')
        # if 'invoked_animations' in self.__dir__():
        #     if self.invoked_animations:
        #         for anim in self.invoked_animations:
        #             print(f'ANIMS: {anim}')
        #             anim.cancel()
        #
        # if 'animations' in self.__dir__():
        #     if self.animations:
        #         self.animations.animate_stop()
        #
        # destroy(self.background)

        clear_all_invokes()
        stop_all_animations_and_invokes()

        # делаем копию списка потомков — нельзя итерироваться по .children во время удаления
        for child in list(self.children):
            print(f"DESTROY {child}")
            destroy(child)
