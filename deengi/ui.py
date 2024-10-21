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
