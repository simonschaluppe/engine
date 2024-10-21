import pygame

from .camera import Camera2D
from .input_handler import InputHandler
from .renderer import Renderer
from .tiles import Tilemap
from .ui import Scene, Option


class Engine:
    def __init__(self, title="Engine"):

        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(title)
        display = pygame.Surface((800, 600))
        camera = Camera2D(display, zoom=(1, 1))
        self.renderer = Renderer(display, camera=camera)
        self.input_handler = InputHandler()

        self.render_stack = []

    def setup_camera(
        self,
        rotation=0,
        isometry=0.3,
        zoom=30,
        mousewheelzoom=True,
        mousedrag_pan=True,
        arrow_rotate=True,
    ):
        self.renderer.camera.set_rotation(rotation)
        self.renderer.camera.set_isometry(isometry)
        self.renderer.camera.zoom(zoom)
        if mousewheelzoom:
            self.input_handler.bind_camera_zoom_to_mousewheel(self.renderer.camera)
        if mousedrag_pan:
            self.input_handler.bind_camera_pan_to_mousedrag(
                self.renderer.camera, button=1
            )
        if arrow_rotate:
            self.input_handler.bind_camera_rotate_to_arrow_keys(self.renderer.camera)

    def run(self):
        while True:
            # handle events
            self.input_handler.update()

            self.renderer.display.fill((0, 0, 0))
            for render_callback, data_dict in self.render_stack:
                render_callback(**data_dict)

            # render calls
            self.screen.blit(self.renderer.display, (0, 0))
            pygame.display.update()

    def show_scene(self, scene: Scene):

        self.input_handler.reset()  # is this appropiate?
        self.input_handler.bind_options_to_keys(scene.options)
        render_callback = self.renderer.render_text_scene
        data = dict(
            title=scene.title,
            text=scene.text,
            options=scene.get_options_text(),
        )
        self.render_stack.pop()
        self.add_rendering_callbacks((render_callback, data))

    def show_dialog(self, scene):
        self.input_handler.reset()  # is this appropiate?
        self.input_handler.bind_options_to_keys(scene.options)
        self.add_rendering_callbacks(
            (
                self.renderer.render_dialog,
                dict(
                    title=scene.title,
                    text=scene.text,
                    options=scene.get_options_text(),
                ),
            )
        )

    def set_rendering_callback(self, render_callback, data=None):
        self.render_stack = [(render_callback, data)]

    def add_rendering_callbacks(self, *tuples):
        for t in tuples:
            self.render_stack.append(t)

    def create_tilemap(self, positions: list, sizes: list, colors: list):
        self.tilemap = Tilemap(positions, sizes, colors)

    def show_tilemap(self):
        self.set_rendering_callback(
            self.renderer.render_tilemap, {"tilemap": self.tilemap}
        )

    def quit(self):
        pygame.quit()
        quit()


if __name__ == "__main__":
    engine = Engine()
    ts = engine.current_scene
    ts.title = "Scene"
    ts.text = """asdasidasd
        asdasdlkasd
        askaslkdmsakdasmd
        askdmasldmas.dmsad
        asldkmasdlasd asld asd"""
    ts.options = """1. [asd] asdsadasd
        2. [M]ove to somewhere"""
    engine.run()

    # render scene
    # scene
