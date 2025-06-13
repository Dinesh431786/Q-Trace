# quantum_engine.py

import cirq
import numpy as np
from pattern_matcher import LogicPattern

# -- Existing 2-input XOR, AND, OR quantum logic --
def build_quantum_circuit(logic_type, a_val=1, b_val=1, c_val=None):
    """
    Build a quantum circuit for the selected logic pattern.
    For 2-input: a, b; for 3-input: a, b, c.
    """
    if logic_type == "XOR":
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        circuit.append([cirq.CNOT(q0, q2), cirq.CNOT(q1, q2)])
        circuit.append(cirq.H([q0, q1, q2]))
        circuit.append(cirq.measure(q0, q1, q2))
        return circuit

    elif logic_type == "AND":
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        circuit.append(cirq.CCNOT(q0, q1, q2))  # Toffoli
        circuit.append(cirq.H([q0, q1, q2]))
        circuit.append(cirq.measure(q0, q1, q2))
        return circuit

    elif logic_type == "OR":
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        # OR using De Morgan: NOT(AND(NOT a, NOT b))
        circuit.append([cirq.X(q0), cirq.X(q1)])
        circuit.append(cirq.CCNOT(q0, q1, q2))
        circuit.append([cirq.X(q0), cirq.X(q1), cirq.X(q2)])
        circuit.append(cirq.H([q0, q1, q2]))
        circuit.append(cirq.measure(q0, q1, q2))
        return circuit

    # --- New: 3-input XOR quantum simulation ---
    elif logic_type == "THREE_XOR":
        q0, q1, q2, q3 = cirq.LineQubit.range(4)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        if c_val: circuit.append(cirq.X(q2))
        # q3 = q0 ^ q1 ^ q2
        circuit.append(cirq.CNOT(q0, q3))
        circuit.append(cirq.CNOT(q1, q3))
        circuit.append(cirq.CNOT(q2, q3))
        circuit.append(cirq.H([q0, q1, q2, q3]))
        circuit.append(cirq.measure(q0, q1, q2, q3))
        return circuit

    else:
        raise ValueError("Unsupported logic type: " + logic_type)

def run_quantum_analysis(circuit, logic_type):
    simulator = cirq.Simulator()
    repetitions = 1000
    result = simulator.run(circuit, repetitions=repetitions)
    measurements = result.measurements
    arr = list(measurements.values())[0]
    # For 2-input logic: q0, q1, q2
    if logic_type in ("XOR", "AND", "OR"):
        matches = sum((bits[2] == (bits[0] ^ bits[1])) for bits in arr)
        score = matches / repetitions
    # For 3-input XOR: q0, q1, q2, q3
    elif logic_type == "THREE_XOR":
        matches = sum((bits[3] == (bits[0] ^ bits[1] ^ bits[2])) for bits in arr)
        score = matches / repetitions
    else:
        score = 0.0
    return score, measurements

# --- Utility for logic_type compatibility ---
class QuantumLogicType:
    @staticmethod
    def from_pattern(pattern: LogicPattern):
        if pattern == LogicPattern.XOR:
            return "XOR"
        if pattern == LogicPattern.AND:
            return "AND"
        if pattern == LogicPattern.OR:
            return "OR"
        if pattern == LogicPattern.THREE_XOR:
            return "THREE_XOR"
        return None
