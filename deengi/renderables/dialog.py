import pygame


class Option:
    text: str
    callback: callable

    def __init__(self, text, callback):
        self.text = text
        self.callback = callback

    def __str__(self):
        return self.text


class Dialog:
    options: list[Option]
    title: str = "Title"
    text: str = "filler text"

    def __init__(self, title="", text=""):
        self.title = title
        self.text = text
        self.options = []

    def get_options_text(self):
        return "\n".join([str(o) for o in self.options])

    def add_option(self, text, callback):
        self.options.append(Option(text, callback))

    def render(self, renderer):
        renderer.draw_text(self.title, pos=(50, 50), size=30)
        renderer.draw_text(self.text, pos=(50, 100), size=20)
        renderer.draw_text(self.get_options_text(), pos=(50, 400), size=20)


class PopupMenu(Dialog):
    def render(self, renderer):
        dialog = pygame.Surface(((400, 150)))
        dialog.fill(renderer.get_color("Dialog Background"))
        renderer.draw_text(self.title, pos=(20, 20), size=20, onto=dialog)
        renderer.draw_text(self.text, pos=(20, 45), size=20, onto=dialog)
        renderer.draw_text(self.get_options_text(), pos=(20, 80), size=20, onto=dialog)
        renderer.display.blit(dialog, (200, 200))
