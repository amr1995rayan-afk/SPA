import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import webbrowser

# === open Links in Browser  ====
def open_link(url):
    webbrowser.open(url)

# === Creat Buttons & Links  ====
def create_shortcut_bar(root):
    shortcut_frame = ttk.Frame(root, bootstyle="dark")
    shortcut_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=5, padx=5)

    # Buttons & Links
    links = {
        "Web": "https://www.google.com",
        "Email": "https://www.gmail.com",
        "Music": "https://www.spotify.com",
        "Shop": "https://www.amazon.com",
        "BHT" : "https://lms.bht-berlin.de/",
        "BHT-Mail" : "https://webmail.bht-berlin.de/",
    }

    for i, (name, url) in enumerate(links.items()):
        # Button erstellen und mit der open_link-Funktion verbinden
        btn = ttk.Button(
            shortcut_frame,
            text=name,
            bootstyle="info-outline",
            command=lambda link=url: open_link(link)  # Übergibt die URL an die Funktion
        )
        btn.grid(row=0, column=i, padx=10, pady=10)

    return shortcut_frame