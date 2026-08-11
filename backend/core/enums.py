# backend/core/enums.py
from enum import Enum


class Importance(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class ToolName(str, Enum):
    SEND_MAIL = "send_mail"