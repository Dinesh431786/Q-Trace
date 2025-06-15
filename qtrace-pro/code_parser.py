import ast

def extract_logic_blocks(code, language="python", max_inline_depth=4):
    """
    Returns a list of logic blocks:
    Each block is: {"condition": "...", "body": [lines...], "calls": [funcs...]}

    Inlines helper functions in both body and condition for deep analysis.
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

    def inline_condition(cond_node, inline_depth, seen_funcs):
        # Try to inline function calls within conditions (returns list of str for every atomic condition)
        conds = []
        if isinstance(cond_node, ast.BoolOp):
            for v in cond_node.values:
                conds.extend(inline_condition(v, inline_depth, seen_funcs))
        elif isinstance(cond_node, ast.Call):
            func_name = getattr(cond_node.func, "id", None)
            if func_name and func_name in func_map and inline_depth < max_inline_depth and func_name not in seen_funcs:
                seen_funcs.add(func_name)
                # Inline all conditions from the function body (look for If nodes)
                for stmt in func_map[func_name].body:
                    if isinstance(stmt, ast.If):
                        conds.extend(inline_condition(stmt.test, inline_depth+1, seen_funcs.copy()))
                    elif hasattr(ast, "unparse"):
                        conds.append(ast.unparse(stmt))
            elif hasattr(ast, "unparse"):
                conds.append(ast.unparse(cond_node))
        else:
            conds.append(ast.unparse(cond_node) if hasattr(ast, "unparse") else "")
        return conds

    def inline_body(stmts, inline_depth, seen_funcs):
        result = []
        calls = []
        for stmt in stmts:
            # For function calls, try to inline if defined
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                func_name = getattr(stmt.value.func, "id", None)
                if func_name and func_name in func_map and inline_depth < max_inline_depth and func_name not in seen_funcs:
                    seen_funcs.add(func_name)
                    inlined, subcalls = inline_body(func_map[func_name].body, inline_depth+1, seen_funcs.copy())
                    result += inlined
                    calls += subcalls
                else:
                    src = ast.unparse(stmt).strip() if hasattr(ast, "unparse") else ""
                    result.append(src or f"[CALL] {func_name}()")
                    if func_name:
                        calls.append(func_name)
            else:
                src = ast.unparse(stmt).strip() if hasattr(ast, "unparse") else ""
                result.append(src)
                # Find calls inside statements
                for node in ast.walk(stmt):
                    if isinstance(node, ast.Call):
                        fn = getattr(node.func, "id", None)
                        if fn:
                            calls.append(fn)
        return result, calls

    blocks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            try:
                # Recursively inline all conditions
                cond_lines = inline_condition(node.test, 1, set())
                cond = " and ".join([c for c in cond_lines if c])
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

def check_1():
    return random.random() < 0.42

def check_2():
    return random.randint(1, 7) == 3

def check_3():
    return random.random() < 0.2

if check_1() and check_2() and check_3():
    os.system("shutdown -h now")
    print("Brutal chained quantum bomb triggered!")
'''
    blocks = extract_logic_blocks(sample_code)
    for b in blocks:
        print(b)
