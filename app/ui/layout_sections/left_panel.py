import tkinter as tk
from tkinter import scrolledtext

from app.core.config import BOX, FG, PANEL


def build_left_panel(app, middle):
    """
    좌측 정보 패널 구축 | Build the left side panel with status info and logs
    연결 상태(heartbeat/CAN/LIN/UART), 입력 정보, 로그 박스를 배치합니다.\n        Positions connection status rows, input info rows, and scrollable log display on the left side.
    """
    left = app.style_frame(middle)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

    top_left = tk.Frame(left, bg=PANEL)
    top_left.pack(fill="x", padx=14, pady=(12, 8))

    app.style_label(top_left, text="Connetion Status", font=app.font_section).pack(anchor="w", pady=(0, 10))

    app.heartbeat_row = app.make_info_row(top_left, "HeartBeat")
    app.can_row = app.make_info_row(top_left, "CAN")
    app.lin_row = app.make_info_row(top_left, "LIN")
    app.uart_row = app.make_info_row(top_left, "UART")

    input_box = tk.Frame(left, bg=PANEL)
    input_box.pack(fill="x", padx=14, pady=(0, 12))

    app.style_label(input_box, text="Input", font=app.font_section).pack(anchor="w", pady=(0, 8))
    app.input_from_row = app.make_info_row(input_box, "From")
    app.input_msg_row = app.make_info_row(input_box, "Message")

    log_frame = app.style_frame(left)
    log_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))

    app.style_label(log_frame, text="LOGS", font=app.font_section).pack(anchor="w", padx=10, pady=(8, 6))

    app.log_box = scrolledtext.ScrolledText(
        log_frame,
        width=48,
        height=10,
        font=app.font_left_content,
        bg=BOX,
        fg=FG,
        insertbackground="white",
        relief="flat",
        bd=0,
    )
    app.log_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    app.log_box.config(state="disabled")
