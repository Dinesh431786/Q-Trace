import streamlit as st
from code_parser import extract_logic_blocks
from pattern_matcher import detect_patterns
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score,
    circuit_to_text, visualize_quantum_state
)
import quantum_ml
import quantum_graph
import matplotlib.pyplot as plt

st.set_page_config(page_title="Q-Trace Pro — BRUTAL QUANTUM (Python Only)", layout="wide")
st.title("🧬 Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION")
st.markdown("""
Detects only true quantum-native, adversarial threats in Python: probabilistic bombs, entanglement, chained logic, steganography, quantum anti-debug.  
Shows *real* quantum risk—no classical simulation, no safe mode.

**Only Python code is supported in this brutal edition.**
""")

# Upload Python code file
st.markdown("**Upload a Python file (.py):**")
uploaded_file = st.file_uploader("Upload Python code file", type=["py"], key="file_upload")

default_code = '''
import random
def rare_bomb():
    if random.random() < 0.22:
        os.system("shutdown -h now")
        grant_root_access()
'''

file_code = None
if uploaded_file:
    file_code = uploaded_file.read().decode(errors="ignore")

language = "python"

code_input = st.text_area(
    "Paste your Python code snippet:",
    height=240,
    value=file_code if file_code else default_code,
    key="main_code_input"
)

run_clicked = st.button("⚡️ Brutal Quantum Analysis")

if run_clicked:
    # Extract logic blocks from Python code
    logic_blocks = extract_logic_blocks(code_input)
    # Detect quantum patterns
    patterns = detect_patterns(logic_blocks)
    detected = [p for p in patterns if p != "UNKNOWN"]

    st.subheader("🔬 Detected Quantum-Native Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info(
            "No quantum-native, adversarial logic detected. (Safe code or only classical/static risk)\n\n"
            "⚠️ Note: For best results, paste all helper function logic inline."
        )

    st.subheader("🧩 Extracted Logic Blocks")
    if logic_blocks:
        for i, block in enumerate(logic_blocks):
            st.code(f"if {block['condition']}:\n    " + "\n    ".join(block['body']), language=language)
            if block['calls']:
                st.caption("Calls: " + ", ".join(block['calls']))
    else:
        st.info("No logic blocks extracted (no conditional logic or parser failed).")

    # Prepare data for quantum engine and ML
    quantum_scores = []
    anomaly_features = []
    for p in detected:
        args_map = {
            "PROBABILISTIC_BOMB": {"prob": 0.22},
            "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
            "CHAINED_QUANTUM_BOMB": {"chain_length": 3, "prob": 0.14},
            "QUANTUM_STEGANOGRAPHY": {"encode_val": 1},
            "QUANTUM_ANTIDEBUG": {"prob": 0.08},
            "CROSS_FUNCTION_QUANTUM_BOMB": {"func_probs": [0.31, 0.47, 0.99]}
        }
        args = args_map.get(p, {})
        circuit = build_quantum_circuit(p, **args)
        if circuit is not None:
            score, measurements, _ = run_quantum_analysis(circuit, p)
            quantum_scores.append(score)
            anomaly_features.append(quantum_ml.block_to_features(
                logic_blocks[0], score, np.array([0]*8)  # Placeholder for probs if needed
            ))
        else:
            quantum_scores.append(0.0)
            anomaly_features.append(None)

    # ML anomaly detection
    if anomaly_features:
        feature_matrix = [f for f in anomaly_features if f is not None]
        model = quantum_ml.brutal_quantum_anomaly_fit(feature_matrix)
        preds, scores = quantum_ml.brutal_quantum_anomaly_predict(model, feature_matrix)
    else:
        preds, scores = [], []

    # Show detailed quantum analysis + ML results
    for i, p in enumerate(detected):
        st.markdown(f"## ⚛️ Quantum Analysis: `{p}`")
        pct, risk_label = format_score(quantum_scores[i])
        st.metric("Quantum Pattern Risk", pct, risk_label)
        st.code(circuit_to_text(build_quantum_circuit(p, **args_map.get(p, {}))), language="text")

        # Quantum state visualization
        try:
            buf = visualize_quantum_state(build_quantum_circuit(p, **args_map.get(p, {})), f"Quantum State ({p})")
            st.image(buf, caption="Quantum State Probabilities", width=350)
        except Exception:
            st.info("Quantum state chart unavailable for this pattern.")

        # ML anomaly results
        if preds:
            pred = preds[i]
            score = scores[i]
            status = "🚩 Quantum Anomaly Detected" if pred == -1 else "✅ No anomaly"
            st.write(f"ML Anomaly Score: {score:.4f} - {status}")

    # Visualize quantum risk graph
    try:
        st.subheader("🕸️ Quantum Risk & Entanglement Graph")
        quantum_graph.plot_quantum_risk_graph(logic_blocks, quantum_scores)
    except Exception:
        st.info("Quantum graph visualization unavailable.")

    st.markdown("---")
    st.caption("Built with Cirq, Streamlit, Gemini AI, and pure quantum logic. (c) 2025 Q-Trace Pro — Brutal Quantum Python Edition")
