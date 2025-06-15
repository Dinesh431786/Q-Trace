"""
code_parser.py — Brutal Quantum Python-Only Edition
Recursively extracts logic blocks and inlines all helper logic for maximum adversarial detection.
"""

import ast

def extract_logic_blocks(code, language="python", max_inline_depth=4):
    """
    Returns a list of logic blocks:
    Each block is: {"condition": "...", "body": [lines...], "calls": [funcs...]}

    Supports only Python for now. Recursively inlines helper functions up to max_inline_depth.

    Args:
        code (str): Python source code
        language (str): Language to parse (currently only "python")
        max_inline_depth (int): Maximum recursion depth for inlining helper functions

    Returns:
        List[Dict]: List of extracted logic blocks
    """
    if language != "python":
        raise ValueError(f"[code_parser] Unsupported language: {language}")

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"[code_parser] AST parse failed: {e}")
        return []

    # Build function name -> ast.FunctionDef node mapping
    func_map = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_map[node.name] = node

    blocks = []

    def inline_body(stmts, inline_depth, seen_funcs):
        """
        Recursively inline function calls inside body statements
        Returns:
            (list of lines, list of called function names)
        """
        result = []
        calls = []
        for stmt in stmts:
            # Inline function calls (only top-level calls, not inside assignments)
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func_name = getattr(stmt.value.func, "id", None)
                if (
                    func_name
                    and func_name in func_map
                    and inline_depth < max_inline_depth
                    and func_name not in seen_funcs
                ):
                    # Use a new set for each recursion branch!
                    next_seen = seen_funcs | {func_name}
                    inlined, subcalls = inline_body(
                        func_map[func_name].body,
                        inline_depth + 1,
                        next_seen
                    )
                    result.extend(inlined)
                    calls.extend(subcalls)
                else:
                    src = ast.unparse(stmt).strip() if hasattr(ast, "unparse") else ""
                    result.append(src or f"[CALL] {func_name}()")
                    if func_name:
                        calls.append(func_name)
            else:
                src = ast.unparse(stmt).strip() if hasattr(ast, "unparse") else ""
                result.append(src)
                # Find function calls inside other statements
                for node in ast.walk(stmt):
                    if isinstance(node, ast.Call):
                        fn = getattr(node.func, "id", None)
                        if fn:
                            calls.append(fn)
        return result, calls

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            try:
                # Extract condition
                cond = ast.unparse(node.test).strip() if hasattr(ast, "unparse") else ""
                # Inline nested logic
                body_lines, body_calls = inline_body(node.body, 1, set())
                if cond and body_lines:
                    blocks.append({
                        "condition": cond,
                        "body": body_lines,
                        "calls": list(set(body_calls))
                    })
            except Exception as e:
                print(f"[code_parser] Failed to extract block: {e}")

    return blocks

# --- DEMO ---
if __name__ == "__main__":
    sample_code = '''
import random

def helper():
    if random.randint(1, 10) == 7:
        dangerous()

def dangerous():
    os.system("shutdown -h now")

def rare_bomb():
    if random.random() < 0.22:
        helper()
        grant_root_access()

def grant_root_access():
    print("Root access granted!")
'''

    print("Extracted Logic Blocks:")
    blocks = extract_logic_blocks(sample_code)
    for idx, block in enumerate(blocks):
        print(f"\nBlock {idx}:")
        print("Condition:", block["condition"])
        print("Body:")
        for line in block["body"]:
            print("  ", line)
        print("Calls:", block["calls"])
