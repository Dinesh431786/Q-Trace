import networkx as nx
import matplotlib.pyplot as plt

def plot_quantum_risk_graph(blocks, quantum_scores, entangled_pairs=None, anomaly_scores=None, title="Quantum Logic/Risk Graph"):
    """
    blocks: List of logic blocks (dict, must have 'condition', 'calls')
    quantum_scores: List of quantum risk scores (0-1) for each block
    entangled_pairs: Optional list of (idx1, idx2) pairs to connect
    anomaly_scores: Optional list (same length as blocks) with anomaly scores
    """
    G = nx.DiGraph()
    for idx, block in enumerate(blocks):
        label = block['condition'][:25] + ("..." if len(block['condition']) > 25 else "")
        q_score = quantum_scores[idx]
        a_score = anomaly_scores[idx] if anomaly_scores is not None else 0
        color = (
            "#e74c3c" if q_score > 0.7 or a_score < -0.3 else
            "#f1c40f" if q_score > 0.3 else
            "#2ecc71"
        )
        G.add_node(idx, label=label, quantum_score=q_score, color=color)
        # Add call edges
        for call in block['calls']:
            # Find the block called, if in our list
            for tgt_idx, blk in enumerate(blocks):
                if call in "".join(blk['body']):
                    G.add_edge(idx, tgt_idx, weight=1)

    # Entanglement (draw with double weight or dashed)
    if entangled_pairs:
        for i, j in entangled_pairs:
            G.add_edge(i, j, weight=2, style="dashed")

    pos = nx.spring_layout(G, seed=42)
    colors = [G.nodes[n]['color'] for n in G.nodes()]
    sizes = [350 + 1500*G.nodes[n]['quantum_score'] for n in G.nodes()]
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}

    plt.figure(figsize=(9,5))
    nx.draw(
        G, pos, labels=labels, node_color=colors, node_size=sizes,
        with_labels=True, edge_color="#95a5a6", font_weight="bold", arrows=True
    )
    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

# -------- DEMO ----------
if __name__ == "__main__":
    # Brutal demo: blocks with risk/anomaly/entanglement
    demo_blocks = [
        {"condition": "random.random() < 0.19", "calls": ["quantum_bomb"], "body": ["quantum_bomb()"]},
        {"condition": "user_input == secret", "calls": ["grant_access"], "body": ["grant_access()"]},
        {"condition": "seed(x) == 42", "calls": [], "body": ["shutdown()"]},
        {"condition": "quantum_check(y)", "calls": ["rare_chain"], "body": ["rare_chain()"]}
    ]
    quantum_scores = [0.88, 0.15, 0.71, 0.43]
    anomaly_scores = [-0.45, 0.13, -0.33, -0.07]
    entangled_pairs = [(0,2), (2,3)]  # Show logic chains/entanglement

    plot_quantum_risk_graph(
        demo_blocks,
        quantum_scores,
        entangled_pairs=entangled_pairs,
        anomaly_scores=anomaly_scores,
        title="Brutal Quantum Risk & Entanglement Graph"
    )
