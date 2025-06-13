import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import build_quantum_circuit, run_quantum_analysis, QuantumLogicType
from gemini_explainer import explain_result
from utils import format_score, circuit_to_text

st.set_page_config(page_title="Q-Trace Pro", layout="wide")
st.title("🌀 Q-Trace Pro – Quantum Logic Anomaly Detector")
st.markdown(
    """
Detect hidden adversarial logic in code using **quantum computing** and **AI explanations**.
Supports XOR, AND, OR, 3-input XOR, time-based logic, and obfuscated control flow.
"""
)

code_input = st.text_area(
    "Paste your code snippet (Python, C, or pseudo-code supported):",
    height=200,
    value="""
def triple_check(a, b, c):
    # 3-input XOR backdoor
    if (a ^ b ^ c) == 42:
        get_admin_shell()
""",
)

if st.button("Run Quantum Security Analysis"):

    patterns = detect_patterns(code_input)
    detected = [p.name for p in patterns if p != LogicPattern.UNKNOWN]

    st.subheader("🔍 Detected Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info("No known risky logic patterns detected.")

    logic_exprs = extract_logic_expressions(code_input)
    if logic_exprs:
        st.write("**Extracted logic expressions:**")
        for expr in logic_exprs:
            st.code(expr)
    else:
        st.write("No explicit logic expressions parsed.")

    QUANTUM_SUPPORTED = [
        LogicPattern.XOR,
        LogicPattern.AND,
        LogicPattern.OR,
        LogicPattern.THREE_XOR,
    ]
    quantum_displayed = False

    for pattern in patterns:
        if pattern in QUANTUM_SUPPORTED:
            logic_type = QuantumLogicType.from_pattern(pattern)
            quantum_displayed = True

            # Always render input boxes and results, regardless of input values
            if logic_type == "THREE_XOR":
                st.markdown(f"### ⚛️ Quantum Analysis: 3-input XOR (4 Qubits)")
                a_val = st.number_input("Input value A (0 or 1):", min_value=0, max_value=1, value=1, key="A3")
                b_val = st.number_input("Input value B (0 or 1):", min_value=0, max_value=1, value=1, key="B3")
                c_val = st.number_input("Input value C (0 or 1):", min_value=0, max_value=1, value=1, key="C3")
                circuit = build_quantum_circuit(logic_type, a_val=a_val, b_val=b_val, c_val=c_val)
            else:
                st.markdown(f"### ⚛️ Quantum Analysis: {logic_type} (3 Qubits)")
                a_val, b_val = 1, 1  # Optionally let user set these too
                circuit = build_quantum_circuit(logic_type, a_val=a_val, b_val=b_val)

            score, measurements = run_quantum_analysis(circuit, logic_type)
            pct, risk_label = format_score(score)
            st.metric("Quantum Pattern Match Score", pct, risk_label)

            st.write("**Quantum Circuit Diagram:**")
            st.code(circuit_to_text(circuit), language="text")

            with st.spinner("Gemini is explaining the result..."):
                explanation = explain_result(score, logic_type, code_input)
            st.info("**Gemini AI Explanation:**\n" + explanation)

    # Always show quantum section if detected, even if score == 0 or all input zero
    if not quantum_displayed:
        st.markdown(
            """
❌ **Quantum analysis not performed for this pattern.**  
(Quantum simulation is only run for logic gates like XOR, AND, OR, 3-input XOR.)
"""
        )
        with st.spinner("Gemini is analyzing the code..."):
            explanation = explain_result(0.0, "OTHER", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    if LogicPattern.TIME_BOMB in patterns:
        st.warning(
            "⏰ **Time-based condition detected!** This may indicate a logic time-bomb or scheduled exploit."
        )
    if LogicPattern.CONTROL_FLOW in patterns:
        st.error(
            "🛑 **Obfuscated or suspicious control flow detected!** Please review the code carefully."
        )

st.markdown("---")
st.markdown(
    "Built with 🧑‍💻 Cirq, 🦾 Gemini AI, and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro"
)
