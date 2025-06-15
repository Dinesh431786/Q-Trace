import numpy as np
from sklearn.ensemble import IsolationForest

# Features you could use:
# - Quantum risk score (from engine)
# - State probability vector (flattened)
# - Entanglement metric (if multi-qubit)
# - Block length, unique call count, etc.

def block_to_features(block, risk_score, state_probs):
    # Example: flatten features for ML
    feats = []
    feats.append(risk_score)
    feats.extend(state_probs[:8])  # Take top-8 state probabilities (pad if needed)
    feats.append(len(block["body"]))
    feats.append(len(set(block["calls"])))
    return np.array(feats)

def brutal_quantum_anomaly_fit(feature_matrix):
    """
    Fit a brutal quantum anomaly model.
    Use IsolationForest for unsupervised outlier (bomb) detection.
    """
    model = IsolationForest(n_estimators=200, contamination=0.07, random_state=42)
    model.fit(feature_matrix)
    return model

def brutal_quantum_anomaly_predict(model, feature_matrix):
    """
    -1 = likely quantum bomb/outlier, 1 = normal
    """
    preds = model.predict(feature_matrix)
    scores = model.decision_function(feature_matrix)
    return preds, scores

# -------- DEMO: fit and test on synthetic data --------
if __name__ == "__main__":
    # Fake "blocks" from red team and normal code
    np.random.seed(1)
    norm_blocks = [block_to_features(
        {"body": ["foo()"], "calls": ["foo"]}, 0.09, np.random.dirichlet([1]*8)) for _ in range(20)]
    bombs = [block_to_features(
        {"body": ["os.system('shutdown')"], "calls": ["os", "system"]}, 0.87, np.random.dirichlet([3]+[1]*7)) for _ in range(5)]
    X = np.vstack(norm_blocks + bombs)
    y_true = np.array([1]*20 + [-1]*5)

    model = brutal_quantum_anomaly_fit(X)
    preds, scores = brutal_quantum_anomaly_predict(model, X)

    print("Ground truth: ", y_true)
    print("Model preds:  ", preds)
    print("Scores:       ", scores)
    print("Anomalies flagged (bombs):")
    for i, (p, score) in enumerate(zip(preds, scores)):
        if p == -1:
            print(f"Block {i}, Score: {score:.4f}")
