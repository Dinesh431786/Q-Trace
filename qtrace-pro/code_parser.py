# code_parser.py
"""
Fixed version for tree-sitter compatibility with fallback to regex parsing
"""
import re
import streamlit as st

# Global flag to track if tree-sitter is working
TREE_SITTER_AVAILABLE = False
LANGUAGE_MAP = {}

def initialize_tree_sitter():
    """Initialize tree-sitter with proper error handling"""
    global TREE_SITTER_AVAILABLE, LANGUAGE_MAP
    
    try:
        from tree_sitter import Parser
        from tree_sitter_language_pack import get_language
        
        # Test if we can create a parser and get languages
        test_parser = Parser()
        python_lang = get_language("python")
        c_lang = get_language("c")
        
        # Test setting language with new API
        try:
            test_parser.language = python_lang
            api_method = "language_property"
        except AttributeError:
            # Try old API
            try:
                test_parser.set_language(python_lang)
                api_method = "set_language_method"
            except AttributeError:
                raise Exception("Neither .language nor .set_language methods work")
        
        # If we get here, tree-sitter is working
        LANGUAGE_MAP = {
            "python": python_lang,
            "c": c_lang,
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
        # Match Python if statements - more comprehensive patterns
        patterns = [
            r'if\s+(.+?):',  # Basic if
            r'elif\s+(.+?):',  # elif
            r'while\s+(.+?):',  # while loops with conditions
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Clean up the match
                clean_match = match.strip()
                if clean_match and not clean_match.startswith('#'):
                    logic_expressions.append(clean_match)
                    
    elif language == "c":
        # Match C if statements
        patterns = [
            r'if\s*\(([^)]+(?:\([^)]*\)[^)]*)*)\)',  # if statements with nested parentheses
            r'while\s*\(([^)]+(?:\([^)]*\)[^)]*)*)\)',  # while loops
            r'for\s*\([^;]*;([^;]+);[^)]*\)',  # for loop conditions
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
            for match in matches:
                clean_match = match.strip()
                if clean_match:
                    # For C, we want to include the parentheses for consistency
                    if not clean_match.startswith('('):
                        clean_match = f"({clean_match})"
                    logic_expressions.append(clean_match)
    
    return [expr.strip() for expr in logic_expressions if expr.strip()]

def extract_logic_expressions_treesitter(code, language="python"):
    """
    Tree-sitter based extraction (when available)
    """
    from tree_sitter import Parser
    
    if language not in LANGUAGE_MAP:
        raise ValueError(f"Unsupported language: {language}")
    
    parser = Parser()
    
    # Try new API first, then old API
    try:
        parser.language = LANGUAGE_MAP[language]
    except AttributeError:
        parser.set_language(LANGUAGE_MAP[language])
    
    tree = parser.parse(code.encode() if isinstance(code, str) else code)
    root = tree.root_node
    
    logic_expressions = []
    
    def walk_python(node):
        # Find if_statement, elif_clause, while_statement conditions
        if node.type in ["if_statement", "elif_clause", "while_statement"]:
            for child in node.children:
                if child.type == "test":  # Python condition node
                    expr = code[child.start_byte:child.end_byte].strip()
                    if expr:
                        logic_expressions.append(expr)
        
        for child in node.children:
            walk_python(child)
    
    def walk_c(node):
        # Find C if_statement, while_statement, for_statement conditions
        if node.type in ["if_statement", "while_statement"]:
            for child in node.children:
                if child.type == "parenthesized_expression":
                    expr = code[child.start_byte:child.end_byte].strip()
                    if expr:
                        logic_expressions.append(expr)
        elif node.type == "for_statement":
            # For statements have multiple parts, get the condition
            children = list(node.children)
            for i, child in enumerate(children):
                if child.type == ";" and i + 1 < len(children):
                    condition_child = children[i + 1]
                    if condition_child.type != ";":
                        expr = code[condition_child.start_byte:condition_child.end_byte].strip()
                        if expr and expr != ";":
                            logic_expressions.append(f"({expr})")
                    break
        
        for child in node.children:
            walk_c(child)
    
    if language == "python":
        walk_python(root)
    elif language == "c":
        walk_c(root)
    
    return [expr.strip() for expr in logic_expressions if expr.strip()]

def extract_logic_expressions(code, language="python"):
    """
    Main function to extract logic expressions with automatic fallback
    """
    if not code or not code.strip():
        return []
    
    # Initialize tree-sitter on first call
    if not TREE_SITTER_AVAILABLE and LANGUAGE_MAP == {}:
        initialize_tree_sitter()
    
    # Try tree-sitter first if available
    if TREE_SITTER_AVAILABLE:
        try:
            result = extract_logic_expressions_treesitter(code, language)
            if result:  # If we got results, return them
                return result
        except Exception as e:
            print(f"Tree-sitter parsing failed: {e}")
            print("Falling back to regex parsing...")
    
    # Fallback to regex parsing
    return extract_logic_expressions_regex(code, language)

# Initialize tree-sitter when module is imported
initialize_tree_sitter()

# --- Demo/Test block ---
if __name__ == "__main__":
    py_code = '''
def foo(a, b):
    if (a ^ b) == 42:
        bar()
    if a and b:
        baz()
    while x > 0:
        x -= 1
'''
    
    c_code = '''
int main(int user_id, int timestamp) {
    if ((user_id ^ timestamp) == 0xDEADBEEF) {
        grant_admin();
    }
    if ((user_id & 1) == 1) {
        safe_access();
    }
    while (count > 0) {
        count--;
    }
}
'''
    
    print("Testing Python extraction:")
    py_result = extract_logic_expressions(py_code, "python")
    print("Python logic expressions:", py_result)
    
    print("\nTesting C extraction:")
    c_result = extract_logic_expressions(c_code, "c")
    print("C logic expressions:", c_result)
