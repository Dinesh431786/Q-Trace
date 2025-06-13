# utils.py

import numpy as np

def format_score(score, threshold=0.8):
    """
    Formats the score as a percentage and gives a risk label.
    Returns: (score_str, label)
    """
    pct = f"{score * 100:.1f}%"
    if score >= threshold:
        label = "HIGH RISK"
    elif score >= 0.5:
        label = "MODERATE RISK"
    else:
        label = "LOW RISK"
    return pct, label

def bitwise_truth(a, b, logic_type):
    """
    Returns the expected result of a logic operation on a, b.
    Supports 'XOR', 'AND', 'OR'.
    """
    if logic_type == "XOR":
        return a ^ b
    elif logic_type == "AND":
        return a & b
    elif logic_type == "OR":
        return a | b
    else:
        raise ValueError(f"Unknown logic type: {logic_type}")

def circuit_to_text(circuit):
    """
    Returns a string representation of a Cirq quantum circuit for display.
    """
    try:
        return str(circuit.draw())
    except Exception:
        return str(circuit)

def array_sample_stats(arr):
    """
    Given a numpy array, returns min, max, mean as a tuple.
    """
    arr = np.array(arr)
    return arr.min(), arr.max(), arr.mean()
