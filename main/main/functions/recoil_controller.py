# main/functions/recoil_controller.py

import logging
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
        self.update_position()

    def update_position(self):
        self.position = win32gui.GetCursorPos()

    def move(self, dx: float, dy: float):
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy))
        self.update_position()

class MouseListener:
    def __init__(self, on_click=None, on_move=None):
        self.on_click_cb = on_click
        self.on_move_cb = on_move
        self.listener = None
        self.is_listening = False

    def start_listening(self):
        if not self.is_listening:
            self.listener = Listener(
                on_click=self._on_click,
                on_move=self._on_move
            )
            self.listener.start()
            self.is_listening = True

    def stop_listening(self):
        if self.is_listening and self.listener:
            self.listener.stop()
            self.is_listening = False

    def _on_click(self, x, y, button, pressed):
        if self.on_click_cb:
            self.on_click_cb(x, y, button, pressed)

    def _on_move(self, x, y):
        if self.on_move_cb:
            self.on_move_cb(x, y)

class RecoilController:
    def __init__(self):
        self.mouse = MouseController()
        self.listener = MouseListener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move
        )

        self.enabled = False
        self.lbutton_held = False
        self.rbutton_held = False

        self.base_recoil_x = 0.0
        self.base_recoil_y = 0.0

        self._recoil_lock = threading.Lock()
        self._recoil_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)

        self.shoot_delay = 0.01   
        self.max_movement = 500  

    def start(self):
        if not self.enabled:
            self.enabled = True
            self.listener.start_listening()
            self.logger.info("[RecoilController] Started.")

    def stop(self):
        if self.enabled:
            self.enabled = False
            self.listener.stop_listening()
            self._stop_recoil_loop()
            self.logger.info("[RecoilController] Stopped.")

    def set_recoil_x(self, value: float):
        with self._recoil_lock:
            self.base_recoil_x = value
        self.logger.debug(f"[RecoilController] Recoil X set to {value:.2f}")

    def set_recoil_y(self, value: float):
        with self._recoil_lock:
            self.base_recoil_y = value
        self.logger.debug(f"[RecoilController] Recoil Y set to {value:.2f}")

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

    def _on_mouse_move(self, x, y):
        self.mouse.update_position()

    def _start_recoil_loop(self):
        if not self._recoil_thread or not self._recoil_thread.is_alive():
            self._recoil_thread = threading.Thread(
                target=self._recoil_loop, daemon=True
            )
            self._recoil_thread.start()
            self.logger.info("[RecoilController] Recoil loop started.")

    def _stop_recoil_loop(self):
        self._recoil_thread = None
        self.logger.info("[RecoilController] Recoil loop stopped.")

    def _recoil_loop(self):
        try:
            shot_count = 0
            while self.enabled and self.lbutton_held and self.rbutton_held:
                shot_count += 1

                with self._recoil_lock:
                    dx = self.base_recoil_x
                    dy = self.base_recoil_y

                dx = max(-self.max_movement, min(self.max_movement, dx))
                dy = max(-self.max_movement, min(self.max_movement, dy))

                if abs(dx) > 0.01 or abs(dy) > 0.01:
                    self.mouse.move(dx, dy)
                    self.logger.debug(f"[RecoilController] Correction: dx={dx:.2f}, dy={dy:.2f}")

                time.sleep(self.shoot_delay)
        except Exception as e:
            self.logger.error(f"[RecoilController] Error in loop: {e}")
        finally:
            self.logger.info("[RecoilController] Recoil loop ended.")

def run_recoil_controller_standalone():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    controller = RecoilController()
    controller.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        controller.stop()
        logging.info("Stopped via KeyboardInterrupt.")


if __name__ == "__main__":
    run_recoil_controller_standalone()

