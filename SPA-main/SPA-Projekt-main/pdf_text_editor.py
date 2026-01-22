import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from io import BytesIO
from pathlib import Path
import pyperclip


def create_pdf_text_editor(root):
    pdf_frame = ttk.Frame(root, bootstyle="secondary")
    pdf_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)
    pdf_frame.rowconfigure(0, weight=0)  # Toolbar
    pdf_frame.rowconfigure(1, weight=0)  # Page controls
    pdf_frame.rowconfigure(2, weight=1)  # PDF viewer
    pdf_frame.columnconfigure(0, weight=1)

    # State
    pdf_state = {
        "current_file": None,
        "pdf_doc": None,
        "current_page": 0,
        "total_pages": 0,
        "photo_image": None,  # Keep reference to prevent garbage collection
        "zoom_level": 1.0,  # Zoom Faktor
    }

    # Toolbar
    toolbar = ttk.Frame(pdf_frame)
    toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    toolbar.columnconfigure(3, weight=1)

    file_label = ttk.Label(
        toolbar, text="Keine Datei geöffnet", foreground="gray")
    file_label.grid(row=0, column=0, padx=(0, 10))

    btn_open = ttk.Button(toolbar, text="PDF öffnen", bootstyle="success")
    btn_open.grid(row=0, column=1, padx=2)

    zoom_label = ttk.Label(toolbar, text="100%", font=("Helvetica", 9))
    zoom_label.grid(row=0, column=2, padx=5)

    btn_zoom_in = ttk.Button(toolbar, text="🔍+", bootstyle="info", width=3)
    btn_zoom_in.grid(row=0, column=3, padx=2)

    btn_zoom_out = ttk.Button(toolbar, text="🔍-", bootstyle="info", width=3)
    btn_zoom_out.grid(row=0, column=4, padx=2)

    btn_zoom_reset = ttk.Button(
        toolbar, text="↺ Zoom", bootstyle="secondary", width=5)
    btn_zoom_reset.grid(row=0, column=5, padx=2)

    # Page controls
    controls = ttk.Frame(pdf_frame)
    controls.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
    controls.columnconfigure(2, weight=1)

    btn_prev = ttk.Button(controls, text="◀ Zurück",
                          bootstyle="secondary", width=10)
    btn_prev.grid(row=0, column=0, padx=2)

    page_label = ttk.Label(controls, text="Seite 1/1", font=("Helvetica", 10))
    page_label.grid(row=0, column=1, padx=10)

    btn_next = ttk.Button(controls, text="Weiter ▶",
                          bootstyle="secondary", width=10)
    btn_next.grid(row=0, column=3, padx=2)

    # Canvas für PDF Anzeige
    canvas_frame = ttk.Frame(pdf_frame)
    canvas_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
    canvas_frame.rowconfigure(0, weight=1)
    canvas_frame.columnconfigure(0, weight=1)

    canvas = tk.Canvas(canvas_frame, bg="#2b2b2b", highlightthickness=0)
    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar_y = ttk.Scrollbar(
        canvas_frame, orient="vertical", command=canvas.yview)
    scrollbar_y.grid(row=0, column=1, sticky="ns")
    scrollbar_x = ttk.Scrollbar(
        canvas_frame, orient="horizontal", command=canvas.xview)
    scrollbar_x.grid(row=1, column=0, sticky="ew")

    canvas.configure(yscrollcommand=scrollbar_y.set,
                     xscrollcommand=scrollbar_x.set)

    def render_page(page_num):
        """Rendern einer PDF-Seite"""
        if not pdf_state["pdf_doc"] or page_num < 0 or page_num >= pdf_state["total_pages"]:
            return

        try:
            # Canvas aktualisieren um aktuelle Größe zu bekommen
            canvas.update()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            if canvas_width < 2 or canvas_height < 2:
                return  # Canvas hat noch keine Größe

            page = pdf_state["pdf_doc"][page_num]

            # Get page dimensions
            page_width = page.rect.width
            page_height = page.rect.height

            # Berechne Standard-Zoom-Faktor um PDF optimal anzuzeigen
            zoom_x = (canvas_width - 20) / page_width
            zoom_y = (canvas_height - 20) / page_height
            # Nutze kleineren Zoom um in Canvas zu passen
            default_zoom = min(zoom_x, zoom_y)
            default_zoom = max(default_zoom, 0.5)  # Minimum zoom

            # Wende benutzer-zoom an
            final_zoom = default_zoom * pdf_state["zoom_level"]

            # Render mit berechnetem Zoom
            pix = page.get_pixmap(matrix=fitz.Matrix(final_zoom, final_zoom))
            img_data = pix.tobytes("ppm")

            img = Image.open(BytesIO(img_data))
            photo = ImageTk.PhotoImage(img)

            # Update canvas
            canvas.delete("all")
            canvas.create_image(0, 0, image=photo, anchor="nw")

            # Update zoom label
            zoom_percent = int(pdf_state["zoom_level"] * 100)
            zoom_label.config(text=f"{zoom_percent}%")

            # Update canvas
            canvas.delete("all")
            canvas.create_image(0, 0, image=photo, anchor="nw")
            canvas.config(scrollregion=canvas.bbox("all"))

            # Keep reference
            pdf_state["photo_image"] = photo
            pdf_state["current_page"] = page_num

            page_label.config(
                text=f"Seite {page_num + 1}/{pdf_state['total_pages']}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Rendern:\n{str(e)}")

    def open_pdf():
        """Öffne eine PDF-Datei"""
        file_path = filedialog.askopenfilename(
            title="PDF öffnen",
            filetypes=[("PDF Dateien", "*.pdf"), ("Alle Dateien", "*.*")]
        )
        if not file_path:
            return

        try:
            if pdf_state["pdf_doc"]:
                pdf_state["pdf_doc"].close()

            pdf_state["current_file"] = file_path
            pdf_state["pdf_doc"] = fitz.open(file_path)
            pdf_state["total_pages"] = len(pdf_state["pdf_doc"])
            pdf_state["current_page"] = 0

            file_name = Path(file_path).name
            file_label.config(text=f"📄 {file_name}", foreground="green")

            # Render first page
            render_page(0)

            messagebox.showinfo(
                "Erfolg", f"PDF geladen: {file_name}\n({pdf_state['total_pages']} Seiten)")

        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Fehler beim Öffnen der PDF:\n{str(e)}")

    def prev_page():
        """Vorige Seite"""
        if pdf_state["pdf_doc"] and pdf_state["current_page"] > 0:
            render_page(pdf_state["current_page"] - 1)

    def next_page():
        """Nächste Seite"""
        if pdf_state["pdf_doc"] and pdf_state["current_page"] < pdf_state["total_pages"] - 1:
            render_page(pdf_state["current_page"] + 1)

    def zoom_in():
        """Zoom vergrößern"""
        pdf_state["zoom_level"] = min(pdf_state["zoom_level"] + 0.2, 3.0)
        render_page(pdf_state["current_page"])

    def zoom_out():
        """Zoom verkleinern"""
        pdf_state["zoom_level"] = max(pdf_state["zoom_level"] - 0.2, 0.5)
        render_page(pdf_state["current_page"])

    def reset_zoom():
        """Zoom zurücksetzen"""
        pdf_state["zoom_level"] = 1.0
        render_page(pdf_state["current_page"])

    btn_open.config(command=open_pdf)
    btn_zoom_in.config(command=zoom_in)
    btn_zoom_out.config(command=zoom_out)
    btn_zoom_reset.config(command=reset_zoom)
    btn_prev.config(command=prev_page)
    btn_next.config(command=next_page)

    # Keyboard shortcuts
    def on_key(event):
        if event.keysym == "Left":
            prev_page()
        elif event.keysym == "Right":
            next_page()
        elif event.keysym == "Up":
            # Scroll Text-Viewer oben / oder Canvas scrolling
            canvas.yview_scroll(-3, "units")
            text_display.yview_scroll(-3, "units")
        elif event.keysym == "Down":
            # Scroll Text-Viewer unten / oder Canvas scrolling
            canvas.yview_scroll(3, "units")
            text_display.yview_scroll(3, "units")
        elif event.keysym == "Home":
            # Zum Anfang gehen
            render_page(0)
        elif event.keysym == "End":
            # Zur letzten Seite gehen
            if pdf_state["pdf_doc"]:
                render_page(pdf_state["total_pages"] - 1)
        elif event.keysym == "plus" or event.keysym == "equal":
            # Zoom in
            zoom_in()
        elif event.keysym == "minus":
            # Zoom out
            zoom_out()
        elif event.keysym == "0":
            # Zoom reset
            reset_zoom()

    pdf_frame.bind("<Left>", on_key)
    pdf_frame.bind("<Right>", on_key)
    pdf_frame.bind("<Up>", on_key)
    pdf_frame.bind("<Down>", on_key)
    pdf_frame.bind("<Home>", on_key)
    pdf_frame.bind("<End>", on_key)

    return pdf_frame
