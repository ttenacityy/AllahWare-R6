import threading
import time
import win32api
import win32con
from pynput import keyboard


KEY_MAP = {
    keyboard.Key.ctrl_l: win32con.VK_LCONTROL,
    keyboard.Key.ctrl_r: win32con.VK_RCONTROL,
    keyboard.Key.shift: win32con.VK_SHIFT,
    keyboard.Key.space: win32con.VK_SPACE,
}


class TBag:
    def __init__(self):
        self.crouch_key = None
        self.tbag_key = None
        self.delay = 0.05
        self.running = False
        self.thread = None
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()

    def set_crouch_key(self, key):
        if isinstance(key, str) and len(key) == 1:
            self.crouch_key = ord(key.upper())
        elif isinstance(key, keyboard.KeyCode) and key.char:
            self.crouch_key = ord(key.char.upper())
        elif isinstance(key, keyboard.Key):
            self.crouch_key = KEY_MAP.get(key)
        else:
            self.crouch_key = None

    def set_tbag_key(self, key):
        self.tbag_key = key

    def set_delay(self, ms: int):
        self.delay = ms / 1000.0

    def _on_press(self, key):
        if self.tbag_key and key == self.tbag_key and not self.running:
            self.start()

    def _on_release(self, key):
        if self.tbag_key and key == self.tbag_key:
            self.stop()

    def start(self):
        if not self.running and self.crouch_key:
            self.running = True
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        code = self.crouch_key
        scan = win32api.MapVirtualKey(code, 0)
        while self.running:
            win32api.keybd_event(code, scan, 0, 0)
            time.sleep(0.01)
            win32api.keybd_event(code, scan, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(self.delay)
