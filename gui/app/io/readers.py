import os
import threading
import time

import serial


class SerialReader:
    def __init__(self, on_line, on_error):
        self.on_line = on_line
        self.on_error = on_error
        self.ser = None
        self.thread = None
        self.running = False

    @property
    def is_open(self):
        return self.ser is not None and self.ser.is_open

    @property
    def port(self):
        if not self.is_open:
            return None
        return self.ser.port

    def connect(self, port, baud):
        self.disconnect()
        self.ser = serial.Serial(port, baud, timeout=1)
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def disconnect(self):
        self.running = False
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass
        finally:
            self.ser = None

    def _read_loop(self):
        while self.running and self.ser is not None and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode(errors="ignore").strip()
                    if line:
                        self.on_line(line)
                else:
                    time.sleep(0.02)
            except Exception as e:
                self.on_error(e)
                break
        self.running = False


class FileReader:
    def __init__(self, on_lines, on_status, on_error):
        self.on_lines = on_lines
        self.on_status = on_status
        self.on_error = on_error
        self.running = False
        self.thread = None
        self.file_path = None
        self.poll_interval = 0.3
        self.last_snapshot = None

    def start(self, file_path, poll_interval):
        self.stop()
        self.file_path = file_path
        self.poll_interval = poll_interval
        self.last_snapshot = None
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        missing_logged = False

        while self.running:
            try:
                if not os.path.exists(self.file_path):
                    if not missing_logged:
                        self.on_status(f"Test mode waiting for file: {self.file_path}")
                        missing_logged = True
                    time.sleep(self.poll_interval)
                    continue

                with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if self.last_snapshot != content:
                    self.last_snapshot = content
                    missing_logged = False

                    lines = content.splitlines()
                    if not lines:
                        self.on_status(f"Test mode file empty: {self.file_path}")
                    else:
                        self.on_lines(lines)
                        self.on_status(f"Test mode active ({len(lines)} lines, updated)")

                time.sleep(self.poll_interval)
            except Exception as e:
                self.on_error(e)
                time.sleep(self.poll_interval)
