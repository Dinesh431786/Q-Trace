"""
quantum_engine.py — Brutal Quantum Innovator Edition
Complete brutal quantum simulation with full CHAINED_QUANTUM_BOMB support.
"""
import cirq
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

def build_quantum_circuit(pattern, **kwargs):
    if pattern == "PROBABILISTIC_BOMB":
        return probabilistic_bomb_circuit(kwargs.get("prob", 0.2))
    elif pattern == "ENTANGLED_BOMB":
        return entangled_bomb_circuit(kwargs.get("probs", [0.2, 0.5]))
    elif pattern == "CHAINED_QUANTUM_BOMB":
        return chained_quantum_bomb_circuit(kwargs.get("chain_length", 3), kwargs.get("prob", 0.3))
    elif pattern == "QUANTUM_STEGANOGRAPHY":
        return stego_circuit(kwargs.get("encode_val", 1))
    elif pattern == "QUANTUM_ANTIDEBUG":
        return antidebug_circuit(kwargs.get("prob", 0.1))
    elif pattern == "CROSS_FUNCTION_QUANTUM_BOMB":
        return cross_func_bomb_circuit(kwargs.get("func_probs", [0.3, 0.5, 0.8]))
    else:
        return None

def probabilistic_bomb_circuit(prob=0.2):
    qubit = cirq.LineQubit(0)
    theta = 2 * np.arcsin(np.sqrt(prob))
    circuit = cirq.Circuit()
    circuit.append(cirq.ry(theta)(qubit))
    circuit.append(cirq.measure(qubit, key='result'))
    return circuit

def entangled_bomb_circuit(probs=[0.2, 0.5]):
    q0, q1 = cirq.LineQubit.range(2)
    theta0 = 2 * np.arcsin(np.sqrt(probs[0]))
    theta1 = 2 * np.arcsin(np.sqrt(probs[1]))
    circuit = cirq.Circuit()
    circuit.append(cirq.ry(theta0)(q0))
    circuit.append(cirq.ry(theta1)(q1))
    circuit.append(cirq.CNOT(q0, q1))
    circuit.append(cirq.measure(q0, key='result0'))
    circuit.append(cirq.measure(q1, key='result1'))
    return circuit

def chained_quantum_bomb_circuit(chain_length=3, prob=0.3):
    """
    Brutal quantum chain bomb:  
    - Prepare chain_length qubits.  
    - Each rotated Ry with given prob.  
    - Link qubits with CNOT in a chain (entanglement).  
    - Measure all qubits.  
    - Risk = probability all measured bits are 1 (all triggers).  
    """
    qubits = cirq.LineQubit.range(chain_length)
    theta = 2 * np.arcsin(np.sqrt(prob))
    circuit = cirq.Circuit()
    for q in qubits:
        circuit.append(cirq.ry(theta)(q))
    for i in range(chain_length - 1):
        circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
    for i, q in enumerate(qubits):
        circuit.append(cirq.measure(q, key=f'result{i}'))
    return circuit

def stego_circuit(encode_val=1):
    q = cirq.LineQubit(0)
    circuit = cirq.Circuit()
    if encode_val:
        circuit.append(cirq.X(q))
    circuit.append(cirq.H(q))
    circuit.append(cirq.measure(q, key='stego'))
    return circuit

def antidebug_circuit(prob=0.1):
    q = cirq.LineQubit(0)
    theta = 2 * np.arcsin(np.sqrt(prob))
    circuit = cirq.Circuit()
    circuit.append(cirq.ry(theta)(q))
    circuit.append(cirq.measure(q, key='anti'))
    return circuit

def cross_func_bomb_circuit(func_probs=[0.3, 0.5, 0.8]):
    n = len(func_probs)
    qubits = cirq.LineQubit.range(n)
    circuit = cirq.Circuit()
    for i, q in enumerate(qubits):
        theta = 2 * np.arcsin(np.sqrt(func_probs[i]))
        circuit.append(cirq.ry(theta)(q))
    for i in range(n - 1):
        circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
    for i, q in enumerate(qubits):
        circuit.append(cirq.measure(q, key=f'f{i}'))
    return circuit

def run_quantum_analysis(circuit, pattern="PROBABILISTIC_BOMB", shots=1024):
    if circuit is None:
        return 0.0, {}, {}
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=shots)
    measurements = result.measurements

    # For multi-qubit patterns (CHAINED, ENTANGLED, CROSS_FUNCTION)
    multi_qubit_patterns = ["CHAINED_QUANTUM_BOMB", "ENTANGLED_BOMB", "CROSS_FUNCTION_QUANTUM_BOMB"]
    if pattern in multi_qubit_patterns:
        keys = list(measurements.keys())
        # Stack all measurement arrays [num_shots x num_qubits]
        combined = np.vstack([measurements[k].flatten() for k in keys])
        # Calculate probability all qubits triggered (all bits == 1 per shot)
        all_trigger = np.all(combined == 1, axis=0)
        score = np.mean(all_trigger)
    else:
        # Single qubit measurement average
        key = list(measurements.keys())[0]
        score = np.mean(measurements[key])

    return score, measurements, circuit

def format_score(score):
    pct = f"{score * 100:.1f}%"
    if score > 0.5:
        return pct, "💀 EXTREME RISK"
    elif score > 0.3:
        return pct, "⚠️ HIGH RISK"
    elif score > 0.1:
        return pct, "LOW RISK"
    return pct, "SAFE"

def circuit_to_text(circuit):
    return str(circuit)

def visualize_quantum_state(circuit, title="Quantum State Probabilities"):
    sim = cirq.Simulator()
    result = sim.simulate(circuit)
    state_vector = result.final_state_vector
    probs = np.abs(state_vector) ** 2
    fig, ax = plt.subplots(figsize=(5, 2.5))
    ax.bar(range(len(probs)), probs)
    ax.set_xlabel("State")
    ax.set_ylabel("Probability")
    ax.set_title(title)
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

if __name__ == "__main__":
    print("BRUTAL Quantum Engine: Self-Test")
    test_patterns = [
        ("PROBABILISTIC_BOMB", {"prob": 0.22}),
        ("ENTANGLED_BOMB", {"probs": [0.19, 0.71]}),
        ("CHAINED_QUANTUM_BOMB", {"chain_length": 4, "prob": 0.14}),
        ("CROSS_FUNCTION_QUANTUM_BOMB", {"func_probs": [0.31, 0.47, 0.99]}),
        ("QUANTUM_STEGANOGRAPHY", {"encode_val": 1}),
        ("QUANTUM_ANTIDEBUG", {"prob": 0.08}),
    ]
    for pattern, args in test_patterns:
        print(f"Testing pattern: {pattern}")
        circuit = build_quantum_circuit(pattern, **args)
        score, measurements, _ = run_quantum_analysis(circuit, pattern)
        print(f"Risk Score: {format_score(score)}")
        print(circuit)
        print("----")
