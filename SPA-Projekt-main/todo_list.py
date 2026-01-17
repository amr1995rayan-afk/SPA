import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox

def create_todo_list(root):

    # --- Frame ---
    # To-Do-Liste erstellen
    todo_frame = ttk.Labelframe(root, text="To-Do List", bootstyle="primary", height=100)  # Höhe direkt begrenzen
    todo_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    # Spaltenbreite konfigurieren
    todo_frame.grid_columnconfigure(0, weight=1)

    # Zeilenhöhe konfigurieren (reduzieren)
    todo_frame.grid_rowconfigure(1, weight=0)  # Minimale Höhe

    # Übergeordneten Container konfigurieren
    root.rowconfigure(0, weight=1)  # Weniger Platz für die Zeile 0
    # ======================
    #   Toolbar: 2 Buttons
    # ======================
    toolbar = ttk.Frame(todo_frame)
    toolbar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
    toolbar.grid_columnconfigure(3, weight=1)

    btn_delete_selected = ttk.Button(toolbar, text="Markierte löschen", bootstyle=DANGER)
    btn_edit_selected   = ttk.Button(toolbar, text="Markierte bearbeiten", bootstyle=INFO)

    btn_delete_selected.grid(row=0, column=0, padx=(0, 8))
    btn_edit_selected.grid(row=0, column=1)

    # --- Status: sind wir im Bearbeitungsmodus? ---
    todo_frame._state = {
        "tasks": [],
        "editing_active": False,   # globaler Modus-Schalter
        "widgets": {}
    }

    # --- Eingabezeile ---
    input_frame = ttk.Frame(todo_frame)
    input_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 4))
    input_frame.grid_columnconfigure(1, weight=1)

    ttk.Label(input_frame, text="Neue Aufgabe:").grid(row=0, column=0, padx=(0, 6))
    task_entry = ttk.Entry(input_frame)
    task_entry.grid(row=0, column=1, sticky="ew")
    add_btn = ttk.Button(input_frame, text="Hinzufügen", bootstyle=SUCCESS)
    add_btn.grid(row=0, column=2, padx=(6, 0))
    todo_frame._state["widgets"]["task_entry"] = task_entry

    # --- Scrollbereich ---
    scroll_container = ttk.Frame(todo_frame)
    scroll_container.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 8))
    scroll_container.grid_rowconfigure(0, weight=1)
    scroll_container.grid_columnconfigure(0, weight=1)

    canvas = tk.Canvas(scroll_container, highlightthickness=0)
    items_frame = ttk.Frame(canvas)
    scrollbar = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    items_window = canvas.create_window((0, 0), window=items_frame, anchor="nw")

    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        canvas.itemconfigure(items_window, width=event.width)

    items_frame.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)

    # --- Zeile erstellen ---
    def _create_task_row(text):
        row = ttk.Frame(items_frame)
        row.pack(fill="x", padx=4, pady=3)

        selected_var = tk.BooleanVar(value=False)
        select_cb = ttk.Checkbutton(row, text="", variable=selected_var)
        select_cb.pack(side="left", padx=(2, 8))

        # Start: Label sichtbar, Entry verborgen
        label = ttk.Label(row, text=text)
        label.pack(side="left", fill="x", expand=True)

        entry = ttk.Entry(row)
        entry.insert(0, text)
        # Entry erst bei Bearbeitung zeigen, sonst versteckt:
        entry.pack_forget()

        # Enter im Entry speichert direkt die Zeile
        def _save_row_from_entry(event=None):
            new_text = entry.get().strip()
            if not new_text:
                messagebox.showinfo("Hinweis", "Der Text darf nicht leer sein.")
                return
            label.configure(text=new_text)
            row._meta["text"] = new_text
            # zurückwechseln: Entry verstecken, Label zeigen
            entry.pack_forget()
            label.pack(side="left", fill="x", expand=True)
            row._meta["editing"] = False

        entry.bind("<Return>", _save_row_from_entry)

        row._meta = {
            "text": text,
            "vars": {"selected_var": selected_var},
            "widgets": {"label": label, "entry": entry, "select_cb": select_cb},
            "editing": False,  # Zeilen-Editing aktiv?
        }

        todo_frame._state["tasks"].append(row)

    # --- Hinzufügen ---
    def _add_task(event=None):
        txt = task_entry.get().strip()
        if not txt:
            messagebox.showinfo("Hinweis", "Bitte gib einen Aufgabentext ein.")
            return
        _create_task_row(txt)
        task_entry.delete(0, tk.END)

    add_btn.configure(command=_add_task)
    task_entry.bind("<Return>", _add_task)

    # --- Auswahl abrufen ---
    def _get_selected_rows():
        return [row for row in todo_frame._state["tasks"] if row._meta["vars"]["selected_var"].get()]

    # --- Markierte löschen ---
    def _delete_selected():
        selected = _get_selected_rows()
        if not selected:
            messagebox.showinfo("Hinweis", "Keine Aufgaben markiert.")
            return
        if not messagebox.askyesno("Löschen bestätigen", f"{len(selected)} markierte Aufgabe(n) löschen?"):
            return
        for row in selected:
            if row in todo_frame._state["tasks"]:
                todo_frame._state["tasks"].remove(row)
            row.destroy()

    btn_delete_selected.configure(command=_delete_selected)

    # --- Markierte bearbeiten (Inline) ---
    def _start_edit_selected():
        selected = _get_selected_rows()
        if not selected:
            messagebox.showinfo("Hinweis", "Keine Aufgaben markiert.")
            return

        # Für jede markierte Zeile: Label -> Entry
        for row in selected:
            if row._meta["editing"]:
                continue
            label = row._meta["widgets"]["label"]
            entry = row._meta["widgets"]["entry"]

            # Text vom Label in Entry sicherstellen
            entry.delete(0, tk.END)
            entry.insert(0, row._meta["text"])

            # Label verstecken, Entry zeigen
            label.pack_forget()
            entry.pack(side="left", fill="x", expand=True)
            row._meta["editing"] = True

        # Globale UI: Button zum Speichern umschalten
        todo_frame._state["editing_active"] = True
        btn_edit_selected.configure(text="Änderungen speichern", bootstyle=SUCCESS, command=_save_edit_selected)

    def _save_edit_selected(event=None):
        # Speichert alle bearbeitenden (markierten oder nicht) Zeilen
        any_edited = False
        for row in list(todo_frame._state["tasks"]):
            if row._meta["editing"]:
                any_edited = True
                entry = row._meta["widgets"]["entry"]
                label = row._meta["widgets"]["label"]
                new_text = entry.get().strip()
                if not new_text:
                    # bei leerem Text nicht speichern – Zeile im Edit-Modus lassen
                    continue
                row._meta["text"] = new_text
                label.configure(text=new_text)
                # zurückwechseln
                entry.pack_forget()
                label.pack(side="left", fill="x", expand=True)
                row._meta["editing"] = False
                # optional: Auswahl entfernen
                row._meta["vars"]["selected_var"].set(False)

        if not any_edited:
            messagebox.showinfo("Hinweis", "Keine Zeile befindet sich im Bearbeitungsmodus.")
            return

        # Globalen Modus beenden und Button zurücksetzen
        todo_frame._state["editing_active"] = False
        btn_edit_selected.configure(text="Markierte bearbeiten", bootstyle=INFO, command=_start_edit_selected)

    # Button initial: startet die Bearbeitung
    btn_edit_selected.configure(command=_start_edit_selected)

    # Optional: Beispiel-Tasks
    for t in ["Task 1", "Task 2", "Task 3"]:
        _create_task_row(t)

    return todo_frame

