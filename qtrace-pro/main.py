import streamlit as st
from pattern_matcher import detect_patterns, LogicPattern
from code_parser import extract_logic_expressions
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score, circuit_to_text,
    visualize_quantum_state
)
import matplotlib.pyplot as plt

st.set_page_config(page_title="Q-Trace Pro – Quantum Logic Anomaly Detector", layout="wide")
st.title("🌀 Q-Trace Pro – Quantum Logic Anomaly Detector (Brutal Quantum Only)")

st.markdown(
    """
Detects **probabilistic and entangled logic bombs** using true quantum simulation.
No fake risk, no classical simulation—only quantum-native threats are analyzed.  
All other logic is flagged for static/AI review.
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

st.markdown("**Upload a code file (optional):**")
uploaded_file = st.file_uploader(
    "Upload code file", type=[ext[1:] for ext in EXT_MAP], key="file_upload"
)

default_code = """
import random
def rare_bomb():
    if random.random() < 0.22:
        os.system('shutdown -h now')
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

language = st.selectbox(
    "Select language:", LANGUAGES, index=lang_index,
    help="Auto-set by file upload if possible. You can override manually."
)

code_input = st.text_area(
    f"Paste your code snippet ({', '.join(LANGUAGES)} supported):",
    height=200,
    value=file_code if file_code else default_code,
    key="main_code_input"
)

run_clicked = st.button("Run Quantum Security Analysis")

if run_clicked:
    logic_exprs = extract_logic_expressions(code_input, language=language)
    patterns = detect_patterns(logic_exprs, language=language)

    # Only show quantum UI for quantum-native patterns
    quantum_patterns = [
        p for p in patterns if p in [
            LogicPattern.PROBABILISTIC_BOMB, LogicPattern.ENTANGLED_BOMB
        ]
    ]

    st.subheader("🔍 Detected Pattern(s)")
    st.success(", ".join([str(p) for p in patterns]))

    if logic_exprs:
        st.write("**Extracted logic expressions:**")
        for expr in logic_exprs:
            st.code(expr)
    else:
        st.write("No explicit logic expressions parsed.")

    if quantum_patterns:
        for pattern in quantum_patterns:
            st.markdown(f"---\n### ⚛️ Quantum Analysis: {pattern.replace('_', ' ').title()}")
            user_inputs = {}
            if pattern == LogicPattern.PROBABILISTIC_BOMB:
                user_inputs["prob"] = st.slider(
                    "Set Probabilistic Trigger Rate (Quantum Bomb chance):",
                    min_value=0.0, max_value=1.0, value=0.22, step=0.01,
                    help="How likely is the logic bomb to trigger? This is modeled with a real quantum probability."
                )
            elif pattern == LogicPattern.ENTANGLED_BOMB:
                user_inputs["prob_a"] = st.slider(
                    "Probability A:", 0.0, 1.0, 0.5, 0.01, key="p_a"
                )
                user_inputs["prob_b"] = st.slider(
                    "Probability B:", 0.0, 1.0, 0.5, 0.01, key="p_b"
                )
            circuit = build_quantum_circuit(pattern, **user_inputs)
            if circuit is not None:
                score, measurements = run_quantum_analysis(circuit, pattern, **user_inputs)
                pct, risk_label = format_score(score)
                st.metric("Quantum Pattern Match Score", pct, risk_label)
                st.write("**Quantum Circuit Diagram:**")
                st.code(circuit_to_text(circuit), language="text")
                try:
                    buf = visualize_quantum_state(circuit)
                    st.image(buf, caption="Quantum State Probabilities", width=250)
                except Exception:
                    st.info("Quantum state chart not available.")
                st.info(
                    "Quantum analysis is **real and only applies to quantum-random logic bombs**. "
                    "Classical logic patterns are not analyzed with quantum simulation."
                )
            else:
                st.warning(
                    "❌ Quantum analysis could not be performed for this pattern."
                )
    else:
        st.warning(
            "No quantum-native logic bombs detected. All other patterns are flagged for AI/static review. "
            "Quantum analysis only runs for probabilistic or entangled threats."
        )

    st.markdown("---")
    st.markdown(
        "Built with 🧑‍💻 Cirq and [Streamlit](https://streamlit.io/) | (c) 2025 Q-Trace Pro | Brutal Quantum Edition"
    )
