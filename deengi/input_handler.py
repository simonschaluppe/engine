from functools import partial
import pygame as pg

from .renderables.dialog import Option


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


class InputHandler:
    def __init__(self, screen_coords=None, debug=True):
        self.keypress_bindings = {}
        self.keyrelease_bindings = {}
        self.continuous_keypress_bindings = {}
        self.mousebutton_bindings = {}
        self.continuous_mousebutton_bindings = {}
        
        self.all_binding_dicts = {
            "on keypress": self.keypress_bindings, 
            "on keyrelease": self.keyrelease_bindings, 
            "key hold": self.continuous_keypress_bindings, 
            "mouse press": self.mousebutton_bindings, 
            "mouse hold": self.continuous_mousebutton_bindings
        }
        self.bindings = []
            
        self.clickable_rects = {}
        self.hoverable_rects = {}

        self.buttons = []
        self.screen_coords = screen_coords or (lambda x: x)

        self.debug = debug
        
        

    def get_keybinds(self):
        return sorted(set(self.bindings))

    def register_clickable(self, clickable, callback):
        self.clickable_rects[clickable] = callback

    def register_hover(self, hoverable, callback):
        self.hoverable_rects[hoverable] = callback

    def register_button(self, button):
        """Register a button to be checked for clicks."""
        self.buttons.append(button)

    def bind_keypress(self, key, action, binding_name=None):
        name = binding_name or repr(action)
        self.bindings.append((pg.key.name(key), "key press", name))
        self.keypress_bindings[key] = action

    def bind_keyrelease(self, key, action, binding_name=None):
        name = binding_name or repr(action)
        self.bindings.append((pg.key.name(key), "key release", name))
        self.keyrelease_bindings[key] = action

    def bind_continuous_keypress(self, key, action, binding_name=None):
        name = binding_name or repr(action)
        self.bindings.append((pg.key.name(key), "continuous key hold", name))
        self.continuous_keypress_bindings[key] = action

    def bind_mousebutton_down(self, button, action, binding_name=None):
        """left mousebutton is button 0"""
        name = binding_name or repr(action)
        self.bindings.append((str(button),"Mousebutton click", name))
        self.mousebutton_bindings[button] = action

    def bind_continuous_mousebutton(self, button, action, binding_name=None):
        """left mousebutton is button 0"""
        name = binding_name or repr(action)
        self.bindings.append((str(button+1),"Mousebutton hold", name))
        self.continuous_mousebutton_bindings[button] = action

    def bind_WASD_movement(self, mover, speed: float, turnspeed: float):
        self.bind_continuous_keypress(pg.K_w, lambda: mover.move_in_direction(speed), "Move up")
        self.bind_continuous_keypress(pg.K_s, lambda: mover.move_in_direction(-speed), "Move down")
        self.bind_continuous_keypress(pg.K_a, lambda: mover.turn(angle=turnspeed), "Turn left")
        self.bind_continuous_keypress(pg.K_d, lambda: mover.turn(angle=-turnspeed), "Turn right")

    def bind_camera_zoom_to_mousewheel(self, camera, change=0.1):
        self.bind_mousebutton_down(4, lambda: camera.zoom(1 + change), "Camera Zoom in")
        self.bind_mousebutton_down(5, lambda: camera.zoom(1 - change), "Camera Zoom out")

    def bind_camera_pan_to_arrows_keys(self, camera, speed=1):
        self.bind_continuous_keypress(pg.K_UP, lambda: camera.move((0, speed)), "Camera Pan up")
        self.bind_continuous_keypress(pg.K_DOWN, lambda: camera.move((0, -speed)), "Camera Pan down")
        self.bind_continuous_keypress(pg.K_LEFT, lambda: camera.move((-speed, 0)), "Camera Pan left")
        self.bind_continuous_keypress(pg.K_RIGHT, lambda: camera.move((speed, 0)), "Camera Pan right")

    def bind_camera_rotate_to_arrow_keys(self, camera, speed=0.5):
        self.bind_continuous_keypress(pg.K_UP, partial(camera.tilt, speed / 360), "Camera tilt up")
        self.bind_continuous_keypress(pg.K_DOWN, partial(camera.tilt, -speed / 360), "Camera tilt down")
        self.bind_continuous_keypress(pg.K_LEFT, partial(camera.rotate, speed), "Camera rotate counter-clockwise")
        self.bind_continuous_keypress(pg.K_RIGHT, partial(camera.rotate, -speed), "Camera rotate clockwise")

    def bind_camera_pan_to_mousedrag(self, camera, button=1):
        self.bind_mousebutton_down(button, camera.drag_start,)
        self.bind_continuous_mousebutton(button - 1, camera.move_to, "Camera drag")  # continous

    def bind_options_to_keys(self, options: list[Option]):
        used_keys = []
        prefix = ""
        for i, option in enumerate(options):
            if i < 9 and i + 1 not in used_keys:
                used_keys.append(i + 1)
                self.bind_keypress(49 + i, option.callback)  # 49 = K_1
                prefix = f"{i+1}. "
            first_letter = option.text[:1].lower()
            rest = option.text[1:]
            if first_letter not in used_keys:
                used_keys.append(first_letter)
                self.bind_keypress(ord(first_letter), option.callback)  # 49 = K_1
                option.text = f"[{first_letter.upper()}]{rest}"
            option.text = prefix + option.text

    def handle_mouse_movement(self):
        mousepos = pg.mouse.get_pos()

        for button in self.buttons:
            button.is_hovering(mousepos)

        for hoverable, callback in self.hoverable_rects.items():
            collision = hoverable.collidepoint(mousepos)
            callback(collision)

    def handle_mouse_down(self, event):
        if self.debug:
            print(event.button, pg.mouse.get_pos())

        if event.button in self.mousebutton_bindings:
            self.mousebutton_bindings[event.button]()

        for button in self.buttons:
            if button.is_hovering(pg.mouse.get_pos()):
                button.press()
                break

        for clickable, callback in self.clickable_rects.items():
            if clickable.collidepoint(pg.mouse.get_pos()):
                print("clicked", clickable)
                callback()  # Trigger the callback if click is within rect
                break

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
                self.keypress_bindings[event.key]()
        elif event.type == pg.KEYUP:
            if event.key in self.keyrelease_bindings:
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
