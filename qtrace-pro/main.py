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
Supports XOR, AND, OR, 3-input XOR, time-based logic, overflow, hardcoded credentials, privilege escalation, probabilistic bombs, and more.
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

MAX_CODE_LENGTH = 50000  # Guard against extremely large code input

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

if len(code_input) > MAX_CODE_LENGTH:
    st.error(f"Code too long for analysis (>{MAX_CODE_LENGTH} chars). Please reduce the size.")
    st.stop()

run_clicked = st.button("Run Quantum Security Analysis")
run_all_quantum = st.checkbox("Run Quantum Analysis for All Detected Patterns", value=False)

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
        "HARDCODED_CREDENTIAL", "WEB_BACKDOOR", "PROBABILISTIC_BOMB"
    ]
    results = []
    for p in pattern_list:
        try:
            if p == "PROBABILISTIC_BOMB":
                circuit = build_quantum_circuit(p, prob=0.3)
            else:
                circuit = build_quantum_circuit(p)
            score, _ = run_quantum_analysis(circuit, p)
            pct, risk = format_score(score)
        except Exception:
            pct, risk = "-", "N/A"
        results.append({"Pattern": p, "Quantum Score": pct, "Risk": risk})

    df = pd.DataFrame(results)
    st.subheader("🚦 Quantum Pattern Benchmark Results")
    st.dataframe(df, use_container_width=True)

    # --- Small horizontal bar chart ---
    fig, ax = plt.subplots(figsize=(7, 2.5))   # <--- Nice small size
    plot_vals = [float(x['Quantum Score'][:-1]) if x['Quantum Score'] != "-" else 0 for x in results]
    ax.bar(pattern_list, plot_vals, color="#2980b9")
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

    # Choose which patterns to quantum-analyze
    patterns_to_analyze = []
    if run_all_quantum:
        # All risky patterns (that can be mapped)
        patterns_to_analyze = [
            pattern_label(p) for p in detected
            if build_quantum_circuit(pattern_label(p)) is not None
        ]
    else:
        # Priority order—just the first risky pattern (old default)
        priority = [
            "THREE_XOR", "XOR", "AND", "OR", "TIME_BOMB", "ARITHMETIC",
            "CONTROL_FLOW", "HARDCODED_CREDENTIAL", "WEB_BACKDOOR", "PROBABILISTIC_BOMB"
        ]
        for p in priority:
            if p in [pattern_label(x) for x in detected]:
                patterns_to_analyze = [p]
                break

    # For each pattern, run quantum analysis and render UI
    for idx, chosen_pattern in enumerate(patterns_to_analyze):
        st.markdown(f"---\n### ⚛️ Quantum Analysis: {chosen_pattern.replace('_', ' ').title()}")

        user_inputs = {}

        if chosen_pattern == "THREE_XOR":
            user_inputs["a_val"] = st.number_input(
                f"[{chosen_pattern}] Input value A (0 or 1):", 0, 1, 1, key=f"A3_input_{idx}"
            )
            user_inputs["b_val"] = st.number_input(
                f"[{chosen_pattern}] Input value B (0 or 1):", 0, 1, 1, key=f"B3_input_{idx}"
            )
            user_inputs["c_val"] = st.number_input(
                f"[{chosen_pattern}] Input value C (0 or 1):", 0, 1, 1, key=f"C3_input_{idx}"
            )
        elif chosen_pattern in ["XOR", "AND", "OR"]:
            user_inputs["a_val"] = st.number_input(
                f"[{chosen_pattern}] Input value A (0 or 1):", 0, 1, 1, key=f"A2_input_{idx}"
            )
            user_inputs["b_val"] = st.number_input(
                f"[{chosen_pattern}] Input value B (0 or 1):", 0, 1, 1, key=f"B2_input_{idx}"
            )
        elif chosen_pattern == "TIME_BOMB":
            col1, col2 = st.columns(2)
            user_inputs["timestamp_val"] = col1.number_input(
                f"[{chosen_pattern}] Simulated timestamp:",
                0, 2147483647, 1799999999, key=f"timestamp_input_{idx}"
            )
            user_inputs["threshold"] = col2.number_input(
                f"[{chosen_pattern}] Threshold:",
                0, 2147483647, 1800000000, key=f"threshold_input_{idx}"
            )
            st.caption(
                "For full trigger (100% risk): set Simulated timestamp *much* greater than Threshold.\n"
                "For no trigger (0% risk): set Simulated timestamp *much* less than Threshold."
            )
        elif chosen_pattern == "ARITHMETIC":
            user_inputs["val1"] = st.number_input(f"[{chosen_pattern}] Value 1:", 0, 100000, 13)
            user_inputs["val2"] = st.number_input(f"[{chosen_pattern}] Value 2:", 0, 100000, 7)
        elif chosen_pattern == "PROBABILISTIC_BOMB":
            user_inputs["prob"] = st.slider(
                "Set Probabilistic Trigger Rate (Quantum Bomb chance):",
                min_value=0.0, max_value=1.0, value=0.3, step=0.01,
                help="How likely is the hidden logic bomb to trigger? This is modeled as quantum probability."
            )

        circuit = build_quantum_circuit(chosen_pattern, **user_inputs) if chosen_pattern else None

        if circuit is not None:
            score, measurements = run_quantum_analysis(circuit, chosen_pattern, **user_inputs)
            pct, risk_label = format_score(score)
            st.metric("Quantum Pattern Match Score", pct, risk_label)
            st.write("**Quantum Circuit Diagram:**")
            st.code(circuit_to_text(circuit), language="text")

            try:
                buf = visualize_quantum_state(circuit)
                st.image(buf, caption="Quantum State Probabilities", width=250)
                st.markdown("""
                    <div style="background-color:#eef7ff;padding:10px 16px;border-radius:8px;margin-top:3px;">
                    <b>How to read this chart:</b><br>
                    • Each bar shows the probability of the quantum circuit ending in a particular state.<br>
                    • For simple logic/backdoors, only one state (a single bar) will be high—meaning the trigger is rare.<br>
                    • For probabilistic bombs, the bars show true quantum risk.<br>
                    </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.info("Quantum state chart not available for this logic.")

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
        if chosen_pattern == "TIME_BOMB":
            st.warning("⏰ **Time-based condition detected!** This may indicate a logic time-bomb or scheduled exploit.")
        if chosen_pattern == "CONTROL_FLOW":
            st.error("🛑 **Obfuscated or suspicious control flow detected!** Please review the code carefully.")
        if chosen_pattern == "HARDCODED_CREDENTIAL":
            st.warning("🔐 **Hardcoded credential or secret detected!** This is a major enterprise risk.")
        if chosen_pattern == "WEB_BACKDOOR":
            st.error("🕵️ **Possible web backdoor detected!** This could expose hidden admin/debug access.")
        if chosen_pattern == "PROBABILISTIC_BOMB":
            st.error("⚛️ **Probabilistic logic bomb detected!** This logic is quantum-random and harder to predict or catch with classical tools.")

    st.markdown("---")
    st.markdown(
        "Built with 🧑‍💻 Cirq, 🦾 Gemini AI, and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro"
    )
