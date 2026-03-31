import tkinter as tk

from app.core.config import ADC_DANGER_MAX, ADC_MAX, ADC_SAFE_MAX, ADC_WARNING_MAX, BOX, FG


class AdcGaugeWidget(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            height=92,
            bg=BOX,
            highlightthickness=0,
            bd=0,
            relief="flat",
            **kwargs,
        )

    @staticmethod
    def blend_hex_color(c1, c2, t):
        t = max(0.0, min(1.0, t))
        r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
        r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw(self, adc_numeric, level_label, font_section, font_mode):
        self.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()
        if width < 40 or height < 30:
            return

        left = 8
        right = width - 8

        tick_font_size = max(10, int(round(font_section.metrics("linespace") * 0.75)))
        tick_font = ("Consolas", tick_font_size, "bold")

        level_label_h = level_label.winfo_height()
        if level_label_h <= 1:
            level_label_h = font_mode.metrics("linespace") + 8

        bar_height = max(24, int(round(level_label_h * 2.0)))

        top_label_area = int(round(tick_font_size * 3.6))
        bottom_label_area = int(round(tick_font_size * 1.6))
        top = 6 + top_label_area
        max_bar_height = max(20, height - top - bottom_label_area - 8)
        bar_height = min(bar_height, max_bar_height)
        bottom = top + bar_height

        steps = 24
        for i in range(steps):
            t0 = i / steps
            t1 = (i + 1) / steps
            x0 = left + (right - left) * t0
            x1 = left + (right - left) * t1

            tm = (t0 + t1) * 0.5
            if tm <= 0.5:
                color = self.blend_hex_color("#008000", "#ffff00", tm / 0.5)
            else:
                color = self.blend_hex_color("#ffff00", "#ff0000", (tm - 0.5) / 0.5)

            self.create_rectangle(x0, top, x1, bottom, outline=color, fill=color)

        safe_ratio = ADC_SAFE_MAX / max(1, ADC_MAX)
        warning_ratio = ADC_WARNING_MAX / max(1, ADC_MAX)
        danger_ratio = ADC_DANGER_MAX / max(1, ADC_MAX)

        safe_pct = int(round(safe_ratio * 100))
        warning_pct = int(round(warning_ratio * 100))
        danger_pct = int(round(danger_ratio * 100))

        top_ticks = [
            (safe_ratio, f"{safe_pct}%~\nWarning"),
            (warning_ratio, f"{warning_pct}%~\nDanger"),
            (danger_ratio, f"{danger_pct}%~\nEmergency"),
        ]
        for t, label in top_ticks:
            tx = left + (right - left) * t
            anchor = "se" if t >= 0.9 else "s"
            self.create_line(tx, top - 6, tx, bottom + 6, fill="#111111", width=2)
            self.create_text(
                tx,
                top - 10,
                text=label,
                fill=FG,
                anchor=anchor,
                justify="center",
                font=tick_font,
            )

        full_x = right
        full_label_y = min(height, bottom + tick_font_size)
        safe_label_y = min(height - 2, bottom + tick_font_size)
        self.create_text(full_x, full_label_y, text="FULL", fill=FG, anchor="ne", font=tick_font)
        self.create_text(left, safe_label_y, text="SAFE", fill=FG, anchor="nw", font=tick_font)

        ratio = adc_numeric / max(1, ADC_MAX)
        x = left + (right - left) * ratio
        cy = (top + bottom) * 0.5
        marker_size = max(6, int(round(bar_height * 0.35)))
        self.create_oval(
            x - marker_size,
            cy - marker_size,
            x + marker_size,
            cy + marker_size,
            outline="#ffff00",
            width=3,
            fill="",
        )
        self.create_oval(x - 3, cy - 3, x + 3, cy + 3, outline="#111111", fill="#ffff00", width=1)
