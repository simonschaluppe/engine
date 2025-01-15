import pygame

from .renderable import Renderable


class Button:
    pass


class Label(Renderable):
    def __init__(
        self, pos, text="", size=20, color=None, outline_color=None, font=None
    ):
        self.pos = pos
        self.text = text
        self.size = size
        self.color = color or (10, 10, 10)
        self.outline_color = outline_color or (255, 255, 255)
        self.font = font

    def render(self, renderer):
        font = self.font or renderer.font
        renderer.draw_text(
            self.text,
            pos=renderer.screen_coords(self.pos),
            size=self.size,
            lineheight=self.size * 0.9,
            color=self.color,
            font=font,
            border_color=self.outline_color,
        )


class Tooltip(Renderable):
    def __init__(self, text, color=None):
        self.text = text
        self.is_hovering = False
        self.color = color or (0, 0, 0)

    def set_hover(self, state):
        self.is_hovering = state

    def render(self, renderer):
        if not self.is_hovering:
            return
        tooltip = pygame.Surface(((200, 50)))
        tooltip.fill(self.color)
        renderer.draw_text(self.text, pos=(10, 10), size=20, onto=tooltip)
        renderer.display.blit(tooltip, pygame.mouse.get_pos())
