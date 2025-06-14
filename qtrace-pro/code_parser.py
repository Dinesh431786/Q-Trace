# code_parser.py

from tree_sitter import Parser
from tree_sitter_language_pack import get_parser

# --- Language map (expand as needed) ---
LANGUAGE_MAP = {
    "python": get_parser("python"),
    "c": get_parser("c"),
}

def extract_logic_expressions(code, language="python"):
    """
    Extract if/conditional expressions from the code using Tree-sitter AST.
    Supports: Python, C.
    Returns: list of expressions as strings
    """
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {language}")

    parser = Parser()
    parser.set_language(LANGUAGE_MAP[language])
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node

    logic_expressions = []

    def walk_python(node):
        # Python: Look for if_statement nodes
        if node.type == "if_statement":
            # Get the 'test' child (the condition)
            for child in node.children:
                if child.type == "test":
                    logic_expressions.append(code[child.start_byte:child.end_byte])
        for child in node.children:
            walk_python(child)

    def walk_c(node):
        # C: Look for if_statement nodes
        if node.type == "if_statement":
            for child in node.children:
                if child.type == "parenthesized_expression":
                    logic_expressions.append(code[child.start_byte:child.end_byte])
        for child in node.children:
            walk_c(child)

    # Choose walker by language
    if language == "python":
        walk_python(root)
    elif language == "c":
        walk_c(root)
    else:
        pass  # Add more languages as needed

    return [expr.strip() for expr in logic_expressions]

# --- Test Example ---

if __name__ == "__main__":
    py_code = '''
def foo(a, b):
    if (a ^ b) == 42:
        bar()
'''
    c_code = '''
int main(int user_id, int timestamp) {
    if ((user_id ^ timestamp) == 0xDEADBEEF) {
        grant_admin();
    }
}
'''
    print("Python extracted:", extract_logic_expressions(py_code, "python"))
    print("C extracted:", extract_logic_expressions(c_code, "c"))
