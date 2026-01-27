from openai import OpenAI
from ttkbootstrap.scrolled import ScrolledText
from ttkbootstrap.constants import *
import ttkbootstrap as ttk
import threading
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def build_chat_ui(parent):
    print("✅ build_chat_ui CALLED")
    """
    Builds a chat UI inside `parent`.
    Requires env var GITHUB_TOKEN (for GitHub Models) or OPENAI_API_KEY (for OpenAI).
    """

    # --- Frame ---
    frame = ttk.Frame(parent, padding=10)
    frame.pack(fill=BOTH, expand=True)

    # --- Provider Selection ---
    provider_frame = ttk.Frame(frame)
    provider_frame.pack(fill=X, pady=(0, 10))

    ttk.Label(provider_frame, text="KI-Anbieter:").pack(side="left", padx=(0, 10))

    provider_var = ttk.StringVar(value="github")
    providers = {
        "github": "GitHub Models",
        "openai": "OpenAI",
        "perplexity": "Perplexity"
    }

    for key, label in providers.items():
        ttk.Radiobutton(provider_frame, text=label,
                        variable=provider_var, value=key).pack(side="left", padx=5)

    # --- Initialize client based on provider ---
    def get_client():
        provider = provider_var.get()

        if provider == "github":
            token = os.getenv("GITHUB_TOKEN")
            if not token:
                raise RuntimeError(
                    "Set GITHUB_TOKEN in your environment first.")
            client = OpenAI(
                api_key=token, base_url="https://models.github.ai/inference")
            return client, "gpt-4o-mini"

        elif provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
            if not key:
                raise RuntimeError(
                    "Set OPENAI_API_KEY in your environment first.")
            client = OpenAI(api_key=key)
            return client, "gpt-4o-mini"

        elif provider == "perplexity":
            key = os.getenv("PERPLEXITY_API_KEY")
            if not key:
                raise RuntimeError(
                    "Set PERPLEXITY_API_KEY in your environment first.")
            client = OpenAI(api_key=key, base_url="https://api.perplexity.ai")
            return client, "llama-3.1-sonar-small-128k-online"

    # --- Conversation state ---
    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    # --- Widgets ---
    chat_box = ScrolledText(frame, autohide=True, height=14)
    chat_box.pack(fill=BOTH, expand=True)
    # ScrolledText wraps a Text widget
    chat_box.text.configure(state="disabled")

    status_var = ttk.StringVar(value="Ready")
    ttk.Label(frame, textvariable=status_var).pack(anchor="w", pady=(6, 0))

    bottom = ttk.Frame(frame)
    bottom.pack(fill=X, pady=(6, 0))

    user_entry = ttk.Entry(bottom)
    user_entry.pack(side=LEFT, fill=X, expand=True)

    send_btn = ttk.Button(bottom, text="Send", bootstyle="success")
    send_btn.pack(side=LEFT, padx=(6, 0))

    def append(role, text):
        chat_box.text.configure(state="normal")
        prefix = "You: " if role == "user" else "Assistant: "
        chat_box.text.insert("end", f"{prefix}{text}\n\n")
        chat_box.text.see("end")
        chat_box.text.configure(state="disabled")

    def set_busy(is_busy: bool):
        send_btn.config(state="disabled" if is_busy else "normal")
        user_entry.config(state="disabled" if is_busy else "normal")

    def send_message(event=None):
        print("SEND CLICKED")

        user_text = user_entry.get().strip()
        if not user_text:
            return

        user_entry.delete(0, "end")
        append("user", user_text)

        messages.append({"role": "user", "content": user_text})
        status_var.set("Thinking...")
        set_busy(True)

        def worker():
            try:
                client, model_name = get_client()
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=500,
                )
                reply = resp.choices[0].message.content
                # update UI on main thread
                frame.after(0, lambda: on_success(reply))
            except Exception as e:
                frame.after(0, lambda: on_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def on_success(reply: str):
        messages.append({"role": "assistant", "content": reply})
        append("assistant", reply)
        status_var.set("Ready")
        set_busy(False)

    def on_error(e: Exception):
        append("assistant", f"⚠️ Error: {e}")
        status_var.set("Ready")
        set_busy(False)

    send_btn.config(command=send_message)
    user_entry.bind("<Return>", send_message)
    user_entry.focus()

    return frame
