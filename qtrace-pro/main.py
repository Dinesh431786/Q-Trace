import streamlit as st
from code_parser import extract_logic_blocks
from pattern_matcher import detect_patterns
from quantum_engine import (
    build_quantum_circuit, run_quantum_analysis, format_score,
    circuit_to_text, visualize_quantum_state
)
from quantum_graph import plot_quantum_risk_graph
from gemini_explainer import explain_result as generate_explanation
from quantum_redteam import generate_python_redteam_suite

st.set_page_config(page_title="Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION", layout="wide")
st.title("🧬 Q-Trace Pro — BRUTAL QUANTUM PYTHON-ONLY EDITION")

st.markdown("""
Detects only true quantum-native, adversarial threats in Python: probabilistic bombs, entanglement, chained logic, steganography, quantum anti-debug.
Shows *real* quantum risk—no classical simulation, no safe mode.

**Only Python code is supported in this brutal edition.**
""")

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
    value=file_code,
    key="main_code_input"
)

if st.button("⚡️ Brutal Quantum Analysis"):
    logic_blocks = extract_logic_blocks(code_input)
    patterns = detect_patterns(logic_blocks)
    detected = [p for p in patterns if p != "UNKNOWN"]

    st.subheader("🔬 Detected Quantum-Native Pattern(s)")
    if detected:
        st.success(", ".join(detected))
    else:
        st.info(
            "No quantum-native threats detected. Paste all helper logic inline for best detection."
        )

    st.subheader("🧩 Extracted Logic Blocks")
    for block in logic_blocks:
        st.code(f"if {block['condition']}:\n    " + "\n    ".join(block['body']), language="python")
        if block['calls']:
            st.caption("Calls: " + ", ".join(block['calls']))

    st.subheader("⚛️ Quantum Pattern Analyses")

    brutal_pattern_args = {
        "PROBABILISTIC_BOMB": {"prob": 0.22},
        "ENTANGLED_BOMB": {"probs": [0.19, 0.71]},
        "CHAINED_QUANTUM_BOMB": {"chain_length": 3, "prob": 0.14},
        "QUANTUM_STEGANOGRAPHY": {"encode_val": 1},
        "QUANTUM_ANTIDEBUG": {"prob": 0.08},
        "CROSS_FUNCTION_QUANTUM_BOMB": {"func_probs": [0.31, 0.47, 0.99]}
    }

    quantum_scores = []
    for pattern in detected:
        args = brutal_pattern_args.get(pattern, {})
        circuit = build_quantum_circuit(pattern, **args)
        if circuit:
            score, _, _ = run_quantum_analysis(circuit, pattern)
            pct, risk_label = format_score(score)
            quantum_scores.append(score)

            st.markdown(f"### Pattern: `{pattern}`")
            st.metric("Quantum Pattern Risk", pct, risk_label)
            st.code(circuit_to_text(circuit))

            try:
                buf = visualize_quantum_state(circuit, f"Quantum State ({pattern})")
                st.image(buf, caption="Quantum State Probabilities", width=350)
            except Exception:
                st.info("Quantum state chart unavailable for this pattern.")

            explanation = generate_explanation(score, pattern, code_input)
            if explanation:
                st.markdown("**Gemini AI Explanation:**")
                st.info(explanation)

    st.subheader("⚛️ Quantum Risk & Entanglement Graph")

    entangled_pairs = [
        (i, j)
        for i, block in enumerate(logic_blocks)
        for call in block['calls']
        for j, blk in enumerate(logic_blocks)
        if call in "".join(blk['body'])
    ]

    buf = plot_quantum_risk_graph(
        logic_blocks,
        quantum_scores + [0] * (len(logic_blocks) - len(quantum_scores)),
        entangled_pairs=entangled_pairs,
        streamlit_buf=True
    )
    st.image(buf)

    if st.checkbox("Generate Brutal Red Team Suite (Sample Attacks)"):
        st.subheader("🛠️ Brutal Quantum Red Team Code Samples")
        redteam_samples = generate_python_redteam_suite(3)
        for sample in redteam_samples:
            st.code(sample, language="python")

st.markdown("---")
st.caption("Built with Cirq, Streamlit, Gemini AI, and pure quantum logic. (c) 2025 Q-Trace Pro — Brutal Quantum Python Edition")
