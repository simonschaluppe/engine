from functools import partial
import pygame


from .camera import Camera2D
from .input_handler import InputHandler
from .renderer import Renderer

from .renderables.ui import Tooltip


class Engine:
    def __init__(self, title="Engine", debug=True):
        self.debug = debug
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(title)
        self.camera = Camera2D(self.screen, zoom=(1, 1), debug=self.debug)
        self.renderer = Renderer(self.screen, camera=self.camera, debug=self.debug)
        self.input_handler = InputHandler(
            screen_coords=self.camera.screen_coords, debug=self.debug
        )

        self.layers = {
            "background": [],
            "main": [],
            "ui": [],
            "overlay": [],
        }
        self.layer_visibility = {
            "background": True,
            "main": True,
            "ui": True,
            "overlay": True,  # Tooltips or dialogs can default to hidden
        }

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
            for layer_name in ["background", "main", "ui", "overlay"]:
                if not self.layer_visibility[layer_name]:
                    continue
                for render_callback, data_dict in self.layers[layer_name]:
                    render_callback(**data_dict)

            if self.debug:  # putnthis in overlay
                self.renderer.draw_debug()
            # render calls
            self.screen.blit(self.renderer.display, (0, 0))
            pygame.display.update()

    def clear_layer(self, layer):
        self.layers[layer] = []

    def add_to_layer(self, layer, renderable):
        self.layers[layer].append((renderable.render, dict(renderer=self.renderer)))

    def add_tooltip(self, renderable, tooltip_message, color=None):
        tooltip = Tooltip(tooltip_message, color=color)
        self.add_to_layer("overlay", tooltip)
        self.input_handler.register_hover(renderable, tooltip.set_hover)

    def show_debug(self, callback):
        self.renderer.debug_statements.append(callback)

    def show_scene(self, scene):
        self.clear_layer("ui")
        self.input_handler.reset()  # is this appropiate?
        self.input_handler.bind_options_to_keys(scene.options)
        self.layers["ui"] = []
        self.add_to_layer("ui", scene)

    def show_dialog(self, scene):
        self.input_handler.reset()  # is this appropiate?
        self.input_handler.bind_options_to_keys(scene.options)
        self.add_to_layer("ui", scene)

    def show_background(self, color):
        self.layers["background"].append((self.renderer.draw_bg, dict(color=color)))

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
