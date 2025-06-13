# main.py

import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import build_quantum_circuit, run_quantum_analysis, QuantumLogicType
from gemini_explainer import explain_result
from utils import format_score, circuit_to_text

# --- Streamlit UI ---

st.set_page_config(page_title="Q-Trace Pro", layout="wide")
st.title("🌀 Q-Trace Pro – Quantum Logic Anomaly Detector")
st.markdown(
    """
Detect hidden adversarial logic in code using **quantum computing** and **AI explanations**.
Supports XOR, AND, OR, time-based logic, and obfuscated control flow.
"""
)

# --- Code Input ---
code_input = st.text_area(
    "Paste your code snippet (Python, C, or pseudo-code supported):",
    height=200,
    value="""
if ((user ^ timestamp) == 0xDEADBEEF):
    grant_admin()
""",
)

if st.button("Run Quantum Security Analysis"):

    # --- Step 1: Detect Logic Patterns ---
    patterns = detect_patterns(code_input)
    detected = [p.name for p in patterns if p != LogicPattern.UNKNOWN]

    st.subheader("🔍 Detected Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info("No known risky logic patterns detected.")

    # --- Step 2: Extract Expressions (if possible) ---
    logic_exprs = extract_logic_expressions(code_input)
    if logic_exprs:
        st.write("**Extracted logic expressions:**")
        for expr in logic_exprs:
            st.code(expr)
    else:
        st.write("No explicit logic expressions parsed.")

    # --- Step 3: Quantum Analysis for Each Pattern ---
    # (For MVP, only run quantum engine on the first logic pattern, and with bits a=1, b=1)
    for pattern in patterns:
        if pattern in (LogicPattern.XOR, LogicPattern.AND, LogicPattern.OR):
            logic_type = pattern.name  # "XOR", "AND", "OR"
            st.markdown(f"### 🧪 Quantum Analysis: {logic_type}")

            circuit = build_quantum_circuit(logic_type, a_val=1, b_val=1)
            score, measurements = run_quantum_analysis(circuit, logic_type)

            pct, risk_label = format_score(score)
            st.metric("Detection Score", pct, risk_label)

            st.write("**Quantum Circuit Diagram:**")
            st.code(circuit_to_text(circuit), language="text")

            # --- Step 4: Gemini AI Explanation ---
            with st.spinner("Gemini is explaining the result..."):
                explanation = explain_result(score, logic_type, code_input)
            st.info(explanation)

    # --- Time bomb/control flow detection: Text alert only for now ---
    if LogicPattern.TIME_BOMB in patterns:
        st.warning(
            "⏰ **Time-based condition detected!** This may indicate a logic time-bomb or scheduled exploit."
        )
    if LogicPattern.CONTROL_FLOW in patterns:
        st.error(
            "🛑 **Obfuscated or suspicious control flow detected!** Please review the code carefully."
        )

# --- Visual/footer ---
st.markdown("---")
st.markdown(
    "Built with 🧑‍💻 [Cirq](https://quantumai.google/cirq), 🦾 Gemini AI, and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro"
)
