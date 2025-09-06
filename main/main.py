import sys, os, json, urllib.request, webbrowser
import customtkinter as ctk
from PIL import Image
from main.functions.recoil_controller import RecoilController
from main.functions.autoclicker import AutoClicker
from pynput import mouse

CURRENT_VERSION = "1.0.0"
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
    """ Get absolute path to resource (works for dev and for PyInstaller exe) """
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

DISPLAY_ORDER = {
    "attackers": ["striker","sledge","thatcher","ash","thermite","twitch","montagne","glaz","fuze","blitz","iq","buck","blackbeard","capitao","hibana","jackal","ying","zofia","dokkaebi","lion","finka","maverick","nomad","gridlock","nokk","amaru","kali","iana","ace","zero","flores","osa","sens","grim","brava","ram","deimos","rauora"],
    "defenders": ["sentry","smoke","mute","castle","pulse","doc","rook","kapkan","tachanka","jager","bandit","frost","valkyrie","caveira","echo","mira","lesion","ela","vigil","maestro","alibi","clash","kaid","mozzie","warden","goyo","wamai","oryx","melusi","aruni","thunderbird","thorn","azami","solis","fenrir","tubarao","skopos","denari"],
}


class RecoilApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Allah Ware")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.iconbitmap(ICON_PATH)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.current_page = None
        self.current_side = "attackers"
        self.selected_operator = None
        self.operator_frames = {}
        self.operator_images = {}
        self.operator_side_map = {}
        self.all_operators = {"attackers": [], "defenders": []}
        self.recoil = RecoilController()
        self.enabled = False

        self.listening_for_key = False
        self.ignore_next_click = False
        self.bound_key = None
        self.bound_display = None

        self.left_img = ctk.CTkImage(Image.open(os.path.join(IMG_DIR, "leftclick.png")), size=(48, 48))
        self.right_img = ctk.CTkImage(Image.open(os.path.join(IMG_DIR, "rightclick.png")), size=(48, 48))
        self.loading_img = ctk.CTkImage(Image.open(os.path.join(IMG_DIR, "loading.png")), size=(48, 48))
        mouse4_path = os.path.join(IMG_DIR, "mouse4.png")
        mouse5_path = os.path.join(IMG_DIR, "mouse5.png")
        self.mouse4_img = ctk.CTkImage(Image.open(mouse4_path), size=(48, 48)) if os.path.isfile(mouse4_path) else None
        self.mouse5_img = ctk.CTkImage(Image.open(mouse5_path), size=(48, 48)) if os.path.isfile(mouse5_path) else None

        self.autoclicker = AutoClicker()
        self.autoclicker_enabled = False
        self.listener = mouse.Listener(on_click=self._on_global_mouse)
        self.listener.start()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self.container = ctk.CTkFrame(self, fg_color="#111111")
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.pages = {}
        self._create_pages()
        self._load_all_operators()
        self._create_all_configs()
        self.show_page("Operators")

        self.bind_all("<Button>", self._on_mouse_press)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        sidebar.grid(row=0, column=0, sticky="ns")
        title = ctk.CTkLabel(sidebar, text="Recoil Control", font=("Segoe UI", 20, "bold"), text_color="#e6e6e6")
        title.pack(pady=(30, 20))
        self.nav_buttons = {}
        for page in ["Operators", "Control", "Autoclicker"]:
            btn = ctk.CTkButton(sidebar, text=page, width=160, height=40, corner_radius=12,
                                fg_color="transparent", hover_color="#2a2a2a",
                                anchor="center", command=lambda p=page: self.show_page(p))
            btn.pack(pady=10)
            self.nav_buttons[page] = btn

    def _create_pages(self):
        operators_page = ctk.CTkFrame(self.container, fg_color="#111111")
        operators_page.grid_rowconfigure(2, weight=1)
        operators_page.grid_columnconfigure(0, weight=1)
        self.pages["Operators"] = operators_page

        self.side_selector = ctk.CTkSegmentedButton(operators_page,
            values=["Attackers", "Defenders"], command=self._on_side_changed)
        self.side_selector.set("Attackers")
        self.side_selector.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(operators_page, placeholder_text="Search operators...",
                                    textvariable=self.search_var)
        search_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.search_var.trace_add("write", lambda *_: self._refresh_operator_grid())

        self.operator_scroll = ctk.CTkScrollableFrame(operators_page, fg_color="transparent")
        self.operator_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        self.operator_scroll.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)

        control_page = ctk.CTkFrame(self.container, fg_color="#111111")
        control_page.grid_rowconfigure(0, weight=1)
        control_page.grid_columnconfigure(0, weight=1)
        self.pages["Control"] = control_page

        card = ctk.CTkFrame(control_page, corner_radius=15, fg_color="#1a1a1a",
                            border_width=2, border_color="#333333")
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)
        title = ctk.CTkLabel(card, text="Control Settings", font=("Segoe UI", 20, "bold"), text_color="#e6e6e6")
        title.pack(pady=20)
        self.toggle_button = ctk.CTkButton(card, text="DISABLED", width=120, height=40,
                                           corner_radius=10, fg_color="#c44242",
                                           hover_color="#a23232", command=self._toggle_enabled)
        self.toggle_button.pack(pady=10)
        self.y_value = ctk.StringVar(value="0.000")
        y_label = ctk.CTkLabel(card, text="Vertical Recoil (Y)", font=("Segoe UI", 16))
        y_label.pack()
        self.y_slider = ctk.CTkSlider(card, from_=0, to=100, command=self._on_y_changed)
        self.y_slider.pack(padx=40, fill="x")
        y_val_label = ctk.CTkLabel(card, textvariable=self.y_value)
        y_val_label.pack(pady=(5, 20))
        self.x_value = ctk.StringVar(value="0.000")
        x_label = ctk.CTkLabel(card, text="Horizontal Recoil (X)", font=("Segoe UI", 16))
        x_label.pack()
        self.x_slider = ctk.CTkSlider(card, from_=-50, to=50, command=self._on_x_changed)
        self.x_slider.pack(padx=40, fill="x")
        x_val_label = ctk.CTkLabel(card, textvariable=self.x_value)
        x_val_label.pack(pady=(5, 20))

        autoclicker_page = ctk.CTkFrame(self.container, fg_color="#111111")
        autoclicker_page.grid_rowconfigure(0, weight=1)
        autoclicker_page.grid_columnconfigure(0, weight=1)
        self.pages["Autoclicker"] = autoclicker_page

        card2 = ctk.CTkFrame(autoclicker_page, corner_radius=15, fg_color="#1a1a1a",
                             border_width=2, border_color="#333333")
        card2.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)
        title2 = ctk.CTkLabel(card2, text="Autoclicker", font=("Segoe UI", 20, "bold"), text_color="#e6e6e6")
        title2.pack(pady=20)

        self.ac_toggle_button = ctk.CTkButton(card2, text="DISABLED", width=120, height=40,
                                              corner_radius=10, fg_color="#c44242",
                                              hover_color="#a23232", command=self._toggle_autoclicker)
        self.ac_toggle_button.pack(pady=10)

        self.cps_value = ctk.StringVar(value="10 CPS")
        cps_slider = ctk.CTkSlider(card2, from_=1, to=50, command=lambda v: self.cps_value.set(f"{int(v)} CPS"))
        cps_slider.set(10)
        cps_slider.pack(padx=40, fill="x")
        cps_label = ctk.CTkLabel(card2, textvariable=self.cps_value)
        cps_label.pack(pady=(5, 20))

        self.bind_button = ctk.CTkButton(card2, text="Bind Activator", width=160, height=40,
                                         corner_radius=10, fg_color="#2fa372",
                                         hover_color="#25815a", command=self._start_listen)
        self.bind_button.pack(pady=10)

        self.bound_display = ctk.CTkLabel(card2, text="No activator bound", font=("Segoe UI", 16))
        self.bound_display.pack(pady=10)

    def _start_listen(self):
        self.listening_for_key = True
        self.ignore_next_click = True
        self.bound_display.configure(text="", image=self.loading_img, compound="center")

    def _clear_loading_and_show_text(self, text_value: str):
        self.bound_display.configure(image=None, compound=None, text=text_value)

    def _clear_loading_and_show_image(self, image_obj):
        if image_obj:
            self.bound_display.configure(text="", image=image_obj, compound="center")
        else:
            self._clear_loading_and_show_text(self.bound_key)

    def _on_mouse_press(self, event):
        if not self.listening_for_key:
            return
        if self.ignore_next_click:
            self.ignore_next_click = False
            return
        if event.num == 1:
            self.bound_key = "Left Click"
            self._clear_loading_and_show_image(self.left_img)
        elif event.num == 3:
            self.bound_key = "Right Click"
            self._clear_loading_and_show_image(self.right_img)
        elif event.num in (4, 8):
            self.bound_key = "Mouse4"
            self._clear_loading_and_show_image(self.mouse4_img)
        elif event.num in (5, 9):
            self.bound_key = "Mouse5"
            self._clear_loading_and_show_image(self.mouse5_img)
        else:
            self.bound_key = f"Mouse{event.num}"
            self._clear_loading_and_show_text(self.bound_key)
        self.listening_for_key = False

    def _on_global_mouse(self, x, y, button, pressed):
        if not self.autoclicker_enabled:
            return
        if not self.bound_key:
            return

        key_map = {
            "Left Click": button == mouse.Button.left,
            "Right Click": button == mouse.Button.right,
            "Mouse4": button == mouse.Button.x1,
            "Mouse5": button == mouse.Button.x2
        }

        if key_map.get(self.bound_key, False):
            if pressed:
                self.autoclicker.set_cps(int(self.cps_value.get().split()[0]))
                self.autoclicker.start()
            else:
                self.autoclicker.stop()

    def _toggle_autoclicker(self):
        self.autoclicker_enabled = not self.autoclicker_enabled
        if self.autoclicker_enabled:
            self.ac_toggle_button.configure(text="ENABLED", fg_color="#2fa372", hover_color="#25815a")
        else:
            self.ac_toggle_button.configure(text="DISABLED", fg_color="#c44242", hover_color="#a23232")
            self.autoclicker.stop()

    # ---------------- Operator / Config logic (unchanged) ----------------
    def _load_all_operators(self):
        for side in ["attackers","defenders"]:
            path = os.path.join(OPERATORS_DIR, side)
            if os.path.isdir(path):
                files = [f for f in os.listdir(path) if f.lower().endswith(".png")]
                self.all_operators[side] = [os.path.splitext(f)[0] for f in files]
                for name in self.all_operators[side]:
                    if name not in self.operator_images:
                        img_path = os.path.join(path, f"{name}.png")
                        if os.path.isfile(img_path):
                            img = Image.open(img_path).resize((64,64), Image.LANCZOS)
                            self.operator_images[name] = ctk.CTkImage(img, size=(64,64))
                            frame = ctk.CTkFrame(self.operator_scroll, width=80, height=80,
                                                 corner_radius=6, fg_color="#111111",
                                                 border_width=4, border_color="#888888")
                            frame.grid_propagate(False)
                            btn = ctk.CTkButton(frame, image=self.operator_images[name], text="",
                                                width=72, height=72, corner_radius=4,
                                                fg_color="#111111", hover_color="#222222",
                                                command=lambda n=name: self._select_operator(n))
                            btn.pack(expand=True, fill="both", padx=2, pady=2)
                            self.operator_frames[name] = frame
                            self.operator_side_map[name] = side
        self._refresh_operator_grid(initial=True)

    def _create_all_configs(self):
        for side in self.all_operators:
            for name in self.all_operators[side]:
                cfg_path = os.path.join(CONFIGS_DIR, f"{name}.cfg")
                if not os.path.isfile(cfg_path):
                    with open(cfg_path,"w",encoding="utf-8") as f:
                        json.dump({"Y":0.0,"X":0.0},f)

    def _refresh_operator_grid(self, initial=False):
        side = self.current_side
        search = self.search_var.get().lower()
        names = self.all_operators.get(side, [])
        ordered = []
        if side in DISPLAY_ORDER:
            ordered += [n for n in DISPLAY_ORDER[side] if n in names]
        ordered += [n for n in names if n not in DISPLAY_ORDER.get(side, [])]
        row, col = 0, 0
        for name in ordered:
            frame = self.operator_frames[name]
            if search and search not in name.lower():
                frame.grid_remove()
                continue
            frame.grid(row=row, column=col, padx=8, pady=8)
            col += 1
            if col >= 8:
                col = 0
                row += 1
        if not initial:
            for n, frame in self.operator_frames.items():
                if n not in ordered:
                    frame.grid_remove()

    def _select_operator(self, name):
        for f in self.operator_frames.values():
            f.configure(border_color="#888888", border_width=4)
        frame = self.operator_frames.get(name)
        if frame:
            frame.configure(border_color="white", border_width=4)
        self.selected_operator = name
        cfg = self._load_config(name)
        self.y_slider.set(cfg["Y"])
        self.x_slider.set(cfg["X"])
        self.y_value.set(f"{cfg['Y']:.3f}")
        self.x_value.set(f"{cfg['X']:.3f}")
        self.recoil.set_recoil_y(cfg["Y"])
        self.recoil.set_recoil_x(cfg["X"])
        self._save_current_config()

    def _on_side_changed(self, value: str):
        self.current_side = value.lower()
        self._refresh_operator_grid()

    def _load_config(self, operator):
        cfg_path = os.path.join(CONFIGS_DIR, f"{operator}.cfg")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path,"r",encoding="utf-8") as f:
                    data = json.load(f)
                    return {"Y": float(data.get("Y",0)), "X": float(data.get("X",0))}
            except:
                pass
        return {"Y":0.0,"X":0.0}

    def _save_current_config(self):
        if not self.selected_operator: return
        cfg_path = os.path.join(CONFIGS_DIR, f"{self.selected_operator}.cfg")
        config = {"Y": float(self.y_slider.get()), "X": float(self.x_slider.get())}
        try:
            with open(cfg_path,"w",encoding="utf-8") as f:
                json.dump(config,f)
        except:
            pass

    def _on_y_changed(self, value):
        self.y_value.set(f"{value:.3f}")
        self._save_current_config()
        self.recoil.set_recoil_y(value)

    def _on_x_changed(self, value):
        self.x_value.set(f"{value:.3f}")
        self._save_current_config()
        self.recoil.set_recoil_x(value)

    def _toggle_enabled(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.toggle_button.configure(text="ENABLED", fg_color="#2fa372", hover_color="#25815a")
            self.recoil.start()
        else:
            self.toggle_button.configure(text="DISABLED", fg_color="#c44242", hover_color="#a23232")
            self.recoil.stop()

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.grid_forget()
        page = self.pages[page_name]
        page.grid(row=0, column=0, sticky="nsew")
        self.current_page = page
        for name, btn in self.nav_buttons.items():
            btn.configure(fg_color="#1f538d" if name==page_name else "transparent")

if __name__=="__main__":
    app = RecoilApp()
    app.mainloop()
