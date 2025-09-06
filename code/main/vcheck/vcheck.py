import sys, urllib.request, webbrowser
import customtkinter as ctk


VERSION_URL = "https://raw.githubusercontent.com/ttenacityy/AllahWare-R6/main/version"
GITHUB_URL = "https://github.com/ttenacityy/AllahWare-R6/tree/main"


def check_version(current_version: str):
    try:
        with urllib.request.urlopen(VERSION_URL, timeout=5) as resp:
            remote_version = resp.read().decode("utf-8").strip()
        if remote_version != current_version:
            show_update_popup(current_version, remote_version)
    except Exception:
        pass


def show_update_popup(current_version: str, remote_version: str):
    popup = ctk.CTk()
    popup.title("Update Available")
    popup.geometry("480x320")
    popup.resizable(False, False)
    popup.attributes("-topmost", True)

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    # Main card
    card = ctk.CTkFrame(
        popup,
        corner_radius=15,
        fg_color="#1a1a1a",
        border_width=2,
        border_color="#333333",
    )
    card.pack(expand=True, fill="both", padx=20, pady=20)

    # Title
    title = ctk.CTkLabel(
        card,
        text="AllahWare Update",
        font=("Segoe UI", 20, "bold"),
        text_color="#ffffff",
    )
    title.pack(pady=(15, 10))

    # Message
    msg = (
        f"A new version of AllahWare is available!\n\n"
        f"Current Version: {current_version}\n"
        f"Latest Version:  {remote_version}\n\n"
        f"Would you like to download the update?"
    )
    label = ctk.CTkLabel(
        card, text=msg, font=("Segoe UI", 15), text_color="#cccccc", justify="center"
    )
    label.pack(pady=10, padx=20)

    # Button row
    btn_frame = ctk.CTkFrame(card, fg_color="transparent")
    btn_frame.pack(pady=15)

    def on_yes():
        webbrowser.open(GITHUB_URL)
        popup.destroy()
        sys.exit(0)

    def on_no():
        popup.destroy()
        sys.exit(0)

    yes_btn = ctk.CTkButton(
        btn_frame,
        text="Yes",
        width=120,
        height=35,
        corner_radius=8,
        fg_color="#2fa372",
        hover_color="#25815a",
        command=on_yes,
    )
    yes_btn.grid(row=0, column=0, padx=10)

    no_btn = ctk.CTkButton(
        btn_frame,
        text="No",
        width=120,
        height=35,
        corner_radius=8,
        fg_color="#c44242",
        hover_color="#a23232",
        command=on_no,
    )
    no_btn.grid(row=0, column=1, padx=10)

    popup.protocol("WM_DELETE_WINDOW", on_no)
    popup.mainloop()
