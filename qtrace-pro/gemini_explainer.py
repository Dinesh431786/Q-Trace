# gemini_explainer.py — BRUTAL QUANTUM BEAST EDITION

import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=GOOGLE_API_KEY)

def explain_result(score, pattern, code_snippet):
    """
    Brutal, quantum-native Gemini explanation for ANY quantum logic anomaly.
    Args:
        score (float): Quantum pattern risk score (0.0 - 1.0)
        pattern (str): Detected quantum logic pattern (XOR, CHAINED_BOMB, etc.)
        code_snippet (str): Full code snippet under analysis.
    Returns:
        str: Brutal, direct, plain-language Gemini explanation.
    """
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
You are an elite cybersecurity expert with deep quantum computing knowledge.
You are reviewing a code sample that has triggered a quantum-native threat detector.

CODE UNDER ANALYSIS:
--------------------
{code_snippet}
--------------------

Detected quantum pattern: {pattern}
Quantum anomaly score: {score:.2f} (0 = benign, 1 = most suspicious)

YOUR TASK:
- Clearly explain what this pattern means in a *real* attack, with reference to quantum logic (entanglement, probabilistic triggers, hidden logic bombs, etc.)
- State how rare or advanced this attack is in real-world malware/hacking.
- Tell the reader exactly why a reviewer MUST investigate or remove it (even if a static tool would miss it).
- Use strong, blunt language: DO NOT soften the risk.
- Assume the reader is smart but not a quantum security expert.
- 4-8 sentences. Brutally honest and direct.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini error: {str(e)}]"

# -------------- DEMO USAGE ---------------
if __name__ == "__main__":
    code_snippet = '''
if (random.random() < 0.12):
    os.system("shutdown -h now")
'''
    score = 0.93
    pattern = "PROBABILISTIC_BOMB"

    explanation = explain_result(score, pattern, code_snippet)
    print("Gemini brutal quantum explanation:")
    print(explanation)
