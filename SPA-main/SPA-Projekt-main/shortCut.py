import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser

# === open Links in Browser  ====


def open_link(url):
    webbrowser.open(url)

# === Theme Wechsel ====


def change_theme(root, theme_name):
    """Ändert das Theme der Anwendung"""
    root.style.theme_use(theme_name)

# === Creat Buttons & Links  ====


def create_shortcut_bar(root):
    shortcut_frame = ttk.Frame(root, bootstyle="dark")
    shortcut_frame.grid(row=0, column=0, columnspan=2,
                        sticky="nsew", pady=5, padx=5)

    # Buttons & Links
    links = {
        "Web": "https://www.google.com",
        "Email": "https://www.gmail.com",
        "Music": "https://www.spotify.com",
        "Shop": "https://www.amazon.com",
        "BHT": "https://lms.bht-berlin.de/",
        "BHT-Mail": "https://webmail.bht-berlin.de/",
    }

    i = 0
    for name, url in links.items():
        # Button erstellen und mit der open_link-Funktion verbinden
        btn = ttk.Button(
            shortcut_frame,
            text=name,
            bootstyle="info-outline",
            # Übergibt die URL an die Funktion
            command=lambda link=url: open_link(link)
        )
        btn.grid(row=0, column=i, padx=10, pady=10)
        i += 1

    # --- Theme Selection ---
    ttk.Separator(shortcut_frame, orient="vertical").grid(
        row=0, column=i, padx=10, sticky="ns")
    i += 1

    ttk.Label(shortcut_frame, text="Theme:").grid(
        row=0, column=i, padx=(10, 5))
    i += 1

    themes = ["superhero", "darkly", "solar",
              "cyborg", "minty", "litera", "sandstone"]

    for theme in themes:
        theme_btn = ttk.Button(
            shortcut_frame,
            text=theme.capitalize(),
            bootstyle="secondary-outline",
            command=lambda t=theme: change_theme(root, t)
        )
        theme_btn.grid(row=0, column=i, padx=2)
        i += 1

    return shortcut_frame
