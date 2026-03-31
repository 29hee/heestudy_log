import tkinter as tk

from app.core.config import BG, DEFAULT_BAUDRATE, PANEL


def build_top_controls(app):
    """
    상단 제어 패널 구축 | Build the top control bar with port/mode/baud settings
    제목, 포트 선택, 모드 선택, 보드레이트 입력, 포트 갱신/연결/연결 해제 버튼을 배치합니다.\n        Builds title, serial mode dropdown, port dropdown, baud rate entry, and control buttons.
    """
    title = app.style_label(
        app.root,
        text="MCU Monitor Dashboard",
        font=app.font_title,
        bg=BG,
    )
    title.pack(anchor="w", padx=12, pady=(10, 8))

    port_frame = app.style_frame(app.root)
    port_frame.pack(fill="x", padx=12, pady=(0, 10))

    app.style_label(port_frame, text="Serial Port Control", font=app.font_section).pack(anchor="w", padx=10, pady=(8, 6))

    row = tk.Frame(port_frame, bg=PANEL)
    row.pack(fill="x", padx=10, pady=(0, 10))

    app.style_label(row, text="Mode", bg=PANEL).pack(side="left", padx=(0, 6))
    app.conn_mode_var = tk.StringVar(value="Serial")
    app.conn_mode_menu = tk.OptionMenu(row, app.conn_mode_var, "Serial", "File")
    app.conn_mode_menu.config(width=8, font=("Consolas", 11), bg="white")
    app.conn_mode_menu.pack(side="left", padx=(0, 10))

    app.style_label(row, text="port", bg=PANEL).pack(side="left", padx=(0, 6))

    app.port_var = tk.StringVar()
    app.port_menu = tk.OptionMenu(row, app.port_var, "")
    app.port_menu.config(width=10, font=app.font_button, bg="white")
    app.port_menu.pack(side="left", padx=(0, 10))

    app.style_label(row, text="Baud", bg=PANEL).pack(side="left", padx=(0, 6))
    app.baud_entry = tk.Entry(row, width=10, font=app.font_button)
    app.baud_entry.insert(0, str(DEFAULT_BAUDRATE))
    app.baud_entry.pack(side="left", padx=(0, 10))

    app.style_button(row, "refresh ports", app.refresh_ports, 12).pack(side="left", padx=4)
    app.style_button(row, "connect", app.connect_serial, 10).pack(side="left", padx=4)
    app.style_button(row, "disconnect", app.disconnect_serial, 10).pack(side="left", padx=4)
