import math
import pygame as pg


def draw_grid(surface, spacing=100, color="blue"):
    for x in range(0, surface.get_width(), spacing):
        pg.draw.line(surface, color, (0, x), (surface.get_width(), x))
        pg.draw.line(surface, color, (x, 0), (x, surface.get_height()))


def hexagon_points(center=pg.Vector2(0, 0), r=1):
    points = []
    for angle in range(0, 360, 60):
        points.append(center + pg.Vector2(r, 0).rotate(angle))
    return points


if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((800, 600))

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

        screen.fill((255, 255, 255))

        center = pg.mouse.get_pos()

        pg.draw.polygon(screen, "green", hexagon_points(center, r=100))

        pg.display.flip()
