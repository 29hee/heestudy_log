import tkinter as tk

from app.core.config import ADC_SAFE_COLOR, BG, BORDER, BOX, MUTED, NORMAL_COLOR
from app.ui.gauge_widget import AdcGaugeWidget


def build_status_panel(app, middle):
    """
    우측 상태 표시 패널 구축 | Build the right side status display panel
    ADC 게이지, 안전 레벨/락 배지, 모드 상태, 하단 요약 정보를 배치합니다.\n        Displays ADC value/gauge, safety level badge, lock badge, mode display, and bottom status bar.
    """
    right = app.style_frame(middle)
    right.grid(row=0, column=1, sticky="nsew")

    app.style_label(right, text="STATUS", font=app.font_section).pack(anchor="center", pady=(12, 8))

    app.status_card = tk.Frame(
        right,
        bg=BOX,
        highlightbackground=BORDER,
        highlightthickness=1,
        bd=0,
    )
    app.status_card.pack(fill="both", expand=True, padx=28, pady=(0, 12))

    app.number_row = tk.Frame(app.status_card, bg=BOX)
    app.number_row.pack(fill="x", padx=18, pady=(14, 10))
    app.number_row.grid_columnconfigure(0, weight=1)
    app.number_row.grid_columnconfigure(1, weight=1)

    app.number_title_label = app.style_label(app.number_row, text="NUMBER", font=app.font_section, bg=BOX)
    app.number_title_label.grid(row=0, column=0, sticky="w")

    app.number_label = app.style_label(app.number_row, text=app.state.adc_value, font=app.font_big, bg=BOX, fg="#ffff00")
    app.number_label.grid(row=0, column=1, sticky="e")

    app.adc_gauge_canvas = AdcGaugeWidget(app.status_card)
    app.adc_gauge_canvas.pack(fill="x", padx=18, pady=(0, 14))

    app.badge_title_row = tk.Frame(app.status_card, bg=BOX)
    app.badge_title_row.pack(fill="x", padx=18, pady=(0, 6))
    app.badge_title_row.grid_columnconfigure(0, weight=1)
    app.badge_title_row.grid_columnconfigure(1, weight=1)
    app.badge_title_row.grid_columnconfigure(2, weight=1)

    app.badge_level_title = app.style_label(
        app.badge_title_row,
        text="LEVEL",
        font=app.font_left_content,
        fg=MUTED,
        bg=BOX,
        anchor="center",
    )
    app.badge_level_title.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    app.badge_lock_title = app.style_label(
        app.badge_title_row,
        text="LOCK",
        font=app.font_left_content,
        fg=MUTED,
        bg=BOX,
        anchor="center",
    )
    app.badge_lock_title.grid(row=0, column=1, sticky="ew", padx=(0, 8))

    app.badge_button_title = app.style_label(
        app.badge_title_row,
        text="BUTTON",
        font=app.font_left_content,
        fg=MUTED,
        bg=BOX,
        anchor="center",
    )
    app.badge_button_title.grid(row=0, column=2, sticky="ew")

    app.badge_row = tk.Frame(app.status_card, bg=BOX)
    app.badge_row.pack(fill="x", padx=18, pady=(0, 18))
    app.badge_row.grid_columnconfigure(0, weight=1)
    app.badge_row.grid_columnconfigure(1, weight=1)
    app.badge_row.grid_columnconfigure(2, weight=1)

    app.level_label = tk.Label(
        app.badge_row,
        text=app.state.adc_state.upper(),
        font=app.font_mode,
        fg="white",
        bg=ADC_SAFE_COLOR,
        pady=4,
    )
    app.level_label.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    app.lock_label = tk.Label(
        app.badge_row,
        text="UNLOCK",
        font=app.font_mode,
        fg="white",
        bg=ADC_SAFE_COLOR,
        pady=4,
    )
    app.lock_label.grid(row=0, column=1, sticky="ew", padx=(0, 8))

    app.button_label = tk.Label(
        app.badge_row,
        text=app.state.button_status.upper(),
        font=app.font_mode,
        fg="white",
        bg=MUTED,
        pady=4,
    )
    app.button_label.grid(row=0, column=2, sticky="ew")

    app.mode_title_label = app.style_label(app.status_card, text="MODE", font=app.font_mode_title, bg=BOX)
    app.mode_title_label.pack(anchor="w", padx=18, pady=(0, 8))

    app.mode_label = tk.Label(
        app.status_card,
        text=app.state.mode,
        font=app.font_mode_button,
        fg="white",
        bg=NORMAL_COLOR,
        width=18,
        pady=42,
    )
    app.mode_label.pack(anchor="center", pady=(0, 18))

    app.bottom_label = app.style_label(
        app.root,
        text="STATUS: Disconnected",
        font=app.font_status,
        bg=BG,
    )
    app.bottom_label.pack(anchor="w", padx=12, pady=(0, 8))
