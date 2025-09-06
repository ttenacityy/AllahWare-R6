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
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)

        title = ctk.CTkLabel(
            card,
            text="Control Settings",
            font=("Segoe UI", 20, "bold"),
            text_color="#e6e6e6",
        )
        title.pack(pady=20)

        self.toggle_button = ctk.CTkButton(
            card,
            text="DISABLED",
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#c44242",
            hover_color="#a23232",
            command=self._toggle_enabled,
        )
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
        self.x_slider = ctk.CTkSlider(
            card, from_=-50, to=50, command=self._on_x_changed
        )
        self.x_slider.pack(padx=40, fill="x")
        x_val_label = ctk.CTkLabel(card, textvariable=self.x_value)
        x_val_label.pack(pady=(5, 20))

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
