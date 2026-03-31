import re

from app.core.config import ADC_DANGER_MAX, ADC_SAFE_MAX, ADC_WARNING_MAX


def classify_adc_level(adc_number):
    if adc_number <= ADC_SAFE_MAX:
        return "safe"
    if adc_number <= ADC_WARNING_MAX:
        return "warning"
    if adc_number <= ADC_DANGER_MAX:
        return "danger"
    return "emergency"


def parse_mode_payload(payload):
    mode_match = re.search(r"(normal|emergency)", payload, re.IGNORECASE)
    if mode_match:
        return mode_match.group(1).strip().lower()
    return None


def parse_button_payload(payload):
    button_match = re.search(r"(approved|denied|ok|waiting)", payload, re.IGNORECASE)
    if button_match:
        return button_match.group(1).strip().lower()
    return None


def parse_adc_payload(payload):
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
    line = re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", line)
    for token in ["←[2K", "[2K", "^[", "\x1b", "\r"]:
        line = line.replace(token, "")
    return line.strip()


def parse_section_header(line):
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
    lower = line.lower()
    if lower.startswith("mode"):
        return "mode", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("button"):
        return "button", line.split(":", 1)[1].strip() if ":" in line else line
    if lower.startswith("adc"):
        return "adc", line.split(":", 1)[1].strip() if ":" in line else line
    return None, None


def parse_input_line(line):
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
