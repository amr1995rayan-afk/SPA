import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def create_pdf_text_editor(root):
    pdf_frame = ttk.Frame(root, bootstyle="secondary")
    pdf_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
    ttk.Label(pdf_frame, text="PDF and Text Editor", font=("Helvetica", 16)).pack(pady=20)
    return pdf_frame

