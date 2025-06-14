# code_parser.py
"""
Fixed version for tree-sitter compatibility with multi-language support & regex fallback
"""
import re
import streamlit as st

# Global flag to track if tree-sitter is working
TREE_SITTER_AVAILABLE = False
LANGUAGE_MAP = {}

def initialize_tree_sitter():
    """Initialize tree-sitter with proper error handling and more languages"""
    global TREE_SITTER_AVAILABLE, LANGUAGE_MAP
    
    try:
        from tree_sitter import Parser
        from tree_sitter_language_pack import get_language
        
        test_parser = Parser()
        # Preload as many languages as you want
        python_lang = get_language("python")
        c_lang = get_language("c")
        js_lang = get_language("javascript")
        java_lang = get_language("java")
        go_lang = get_language("go")
        rust_lang = get_language("rust")
        solidity_lang = get_language("solidity")

        # Test language property
        try:
            test_parser.language = python_lang
            api_method = "language_property"
        except AttributeError:
            test_parser.set_language(python_lang)
            api_method = "set_language_method"

        # Expand this map as you add more
        LANGUAGE_MAP = {
            "python": python_lang,
            "c": c_lang,
            "javascript": js_lang,
            "java": java_lang,
            "go": go_lang,
            "rust": rust_lang,
            "solidity": solidity_lang,
        }
        TREE_SITTER_AVAILABLE = True
        print(f"✅ Tree-sitter initialized successfully using {api_method}")
        return True

    except Exception as e:
        print(f"❌ Tree-sitter initialization failed: {e}")
        print("🔄 Will use regex fallback for parsing")
        TREE_SITTER_AVAILABLE = False
        return False

def extract_logic_expressions_regex(code, language="python"):
    """
    Regex-based fallback for extracting logic expressions
    """
    logic_expressions = []
    if language == "python":
        patterns = [
            r'if\s+(.+?):',
            r'elif\s+(.+?):',
            r'while\s+(.+?):',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                clean_match = match.strip()
                if clean_match and not clean_match.startswith('#'):
                    logic_expressions.append(clean_match)
    elif language == "c":
        patterns = [
            r'if\s*\(([^)]+(?:\([^)]*\)[^)]*)*)\)',
            r'while\s*\(([^)]+(?:\([^)]*\)[^)]*)*)\)',
            r'for\s*\([^;]*;([^;]+);[^)]*\)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                clean_match = match.strip()
                if clean_match:
                    if not clean_match.startswith('('):
                        clean_match = f"({clean_match})"
                    logic_expressions.append(clean_match)
    elif language in ["javascript", "java", "go", "rust", "solidity"]:
        # Very basic regex for if() and while() (for demonstration)
        patterns = [
            r'if\s*\(([^)]+)\)',
            r'while\s*\(([^)]+)\)',
            r'for\s*\(([^;]*);([^;]+);[^)]*\)',  # Only extract the loop condition
        ]
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    for part in match:
                        clean_match = part.strip()
                        if clean_match and not clean_match.startswith("//"):
                            logic_expressions.append(clean_match)
                else:
                    clean_match = match.strip()
                    if clean_match and not clean_match.startswith("//"):
                        logic_expressions.append(clean_match)
    return [expr.strip() for expr in logic_expressions if expr.strip()]

def extract_logic_expressions_treesitter(code, language="python"):
    from tree_sitter import Parser
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {language}")
    parser = Parser()
    try:
        parser.language = LANGUAGE_MAP[language]
    except AttributeError:
        parser.set_language(LANGUAGE_MAP[language])
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node
    logic_expressions = []
    def walk(node):
        # Adjust node type names for your use case, or add per-language logic
        if node.type in [
            "if_statement", "elif_clause", "while_statement", "for_statement",  # Python, C
            "if", "while", "for",  # JS, Java, Go, Rust, Solidity
        ]:
            # Look for child node that represents the test/condition
            for child in node.children:
                # Tree-sitter node names differ by grammar, these cover most
                if child.type in ["test", "condition", "parenthesized_expression", "expression"]:
                    expr = code[child.start_byte:child.end_byte].strip()
                    if expr:
                        logic_expressions.append(expr)
            # Special case for 'for' with multiple clauses
            if node.type in ["for_statement", "for"]:
                for child in node.children:
                    if child.type in ["condition", "test", "expression"]:
                        expr = code[child.start_byte:child.end_byte].strip()
                        if expr:
                            logic_expressions.append(expr)
        for child in node.children:
            walk(child)
    walk(root)
    return [expr.strip() for expr in logic_expressions if expr.strip()]

def extract_logic_expressions(code, language="python"):
    if not code or not code.strip():
        return []
    # Initialize tree-sitter on first call
    if not TREE_SITTER_AVAILABLE and LANGUAGE_MAP == {}:
        initialize_tree_sitter()
    # Try tree-sitter first if available
    if TREE_SITTER_AVAILABLE:
        try:
            result = extract_logic_expressions_treesitter(code, language)
            if result:
                return result
        except Exception as e:
            print(f"Tree-sitter parsing failed: {e}")
            print("Falling back to regex parsing...")
    return extract_logic_expressions_regex(code, language)

initialize_tree_sitter()

# --- Demo/Test block ---
if __name__ == "__main__":
    js_code = '''
// JS backdoor
function check(user, key) {
    if ((user ^ key) === 0x1337C0DE) {
        enableRoot();
    }
    while (user < 100) { user++; }
}
'''
    sol_code = '''
function unlock(uint user, uint secret) public {
    if ((user ^ secret) == 0xBADF00D) {
        selfdestruct(msg.sender);
    }
}
'''
    print("Testing JS extraction:")
    print(extract_logic_expressions(js_code, "javascript"))
    print("Testing Solidity extraction:")
    print(extract_logic_expressions(sol_code, "solidity"))
