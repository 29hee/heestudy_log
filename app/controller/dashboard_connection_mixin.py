"""Responsibility: Connection module (port discovery, connect/disconnect flow, IO callbacks)."""

from tkinter import messagebox

import serial
import serial.tools.list_ports

from app.core.config import DEFAULT_PORT, STRICT_REAL_PORT_ONLY


class DashboardConnectionPortsMixin:
    def refresh_ports(self, select_default=False):
        prev_port = self.port_var.get().strip() if hasattr(self, "port_var") else ""
        raw_ports = list(serial.tools.list_ports.comports())

        if STRICT_REAL_PORT_ONLY:
            raw_ports = [p for p in raw_ports if self.is_real_serial_port(p)]

        raw_ports = [p for p in raw_ports if self.is_port_currently_available(p.device)]
        self.port_map = {p.device: p for p in raw_ports}

        ports = [p.device for p in raw_ports]
        if not ports:
            ports = ["No Ports"]

        menu = self.port_menu["menu"]
        menu.delete(0, "end")

        for port in ports:
            menu.add_command(label=port, command=lambda v=port: self.port_var.set(v))

        if select_default and DEFAULT_PORT in ports:
            self.port_var.set(DEFAULT_PORT)
        elif prev_port in ports:
            self.port_var.set(prev_port)
        else:
            self.port_var.set(ports[0])

        self.add_log(f"[INFO] ports: {', '.join(ports)}")

    def is_real_serial_port(self, port_info):
        desc = (port_info.description or "").lower()
        hwid = (port_info.hwid or "").lower()

        if getattr(port_info, "vid", None) is not None:
            return True
        if "usb" in desc or "usb" in hwid:
            return True
        if "uart" in desc or "cp210" in desc or "ch340" in desc or "ftdi" in desc:
            return True

        if "bluetooth" in desc or "bth" in hwid:
            return False

        return False

    def is_port_currently_available(self, port_name):
        if self.serial_reader.is_open and self.serial_reader.port == port_name:
            return True

        try:
            probe = serial.Serial(port_name, self.get_baudrate(), timeout=0)
            probe.close()
            return True
        except Exception as e:
            if self.is_missing_port_error(e):
                return False
            return True

    def is_missing_port_error(self, err):
        msg = str(err).lower()
        if isinstance(err, FileNotFoundError):
            return True
        if "filenotfounderror" in msg:
            return True
        if "지정된 파일을 찾을 수 없습니다" in msg:
            return True
        if "could not open port" in msg and ("file" in msg or "2" in msg):
            return True
        return False


class DashboardConnectionFlowMixin:
    def connect_serial(self):
        selected_mode = self.conn_mode_var.get().strip().lower()
        selected_port = self.port_var.get().strip()
        baud = self.get_baudrate()

        if selected_mode == "file":
            if self.serial_reader.is_open:
                self.disconnect_serial()
            self.start_file_fallback_mode()
            return

        if selected_port == "No Ports":
            messagebox.showwarning("Warning", "연결 가능한 포트가 없음\nMode를 File로 바꿔서 테스트 모드를 사용하세요.")
            return

        if STRICT_REAL_PORT_ONLY:
            info = self.port_map.get(selected_port)
            if info is not None and not self.is_real_serial_port(info):
                messagebox.showwarning(
                    "Warning",
                    f"가상 포트로 보이는 {selected_port}는 차단됨\nMode를 File로 테스트하거나 실제 USB UART를 연결하세요.",
                )
                self.add_log(f"[WARN] blocked virtual port: {selected_port} ({info.description})")
                return

        if self.file_mode_active:
            self.stop_file_fallback_mode()

        if self.serial_reader.is_open:
            self.add_log("[INFO] already connected")
            return

        try:
            self.serial_reader.connect(selected_port, baud)
            self.state.port_status = f"Connected ({selected_port}, {baud})"
            self.add_log(f"[INFO] connected: {selected_port}, {baud}")
        except Exception as e:
            self.state.port_status = f"Connection failed: {e}"
            self.add_log(f"[ERROR] {e}")
            if self.is_missing_port_error(e):
                self.refresh_ports(select_default=False)

    def disconnect_serial(self):
        if self.file_mode_active:
            self.stop_file_fallback_mode()

        try:
            if self.serial_reader.is_open:
                port_name = self.serial_reader.port
                self.serial_reader.disconnect()
                self.add_log(f"[INFO] disconnected: {port_name}")
        except Exception as e:
            self.add_log(f"[ERROR] disconnect failed: {e}")
        finally:
            self.state.port_status = "Disconnected"

    def start_file_fallback_mode(self):
        if self.file_mode_active:
            self.add_log("[INFO] file test mode already active")
            return

        self.file_mode_active = True
        self.state.port_status = f"Test mode (file: {self.fallback_file_path})"
        self.add_log(f"[INFO] started file test mode: {self.fallback_file_path}")
        self.file_reader.start(self.fallback_file_path, self.fallback_poll_interval)

    def stop_file_fallback_mode(self):
        self.file_mode_active = False
        self.file_reader.stop()
        self.add_log("[INFO] file test mode stopped")

    def _on_serial_line(self, line):
        self.parse_line(line, source="UART")

    def _on_serial_error(self, e):
        self.add_log(f"[ERROR] read error: {e}")
        self.state.port_status = f"Read error: {e}"
        if self.is_missing_port_error(e):
            self.refresh_ports(select_default=False)
            self.serial_reader.disconnect()

    def _on_file_lines(self, lines):
        self.current_section = None
        for raw in lines:
            self.parse_line(raw.strip(), source="FILE")

    def _on_file_status(self, status_text):
        self.state.port_status = status_text

    def _on_file_error(self, e):
        self.add_log(f"[ERROR] file test mode error: {e}")
        self.state.port_status = f"Test mode error: {e}"


class DashboardConnectionMixin(DashboardConnectionPortsMixin, DashboardConnectionFlowMixin):
    pass
