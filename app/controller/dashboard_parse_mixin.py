"""Responsibility: Parse module (line parsing and state-apply rules)."""

from app.parser.parsers import (
    classify_adc_level,
    clean_line,
    parse_adc_payload,
    parse_button_payload,
    parse_connection_line,
    parse_input_line,
    parse_mode_payload,
    parse_section_header,
    parse_status_line,
)


class DashboardParseApplyMixin:
    def apply_mode_pattern(self, mode_value):
        """
        모드 상태 적용 | Apply parsed mode value to state
        normal, emergency 값을 state.mode에 저장합니다.\n        Updates state.mode with parsed mode from received data.
        """
        if mode_value in {"normal", "emergency"}:
            self.state.mode = mode_value.upper()

    def apply_button_pattern(self, button_value):
        """
        버튼 상태 적용 | Apply parsed button status to state
        approved, denied, ok, waiting 값을 state.button_status에 저장합니다.\n        Updates state.button_status with parsed button status.
        """
        if button_value in {"approved", "denied", "ok", "waiting"}:
            self.state.button_status = button_value

    def apply_adc_pattern(self, adc_value=None, adc_level=None, lock_value=None, update_adc_value=True):
        """
        ADC 상태 적용 | Apply parsed ADC data to state
        ADC 값, 레벨, 락 상태를 state에 저장하고, classify_adc_level로 자동 분류합니다.\n        Parses ADC numeric value, determines safety level, and updates lock state.
        """
        parsed_adc = None
        if adc_value is not None:
            try:
                parsed_adc = int(str(adc_value).strip())
                if update_adc_value:
                    self.state.adc_value = str(parsed_adc)
            except ValueError:
                pass

        level_key = (adc_level or "").strip().lower()
        if not level_key and parsed_adc is not None:
            level_key = classify_adc_level(parsed_adc)

        if level_key in {"safe", "warning", "danger", "emergency"}:
            self.state.adc_state = level_key

        if lock_value in {"0", "1"}:
            self.state.lock_state = lock_value


class DashboardParseLineMixin(DashboardParseApplyMixin):
    def parse_line(self, line, source="UART"):
        """
        한 줄 데이터 파싱 및 상태 업데이트 | Parse a single line and update dashboard state
        줄을 정제한 후 섹션 헤더 인식, 현재 섹션에 맞춰 패턴 매칭 및 apply 함수 호출합니다.\n        Extracts state info (mode, button, ADC, connection status, input) and dispatches to apply methods.
        """
        line = clean_line(line)
        if not line:
            return

        self.add_log(f"[{source}] {line}", add_to_panel=False)

        section_type, raw_title = parse_section_header(line)
        if section_type is not None:
            if section_type == "master":
                self.state.master_node = raw_title
                self.current_section = "master"
            elif section_type == "connection":
                self.current_section = "connection"
            elif section_type == "status":
                self.current_section = "status"
            elif section_type == "input":
                self.current_section = "input"
            elif section_type == "message":
                self.current_section = "message"
                self.waiting_message_line = True
            else:
                self.current_section = None
            return

        if self.waiting_message_line:
            self.waiting_message_line = False
            message_text = line.strip()
            if message_text and message_text != self.last_logged_message:
                self.last_logged_message = message_text
                self.add_log(message_text, add_to_terminal=False)

        if self.current_section == "connection":
            key, value = parse_connection_line(line)
            if key and value is not None:
                setattr(self.state, key, value)

        elif self.current_section == "status":
            status_key, payload = parse_status_line(line)
            if status_key == "mode":
                parsed_mode = parse_mode_payload(payload)
                if parsed_mode:
                    self.apply_mode_pattern(parsed_mode)
            elif status_key == "button":
                parsed_button = parse_button_payload(payload)
                if parsed_button:
                    self.apply_button_pattern(parsed_button)
            elif status_key == "adc":
                adc_data = parse_adc_payload(payload)
                self.apply_adc_pattern(
                    adc_value=adc_data["adc_value"],
                    adc_level=adc_data["adc_level"],
                    lock_value=adc_data["lock_value"],
                    update_adc_value=True,
                )

        elif self.current_section == "input":
            input_from, input_message = parse_input_line(line)
            if input_from is not None:
                self.state.input_from = input_from
                self.state.input_message = input_message


class DashboardParseMixin(DashboardParseLineMixin):
    pass
