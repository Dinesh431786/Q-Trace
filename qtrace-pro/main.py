import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score, circuit_to_text,
    visualize_quantum_state  # No-op is fine if not yet implemented
)
from gemini_explainer import explain_result

import pandas as pd

st.set_page_config(page_title="Q-Trace Pro", layout="wide")
st.title("🌀 Q-Trace Pro – Quantum Logic Anomaly Detector")
st.markdown(
    """
Detect hidden adversarial logic in code using **quantum computing** and **AI explanations**.  
Supports XOR, AND, OR, 3-input XOR, time-based logic, overflow, hardcoded credentials, privilege escalation, and more.
"""
)

LANGUAGES = ["python", "c", "javascript", "java", "go", "rust", "solidity"]
EXT_MAP = {
    ".py": "python",
    ".c": "c",
    ".js": "javascript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".sol": "solidity",
}

# ---- File upload and auto language detection ----
st.markdown("**Upload a code file (optional):**")
uploaded_file = st.file_uploader(
    "Upload code file", type=[ext[1:] for ext in EXT_MAP], key="file_upload"
)

default_code = """
def triple_check(a, b, c):
    # 3-input XOR backdoor
    if (a ^ b ^ c) == 42:
        get_admin_shell()
"""
detected_lang = None
file_code = None

if uploaded_file:
    file_code = uploaded_file.read().decode(errors="ignore")
    fname = uploaded_file.name.lower()
    ext = next((e for e in EXT_MAP if fname.endswith(e)), None)
    if ext:
        detected_lang = EXT_MAP[ext]

lang_index = 0
if detected_lang and detected_lang in LANGUAGES:
    lang_index = LANGUAGES.index(detected_lang)

# ---- Language selection ----
language = st.selectbox(
    "Select language:", LANGUAGES, index=lang_index,
    help="Auto-set by file upload if possible. You can override manually."
)

# ---- Code input (from file or textbox) ----
code_input = st.text_area(
    f"Paste your code snippet ({', '.join(LANGUAGES)} supported):",
    height=200,
    value=file_code if file_code else default_code,
    key="main_code_input"
)

run_clicked = st.button("Run Quantum Security Analysis")

if "run_analysis" not in st.session_state:
    st.session_state["run_analysis"] = False
if "last_code" not in st.session_state:
    st.session_state["last_code"] = ""
if "last_lang" not in st.session_state:
    st.session_state["last_lang"] = language

if run_clicked:
    st.session_state["run_analysis"] = True
    st.session_state["last_code"] = code_input
    st.session_state["last_lang"] = language
elif st.session_state["last_code"] != code_input or st.session_state["last_lang"] != language:
    st.session_state["run_analysis"] = False

# ---- Benchmark mode switch ----
show_benchmark = st.checkbox("Run Quantum Pattern Benchmark (developer mode)", value=False)

def run_quantum_benchmark():
    # Example: Run all patterns on test cases and report scores
    PATTERNS = [
        "XOR", "THREE_XOR", "AND", "OR",
        "TIME_BOMB", "ARITHMETIC", "CONTROL_FLOW",
        "HARDCODED_CREDENTIAL", "WEB_BACKDOOR"
    ]
    results = []
    for pat in PATTERNS:
        try:
            # Demo: supply demo values for input for each pattern
            if pat == "XOR":
                c = build_quantum_circuit("XOR", a_val=1, b_val=0)
            elif pat == "THREE_XOR":
                c = build_quantum_circuit("THREE_XOR", a_val=1, b_val=1, c_val=0)
            elif pat == "AND":
                c = build_quantum_circuit("AND", a_val=1, b_val=1)
            elif pat == "OR":
                c = build_quantum_circuit("OR", a_val=1, b_val=0)
            elif pat == "TIME_BOMB":
                c = build_quantum_circuit("TIME_BOMB", timestamp_val=1800000001)
            elif pat == "ARITHMETIC":
                c = build_quantum_circuit("ARITHMETIC", val1=99999, val2=2)
            elif pat == "CONTROL_FLOW":
                c = build_quantum_circuit("CONTROL_FLOW")
            elif pat == "HARDCODED_CREDENTIAL":
                c = build_quantum_circuit("HARDCODED_CREDENTIAL")
            elif pat == "WEB_BACKDOOR":
                c = build_quantum_circuit("WEB_BACKDOOR")
            else:
                continue
            if c is not None:
                score, _ = run_quantum_analysis(c, pat)
                pct, risk_label = format_score(score)
                results.append({"Pattern": pat, "Quantum Score": pct, "Risk": risk_label})
            else:
                results.append({"Pattern": pat, "Quantum Score": "-", "Risk": "-"})
        except Exception as e:
            results.append({"Pattern": pat, "Quantum Score": "Error", "Risk": str(e)})
    return results

