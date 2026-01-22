from chatBot import create_chatbot
from widgets import create_weather_widget, create_timer_widget
from todo_list import create_todo_list
from pdf_text_editor import create_pdf_text_editor
from shortCut import create_shortcut_bar
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def main():
    # Hauptfenster erstellen
    root = ttk.Window(themename="superhero")
    root.title("Student Personal Assistant")
    root.geometry("1200x800")

    # Layout konfigurieren: Spalten und Zeilen
    # Linke Hauptspalte (PDF-Editor) - größer
    root.columnconfigure(0, weight=5)
    # Rechte Spalte (To-Do, Widget, Chatbot) - kleiner
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=0)  # Shortcut bar (oben)
    root.rowconfigure(1, weight=1)  # PDF und rechte Spalte
    root.rowconfigure(2, weight=1)  # Continuation für rowspan

    # Shortcut-Bar oben erstellen (bleibt wie bisher)
    create_shortcut_bar(root)

    # Linker Bereich: PDF-Editor
    create_pdf_text_editor(root)

    # Rechter Bereich: To-Do-Liste, Wetter-Widget, Chatbot
    # Frame für die rechte Spalte erstellen

    right_frame = ttk.Frame(root, bootstyle="secondary")
    right_frame.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=2, pady=2)
    # Configure right_frame for 3 widgets in the top row, chatbot below
    # Top row: To-Do, Weather, Timer (minimal height)
    right_frame.rowconfigure(0, weight=0)
    # Bottom: Chatbot (fills remaining space)
    right_frame.rowconfigure(1, weight=1)
    right_frame.columnconfigure(0, weight=1)
    right_frame.columnconfigure(1, weight=1)
    right_frame.columnconfigure(2, weight=1)

    # Top row: To-Do (col 0), Weather (col 1), Timer (col 2)
    todo_frame = ttk.Frame(right_frame)
    todo_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

    # ✅ add these:
    todo_frame.rowconfigure(0, weight=1)
    todo_frame.columnconfigure(0, weight=1)

    create_todo_list(todo_frame)

    weather_frame = ttk.Frame(right_frame)
    weather_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
    create_weather_widget(weather_frame)

    timer_frame = ttk.Frame(right_frame)
    timer_frame.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
    create_timer_widget(timer_frame)

    # Chatbot takes the entire lower section (row 1, spans all columns, direct child, no extra container)
    chatbot_frame = ttk.Frame(right_frame)
    chatbot_frame.grid(row=1, column=0, columnspan=3,
                       sticky="nsew", padx=2, pady=2)
    right_frame.grid_rowconfigure(1, weight=10)
    create_chatbot(chatbot_frame)

    weather_frame.rowconfigure(0, weight=1)
    weather_frame.columnconfigure(0, weight=1)
    timer_frame.rowconfigure(0, weight=1)
    timer_frame.columnconfigure(0, weight=1)
    chatbot_frame.rowconfigure(0, weight=1)
    chatbot_frame.columnconfigure(0, weight=1)

    # Haupt-Loop starten
    root.mainloop()


if __name__ == "__main__":
    main()
