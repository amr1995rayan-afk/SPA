
# Ensure environment variables are loaded before any other imports
import os
from dotenv import load_dotenv
load_dotenv(".env")

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from shortCut import create_shortcut_bar
from pdf_text_editor import create_pdf_text_editor
from todo_list import create_todo_list
from widgets import create_weather_widget, create_timer_widget
from chatBot import create_chatbot


def main():
    # Hauptfenster erstellen
    root = ttk.Window(themename="superhero")
    root.title("Student Personal Assistant")
    root.geometry("1200x800")

    # Layout konfigurieren: Spalten und Zeilen
    root.columnconfigure(0, weight=3)  # Linke Hauptspalte (PDF-Editor)
    root.columnconfigure(1, weight=1)  # Rechte Spalte (To-Do, Widget, Chatbot)
    root.rowconfigure(0, weight=0)  # Shortcut bar (oben)
    root.rowconfigure(1, weight=1)  # Bereich für den Rest der GUI

    # Shortcut-Bar oben erstellen (bleibt wie bisher)
    create_shortcut_bar(root)

    # Linker Bereich: PDF-Editor
    create_pdf_text_editor(root)

    # Rechter Bereich: To-Do-Liste, Wetter-Widget, Chatbot
    # Frame für die rechte Spalte erstellen
    right_frame = ttk.Frame(root, bootstyle="secondary")
    right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
    right_frame.rowconfigure(0, weight=1)  # To-Do-Liste (weniger Höhe)
    right_frame.rowconfigure(1, weight=2)  # Wetter-Widget (größer)
    right_frame.rowconfigure(2, weight=2)  # Timer-Widget (größer)
    right_frame.rowconfigure(3, weight=2)  # Chatbot (größer)
    right_frame.columnconfigure(0, weight=1)

    # To-Do-Liste oben rechts (row 0)
    create_todo_list(right_frame)

    # Wetter-Widget mittig rechts (row 1)
    create_weather_widget(right_frame)

    # Timer-Widget mittig rechts (row 2)
    create_timer_widget(right_frame)

    # Chatbot unten rechts (row 3)
    chatbot_frame = ttk.Labelframe(right_frame, text="Chatbot", bootstyle="warning")
    chatbot_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
    create_chatbot(chatbot_frame)

    # Haupt-Loop starten
    root.mainloop()


if __name__ == "__main__":
    main()