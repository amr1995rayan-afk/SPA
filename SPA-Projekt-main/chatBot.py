import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from Chatbotai import build_chat_ui

def create_chatbot(parent):
    chat_frame = ttk.Labelframe(parent, text="Chat", bootstyle="primary")
    chat_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

    build_chat_ui(chat_frame)
    return chat_frame