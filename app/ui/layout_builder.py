import tkinter as tk

from app.core.config import BG
from app.ui.layout_sections import build_left_panel, build_status_panel, build_top_controls


def build_ui(app):
    build_top_controls(app)

    middle = tk.Frame(app.root, bg=BG)
    middle.pack(fill="both", expand=True, padx=12, pady=(0, 10))
    middle.grid_columnconfigure(0, weight=1)
    middle.grid_columnconfigure(1, weight=3)
    middle.grid_rowconfigure(0, weight=1)

    build_left_panel(app, middle)
    build_status_panel(app, middle)
