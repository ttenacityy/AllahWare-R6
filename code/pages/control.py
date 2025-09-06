import customtkinter as ctk

class ControlPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#111111")
        self.app = app
        card = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#1a1a1a",
            border_width=2,
            border_color="#333333",
        )
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.65)
        title = ctk.CTkLabel(
            card,
            text="Control Settings",
            font=("Segoe UI", 22, "bold"),
            text_color="#e6e6e6",
        )
        title.pack(pady=(20, 10))
        self.toggle_button = ctk.CTkButton(
            card,
            text="DISABLED",
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#c44242",
            hover_color="#a23232",
            font=("Segoe UI", 14, "bold"),
            command=self._toggle_enabled,
        )
        self.toggle_button.pack(pady=(5, 20))
        y_label = ctk.CTkLabel(
            card, text="Vertical Recoil (Y)", font=("Segoe UI", 16), text_color="#ffffff"
        )
        y_label.pack()

        self.y_slider = ctk.CTkSlider(
            card, from_=0, to=100, number_of_steps=100, command=self._on_y_changed
        )
        self.y_slider.pack(padx=40, fill="x")

        self.y_value = ctk.StringVar(value="0.000")
        self.y_entry = ctk.CTkEntry(
            card,
            textvariable=self.y_value,
            width=80,
            justify="center",
        )
        self.y_entry.pack(pady=(5, 20))
        self.y_entry.bind("<Return>", self._on_y_entry) 
        self.y_entry.bind("<FocusOut>", self._on_y_entry)  
        x_label = ctk.CTkLabel(
            card, text="Horizontal Recoil (X)", font=("Segoe UI", 16), text_color="#ffffff"
        )
        x_label.pack()

        self.x_slider = ctk.CTkSlider(
            card, from_=-50, to=50, number_of_steps=100, command=self._on_x_changed
        )
        self.x_slider.pack(padx=40, fill="x")
        self.x_value = ctk.StringVar(value="0.000")
        self.x_entry = ctk.CTkEntry(
            card,
            textvariable=self.x_value,
            width=80,
            justify="center",
        )
        self.x_entry.pack(pady=(5, 20))
        self.x_entry.bind("<Return>", self._on_x_entry)
        self.x_entry.bind("<FocusOut>", self._on_x_entry)

    def _toggle_enabled(self):
        self.app.enabled = not getattr(self.app, "enabled", False)
        if self.app.enabled:
            self.toggle_button.configure(
                text="ENABLED", fg_color="#2fa372", hover_color="#25815a"
            )
            self.app.recoil.start()
        else:
            self.toggle_button.configure(
                text="DISABLED", fg_color="#c44242", hover_color="#a23232"
            )
            self.app.recoil.stop()

    def _on_y_changed(self, value):
        self.y_value.set(f"{value:.3f}")
        self.app.recoil.set_recoil_y(value)
        if "Operators" in self.app.pages:
            self.app.pages["Operators"]._save_current_config()

    def _on_x_changed(self, value):
        self.x_value.set(f"{value:.3f}")
        self.app.recoil.set_recoil_x(value)
        if "Operators" in self.app.pages:
            self.app.pages["Operators"]._save_current_config()

    def _on_y_entry(self, event=None):
        try:
            val = float(self.y_value.get())
            val = max(0, min(100, val))  # clamp
            self.y_slider.set(val)
            self._on_y_changed(val)
        except ValueError:
            self.y_value.set(f"{self.y_slider.get():.3f}")  # reset invalid

    def _on_x_entry(self, event=None):
        try:
            val = float(self.x_value.get())
            val = max(-50, min(50, val))  # clamp
            self.x_slider.set(val)
            self._on_x_changed(val)
        except ValueError:
            self.x_value.set(f"{self.x_slider.get():.3f}")  # reset invalid
