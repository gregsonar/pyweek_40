from ursina import Entity, color, Sequence, Func, destroy, camera

class SceneManager(Entity):
    def __init__(self):
        super().__init__()
        self.current_scene = None
        self.overlay = Entity(
            parent=camera, model='quad',
            color=color.black, alpha=0, z=-1, scale=(2,2)
        )
        self.scenes = {}

    def register(self, scene):
        self.scenes[scene.scene_id] = scene

    def switch(self, name, fade_duration=2):
        print(self.scenes.keys())
        if name not in self.scenes.keys():
            print(f"[SceneManager] Scene '{name}' not found")
            return

        def _disable_old():
            if self.current_scene:
                # self.current_scene.on_disable()
                self.current_scene.enabled = False

        def _enable_new():
            self.current_scene = self.scenes[name]
            self.current_scene.enabled = True
            # self.current_scene.on_enable()

        Sequence(
            Func(lambda: self.overlay.animate('alpha', 1, duration=fade_duration)),
            Func(_disable_old),
            Func(_enable_new),
            Func(lambda: self.overlay.animate('alpha', 0, duration=fade_duration)),
        ).start()
