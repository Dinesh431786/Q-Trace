"""
code_parser.py — Brutal Quantum Python-Only Edition
Recursively extracts logic blocks and inlines all helper logic for maximum adversarial detection.
"""
import ast

def extract_logic_blocks(code, max_inline_depth=4):
    """
    Returns a list of logic blocks:
    Each block is: {"condition": "...", "body": [lines...], "calls": [funcs...]}
    All Python helper functions are inlined recursively up to max_inline_depth.
    """
    try:
        tree = ast.parse(code)
    except Exception as e:
        print(f"[code_parser] AST parse failed: {e}")
        return []

    # Build function name -> ast.FunctionDef node mapping
    func_map = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            func_map[node.name] = node

    blocks = []

    def get_source_segment(node, code_str):
        # Get code source text for node (Python 3.8+)
        try:
            return ast.get_source_segment(code_str, node)
        except Exception:
            return ""

    def inline_body(stmts, inline_depth, seen_funcs):
        result = []
        calls = []
        for stmt in stmts:
            # For function calls, try to inline if defined
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func_name = getattr(stmt.value.func, "id", None)
                if func_name and func_name in func_map and inline_depth < max_inline_depth and func_name not in seen_funcs:
                    seen_funcs = seen_funcs | {func_name}
                    # Inline called helper function recursively
                    result += inline_body(func_map[func_name].body, inline_depth+1, seen_funcs)
                else:
                    src = ast.unparse(stmt).strip() if hasattr(ast, "unparse") else ""
                    result.append(src or f"[CALL] {func_name}()")
                    if func_name:
                        calls.append(func_name)
            else:
                src = ast.unparse(stmt).strip() if hasattr(ast, "unparse") else ""
                result.append(src)
                # Find calls inside statements (not just at top-level)
                for node in ast.walk(stmt):
                    if isinstance(node, ast.Call):
                        fn = getattr(node.func, "id", None)
                        if fn:
                            calls.append(fn)
        return result, calls

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            try:
                # Condition
                cond = ast.unparse(node.test).strip() if hasattr(ast, "unparse") else ""
                # Inline body, recursively expand helpers
                body_lines, body_calls = inline_body(node.body, 1, set())
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
    sample = '''
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
'''
    blocks = extract_logic_blocks(sample)
    for b in blocks:
        print(b)
