import cirq
import numpy as np

class QuantumLogicType:
    XOR = "XOR"
    AND = "AND"
    OR = "OR"
    THREE_XOR = "THREE_XOR"

def build_quantum_circuit(pattern, a_val=1, b_val=1, c_val=1):
    if pattern == "XOR":
        # 2-input XOR with 3 qubits: q0, q1, q2 (result)
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        circuit.append([
            cirq.CNOT(q0, q2),
            cirq.CNOT(q1, q2)
        ])
        circuit.append([cirq.H(q0), cirq.H(q1), cirq.H(q2)])
        circuit.append(cirq.measure(q0, q1, q2, key='result'))
        return circuit

    elif pattern == "AND":
        # 2-input AND with 3 qubits: q0, q1, q2 (result)
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        # AND logic using Toffoli gate
        circuit.append(cirq.TOFFOLI(q0, q1, q2))
        circuit.append([cirq.H(q0), cirq.H(q1), cirq.H(q2)])
        circuit.append(cirq.measure(q0, q1, q2, key='result'))
        return circuit

    elif pattern == "OR":
        # 2-input OR with 3 qubits: q0, q1, q2 (result)
        q0, q1, q2 = cirq.LineQubit.range(3)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        # OR logic: result = a OR b = NOT ( (NOT a) AND (NOT b) )
        circuit.append([cirq.X(q0), cirq.X(q1)])
        circuit.append(cirq.TOFFOLI(q0, q1, q2))
        circuit.append([cirq.X(q0), cirq.X(q1), cirq.X(q2)])
        circuit.append([cirq.H(q0), cirq.H(q1), cirq.H(q2)])
        circuit.append(cirq.measure(q0, q1, q2, key='result'))
        return circuit

    elif pattern == "THREE_XOR":
        # 3-input XOR with 4 qubits: q0, q1, q2, q3 (result)
        q0, q1, q2, q3 = cirq.LineQubit.range(4)
        circuit = cirq.Circuit()
        if a_val: circuit.append(cirq.X(q0))
        if b_val: circuit.append(cirq.X(q1))
        if c_val: circuit.append(cirq.X(q2))
        # XOR logic for three inputs: result = a ^ b ^ c
        circuit.append([
            cirq.CNOT(q0, q3),
            cirq.CNOT(q1, q3),
            cirq.CNOT(q2, q3)
        ])
        circuit.append([cirq.H(q0), cirq.H(q1), cirq.H(q2), cirq.H(q3)])
        circuit.append(cirq.measure(q0, q1, q2, q3, key='result'))
        return circuit

    else:
        raise ValueError(f"Unknown quantum pattern: {pattern}")

def run_quantum_analysis(circuit, pattern):
    simulator = cirq.Simulator()
    try:
        result = simulator.run(circuit, repetitions=1000)
    except Exception as e:
        # Always return a 0.0 score on failure
        return 0.0, {}

    measurements = result.measurements.get('result')
    if measurements is None:
        return 0.0, {}

    # For scoring: measure how often result qubit matches logic
    match_count = 0
    total = len(measurements)

    if pattern == "XOR":
        # 3 qubits: a, b, res. res should be a^b
        for row in measurements:
            a, b, res = row
            if res == (a ^ b):
                match_count += 1
    elif pattern == "AND":
        # res == (a & b)
        for row in measurements:
            a, b, res = row
            if res == (a & b):
                match_count += 1
    elif pattern == "OR":
        # res == (a | b)
        for row in measurements:
            a, b, res = row
            if res == (a | b):
                match_count += 1
    elif pattern == "THREE_XOR":
        # 4 qubits: a, b, c, res. res == (a^b^c)
        for row in measurements:
            a, b, c, res = row
            if res == (a ^ b ^ c):
                match_count += 1
    else:
        return 0.0, {}

    if total == 0:
        score = 0.0
    else:
        score = match_count / total

    # Clamp to [0, 1]
    score = max(0.0, min(1.0, score))
    return score, measurements
