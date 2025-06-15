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
    return any(
        danger in stmt.lower() for danger in [
            "os.system", "exec", "subprocess", "shutdown", "selfdestruct", "grant_root",
            "open(", "delete", "remove", "pickle", "eval", "marshal", "write", "chmod"
        ]
    )

def _is_randomness(stmt):
    return any(
        rng in stmt.lower() for rng in [
            "random.random", "random.randint", "random.choice",
            "secrets.randbelow", "np.random", "quantum_rng", "qrng"
        ]
    )

def _is_antidebug(stmt):
    return any(antid in stmt.lower() for antid in [
        "time.sleep", "signal.pause", "inspect.", "sys.settrace", "ptrace", "anti_debug", "traceback"
    ])

def detect_patterns(logic_blocks):
    """
    Accepts a list of logic blocks:
    Each block: {"condition": "...", "body": [stmts], "calls": [funcs]}
    Returns: list of detected quantum/adversarial patterns (Python only).
    """
    patterns = set()
    for block in logic_blocks:
        cond = block.get("condition", "").lower()
        body = [b.lower() for b in block.get("body", [])]
        calls = block.get("calls", [])
        body_all = " ".join(body)

        # PROBABILISTIC BOMB (random in condition + dangerous in body)
        if _is_randomness(cond) and any(_is_dangerous_call(stmt) for stmt in body):
            patterns.add(LogicPattern.PROBABILISTIC_BOMB)

        # ENTANGLED BOMB (multiple random/dangerous or chained)
        if (
            sum(_is_randomness(stmt) for stmt in [cond] + body) >= 2 and
            sum(_is_dangerous_call(stmt) for stmt in body) >= 2
        ):
            patterns.add(LogicPattern.ENTANGLED_BOMB)

        # CHAINED/DEEP BOMB (danger in cross-function call)
        for call in calls:
            if "danger" in call or "backdoor" in call or "root" in call or "admin" in call:
                patterns.add(LogicPattern.CHAINED_QUANTUM_BOMB)
                break

        # QUANTUM STEGANOGRAPHY (encode/decode, xor, hide + randomness)
        if (
            re.search(r'encode|decode|stego|bitwise|xor|hide|obfuscate', body_all)
            and _is_randomness(cond)
        ):
            patterns.add(LogicPattern.QUANTUM_STEGANOGRAPHY)

        # QUANTUM ANTI-DEBUGGING
        if _is_antidebug(body_all) and _is_randomness(cond):
            patterns.add(LogicPattern.QUANTUM_ANTIDEBUG)

        # CROSS-FUNCTIONAL BOMB (random/danger across helpers)
        if (
            len(calls) > 0
            and any(_is_randomness(cond) or _is_randomness(call) for call in calls)
        ):
            patterns.add(LogicPattern.CROSS_FUNCTION_QUANTUM_BOMB)

    if not patterns:
        patterns.add(LogicPattern.UNKNOWN)
    return list(patterns)

# --- Example brutal quantum logic input for testing ---
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
        }
    ]
    print("BRUTAL Quantum Patterns Detected:", detect_patterns(logic_blocks))
