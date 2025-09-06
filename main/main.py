import sys, os, urllib.request, webbrowser
import customtkinter as ctk
from PIL import Image
from main.functions.recoil_controller import RecoilController
from main.functions.autoclicker import AutoClicker
from main.functions.tbag import TBag
from pynput import mouse

from pages.operators import OperatorsPage
from pages.control import ControlPage
from pages.autoclicker import AutoclickerPage
from pages.tbag import TBagPage
from pages.settings import SettingsPage

CURRENT_VERSION = "1.0.2"
VERSION_URL = "https://raw.githubusercontent.com/ttenacityy/AllahWare-R6/main/version"
GITHUB_URL = "https://github.com/ttenacityy/AllahWare-R6/tree/main"

def check_version():
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as resp:
            remote_version = resp.read().decode("utf-8").strip()
        if remote_version != CURRENT_VERSION:
            show_update_popup(remote_version)
    except Exception:
        pass

def show_update_popup(remote_version: str):
    popup = ctk.CTk()
    popup.title("Update Available")
    popup.geometry("480x180")

    msg = f"New version available!\nCurrent: {CURRENT_VERSION}\nLatest: {remote_version}\n\nGet it now?"
    label = ctk.CTkLabel(popup, text=msg, font=("Segoe UI", 16), justify="center")
    label.pack(pady=10)

    def on_yes():
        webbrowser.open(GITHUB_URL)
        popup.destroy()
        sys.exit(0)

    def on_no():
        popup.destroy()
        sys.exit(0)

    btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
    btn_frame.pack(pady=10)
    yes_btn = ctk.CTkButton(btn_frame, text="Yes", width=100, command=on_yes)
    yes_btn.grid(row=0, column=0, padx=10)
    no_btn = ctk.CTkButton(btn_frame, text="No", width=100, command=on_no)
    no_btn.grid(row=0, column=1, padx=10)
    popup.protocol("WM_DELETE_WINDOW", on_no)
    popup.mainloop()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

check_version()

BASE_DIR = resource_path("main")
APPDATA_DIR = r"C:\AllahWare"
CONFIGS_DIR = os.path.join(APPDATA_DIR, "operator_configs")
os.makedirs(CONFIGS_DIR, exist_ok=True)

OPERATORS_DIR = os.path.join(BASE_DIR, "operators")
ICON_PATH = resource_path("main/icon.ico")
IMG_DIR = resource_path("main/img")
PAGE_ICON_DIR = resource_path("pages/page_icons")


class RecoilApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Allah Ware")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.iconbitmap(ICON_PATH)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.OPERATORS_DIR = OPERATORS_DIR
        self.CONFIGS_DIR = CONFIGS_DIR
        self.IMG_DIR = IMG_DIR
        self.PAGE_ICON_DIR = PAGE_ICON_DIR

        self.recoil = RecoilController()
        self.autoclicker = AutoClicker()
        self.tbag = TBag()
        self.autoclicker_enabled = False
        self.enabled = False

        self.current_page = None
        self.pages = {}
        self.page_icons = {}

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self.container = ctk.CTkFrame(self, fg_color="#111111")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages["Operators"] = OperatorsPage(self.container, self)
        self.pages["Control"] = ControlPage(self.container, self)
        self.pages["Autoclicker"] = AutoclickerPage(self.container, self)
        self.pages["T-Bag"] = TBagPage(self.container, self)
        self.pages["Settings"] = SettingsPage(self.container, self)

        self.show_page("Operators")

    def _load_page_icon(self, page_name):
        """Try to load icon for page (pages/page_icons/<name>.png)"""
        # Normalized map for special filenames
        name_map = {
            "T-Bag": "tbag.png",
            "Settings": "settings.png",
        }

        file_name = name_map.get(page_name, f"{page_name.lower()}.png")
        path = os.path.join(self.PAGE_ICON_DIR, file_name)
        if os.path.isfile(path):
            img = Image.open(path)
            return ctk.CTkImage(img, size=(20, 20))
        return None

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        sidebar.grid(row=0, column=0, sticky="ns")
        title = ctk.CTkLabel(
            sidebar,
            text="Recoil Control",
            font=("Segoe UI", 20, "bold"),
            text_color="#e6e6e6",
        )
        title.pack(pady=(30, 20))

        self.nav_buttons = {}
        for page in ["Operators", "Control", "Autoclicker", "T-Bag", "Settings"]:
            icon = self._load_page_icon(page)
            self.page_icons[page] = icon

            btn = ctk.CTkButton(
                sidebar,
                text=page,
                image=icon,
                compound="left",
                width=160,
                height=40,
                corner_radius=12,
                fg_color="transparent",
                hover_color="#2a2a2a",
                anchor="w",
                command=lambda p=page: self.show_page(p),
            )
            btn.pack(pady=10, padx=10, fill="x")
            self.nav_buttons[page] = btn

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.grid_forget()
        page = self.pages[page_name]
        page.grid(row=0, column=0, sticky="nsew")
        self.current_page = page
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color="#1f538d" if name == page_name else "transparent")


if __name__ == "__main__":
    app = RecoilApp()
    app.mainloop()
