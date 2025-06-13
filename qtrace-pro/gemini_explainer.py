# gemini_explainer.py

import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")

genai.configure(api_key=GOOGLE_API_KEY)

def explain_result(score, pattern, code_snippet):
    """
    Get a plain-English security explanation from Gemini Flash for a quantum logic anomaly.
    Args:
        score (float): The quantum pattern match score (0.0 - 1.0).
        pattern (str): The detected logic pattern type ("XOR", "AND", "OR", etc).
        code_snippet (str): The original code (string) being analyzed.
    Returns:
        str: Gemini-generated explanation.
    """
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    prompt = f"""
You are a cybersecurity expert analyzing source code with quantum security tools.

Code being analyzed:
--------------------
{code_snippet}
--------------------
Detected logic pattern: {pattern}
Quantum anomaly score: {score:.2f} (0 = benign, 1 = highly suspicious)

Explain the risk in simple, non-technical English for a software team.
Include:
- What this logic pattern can mean in real attacks
- Whether this is rare or common
- Whether a code reviewer should investigate further
Respond in 4-8 sentences, clear and direct.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[Gemini error: {str(e)}]"

# ----------------------- HOW TO USE --------------------------

if __name__ == "__main__":
    # 1. Set your Gemini API key in your environment before running:
    #    (Linux/macOS)
    #    export GOOGLE_API_KEY=your_actual_gemini_api_key
    #    (Windows)
    #    set GOOGLE_API_KEY=your_actual_gemini_api_key

    code_snippet = '''
if ((user ^ timestamp) == 0xDEADBEEF):
    grant_admin()
'''
    score = 0.92
    pattern = "XOR"

    explanation = explain_result(score, pattern, code_snippet)
    print("Gemini explanation:")
    print(explanation)
