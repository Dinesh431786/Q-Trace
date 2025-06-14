import cirq
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# --- Pattern to circuit mapping ---

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
        return build_time_bomb_circuit(kwargs.get("timestamp_val", 1799999999))
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
    if a_val:
        circuit.append(cirq.X(qubits[0]))
    if b_val:
        circuit.append(cirq.X(qubits[1]))
    circuit.append(cirq.CNOT(qubits[0], qubits[2]))
    circuit.append(cirq.CNOT(qubits[1], qubits[2]))
    circuit.append(cirq.H(qubits[2]))
    circuit.append(cirq.measure(qubits[2], key='result'))
    return circuit

def build_3xor_circuit(a_val=1, b_val=1, c_val=1):
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()
    if a_val:
        circuit.append(cirq.X(qubits[0]))
    if b_val:
        circuit.append(cirq.X(qubits[1]))
    if c_val:
        circuit.append(cirq.X(qubits[2]))
    circuit.append(cirq.CNOT(qubits[0], qubits[3]))
    circuit.append(cirq.CNOT(qubits[1], qubits[3]))
    circuit.append(cirq.CNOT(qubits[2], qubits[3]))
    circuit.append(cirq.H(qubits[3]))
    circuit.append(cirq.measure(qubits[3], key='result'))
    return circuit

def build_and_circuit(a_val=1, b_val=1):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if a_val:
        circuit.append(cirq.X(qubits[0]))
    if b_val:
        circuit.append(cirq.X(qubits[1]))
    circuit.append(cirq.TOFFOLI(qubits[0], qubits[1], qubits[2]))
    circuit.append(cirq.H(qubits[2]))
    circuit.append(cirq.measure(qubits[2], key='result'))
    return circuit

def build_or_circuit(a_val=1, b_val=1):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if a_val:
        circuit.append(cirq.X(qubits[0]))
    if b_val:
        circuit.append(cirq.X(qubits[1]))
    circuit.append(cirq.CNOT(qubits[0], qubits[2]))
    circuit.append(cirq.CNOT(qubits[1], qubits[2]))
    circuit.append(cirq.TOFFOLI(qubits[0], qubits[1], qubits[2]))
    circuit.append(cirq.H(qubits[2]))
    circuit.append(cirq.measure(qubits[2], key='result'))
    return circuit

def build_time_bomb_circuit(timestamp_val=1799999999, threshold=1800000000):
    # Updated: 100% triggered if timestamp > threshold, otherwise 0%
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit()
    if timestamp_val > threshold:
        circuit.append(cirq.X(qubits[0]))  # Always flip to 1 if triggered
    circuit.append(cirq.measure(qubits[0], key='result'))
    return circuit

def build_arithmetic_circuit(val1=13, val2=7):
    qubits = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    if val1 % 2:
        circuit.append(cirq.X(qubits[0]))
    if val2 % 2:
        circuit.append(cirq.X(qubits[1]))
    circuit.append(cirq.CNOT(qubits[0], qubits[2]))
    circuit.append(cirq.CNOT(qubits[1], qubits[2]))
    circuit.append(cirq.H(qubits[2]))
    circuit.append(cirq.measure(qubits[2], key='result'))
    return circuit

def build_control_flow_circuit():
    qubits = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()
    circuit.append(cirq.H(qubits[0]))
    circuit.append(cirq.CNOT(qubits[0], qubits[1]))
    circuit.append(cirq.measure(qubits[1], key='result'))
    return circuit

def build_hardcoded_cred_circuit():
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit()
    circuit.append(cirq.X(qubits[0]))
    circuit.append(cirq.measure(qubits[0], key='result'))
    return circuit

def build_web_backdoor_circuit():
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit()
    circuit.append(cirq.H(qubits[0]))
    circuit.append(cirq.measure(qubits[0], key='result'))
    return circuit

# --- Quantum scoring and analysis ---

QUANTUM_RISK_BOOST = {
    "CONTROL_FLOW": 0.08,
    "ARITHMETIC": 0.09,
    "HARDCODED_CREDENTIAL": 0.07,
    "WEB_BACKDOOR": 0.08,
    # "TIME_BOMB": 0.10,  # Not needed if score is 100%
}

def run_quantum_analysis(circuit, pattern="XOR"):
    if circuit is None:
        return 0.0, {}
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=250)
    m_key = list(result.measurements.keys())[0]
    measurements = result.measurements[m_key]
    score = np.mean(measurements)
    # Apply risk boost for specific patterns (except TIME_BOMB, now handled by logic)
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
    fig, ax = plt.subplots()
    ax.bar(range(len(probs)), probs)
    ax.set_xlabel("State")
    ax.set_ylabel("Probability")
    ax.set_title(title)
    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

# --- For direct CLI or unit test use ---
if __name__ == "__main__":
    # Example: Show quantum state for always-on time bomb
    circuit = build_time_bomb_circuit(1800000100)
    buf = visualize_quantum_state(circuit)
    with open("quantum_state.png", "wb") as f:
        f.write(buf.read())
    print("Saved state visualization as quantum_state.png")
