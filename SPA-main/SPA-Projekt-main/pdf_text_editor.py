
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from io import BytesIO
from pathlib import Path


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
        "zoom_level": 1.0,  # Benutzer-Zoom (multipliziert mit default fit)
        "fit_zoom": 1.0,    # berechneter Fit-Zoom pro Seite/Canvas
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

    # --- Maus-Pan (wie "Hand"-Werkzeug) ---
    _drag_origin = {"x": 0, "y": 0}

    def _start_pan(evt):
        _drag_origin["x"], _drag_origin["y"] = evt.x, evt.y
        canvas.scan_mark(evt.x, evt.y)

    def _do_pan(evt):
        canvas.scan_dragto(evt.x, evt.y, gain=1)

    canvas.bind("<ButtonPress-1>", _start_pan)
    canvas.bind("<B1-Motion>", _do_pan)

    def _update_zoom_label():
        zoom_percent = int(pdf_state["zoom_level"] * 100)
        zoom_label.config(text=f"{zoom_percent}%")

    def _compute_fit_zoom(page, c_w, c_h):
        """Berechnet den Fit-Zoom (sodass die Seite in den Canvas passt)."""
        page_width = page.rect.width
        page_height = page.rect.height
        if c_w < 2 or c_h < 2 or page_width == 0 or page_height == 0:
            return 1.0
        # kleiner Rand
        avail_w = max(1, c_w - 20)
        avail_h = max(1, c_h - 20)
        zoom_x = avail_w / page_width
        zoom_y = avail_h / page_height
        return max(0.1, min(zoom_x, zoom_y))

    def render_page(page_num):
        """Rendern einer PDF-Seite"""
        if not pdf_state["pdf_doc"] or page_num < 0 or page_num >= pdf_state["total_pages"]:
            return

        try:
            # Canvas Maße
            canvas.update_idletasks()
            c_w, c_h = canvas.winfo_width(), canvas.winfo_height()
            if c_w < 2 or c_h < 2:
                return

            page = pdf_state["pdf_doc"][page_num]

            # Fit-Zoom neu berechnen (abhängig von Canvas-Größe & Seite)
            pdf_state["fit_zoom"] = _compute_fit_zoom(page, c_w, c_h)

            # Gesamt-Zoom = Fit * Benutzer-Zoom
            final_zoom = pdf_state["fit_zoom"] * pdf_state["zoom_level"]

            # Render
            pix = page.get_pixmap(matrix=fitz.Matrix(final_zoom, final_zoom))
            img_data = pix.tobytes("ppm")
            img = Image.open(BytesIO(img_data))
            photo = ImageTk.PhotoImage(img)

            # Canvas aktualisieren (nur 1x löschen)
            canvas.delete("all")
            # Wir zeichnen ab (0,0), nutzen aber Scrollregion für Panning/Scrollbars
            canvas.create_image(0, 0, image=photo, anchor="nw")
            canvas.config(scrollregion=(0, 0, pix.width, pix.height))

            # State/UI aktualisieren
            pdf_state["photo_image"] = photo
            pdf_state["current_page"] = page_num
            page_label.config(
                text=f"Seite {page_num + 1}/{pdf_state['total_pages']}")
            _update_zoom_label()

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
            pdf_state["zoom_level"] = 1.0

            file_name = Path(file_path).name
            file_label.config(text=f"📄 {file_name}", foreground="green")

            render_page(0)

            # Fokus aufs Canvas, damit Keybindings wirken
            canvas.focus_set()

            messagebox.showinfo(
                "Erfolg", f"PDF geladen: {file_name}\n({pdf_state['total_pages']} Seiten)"
            )

        except Exception as e:
            messagebox.showerror(
                "Fehler", f"Fehler beim Öffnen der PDF:\n{str(e)}")

    def prev_page():
        if pdf_state["pdf_doc"] and pdf_state["current_page"] > 0:
            render_page(pdf_state["current_page"] - 1)

    def next_page():
        if pdf_state["pdf_doc"] and pdf_state["current_page"] < pdf_state["total_pages"] - 1:
            render_page(pdf_state["current_page"] + 1)

    def go_first(_evt=None):
        if pdf_state["pdf_doc"]:
            render_page(0)

    def go_last(_evt=None):
        if pdf_state["pdf_doc"]:
            render_page(pdf_state["total_pages"] - 1)

    def page_up(_evt=None):
        """Seite 'hoch' → vorherige Seite"""
        prev_page()

    def page_down(_evt=None):
        """Seite 'runter' → nächste Seite"""
        next_page()

    def change_zoom(factor):
        pdf_state["zoom_level"] = max(
            0.2, min(pdf_state["zoom_level"] * factor, 5.0))
        render_page(pdf_state["current_page"])

    def set_zoom(z):
        pdf_state["zoom_level"] = max(0.2, min(z, 5.0))
        render_page(pdf_state["current_page"])

    def zoom_in():
        change_zoom(1.1)

    def zoom_out():
        change_zoom(0.9)

    def reset_zoom():
        pdf_state["zoom_level"] = 1.0
        render_page(pdf_state["current_page"])

    # --- Panning per Tastatur ---
    def keyboard_pan(dx_units, dy_units, fast=False):
        """Scrollt Canvas in 'units'. Bei fast=True stärkere Schritte."""
        step = 6 if fast else 2
        if dx_units != 0:
            for _ in range(abs(dx_units) * step):
                canvas.xview_scroll(1 if dx_units > 0 else -1, "units")
        if dy_units != 0:
            for _ in range(abs(dy_units) * step):
                canvas.yview_scroll(1 if dy_units > 0 else -1, "units")

    # ---- Tastatur-Handling (mit Fokus) ----
    # Wichtig: bind_all sorgt dafür, dass die Pfeile auch ohne expliziten Fokus greifen.
    # Wenn du es strenger willst, nutze canvas.bind statt root.bind_all.
    root.bind_all("<Left>", lambda e: prev_page())
    root.bind_all("<Right>", lambda e: next_page())
    root.bind_all("<Home>", go_first)
    root.bind_all("<End>", go_last)
    root.bind_all("<Prior>", page_up)    # PageUp
    root.bind_all("<Next>", page_down)   # PageDown

    # Pfeile für Panning
    root.bind_all("<Up>", lambda e: keyboard_pan(0, -1, fast=False))
    root.bind_all("<Down>", lambda e: keyboard_pan(0,  1, fast=False))
    root.bind_all("<Shift-Up>", lambda e: keyboard_pan(0, -1, fast=True))
    root.bind_all("<Shift-Down>", lambda e: keyboard_pan(0,  1, fast=True))
    root.bind_all("<Shift-Left>", lambda e: keyboard_pan(-1, 0, fast=True))
    root.bind_all("<Shift-Right>", lambda e: keyboard_pan(1, 0, fast=True))

    # Zoom per Tastatur
    root.bind_all("<Control-Up>", lambda e: zoom_in())
    root.bind_all("<Control-Down>", lambda e: zoom_out())
    root.bind_all("+", lambda e: zoom_in())
    root.bind_all("=", lambda e: zoom_in())  # US-Layout
    root.bind_all("-", lambda e: zoom_out())
    root.bind_all("0", lambda e: reset_zoom())

    # Zoom per Maus (Ctrl + Wheel)
    def wheel_zoom(event):
        delta = getattr(event, "delta", 0)
        num = getattr(event, "num", None)
        if num == 4 or delta > 0:   # Linux up / Windows positive delta
            zoom_in()
        else:
            zoom_out()

    canvas.bind("<Control-MouseWheel>", wheel_zoom)     # Windows
    canvas.bind("<Control-Button-4>", wheel_zoom)       # Linux up
    canvas.bind("<Control-Button-5>", wheel_zoom)       # Linux down

    # Buttons
    btn_open.config(command=open_pdf)
    btn_zoom_in.config(command=zoom_in)
    btn_zoom_out.config(command=zoom_out)
    btn_zoom_reset.config(command=reset_zoom)
    btn_prev.config(command=prev_page)
    btn_next.config(command=next_page)

    # Bei Größenänderung neu rendern (Fit-Zoom aktualisieren)
    def on_resize(evt):
        # nur neu rendern, wenn das Canvas selbst seine Größe ändert
        if evt.widget is canvas:
            render_page(pdf_state["current_page"])

    canvas.bind("<Configure>", on_resize)

    return pdf_frame
