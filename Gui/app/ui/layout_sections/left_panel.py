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

    app.style_label(top_left, text="Connetion Status", font=app.font_section).pack(anchor="w", pady=(0, 4))

    app.heartbeat_row = app.make_info_row(top_left, "HeartBeat")
    app.can_row = app.make_info_row(top_left, "CAN")
    app.lin_row = app.make_info_row(top_left, "LIN")
    app.uart_row = app.make_info_row(top_left, "UART")

    input_box = tk.Frame(left, bg=PANEL)
    input_box.pack(fill="x", padx=14, pady=(0, 8))

    app.style_label(input_box, text="Status", font=app.font_section).pack(anchor="w", pady=(0, 4))
    app.status_mode_row = app.make_info_row(input_box, "Mode")
    app.status_canmsg_row = app.make_info_row(input_box, "CAN msg")
    app.status_linmsg_row = app.make_info_row(input_box, "LIN msg")

    flow_box = app.style_frame(left)
    flow_box.pack(fill="x", padx=14, pady=(0, 8))
    app.style_label(flow_box, text="DATA FLOW", font=app.font_section).pack(anchor="w", padx=10, pady=(8, 6))

    app.flow_step_labels = {}
    flow_items = [
        ("adc_to_master", "1. Slave1 ADC -> LIN -> Master"),
        ("master_decision", "2. Master decide -> LOCK hold"),
        ("master_to_can", "3. Master -> CAN Emergency -> Slave2"),
        ("can_release", "4. Slave2 button -> CAN Release"),
        ("master_unlock", "5. Master -> LIN Unlock -> Slave1"),
        ("uart_to_gui", "6. Master UART -> PC GUI"),
    ]
    for key, text in flow_items:
        lbl = app.style_label(
            flow_box,
            text=text,
            font=app.font_left_content,
            bg=PANEL,
            fg=FG,
            anchor="w",
            justify="left",
        )
        lbl.pack(fill="x", padx=10, pady=(0, 2))
        app.flow_step_labels[key] = lbl

    app.flow_detail_label = app.style_label(
        flow_box,
        text="Waiting UART data...",
        font=app.font_left_content,
        bg=PANEL,
        fg="#9ad3ff",
        anchor="w",
        justify="left",
    )
    app.flow_detail_label.pack(fill="x", padx=10, pady=(4, 8))

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
    app.log_box.bind("<ButtonRelease-1>", app.on_log_click)
    app.log_box.config(state="disabled")
