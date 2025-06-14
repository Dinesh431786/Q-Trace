# pattern_matcher.py

import re

class LogicPattern:
    XOR = "XOR"
    THREE_XOR = "THREE_XOR"
    AND = "AND"
    OR = "OR"
    ARITHMETIC = "ARITHMETIC"
    MAGIC_CONSTANT = "MAGIC_CONSTANT"
    TIME_BOMB = "TIME_BOMB"
    CONTROL_FLOW = "CONTROL_FLOW"
    DANGEROUS_FUNCTION = "DANGEROUS_FUNCTION"
    HARDCODED_CREDENTIAL = "HARDCODED_CREDENTIAL"
    UNSAFE_DESERIALIZATION = "UNSAFE_DESERIALIZATION"
    OBFUSCATED_VARIABLES = "OBFUSCATED_VARIABLES"
    INSECURE_RANDOM = "INSECURE_RANDOM"
    INTEGER_OVERFLOW = "INTEGER_OVERFLOW"
    UNRESTRICTED_FILE_WRITE = "UNRESTRICTED_FILE_WRITE"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    WEB_BACKDOOR = "WEB_BACKDOOR"
    UNKNOWN = "UNKNOWN"

def detect_patterns(expr_list, language="generic"):
    """
    Given a list of extracted logic expressions, return list of detected pattern types.
    Optionally use language for language-specific heuristics.
    """
    patterns = set()
    for expr in expr_list:
        text = expr.lower()
        # --- Cross-language patterns ---
        if re.search(r'\b[a-z0-9_]+\s*\^\s*[a-z0-9_]+\s*\^\s*[a-z0-9_]+', text):
            patterns.add(LogicPattern.THREE_XOR)
        elif '^' in text or 'xor' in text:
            patterns.add(LogicPattern.XOR)
        if re.search(r'&', text) or ' and ' in text:
            patterns.add(LogicPattern.AND)
        if re.search(r'\|', text) or ' or ' in text:
            patterns.add(LogicPattern.OR)
        if re.search(r'[+\-*/%]', text) and '==' in text:
            patterns.add(LogicPattern.ARITHMETIC)
        if re.search(r'==\s*(0x[a-f0-9]+|\d+|["\'][^"\']+["\'])', text):
            patterns.add(LogicPattern.MAGIC_CONSTANT)
        if any(x in text for x in ['time', 'date', 'datetime', 'timestamp']):
            patterns.add(LogicPattern.TIME_BOMB)
        if any(x in text for x in ['goto', 'unreachable', 'break', 'continue']):
            patterns.add(LogicPattern.CONTROL_FLOW)

        # --- Language & risk-specific enterprise patterns ---
        # Dangerous function calls
        if language in ["python", "generic"]:
            if re.search(r'os\.system|subprocess\.popen|eval\(', text):
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)
            if re.search(r'pickle\.load|eval\(|marshal\.loads', text):
                patterns.add(LogicPattern.UNSAFE_DESERIALIZATION)
            if re.search(r'(["\'])[A-Za-z0-9]{8,}(["\'])', text) and "key" in text:
                patterns.add(LogicPattern.HARDCODED_CREDENTIAL)
            if re.search(r'random\.random|random\.randint|random\.choice', text):
                patterns.add(LogicPattern.INSECURE_RANDOM)
        if language == "java":
            if "processbuilder" in text or "runtime.getruntime().exec" in text:
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)
            if "objectinputstream" in text and "readobject" in text:
                patterns.add(LogicPattern.UNSAFE_DESERIALIZATION)
            if re.search(r'string\s+[a-z]\s*=', expr, re.IGNORECASE):
                patterns.add(LogicPattern.OBFUSCATED_VARIABLES)
            if re.search(r'new\s+random\(', text):
                patterns.add(LogicPattern.INSECURE_RANDOM)
            if re.search(r'\bapi[_\-]?key\b', text) or re.search(r'private\s+static\s+final\s+string\s+\w+\s*=', text):
                patterns.add(LogicPattern.HARDCODED_CREDENTIAL)
            if "filewriter" in text:
                patterns.add(LogicPattern.UNRESTRICTED_FILE_WRITE)
            if "parseint" in text and "*" in text:
                patterns.add(LogicPattern.INTEGER_OVERFLOW)
            if re.search(r'userinput\.equals\(["\']admin["\']\)', text):
                patterns.add(LogicPattern.PRIVILEGE_ESCALATION)
        if language == "javascript":
            if re.search(r'eval\(|child_process\.exec|document\.cookie', text):
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)
            if re.search(r'crypto\.randombytes|math\.random', text):
                patterns.add(LogicPattern.INSECURE_RANDOM)
            if re.search(r'process\.env\.[a-z_]+', text):
                patterns.add(LogicPattern.HARDCODED_CREDENTIAL)
            if re.search(r'fs\.writefile', text):
                patterns.add(LogicPattern.UNRESTRICTED_FILE_WRITE)
        if language == "solidity":
            if re.search(r'(tx\.origin|block\.timestamp)', text):
                patterns.add(LogicPattern.TIME_BOMB)
            if re.search(r'private\s+[a-z0-9_]+\s*=', text):
                patterns.add(LogicPattern.HARDCODED_CREDENTIAL)
        if language in ["c", "cpp"]:
            if re.search(r'system\(', text) or re.search(r'popen\(', text):
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)
            if re.search(r'gets\(', text) or re.search(r'scanf\(', text):
                patterns.add(LogicPattern.UNSAFE_DESERIALIZATION)
        # Go/Rust (basic)
        if language == "go":
            if re.search(r'os\.exec|syscall', text):
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)
        if language == "rust":
            if re.search(r'std::process::command', text):
                patterns.add(LogicPattern.DANGEROUS_FUNCTION)

        # Web backdoor / suspicious route
        if re.search(r'debug|admin|root|backdoor', text) and ('if' in text or 'route' in text):
            patterns.add(LogicPattern.WEB_BACKDOOR)
        
        # Generic obfuscation (single char vars)
        if re.search(r'\b[a-z]\s*=', expr, re.IGNORECASE) and len(expr) < 60:
            patterns.add(LogicPattern.OBFUSCATED_VARIABLES)
        
    if not patterns:
        patterns.add(LogicPattern.UNKNOWN)
    return list(patterns)

# --- Test Example ---
if __name__ == "__main__":
    # Test all main patterns on a multi-language set of expressions
    exprs = [
        "(a ^ b ^ c) == 42",
        "datetime.date.today() == datetime.date(2077, 1, 1)",
        "(user_id & role) == 7",
        "if (a + b) % 13 == 5",
        "goto error_handler",
        'os.system("ls")',
        'ProcessBuilder("bash", "-c", "rm -rf /")',
        'private static final String API_KEY = "XYZ12345";',
        'ObjectInputStream ois = new ObjectInputStream(f); ois.readObject();',
        'eval(userInput)',
        'random.randint(0,100)',
        'FileWriter("/tmp/output.txt")',
        'if(userInput.equals("admin")){ ... }',
        'route("/debug")',
        'tx.origin'
    ]
    for lang in ["python", "c", "java", "javascript", "solidity"]:
        print(f"\n--- Language: {lang} ---")
        print("Patterns detected:", detect_patterns(exprs, language=lang))
