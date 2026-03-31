"""Responsibility: Runtime module (event loop, UI refresh, resize/close lifecycle)."""

import sys
import time

import tkinter as tk

from app.core.config import (
    ADC_DANGER_COLOR,
    ADC_SAFE_COLOR,
    ADC_WARNING_COLOR,
    BORDER,
    BOX,
    EM_COLOR,
    FG,
    MUTED,
    NORMAL_COLOR,
)


class DashboardRuntimeLoopMixin:
    def schedule_blink_tick(self):
        if not self.running:
            return
        self.blink_on = not self.blink_on
        self.root.after(self.blink_interval_ms, self.schedule_blink_tick)

    def add_log(self, text, add_to_panel=True, add_to_terminal=True):
        timestamp = time.strftime("%H:%M:%S")
        line = f"{timestamp} {text}"
        if add_to_terminal:
            print(line)

        if not add_to_panel:
            return

        self.log_lines.append(line)
        self.log_lines = self.log_lines[-100:]

        self.log_box.config(state="normal")
        self.log_box.delete("1.0", tk.END)
        self.log_box.insert(tk.END, "\n".join(self.log_lines))
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")


class DashboardRuntimeViewMixin:
    def update_gui(self):
        left_px = self.heartbeat_row.winfo_width()
        if left_px <= 1:
            left_px = 300
        max_chars = max(18, min(72, left_px // 8))

        self.heartbeat_row.config(text=self.elide_text(self.state.heartbeat, max_chars))
        self.can_row.config(text=self.elide_text(self.state.can_status, max_chars))
        self.lin_row.config(text=self.elide_text(self.state.lin_status, max_chars))
        self.uart_row.config(text=self.elide_text(self.state.uart_status, max_chars))

        self.input_from_row.config(text=self.elide_text(self.state.input_from, max_chars))
        self.input_msg_row.config(text=self.elide_text(self.state.input_message, max_chars))

        self.number_label.config(text=self.state.adc_value)
        self.draw_adc_gauge(self.get_adc_numeric())

        adc_color_map = {
            "safe": ADC_SAFE_COLOR,
            "warning": ADC_WARNING_COLOR,
            "danger": ADC_DANGER_COLOR,
            "emergency": ADC_DANGER_COLOR,
        }
        self.number_label.config(fg=adc_color_map.get(self.state.adc_state, FG))

        level_color_map = {
            "safe": ADC_SAFE_COLOR,
            "warning": ADC_WARNING_COLOR,
            "danger": ADC_DANGER_COLOR,
            "emergency": ADC_DANGER_COLOR,
        }
        level_text = self.state.adc_state.upper()
        if self.state.adc_state == "emergency":
            self.level_label.config(text=level_text, bg=(ADC_DANGER_COLOR if self.blink_on else BOX))
        else:
            self.level_label.config(text=level_text, bg=level_color_map.get(self.state.adc_state, MUTED))

        lock_is_locked = self.state.lock_state == "1"
        self.lock_label.config(
            text=("LOCK" if lock_is_locked else "UNLOCK"),
            bg=(ADC_DANGER_COLOR if lock_is_locked else ADC_SAFE_COLOR),
        )

        if self.state.mode.upper() == "EMERGENCY":
            blink_active = self.state.adc_state == "emergency" or self.state.mode.upper() == "EMERGENCY"
            if blink_active:
                self.mode_label.config(text="EMERGENCY", bg=(EM_COLOR if self.blink_on else BOX))
                if self.state.adc_state == "emergency":
                    self.number_label.config(fg=(ADC_DANGER_COLOR if self.blink_on else FG))
                self.set_border_color(EM_COLOR if self.blink_on else BORDER)
            else:
                self.mode_label.config(text="EMERGENCY", bg=EM_COLOR)
                self.set_border_color(EM_COLOR)
        else:
            self.mode_label.config(text="NORMAL", bg=NORMAL_COLOR)
            self.set_border_color(BORDER)

        button_color_map = {
            "approved": ADC_SAFE_COLOR,
            "ok": ADC_WARNING_COLOR,
            "waiting": MUTED,
            "denied": ADC_DANGER_COLOR,
        }
        self.input_msg_row.config(fg=button_color_map.get(self.state.button_status, MUTED))

        self.bottom_label.config(
            text=(
                f"MODE: {self.conn_mode_var.get()} / PORT: {self.port_var.get()} / BAUD: {self.get_baudrate()} "
                f"/ STATUS: {self.state.port_status} / ADC_STATE: {self.state.adc_state.upper()} "
                f"/ LOCK: {self.state.lock_state} / BUTTON: {self.state.button_status}"
            )
        )

        if self.running:
            self.root.after(100, self.update_gui)


class DashboardRuntimeWindowMixin:
    def on_window_resize(self, event):
        if event.widget != self.root:
            return

        scale_w = event.width / self.base_width
        scale_h = event.height / self.base_height
        scale = max(0.8, min(1.8, min(scale_w, scale_h)))

        if abs(scale - self.current_scale) < 0.03:
            return

        self.current_scale = scale
        self.apply_scaled_styles(scale)

    def apply_scaled_styles(self, scale):
        self.font_title.configure(size=max(13, int(round(17 * scale))))
        self.font_section.configure(size=max(10, int(round(13 * scale))))
        self.font_label.configure(size=max(9, int(round(12 * scale))))
        self.font_left_content.configure(size=max(8, int(round(10 * scale))))
        self.font_value.configure(size=max(9, int(round(12 * scale))))
        self.font_big.configure(size=max(20, int(round(18 * scale))))
        self.font_mode.configure(size=max(12, int(round(18 * scale))))
        self.font_mode_title.configure(size=max(14, int(round(18 * scale))))
        self.font_mode_button.configure(size=max(24, int(round(34 * scale))))
        self.font_button.configure(size=max(9, int(round(11 * scale))))
        self.font_status.configure(size=max(9, int(round(11 * scale))))

        card_padx = max(14, int(round(28 * scale)))
        section_padx = max(10, int(round(18 * scale)))
        section_top = max(8, int(round(14 * scale)))
        section_gap = max(2, int(round(4 * scale)))
        number_gap = max(10, int(round(24 * scale)))
        mode_gap = max(10, int(round(20 * scale)))
        mode_width = max(14, int(round(18 * scale)))
        badge_pady = max(8, int(round(14 * scale)))
        mode_button_pady = max(24, int(round(42 * scale)))

        self.status_card.pack_configure(padx=card_padx)
        self.number_row.pack_configure(padx=section_padx, pady=(section_top, max(6, number_gap // 3)))

        level_h_est = self.font_mode.metrics("linespace") + badge_pady * 2
        bar_h = int(round(level_h_est * 2.0))
        top_h = int(round(self.font_section.metrics("linespace") * 2.8))
        bottom_h = int(round(self.font_section.metrics("linespace") * 1.6))
        gauge_height = max(96, bar_h + top_h + bottom_h + 20)

        self.adc_gauge_canvas.config(height=gauge_height)
        self.adc_gauge_canvas.pack_configure(padx=section_padx, pady=(0, max(8, number_gap // 2)))

        self.badge_row.pack_configure(pady=(0, max(10, number_gap // 2)))
        self.level_label.config(width=mode_width, pady=badge_pady)
        self.level_label.pack_configure(padx=(0, max(8, mode_gap // 2)))
        self.lock_label.config(width=mode_width, pady=badge_pady)
        self.lock_label.pack_configure()

        self.mode_title_label.pack_configure(padx=section_padx, pady=(0, max(6, section_gap)))
        self.mode_label.config(width=mode_width, pady=mode_button_pady)
        self.mode_label.pack_configure(pady=(0, mode_gap))

    def on_close(self):
        self.running = False
        if self.file_mode_active:
            self.stop_file_fallback_mode()

        self.serial_reader.disconnect()

        try:
            self.root.quit()
            self.root.destroy()
        except Exception:
            pass

        sys.exit(0)


class DashboardRuntimeMixin(
    DashboardRuntimeLoopMixin,
    DashboardRuntimeViewMixin,
    DashboardRuntimeWindowMixin,
):
    pass
