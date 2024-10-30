import sys
import pygame as pg
from pathlib import Path

import logging

from .camera import Camera2D
from .font import Font

ROOT_PATH = Path(__file__).parent
sys.path.append(ROOT_PATH)

FONT_PATH = ROOT_PATH / "fonts"

default_colors = {
    "Title": (100, 30, 0),
    "DEBUG": (40, 64, 123),
    "Button hovered": (61, 98, 116),
    "Button": (51, 58, 96),
    "UI Text": (76, 37, 29),
    "Dialog Background": (51, 58, 96),
    "Grid": (200, 255, 200),
}

# Define color constants
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_BLUE = (0, 0, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ALMOSTBLACK = (10, 10, 10)
GREEN = (0, 255, 0)


import math
import pygame as pg


def color_interpolation(color1, color2, weight):
    colorvector1 = pg.Vector3(color1)
    colorvector2 = pg.Vector3(color2)
    dist = colorvector1.distance_to(colorvector2)
    return tuple(colorvector1.move_towards(colorvector2, weight * dist))


def circle_surf(radius, color):
    surf = pg.Surface((radius * 2, radius * 2))
    pg.draw.circle(surf, color, (radius, radius), radius)
    surf.set_colorkey((0, 0, 0))
    return surf


def hexagon_points(center=pg.Vector2(0, 0), r=1):
    points = []
    for angle in range(0, 360, 60):
        points.append(center + pg.Vector2(r, 0).rotate(angle))
    return points


class Renderer:
    def __init__(
        self,
        display: pg.Surface,
        camera: Camera2D,
        scale=1.0,
        colors=default_colors,
        debug=True,
    ):
        self.display = display
        self.cx, self.cy = display.get_width() // 2, display.get_height() // 2
        self.camera = camera
        self.scale = scale
        self.colors = colors
        self.debug = debug

        # defaults
        self.lineheight = 25
        self.font = Font(FONT_PATH / "small_font.png")
        self.titlefont = Font(FONT_PATH / "large_font.png")

        self.debug_statements = []

    def screen_coords(self, *args):
        if type(args[0]) is tuple or type(args[0]) is pg.Vector2:
            return self.camera.screen_coords(args[0])
        elif len(args) == 2:
            return self.camera.screen_coords((args[0], args[1]))
        elif type(args[0]) is list:
            return self.camera.screen_coords(args[0])
        else:
            raise ValueError(
                "args[0] must be tuple, pg.Vector2d or list of points, or args must be list of two coordinates"
            )

    def get_color(self, color):
        """Retrieve color from self.colors or default_colors, with a final fallback."""
        if color in self.colors:
            return self.colors[color]
        elif color in default_colors:
            return default_colors[color]
        else:
            # Final fallback to a safe color or raise an exception
            logging.warning(
                f"Color '{color}' not found in both self.colors and default_colors. Using DEBUG color."
            )
            return default_colors["DEBUG"]  # Fallback color (black)

    # debug stuff, should be low level
    def draw_debug(self):
        # Render debug statements
        for i, callback in enumerate(self.debug_statements):
            debug_text = f"{callback()}"
            self.draw_text(
                debug_text,
                self.get_color("DEBUG"),
                (10, i * self.lineheight),
            )

    # basic rendering
    def outline(self, surf, loc, pixel, color=(10, 10, 10), onto=False):
        if not onto:
            onto = self.display
        mask = pg.mask.from_surface(surf)
        mask_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0))
        mask_surf.set_colorkey((0, 0, 0))
        x, y = loc
        onto.blit(mask_surf, (x - pixel, y))
        onto.blit(mask_surf, (x + pixel, y))
        onto.blit(mask_surf, (x, y - pixel))
        onto.blit(mask_surf, (x, y + pixel))
        onto.blit(mask_surf, (x - pixel, y - pixel))
        onto.blit(mask_surf, (x + pixel, y + pixel))
        onto.blit(mask_surf, (x + pixel, y - pixel))
        onto.blit(mask_surf, (x - pixel, y + pixel))

    def draw_textline(
        self,
        text: str,
        color=ALMOSTBLACK,
        pos=(0, 0),
        size=20,
        border_width=2,
        border_color=WHITE,
        font=None,
        onto=None,
    ):
        """Render a single text line onto a surface."""
        if not font:
            font = self.font
        if not onto:
            onto = self.display
        px, py = pos
        textsurf = font.surface(text, size, color)
        self.outline(textsurf, (px, py), border_width, border_color, onto=onto)
        font.render(onto, text, (px, py), size, color)
        if self.debug:
            pg.draw.rect(onto, self.get_color("DEBUG"), (px, py, 3, 3))

    def draw_text(
        self, text: str, color=ALMOSTBLACK, pos=(0, 0), lineheight=None, **kwargs
    ):
        px, py = pos
        dy = 0
        for line in text.splitlines():
            self.draw_textline(line, color, (px, py + dy), **kwargs)
            dy += lineheight if lineheight else self.lineheight

    def draw_bg(self, color=None):
        color = color or self.get_color("background")
        self.display.fill(color)

    # button
    def render_button(self, button):
        button_surf = pg.Surface(button.size)
        button_surf.fill(
            self.get_color("Button hovered")
            if button.hovered
            else self.get_color("Button")
        )
        # outline
        self.outline(
            button_surf, button.position, pixel=1 + button.hovered - button.pressed
        )
        # text
        offset = 5 + 2 * button.pressed
        self.draw_text(
            button.text,
            pos=(5, offset),
            onto=button_surf,
            size=20,
            border_width=1 + button.hovered,
        )
        # button
        self.display.blit(button_surf, button.position)

    # particle renderer
    def draw_particles(self, particleList, color):
        for p in particleList:
            pos = self.camera.screen_coords(p.pos)
            x, y = pos
            pg.draw.circle(self.display, color, pos, p.lifetime / 8)
            glow_color = color_interpolation((0, 0, 0), color, 0.2)
            radius = p.lifetime / 3
            self.display.blit(
                circle_surf(radius, glow_color),
                (x - radius, y - radius),
                special_flags=pg.BLEND_RGB_ADD,
            )


