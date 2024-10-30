import pygame

from .ui import Tooltip


class Tile:
    def __init__(
        self,
        game_position,
        size,
        color=None,
        click_callback=None,
        hover_callback=None,
    ):
        self.position = game_position  # game coords, not screen coords
        self.size = size  # (width, height)
        self.color = color or (255, 255, 255)
        self.clicked = False
        self.hovered = False

        self.click_callback = click_callback
        self.hover_callback = hover_callback

    @property
    def rect(self):
        return pygame.Rect(self.position, self.size)

    def render(self, renderer):
        x, y = self.position
        dx, dy = self.size
        rect = pygame.draw.polygon(
            surface=renderer.display,
            points=renderer.screen_coords(
                [(x, y), (x + dx, y), (x + dx, y + dy), (x, y + dy)]
            ),
            color=self.color,
        )


class Tilemap:
    def __init__(self, tile_tuples=None):
        self.tiles = []
        tile_tuples = tile_tuples or []
        for args in tile_tuples:
            self.add(Tile(*args))

        self.grid = True

    def __iter__(self):
        """Make Tilemap iterable by returning an iterator over the tiles."""
        return iter(self.tiles)

    def as_list(self):
        return self.tiles

    def as_dict(self):
        return {t.position: t for t in self.tiles}

    def add(self, tile: Tile):
        self.tiles.append(tile)

    def render(self, renderer):
        for tile in self.as_list():
            tile.render(renderer)


class Grid:
    def __init__(
        self,
        xrange: tuple,
        yrange: tuple,
        spacing=1,
        color="blue",
        labels=True,
        width=1,
    ):
        self.minx, self.maxx = xrange
        self.miny, self.maxy = yrange
        self.spacing = spacing
        self.color = color
        self.show_labels = labels
        self.width = width

    def render(self, renderer):
        for x in range(self.minx, self.maxx + 1, self.spacing):
            pygame.draw.line(
                renderer.display,
                self.color,
                *renderer.screen_coords([(x, self.miny), (x, self.maxy)]),
                width=self.width,
            )
            if self.show_labels and x < self.maxx:  # x axis
                renderer.draw_text(
                    str(x), pos=renderer.screen_coords(x + 0.5, self.miny - 0.5)
                )

        for y in range(self.miny, self.maxy + 1, self.spacing):
            pygame.draw.line(
                renderer.display,
                self.color,
                *renderer.screen_coords([(self.minx, y), (self.maxx, y)]),
                width=self.width,
            )
            if self.show_labels and y < self.maxy:
                renderer.draw_text(
                    str(y), pos=renderer.screen_coords(self.minx - 0.5, y + 0.5)
                )
