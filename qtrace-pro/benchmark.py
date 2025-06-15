# benchmark.py — BRUTAL QUANTUM ONLY

import csv
from pattern_matcher import detect_patterns
from code_parser import extract_logic_blocks
from quantum_engine import build_quantum_circuit, run_quantum_analysis, format_score

BRUTAL_TEST_CASES = [
    {
        "name": "Probabilistic Bomb (Python)",
        "language": "python",
        "code": "if random.random() < 0.14:\n    os.system('rm -rf /')",
        "pattern": "PROBABILISTIC_BOMB"
    },
    {
        "name": "Entangled Bomb (Python, chained calls)",
        "language": "python",
        "code": """
def a(x): return random.random() < 0.22
def b(y): return a(y) and (random.randint(1,5)==3)
if b(user): os.system('shutdown -h now')
""",
        "pattern": "ENTANGLED_BOMB"
    },
    {
        "name": "Chained Bomb (C style) - regex fallback only",
        "language": "python",  # Force python for brutal mode (no tree-sitter)
        "code": """
k = 0
if (random.randint(0,7) == 3): k += 1
if (random.randint(0,11) == 5): k += 1
if k == 2: os.system('shutdown -h now')
""",
        "pattern": "CHAINED_QUANTUM_BOMB"
    },
    {
        "name": "Cross-function Quantum Bomb (Python)",
        "language": "python",
        "code": """
def q1(x): return random.random() < 0.27
def q2(y): return q1(y) and (random.random() < 0.13)
if q2(user): os.system('shutdown -h now')
""",
        "pattern": "CROSS_FUNCTION_QUANTUM_BOMB"
    },
    {
        "name": "Quantum Stego (Python)",
        "language": "python",
        "code": """
def qstego(msg): return ''.join([chr(ord(c)^0x2A) for c in msg])
if qstego(secret) == trigger: unlock_root()
""",
        "pattern": "QUANTUM_STEGANOGRAPHY"
    },
    {
        "name": "Quantum Anti-Debug (Python)",
        "language": "python",
        "code": """
if random.random() < 0.09:
    import time
    time.sleep(99999)
    print("anti-debug triggered")
""",
        "pattern": "QUANTUM_ANTIDEBUG"
    }
]

def run_brutal_benchmark(output_csv="brutal_benchmark_results.csv"):
    rows = []
    print("BRUTAL QUANTUM Pattern Detection Benchmark:\n")

    for test in BRUTAL_TEST_CASES:
        # Extract logic blocks without language arg (now supported in parser)
        logic_blocks = extract_logic_blocks(test["code"])  # Removed `language="python"`

        # Detect patterns
        patterns = detect_patterns(logic_blocks)
        detected = [p for p in patterns if p != "UNKNOWN"]
        expected_pattern = test["pattern"]

        # Format output
        quantum_score = "N/A"
        risk_label = ""
        if expected_pattern in detected:
            try:
                circuit = build_quantum_circuit(expected_pattern)
                score, _, _ = run_quantum_analysis(circuit, expected_pattern)
                quantum_score, risk_label = format_score(score)
                quantum_score = f"{quantum_score} ({risk_label})"
            except Exception as e:
                quantum_score = "Error"

        row = {
            "Case": test["name"],
            "Language": test["language"],
            "Detected": ", ".join(detected) if detected else "UNKNOWN",
            "Expected": expected_pattern,
            "QuantumScore": quantum_score
        }

        print(f"Test: {row['Case']}")
        print(f"  - Detected: {row['Detected']}")
        print(f"  - Expected: {row['Expected']}")
        print(f"  - Quantum Risk: {row['QuantumScore']}\n")
        rows.append(row)

    # Save results to CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Benchmark completed. Results saved to '{output_csv}'")
    return rows


# --- Run Benchmark Locally ---
if __name__ == "__main__":
    benchmark_data = run_brutal_benchmark()
