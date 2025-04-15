import math
from typing import Protocol
import pygame as pg
import logging

logging.basicConfig(level=logging.WARNING)


class Camera(Protocol):
    def project(self, sprite): ...

    def game_coords(self, screen_coords: pg.Vector2) -> pg.Vector2: ...

    def screen_coords(self, game_coords: pg.Vector2) -> pg.Vector2: ...

    def view_rect(self):
        """camera view rectangle in game coordinates"""
        ...


class Camera2D(Camera):
    def __init__(
        self,
        surface: pg.Surface = None,
        game_world_position=(0, 0),
        zoom: tuple = (1, 1),
        rotation: int = 0,
        flatness=1,
        debug=False,
    ):
        self.screen = surface or pg.display.get_surface()
        self.screen_width, self.screen_height = self.screen.get_size()
        # center camera focus in screen center
        self.proj_center = pg.Vector2(self.screen_width // 2, self.screen_height // 2)
        self.proj_startpoint = self.proj_center
        # self.drag_startpoint = self.proj_center
        self.position = pg.Vector2(*game_world_position)
        self.rotation = rotation
        self.flatness = flatness
        self.ex, self.ey = self.get_transformation_matrix(self.rotation, self.flatness)
        self.zoom_level = zoom
        self.follows = None
        self.relative_speed = pg.Vector2(0, 0)  # in game coordinates?

        self.debug = debug

    def drag_start(self):
        mouse_pos = pg.mouse.get_pos()
        self.drag_startpoint = pg.Vector2(mouse_pos)
        self.proj_startpoint = self.proj_center

    def move_to(self):
        direction = pg.mouse.get_pos() - self.drag_startpoint
        if self.debug:
            logging.debug(
                f"Dragging camera from {self.drag_startpoint} to current {pg.mouse.get_pos()} by {direction}"
            )
        self.proj_center = self.proj_startpoint + direction

    def set_game_position(self, pos):
        self.position = pg.Vector2(*pos)

    def set_isometry(self, flatness):
        """1 = No Isometry
        0 = Infinitely flat (capped to 0.05)"""
        self.flatness = max(0.05, min(flatness, 1))
        self.ex, self.ey = self.get_transformation_matrix(self.rotation, self.flatness)

    def tilt(self, amount):
        self.set_isometry(self.flatness + amount)

    def set_rotation(self, rotation):
        self.rotation = rotation % 360
        self.ex, self.ey = self.get_transformation_matrix(self.rotation, self.flatness)

    def rotate(self, angle):
        self.set_rotation(self.rotation + angle)

    def get_transformation_matrix(self, rotation, flatness):
        ex = pg.Vector2(
            math.cos(rotation / 360 * 2 * math.pi),
            flatness * math.sin(rotation / 360 * 2 * math.pi),
        )
        ey = -pg.Vector2(
            -math.sin(rotation / 360 * 2 * math.pi),
            flatness * math.cos(rotation / 360 * 2 * math.pi),
        )
        return ex, ey

    def follow(self, Node, maxdist=1):
        self.maxdist = maxdist  # is in screencoords, should be game coords?
        self.follows = Node

    def update(self):
        if self.follows is not None:
            screendist = self.screen_coords(self.follows.position) - self.screen_coords(
                self.position
            )
            gap = screendist.length() - self.maxdist
            if gap > 0:
                self.position.move_towards_ip(self.follows.position, gap)

    # @property
    # def view_rect(self):
    #     rect = pg.Rect(
    #         self.position.x - self.screen_width / 2 / self.zoom_level[0],
    #         self.position.y - self.screen_height / 2 / self.zoom_level[1],
    #         self.position.x + self.screen_width / 2 / self.zoom_level[0],
    #         self.position.y + self.screen_height / 2 / self.zoom_level[1],
    #     )
    #     return rect

    # def project(self, sprite: pg.sprite.Sprite):
    #     image = pg.transform.scale_by(sprite.image, self.zoom_level)
    #     rect = self.project_rect(sprite.rect)
    #     return image, rect

    # def project_rect(
    #     self, rect: pg.Rect
    # ) -> pg.Rect:  # TODO: this should just be in screen coords
    #     v_game = pg.Vector2(rect.center[0], rect.center[1])
    #     v_proj = self.screen_coords(v_game)
    #     dx = v_proj.x - v_game.x
    #     dy = v_proj.y - v_game.y
    #     # dx = self.proj_loc_on_screen_x + projector_x - game_x
    #     # dy = self.proj_loc_on_screen_y + projector_y - game_y
    #     screenrect = rect.move(dx, dy)
    #     screenrect.scale_by_ip(*self.zoom_level)
    #     return screenrect

    def screen_coords(self, game_coords):
        """
        Convert game-space coordinates to screen-space coordinates.

        This method transforms various types of game-space coordinates into screen-space
        coordinates, taking into account camera position, zoom level, and projection.

        Parameters:
        ----------
        game_coords : list, pg.Rect, tuple, or pg.Vector2
        The game-space coordinates to convert. Can be provided as:
        - A single pg.Vector2 or tuple representing a point.
        - A pg.Rect, representing a rectangular area, which will be scaled to screen-space.
        - A list of points, each as a tuple or pg.Vector2, which will be recursively converted.

        Returns:
        -------
        pg.Vector2 or pg.Rect or list
        - If `game_coords` is a single point (pg.Vector2 or tuple), returns the corresponding
            screen-space pg.Vector2.
        - If `game_coords` is a pg.Rect, returns a pg.Rect in screen-space with scaled width and height.
        - If `game_coords` is a list of points, returns a list of converted pg.Vector2 objects.

        Notes:
        -----
        - This method accounts for camera position and zoom level, converting game coordinates
          relative to the camera's view.
        - For rectangular areas (pg.Rect), the bottom-left corner is converted, and the width and
          height are scaled by the zoom level, corresponding with a flip of the y-axis
        """
        if isinstance(game_coords, list):
            return [self.screen_coords(v) for v in game_coords]
        elif isinstance(game_coords, pg.Rect):
            top_left = pg.Vector2(game_coords.bottomleft)
            screen_top_left = self.screen_coords(top_left)
            width = game_coords.width * self.zoom_level[0]
            height = game_coords.height * self.zoom_level[1]
            return pg.Rect(screen_top_left, (width, height))
        elif type(game_coords) is not pg.Vector2:
            return self.screen_coords(pg.Vector2(*game_coords))
        else:
            x, y = game_coords - self.position
            x_camera = (x * self.ex[0] + y * self.ey[0]) * self.zoom_level[0]
            y_camera = (x * self.ex[1] + y * self.ey[1]) * self.zoom_level[1]
            return pg.Vector2(x_camera, y_camera) + self.proj_center

    # def game_coords(self, screen_coords) -> pg.Vector2:
    #     if isinstance(screen_coords, list):
    #         return [self.screen_coords(v) for v in screen_coords]
    #     elif type(screen_coords) is not pg.Vector2:
    #         return self.screen_coords(pg.Vector2(*screen_coords))
    #     else:
    #         x, y = screen_coords - self.proj_center
    #         x_game = x / self.zoom_level[0]
    #         y_game = -(y / self.ey) / self.zoom_level[1]
    #         return pg.Vector2(x_game, y_game) + self.position

    def game_coords(self, screen_coords) -> pg.Vector2:
        """
        Convert screen-space coordinates to game-space coordinates.

        Parameters:
        ----------
        screen_coords : list, pg.Rect, tuple, or pg.Vector2
            The screen-space coordinates to convert. Can be:
            - A single pg.Vector2 or tuple representing a point.
            - A pg.Rect, representing a rectangular area, which will be scaled back to game-space.
            - A list of points, each as a tuple or pg.Vector2, which will be recursively converted.

        Returns:
        -------
        pg.Vector2 or pg.Rect or list
            - If `screen_coords` is a single point, returns the corresponding game-space pg.Vector2.
            - If `screen_coords` is a pg.Rect, returns a pg.Rect in game-space with adjusted width and height.
            - If `screen_coords` is a list of points, returns a list of converted pg.Vector2 objects.

        Notes:
        -----
        - This method inverts the screen_coords transformation, taking into account zoom level,
        camera position, and projection center.
        """
        # Handle list input by recursively converting each point
        if isinstance(screen_coords, list):
            return [self.game_coords(v) for v in screen_coords]

        # Handle Rect input by converting its top-left corner and adjusting dimensions
        elif isinstance(screen_coords, pg.Rect):
            top_left = pg.Vector2(screen_coords.topleft)
            game_top_left = self.game_coords(top_left)
            width = screen_coords.width / self.zoom_level[0]
            height = screen_coords.height / self.zoom_level[1]
            return pg.Rect(game_top_left, (width, height))

        # Convert tuples to pg.Vector2 for consistency
        elif type(screen_coords) is not pg.Vector2:
            return self.game_coords(pg.Vector2(*screen_coords))

        # Apply the inverse transformation for a single point
        else:
            # Step 1: Offset from the projection center
            x, y = screen_coords - self.proj_center

            # Step 2: Reverse zoom scaling
            x /= self.zoom_level[0]
            y /= self.zoom_level[1]

            # Step 3: Apply the inverse of the camera basis vectors
            x_game = (x * self.ey[1] - y * self.ey[0]) / (
                self.ex[0] * self.ey[1] - self.ex[1] * self.ey[0]
            )
            y_game = (y * self.ex[0] - x * self.ex[1]) / (
                self.ex[0] * self.ey[1] - self.ex[1] * self.ey[0]
            )

            # Return the calculated game-space position, adjusted by the camera position
            return pg.Vector2(x_game, y_game) + self.position

    def zoom(self, factor):
        """single factor or tuple (x,y) factor"""
        if isinstance(factor, int) or isinstance(factor, float):
            factorx = factory = factor
        elif len(factor) == 2:
            factorx, factory = factor
        else:
            raise ValueError
        x, y = self.zoom_level
        self.zoom_level = (x * factorx, y * factory)

    def move(self, xy_tuple):
        # should be in screen coordinates, not in game coordinates
        self.position += pg.Vector2(*xy_tuple)

    def reset(self):
        self.zoom_level = (1, 1)
        self.position = pg.Vector2(0, 0)
        if self.follows is not None:
            logging.debug("resetting camera to follow")
            self.position.xy = self.follows.position.xy

    def __repr__(self) -> str:
        return f"Camera(screen={self.screen.get_size()}, game_pos={self.position}, {self.zoom_level=})"
