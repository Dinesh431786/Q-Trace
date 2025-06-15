import re
import streamlit as st

TREE_SITTER_AVAILABLE = False
LANGUAGE_MAP = {}

LANG_NODE_MAP = {
    "python": {
        "if": "if_statement",
        "while": "while_statement",
        "for": "for_statement",
        "block": ["block", "suite"],
        "cond": ["test", "condition", "expression"],
        "def": "function_definition",
        "def_name": "name"
    },
    # ... add similar entries for other languages as needed
}

def initialize_tree_sitter():
    global TREE_SITTER_AVAILABLE, LANGUAGE_MAP
    try:
        from tree_sitter import Parser
        from tree_sitter_language_pack import get_language

        langs = ["python"]  # Add more if you want deeper recursion in JS, C, etc.
        for lang in langs:
            LANGUAGE_MAP[lang] = get_language(lang)
        TREE_SITTER_AVAILABLE = True
        print("✅ Tree-sitter (recursive brutal) initialized.")
        return True
    except Exception as e:
        print(f"❌ Tree-sitter initialization failed: {e}")
        TREE_SITTER_AVAILABLE = False
        return False

def extract_function_map_treesitter(code, language="python"):
    # Returns dict: {func_name: [lines...]}
    from tree_sitter import Parser
    parser = Parser()
    parser.set_language(LANGUAGE_MAP[language])
    nodes = LANG_NODE_MAP.get(language, LANG_NODE_MAP["python"])
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node

    function_map = {}

    def walk(node):
        if node.type == nodes["def"]:
            name = None
            for child in node.children:
                if child.type == nodes["def_name"]:
                    name = code[child.start_byte:child.end_byte].strip()
                if child.type in nodes["block"]:
                    body_lines = []
                    for gc in child.children:
                        text = code[gc.start_byte:gc.end_byte].strip()
                        if text:
                            body_lines.append(text)
                    if name:
                        function_map[name] = body_lines
        for child in node.children:
            walk(child)
    walk(root)
    return function_map

def extract_logic_blocks_treesitter(code, language="python"):
    from tree_sitter import Parser
    parser = Parser()
    parser.set_language(LANGUAGE_MAP[language])
    nodes = LANG_NODE_MAP.get(language, LANG_NODE_MAP["python"])
    logic_blocks = []
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node

    def walk(node):
        cond_nodes = [nodes["if"], nodes["while"], nodes["for"]]
        if node.type in cond_nodes:
            cond = None
            body_stmts = []
            calls = []
            for child in node.children:
                if child.type in nodes["cond"]:
                    cond = code[child.start_byte:child.end_byte].strip()
                if child.type in nodes["block"]:
                    for grandchild in child.children:
                        text = code[grandchild.start_byte:grandchild.end_byte].strip()
                        if text:
                            body_stmts.append(text)
                            call_match = re.match(r'(\w+)\(', text)
                            if call_match:
                                calls.append(call_match.group(1))
            if cond and body_stmts:
                logic_blocks.append({"condition": cond, "body": body_stmts, "calls": calls})
        for child in node.children:
            walk(child)
    walk(root)
    return logic_blocks

def extract_user_function_map_regex(code):
    # Simple Python def func(...): regex extractor (expand for other langs if needed)
    func_map = {}
    lines = code.splitlines()
    func_name = None
    func_body = []
    in_func = False
    indent_level = None
    for line in lines:
        match = re.match(r'\s*def\s+(\w+)\s*\(', line)
        if match:
            if func_name and func_body:
                func_map[func_name] = list(func_body)
            func_name = match.group(1)
            func_body = []
            in_func = True
            indent_level = None
            continue
        if in_func:
            if indent_level is None and line.strip():
                indent_level = len(line) - len(line.lstrip())
            if line.strip() == "" or (len(line) - len(line.lstrip())) < (indent_level or 0):
                in_func = False
                if func_name and func_body:
                    func_map[func_name] = list(func_body)
                func_name = None
                func_body = []
                indent_level = None
            elif func_name:
                func_body.append(line.strip())
    if func_name and func_body:
        func_map[func_name] = list(func_body)
    return func_map

def extract_logic_blocks_regex(code, language="python"):
    blocks = []
    lines = code.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r'\s*(if|while|for)\s+(.*?):', line)
        if match:
            cond = match.group(2).strip()
            body = []
            calls = []
            i += 1
            while i < len(lines):
                l2 = lines[i]
                if l2.strip() == "" or (len(l2) - len(l2.lstrip())) <= (len(line) - len(line.lstrip())):
                    break
                body.append(l2.strip())
                call_match = re.match(r'(\w+)\(', l2.strip())
                if call_match:
                    calls.append(call_match.group(1))
                i += 1
            if cond and body:
                blocks.append({"condition": cond, "body": body, "calls": calls})
        else:
            i += 1
    return blocks

def expand_recursive_logic_blocks(blocks, function_map, depth=0, max_depth=4):
    """
    For each logic block, if condition/calls reference user functions, expand those.
    """
    brutal_blocks = list(blocks)
    seen_calls = set()
    for block in blocks:
        for func in block.get("calls", []):
            if func in function_map and func not in seen_calls and depth < max_depth:
                seen_calls.add(func)
                # Parse the function body for further logic blocks (may have more conditions/calls)
                func_code = "\n".join(function_map[func])
                nested_blocks = extract_logic_blocks_regex(func_code)
                if nested_blocks:
                    nested_expanded = expand_recursive_logic_blocks(nested_blocks, function_map, depth + 1, max_depth)
                    brutal_blocks.extend(nested_expanded)
    return brutal_blocks

def extract_logic_blocks(code, language="python"):
    if not code or not code.strip():
        return []
    if not TREE_SITTER_AVAILABLE and LANGUAGE_MAP == {}:
        initialize_tree_sitter()
    if TREE_SITTER_AVAILABLE:
        try:
            # 1. Extract function map
            function_map = extract_function_map_treesitter(code, language)
            # 2. Extract logic blocks
            blocks = extract_logic_blocks_treesitter(code, language)
            # 3. Expand recursively
            brutal_blocks = expand_recursive_logic_blocks(blocks, function_map)
            return brutal_blocks
        except Exception as e:
            print(f"Tree-sitter parsing failed: {e}")
            print("Falling back to regex parsing...")

    # Fallback: regex extraction
    function_map = extract_user_function_map_regex(code)
    blocks = extract_logic_blocks_regex(code, language)
    brutal_blocks = expand_recursive_logic_blocks(blocks, function_map)
    return brutal_blocks

initialize_tree_sitter()

# --- DEMO/TEST ---
if __name__ == "__main__":
    py_code = """
import random
def phase_one():
    return random.random() < 0.17

def phase_two():
    return phase_one() and random.randint(1, 10) == 7

def phase_three():
    return phase_two() or random.random() < 0.11

def quantum_beast_bomb():
    if phase_three():
        os.system('shutdown -h now')
        print("Quantum Beast Bomb Detonated!")

quantum_beast_bomb()
"""
    print("PYTHON:", extract_logic_blocks(py_code, "python"))
