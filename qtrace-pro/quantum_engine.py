import cirq
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

def build_quantum_circuit(pattern, **kwargs):
    if pattern == "XOR":
        return build_xor_circuit(kwargs.get("a_val", 1), kwargs.get("b_val", 1))
    elif pattern == "THREE_XOR":
        return build_3xor_circuit(kwargs.get("a_val", 1), kwargs.get("b_val", 1), kwargs.get("c_val", 1))
    elif pattern == "AND":
        return build_and_circuit(kwargs.get("a_val", 1), kwargs.get("b_val", 1))
    elif pattern == "OR":
        return build_or_circuit(kwargs.get("a_val", 1), kwargs.get("b_val", 1))
    elif pattern == "TIME_BOMB":
        return build_time_bomb_circuit(kwargs.get("timestamp_val", 1799999999), kwargs.get("threshold", 1800000000))
    elif pattern == "ARITHMETIC":
        return build_arithmetic_circuit(kwargs.get("val1", 13), kwargs.get("val2", 7))
    elif pattern == "CONTROL_FLOW":
        return build_control_flow_circuit()
    elif pattern == "HARDCODED_CREDENTIAL":
        return build_hardcoded_cred_circuit()
    elif pattern == "WEB_BACKDOOR":
        return build_web_backdoor_circuit()
    else:
        return None

def build_xor_circuit(a_val=1, b_val=1):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if a_val: circuit.append(cirq.X(qubits[0]))
    if b_val: circuit.append(cirq.X(qubits[1]))
    circuit.append([
        cirq.CNOT(qubits[0], qubits[2]),
        cirq.CNOT(qubits[1], qubits[2]),
        cirq.H(qubits[2]),
        cirq.measure(qubits[2], key='result')
    ])
    return circuit

def build_3xor_circuit(a_val=1, b_val=1, c_val=1):
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()
    if a_val: circuit.append(cirq.X(qubits[0]))
    if b_val: circuit.append(cirq.X(qubits[1]))
    if c_val: circuit.append(cirq.X(qubits[2]))
    circuit.append([
        cirq.CNOT(qubits[0], qubits[3]),
        cirq.CNOT(qubits[1], qubits[3]),
        cirq.CNOT(qubits[2], qubits[3]),
        cirq.H(qubits[3]),
        cirq.measure(qubits[3], key='result')
    ])
    return circuit

def build_and_circuit(a_val=1, b_val=1):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if a_val: circuit.append(cirq.X(qubits[0]))
    if b_val: circuit.append(cirq.X(qubits[1]))
    circuit.append([
        cirq.TOFFOLI(qubits[0], qubits[1], qubits[2]),
        cirq.H(qubits[2]),
        cirq.measure(qubits[2], key='result')
    ])
    return circuit

def build_or_circuit(a_val=1, b_val=1):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if a_val: circuit.append(cirq.X(qubits[0]))
    if b_val: circuit.append(cirq.X(qubits[1]))
    circuit.append([
        cirq.CNOT(qubits[0], qubits[2]),
        cirq.CNOT(qubits[1], qubits[2]),
        cirq.TOFFOLI(qubits[0], qubits[1], qubits[2]),
        cirq.H(qubits[2]),
        cirq.measure(qubits[2], key='result')
    ])
    return circuit

def build_time_bomb_circuit(timestamp_val=1799999999, threshold=1800000000):
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit()
    if timestamp_val > threshold:
        circuit.append(cirq.X(qubits[0]))
    circuit.append(cirq.measure(qubits[0], key='result'))
    return circuit

def build_arithmetic_circuit(val1=13, val2=7):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if val1 % 2: circuit.append(cirq.X(qubits[0]))
    if val2 % 2: circuit.append(cirq.X(qubits[1]))
    circuit.append([
        cirq.CNOT(qubits[0], qubits[2]),
        cirq.CNOT(qubits[1], qubits[2]),
        cirq.H(qubits[2]),
        cirq.measure(qubits[2], key='result')
    ])
    return circuit

def build_control_flow_circuit():
    qubits = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()
    circuit.append([
        cirq.H(qubits[0]),
        cirq.CNOT(qubits[0], qubits[1]),
        cirq.measure(qubits[1], key='result')
    ])
    return circuit

def build_hardcoded_cred_circuit():
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit([cirq.X(qubits[0]), cirq.measure(qubits[0], key='result')])
    return circuit

def build_web_backdoor_circuit():
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit([cirq.H(qubits[0]), cirq.measure(qubits[0], key='result')])
    return circuit

QUANTUM_RISK_BOOST = {
    "CONTROL_FLOW": 0.08,
    "ARITHMETIC": 0.09,
    "HARDCODED_CREDENTIAL": 0.07,
    "WEB_BACKDOOR": 0.08,
}

def run_quantum_analysis(circuit, pattern="XOR", **kwargs):
    if circuit is None:
        return 0.0, {}
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=250)
    m_key = list(result.measurements.keys())[0]
    measurements = result.measurements[m_key]
    score = np.mean(measurements)
    # For TIME_BOMB: 0% or 100% (binary, no boost)
    if pattern == "TIME_BOMB":
        if kwargs.get("timestamp_val", 0) > kwargs.get("threshold", 1800000000):
            score = 1.0
        else:
            score = 0.0
    else:
        score = min(1.0, score + QUANTUM_RISK_BOOST.get(pattern, 0.0))
    return score, measurements

def format_score(score):
    pct = f"{score * 100:.1f}%"
    if score > 0.8:
        return pct, "HIGH RISK"
    elif score > 0.5:
        return pct, "MODERATE RISK"
    elif score > 0.25:
        return pct, "LOW RISK"
    return pct, "SAFE"

def circuit_to_text(circuit):
    return str(circuit)

def visualize_quantum_state(circuit, title="Quantum State Probabilities"):
    sim = cirq.Simulator()
    result = sim.simulate(circuit)
    state_vector = result.final_state_vector
    probs = np.abs(state_vector) ** 2
    fig, ax = plt.subplots(figsize=(3.6, 2.4))
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
    circuit = build_time_bomb_circuit(1800000101, 1800000000)
    buf = visualize_quantum_state(circuit)
    with open("quantum_state.png", "wb") as f:
        f.write(buf.read())
    print("Saved state visualization as quantum_state.png")
