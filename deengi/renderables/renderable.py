import pygame


class Renderable:
    default_coord_transform = None
    visible = True

    def render(self):
        raise NotImplementedError("Subclasses must implement render method")

    def toggle_visibility(self):
        self.visible = not self.visible
        if hasattr(self, "members"):
            for member in self.members:
                member.toggle_visibility()

    def add_to_layer(self, layer):
        layer.append(self)


class RenderGroup(Renderable):
    name: str

    def __init__(self, name):
        self.name = name
        self.members = []

    def __iter__(self):
        return iter(self.members)

    def add(self, *renderables):
        self.members.extend(renderables)

    def render(self, renderer):
        for member in self.members:
            if member.visible:
                member.render(renderer)
