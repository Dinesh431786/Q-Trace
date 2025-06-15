import streamlit as st
from code_parser import extract_logic_blocks
from pattern_matcher import detect_patterns, LogicPattern
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score,
    circuit_to_text, visualize_quantum_state
)
from gemini_explainer import explain_result  # BRUTAL: Gemini explanations!
import matplotlib.pyplot as plt

st.set_page_config(page_title="Q-Trace Pro — BRUTAL QUANTUM", layout="wide")
st.title("🧬 Q-Trace Pro — BRUTAL QUANTUM BEAST EDITION")
st.markdown("""
Detects only true quantum-native, adversarial threats: probabilistic bombs, entanglement, chained logic, steganography, quantum anti-debug.
Shows *real* quantum risk—no classical simulation, no safe mode.
""")

LANGUAGES = ["python", "c", "javascript", "java", "go", "rust", "solidity"]
EXT_MAP = {".py": "python", ".c": "c", ".js": "javascript", ".java": "java", ".go": "go", ".rs": "rust", ".sol": "solidity"}

st.markdown("**Upload a code file (any supported language):**")
uploaded_file = st.file_uploader("Upload code file", type=[e[1:] for e in EXT_MAP], key="file_upload")

default_code = """
import random
def rare_bomb():
    if random.random() < 0.22:
        os.system('shutdown -h now')
        grant_root_access()
"""

file_code = None
detected_lang = None

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
    height=240,
    value=file_code if file_code else default_code,
    key="main_code_input"
)

run_clicked = st.button("⚡️ Brutal Quantum Analysis")

if run_clicked:
    logic_blocks = extract_logic_blocks(code_input, language=language)
    patterns = detect_patterns(logic_blocks, language=language)

    detected = [p for p in patterns if p != LogicPattern.UNKNOWN]
    st.subheader("🔬 Detected Quantum-Native Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info("No quantum-native, adversarial logic detected. (Safe code or only classical/static risk)")

    st.subheader("🧩 Extracted Logic Blocks")
    if logic_blocks:
        for i, block in enumerate(logic_blocks):
            st.code(f"if {block['condition']}:\n    " + "\n    ".join(block['body']), language=language)
            if block['calls']:
                st.caption("Calls: " + ", ".join(block['calls']))
    else:
        st.info("No logic blocks extracted (no conditional logic or parser failed).")

    # Show analysis for each detected quantum-native pattern
    brutal_pattern_args = {
        "PROBABILISTIC_BOMB": {"prob": 0.22},
        "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
        "CHAINED_BOMB": {"chain_length": 3, "prob": 0.14},
        "QUANTUM_STEGANOGRAPHY": {"encode_val": 1},
        "QUANTUM_ANTIDEBUG": {"prob": 0.08},
        "CROSS_FUNCTION_QUANTUM_BOMB": {"func_probs": [0.31, 0.47, 0.99]}
    }

    for p in detected:
        st.markdown(f"## ⚛️ Quantum Analysis: `{p}`")
        args = brutal_pattern_args.get(p, {})
        circuit = build_quantum_circuit(p, **args)
        if circuit is not None:
            score, measurements, _ = run_quantum_analysis(circuit, p)
            pct, risk_label = format_score(score)
            st.metric("Quantum Pattern Risk", pct, risk_label)
            st.code(circuit_to_text(circuit), language="text")
            # Quantum probability/state chart
            try:
                buf = visualize_quantum_state(circuit, f"Quantum State ({p})")
                st.image(buf, caption="Quantum State Probabilities", width=350)
            except Exception:
                st.info("Quantum state chart unavailable for this pattern.")
            # Gemini explanation block (brutal, clear)
            try:
                explanation = explain_result(score, p, code_input)
                st.info("**Gemini AI Explanation:**\n" + explanation)
            except Exception as e:
                st.warning(f"Gemini explanation unavailable: {e}")
        else:
            st.warning("No quantum circuit for this pattern. (Extend engine for new quantum pattern support!)")
            # Still try to get Gemini's view of the pattern
            try:
                explanation = explain_result(0.0, p, code_input)
                st.info("**Gemini AI Explanation:**\n" + explanation)
            except Exception as e:
                st.warning(f"Gemini explanation unavailable: {e}")

    st.markdown("---")
    st.caption("Built with Cirq, Streamlit, Gemini AI, and pure quantum logic. (c) 2025 Q-Trace Pro — Brutal Quantum Edition")
