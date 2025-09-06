import threading
import time
from typing import Optional

import win32api
import win32con
import win32gui
from pynput.mouse import Button, Listener

class MouseController:
    def __init__(self):
        self.position = (0, 0)
        self._remainder_x = 0.0
        self._remainder_y = 0.0
        self.update_position()

    def update_position(self):
        self.position = win32gui.GetCursorPos()

    def move(self, dx: float, dy: float):
        self._remainder_x += dx
        self._remainder_y += dy

        int_dx = int(round(self._remainder_x))
        int_dy = int(round(self._remainder_y))

        if int_dx != 0 or int_dy != 0:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int_dx, int_dy)
            self._remainder_x -= int_dx
            self._remainder_y -= int_dy

        self.update_position()

class MouseListener:
    def __init__(self, on_click=None):
        self.on_click_cb = on_click
        self.listener = None
        self.is_listening = False

    def start_listening(self):
        if not self.is_listening:
            self.listener = Listener(on_click=self._on_click)
            self.listener.start()
            self.is_listening = True

    def stop_listening(self):
        if self.is_listening and self.listener:
            self.listener.stop()
            self.is_listening = False

    def _on_click(self, x, y, button, pressed):
        if self.on_click_cb:
            self.on_click_cb(x, y, button, pressed)

class RecoilController:
    def __init__(self, sensitivity: float = 50.0, dynamic_control: bool = False):
        self.mouse = MouseController()
        self.listener = MouseListener(on_click=self._on_mouse_click)
        self.enabled = False
        self.lbutton_held = False
        self.rbutton_held = False
        self.base_recoil_x = 0.0
        self.base_recoil_y = 0.0
        self._recoil_lock = threading.Lock()
        self._recoil_thread: Optional[threading.Thread] = None
        self.shoot_delay = 0.01
        self.max_movement = 500
        self.sensitivity = sensitivity
        self.dynamic_control = dynamic_control
        self.dynamic_stages = {}

    def start(self):
        if not self.enabled:
            self.enabled = True
            self.listener.start_listening()

    def stop(self):
        if self.enabled:
            self.enabled = False
            self.listener.stop_listening()
            self._stop_recoil_loop()

    def set_recoil_x(self, value: float):
        with self._recoil_lock:
            self.base_recoil_x = value

    def set_recoil_y(self, value: float):
        with self._recoil_lock:
            self.base_recoil_y = value

    def set_sensitivity(self, value: float):
        self.sensitivity = max(1.0, value)

    def set_dynamic_control(self, enabled: bool):
        self.dynamic_control = enabled

    def set_dynamic_stages(self, stages: dict):
        self.dynamic_stages = stages

    def _on_mouse_click(self, x, y, button, pressed):
        if button == Button.left:
            self.lbutton_held = pressed
        elif button == Button.right:
            self.rbutton_held = pressed
        if self.lbutton_held and self.rbutton_held:
            if not (self._recoil_thread and self._recoil_thread.is_alive()):
                self._start_recoil_loop()
        else:
            self._stop_recoil_loop()

    def _start_recoil_loop(self):
        if not self._recoil_thread or not self._recoil_thread.is_alive():
            self._recoil_thread = threading.Thread(
                target=self._recoil_loop, daemon=True
            )
            self._recoil_thread.start()

    def _stop_recoil_loop(self):
        self._recoil_thread = None

    def _recoil_loop(self):
        start_time = time.time()
        try:
            while self.enabled and self.lbutton_held and self.rbutton_held:
                with self._recoil_lock:
                    dx = self.base_recoil_x
                    dy = self.base_recoil_y
                dx *= (self.sensitivity / 50.0)
                dy *= (self.sensitivity / 50.0)
                if self.dynamic_control and self.dynamic_stages:
                    held_time = time.time() - start_time
                    scale = 1.0
                    for stage_time, stage in sorted(
                        ((float(k), v) for k, v in self.dynamic_stages.items()),
                        key=lambda x: x[0],
                    ):
                        if stage["enabled"] and held_time >= stage_time:
                            scale = stage["multiplier"]
                    dx *= scale
                    dy *= scale

                dx = max(-self.max_movement, min(self.max_movement, dx))
                dy = max(-self.max_movement, min(self.max_movement, dy))
                if abs(dx) > 0.001 or abs(dy) > 0.001:
                    self.mouse.move(dx, dy)

                time.sleep(self.shoot_delay)
        except Exception:
            pass
