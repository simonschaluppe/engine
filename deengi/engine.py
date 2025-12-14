from functools import partial
import pygame

from deengi import renderables
from deengi.renderables.renderable import Renderable


from deengi.camera import Camera2D
from deengi.input_handler import InputHandler
from deengi.renderer import Renderer

from deengi.renderables.ui import Tooltip


class Engine:
    def __init__(self, title="Engine", debug=True, screen_size=(800, 600)):
        self.debugmode = debug
        pygame.init()
        self.layers = {
            "background": [],
            "main": [],
            "ui": [],
            "overlay": [],
            "debug": [],
        }
        self.layer_visibility = {
            "background": True,
            "main": True,
            "ui": True,
            "overlay": True,  # Tooltips or dialogs can default to hidden
            "debug": debug,
        }
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(title)

        self.camera = Camera2D(self.screen, zoom=(1, 1), debug=self.debugmode)
        pygame.screen_coords = self.camera.screen_coords

        self.renderer = Renderer(self.screen, camera=self.camera, debug=self.debugmode)

        self.input_handler = InputHandler(
            screen_coords=self.camera.screen_coords, debug=self.debugmode
        )
        self.setup_camera()
        self.show_background()

        self.paused = False
        self.bind_key("q", self.quit, "Quit")
        self.bind_key("d", self.toggle_debug, "toggle debug mode")
        self.bind_key("p", self.toggle_pause, "Pause")

        self.update_callbacks = []

    def setup_camera(
        self,
        rotation=0,
        isometry=1,
        zoom=100,
        mousewheelzoom=True,
        mousedrag_pan=True,
        arrow_rotate=True,
        pos=(0, 0),
    ):
        self.camera.set_game_position(pos)
        self.camera.set_rotation(rotation)
        self.camera.set_isometry(isometry)
        self.camera.zoom(zoom)
        if mousewheelzoom:
            self.input_handler.bind_camera_zoom_to_mousewheel(self.renderer.camera)
        if mousedrag_pan:
            self.input_handler.bind_camera_pan_to_mousedrag(
                self.renderer.camera, button=1
            )
        if arrow_rotate:
            self.input_handler.bind_camera_rotate_to_arrow_keys(self.renderer.camera)

    def update(self):
        for callback in self.update_callbacks:
            callback()

    def run(self):
        while True:
            # handle events
            self.clock.tick(60)
            if not self.paused:
                self.update()

            self.input_handler.update()

            for layer_name in ["background", "main", "ui", "overlay", "debug"]:
                if not self.layer_visibility[layer_name]:
                    continue
                for renderable in self.layers[layer_name]:
                    if isinstance(renderable, Renderable) and renderable.visible:
                        renderable.render(self.renderer)
                    elif isinstance(renderable, tuple):
                        callback, data_dict = renderable
                        callback(**data_dict)

            if self.debugmode:  # putnthis in overlay
                self.renderer.draw_debug()
            # render calls
            self.screen.blit(self.renderer.display, (0, 0))
            pygame.display.update()

    def clear_layer(self, layer=None):
        self.layers[layer] = []

    def clear(self, *layers):
        if not layers:
            layers = self.layers
        for l in layers:
            if l in self.layers:
                self.layers[l] = []
            else:
                raise KeyError(f"layer {l=} not in {self.layers=}")

    def add_to_layer(self, layer="main", *renderables):
        if layer not in self.layers:
            raise KeyError(
                f"Layer {layer} not found in engine Layers: {list(self.layers.keys())}"
            )
        for renderable in renderables:
            self.layers[layer].append(renderable)

    def add_tooltip(self, renderable, tooltip_message, color=None):
        tooltip = Tooltip(tooltip_message, color=color)
        self.add_to_layer("overlay", tooltip)
        self.input_handler.register_hover(renderable, tooltip.set_hover)

    def add_callback(self, callback):
        self.update_callbacks.append(callback)

    def show_debug(self, statement):
        self.renderer.debug_statements.append(statement)

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

    def show_background(self, color=(0, 0, 0)):
        self.clear_layer("background")
        self.layers["background"].append((self.renderer.draw_bg, dict(color=color)))

    def show_grid(
        self, lines: int | tuple[int, int] = 20, start: tuple[int, int] = None, **kwargs
    ):
        if isinstance(lines, int):
            xlines = ylines = lines
        elif isinstance(lines, tuple):
            xlines, ylines = lines
        else:
            raise ValueError(f"Argument lines must be int or tuple of ints")
        if not start:
            startx = -xlines // 2
            starty = -ylines // 2
        elif isinstance(start, tuple):
            startx, starty = start
        else:
            raise ValueError(f"Argument start must be tuple of ints")

        grid = renderables.Grid(
            (startx, startx + xlines), (starty, starty + ylines), **kwargs
        )
        self.add_to_layer(
            "background",
            grid,
        )
        return grid

    def toggle_debug(self):
        self.debugmode = not self.debugmode
        self.renderer.debug = self.debugmode
        self.input_handler.debug = self.debugmode
        self.camera.debug = self.debugmode

    def toggle_visibility_cb(self, *renderables: Renderable):
        def callback():
            for renderable in renderables:
                renderable.toggle_visibility()

        return callback

    def toggle_pause(self):
        self.paused = not self.paused

    def bind_key(self, key, callback, binding_name=None):
        key = str(key) if type(key) is not str else key
        self.input_handler.bind_keypress(
            ord(key.lower()), callback, binding_name=binding_name
        )

    def get_keybinds(self):
        return self.input_handler.get_keybinds()

    def quit(self):
        pygame.quit()
        quit()
