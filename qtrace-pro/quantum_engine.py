import cirq
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# ---- Real Quantum-Only Circuits ----

def build_probabilistic_bomb_circuit(prob=0.3):
    """
    Create a quantum circuit that models a probabilistic logic bomb.
    The risk score is truly quantum: the bomb triggers with probability 'prob'.
    """
    qubit = cirq.LineQubit(0)
    circuit = cirq.Circuit()
    # Ry rotation: maps probability directly to measurement outcome
    theta = 2 * np.arcsin(np.sqrt(prob))
    circuit.append(cirq.ry(theta)(qubit))
    circuit.append(cirq.measure(qubit, key='result'))
    return circuit

def build_entangled_bomb_circuit(prob_a=0.5, prob_b=0.5):
    """
    Example: Two-qubit entangled bomb—dangerous action only if both conditions met quantumly.
    """
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit()
    # First bomb arm
    theta_a = 2 * np.arcsin(np.sqrt(prob_a))
    circuit.append(cirq.ry(theta_a)(q0))
    # Entangle with second
    circuit.append(cirq.CNOT(q0, q1))
    # Second bomb arm
    theta_b = 2 * np.arcsin(np.sqrt(prob_b))
    circuit.append(cirq.ry(theta_b)(q1))
    circuit.append(cirq.measure(q0, q1, key='result'))
    return circuit

# ---- Brutal Quantum Pattern-to-Circuit Mapping ----

def build_quantum_circuit(pattern, **kwargs):
    """
    Only supports true quantum-native patterns.
    """
    if pattern == "PROBABILISTIC_BOMB":
        return build_probabilistic_bomb_circuit(kwargs.get("prob", 0.3))
    elif pattern == "ENTANGLED_BOMB":
        return build_entangled_bomb_circuit(
            kwargs.get("prob_a", 0.5),
            kwargs.get("prob_b", 0.5)
        )
    # Add more real quantum circuits as needed
    return None

# ---- Brutal Quantum Risk Analysis ----

def run_quantum_analysis(circuit, pattern, **kwargs):
    if circuit is None:
        return 0.0, {}
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1000)
    m_key = list(result.measurements.keys())[0]
    measurements = result.measurements[m_key]
    # Quantum risk is the observed trigger probability (truly quantum, not faked)
    if len(measurements.shape) == 1:  # Single qubit
        score = np.mean(measurements)
    else:  # Multi-qubit: only triggers if all are 1
        score = np.mean(np.all(measurements == 1, axis=1))
    return score, measurements

def format_score(score):
    pct = f"{score * 100:.1f}%"
    if score > 0.8:
        return pct, "HIGH QUANTUM RISK"
    elif score > 0.5:
        return pct, "MODERATE QUANTUM RISK"
    elif score > 0.25:
        return pct, "LOW QUANTUM RISK"
    return pct, "MINIMAL QUANTUM RISK"

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

# ---- DEMO: Only Real Quantum Patterns Work ----
if __name__ == "__main__":
    print("Quantum Brutal Demo: Probabilistic Bomb (prob=0.17)")
    circuit = build_probabilistic_bomb_circuit(0.17)
    score, _ = run_quantum_analysis(circuit, "PROBABILISTIC_BOMB", prob=0.17)
    print(f"Quantum risk observed: {score:.2%}")

    print("Quantum Brutal Demo: Entangled Bomb (prob_a=0.5, prob_b=0.5)")
    ent_circuit = build_entangled_bomb_circuit(0.5, 0.5)
    score, _ = run_quantum_analysis(ent_circuit, "ENTANGLED_BOMB", prob_a=0.5, prob_b=0.5)
    print(f"Entangled quantum risk: {score:.2%}")
