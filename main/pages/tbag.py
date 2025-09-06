import customtkinter as ctk
from pynput import keyboard

class TBagPage(ctk.CTkFrame):
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

        # Title
        title = ctk.CTkLabel(
            card,
            text="T-Bag Macro",
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
        self.crouch_label = ctk.CTkLabel(card, text="In-game Crouch: None", font=("Segoe UI", 16))
        self.crouch_label.pack(pady=10)
        crouch_btn = ctk.CTkButton(card, text="Bind Crouch Key", command=lambda: self._start_listen("crouch"))
        crouch_btn.pack(pady=5)
        self.tbag_label = ctk.CTkLabel(card, text="T-Bag Key: None", font=("Segoe UI", 16))
        self.tbag_label.pack(pady=10)
        tbag_btn = ctk.CTkButton(card, text="Bind T-Bag Key", command=lambda: self._start_listen("tbag"))
        tbag_btn.pack(pady=5)
        self.speed_value = ctk.StringVar(value="300 ms")
        speed_slider = ctk.CTkSlider(
            card,
            from_=50,
            to=1000,
            command=lambda v: self._set_delay(v),
        )
        speed_slider.set(300)
        speed_slider.pack(padx=40, fill="x", pady=10)
        speed_label = ctk.CTkLabel(card, textvariable=self.speed_value)
        speed_label.pack()

        # State for key listening
        self.listening_for = None
        self.klistener = keyboard.Listener(on_press=self._on_key)
        self.klistener.start()

    def _toggle_enabled(self):
        self.app.tbag.enabled = not getattr(self.app.tbag, "enabled", False)
        if self.app.tbag.enabled:
            self.toggle_button.configure(
                text="ENABLED", fg_color="#2fa372", hover_color="#25815a"
            )
        else:
            self.toggle_button.configure(
                text="DISABLED", fg_color="#c44242", hover_color="#a23232"
            )

    def _start_listen(self, which):
        self.listening_for = which
        if which == "crouch":
            self.crouch_label.configure(text="In-game Crouch: [Press a key...]")
        elif which == "tbag":
            self.tbag_label.configure(text="T-Bag Key: [Press a key...]")

    def _set_delay(self, value):
        self.app.tbag.set_delay(float(value))
        self.speed_value.set(f"{int(value)} ms")

    def _on_key(self, key):
        if not self.listening_for:
            return
        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key)

        if self.listening_for == "crouch":
            self.app.tbag.set_crouch_key(key)
            self.crouch_label.configure(text=f"In-game Crouch: {key_name}")
        elif self.listening_for == "tbag":
            self.app.tbag.set_tbag_key(key)
            self.tbag_label.configure(text=f"T-Bag Key: {key_name}")

        self.listening_for = None
