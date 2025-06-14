import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import build_quantum_circuit, run_quantum_analysis
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
    key="main_code_input"
)

# --- Run button with session state flag ---
run_clicked = st.button("Run Quantum Security Analysis")

if "run_analysis" not in st.session_state:
    st.session_state["run_analysis"] = False
if "last_code" not in st.session_state:
    st.session_state["last_code"] = ""

if run_clicked:
    st.session_state["run_analysis"] = True
    st.session_state["last_code"] = code_input
elif st.session_state["last_code"] != code_input:
    st.session_state["run_analysis"] = False

if st.session_state.get("run_analysis"):
    logic_exprs = extract_logic_expressions(code_input)
    patterns = detect_patterns(logic_exprs)
    # --- Pattern detection fix: support both enums and strings
    detected = [
        p for p in patterns
        if (isinstance(p, LogicPattern) and p != LogicPattern.UNKNOWN)
        or (isinstance(p, str) and p != "UNKNOWN")
    ]

    def pattern_label(p):
        return p.name if isinstance(p, LogicPattern) else str(p)

    st.subheader("🔍 Detected Pattern(s)")
    if detected:
        st.success(", ".join([pattern_label(p) for p in detected]))
    else:
        st.info("No known risky logic patterns detected.")

    if logic_exprs:
        st.write("**Extracted logic expressions:**")
        for expr in logic_exprs:
            st.code(expr)
    else:
        st.write("No explicit logic expressions parsed.")

    # --- Pattern-specific quantum input and analysis ---
    if LogicPattern.THREE_XOR in patterns or "THREE_XOR" in patterns:
        st.markdown("### ⚛️ Quantum Analysis: 3-input XOR (4 Qubits)")
        a_val = st.number_input("Input value A (0 or 1):", 0, 1, 1, key="A3_input")
        b_val = st.number_input("Input value B (0 or 1):", 0, 1, 1, key="B3_input")
        c_val = st.number_input("Input value C (0 or 1):", 0, 1, 1, key="C3_input")
        try:
            circuit = build_quantum_circuit("THREE_XOR", a_val=a_val, b_val=b_val, c_val=c_val)
            score, measurements = run_quantum_analysis(circuit, "THREE_XOR")
            pct, risk_label = format_score(score)
        except Exception as e:
            st.error(f"Quantum analysis failed: {e}")
            score, pct, risk_label = 0.0, "N/A", "UNKNOWN"
        st.metric("Quantum Pattern Match Score", pct, risk_label)
        st.write("**Quantum Circuit Diagram:**")
        st.code(circuit_to_text(circuit), language="text")
        with st.spinner("Gemini is explaining the result..."):
            explanation = explain_result(score, "THREE_XOR", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    elif LogicPattern.XOR in patterns or "XOR" in patterns:
        st.markdown("### ⚛️ Quantum Analysis: XOR (3 Qubits)")
        try:
            circuit = build_quantum_circuit("XOR", a_val=1, b_val=1)
            score, measurements = run_quantum_analysis(circuit, "XOR")
            pct, risk_label = format_score(score)
        except Exception as e:
            st.error(f"Quantum analysis failed: {e}")
            score, pct, risk_label = 0.0, "N/A", "UNKNOWN"
        st.metric("Quantum Pattern Match Score", pct, risk_label)
        st.write("**Quantum Circuit Diagram:**")
        st.code(circuit_to_text(circuit), language="text")
        with st.spinner("Gemini is explaining the result..."):
            explanation = explain_result(score, "XOR", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    elif LogicPattern.AND in patterns or "AND" in patterns:
        st.markdown("### ⚛️ Quantum Analysis: AND (3 Qubits)")
        try:
            circuit = build_quantum_circuit("AND", a_val=1, b_val=1)
            score, measurements = run_quantum_analysis(circuit, "AND")
            pct, risk_label = format_score(score)
        except Exception as e:
            st.error(f"Quantum analysis failed: {e}")
            score, pct, risk_label = 0.0, "N/A", "UNKNOWN"
        st.metric("Quantum Pattern Match Score", pct, risk_label)
        st.write("**Quantum Circuit Diagram:**")
        st.code(circuit_to_text(circuit), language="text")
        with st.spinner("Gemini is explaining the result..."):
            explanation = explain_result(score, "AND", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    elif LogicPattern.OR in patterns or "OR" in patterns:
        st.markdown("### ⚛️ Quantum Analysis: OR (3 Qubits)")
        try:
            circuit = build_quantum_circuit("OR", a_val=1, b_val=1)
            score, measurements = run_quantum_analysis(circuit, "OR")
            pct, risk_label = format_score(score)
        except Exception as e:
            st.error(f"Quantum analysis failed: {e}")
            score, pct, risk_label = 0.0, "N/A", "UNKNOWN"
        st.metric("Quantum Pattern Match Score", pct, risk_label)
        st.write("**Quantum Circuit Diagram:**")
        st.code(circuit_to_text(circuit), language="text")
        with st.spinner("Gemini is explaining the result..."):
            explanation = explain_result(score, "OR", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    else:
        st.warning(
            "❌ Quantum analysis not performed for this pattern. "
            "Quantum simulation is only run for logic gates like XOR, AND, OR, 3-input XOR."
        )
        with st.spinner("Gemini is analyzing the code..."):
            explanation = explain_result(0.0, "OTHER", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    if LogicPattern.TIME_BOMB in patterns or "TIME_BOMB" in patterns:
        st.warning(
            "⏰ **Time-based condition detected!** This may indicate a logic time-bomb or scheduled exploit."
        )
    if LogicPattern.CONTROL_FLOW in patterns or "CONTROL_FLOW" in patterns:
        st.error(
            "🛑 **Obfuscated or suspicious control flow detected!** Please review the code carefully."
        )

    st.markdown("---")
    st.markdown(
        "Built with 🧑‍💻 Cirq, 🦾 Gemini AI, and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro"
    )