if show_benchmark:
    st.subheader("🚦 Quantum Pattern Benchmark Results")
    bench_results = run_quantum_benchmark()
    st.table(bench_results)
    df = pd.DataFrame(bench_results)
    try:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(df["Pattern"], [float(str(s).replace('%','').replace('Error','0')) for s in df["Quantum Score"]])
        ax.set_ylabel("Quantum Score (%)")
        st.pyplot(fig)
    except Exception:
        pass
    st.markdown("---")

# ---- Main App Logic ----
if st.session_state.get("run_analysis"):
    logic_exprs = extract_logic_expressions(code_input, language=language)
    patterns = detect_patterns(logic_exprs, language=language)

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

    # --- Pattern-specific quantum input and analysis ---
    # (expandable to all enterprise patterns)
    pattern_name = next((pattern_label(p) for p in detected), None)
    user_inputs = {}
    if pattern_name == "THREE_XOR":
        st.markdown("### ⚛️ Quantum Analysis: 3-input XOR (4 Qubits)")
        user_inputs["a_val"] = st.number_input("Input value A (0 or 1):", 0, 1, 1, key="A3_input")
        user_inputs["b_val"] = st.number_input("Input value B (0 or 1):", 0, 1, 1, key="B3_input")
        user_inputs["c_val"] = st.number_input("Input value C (0 or 1):", 0, 1, 1, key="C3_input")
    elif pattern_name in ["XOR", "AND", "OR"]:
        st.markdown(f"### ⚛️ Quantum Analysis: {pattern_name} (3 Qubits)")
        user_inputs["a_val"] = st.number_input("Input value A (0 or 1):", 0, 1, 1, key="A2_input")
        user_inputs["b_val"] = st.number_input("Input value B (0 or 1):", 0, 1, 1, key="B2_input")
    elif pattern_name == "TIME_BOMB":
        st.markdown("### ⚛️ Quantum Analysis: Time Bomb Logic")
        user_inputs["timestamp_val"] = st.number_input("Timestamp value:", 0, 2147483647, 1799999999)
    elif pattern_name == "ARITHMETIC":
        st.markdown("### ⚛️ Quantum Analysis: Arithmetic/Overflow Logic")
        user_inputs["val1"] = st.number_input("Value 1:", 0, 100000, 13)
        user_inputs["val2"] = st.number_input("Value 2:", 0, 100000, 7)
    # Add more UI input fields for other patterns as needed

    circuit = build_quantum_circuit(pattern_name, **user_inputs)
    if circuit is not None:
        score, measurements = run_quantum_analysis(circuit, pattern_name)
        pct, risk_label = format_score(score)
        st.metric("Quantum Pattern Match Score", pct, risk_label)
        st.write("**Quantum Circuit Diagram:**")
        st.code(circuit_to_text(circuit), language="text")
        # Optional: quantum state visualization (if implemented)
        try:
            buf = visualize_quantum_state(circuit)
            st.image(buf, caption="Quantum State Probabilities")
        except Exception:
            pass
        with st.spinner("Gemini is explaining the result..."):
            explanation = explain_result(score, pattern_name, code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)
    else:
        st.warning(
            "❌ Quantum analysis not performed for this pattern. "
            "Quantum simulation is only run for patterns that can be mapped to quantum circuits."
        )
        with st.spinner("Gemini is analyzing the code..."):
            explanation = explain_result(0.0, "OTHER", code_input)
        st.info("**Gemini AI Explanation:**\n" + explanation)

    # Extra warnings for risky patterns
    if any(pattern_label(p) == "TIME_BOMB" for p in detected):
        st.warning("⏰ **Time-based condition detected!** This may indicate a logic time-bomb or scheduled exploit.")
    if any(pattern_label(p) == "CONTROL_FLOW" for p in detected):
        st.error("🛑 **Obfuscated or suspicious control flow detected!** Please review the code carefully.")
    if any(pattern_label(p) == "HARDCODED_CREDENTIAL" for p in detected):
        st.warning("🔐 **Hardcoded credential or secret detected!** This is a major enterprise risk.")
    if any(pattern_label(p) == "WEB_BACKDOOR" for p in detected):
        st.error("🕵️ **Possible web backdoor detected!** This could expose hidden admin/debug access.")

    st.markdown("---")
    st.markdown(
        "Built with 🧑‍💻 Cirq, 🦾 Gemini AI, and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro"
    )
