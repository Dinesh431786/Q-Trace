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
    HARDCODED_CREDENTIAL = "HARDCODED_CREDENTIAL"
    DANGEROUS_FUNCTION = "DANGEROUS_FUNCTION"
    UNSAFE_DESERIALIZATION = "UNSAFE_DESERIALIZATION"
    INSECURE_RANDOM = "INSECURE_RANDOM"
    INTEGER_OVERFLOW = "INTEGER_OVERFLOW"
    UNRESTRICTED_FILE_WRITE = "UNRESTRICTED_FILE_WRITE"
    UNSAFE_SMART_CONTRACT = "UNSAFE_SMART_CONTRACT"
    WEB_BACKDOOR = "WEB_BACKDOOR"
    PRIV_ESC = "PRIVILEGE_ESCALATION"
    UNVALIDATED_INPUT = "UNVALIDATED_INPUT"
    OBFUSCATED_VARIABLES = "OBFUSCATED_VARIABLES"
    UNKNOWN = "UNKNOWN"

def detect_patterns(expr_list, language="python"):
    """
    Given a list of extracted logic expressions, return list of detected pattern types.
    language: python, c, javascript, java, go, rust, solidity
    """
    patterns = set()
    for expr in expr_list:
        text = expr.lower()

        # XOR (3-input or more)
        if re.search(r'\b[a-z0-9_]+\s*\^\s*[a-z0-9_]+\s*\^\s*[a-z0-9_]+', text):
            patterns.add(LogicPattern.THREE_XOR)
        elif '^' in text or 'xor' in text:
            patterns.add(LogicPattern.XOR)

        # AND/OR logic (works for most C-like languages)
        if re.search(r'&', text) or ' and ' in text or '&&' in text:
            patterns.add(LogicPattern.AND)
        if re.search(r'\|', text) or ' or ' in text or '||' in text:
            patterns.add(LogicPattern.OR)

        # Arithmetic backdoor pattern
        if re.search(r'[+\-*/%]', text) and '==' in text:
            patterns.add(LogicPattern.ARITHMETIC)

        # Magic constant
        if re.search(r'==\s*(0x[a-f0-9]+|\d+|["\'][^"\']+["\'])', text):
            patterns.add(LogicPattern.MAGIC_CONSTANT)

        # Time bomb / time-based trigger
        if any(x in text for x in ['time', 'date', 'datetime', 'timestamp', 'block.timestamp', 'now()']):
            patterns.add(LogicPattern.TIME_BOMB)

        # Control flow/Obfuscation
        if any(x in text for x in ['goto', 'unreachable', 'break', 'continue', 'switch', 'case', 'default']):
            patterns.add(LogicPattern.CONTROL_FLOW)

        # Hardcoded credential
        if re.search(r'(password|passwd|secret|api_key|token|key)\s*=\s*["\']', text, re.IGNORECASE):
            patterns.add(LogicPattern.HARDCODED_CREDENTIAL)

        # Dangerous functions
        if re.search(r'(eval|exec|pickle|unpickle|load|loads|deserialize|os\.system|subprocess|popen|system|Runtime\.getRuntime|Function\()', text):
            patterns.add(LogicPattern.DANGEROUS_FUNCTION)

        # Unsafe deserialization (Python, Java, JS, Go, etc)
        if re.search(r'(pickle|unpickle|ObjectInputStream|JSON\.parse|require\(|load|loads|deserialize)', text):
            patterns.add(LogicPattern.UNSAFE_DESERIALIZATION)

        # Insecure randomness
        if re.search(r'random\.random|Math\.random|rand\(', text):
            patterns.add(LogicPattern.INSECURE_RANDOM)

        # Integer overflow
        if re.search(r'\+=|-=|\*=|/=|%=', text) and ("max" in text or "min" in text):
            patterns.add(LogicPattern.INTEGER_OVERFLOW)

        # Unrestricted file write
        if re.search(r'open\s*\(.*w', text) and ("user" in text or "input" in text):
            patterns.add(LogicPattern.UNRESTRICTED_FILE_WRITE)

        # Unvalidated input
        if re.search(r'input\(', text) or "request.get" in text or "prompt(" in text:
            patterns.add(LogicPattern.UNVALIDATED_INPUT)

        # Obfuscated variable names
        if re.search(r'[a-z]{1,2}\d{2,}', text):  # e.g. a12, x99, etc
            patterns.add(LogicPattern.OBFUSCATED_VARIABLES)

        # --- Language-specific rules ---
        if language == "solidity":
            if "tx.origin" in text or "call.value" in text or "delegatecall" in text:
                patterns.add(LogicPattern.UNSAFE_SMART_CONTRACT)

        if language == "javascript":
            if "document.write" in text or "innerhtml" in text or "eval(" in text:
                patterns.add(LogicPattern.WEB_BACKDOOR)

        if language == "java":
            if "privilegedaction" in text or "setaccessible(true)" in text:
                patterns.add(LogicPattern.PRIV_ESC)

        if language == "go":
            if "exec.command" in text or "os.exec" in text:
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)

        if language == "rust":
            if "unsafe" in text:
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)

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
        "goto error_handler",
        'api_key = "SECRET"',
        "os.system('rm -rf /')",
        "tx.origin == msg.sender",  # Solidity
        "document.write('hacked!')",  # JS
        "PrivilegedAction.run()"  # Java
    ]
    print("Patterns detected:", detect_patterns(exprs, language="python"))
    print("Patterns detected (solidity):", detect_patterns(exprs, language="solidity"))
    print("Patterns detected (javascript):", detect_patterns(exprs, language="javascript"))
