# pattern_matcher.py

from enum import Enum, auto
import re

class LogicPattern(Enum):
    XOR = auto()
    AND = auto()
    OR = auto()
    TIME_BOMB = auto()
    CONTROL_FLOW = auto()
    UNKNOWN = auto()

def detect_patterns(code_text: str):
    """
    Detects which logic patterns are present in the given code snippet.
    Returns a set of LogicPattern enums.
    """
    code_lower = code_text.lower()
    patterns = set()

    # XOR logic (bitwise or word 'xor')
    if re.search(r"\b(xor)\b", code_lower) or "^" in code_text:
        patterns.add(LogicPattern.XOR)

    # AND logic (bitwise, logical, word 'and')
    if re.search(r"&&|\band\b|&", code_lower):
        patterns.add(LogicPattern.AND)

    # OR logic (bitwise, logical, word 'or')
    if re.search(r"\|\||\bor\b|\|", code_lower):
        patterns.add(LogicPattern.OR)

    # Time bomb (date/time related logic)
    if re.search(r"\b(time|date|year|month|hour|minute|second)\b", code_lower):
        patterns.add(LogicPattern.TIME_BOMB)

    # Obfuscated or suspicious control flow
    if re.search(r"\bgoto\b|\bunreachable\b|label\s*:", code_lower):
        patterns.add(LogicPattern.CONTROL_FLOW)

    if not patterns:
        patterns.add(LogicPattern.UNKNOWN)
    return patterns
