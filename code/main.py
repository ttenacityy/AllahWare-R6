import sys, os, importlib, threading
import customtkinter as ctk
from main.functions.recoil_controller import RecoilController
from main.functions.autoclicker import AutoClicker
from main.functions.tbag import TBag
from PIL import Image
from pynput import keyboard

CURRENT_VERSION = "1.0.2"

from main.vcheck import vcheck
vcheck.check_version(CURRENT_VERSION)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

BASE_DIR = resource_path("main")
APPDATA_DIR = r"C:\AllahWare"
CONFIGS_DIR = os.path.join(APPDATA_DIR, "operator_configs")
os.makedirs(CONFIGS_DIR, exist_ok=True)

OPERATORS_DIR = os.path.join(BASE_DIR, "operators")
ICON_PATH = resource_path("main/icon.ico")
IMG_DIR = resource_path("main/img")
PAGE_ICON_DIR = resource_path("pages/page_icons")
PAGES_DIR = resource_path("pages")

PAGE_ORDER = ["Operators", "Control", "Autoclicker", "TBag", "Settings"]

class PageContainer(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#111111", corner_radius=15)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

class RecoilApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Allah Ware")
        self.geometry("1000x650")
        self.minsize(900, 550)
        self.iconbitmap(ICON_PATH)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.overlay_visible = False
        self.attributes("-alpha", 0.0)
        self.OPERATORS_DIR = OPERATORS_DIR
        self.CONFIGS_DIR = CONFIGS_DIR
        self.IMG_DIR = IMG_DIR
        self.PAGE_ICON_DIR = PAGE_ICON_DIR
        self.recoil = RecoilController()
        self.autoclicker = AutoClicker()
        self.tbag = TBag()
        self.pages = {}           
        self.page_containers = {} 
        self.nav_buttons = {}
        self.nav_underlines = {}
        self.current_page = None
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar_panel()
        self.container = ctk.CTkFrame(self, fg_color="#000000", corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self._load_pages()
        if self.pages:
            self.show_page(PAGE_ORDER[0])
        threading.Thread(target=self._start_key_listener, daemon=True).start()

    def _build_sidebar_panel(self):
        outer_strip = ctk.CTkFrame(self, width=240, fg_color="#000000", corner_radius=0)
        outer_strip.grid(row=0, column=0, sticky="nswe")
        outer_strip.grid_propagate(False)

        panel = ctk.CTkFrame(outer_strip, width=220, fg_color="#1a1a1a", corner_radius=12)
        panel.pack(fill="y", expand=True, padx=10, pady=10)

        title = ctk.CTkLabel(panel, text="AllahWare", font=("Segoe UI", 17, "bold"), text_color="#ffffff")
        title.pack(pady=(15, 20))

        self.sidebar = ctk.CTkFrame(panel, fg_color="transparent")
        self.sidebar.pack(fill="both", expand=True, padx=10, pady=10)

    def _load_pages(self):
        sys.path.append(PAGES_DIR)
        for page_name in PAGE_ORDER:
            filename = page_name.lower().replace("-", "_") + ".py"
            filepath = os.path.join(PAGES_DIR, filename)
            if not os.path.isfile(filepath):
                continue
            module = importlib.import_module(f"pages.{filename[:-3]}")
            class_name = page_name.replace("-", "") + "Page"
            if hasattr(module, class_name):
                page_class = getattr(module, class_name)

                container = PageContainer(self.container)
                page = page_class(container, self)
                page.grid(row=0, column=0, sticky="nsew")

                self.pages[page_name] = page
                self.page_containers[page_name] = container

                container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
                container.grid_remove()

                self._add_sidebar_button(page_name)

    def _load_icon(self, page_name):
        filename = page_name.lower().replace("-", "") + ".png"
        path = os.path.join(PAGE_ICON_DIR, filename)
        if os.path.isfile(path):
            img = Image.open(path)
            return ctk.CTkImage(img, size=(18, 18))
        return None

    def _add_sidebar_button(self, page_name):
        icon = self._load_icon(page_name)
        frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame.pack(fill="x", pady=4)

        btn = ctk.CTkButton(
            frame,
            text=page_name,
            image=icon,
            compound="left",
            width=180,
            height=38,
            corner_radius=10,
            fg_color="#000000",
            hover_color="#222222",
            text_color="#cccccc",
            font=("Segoe UI", 13),
            anchor="w",
            command=lambda p=page_name: self.show_page(p),
        )
        btn.pack(fill="x")

        underline = ctk.CTkFrame(frame, height=2, fg_color="transparent")
        underline.pack(fill="x", pady=(0, 2))

        self.nav_buttons[page_name] = btn
        self.nav_underlines[page_name] = underline

    def show_page(self, page_name):
        if self.current_page:
            self.page_containers[self.current_page].grid_remove()

        container = self.page_containers[page_name]
        container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.current_page = page_name

        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(text_color="#ffffff", font=("Segoe UI Semibold", 13), fg_color="#333333")
                self.nav_underlines[name].configure(fg_color="#ffffff")
            else:
                btn.configure(text_color="#cccccc", font=("Segoe UI", 13), fg_color="#000000")
                self.nav_underlines[name].configure(fg_color="transparent")

    def _start_key_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.shift_r:
                    self.toggle_overlay()
            except:
                pass
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def toggle_overlay(self):
        if self.overlay_visible:
            # hide by transparency
            self.attributes("-alpha", 0.0)
            self.overlay_visible = False
        else:
            # show instantly (no redraw)
            self.attributes("-alpha", 1.0)
            self.lift()
            self.focus_force()
            self.overlay_visible = True

if __name__ == "__main__":
    app = RecoilApp()
    app.mainloop()
