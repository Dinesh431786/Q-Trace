import cirq
import numpy as np

class QuantumLogicType:
    XOR = "XOR"
    AND = "AND"
    OR = "OR"

def build_quantum_circuit(logic_type, a_val=1, b_val=1):
    """
    Returns a Cirq quantum circuit implementing the given logic.
    Supports XOR, AND, OR.
    """
    q0, q1, q2 = cirq.LineQubit.range(3)
    circuit = cirq.Circuit()
    # Encode classical bits as quantum state
    if a_val:
        circuit.append(cirq.X(q0))
    if b_val:
        circuit.append(cirq.X(q1))

    if logic_type == QuantumLogicType.XOR:
        circuit.append([cirq.CNOT(q0, q2), cirq.CNOT(q1, q2)])
    elif logic_type == QuantumLogicType.AND:
        circuit.append(cirq.CCNOT(q0, q1, q2))  # Toffoli = AND
    elif logic_type == QuantumLogicType.OR:
        # OR(a,b) = NOT(AND(NOT a, NOT b))
        circuit.append([cirq.X(q0), cirq.X(q1)])  # NOT a, NOT b
        circuit.append(cirq.CCNOT(q0, q1, q2))   # AND(NOT a, NOT b)
        circuit.append(cirq.X(q2))               # NOT (...)
        circuit.append([cirq.X(q0), cirq.X(q1)]) # Restore a, b
    else:
        raise ValueError(f"Unknown logic type: {logic_type}")

    # Interference (optional, for analysis)
    circuit.append([cirq.H(q0), cirq.H(q1), cirq.H(q2)])

    # Measurement
    circuit.append(cirq.measure(q0, q1, q2, key='result'))
    return circuit

def run_quantum_analysis(circuit, logic_type):
    """
    Runs the quantum circuit and computes a 'pattern match score'.
    Score = frequency (0..1) that the result qubit matches the expected logic.
    """
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=1000)
    measurements = result.measurements['result']

    match_count = 0
    for meas in measurements:
        a, b, c = int(meas[0]), int(meas[1]), int(meas[2])
        expected = None
        if logic_type == QuantumLogicType.XOR:
            expected = a ^ b
        elif logic_type == QuantumLogicType.AND:
            expected = a & b
        elif logic_type == QuantumLogicType.OR:
            expected = a | b
        if c == expected:
            match_count += 1
    score = match_count / len(measurements)
    return score, measurements
