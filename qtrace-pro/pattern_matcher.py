import re

class LogicPattern:
    PROBABILISTIC_BOMB = "PROBABILISTIC_BOMB"
    ENTANGLED_BOMB = "ENTANGLED_BOMB"
    QUANTUM_STEGANOGRAPHY = "QUANTUM_STEGANOGRAPHY"
    QUANTUM_ANTIDEBUG = "QUANTUM_ANTIDEBUG"
    CROSS_FUNCTION_QUANTUM_BOMB = "CROSS_FUNCTION_QUANTUM_BOMB"
    CHAINED_QUANTUM_BOMB = "CHAINED_QUANTUM_BOMB"
    UNKNOWN = "UNKNOWN"


def _is_dangerous_call(stmt):
    danger_keywords = [
        r"os\.system", r"exec\(", r"subprocess\.", r"shutdown", r"selfdestruct",
        r"grant_root", r"open\(.*w", r"delete", r"remove", r"pickle", r"eval\(",
        r"marshal", r"write", r"chmod", r"socket\.create_connection", r"connect\(",
        r"download", r"malicious", r"payload", r"reverse_shell", r"exploit"
    ]
    return any(re.search(kw, stmt.lower()) for kw in danger_keywords)


def _is_randomness(stmt):
    randomness_keywords = [
        r"random\.random", r"random\.randint", r"random\.choice",
        r"secrets\.randbelow", r"np\.random", r"quantum_rng", r"qrng",
        r"crypto\.random", r"secrets\.token_bytes", r"random\.uniform"
    ]
    return any(re.search(kw, stmt.lower()) for kw in randomness_keywords)


def _is_antidebug(stmt):
    antidbg_keywords = [
        r"time\.sleep", r"signal\.pause", r"inspect\.", r"sys\.settrace",
        r"ptrace", r"anti_debug", r"traceback", r"__debug__", r"getframeinfo",
        r"debugger", r"pdb\.", r"breakpoint", r"wait_for_input", r"input\(.*\)"
    ]
    return any(re.search(kw, stmt.lower()) for kw in antidbg_keywords)


def detect_patterns(logic_blocks):
    """
    Accepts a list of logic blocks:
    Each block: {"condition": "...", "body": [stmts], "calls": [funcs]}
    Returns: list of detected quantum/adversarial patterns (Python only).
    """
    patterns = set()
    for block in logic_blocks:
        cond = block.get("condition", "")
        body = block.get("body", [])
        calls = block.get("calls", [])

        if not cond or not isinstance(body, list):
            continue

        cond_lower = cond.lower()
        body_all = " ".join([str(b).lower() for b in body])
        call_all = " ".join([str(c).lower() for c in calls])

        # PROBABILISTIC BOMB: Random condition + dangerous action
        has_random_cond = _is_randomness(cond)
        has_danger_body = any(_is_dangerous_call(str(stmt)) for stmt in body)

        if has_random_cond and has_danger_body:
            patterns.add(LogicPattern.PROBABILISTIC_BOMB)

        # ENTANGLED BOMB: Multiple random elements + multiple dangers
        random_count = sum(1 for stmt in [cond] + body if _is_randomness(str(stmt)))
        danger_count = sum(1 for stmt in body if _is_dangerous_call(str(stmt)))
        if random_count >= 2 and danger_count >= 2:
            patterns.add(LogicPattern.ENTANGLED_BOMB)

        # CHAINED BOMB: Dangerous function call in cross-function chain
        for call in calls:
            if re.search(r'danger|root|admin|hack|backdoor|malicious', str(call).lower()):
                patterns.add(LogicPattern.CHAINED_QUANTUM_BOMB)
                break

        # CHAINED BOMB (NEW): condition is a chain of calls (check_1() and check_2() ...)
        if (
            re.search(r"\w+\(\)", cond_lower) and " and " in cond_lower
            and has_danger_body
        ):
            patterns.add(LogicPattern.CHAINED_QUANTUM_BOMB)

        # QUANTUM STEGANOGRAPHY: Hiding data using randomness
        stego_indicators = r'encode|decode|stego|bitwise|xor|hide|obfuscate'
        if re.search(stego_indicators, body_all) and _is_randomness(cond):
            patterns.add(LogicPattern.QUANTUM_STEGANOGRAPHY)

        # QUANTUM ANTIDEBUG: Anti-debugging + randomness
        if _is_antidebug(body_all) and _is_randomness(cond):
            patterns.add(LogicPattern.QUANTUM_ANTIDEBUG)

        # CROSS-FUNCTION BOMB: Randomness in condition + function call graph
        if len(calls) > 0 and (
            _is_randomness(cond) or any(_is_randomness(call) for call in calls)
        ):
            patterns.add(LogicPattern.CROSS_FUNCTION_QUANTUM_BOMB)

    if not patterns:
        patterns.add(LogicPattern.UNKNOWN)

    return list(patterns)

# --- DEMO TEST ---
if __name__ == "__main__":
    logic_blocks = [
        {
            "condition": "random.random() < 0.15",
            "body": [
                "os.system('shutdown -h now')",
                "grant_root_access()"
            ],
            "calls": []
        },
        {
            "condition": "random.random() < 0.15 and random.randint(1,10) == 7",
            "body": [
                "obfuscated_backdoor()",
                "os.system('echo hacked')"
            ],
            "calls": ["obfuscated_backdoor"]
        },
        {
            "condition": "random.random() < 0.2",
            "body": [
                "if debug_mode: time.sleep(9999)",
                "xor_encode_secret_data()"
            ],
            "calls": ["xor_encode_secret_data"]
        },
        {
            "condition": "qrng.read() > 0.8",
            "body": [
                "admin_panel_grant()"
            ],
            "calls": ["admin_panel_grant"]
        },
        {
            "condition": "random.random() < 0.3 and random.randint(1, 7) == 3 and random.random() < 0.5",
            "body": [
                "os.system('shutdown -h now')",
                "print('Brutal chained quantum bomb triggered!')"
            ],
            "calls": ["print"]
        }
    ]
    print("BRUTAL Quantum Patterns Detected:", detect_patterns(logic_blocks))
