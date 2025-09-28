from ursina import Button, Text, application, curve, Animation, window, color, Entity, invoke, destroy, camera, Sequence
from ursina.camera import Camera
from base_scene import BaseScene
import pathlib
from globals import stop_all_animations_and_invokes, clear_all_invokes, button_click, SCORE_FILE_PATH
import os


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

        global camera
        if camera and hasattr(camera, 'model'):
            destroy(camera)
        camera = Camera()

        a = Animation('ursina_wink', parent=self)
        a.position = window.bottom_right
        a.x += 6
        a.y -= 3

        pw_text = Text("The Window Washing Game\nPyWeek 40", x=2, y=.4, scale=14, parent=self)
        pw_text.animate('rotation_z', pw_text.rotation_z + 360, duration=3, loop=True, curve=curve.linear)

        font_path = 'assets/fonts/monogram-extended.ttf'
        custom_font = loader.loadFont(font_path)  # noqa <- так работает
        Text.default_font = font_path

        score_text = Text(x=-5.5, y=-1.2, scale=12, parent=self)
        try:
            if os.path.exists(SCORE_FILE_PATH):
                with open(SCORE_FILE_PATH, "r", encoding="utf-8") as f:
                    lines = f.read().strip().splitlines()
                    result=lines[-1] if lines else None
                if result:
                    score_text.text = f"Last score: {result.split(': ')[-1]}"
        except Exception as e:
            print(e)

        howto_text = Text("How to play: You need to wash all the windows in this skyscraper before time runs out.\n"
                          "To wash a window, press and hold [E] while standing next to the window.\n"
                          "When the timer expires or all windows on the floor have been washed,\n"
                          "the cradle will move to the next floor. GLHF!", x=-5.5, y=-2, scale=10, parent=self)

        credits_text = Text("Knotty Kaa, 2025 (Dudnikov, rikovmike, Juna_Gala, ObiXoD)",
                            x=-5.5, y=-3.5, scale=10, parent=self)

        camera.fov=12
        hidden_text = Text("Well... Camera is somehow broken, I know. Sorry :) (And you've probably noticed that it's always Level 1 here, right?)",
                            x=-5.5, y=4.5, scale=14, parent=self)

        start_button = (Button(text='Play!', x=-3, y=2, z=-1,
                               highlight_scale=1.05, highlight_color=color.rgb32(191, 176, 155),
                               on_click=lambda: self.change_scene('level'), parent=self))
        start_button.font = custom_font
        start_button.pressed_sound = button_click
        start_button.fit_to_text(padding=(5,1))

        exit_button = Button(text='Quit', x=-3, y=0, z=-1,
                             highlight_scale=1.05, highlight_color=color.rgb32(191, 176, 155),
                             on_click=application.quit, parent=self)
        exit_button.font = custom_font
        exit_button.fit_to_text(padding=(5, 1))

    def on_disable(self):
        clear_all_invokes()
        stop_all_animations_and_invokes()

        # делаем копию списка потомков — нельзя итерироваться по .children во время удаления
        for child in list(self.children):
            print(f"DESTROY {child}")
            destroy(child)
