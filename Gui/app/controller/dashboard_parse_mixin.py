"""Responsibility: Parse module (line parsing and state-apply rules)."""

from app.parser.parsers import (
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
        ADC 값, 레벨, 락 상태를 state에 저장합니다. 레벨은 직접 파싱된 값만 사용합니다.\n        Stores ADC value, level, and lock state using directly parsed level only.
        """
        if adc_value is not None:
            try:
                parsed_adc = int(str(adc_value).strip())
                if update_adc_value:
                    self.state.adc_value = str(parsed_adc)
            except ValueError:
                pass

        # If lock is asserted, freeze status level regardless of incoming adc_level.
        if lock_value == "1":
            self.state.lock_state = "1"
            return

        # If currently locked and unlock signal is not explicitly provided, keep level unchanged.
        if self.state.lock_state == "1" and lock_value is None:
            return

        level_key = (adc_level or "").strip().lower()
        if level_key in {"safe", "warning", "danger", "emergency"}:
            self.state.adc_state = level_key

        if lock_value in {"0", "1"}:
            self.state.lock_state = lock_value


class DashboardParseLineMixin(DashboardParseApplyMixin):
    def apply_input_pattern(self, input_from, input_message):
        src = str(input_from).strip().lower()
        self.state.input_from = input_from

        if "can" in src:
            self.state.input_can_message = input_message
            self.set_flow_step("can_release", f"CAN input: {input_message}")
        elif "lin" in src:
            self.state.input_lin_message = input_message
            self.set_flow_step("adc_to_master", f"LIN input: {input_message}")
        elif "mode" in src:
            mode = parse_mode_payload(str(input_message))
            if mode:
                self.apply_mode_pattern(mode)
        else:
            # Unknown source: keep both messages visible for debug readability.
            self.state.input_can_message = input_message
            self.state.input_lin_message = input_message

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
                if key == "lin_status" and value:
                    self.set_flow_step("adc_to_master", f"LIN status: {value}")
                elif key == "can_status" and value:
                    self.set_flow_step("master_to_can", f"CAN status: {value}")
                elif key == "uart_status" and value:
                    self.set_flow_step("uart_to_gui", f"UART status: {value}")

        elif self.current_section == "status":
            status_key, payload = parse_status_line(line)
            if status_key == "mode":
                parsed_mode = parse_mode_payload(payload)
                if parsed_mode:
                    self.apply_mode_pattern(parsed_mode)
                    if parsed_mode == "emergency":
                        self.set_flow_step("master_to_can", "Emergency detected, notifying CAN node")
                    elif parsed_mode == "normal":
                        self.set_flow_step("master_unlock", "Emergency cleared, returning to normal")
            elif status_key == "can_msg":
                self.apply_input_pattern("can", payload)
                parsed_button = parse_button_payload(payload)
                if parsed_button:
                    self.apply_button_pattern(parsed_button)
            elif status_key == "lin_msg":
                self.apply_input_pattern("lin", payload)
                adc_data = parse_adc_payload(payload)
                if adc_data["adc_value"] is not None or adc_data["lock_value"] in {"0", "1"}:
                    prev_lock = self.state.lock_state
                    self.apply_adc_pattern(
                        adc_value=adc_data["adc_value"],
                        adc_level=adc_data["adc_level"],
                        lock_value=adc_data["lock_value"],
                        update_adc_value=True,
                    )
                    if adc_data["lock_value"] == "1":
                        self.set_flow_step("master_decision", "Threshold exceeded, LOCK maintained")
                    elif prev_lock == "1" and self.state.lock_state == "0":
                        self.set_flow_step("master_unlock", "Unlock sent from Master to Slave1 (LIN)")
            elif status_key == "button":
                parsed_button = parse_button_payload(payload)
                if parsed_button:
                    self.apply_button_pattern(parsed_button)
                    if parsed_button in {"approved", "ok"}:
                        self.set_flow_step("can_release", "Release button accepted on CAN node")
            elif status_key == "adc":
                adc_data = parse_adc_payload(payload)
                prev_lock = self.state.lock_state
                self.apply_adc_pattern(
                    adc_value=adc_data["adc_value"],
                    adc_level=adc_data["adc_level"],
                    lock_value=adc_data["lock_value"],
                    update_adc_value=True,
                )
                adc_text = adc_data["adc_value"] if adc_data["adc_value"] is not None else self.state.adc_value
                lock_text = adc_data["lock_value"] if adc_data["lock_value"] is not None else self.state.lock_state
                self.set_flow_step("adc_to_master", f"Slave1 -> Master | ADC={adc_text}, lock={lock_text}")

                if adc_data["lock_value"] == "1":
                    self.set_flow_step("master_decision", "Threshold exceeded, LOCK maintained")
                elif prev_lock == "1" and self.state.lock_state == "0":
                    self.set_flow_step("master_unlock", "Unlock sent from Master to Slave1 (LIN)")
            else:
                # Some firmware variants print input-like lines under [Status] instead of [Input].
                input_from, input_message = parse_input_line(line)
                if input_from is not None:
                    self.apply_input_pattern(input_from, input_message)

        elif self.current_section == "input":
            input_from, input_message = parse_input_line(line)
            if input_from is not None:
                self.apply_input_pattern(input_from, input_message)


class DashboardParseMixin(DashboardParseLineMixin):
    pass
