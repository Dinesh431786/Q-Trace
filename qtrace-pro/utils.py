def format_score(score):
    """
    Returns (score_string, risk_label) for the UI.
    Always safe: score can be None, not a number, etc.
    """
    try:
        if score is None or not isinstance(score, (int, float)):
            return "N/A", "UNKNOWN"
        elif score < 0.4:
            return f"{score*100:.1f}%", "LOW RISK"
        elif score < 0.7:
            return f"{score*100:.1f}%", "MODERATE RISK"
        else:
            return f"{score*100:.1f}%", "HIGH RISK"
    except Exception:
        return "N/A", "UNKNOWN"

def circuit_to_text(circuit):
    """
    Returns a text/ascii diagram of the quantum circuit.
    """
    try:
        return str(circuit)
    except Exception:
        return "<circuit unavailable>"
