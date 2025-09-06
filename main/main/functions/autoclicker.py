import threading
import time
from pynput.mouse import Controller, Button

class AutoClicker:
    def __init__(self):
        self.running = False
        self.thread = None
        self.cps = 10
        self.mouse = Controller()

    def set_cps(self, cps: int):
        self.cps = max(1, cps)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._click_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        self.thread = None

    def _click_loop(self):
        delay = 1.0 / self.cps
        while self.running:
            self.mouse.click(Button.left) 
            time.sleep(delay)
