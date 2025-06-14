import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import build_quantum_circuit, run_quantum_analysis
from gemini_explainer import explain_result
from utils import format_score, circuit_to_text
import os

try:
    from guesslang import Guess
    GUESSLANG_AVAILABLE = True
except ImportError:
    GUESSLANG_AVAILABLE = False

st.set_page_config(page_title="Q-Trace Pro", layout="wide")
st.title("🌀 Q-Trace Pro – Quantum Logic Anomaly Detector")
st.markdown(
    """
Detect hidden adversarial logic in code using **quantum computing** and **AI explanations**.
Supports XOR, AND, OR, 3-input XOR, time-based logic, and obfuscated control flow.
"""
)

LANGUAGES = ["python", "c", "javascript", "java", "go", "rust", "solidity"]

def guess_language_from_code(code):
    if not GUESSLANG_AVAILABLE:
        return None
    g = Guess()
    result = g.language_name(code)
    # Map to internal options
    if "python" in result.lower():
        return "python"
    if "java" in result.lower():
        return "java"
    if "javascript" in result.lower():
        return "javascript"
    if "c++" in result.lower():
        return "c"  # fallback
    if "c" in result.lower():
        return "c"
    if "go" in result.lower():
        return "go"
    if "rust" in result.lower():
        return "rust"
    if "solidity" in result.lower():
        return "solidity"
    return None

# --- File upload or text area ---
st.markdown("#### Code Input")
uploaded_file = st.file_uploader("Upload a code file:", type=["py", "c", "js", "java", "go", "rs", "sol"])
code_input = ""
detected_language = None

if uploaded_file is not None:
    code_bytes = uploaded_file.read()
    code_input = code_bytes.decode("utf-8", errors="replace")
    if GUESSLANG_AVAILABLE:
        detected_language = guess_language_from_code(code_input)
        st.info(f"Detected language: **{detected_language}**" if detected_language else "Could not auto-detect language.")
    else:
        detected_language = None
else:
    code_input = st.text_area(
        f"Paste your code snippet ({', '.join(LANGUAGES)} supported):",
        height=200,
        value="""
def triple_check(a, b, c):
    # 3-input XOR backdoor
    if (a ^ b ^ c) == 42:
        get_admin_shell()
""",
        key="main_code_input"
    )

# --- Language select ---
default_index = LANGUAGES.index(detected_language) if detected_language in LANGUAGES else 0
language = st.selectbox("Select language:", LANGUAGES, index=default_index, key="lang_select")

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
    # Extract logic expressions AND add all code lines for robust pattern detection
    logic_exprs = extract_logic_expressions(code_input, language=language)
    all_code_lines = [line for line in code_input.split('\n') if line.strip()]
    patterns = detect_patterns(logic_exprs + all_code_lines, language=language)

    def pattern_label(p):
        return getattr(p, "name", str(p))

    detected = [
        p for p in patterns
        if ((hasattr(p, "name") and p != LogicPattern.UNKNOWN) or (isinstance(p, str) and p != "UNKNOWN"))
    ]

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

    # Pattern-specific quantum input and analysis
    if any(pattern_label(p) == "THREE_XOR" for p in detected):
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

    elif any(pattern_label(p) == "XOR" for p in detected):
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

    elif any(pattern_label(p) == "AND" for p in detected):
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

    elif any(pattern_label(p) == "OR" for p in detected):
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

    # Extra warnings for risky patterns
    if any(pattern_label(p) == "TIME_BOMB" for p in detected):
        st.warning(
            "⏰ **Time-based condition detected!** This may indicate a logic time-bomb or scheduled exploit."
        )
    if any(pattern_label(p) == "CONTROL_FLOW" for p in detected):
        st.error(
            "🛑 **Obfuscated or suspicious control flow detected!** Please review the code carefully."
        )

    st.markdown("---")
    st.markdown(
        "Built with 🧑‍💻 Cirq, 🦾 Gemini AI, and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro"
    )
