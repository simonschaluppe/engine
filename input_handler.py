from functools import partial
import pygame as pg


class Clickable:
    mask: pg.Mask
    rect: pg.Rect
    callback: callable

    def __init__(self, mask: pg.Mask, callback: callable):
        self.mask = mask
        self.rect = mask.get_rect()
        self.callback = callback

    def collides(self, other: tuple[int, int]) -> bool:
        if self.rect.collidepoints(other):
            return True
            print("need to check mask!")
        return False


class Button:
    def __init__(self, pos, callback, text="", size=(150, 40)):
        self.position = pos
        self.size = size
        self.text = text
        self.callback = callback
        self.hovered = False
        self.pressed = False

    def release(self):
        self.pressed = False
        self.callback()

    def press(self):
        self.pressed = True

    def is_hovering(self, mouse_pos):
        """Check if the mouse is over the button."""
        x, y = self.position
        w, h = self.size
        self.hovered = x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
        self.pressed = min(self.pressed, self.hovered)
        return self.hovered


class InputHandler(object):
    def __init__(self):
        self.keypress_bindings = {}
        self.keyrelease_bindings = {}
        self.continuous_keypress_bindings = {}
        self.mousebutton_bindings = {}
        self.continuous_mousebutton_bindings = {}

        self.buttons = []

        # needs to keep track of a list of clickables
        # the clickables should be twostaged:
        # first check for "Rect" collisiions
        # if yes, then check for mask collision
        # the callback works like buttons?
        #

    def register_button(self, button):
        """Register a button to be checked for clicks."""
        self.buttons.append(button)

    def bind_keypress(self, key, action):
        self.keypress_bindings[key] = action

    def bind_keyrelease(self, key, action):
        self.keyrelease_bindings[key] = action

    def bind_continuous_keypress(self, key, action):
        self.continuous_keypress_bindings[key] = action

    def bind_mousebutton_down(self, button, action):
        """left mousebutton is button 1"""
        self.mousebutton_bindings[button] = action

    def bind_continuous_mousebutton(self, button, action):
        """left mousebutton is button 0"""
        self.continuous_mousebutton_bindings[button] = action

    def bind_WASD_movement(self, mover, speed: float, turnspeed: float):
        self.bind_continuous_keypress(pg.K_w, lambda: mover.move_in_direction(speed))
        self.bind_continuous_keypress(pg.K_s, lambda: mover.move_in_direction(-speed))
        self.bind_continuous_keypress(pg.K_a, lambda: mover.turn(angle=turnspeed))
        self.bind_continuous_keypress(pg.K_d, lambda: mover.turn(angle=-turnspeed))

    def bind_camera_zoom_to_mousewheel(self, camera, change=0.1):
        self.bind_mousebutton_down(4, lambda: camera.zoom(1 + change))
        self.bind_mousebutton_down(5, lambda: camera.zoom(1 - change))

    def bind_camera_pan_to_arrows_keys(self, camera, speed=1):
        self.bind_continuous_keypress(pg.K_UP, lambda: camera.move((0, speed)))
        self.bind_continuous_keypress(pg.K_DOWN, lambda: camera.move((0, -speed)))
        self.bind_continuous_keypress(pg.K_LEFT, lambda: camera.move((-speed, 0)))
        self.bind_continuous_keypress(pg.K_RIGHT, lambda: camera.move((speed, 0)))

    def bind_camera_pan_to_mousedrag(self, camera, button=1):
        self.bind_mousebutton_down(button, camera.drag_start)
        self.bind_continuous_mousebutton(button - 1, camera.move_to)  # continous

    def handle_mouse_movement(self):
        mousepos = pg.mouse.get_pos()
        for button in self.buttons:
            button.is_hovering(mousepos)

    def handle_mouse_down(self, event):
        print(event.button)
        if event.button in self.mousebutton_bindings:
            self.mousebutton_bindings[event.button]()
        for button in self.buttons:
            if button.is_hovering(pg.mouse.get_pos()):
                button.press()

    def handle_mouse_up(self, event):
        if event.button != 1:
            return
        for button in self.buttons:
            if button.is_hovering(pg.mouse.get_pos()):
                button.release()

    def handle_event(self, event: pg.event):
        if event.type == pg.QUIT:
            print("quitting...")
            pg.quit()
            quit()
        elif event.type == pg.KEYDOWN:
            if event.key in self.keypress_bindings:
                # print(
                #     f"key pressed: {event.key} > calling {self.keypress_bindings[event.key].__name__}"
                # )
                self.keypress_bindings[event.key]()
        elif event.type == pg.KEYUP:
            if event.key in self.keyrelease_bindings:
                # print( # __name__ does not work with partial(function) callbacks
                #    f"key released: {event.key} > calling {self.keyrelease_bindings[event.key].__name__}"
                # )
                self.keyrelease_bindings[event.key]()
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event)
        elif event.type == pg.MOUSEBUTTONUP:
            self.handle_mouse_up(event)

    def handle_continuous_keypresses(self):
        keys = pg.key.get_pressed()
        for key, action in self.continuous_keypress_bindings.items():
            if keys[key]:
                action()

    def handle_continuous_mousebuttons(self):
        buttons = (
            pg.mouse.get_pressed()
        )  # returns tuple of bools, in order of mouse button
        for button, action in self.continuous_mousebutton_bindings.items():
            if buttons[button]:
                action()

    def update(self):
        self.handle_mouse_movement()
        for event in pg.event.get():
            self.handle_event(event)
        self.handle_continuous_keypresses()
        self.handle_continuous_mousebuttons()

    def reset(self):
        self.keypress_bindings = {}
        # self.keyrelease_bindings = {}
        # self.continuous_keypress_bindings = {}
        # self.mousebutton_bindings = {}
        # self.continuous_mousebutton_bindings = {}

        self.buttons = []