class Layer:
    def __init__(self):
        self.content = []
        self.visible = True

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def toggle_visibility(self):
        self.visible = not self.visible

    def render(self, renderer):
        for renderable in self.content:
            renderable.render(renderer)


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((800, 600))

    display = pg.Surface((800, 600))
    camera = Camera2D(display, rotation=45, flatness=0.5)
    renderer = Renderer(display, camera)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

        display.fill((255, 255, 255))

        mouse = pg.mouse.get_pos()
        mouse_game = renderer.camera.game_coords(mouse)
        mouse_screen = renderer.camera.screen_coords(mouse_game)
        print(mouse, mouse_game, mouse_screen)

        pg.draw.polygon(
            renderer.display,
            "green",
            renderer.screen_coords(hexagon_points((0, 0), r=100)),
        )
        pg.draw.polygon(
            renderer.display,
            "darkgreen",
            renderer.screen_coords(hexagon_points((160, 100), r=100)),
        )
        renderer.draw_grid((-1000, 1000), (-1000, 1000), spacing=100, labels=True)

        screen.blit(renderer.display, (0, 0))

        tile = pg.image.load("../ClimStar/assets/images/tile.png").convert_alpha()

        tile = pg.transform.scale(tile, (200, 200))
        tile.set_colorkey((255, 0, 0))
        screen.blit(tile, renderer.screen_coords(0, 0))
        screen.blit(tile, renderer.screen_coords(-200, -200))

        mask = pg.mask.from_surface(tile)
        screen.blit(
            mask.to_surface(
                unsetcolor=(0, 0, 0, 0),
                setcolor=(255, 0, 0),
            ),
            renderer.screen_coords(0, -200),
        )

        mouse = pg.Surface((5, 5))
        mouse.fill((0, 155, 50))

        screen.blit(mouse, pg.mouse.get_pos())

        pg.display.update()
