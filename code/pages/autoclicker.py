import os
import customtkinter as ctk
from PIL import Image
from pynput import mouse


class AutoclickerPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#111111")
        self.app = app
        self.listening_for_key = False
        self.ignore_next_click = False
        self.bound_key = None
        img_dir = self.app.IMG_DIR
        self.left_img = ctk.CTkImage(Image.open(os.path.join(img_dir, "leftclick.png")), size=(48, 48))
        self.right_img = ctk.CTkImage(Image.open(os.path.join(img_dir, "rightclick.png")), size=(48, 48))
        self.loading_img = ctk.CTkImage(Image.open(os.path.join(img_dir, "loading.png")), size=(48, 48))
        mouse4_path = os.path.join(img_dir, "mouse4.png")
        mouse5_path = os.path.join(img_dir, "mouse5.png")
        self.mouse4_img = ctk.CTkImage(Image.open(mouse4_path), size=(48, 48)) if os.path.isfile(mouse4_path) else None
        self.mouse5_img = ctk.CTkImage(Image.open(mouse5_path), size=(48, 48)) if os.path.isfile(mouse5_path) else None
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
            text="Autoclicker",
            font=("Segoe UI", 20, "bold"),
            text_color="#e6e6e6",
        )
        title.pack(pady=20)
        self.ac_toggle_button = ctk.CTkButton(
            card,
            text="DISABLED",
            width=120,
            height=40,
            corner_radius=10,
            fg_color="#c44242",
            hover_color="#a23232",
            command=self._toggle_autoclicker,
        )
        self.ac_toggle_button.pack(pady=10)
        self.cps_value = ctk.StringVar(value="10 CPS")
        cps_slider = ctk.CTkSlider(
            card,
            from_=1,
            to=50,
            command=lambda v: self.cps_value.set(f"{int(v)} CPS"),
        )
        cps_slider.set(10)
        cps_slider.pack(padx=40, fill="x")
        cps_label = ctk.CTkLabel(card, textvariable=self.cps_value)
        cps_label.pack(pady=(5, 20))
        self.bind_button = ctk.CTkButton(
            card,
            text="Bind Activator",
            width=160,
            height=40,
            corner_radius=10,
            fg_color="#1f538d",      
            hover_color="#163d6b",    
            command=self._start_listen,
        )
        self.bind_button.pack(pady=10)
        self.bound_display = ctk.CTkLabel(
            card, text="No activator bound", font=("Segoe UI", 16)
        )
        self.bound_display.pack(pady=10)
        self.app.bind_all("<Button>", self._on_mouse_press)
        self.listener = mouse.Listener(on_click=self._on_global_mouse)
        self.listener.start()

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
        if not getattr(self.app, "autoclicker_enabled", False):
            return
        if not self.bound_key:
            return

        key_map = {
            "Left Click": button == mouse.Button.left,
            "Right Click": button == mouse.Button.right,
            "Mouse4": button == mouse.Button.x1,
            "Mouse5": button == mouse.Button.x2,
        }

        if key_map.get(self.bound_key, False):
            if pressed:
                self.app.autoclicker.set_cps(int(self.cps_value.get().split()[0]))
                self.app.autoclicker.start()
            else:
                self.app.autoclicker.stop()

    def _toggle_autoclicker(self):
        self.app.autoclicker_enabled = not getattr(self.app, "autoclicker_enabled", False)
        if self.app.autoclicker_enabled:
            self.ac_toggle_button.configure(
                text="ENABLED", fg_color="#2fa372", hover_color="#25815a"
            )
        else:
            self.ac_toggle_button.configure(
                text="DISABLED", fg_color="#c44242", hover_color="#a23232"
            )
            self.app.autoclicker.stop()
