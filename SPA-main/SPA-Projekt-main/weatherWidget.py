import threading
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from getWeather import get_weather

API_KEY = "f98ea81e57ae40208c7190735261701"


def build_weather_ui(parent, default_city="Berlin"):
    """
    Creates the weather UI inside `parent` and returns the frame.
    No Tk(), no mainloop() here.
    """

    frm = ttk.Frame(parent, padding=12)
    frm.pack(fill=BOTH, expand=True)

    city_var = ttk.StringVar(value=default_city)
    status_var = ttk.StringVar(value="Idle")

    city_out = ttk.StringVar(value="—")
    temp_out = ttk.StringVar(value="—")
    cond_out = ttk.StringVar(value="—")
    humidity_out = ttk.StringVar(value="—")
    wind_out = ttk.StringVar(value="—")

    def update_ui(w):
        city_out.set(f"{w.city}, {w.country}")
        temp_out.set(f"{w.temp_c} °C")
        cond_out.set(w.condition)
        humidity_out.set(f"{w.humidity}%")
        wind_out.set(f"{w.wind_kph} km/h")
        status_var.set("Done")
        btn.config(state="normal")

    def show_error(e):
        status_var.set("Failed")
        btn.config(state="normal")
        messagebox.showerror("Weather error", str(e))

    def fetch_weather():
        city = city_var.get().strip()
        if not city:
            messagebox.showwarning("Input error", "Enter a city name.")
            return

        status_var.set("Loading...")
        btn.config(state="disabled")

        def worker():
            try:
                weather = get_weather(API_KEY, city)
                frm.after(0, lambda: update_ui(weather))
            except Exception as e:
                frm.after(0, lambda: show_error(e))

        threading.Thread(target=worker, daemon=True).start()

    ttk.Label(frm, text="City:").grid(row=0, column=0, sticky="w")
    ttk.Entry(frm, textvariable=city_var).grid(row=0, column=1, sticky="ew", padx=8)

    btn = ttk.Button(frm, text="Get Weather", command=fetch_weather)
    btn.grid(row=0, column=2)

    ttk.Separator(frm).grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

    labels = [
        ("Location", city_out),
        ("Temperature", temp_out),
        ("Condition", cond_out),
        ("Humidity", humidity_out),
        ("Wind", wind_out),
    ]

    for i, (label, var) in enumerate(labels, start=2):
        ttk.Label(frm, text=label).grid(row=i, column=0, sticky="w")
        ttk.Label(frm, textvariable=var).grid(row=i, column=1, columnspan=2, sticky="w")

    ttk.Label(frm, textvariable=status_var).grid(row=8, column=0, columnspan=3, pady=10, sticky="w")

    frm.columnconfigure(1, weight=1)

    # optional: auto-load once
    fetch_weather()

    return frm