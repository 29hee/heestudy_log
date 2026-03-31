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
        """
        폰트 초기화 함수 | Initialize all tkinter fonts used in the dashboard
        대시보드에 사용되는 모든 폰트(제목, 섹션, 레이블 등)를 초기화합니다.
        Initializes fonts for title, section headers, labels, and other UI elements.
        """
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
        """
        UI 레이아웃 구축 | Build the entire UI layout\n
        layout_builder를 호출하여 대시보드의 전체 UI를 구성합니다.\n
        Delegates to layout_builder.build_ui() to construct all UI components.
        """
        build_ui(self)

    def style_frame(self, parent, **kwargs):
        """
        스타일이 적용된 Frame 생성 | Create a styled Frame widget
        테마 색상(PANEL, BORDER)이 적용된 프레임을 생성하고 border_widgets에 등록합니다.
        Creates a frame with theme colors and registers it for border color updates.
        """
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
        """
        모든 테두리 위젯의 색상 변경 | Set border color for all tracked widgets
        border_widgets에 등록된 모든 위젯의 highlightbackground 색상을 일괄 변경합니다.
        Changes the border color of all widgets registered in border_widgets list.
        """
        for widget in self.border_widgets:
            try:
                widget.config(highlightbackground=color)
            except Exception:
                pass

    def style_label(self, parent, text="", font=None, fg=FG, bg=PANEL, **kwargs):
        """
        스타일이 적용된 Label 생성 | Create a styled Label widget
        폰트와 색상이 설정된 레이블을 생성합니다. (기본: font_label, FG/PANEL 색상)
        Creates a label with specified or default font and colors.
        """
        if font is None:
            font = self.font_label
        return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kwargs)

    def style_button(self, parent, text, command, width=10):
        """
        스타일이 적용된 Button 생성 | Create a styled Button widget
        flat 스타일의 버튼을 생성합니다. (폰트: font_button, 배경색: #eeeeee)
        Creates a button with flat relief style and custom padding.
        """
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
        """
        정보 행(key+value 레이아웃) 생성 | Create a key-value info row
        "키 : 값" 형식의 가로 배치 행을 생성합니다. 값 레이블을 반환하여 동적 업데이트 가능.
        Creates a horizontal row with key label on left and value label on right (returns value label).
        """
        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill="x", pady=3)

        key_label = self.style_label(row, text=f"{key} :", font=self.font_left_content, bg=PANEL, width=12, anchor="w")
        key_label.pack(side="left")

        value_label = self.style_label(row, text="", font=self.font_left_content, fg=MUTED, bg=PANEL, anchor="w")
        value_label.pack(side="left", fill="x", expand=True)

        return value_label

    def elide_text(self, text, max_len):
        """
        긴 텍스트 트림 | Truncate text with ellipsis if too long
        최대 길이를 초과하면 "..."으로 끝나도록 텍스트를 자릅니다.
        Truncates text to max_len characters and appends "..." if needed.
        """
        text = str(text)
        if max_len < 4:
            return text[:max_len]
        if len(text) <= max_len:
            return text
        return text[: max_len - 3] + "..."

    def get_adc_numeric(self):
        """
        현재 ADC 값(정수)을 반환 | Get current ADC value as integer
        state.adc_value를 정수로 변환하고 ADC_MIN~ADC_MAX 범위 내로 제한합니다.
        Converts state.adc_value to int and clamps it between ADC_MIN and ADC_MAX.
        """
        try:
            value = int(str(self.state.adc_value).strip())
        except ValueError:
            value = 0
        return max(ADC_MIN, min(ADC_MAX, value))

    def draw_adc_gauge(self, adc_numeric):
        """
        ADC 게이지 위젯 업데이트 | Update the ADC gauge canvas
        ADC 수치를 반영하여 게이지 위젯을 다시 그립니다.
        Calls AdcGaugeWidget.draw() to redraw the gauge with updated ADC value.
        """
        self.adc_gauge_canvas.draw(adc_numeric, self.level_label, self.font_section, self.font_mode)

    def get_baudrate(self):
        """
        현재 설정된 보드레이트 값을 반환 | Get current baud rate from entry field
        baud_entry 위젯에서 읽은 보드레이트 값을 반환합니다. (기본값: DEFAULT_BAUDRATE)
        Reads baud_entry and returns as int, defaulting to DEFAULT_BAUDRATE on error.
        """
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
        """
        대시보드 메인 클래스 초기화 | Initialize the StyledDashboard application
        4개 mixin을 상속받아 모든 기능(스타일, 연결, 파싱, 런타임)을 통합합니다.
        Initializes root window, state, readers, fonts, UI, and event handlers for the complete dashboard app.
        """
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
