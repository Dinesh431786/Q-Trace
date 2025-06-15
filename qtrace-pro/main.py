import streamlit as st
import time
from code_parser import extract_logic_blocks
from pattern_matcher import detect_patterns
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score,
    circuit_to_text, visualize_quantum_state
)
from quantum_graph import plot_quantum_risk_graph
from gemini_explainer import explain_result as generate_explanation
from quantum_redteam import generate_python_redteam_suite
from utils import *  # Import necessary utilities

# Initialize session state
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False
if 'detected' not in st.session_state:
    st.session_state.detected = []
if 'logic_blocks' not in st.session_state:
    st.session_state.logic_blocks = []
if 'quantum_scores' not in st.session_state:
    st.session_state.quantum_scores = []
if 'graph_image' not in st.session_state:
    st.session_state.graph_image = None
if 'code_input' not in st.session_state:
    st.session_state.code_input = ''

st.set_page_config(page_title="Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION", layout="wide")
st.title("🧬 Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION")

# Sidebar for options
with st.sidebar:
    st.subheader("Options")
    if st.button("Reset"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Upload or paste code
uploaded_file = st.file_uploader("Upload Python code file", type=["py"], key="file_upload")
default_code = '''import random
def rare_bomb():
    if random.random() < 0.22:
        os.system("shutdown -h now")
        grant_root_access()
'''

file_code = uploaded_file.read().decode(errors="ignore") if uploaded_file else default_code
code_input = st.text_area(
    "Paste your Python code snippet:",
    height=240,
    value=st.session_state.code_input if st.session_state.code_input else file_code,
    key="main_code_input"
)

# Save current code input to session state
st.session_state.code_input = code_input

# Run Analysis Button
run_clicked = st.button("⚡️ Brutal Quantum Analysis")

# Only re-run analysis if button clicked or code changed
if run_clicked or st.session_state.code_input != st.session_state.get('last_code', ''):
    st.session_state.last_code = st.session_state.code_input
    st.session_state.analysis_done = True

    # Extract logic blocks
    try:
        st.session_state.logic_blocks = extract_logic_blocks(code_input)
    except Exception as e:
        st.error(f"Error parsing code: {str(e)}")
        st.stop()

    patterns = detect_patterns(st.session_state.logic_blocks)
    st.session_state.detected = [p for p in patterns if p != "UNKNOWN"]
    st.session_state.quantum_scores = []

    # Pattern arguments
    brutal_pattern_args = {
        "PROBABILISTIC_BOMB": {"prob": 0.22},
        "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
        "CHAINED_QUANTUM_BOMB": {"chain_length": 3, "prob": 0.14},
        "QUANTUM_STEGANOGRAPHY": {"encode_val": 1},
        "QUANTUM_ANTIDEBUG": {"prob": 0.08},
        "CROSS_FUNCTION_QUANTUM_BOMB": {"func_probs": [0.31, 0.47, 0.99]}
    }

    # Run quantum analysis
    start_time = time.time()
    quantum_scores = []
    for pattern in st.session_state.detected:
        args = brutal_pattern_args.get(pattern, {})
        circuit = build_quantum_circuit(pattern, **args)
        if circuit:
            score, _, _ = run_quantum_analysis(circuit, pattern)
            pct, risk_label = format_score(score)
            quantum_scores.append(score)

            st.session_state.quantum_scores = quantum_scores

    end_time = time.time()
    st.info(f"Analysis completed in {end_time - start_time:.2f} seconds.")

    # Build entanglement graph
    logic_blocks = st.session_state.logic_blocks
    entangled_pairs = [
        (i, j)
        for i, block in enumerate(logic_blocks)
        for call in block['calls']
        for j, blk in enumerate(logic_blocks)
        if call in "".join(blk['body'])
    ]

    try:
        buf = plot_quantum_risk_graph(
            logic_blocks,
            quantum_scores + [0] * (len(logic_blocks) - len(quantum_scores)),
            entangled_pairs=entangled_pairs,
            streamlit_buf=True
        )
        st.session_state.graph_image = buf
    except Exception as e:
        st.error(f"Graph generation failed: {e}")
        st.session_state.graph_image = None

# Display persisted results
if st.session_state.analysis_done:
    detected = st.session_state.detected
    logic_blocks = st.session_state.logic_blocks
    quantum_scores = st.session_state.quantum_scores

    # Detected Patterns
    st.subheader("🔬 Detected Quantum-Native Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info("No quantum-native threats detected. Paste all helper logic inline for best detection.")

    # Logic Blocks
    st.subheader("🧩 Extracted Logic Blocks")
    for block in logic_blocks:
        st.code(f"if {block['condition']}:\n    " + "\n    ".join(block['body']), language="python")
        if block['calls']:
            st.caption("Calls: " + ", ".join(block['calls']))

    # Quantum Analyses
    st.subheader("⚛️ Quantum Pattern Analyses")

    brutal_pattern_args = {
        "PROBABILISTIC_BOMB": {"prob": 0.22},
        "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
        "CHAINED_QUANTUM_BOMB": {"chain_length": 3, "prob": 0.14},
        "QUANTUM_STEGANOGRAPHY": {"encode_val": 1},
        "QUANTUM_ANTIDEBUG": {"prob": 0.08},
        "CROSS_FUNCTION_QUANTUM_BOMB": {"func_probs": [0.31, 0.47, 0.99]}
    }

    for pattern in detected:
        args = brutal_pattern_args.get(pattern, {})
        circuit = build_quantum_circuit(pattern, **args)
        if circuit:
            score, _, _ = run_quantum_analysis(circuit, pattern)
            pct, risk_label = format_score(score)

            st.markdown(f"### Pattern: `{pattern}`")
            st.metric("Quantum Pattern Risk", pct, risk_label)
            st.code(circuit_to_text(circuit))

            try:
                img = visualize_quantum_state(circuit, f"Quantum State ({pattern})")
                st.image(img, caption=f"Quantum State Probabilities ({pattern})", width=350)
            except Exception:
                st.info("Quantum state chart unavailable for this pattern.")

            explanation = generate_explanation(score, pattern, code_input)
            if explanation:
                st.markdown("**Gemini AI Explanation:**")
                st.info(explanation)

    # Show Graph
    st.subheader("⚛️ Quantum Risk & Entanglement Graph")
    if st.session_state.graph_image:
        st.image(st.session_state.graph_image)
    else:
        st.warning("Entanglement graph could not be generated.")

    # Red Team Samples
    if st.checkbox("Generate Brutal Red Team Suite (Sample Attacks)"):
        st.subheader("🛠️ Brutal Quantum Red Team Code Samples")
        redteam_samples = generate_python_redteam_suite(3)
        for sample in redteam_samples:
            st.code(sample, language="python")

# Footer
st.markdown("---")
st.caption("Built with Cirq, Streamlit, Gemini AI, and pure quantum logic. (c) 2025 Q-Trace Pro — Brutal Quantum Python Edition")
