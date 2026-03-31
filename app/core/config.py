from dataclasses import dataclass

# Runtime defaults
DEFAULT_BAUDRATE = 115200
DEFAULT_PORT = "COM5"
DEFAULT_FALLBACK_FILE = "test.txt"
FALLBACK_POLL_SEC = 0.3
STRICT_REAL_PORT_ONLY = True

# ADC ranges
ADC_MIN = 0
ADC_MAX = 4095
ADC_SAFE_MAX = 1364
ADC_WARNING_MAX = 2729
ADC_DANGER_MAX = 3412

# Theme colors
BG = "#222222"
PANEL = "#2b2b2b"
BOX = "#1f1f1f"
FG = "white"
MUTED = "#cfcfcf"
BORDER = "#cfcfcf"

NORMAL_COLOR = "#1f7a1f"
EM_COLOR = "#a61d24"

ADC_SAFE_COLOR = "#3aa657"
ADC_WARNING_COLOR = "#b08900"
ADC_DANGER_COLOR = "#a61d24"


@dataclass
class DashboardState:
    master_node: str = "MASTER NODE"
    heartbeat: str = "Waiting..."
    can_status: str = "Waiting..."
    lin_status: str = "Waiting..."
    uart_status: str = "Waiting..."

    mode: str = "NORMAL"
    button_status: str = "waiting"

    adc_state: str = "safe"
    adc_value: str = "2000"
    lock_state: str = "0"

    input_from: str = "normal"
    input_can_message: str = "waiting..."
    input_lin_message: str = "0 (safe, lock=0)"

    port_status: str = "Disconnected"

__all__ = [
    "DEFAULT_BAUDRATE",
    "DEFAULT_PORT",
    "DEFAULT_FALLBACK_FILE",
    "FALLBACK_POLL_SEC",
    "STRICT_REAL_PORT_ONLY",
    "ADC_MIN",
    "ADC_MAX",
    "ADC_SAFE_MAX",
    "ADC_WARNING_MAX",
    "ADC_DANGER_MAX",
    "BG",
    "PANEL",
    "BOX",
    "FG",
    "MUTED",
    "BORDER",
    "NORMAL_COLOR",
    "EM_COLOR",
    "ADC_SAFE_COLOR",
    "ADC_WARNING_COLOR",
    "ADC_DANGER_COLOR",
    "DashboardState",
]
