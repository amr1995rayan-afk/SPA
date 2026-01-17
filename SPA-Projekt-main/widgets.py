# widgets.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from weatherWidget import build_weather_ui
from timerWidget import build_timer_ui


def create_weather_widget(parent):
    weather_frame = ttk.Labelframe(parent, text="Weather", bootstyle="success")
    weather_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    build_weather_ui(weather_frame, default_city="Berlin")
    return weather_frame


def create_timer_widget(parent):
    timer_frame = ttk.Labelframe(parent, text="Focus Timer", bootstyle="info")
    timer_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

    build_timer_ui(timer_frame, focus_minutes=20, break_minutes=5)
    return timer_frame