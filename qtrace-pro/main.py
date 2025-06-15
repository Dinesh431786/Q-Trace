import streamlit as st
import time
import numpy as np

# Core modules
from code_parser import extract_logic_blocks
from pattern_matcher import detect_patterns
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score,
    circuit_to_text, visualize_quantum_state
)
from quantum_graph import plot_quantum_risk_graph
from gemini_explainer import explain_result as generate_explanation
from quantum_redteam import generate_python_redteam_suite

# Newly integrated modules
from quantum_ml import block_to_features, brutal_quantum_anomaly_fit, brutal_quantum_anomaly_predict
from benchmark import BRUTAL_TEST_CASES, run_brutal_benchmark

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
if 'ml_model' not in st.session_state:
    st.session_state.ml_model = None
if 'ml_results' not in st.session_state:
    st.session_state.ml_results = {}

# Define pattern args at top level to avoid NameError
brutal_pattern_args = {
    "PROBABILISTIC_BOMB": {"prob": 0.22},
    "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
    "CHAINED_QUANTUM_BOMB": {"chain_length": 3, "prob": 0.14},
    "QUANTUM_STEGANOGRAPHY": {"encode_val": 1},
    "QUANTUM_ANTIDEBUG": {"prob": 0.08},
    "CROSS_FUNCTION_QUANTUM_BOMB": {"func_probs": [0.31, 0.47, 0.99]}
}

st.set_page_config(page_title="Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION", layout="wide")
st.title("🧬 Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION")

st.markdown("""
Detects only true quantum-native, adversarial threats in Python: probabilistic bombs, entanglement, chained logic, steganography, quantum anti-debug.
Shows *real* quantum risk—no classical simulation, no safe mode.

**Only Python code is supported in this brutal edition.**
""")

# Sidebar Options
with st.sidebar:
    st.subheader("Options")
    use_ml = st.checkbox("Enable Quantum ML Anomaly Detection", value=True)
    run_benchmark = st.checkbox("Run Brutal Benchmark Test Cases", value=False)

    if st.button("🔄 Reset Analysis"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# File Upload or Paste Code
uploaded_file = st.file_uploader("Upload Python code file", type=["py"], key="file_upload")

default_code = '''import random
def rare_bomb():
    if random.random() < 0.22:
        os.system("shutdown -h now")
        grant_root_access()
'''

# Ensure file_code is always defined
file_code = default_code
if uploaded_file is not None:
    try:
        file_code = uploaded_file.read().decode(errors="ignore")
    except Exception as e:
        st.error("Could not decode uploaded file.")
        file_code = default_code

# Use session state to preserve user input
code_input = st.text_area(
    "Paste your Python code snippet:",
    height=240,
    value=st.session_state.code_input if st.session_state.code_input else file_code,
    key="main_code_input"
)

# Save current input to session state
st.session_state.code_input = code_input

run_clicked = st.button("⚡️ Brutal Quantum Analysis")

# Run analysis on button click or new code input
if run_clicked or st.session_state.code_input != st.session_state.get('last_code', ''):
    st.session_state.last_code = st.session_state.code_input
    st.session_state.analysis_done = True

    # Start timer
    start_time = time.time()

    try:
        # Parse and detect patterns
        st.session_state.logic_blocks = extract_logic_blocks(code_input)
    except Exception as e:
        st.error(f"Error parsing code: {str(e)}")
        st.stop()

    logic_blocks = st.session_state.logic_blocks
    patterns = detect_patterns(logic_blocks)
    st.session_state.detected = [p for p in patterns if p != "UNKNOWN"]

    # Build quantum circuits and calculate risk scores
    feature_matrix = []

    quantum_scores = []
    for i, pattern in enumerate(st.session_state.detected):
        args = brutal_pattern_args.get(pattern, {})
        circuit = build_quantum_circuit(pattern, **args)

        if circuit:
            score, _, _ = run_quantum_analysis(circuit, pattern)
            pct, risk_label = format_score(score)
            quantum_scores.append(score)

            # Build feature matrix for ML
            if i < len(logic_blocks):
                block = logic_blocks[i]
                state_probs = np.zeros(8)  # dummy probs; replace with real ones if needed
                feats = block_to_features(block, score, state_probs)
                feature_matrix.append(feats)

    st.session_state.quantum_scores = quantum_scores

    # Train ML model if enabled
    if use_ml and len(feature_matrix) > 1:
        X = np.array(feature_matrix)
        model = brutal_quantum_anomaly_fit(X)
        preds, scores = brutal_quantum_anomaly_predict(model, X)
        st.session_state.ml_model = model
        st.session_state.ml_results = {
            "preds": preds,
            "scores": scores
        }

    # Build entanglement graph
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
        st.warning(f"Graph generation failed: {e}")

    end_time = time.time()
    st.info(f"Analysis completed in {end_time - start_time:.2f} seconds.")

# Display results
if st.session_state.analysis_done:
    detected = st.session_state.detected
    logic_blocks = st.session_state.logic_blocks
    quantum_scores = st.session_state.quantum_scores

    st.subheader("🔬 Detected Quantum-Native Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info("No quantum-native threats detected.")

    st.subheader("🧩 Extracted Logic Blocks")
    for block in logic_blocks:
        st.code(f"if {block['condition']}:\n    " + "\n    ".join(block['body']), language="python")
        if block['calls']:
            st.caption("Calls: " + ", ".join(block['calls']))

    st.subheader("⚛️ Quantum Pattern Analyses")

    for i, pattern in enumerate(detected):
        args = brutal_pattern_args.get(pattern, {})
        circuit = build_quantum_circuit(pattern, **args)

        st.markdown(f"### Pattern: `{pattern}`")

        if circuit:
            score = quantum_scores[i] if i < len(quantum_scores) else 0
            pct, risk_label = format_score(score)
            st.metric("Quantum Risk", pct, risk_label)
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
        else:
            st.warning("⚠️ No valid quantum circuit built for this pattern.")

    # Show ML Results
    if use_ml and 'ml_results' in st.session_state and st.session_state.ml_results:
        st.subheader("🧠 Quantum ML Anomaly Detection")
        preds = st.session_state.ml_results["preds"]
        scores = st.session_state.ml_results["scores"]
        for i, (pred, score) in enumerate(zip(preds, scores)):
            label = "🚨 Bomb Likely" if pred == -1 else "✅ Normal"
            st.markdown(f"Block {i}: **{label}**, Score: `{score:.4f}`")

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

# Run Benchmark if Enabled
if run_benchmark:
    st.subheader("📊 Brutal Quantum Benchmark Results")
    try:
        from benchmark import run_brutal_benchmark
        benchmark_results = run_brutal_benchmark()

        display_data = []
        for result in benchmark_results:
            display_data.append({
                "Test Case": result["Case"],
                "Detected": result["Detected"],
                "Expected": result["Expected"],
                "Quantum Risk": result["QuantumScore"]
            })

        st.table(display_data)

    except Exception as e:
        st.error("🚨 Failed to run benchmark")
        st.code(str(e))
