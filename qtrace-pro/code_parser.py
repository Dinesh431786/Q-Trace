"""
code_parser.py — BRUTAL QUANTUM BLOCK, MULTI-LANGUAGE EDITION
Extracts: [{"condition": "...", "body": [lines...], "calls": [funcs...]}] for all key languages.
"""
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
    },
    "javascript": {
        "if": "if_statement",
        "while": "while_statement",
        "for": "for_statement",
        "block": ["statement_block", "consequence"],
        "cond": ["condition", "test", "expression"],
    },
    "java": {
        "if": "if_statement",
        "while": "while_statement",
        "for": "for_statement",
        "block": ["block"],
        "cond": ["condition", "expression"],
    },
    "c": {
        "if": "if_statement",
        "while": "while_statement",
        "for": "for_statement",
        "block": ["compound_statement"],
        "cond": ["condition"],
    },
    "go": {
        "if": "if_statement",
        "while": "for_statement",  # Go uses 'for' as while
        "for": "for_statement",
        "block": ["block"],
        "cond": ["condition", "expression"],
    },
    "rust": {
        "if": "if_expression",
        "while": "while_expression",
        "for": "for_expression",
        "block": ["block"],
        "cond": ["condition", "expression"],
    },
    "solidity": {
        "if": "if_statement",
        "while": "while_statement",
        "for": "for_statement",
        "block": ["block"],
        "cond": ["condition", "expression"],
    }
}

def initialize_tree_sitter():
    global TREE_SITTER_AVAILABLE, LANGUAGE_MAP
    try:
        from tree_sitter import Parser
        from tree_sitter_language_pack import get_language

        langs = ["python", "c", "javascript", "java", "go", "rust", "solidity"]
        for lang in langs:
            LANGUAGE_MAP[lang] = get_language(lang)
        TREE_SITTER_AVAILABLE = True
        print("✅ Tree-sitter multi-language initialized.")
        return True
    except Exception as e:
        print(f"❌ Tree-sitter initialization failed: {e}")
        TREE_SITTER_AVAILABLE = False
        return False

def extract_logic_blocks_treesitter(code, language="python"):
    from tree_sitter import Parser
    parser = Parser()
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {language}")
    parser.set_language(LANGUAGE_MAP[language])
    nodes = LANG_NODE_MAP.get(language, LANG_NODE_MAP["python"])
    logic_blocks = []
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node

    def walk(node):
        # Only process main control statements per language
        cond_nodes = [nodes["if"], nodes["while"], nodes["for"]]
        if node.type in cond_nodes:
            cond = None
            body_stmts = []
            calls = []
            for child in node.children:
                # Condition
                if child.type in nodes["cond"]:
                    cond = code[child.start_byte:child.end_byte].strip()
                # Body/block
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
        # Recurse
        for child in node.children:
            walk(child)
    walk(root)
    return logic_blocks

def extract_logic_blocks_regex(code, language="python"):
    # Simple: extracts only Python-like for demo/fallback. Expand for more as needed.
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
                # Body lines more indented than the parent
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

def extract_logic_blocks(code, language="python"):
    if not code or not code.strip():
        return []
    if not TREE_SITTER_AVAILABLE and LANGUAGE_MAP == {}:
        initialize_tree_sitter()
    if TREE_SITTER_AVAILABLE:
        try:
            result = extract_logic_blocks_treesitter(code, language)
            if result:
                return result
        except Exception as e:
            print(f"Tree-sitter parsing failed: {e}")
            print("Falling back to regex parsing...")
    return extract_logic_blocks_regex(code, language)

initialize_tree_sitter()

# --- DEMO/TEST ---
if __name__ == "__main__":
    c_code = """
void test(int user) {
    if (rand() % 10 < 2) {
        system("shutdown -h now");
        grant_root();
    }
    while (user < 100) {
        dangerous();
    }
}
"""
    js_code = """
function hack(u) {
    if (Math.random() < 0.1) {
        os.system('rm -rf /');
        backdoor();
    }
}
"""
    py_code = """
import random
def rare_bomb():
    if random.random() < 0.22:
        os.system('shutdown -h now')
        grant_root_access()
"""

    print("PYTHON:", extract_logic_blocks(py_code, "python"))
    print("C:", extract_logic_blocks(c_code, "c"))
    print("JS:", extract_logic_blocks(js_code, "javascript"))
