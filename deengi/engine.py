import pygame

from .camera import Camera2D
from .input_handler import InputHandler
from .renderer import Renderer


class Option:
    text: str
    callback: callable

    def __init__(self, text, callback):
        self.text = text
        self.callback = callback

    def __str__(self):
        return self.text


class Scene:
    options: list[Option]
    title: str = "Title"
    text: str = "filler text"

    def __init__(self, title="", text=""):
        self.title = title
        self.text = text
        self.options = []

    def get_options_text(self):
        return "\n".join([str(o) for o in self.options])

    def add_options(self, *options):
        for option in options:
            self.options.append(option)


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
        self.create_keybindings_from_options(scene.options)
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
        self.create_keybindings_from_options(scene.options)
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

    def create_keybindings_from_options(self, options: list[Option]):
        used_keys = []
        prefix = ""
        for i, option in enumerate(options):
            if i < 9 and i + 1 not in used_keys:
                used_keys.append(i + 1)
                self.input_handler.bind_keypress(49 + i, option.callback)  # 49 = K_1
                prefix = f"{i+1}. "
            first_letter = option.text[:1].lower()
            rest = option.text[1:]
            if first_letter not in used_keys:
                used_keys.append(first_letter)
                self.input_handler.bind_keypress(
                    ord(first_letter), option.callback
                )  # 49 = K_1
                option.text = f"[{first_letter.upper()}]{rest}"
            option.text = prefix + option.text

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
