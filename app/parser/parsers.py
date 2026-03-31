import re

from app.core.config import ADC_DANGER_MAX, ADC_SAFE_MAX, ADC_WARNING_MAX


def classify_adc_level(adc_number):
    """
    ADC 값 범위 분류 | Classify ADC numeric value into safety level
    ADC 수치를 임계값과 비교하여 safe/warning/danger/emergency 중 하나를 반환합니다.\n    Maps ADC values to 4 safety levels based on configured thresholds.
    """
    if adc_number <= ADC_SAFE_MAX:
        return "safe"
    if adc_number <= ADC_WARNING_MAX:
        return "warning"
    if adc_number <= ADC_DANGER_MAX:
        return "danger"
    return "emergency"


def parse_mode_payload(payload):
    """
    모드 페이로드 추출 | Extract mode status from payload string
    페이로드 문자열에서 normal 또는 emergency를 정규식으로 찾아 반환합니다.\n    Returns matched mode string or None if no valid mode found.
    """
    mode_match = re.search(r"(normal|emergency)", payload, re.IGNORECASE)
    if mode_match:
        return mode_match.group(1).strip().lower()
    return None


def parse_button_payload(payload):
    """
    버튼 페이로드 추출 | Extract button status from payload string
    페이로드 문자열에서 approved/denied/ok/waiting 중 하나를 정규식으로 찾아 반환합니다.\n    Returns matched button status or None if no valid status found.
    """
    button_match = re.search(r"(approved|denied|ok|waiting)", payload, re.IGNORECASE)
    if button_match:
        return button_match.group(1).strip().lower()
    return None


def parse_adc_payload(payload):
    """
    ADC 페이로드 전체 파싱 | Parse ADC payload to extract value, level, and lock bit
    페이로드에서 ADC 값(숫자), 레벨(safe/warning/danger/emergency), 락 상태(0/1)를 추출합니다.\n    Returns dict with 'adc_value', 'adc_level', 'lock_value' keys (each can be None).
    """
    adc_match = re.search(r"\badc\s*[:=]\s*(-?\d+)", payload, re.IGNORECASE)
    if adc_match is None:
        adc_match = re.search(r"^\s*(-?\d+)", payload)

    level_match = re.search(r"(safe|warning|danger|emergency)", payload, re.IGNORECASE)
    lock_match = re.search(r"lock\s*=\s*([01])", payload, re.IGNORECASE)

    adc_value = adc_match.group(1) if adc_match else None
    adc_level = level_match.group(1).strip().lower() if level_match else None
    lock_value = lock_match.group(1) if lock_match else None

    return {
        "adc_value": adc_value,
        "adc_level": adc_level,
        "lock_value": lock_value,
    }


def clean_line(line):
    """
    라인 정재 | Clean line by removing ANSI escape codes and control characters
    ANSI 컬러 코드, 이동 제어 문자, 캐리지 리턴 등을 제거하고 공백을 정리합니다.\n    Removes terminal control sequences and returns clean text for further parsing.
    """
    line = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", line)
    for token in ["←[2K", "[2K", "^[", "\x1b", "\r"]:
        line = line.replace(token, "")
    return line.strip()


def parse_section_header(line):
    """
    섹션 헤더 인식 | Recognize section headers like [master node] or [status]
    [...]로 둘러싸인 문자열을 찾아 섹션 타입(master/connection/status/input/message)을 반환합니다.\n    Returns (section_type_str, raw_title_str) or (None, None) if not a header.
    """
    section_match = re.match(r"^\[(.+)\]$", line)
    if not section_match:
        return None, None

    raw_title = section_match.group(1).strip()
    sec = raw_title.lower()

    if "master node" in sec:
        return "master", raw_title
    if "connetion status" in sec or "connection status" in sec:
        return "connection", raw_title
    if sec == "status":
        return "status", raw_title
    if sec == "input":
        return "input", raw_title
    if sec == "message":
        return "message", raw_title
    return "unknown", raw_title


def parse_connection_line(line):
    """
    연결 섹션 라인 파싱 | Parse lines within [connection status] section
    heartbeat/can/lin/uart: 값 형식의 라인을 파싱하여 상태 키와 값을 추출합니다.\n        Returns (attribute_key, value_str) or (None, None) if not a connection line.
    """
    lower = line.lower()
    if lower.startswith("heartbeat"):
        return "heartbeat", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("can"):
        return "can_status", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("lin"):
        return "lin_status", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("uart"):
        return "uart_status", line.split(":", 1)[1].strip() if ":" in line else line
    return None, None


def parse_status_line(line):
    """
    상태 섹션 라인 파싱 | Parse lines within [status] section
    mode/button/adc: 값 형식의 라인을 파싱하여 상태 종류와 페이로드를 분리합니다.\n        Returns (status_type, payload_str) or (None, None) if not a status line.
    """
    lower = line.lower()
    if lower.startswith("mode"):
        return "mode", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("button"):
        return "button", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("adc"):
        return "adc", line.split(":", 1)[1].strip() if ":" in line else line
    return None, None


def parse_input_line(line):
    """
    입력 섹션 라인 파싱 | Parse lines within [input] section
    from [SOURCE] \"MESSAGE\" 형식의 라인을 파싱하여 입력 출처와 메시지를 추출합니다.\n        Returns (source_str, message_str) or (None, None) if format doesn't match.
    """
    m = re.match(r"from\s+\[(.+?)\]\s+\"(.*)\"", line, re.IGNORECASE)
    if not m:
        return None, None
    return m.group(1), m.group(2)

__all__ = [
    "classify_adc_level",
    "parse_mode_payload",
    "parse_button_payload",
    "parse_adc_payload",
    "clean_line",
    "parse_section_header",
    "parse_connection_line",
    "parse_status_line",
    "parse_input_line",
]
