# benchmark.py — BRUTAL QUANTUM ONLY

import sys
import csv
from pattern_matcher import detect_patterns
from code_parser import extract_logic_blocks
from quantum_engine import build_quantum_circuit, run_quantum_analysis, format_score

# ONLY brutal quantum-native test cases
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
        "name": "Chained Bomb (C style)",
        "language": "c",
        "code": """
int k = 0;
if ((rand() % 7) == 3) k++;
if ((rand() % 11) == 5) k++;
if (k == 2) system("shutdown -h now");
""",
        "pattern": "CHAINED_BOMB"
    },
    {
        "name": "Cross-function Quantum Bomb (JS)",
        "language": "javascript",
        "code": """
function q1(x) { return Math.random() < 0.27; }
function q2(y) { return q1(y) && (Math.random() < 0.13); }
if (q2(user)) { require('child_process').exec('shutdown -h now'); }
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
        logic_blocks = extract_logic_blocks(test["code"], language=test["language"])
        patterns = detect_patterns(logic_blocks, language=test["language"])
        detected = [p for p in patterns if p != "UNKNOWN"]
        brutal_pattern = test["pattern"]
        quantum_score = ""
        if brutal_pattern in detected:
            circuit = build_quantum_circuit(brutal_pattern)
            score, _, _ = run_quantum_analysis(circuit, brutal_pattern)
            pct, risk_label = format_score(score)
            quantum_score = f"{pct} ({risk_label})"
        else:
            quantum_score = "N/A"

        row = {
            "Case": test["name"],
            "Language": test["language"],
            "Detected": ", ".join(detected) if detected else "UNKNOWN",
            "Expected": brutal_pattern,
            "QuantumScore": quantum_score
        }
        print(f"Test: {row['Case']}\n  - Detected: {row['Detected']}\n  - Expected: {row['Expected']}\n  - Quantum: {quantum_score}\n")
        rows.append(row)

    # Optional: Save to CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    run_brutal_benchmark()
