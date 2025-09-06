import os, json
import customtkinter as ctk
from PIL import Image

DISPLAY_ORDER = {
    "attackers": [
        "striker","sledge","thatcher","ash","thermite","twitch","montagne","glaz","fuze","blitz","iq","buck",
        "blackbeard","capitao","hibana","jackal","ying","zofia","dokkaebi","lion","finka","maverick","nomad",
        "gridlock","nokk","amaru","kali","iana","ace","zero","flores","osa","sens","grim","brava","ram",
        "deimos","rauora"
    ],
    "defenders": [
        "sentry","smoke","mute","castle","pulse","doc","rook","kapkan","tachanka","jager","bandit","frost",
        "valkyrie","caveira","echo","mira","lesion","ela","vigil","maestro","alibi","clash","kaid","mozzie",
        "warden","goyo","wamai","oryx","melusi","aruni","thunderbird","thorn","azami","solis","fenrir",
        "tubarao","skopos","denari"
    ],
}


class OperatorsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#111111")
        self.app = app
        self.current_side = "attackers"
        self.operator_frames = {}
        self.operator_images = {}
        self.operator_side_map = {}
        self.all_operators = {"attackers": [], "defenders": []}
        self.selected_operator = None
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.side_selector = ctk.CTkSegmentedButton(
            self, values=["Attackers", "Defenders"], command=self._on_side_changed
        )
        self.side_selector.set("Attackers")
        self.side_selector.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Search operators...",
            textvariable=self.search_var,
        )
        search_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.search_var.trace_add("write", lambda *_: self._refresh_operator_grid())
        self.operator_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.operator_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        self.operator_scroll.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)
        self._load_all_operators()
        self._create_all_configs()
        self._refresh_operator_grid(initial=True)

    def _load_all_operators(self):
        for side in ["attackers", "defenders"]:
            path = os.path.join(self.app.OPERATORS_DIR, side)
            if os.path.isdir(path):
                files = [f for f in os.listdir(path) if f.lower().endswith(".png")]
                self.all_operators[side] = [os.path.splitext(f)[0] for f in files]
                for name in self.all_operators[side]:
                    if name not in self.operator_images:
                        img_path = os.path.join(path, f"{name}.png")
                        if os.path.isfile(img_path):
                            # Same sizing as original
                            img = Image.open(img_path).resize((64, 64), Image.LANCZOS)
                            self.operator_images[name] = ctk.CTkImage(img, size=(64, 64))
                            frame = ctk.CTkFrame(
                                self.operator_scroll,
                                width=80,
                                height=80,
                                corner_radius=6,
                                fg_color="#111111",
                                border_width=4,
                                border_color="#888888",
                            )
                            frame.grid_propagate(False)

                            btn = ctk.CTkButton(
                                frame,
                                image=self.operator_images[name],
                                text="",
                                width=72,
                                height=72,
                                corner_radius=4,
                                fg_color="#111111",
                                hover_color="#222222",
                                command=lambda n=name: self._select_operator(n),
                            )
                            btn.pack(expand=True, fill="both", padx=2, pady=2)

                            self.operator_frames[name] = frame
                            self.operator_side_map[name] = side

    def _create_all_configs(self):
        for side in self.all_operators:
            for name in self.all_operators[side]:
                cfg_path = os.path.join(self.app.CONFIGS_DIR, f"{name}.cfg")
                if not os.path.isfile(cfg_path):
                    with open(cfg_path, "w", encoding="utf-8") as f:
                        json.dump({"Y": 0.0, "X": 0.0}, f)

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

        # Update Control page sliders
        self.app.pages["Control"].y_slider.set(cfg["Y"])
        self.app.pages["Control"].x_slider.set(cfg["X"])
        self.app.pages["Control"].y_value.set(f"{cfg['Y']:.3f}")
        self.app.pages["Control"].x_value.set(f"{cfg['X']:.3f}")

        self.app.recoil.set_recoil_y(cfg["Y"])
        self.app.recoil.set_recoil_x(cfg["X"])
        self._save_current_config()

    def _on_side_changed(self, value: str):
        self.current_side = value.lower()
        self._refresh_operator_grid()

    def _load_config(self, operator):
        cfg_path = os.path.join(self.app.CONFIGS_DIR, f"{operator}.cfg")
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {
                        "Y": float(data.get("Y", 0)),
                        "X": float(data.get("X", 0)),
                    }
            except:
                pass
        return {"Y": 0.0, "X": 0.0}

    def _save_current_config(self):
        if not self.selected_operator:
            return
        cfg_path = os.path.join(self.app.CONFIGS_DIR, f"{self.selected_operator}.cfg")
        config = {
            "Y": float(self.app.pages["Control"].y_slider.get()),
            "X": float(self.app.pages["Control"].x_slider.get()),
        }
        try:
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except:
            pass
