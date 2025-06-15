import streamlit as st
from code_parser import extract_logic_blocks
from pattern_matcher import detect_patterns
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score,
    circuit_to_text, visualize_quantum_state
)
from gemini_explainer import explain_result
from quantum_ml import brutal_quantum_anomaly_predict, block_to_features, brutal_quantum_anomaly_fit
from quantum_graph import plot_quantum_risk_graph
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Q-Trace Pro — BRUTAL QUANTUM (Python Only)", layout="wide")
st.title("🧬 Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION")
st.markdown("""
Detects only true quantum-native, adversarial threats in Python: probabilistic bombs, entanglement, chained logic, steganography, quantum anti-debug.  
Shows *real* quantum risk—no classical simulation, no safe mode.

**Only Python code is supported in this brutal edition.**
""")

# File upload
st.markdown("**Upload a Python file (.py):**")
uploaded_file = st.file_uploader(
    "Upload Python code file", type=["py"], key="file_upload"
)

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
    logic_blocks = extract_logic_blocks(code_input)
    patterns = detect_patterns(logic_blocks)

    detected = [p for p in patterns if p != "UNKNOWN"]

    st.subheader("🔬 Detected Quantum-Native Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info(
            "No quantum-native, adversarial logic detected. (Safe code or only classical/static risk)\n\n"
            "⚠️ Note: Brutal detection works best if you paste all helper logic inline."
        )

    st.subheader("🧩 Extracted Logic Blocks")
    if logic_blocks:
        for i, block in enumerate(logic_blocks):
            st.code(f"if {block['condition']}:\n    " + "\n    ".join(block['body']), language=language)
            if block['calls']:
                st.caption("Calls: " + ", ".join(block['calls']))
    else:
        st.info("No logic blocks extracted (no conditional logic or parser failed).")

    # Quantum ML anomaly detection
    features = np.array([block_to_features(b, 0, np.zeros(8)) for b in logic_blocks]) if logic_blocks else np.array([])
    if len(features) > 0:
        model = brutal_quantum_anomaly_fit(features)
        preds, scores = brutal_quantum_anomaly_predict(model, features)
        st.subheader("🧠 Quantum ML Anomaly Detection")
        for idx, (pred, score) in enumerate(zip(preds, scores)):
            label = "Quantum Bomb Suspected" if pred == -1 else "Normal"
            risk_pct = f"{abs(score)*100:.2f}%"
            st.write(f"Block {idx}: {label} (Anomaly Score: {risk_pct})")
    else:
        preds, scores = [], []

    # Quantum Analysis & Visualization
    brutal_pattern_args = {
        "PROBABILISTIC_BOMB": {"prob": 0.22},
        "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
        "CHAINED_QUANTUM_BOMB": {"chain_length": 3, "prob": 0.14},
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

            # Gemini AI Explanation
            try:
                expl_text = explain_result(score, p, code_input)
                st.markdown(f"**Gemini AI Explanation:** {expl_text}")
            except Exception as e:
                st.warning(f"Gemini AI explanation error: {str(e)}")

        else:
            st.warning("No quantum circuit for this pattern. (Extend engine for new quantum pattern support!)")

    # Quantum Risk & Entanglement Graph Visualization
    if logic_blocks and detected:
        st.subheader("🕸️ Quantum Risk & Entanglement Graph")
        fig = plt.figure(figsize=(9,5))
        plot_quantum_risk_graph(logic_blocks, [0.1]*len(logic_blocks))  # Dummy scores, improve as needed
        st.pyplot(fig)

    st.markdown("---")
    st.caption("Built with Cirq, Streamlit, Gemini AI, and pure quantum logic. (c) 2025 Q-Trace Pro — Brutal Quantum Python Edition")
