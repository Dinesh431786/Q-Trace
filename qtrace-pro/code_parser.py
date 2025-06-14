# code_parser.py

from tree_sitter import Parser
from tree_sitter_language_pack import get_language

LANGUAGE_MAP = {
    "python": get_language("python"),
    "c": get_language("c"),
    # Add more languages if you want: "javascript", "java", etc.
}

def extract_logic_expressions(code, language="python"):
    """
    Extract logic/conditional expressions from code using Tree-sitter AST.
    Supports: Python, C. Returns a list of expressions as strings.
    """
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {language}")

    parser = Parser()
    parser.set_language(LANGUAGE_MAP[language])
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node

    logic_expressions = []

    def walk_python(node):
        # Find if_statement and their conditions ("test" child)
        if node.type == "if_statement":
            for child in node.children:
                if child.type == "test":
                    logic_expressions.append(code[child.start_byte:child.end_byte])
        for child in node.children:
            walk_python(child)

    def walk_c(node):
        # Find C if_statement and their conditions (parenthesized_expression)
        if node.type == "if_statement":
            for child in node.children:
                if child.type == "parenthesized_expression":
                    logic_expressions.append(code[child.start_byte:child.end_byte])
        for child in node.children:
            walk_c(child)

    if language == "python":
        walk_python(root)
    elif language == "c":
        walk_c(root)

    return [expr.strip() for expr in logic_expressions]

# --- Demo/Test block ---
if __name__ == "__main__":
    py_code = '''
def foo(a, b):
    if (a ^ b) == 42:
        bar()
    if a and b:
        baz()
'''

    c_code = '''
int main(int user_id, int timestamp) {
    if ((user_id ^ timestamp) == 0xDEADBEEF) {
        grant_admin();
    }
    if ((user_id & 1) == 1) {
        safe_access();
    }
}
'''

    print("Python logic expressions:", extract_logic_expressions(py_code, "python"))
    print("C logic expressions:", extract_logic_expressions(c_code, "c"))
