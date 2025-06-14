import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score, circuit_to_text,
    visualize_quantum_state
)
from gemini_explainer import explain_result
import pandas as pd
import matplotlib.pyplot as plt

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

# --- File upload and auto language detection ---
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

# --- Language selection ---
language = st.selectbox(
    "Select language:", LANGUAGES, index=lang_index,
    help="Auto-set by file upload if possible. You can override manually."
)

# --- Code input (from file or textbox) ---
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

# ------------- Benchmark: Show Quantum Scores for all patterns -------------
if st.button("🚦 Show Quantum Pattern Benchmark"):
    pattern_list = [
        "XOR", "THREE_XOR", "AND", "OR",
        "TIME_BOMB", "ARITHMETIC", "CONTROL_FLOW",
        "HARDCODED_CREDENTIAL", "WEB_BACKDOOR"
    ]
    results = []
    for p in pattern_list:
        try:
            circuit = build_quantum_circuit(p)
            score, _ = run_quantum_analysis(circuit, p)
            pct, risk = format_score(score)
        except Exception:
            pct, risk = "-", "N/A"
        results.append({"Pattern": p, "Quantum Score": pct, "Risk": risk})

    df = pd.DataFrame(results)
    st.subheader("🚦 Quantum Pattern Benchmark Results")
    st.dataframe(df, use_container_width=True)

    # --- Small horizontal bar chart (UI fix) ---
    fig, ax = plt.subplots(figsize=(8, 3))
    plot_vals = [float(x['Quantum Score'][:-1]) if x['Quantum Score'] != "-" else 0 for x in results]
    ax.bar(pattern_list, plot_vals)
    ax.set_ylabel("Quantum Score (%)", fontsize=12)
    ax.set_xticklabels(pattern_list, rotation=30, ha="right", fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("---")

# ------------- Main Analysis Section -------------
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

    # --- Pattern-specific quantum input and analysis (expanded for all mapped patterns) ---
    # Priority for the quantum circuit: THREE_XOR > XOR > AND > OR > TIME_BOMB > ARITHMETIC > CONTROL_FLOW > HARDCODED_CREDENTIAL > WEB_BACKDOOR
    priority = ["THREE_XOR", "XOR", "AND", "OR", "TIME_BOMB", "ARITHMETIC", "CONTROL_FLOW", "HARDCODED_CREDENTIAL", "WEB_BACKDOOR"]
    chosen_pattern = next((pattern_label(p) for p in detected if pattern_label(p) in priority), None)
    user_inputs = {}

    if chosen_pattern == "THREE_XOR":
        st.markdown("### ⚛️ Quantum Analysis: 3-input XOR (4 Qubits)")
        user_inputs["a_val"] = st.number_input("Input value A (0 or 1):", 0, 1, 1, key="A3_input")
        user_inputs["b_val"] = st.number_input("Input value B (0 or 1):", 0, 1, 1, key="B3_input")
        user_inputs["c_val"] = st.number_input("Input value C (0 or 1):", 0, 1, 1, key="C3_input")
    elif chosen_pattern in ["XOR", "AND", "OR"]:
        st.markdown(f"### ⚛️ Quantum Analysis: {chosen_pattern} (3 Qubits)")
        user_inputs["a_val"] = st.number_input("Input value A (0 or 1):", 0, 1, 1, key="A2_input")
        user_inputs["b_val"] = st.number_input("Input value B (0 or 1):", 0, 1, 1, key="B2_input")
    elif chosen_pattern == "TIME_BOMB":
        st.markdown("### ⚛️ Quantum Analysis: Time Bomb Logic")
        user_inputs["timestamp_val"] = st.number_input("Timestamp value:", 0, 2147483647, 1799999999)
    elif chosen_pattern == "ARITHMETIC":
        st.markdown("### ⚛️ Quantum Analysis: Arithmetic/Overflow Logic")
        user_inputs["val1"] = st.number_input("Value 1:", 0, 100000, 13)
        user_inputs["val2"] = st.number_input("Value 2:", 0, 100000, 7)

    circuit = build_quantum_circuit(chosen_pattern, **user_inputs) if chosen_pattern else None

    if circuit is not None:
        score, measurements = run_quantum_analysis(circuit, chosen_pattern)
        pct, risk_label = format_score(score)
        st.metric("Quantum Pattern Match Score", pct, risk_label)
        st.write("**Quantum Circuit Diagram:**")
        st.code(circuit_to_text(circuit), language="text")
        # Optional: quantum state visualization
        try:
            buf = visualize_quantum_state(circuit)
            st.image(buf, caption="Quantum State Probabilities", use_container_width=True, width=350)
            # Interpretation help for users:
            st.caption("""
            **What does this chart mean?**
            - Each bar shows how likely the quantum circuit is to end up in a particular state after simulating your code's logic pattern.
            - A **tall bar at one state** (especially at the highest number) means your code is a strong match for a risky or backdoor logic pattern.
            - **More spread out bars** mean the pattern is less clear, but could still be risky.
            - The risk label above tells you how urgently you should review this code!
            """)
            with st.expander("ℹ️ What does this chart mean?"):
                st.markdown("""
                - Each bar = likelihood of the code matching a risky pattern in the quantum simulation.
                - Tall bar at the right = stronger match, higher risk.
                - Multiple bars or mixed = unclear or obfuscated logic, review recommended.
                - See the "Quantum Pattern Match Score" and risk label above for your action step!
                """)
        except Exception:
            pass
        with st.spinner("Gemini is explaining the result..."):
            explanation = explain_result(score, chosen_pattern, code_input)
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
