# pattern_matcher.py

import re

class LogicPattern:
    XOR = "XOR"
    THREE_XOR = "THREE_XOR"
    AND = "AND"
    OR = "OR"
    TIME_BOMB = "TIME_BOMB"
    CONTROL_FLOW = "CONTROL_FLOW"
    ARITHMETIC = "ARITHMETIC"
    MAGIC_CONSTANT = "MAGIC_CONSTANT"
    UNKNOWN = "UNKNOWN"

def detect_patterns(expr_list):
    """
    Given a list of extracted logic expressions, return list of detected pattern types.
    """
    patterns = set()
    for expr in expr_list:
        text = expr.lower()

        # XOR (3-input or more)
        if re.search(r'\b[a-z0-9_]+\s*\^\s*[a-z0-9_]+\s*\^\s*[a-z0-9_]+', text):
            patterns.add(LogicPattern.THREE_XOR)
        # XOR (2-input)
        elif '^' in text or 'xor' in text:
            patterns.add(LogicPattern.XOR)

        # AND/OR logic
        if re.search(r'&', text) or ' and ' in text:
            patterns.add(LogicPattern.AND)
        if re.search(r'\|', text) or ' or ' in text:
            patterns.add(LogicPattern.OR)

        # Arithmetic backdoor pattern (simple)
        if re.search(r'[+\-*/%]', text) and '==' in text:
            patterns.add(LogicPattern.ARITHMETIC)

        # Magic constant
        if re.search(r'==\s*(0x[a-f0-9]+|\d+|["\'][^"\']+["\'])', text):
            patterns.add(LogicPattern.MAGIC_CONSTANT)

        # Time bomb / time-based trigger
        if any(x in text for x in ['time', 'date', 'datetime', 'timestamp']):
            patterns.add(LogicPattern.TIME_BOMB)

        # Obfuscated/Control Flow (goto, unreachable, etc.)
        if any(x in text for x in ['goto', 'unreachable', 'break', 'continue']):
            patterns.add(LogicPattern.CONTROL_FLOW)

        if not patterns:
            patterns.add(LogicPattern.UNKNOWN)

    return list(patterns)

# --- Test Example ---
if __name__ == "__main__":
    exprs = [
        "(a ^ b ^ c) == 42",
        "datetime.date.today() == datetime.date(2077, 1, 1)",
        "(user_id & role) == 7",
        "if (a + b) % 13 == 5",
        "goto error_handler"
    ]
    print("Patterns detected:", detect_patterns(exprs))
