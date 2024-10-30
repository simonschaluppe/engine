import pygame

from .renderable import Renderable


class Button:
    pass


class Label(Renderable):
    def __init__(self, pos, text="", size=20):
        self.pos = pos
        self.text = text
        self.size = size

    def render(self, renderer):
        renderer.draw_text(self.text, pos=self.pos, size=self.size)


class Tooltip:
    def __init__(self, text, color=None):
        self.text = text
        self.is_hovering = False
        self.color = color

    def set_hover(self, state):
        self.is_hovering = state

    def render(self, renderer):
        if not self.is_hovering:
            return
        tooltip = pygame.Surface(((200, 50)))
        tooltip.fill(self.color)
        renderer.draw_text(self.text, pos=(10, 10), size=20, onto=tooltip)
        renderer.display.blit(tooltip, pygame.mouse.get_pos())
