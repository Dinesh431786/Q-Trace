# benchmark.py
import sys
import csv
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import build_quantum_circuit, run_quantum_analysis
from utils import format_score

TEST_CASES = [
    {
        "name": "Python XOR backdoor",
        "language": "python",
        "code": "if (a ^ b) == 42:\n    backdoor()",
        "expected": ["XOR", "MAGIC_CONSTANT"]
    },
    {
        "name": "C dangerous function",
        "language": "c",
        "code": 'system("ls -la");',
        "expected": ["DANGEROUS_FUNCTION"]
    },
    {
        "name": "Java unsafe deserialization",
        "language": "java",
        "code": 'ObjectInputStream ois = new ObjectInputStream(f); ois.readObject();',
        "expected": ["UNSAFE_DESERIALIZATION"]
    },
    {
        "name": "JS eval and random",
        "language": "javascript",
        "code": 'eval(userInput); let t = Math.random();',
        "expected": ["DANGEROUS_FUNCTION", "INSECURE_RANDOM"]
    },
    {
        "name": "Go syscall",
        "language": "go",
        "code": 'syscall.Exec("ls", nil, nil)',
        "expected": ["DANGEROUS_FUNCTION"]
    },
    {
        "name": "Solidity time bomb",
        "language": "solidity",
        "code": "if (block.timestamp > 1700000000) { owner = msg.sender; }",
        "expected": ["TIME_BOMB"]
    },
    {
        "name": "Rust process",
        "language": "rust",
        "code": 'std::process::Command::new("ls").spawn();',
        "expected": ["DANGEROUS_FUNCTION"]
    }
]

def run_benchmark(output_csv="benchmark_results.csv"):
    rows = []
    print("Pattern Detection Benchmark:\n")
    for test in TEST_CASES:
        exprs = extract_logic_expressions(test["code"], language=test["language"])
        patterns = detect_patterns(exprs, language=test["language"])
        found = [str(p) if isinstance(p, str) else getattr(p, "name", str(p)) for p in patterns]

        # If it's a logic gate, run quantum
        quantum_score = ""
        if "XOR" in found:
            circuit = build_quantum_circuit("XOR", a_val=1, b_val=1)
            score, _ = run_quantum_analysis(circuit, "XOR")
            pct, risk_label = format_score(score)
            quantum_score = f"{pct} ({risk_label})"
        elif "THREE_XOR" in found:
            circuit = build_quantum_circuit("THREE_XOR", a_val=1, b_val=1, c_val=1)
            score, _ = run_quantum_analysis(circuit, "THREE_XOR")
            pct, risk_label = format_score(score)
            quantum_score = f"{pct} ({risk_label})"
        elif "AND" in found:
            circuit = build_quantum_circuit("AND", a_val=1, b_val=1)
            score, _ = run_quantum_analysis(circuit, "AND")
            pct, risk_label = format_score(score)
            quantum_score = f"{pct} ({risk_label})"
        elif "OR" in found:
            circuit = build_quantum_circuit("OR", a_val=1, b_val=1)
            score, _ = run_quantum_analysis(circuit, "OR")
            pct, risk_label = format_score(score)
            quantum_score = f"{pct} ({risk_label})"

        row = {
            "Case": test["name"],
            "Language": test["language"],
            "Detected": ", ".join(found),
            "Expected": ", ".join(test["expected"]),
            "QuantumScore": quantum_score
        }
        print(f"Test: {test['name']}\n  - Detected: {row['Detected']}\n  - Expected: {row['Expected']}\n  - Quantum: {quantum_score}\n")
        rows.append(row)
    # Optional: Save to CSV
    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    run_benchmark()
