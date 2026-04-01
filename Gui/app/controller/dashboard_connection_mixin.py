"""Responsibility: Connection module (port discovery, connect/disconnect flow, IO callbacks)."""

from tkinter import messagebox

import serial
import serial.tools.list_ports

from app.core.config import DEFAULT_PORT, STRICT_REAL_PORT_ONLY


class DashboardConnectionPortsMixin:
    def refresh_ports(self, select_default=False):
        """
        시리얼 포트 목록 갱신 | Refresh the list of available serial ports
        Scans available ports, filters by config, and updates the dropdown menu (caches port info in port_map).
        """
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
        """
        실제 하드웨어 시리얼 포트 식별 | Determine if a port is a real hardware serial port
        Checks port description/hwid against patterns (USB, UART, CH340, etc.) to exclude virtual ports.
        """
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
        """
        포트가 현재 연결 가능한지 확인 | Check if a port is currently available for connection
        이미 연결된 포트면 True 반환(다른 프로그램이 이미 사용 중).\n        Tests if port can be opened immediately; avoids port conflicts and FileNotFoundError checks.
        """
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
        """
        포트 미처리 오류 식별 | Identify if error is due to missing/absent port
        FileNotFoundError 등으로 포트가 문제로 식별하여 refresh_ports 같을 미래 갱신 수 있다는 나타냄
        Used to determine if port list should be refreshed after connection errors.
        """
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
        """
        시리얼 연결 또는 테스트 모드 실시 | Connect to serial port or start file test mode
        """
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
        """
        시리얼 연결 끌기 | Disconnect from serial port
        Closes serial connection, stops file fallback mode if active, and updates port_status.
        """
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
        """
        테스트 모드(파일 모드) 실시 | Start test mode reading from a file
        지정된 파일을 poll하면서 라인 데이터를 시뮬레이션합니다.
        Initiates FileReader to read and parse lines from a test file at regular intervals.
        """
        if self.file_mode_active:
            self.add_log("[INFO] file test mode already active")
            return

        self.file_mode_active = True
        self.state.port_status = f"Test mode (file: {self.fallback_file_path})"
        self.add_log(f"[INFO] started file test mode: {self.fallback_file_path}")
        self.file_reader.start(self.fallback_file_path, self.fallback_poll_interval)

    def stop_file_fallback_mode(self):
        """
        테스트 모드 멈추기 | Stop test mode
        Stops FileReader and clears file_mode_active flag.
        """
        self.file_mode_active = False
        self.file_reader.stop()
        self.add_log("[INFO] file test mode stopped")

    def _on_serial_line(self, line):
        """
        시리얼 데이터 줄 수정 및 파싱 내내 | Callback when a line is received from serial port
        Routes received serial data to the parse_line() method for state extraction.
        """
        self.parse_line(line, source="UART")

    def _on_serial_error(self, e):
        """
        시리얼 낮따 메제 처리 | Handle serial read errors
        Logs errors, updates status, and refreshes ports if it's a missing port error.
        """
        self.add_log(f"[ERROR] read error: {e}")
        self.state.port_status = f"Read error: {e}"
        if self.is_missing_port_error(e):
            self.refresh_ports(select_default=False)
            self.serial_reader.disconnect()

    def _on_file_lines(self, lines):
        """
        테스트 파일에서 라인 데이트 맛끔 | Callback when file test data is read
        Parses all lines from file, separates them by section headers to avoid multi-section buffering.
        """
        self.current_section = None
        for raw in lines:
            self.parse_line(raw.strip(), source="FILE")

    def _on_file_status(self, status_text):
        """
        테스트 모드 상태 갱신 | Callback to update test mode status text
        Updates the displayed port status message (e.g., 'waiting for file', 'updated').
        """
        self.state.port_status = status_text

    def _on_file_error(self, e):
        """
        테스트 모드 오류 처리 | Handle file test mode errors
        Logs file mode errors and updates the status display.
        """
        self.add_log(f"[ERROR] file test mode error: {e}")
        self.state.port_status = f"Test mode error: {e}"


class DashboardConnectionMixin(DashboardConnectionPortsMixin, DashboardConnectionFlowMixin):
    pass
