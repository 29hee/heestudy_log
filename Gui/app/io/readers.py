import os
import threading
import time

import serial


class SerialReader:
    def __init__(self, on_line, on_error):
        """
        시리얼 리더 초기화 | Initialize SerialReader with callbacks
        시리얼 포트에서 데이터를 읽을 때마다 호출할 콜백 함수들을 등록합니다.\n        Stores callback functions that will be invoked when data arrives or errors occur.
        """
        self.on_line = on_line
        self.on_error = on_error
        self.ser = None
        self.thread = None
        self.running = False

    @property
    def is_open(self):
        """
        시리얼 포트 개방 상태 확인 | Check if serial port is currently open
        시리얼 포트의 개방 여부를 boolean으로 반환합니다. \n        Returns True if serial connection is active and open.
        """
        return self.ser is not None and self.ser.is_open

    @property
    def port(self):
        """
        현재 연결 포트명 반환 | Get the currently connected port name
        현재 개방된 시리얼 포트의 포트명을 반환합니다 (COM5 등). 미개방 시 None.\n        Returns port name (e.g., 'COM5') or None if not connected.
        """
        if not self.is_open:
            return None
        return self.ser.port

    def connect(self, port, baud):
        """
        시리얼 포트 연결 | Connect to serial port at specified baud rate
        시리얼 포트를 열고 읽기 스레드를 백그라운드에서 시작합니다 (daemon 스레드).\n        Opens serial connection and spawns background read thread.
        """
        self.disconnect()
        self.ser = serial.Serial(port, baud, timeout=1)
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def disconnect(self):
        """
        시리얼 포트 연결 해제 | Disconnect from serial port
        읽기 스레드를 정지하고 시리얼 포트를 닫습니다 (안전한 정리).\n        Stops the read thread and safely closes the serial port.
        """
        self.running = False
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
        except Exception:
            pass
        finally:
            self.ser = None

    def _read_loop(self):
        """
        백그라운드 읽기 스레드 | Background thread loop that reads from serial port
        지속적으로 시리얼 포트에서 데이터를 읽어 on_line 콜백을 호출합니다 (줄 단위).\n        Continuously reads lines from serial and invokes on_line callback; stops on error or disconnect.
        """
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
        """
        파일 리더 초기화 | Initialize FileReader with callbacks
        테스트용 파일 기반 입력을 위한 콜백 함수들을 등록합니다 (lines/status/error).\n        Stores callback functions for receiving file data, status updates, and errors.
        """
        self.on_lines = on_lines
        self.on_status = on_status
        self.on_error = on_error
        self.running = False
        self.thread = None
        self.file_path = None
        self.poll_interval = 0.3
        self.last_snapshot = None

    def start(self, file_path, poll_interval):
        """
        파일 리딩 시작 | Start polling a file for test data
        지정된 파일을 poll_interval 간격으로 주기적으로 감시하고 변화가 있으면 on_lines 콜백을 호출합니다.\n        Spawns background thread that polls file at regular intervals and calls on_lines when content changes.
        """
        self.stop()
        self.file_path = file_path
        self.poll_interval = poll_interval
        self.last_snapshot = None
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        """
        파일 리딩 중지 | Stop polling the file
        running 플래그를 비활성화하여 폴링 스레드를 정지합니다.\n        Sets running=False to signal the background thread to stop.
        """
        self.running = False

    def _loop(self):
        """
        백그라운드 폴링 스레드 | Background thread loop that polls file periodically
        파일을 주기적으로 읽어 이전 내용과 비교하고, 변화가 있으면 on_lines 콜백을 호출합니다.\n        Continuously polls file at poll_interval; when content changes, calls on_lines with updated lines.
        """
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
