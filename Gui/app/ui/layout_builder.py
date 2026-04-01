import tkinter as tk

from app.core.config import BG
from app.ui.layout_sections import build_left_panel, build_status_panel, build_top_controls


def build_ui(app):
    """
    전체 UI 레이아웃 구축 | Build the complete dashboard UI layout
    상단 제어 패널, 좌측 상태 패널, 우측 상태 표시 패널을 순서대로 조립합니다.\n    Orchestrates top controls, left panel, and status panel builders into the main window.
    """
    build_top_controls(app)

    middle = tk.Frame(app.root, bg=BG)
    middle.pack(fill="both", expand=True, padx=12, pady=(0, 10))
    middle.grid_columnconfigure(0, weight=1)
    middle.grid_columnconfigure(1, weight=3)
    middle.grid_rowconfigure(0, weight=1)

    build_left_panel(app, middle)
    build_status_panel(app, middle)
