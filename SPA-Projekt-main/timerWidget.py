# timer_component.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def _beep(parent):
    # Works on many systems; simple and dependency-free
    try:
        parent.winfo_toplevel().bell()
    except Exception:
        pass

def build_timer_ui(parent, focus_minutes=1, break_minutes=1):
    """
    Builds a Focus(20) -> Break(5) timer UI inside `parent`.
    No Tk(), no mainloop().
    Returns the created frame.
    """
    frm = ttk.Frame(parent, padding=10)
    frm.pack(fill=BOTH, expand=True)

    phase_var = ttk.StringVar(value="Ready")
    time_var = ttk.StringVar(value=f"{focus_minutes:02d}:00")
    status_var = ttk.StringVar(value="Press Start to begin focus.")

    running = {"on": False}
    state = {"phase": "focus", "remaining": focus_minutes * 60, "job": None}

    def fmt(sec: int) -> str:
        m = sec // 60
        s = sec % 60
        return f"{m:02d}:{s:02d}"

    def set_phase(phase: str):
        state["phase"] = phase
        if phase == "focus":
            state["remaining"] = focus_minutes * 60
            phase_var.set(f"Focus ({focus_minutes} min)")
            status_var.set("Focus time.")
        else:
            state["remaining"] = break_minutes * 60
            phase_var.set(f"Break ({break_minutes} min)")
            status_var.set("Break time.")
        time_var.set(fmt(state["remaining"]))

    def stop_tick():
        running["on"] = False
        if state["job"] is not None:
            frm.after_cancel(state["job"])
            state["job"] = None

    def tick():
        if not running["on"]:
            return

        state["remaining"] -= 1
        if state["remaining"] < 0:
            state["remaining"] = 0
        time_var.set(fmt(state["remaining"]))

        if state["remaining"] == 0:
            _beep(frm)
            # auto-switch
            if state["phase"] == "focus":
                set_phase("break")
            else:
                set_phase("focus")
            # keep going automatically

        state["job"] = frm.after(1000, tick)

    def start():
        if running["on"]:
            return
        running["on"] = True
        start_btn.config(state="disabled")
        pause_btn.config(state="normal")
        reset_btn.config(state="normal")
        status_var.set("Running...")
        state["job"] = frm.after(1000, tick)

    def pause():
        if not running["on"]:
            return
        stop_tick()
        start_btn.config(state="normal")
        pause_btn.config(state="disabled")
        status_var.set("Paused.")

    def reset():
        stop_tick()
        set_phase("focus")
        start_btn.config(state="normal")
        pause_btn.config(state="disabled")
        reset_btn.config(state="disabled")
        status_var.set("Reset. Press Start to begin focus.")

    # UI
    ttk.Label(frm, textvariable=phase_var, font=("Helvetica", 12)).pack(pady=(6, 0))
    ttk.Label(frm, textvariable=time_var, font=("Helvetica", 26)).pack(pady=(4, 6))
    ttk.Label(frm, textvariable=status_var, wraplength=260, justify="center").pack(pady=(0, 8))

    btns = ttk.Frame(frm)
    btns.pack()

    start_btn = ttk.Button(btns, text="Start", bootstyle="success", command=start)
    pause_btn = ttk.Button(btns, text="Pause", bootstyle="warning", command=pause, state="disabled")
    reset_btn = ttk.Button(btns, text="Reset", bootstyle="secondary", command=reset, state="disabled")

    start_btn.grid(row=0, column=0, padx=4)
    pause_btn.grid(row=0, column=1, padx=4)
    reset_btn.grid(row=0, column=2, padx=4)

    set_phase("focus")
    return frm