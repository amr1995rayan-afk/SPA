import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from weatherWidget import build_weather_ui
from timerWidget import build_timer_ui


def create_weather_widget(parent):
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    weather_frame = ttk.Labelframe(parent, text="Weather", bootstyle="success")
    weather_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # make inside expand (if build_weather_ui uses pack, it should use fill+expand)
    weather_frame.rowconfigure(0, weight=1)
    weather_frame.columnconfigure(0, weight=1)

    build_weather_ui(weather_frame, default_city="Berlin")
    return weather_frame


def create_timer_widget(parent):
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    timer_frame = ttk.Labelframe(parent, text="Focus Timer", bootstyle="info")
    timer_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    timer_frame.rowconfigure(0, weight=1)
    timer_frame.columnconfigure(0, weight=1)

    build_timer_ui(timer_frame, focus_minutes=20, break_minutes=5)
    return timer_frame
