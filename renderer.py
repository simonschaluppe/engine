import sys
import pygame as pg
import math
from pathlib import Path

from camera import Camera2D
from font import Font

ROOT_PATH = Path(__file__).parent
sys.path.append(ROOT_PATH)

FONT_PATH = ROOT_PATH / "fonts"

colors = {
    "Title": (100, 30, 0),
    "DEBUG": (40, 64, 123),
    "Button hovered": (61, 98, 116),
    "Button": (51, 58, 96),
    "UI Text": (76, 37, 29),
    "Dialog Background": (51, 58, 96),
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
        colors=colors,
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

    def draw_grid(
        self,
        xrange: tuple,
        yrange: tuple,
        spacing=1,
        color="blue",
        labels=False,
        width=2,
    ):
        # how many spacings in camera screen coordinates?
        minx, maxx = xrange
        miny, maxy = yrange
        for x in range(minx, maxx + 1, spacing):
            pg.draw.line(
                self.display,
                color,
                *self.screen_coords([(x, miny), (x, maxy)]),
                width=width,
            )
            if labels and x < maxx:  # x axis
                self.draw_text(str(x), pos=self.screen_coords(x + 0.5, miny - 0.5))
        for y in range(miny, maxy + 1, spacing):
            pg.draw.line(
                self.display,
                color,
                *self.screen_coords([(minx, y), (maxx, y)]),
                width=width,
            )
            if labels and y < maxy:
                self.draw_text(str(y), pos=self.screen_coords(minx - 0.5, y + 0.5))

    # debug stuff, should be low level
    def debug(self, statements):
        # Render debug statements
        for i, (label, callback) in enumerate(statements.items()):
            debug_text = f"{label}: {callback()}"
            self.draw_text(debug_text, self.colors["DEBUG"], (10, i * self.lineheight))

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
            pg.draw.rect(onto, self.colors["DEBUG"], (px, py, 3, 3))

    def draw_text(
        self, text: str, color=ALMOSTBLACK, pos=(0, 0), lineheight=None, **kwargs
    ):
        px, py = pos
        dy = 0
        for line in text.splitlines():
            self.draw_textline(line, color, (px, py + dy), **kwargs)
            dy += lineheight if lineheight else self.lineheight

    # button
    def render_button(self, button):
        button_surf = pg.Surface(button.size)
        button_surf.fill(
            self.colors["Button hovered"] if button.hovered else self.colors["Button"]
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

    def render_text_scene(self, title, text, options):
        # self.display.fill((10, 20, 60))
        self.draw_text(title, pos=(50, 50), size=30)
        self.draw_text(text, pos=(50, 100), size=20)
        self.draw_text(options, pos=(50, 400), size=20)

    def render_dialog(self, title, text, options):
        dialog = pg.Surface(((400, 150)))
        dialog.fill(self.colors["Dialog Background"])
        self.draw_text(title, pos=(20, 20), size=20, onto=dialog)
        self.draw_text(text, pos=(20, 45), size=20, onto=dialog)
        self.draw_text(options, pos=(20, 80), size=20, onto=dialog)
        self.display.blit(dialog, (200, 200))

    def render_tile(self, game_coords, color):
        x, y = game_coords
        rect = pg.draw.polygon(
            surface=self.display,
            points=self.screen_coords([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)]),
            color=color,
        )
        if self.debug:
            pg.draw.rect(self.display, rect=rect, color=self.colors["DEBUG"], width=1)

    def render_tilemap(
        self, tilemap: list[tuple[tuple, tuple, str]], grid=True, info=True, mask=False
    ):
        for pos, color, s in tilemap:
            self.render_tile(pos, color)

        if grid:
            self.draw_grid(
                xrange=(-4, 5),
                yrange=(-4, 5),
                spacing=1,
                labels=True,
                color=self.colors["Grid"],
            )
        if info:
            for pos, color, s in tilemap:
                self.draw_text(
                    s,
                    color,
                    self.screen_coords(pos[0] + 0.3, pos[1] + 0.5),
                )


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((800, 600))

    display = pg.Surface((800, 600))
    camera = Camera2D(display, rotation=30, zoom=(1, 1))
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
        renderer.draw_grid((-400, 400), (-400, 400), spacing=50, labels=True)

        screen.blit(renderer.display, (0, 0))
        pg.display.update()
