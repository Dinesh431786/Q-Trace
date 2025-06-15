import re

class LogicPattern:
    PROBABILISTIC_BOMB = "PROBABILISTIC_BOMB"
    ENTANGLED_BOMB = "ENTANGLED_BOMB"
    UNKNOWN = "UNKNOWN"
    # Add other quantum-native patterns as needed

def detect_patterns(expr_list, language="generic"):
    """
    Only detects true quantum-native patterns.
    - PROBABILISTIC_BOMB: Dangerous action triggered by randomness.
    - ENTANGLED_BOMB: Multiple, entangled/random conditions (future expansion).
    All other patterns are reported, but NOT passed to quantum_engine.
    """
    patterns = set()
    for expr in expr_list:
        text = expr.lower()

        # --- Quantum-native: Probabilistic Bomb ---
        # e.g. "if random.random() < 0.2: dangerous_fn()"
        if (
            re.search(r'random\.random|random\.randint|random\.choice|secrets\.randbelow', text)
            and any(danger in text for danger in ['os.system', 'exec', 'shutdown', 'grant_root', 'selfdestruct', 'remove', 'delete'])
        ):
            patterns.add(LogicPattern.PROBABILISTIC_BOMB)

        # --- Quantum-native: Entangled Bomb (future, placeholder, for real research use) ---
        # e.g. two random/dangerous conditions joined by AND/OR (for quantum entanglement modeling)
        if (
            re.search(r'random\.', text) and
            re.search(r'and|or', text) and
            any(danger in text for danger in ['os.system', 'exec', 'shutdown', 'grant_root', 'selfdestruct'])
        ):
            patterns.add(LogicPattern.ENTANGLED_BOMB)

    if not patterns:
        patterns.add(LogicPattern.UNKNOWN)
    return list(patterns)

# --- Demo ---
if __name__ == "__main__":
    exprs = [
        "if random.random() < 0.15: os.system('shutdown -h now')",
        "if random.randint(1,10) == 7 and os.system('echo pwned')",
        "if (a ^ b ^ c) == 42",  # Will NOT be quantum-flagged
        "if time.time() > 1700000000: print('Hello')",
    ]
    for lang in ["python", "c"]:
        print(f"\n--- Language: {lang} ---")
        print("Patterns detected:", detect_patterns(exprs, language=lang))
