# code_parser.py

from tree_sitter import Language, Parser
import os

# Paths and setup
# Make sure you have built the Python grammar:
# Language.build_library('build/my-languages.so', ['tree-sitter-python'])
PARSER_SO_PATH = os.getenv("TREE_SITTER_SO_PATH", "build/my-languages.so")
PY_LANGUAGE = Language(PARSER_SO_PATH, 'python')

parser = Parser()
parser.set_language(PY_LANGUAGE)

def extract_logic_expressions(code_text):
    """
    Parses Python code and extracts logic expressions used in `if` or `return` statements.
    Returns a list of extracted logic expressions as strings.
    """
    tree = parser.parse(bytes(code_text, "utf8"))
    root_node = tree.root_node
    code_bytes = code_text.encode("utf8")
    results = []

    def node_text(node):
        return code_bytes[node.start_byte:node.end_byte].decode("utf8")

    def walk(node):
        # Look for if/return statements with logic ops
        if node.type in ("if_statement", "return_statement"):
            for child in node.children:
                if child.type in ("binary_operator", "comparison_operator", "boolean_operator", "expression"):
                    results.append(node_text(child))
        for child in node.children:
            walk(child)

    walk(root_node)
    return results

if __name__ == "__main__":
    # Demo/test
    code = """
def access(user, timestamp):
    if (user ^ timestamp) == 0xBEEF:
        grant_admin()
    return (user & 42) or (timestamp == 2077)
"""
    logic_exprs = extract_logic_expressions(code)
    print("Extracted logic expressions:")
    for expr in logic_exprs:
        print("-", expr)
