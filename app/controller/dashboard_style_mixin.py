"""Responsibility: Style module (font/theme helpers) and dashboard bootstrap class."""

import tkinter as tk
import tkinter.font as tkfont

from app.core.config import (
    ADC_MAX,
    ADC_MIN,
    BG,
    BORDER,
    DEFAULT_BAUDRATE,
    DEFAULT_FALLBACK_FILE,
    DashboardState,
    FALLBACK_POLL_SEC,
    FG,
    MUTED,
    PANEL,
)
from app.controller.dashboard_connection_mixin import DashboardConnectionMixin
from app.controller.dashboard_parse_mixin import DashboardParseMixin
from app.controller.dashboard_runtime_mixin import DashboardRuntimeMixin
from app.io.readers import FileReader, SerialReader
from app.ui.layout_builder import build_ui


class DashboardStyleMixin:
    def init_fonts(self):
        self.font_title = tkfont.Font(family="Consolas", size=17, weight="bold")
        self.font_section = tkfont.Font(family="Consolas", size=13, weight="bold")
        self.font_label = tkfont.Font(family="Consolas", size=12)
        self.font_left_content = tkfont.Font(family="Consolas", size=10)
        self.font_value = tkfont.Font(family="Consolas", size=12, weight="bold")
        self.font_big = tkfont.Font(family="Consolas", size=18, weight="bold")
        self.font_mode = tkfont.Font(family="Consolas", size=18, weight="bold")
        self.font_mode_title = tkfont.Font(family="Consolas", size=18, weight="bold")
        self.font_mode_button = tkfont.Font(family="Consolas", size=34, weight="bold")
        self.font_button = tkfont.Font(family="Consolas", size=11)
        self.font_status = tkfont.Font(family="Consolas", size=11)

    def build_ui(self):
        build_ui(self)

    def style_frame(self, parent, **kwargs):
        frame = tk.Frame(
            parent,
            bg=PANEL,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
            **kwargs,
        )
        self.border_widgets.append(frame)
        return frame

    def set_border_color(self, color):
        for widget in self.border_widgets:
            try:
                widget.config(highlightbackground=color)
            except Exception:
                pass

    def style_label(self, parent, text="", font=None, fg=FG, bg=PANEL, **kwargs):
        if font is None:
            font = self.font_label
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)

    def style_button(self, parent, text, command, width=10):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            font=self.font_button,
            bg="#eeeeee",
            fg="black",
            relief="flat",
            bd=0,
            padx=4,
            pady=3,
        )

    def make_info_row(self, parent, key):
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", pady=3)

        key_label = self.style_label(row, text=f"{key} :", font=self.font_left_content, bg=PANEL, width=12, anchor="w")
        key_label.pack(side="left")

        value_label = self.style_label(row, text="", font=self.font_left_content, fg=MUTED, bg=PANEL, anchor="w")
        value_label.pack(side="left", fill="x", expand=True)

        return value_label

    def elide_text(self, text, max_len):
        text = str(text)
        if max_len < 4:
            return text[:max_len]
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    def get_adc_numeric(self):
        try:
            value = int(str(self.state.adc_value).strip())
        except ValueError:
            value = 0
        return max(ADC_MIN, min(ADC_MAX, value))

    def draw_adc_gauge(self, adc_numeric):
        self.adc_gauge_canvas.draw(adc_numeric, self.level_label, self.font_section, self.font_mode)

    def get_baudrate(self):
        try:
            return int(self.baud_entry.get().strip())
        except ValueError:
            return DEFAULT_BAUDRATE


class StyledDashboard(
    DashboardStyleMixin,
    DashboardConnectionMixin,
    DashboardParseMixin,
    DashboardRuntimeMixin,
):
    def __init__(self, root):
        self.root = root
        self.root.title("MCU UART Monitor Dashboard")
        self.root.geometry("980x820")
        self.root.configure(bg=BG)
        self.root.minsize(900, 700)
        self.root.resizable(True, True)

        self.running = True
        self.file_mode_active = False
        self.fallback_file_path = DEFAULT_FALLBACK_FILE
        self.fallback_poll_interval = FALLBACK_POLL_SEC

        self.last_logged_message = None
        self.current_section = None
        self.waiting_message_line = False

        self.port_map = {}
        self.border_widgets = []
        self.log_lines = []

        self.blink_on = True
        self.blink_interval_ms = 500

        self.base_width = 980
        self.base_height = 820
        self.current_scale = 1.0

        self.state = DashboardState()

        self.serial_reader = SerialReader(self._on_serial_line, self._on_serial_error)
        self.file_reader = FileReader(self._on_file_lines, self._on_file_status, self._on_file_error)

        self.init_fonts()
        self.build_ui()
        self.apply_scaled_styles(self.current_scale)
        self.refresh_ports(select_default=True)
        self.update_gui()
        self.schedule_blink_tick()

        self.root.after_idle(lambda: self.apply_scaled_styles(self.current_scale))
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
