# chatBot.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from Chatbotai import build_chat_ui   # ✅ import your real chat UI

def create_chatbot(parent):
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    chat_frame = ttk.Labelframe(parent, text="Chat", bootstyle="primary")
    chat_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # ✅ mount the real chat UI inside this frame
    build_chat_ui(chat_frame)

    return chat_frame
