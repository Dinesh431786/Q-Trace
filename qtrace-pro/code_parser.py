# code_parser.py

import re

def extract_logic_expressions(code_text):
    """
    Extracts logical expressions from Python, C, or pseudo-code.
    Returns a list of logic expressions from if/return lines.
    """
    logic_lines = []
    for line in code_text.splitlines():
        line = line.strip()
        # For Python, C, and pseudo-code: handle if/return lines
        if line.startswith("if "):
            # Extract everything after 'if' and before ':' or '{' or '(' or end of line
            expr = re.split(r'[:{(]', line[3:].strip())[0].strip()
            logic_lines.append(expr)
        elif line.startswith("return "):
            expr = line[7:].strip(" ;")
            logic_lines.append(expr)
        # For C-style: if(...) {
        elif line.startswith("if("):
            expr = line[3:].split(")")[0].strip()
            logic_lines.append(expr)
    return logic_lines

if __name__ == "__main__":
    code = """
def access(user, timestamp):
    if (user ^ timestamp) == 0xBEEF:
        grant_admin()
    return (user & 42) or (timestamp == 2077)

int check(int x, int y) {
    if((x & y) == 42) {
        return 1;
    }
    return 0;
}
"""
    logic_exprs = extract_logic_expressions(code)
    print("Extracted logic expressions:")
    for expr in logic_exprs:
        print("-", expr)
