# code_parser.py

from tree_sitter import Language, Parser

# Load Python language
PY_LANGUAGE = Language('python')

LANGUAGE_MAP = {
    'python': PY_LANGUAGE,
    # Add more languages as needed
}

def extract_logic_expressions(code, language='python'):
    lang = LANGUAGE_MAP.get(language)
    if not lang:
        return []

    try:
        parser = Parser(lang)  # ✅ Pass language directly
        tree = parser.parse(bytes(code, 'utf-8'))
        root_node = tree.root_node

        expressions = []

        def walk(node):
            if node.type in ['binary_expression', 'parenthesized_expression']:
                expr = code[node.start_byte:index_end(node)]
                op = None
                for child in node.children:
                    if child.type in ['^', '&', '|']:
                        op = code[child.start_byte:child.end_byte]
                if op:
                    expressions.append(expr.strip())
            for child in node.children:
                walk(child)

        def index_end(n):
            return n.end_byte

        walk(root_node)
        return list(set(expressions))
    except Exception as e:
        print(f"Error parsing code: {e}")
        return []
