import threading
import time
from pynput import keyboard

class TBag:
    def __init__(self):
        self.crouch_key = None
        self.tbag_key = None
        self.spam_delay = 0.3
        self.running = False
        self.enabled = False  # <-- controlled by UI toggle
        self.listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
        self.listener.start()
        self.kb = keyboard.Controller()

    def set_crouch_key(self, key):
        self.crouch_key = key

    def set_tbag_key(self, key):
        self.tbag_key = key

    def set_delay(self, ms):
        self.spam_delay = ms / 1000.0

    def _on_press(self, key):
        # Only work if enabled
        if not self.enabled:
            return
        if self.tbag_key and key == self.tbag_key and not self.running:
            self.running = True
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def _on_release(self, key):
        if key == self.tbag_key:
            self.running = False

    def _spam_loop(self):
        while self.running and self.crouch_key and self.enabled:
            self.kb.press(self.crouch_key)
            self.kb.release(self.crouch_key)
            time.sleep(self.spam_delay)
