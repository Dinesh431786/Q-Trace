import cirq
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# --- Pattern to circuit mapping ---

def build_quantum_circuit(pattern, **kwargs):
    """
    Dispatch to the appropriate quantum circuit template for the given pattern.
    """
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
    # OR logic using Toffoli + single CNOTs (a OR b = a + b - ab)
    circuit.append(cirq.CNOT(qubits[0], qubits[2]))
    circuit.append(cirq.CNOT(qubits[1], qubits[2]))
    circuit.append(cirq.TOFFOLI(qubits[0], qubits[1], qubits[2]))
    circuit.append(cirq.H(qubits[2]))
    circuit.append(cirq.measure(qubits[2], key='result'))
    return circuit

def build_time_bomb_circuit(timestamp_val=1799999999, threshold=1800000000):
    # Simulate a time-bomb: if timestamp > threshold, mark as triggered.
    qubits = cirq.LineQubit.range(4)
    circuit = cirq.Circuit()
    t = int(timestamp_val > threshold)
    if t:
        circuit.append(cirq.X(qubits[0]))
    circuit.append(cirq.H(qubits[1]))
    circuit.append(cirq.CNOT(qubits[0], qubits[2]))
    circuit.append(cirq.CNOT(qubits[1], qubits[2]))
    circuit.append(cirq.H(qubits[2]))
    circuit.append(cirq.measure(qubits[2], key='result'))
    return circuit

def build_arithmetic_circuit(val1=13, val2=7):
    # Model arithmetic modulo operation as quantum superposition
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
    # Simulate control flow obfuscation as a superposition of branches
    qubits = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()
    circuit.append(cirq.H(qubits[0]))
    circuit.append(cirq.CNOT(qubits[0], qubits[1]))
    circuit.append(cirq.measure(qubits[1], key='result'))
    return circuit

def build_hardcoded_cred_circuit():
    # Use a single qubit in a fixed state
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit()
    circuit.append(cirq.X(qubits[0]))
    circuit.append(cirq.measure(qubits[0], key='result'))
    return circuit

def build_web_backdoor_circuit():
    # Simulate hidden route as a fixed state
    qubits = cirq.LineQubit.range(1)
    circuit = cirq.Circuit()
    circuit.append(cirq.H(qubits[0]))
    circuit.append(cirq.measure(qubits[0], key='result'))
    return circuit

# --- Quantum scoring and analysis ---

QUANTUM_RISK_BOOST = {
    "TIME_BOMB": 0.10,
    "CONTROL_FLOW": 0.08,
    "ARITHMETIC": 0.09,
    "HARDCODED_CREDENTIAL": 0.07,
    "WEB_BACKDOOR": 0.08,
}

def run_quantum_analysis(circuit, pattern="XOR"):
    if circuit is None:
        return 0.0, {}
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=250)
    m_key = list(result.measurements.keys())[0]
    measurements = result.measurements[m_key]
    score = np.mean(measurements)
    # Apply risk boost for specific patterns
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
    """Visualizes quantum state vector probabilities for a circuit."""
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
    # Example: Show quantum state for time bomb logic
    circuit = build_time_bomb_circuit(1800000100)
    buf = visualize_quantum_state(circuit)
    with open("quantum_state.png", "wb") as f:
        f.write(buf.read())
    print("Saved state visualization as quantum_state.png")
