# pattern_matcher.py

import re
from enum import Enum, auto

class LogicPattern(Enum):
    XOR = auto()
    AND = auto()
    OR = auto()
    THREE_XOR = auto()
    TIME_BOMB = auto()
    CONTROL_FLOW = auto()
    UNKNOWN = auto()

def detect_patterns(code):
    patterns = []

    # 3-input XOR pattern (Python/C/JS style): (a ^ b ^ c)
    if re.search(r"\w+\s*\^\s*\w+\s*\^\s*\w+", code):
        patterns.append(LogicPattern.THREE_XOR)

    # 2-input XOR
    elif re.search(r"\w+\s*\^\s*\w+", code):
        patterns.append(LogicPattern.XOR)

    # AND pattern
    if re.search(r"\w+\s*&\s*\w+", code):
        patterns.append(LogicPattern.AND)

    # OR pattern
    if re.search(r"\w+\s*\|\s*\w+", code):
        patterns.append(LogicPattern.OR)

    # Time Bomb
    if re.search(r"(date|time|datetime)", code, re.IGNORECASE):
        patterns.append(LogicPattern.TIME_BOMB)

    # Obfuscated control flow
    if re.search(r"goto|flag\s*=", code, re.IGNORECASE):
        patterns.append(LogicPattern.CONTROL_FLOW)

    if not patterns:
        patterns.append(LogicPattern.UNKNOWN)

    return patterns
