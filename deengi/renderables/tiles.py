import math
import pygame

from deengi.renderables.renderable import RenderGroup, Renderable


class Tile(Renderable):
    id = 0

    def __init__(
        self,
        game_position,
        size,
        img=None,
        color=None,
        click_callback=None,
        hover_callback=None,
        use_mask=False,
        name=None,
    ):
        self.id = Tile.id
        Tile.id += 1
        self.name = name or f"Tile {self.id}"
        self.pos = game_position  # game coords, not screen coords
        self.screen_pos = None
        self.size = size  # (width, height)
        self.screen_size = None
        if img:
            self.img = pygame.image.load(img).convert_alpha()
            self.img.set_colorkey((255, 0, 255))
        else:
            self.img = None
        self.color = color or (255, 255, 255)
        self.clicked = False
        self.hovered = False

        self.click_callback = click_callback
        self.hover_callback = hover_callback

        self.use_mask = use_mask
        self.mask = None
        self._rect = pygame.Rect(0, 0, self.size[0], self.size[1])

    @property
    def rect(self):
        return self._rect

    def collidepoint(self, point):
        """all in screen coords"""
        if not self.use_mask or not self.mask:
            return self.rect.collidepoint(point)

        return self.mask.get_at(point)

    def create_mask(self, renderer):
        surf = pygame.Surface(renderer.display.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(
            surface=surf,
            points=self.points(renderer),
            color=(255, 255, 255),
        )
        self.mask = pygame.mask.from_surface(surf)

    def points(self, renderer):
        x, y = self.pos
        dx, dy = self.size
        return renderer.screen_coords(
            [(x, y), (x + dx, y), (x + dx, y + dy), (x, y + dy)]
        )

    def render_area(self, renderer):
        pygame.draw.polygon(
            surface=renderer.display,
            points=self.points(renderer),
            color=self.color,
        )

    def render_img(self, renderer):
        # easier, works, but tile images that are larger than the tile will get squished
        # Get the points in screen coordinates
        # points = self.points(renderer)

        # # Calculate the bounding box from the points
        # min_x = min(point[0] for point in points)
        # max_x = max(point[0] for point in points)
        # min_y = min(point[1] for point in points)
        # max_y = max(point[1] for point in points)

        # # Create a bounding rectangle
        # bounding_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
        # # Scale the image to fit within the bounding rectangle
        # scaled_img = pygame.transform.scale(
        #     self.img, (bounding_rect.width, bounding_rect.height)
        # )

        # # Blit the scaled image to the top-left corner of the bounding rectangle
        # renderer.display.blit(scaled_img, bounding_rect.topleft)

        # complicated but works for images taller than thebuilding rectangle
        zoom_x, zoom_y = renderer.camera.zoom_level
        target_diagonal = 1.414
        img_width, img_height = self.img.get_size()
        img_diagonal = math.sqrt(img_width**2 + img_height**2)

        # Get the zoom level from the renderer
        zoom_x, zoom_y = renderer.camera.zoom_level

        # Calculate scale factor based on target diagonal and zoom
        scale_factor = (target_diagonal / img_diagonal) * zoom_x

        # Scale the image
        scaled_width = int(img_width * scale_factor)
        scaled_height = int(img_height * scale_factor)
        scaled_img = pygame.transform.scale(self.img, (scaled_width, scaled_height))

        # Calculate the center position and adjust for the new size
        center_pos = (self.pos[0] + 0.5, self.pos[1] + 0.5)
        screen_center = renderer.screen_coords(center_pos)

        # Calculate top-left position to blit the centered image
        top_left = (
            screen_center[0] - scaled_img.get_width() // 2,
            screen_center[1] - scaled_img.get_height() // 2,
        )

        # Blit the scaled image
        renderer.display.blit(scaled_img, top_left)

    def render(self, renderer):
        if self.use_mask:
            self.create_mask(renderer)
        self.screen_pos = renderer.screen_coords(self.pos)
        self._rect = renderer.screen_coords(pygame.Rect(*self.pos, *self.size))

        if self.img:
            self.render_img(renderer)

        else:
            self.render_area(renderer)

        if renderer.debug:
            pygame.draw.rect(
                renderer.display,
                rect=self.rect,
                color=renderer.get_color("DEBUG"),
                width=1,
            )
            if self.use_mask:
                mask_surface = self.mask.to_surface(
                    setcolor=renderer.get_color("DEBUG"), unsetcolor=(0, 0, 0, 0)
                )
                renderer.display.blit(mask_surface, (0, 0))


class Tilemap(RenderGroup):
    def __init__(self, tile_tuples=None):
        """Iterable Tilemap of Tiles"""
        tile_tuples = tile_tuples or []
        for args in tile_tuples:
            self.add(Tile(*args))

        self.grid = True

    def as_dict(self):
        return {t.position: t for t in self.tiles}


class Grid(Renderable):
    def __init__(
        self,
        xrange: tuple,
        yrange: tuple,
        spacing=(1, 1),
        color="blue",
        labels=True,
        width=1,
    ):
        self.minx, self.maxx = xrange
        self.miny, self.maxy = yrange
        if isinstance(spacing, (tuple, list)):
            self.dx, self.dy = spacing
        else:
            self.dx = self.dy = spacing
        if isinstance(color, str):
            self.colorx = self.colory = color
        else:
            self.colorx, self.colory = color, color

        self.show_labels = labels
        self.label_spacing = labels * 1
        self.width = width

    def render(self, renderer):

        for x in range(self.minx, self.maxx + 1, self.dx):
            pygame.draw.line(
                renderer.display,
                self.colorx,
                *renderer.screen_coords([(x, self.miny), (x, self.maxy)]),
                width=self.width,
            )
            if (
                self.label_spacing and (x % self.label_spacing == 0) and x < self.maxx
            ):  # x axis
                renderer.draw_text(
                    str(x),
                    color=self.colorx,
                    pos=renderer.screen_coords((x + 0.5, self.miny - 0.5)),
                )

        for y in range(self.miny, self.maxy + 1, self.dy):
            pygame.draw.line(
                renderer.display,
                self.colory,
                *renderer.screen_coords([(self.minx, y), (self.maxx, y)]),
                width=self.width,
            )
            if self.label_spacing and (y % self.label_spacing == 0) and y < self.maxy:
                renderer.draw_text(
                    str(y),
                    color=self.colory,
                    pos=renderer.screen_coords((self.minx - 0.5, y + 0.5)),
                )
