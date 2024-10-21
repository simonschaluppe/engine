import pygame


class Tile:
    def __init__(
        self,
        game_position,
        size,
        color=None,
        click_callback=None,
        hover_callback=None,
        image=None,
        mask=None,
    ):
        self.position = game_position  # game coords, not screen coords
        self.size = size  # (width, height)
        self.color = color or (255, 255, 255)
        self.image = image
        self.mask = mask  #     or pygame.mask.from_surface(image)
        self.clicked = False
        self.hovered = False

        self.click_callback = click_callback
        self.hover_callback = hover_callback

    def on_click(self):
        print(f"{self} clicked!")
        if self.click_callback:
            self.click_callback()

    def on_hover(self):
        print(f"{self} hovered!")
        if self.hover_callback:
            self.hover_callback()


class Tilemap:
    def __init__(self, positions, sizes, colors):
        self.tiles = []
        for pos, size, color in zip(positions, sizes, colors):
            self.add(Tile(pos, size, color))

        self.grid = True

    def as_list(self):
        return self.tiles

    def as_dict(self):
        return {t.position: t for t in self.tiles}

    def add(self, tile: Tile):
        self.tiles.append(tile)
