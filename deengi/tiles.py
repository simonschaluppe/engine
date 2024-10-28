import pygame


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

    def on_click(self):
        print(f"{self} clicked!")
        if self.click_callback:
            self.click_callback()

    def on_hover(self):
        print(f"{self} hovered!")
        if self.hover_callback:
            self.hover_callback()


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
