import os
import json
import customtkinter as ctk

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#111111")
        self.app = app
        self.settings_dir = os.path.join(r"C:\AllahWare", "Settings")
        self.settings_file = os.path.join(self.settings_dir, "settings.cfg")
        os.makedirs(self.settings_dir, exist_ok=True)

        # Defaults
        self.settings = {
            "control_sensitivity": "50",
            "dynamic_control": "OFF",
            "dynamic_stages": {
                "1.0": {"enabled": False, "multiplier": 1.0},
                "1.5": {"enabled": False, "multiplier": 1.0},
                "2.0": {"enabled": False, "multiplier": 1.0},
                "2.5": {"enabled": False, "multiplier": 1.0},
                "3.0": {"enabled": False, "multiplier": 1.0},
            },
        }

        self._load_settings()
        card = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1a1a1a",
            border_width=2,
            border_color="#333333",
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.8)
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)
        title = ctk.CTkLabel(
            card,
            text="Settings",
            font=("Segoe UI", 20, "bold"),
            text_color="#e6e6e6",
        )
        title.grid(row=0, column=0, columnspan=2, pady=20)
        left_frame = ctk.CTkFrame(card, fg_color="transparent")
        left_frame.grid(row=1, column=0, sticky="n", padx=20)
        sens_label = ctk.CTkLabel(left_frame, text="Control Sensitivity", font=("Segoe UI", 16))
        sens_label.pack(anchor="w", pady=(10, 0))
        self.sens_var = ctk.StringVar(value=self.settings["control_sensitivity"])
        self.sens_var.trace_add("write", lambda *args: self._update_sensitivity_live())
        self.sens_entry = ctk.CTkEntry(left_frame, width=100, textvariable=self.sens_var)
        self.sens_entry.pack(anchor="w", pady=(5, 15))
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.grid(row=1, column=1, sticky="n", padx=20)
        self.dynamic_control_toggle = ctk.CTkSwitch(
            right_frame,
            text="Dynamic Control [BETA]",
            font=("Segoe UI", 16),
            command=self._toggle_dynamic_control,
            onvalue="ON",
            offvalue="OFF",
        )
        self.dynamic_control_toggle.pack(anchor="w", pady=(0, 15), padx=5)

        if self.settings["dynamic_control"] == "ON":
            self.dynamic_control_toggle.select()
        else:
            self.dynamic_control_toggle.deselect()
        self.stage_widgets = {}
        for idx, t in enumerate(["1.0", "1.5", "2.0", "2.5", "3.0"]):
            row_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            lbl = ctk.CTkLabel(row_frame, text=f"{t}s", width=40, anchor="w")
            lbl.pack(side="left", padx=5)
            slider_var = ctk.DoubleVar(value=self.settings["dynamic_stages"][t]["multiplier"])
            val_label = ctk.CTkLabel(row_frame, text=f"{slider_var.get():.1f}x", width=40)
            val_label.pack(side="right", padx=5)

            slider = ctk.CTkSlider(
                row_frame,
                from_=0.1,
                to=3.0,
                number_of_steps=29,  # (3.0-0.1)/0.1
                variable=slider_var,
                command=lambda v, time_key=t, lbl=val_label: self._update_stage_multiplier(time_key, v, lbl),
            )
            slider.pack(side="left", fill="x", expand=True, padx=5)

            toggle_var = ctk.StringVar(
                value="ON" if self.settings["dynamic_stages"][t]["enabled"] else "OFF"
            )
            toggle = ctk.CTkSwitch(
                row_frame,
                text="",
                width=30,
                variable=toggle_var,
                onvalue="ON",
                offvalue="OFF",
                command=lambda time_key=t, var=toggle_var: self._update_stage_toggle(time_key, var),
            )
            if toggle_var.get() == "ON":
                toggle.select()
            else:
                toggle.deselect()
            toggle.pack(side="right", padx=5)

            self.stage_widgets[t] = {
                "slider": slider,
                "toggle": toggle,
                "val_label": val_label,
            }

        # Apply initial settings
        self._apply_to_recoil()
        self._apply_stage_states()

    def _load_settings(self):
        if os.path.isfile(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    self.settings.update(file_data)
            except Exception:
                pass
        else:
            self._save_settings()

    def _save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def _apply_to_recoil(self):
        try:
            sens_val = float(self.settings.get("control_sensitivity", "50"))
        except ValueError:
            sens_val = 50.0
        self.app.recoil.set_sensitivity(sens_val)

        dyn_enabled = self.settings.get("dynamic_control", "OFF") == "ON"
        self.app.recoil.set_dynamic_control(dyn_enabled)

        # Push stage multipliers to recoil controller
        self.app.recoil.set_dynamic_stages(self.settings["dynamic_stages"])

    def _apply_stage_states(self):
        enabled = self.settings["dynamic_control"] == "ON"
        for t, widgets in self.stage_widgets.items():
            state = "normal" if enabled else "disabled"
            widgets["slider"].configure(state=state)
            widgets["toggle"].configure(state=state)

    def _update_sensitivity_live(self):
        val = self.sens_var.get().strip()
        if not val.isdigit():
            return
        self.settings["control_sensitivity"] = val
        self._save_settings()
        self._apply_to_recoil()

    def _toggle_dynamic_control(self):
        self.settings["dynamic_control"] = self.dynamic_control_toggle.get()
        self._save_settings()
        self._apply_to_recoil()
        self._apply_stage_states()

    def _update_stage_multiplier(self, time_key, value, lbl):
        self.settings["dynamic_stages"][time_key]["multiplier"] = round(float(value), 1)
        lbl.configure(text=f"{float(value):.1f}x")
        self._save_settings()
        self._apply_to_recoil()

    def _update_stage_toggle(self, time_key, var):
        self.settings["dynamic_stages"][time_key]["enabled"] = var.get() == "ON"
        self._save_settings()
        self._apply_to_recoil()
