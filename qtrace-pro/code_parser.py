# code_parser.py
import sys
print(f"Python version: {sys.version}")

try:
    from tree_sitter import Parser
    print(f"tree_sitter imported successfully")
    print(f"Parser attributes: {dir(Parser())}")
except ImportError as e:
    print(f"Failed to import tree_sitter: {e}")

try:
    from tree_sitter_language_pack import get_language
    print("tree_sitter_language_pack imported successfully")
except ImportError as e:
    print(f"Failed to import tree_sitter_language_pack: {e}")

LANGUAGE_MAP = {}

def safe_get_language(lang_name):
    """Safely get language with error handling"""
    try:
        return get_language(lang_name)
    except Exception as e:
        print(f"Error getting language {lang_name}: {e}")
        return None

# Build language map with error handling
try:
    python_lang = safe_get_language("python")
    c_lang = safe_get_language("c")
    
    if python_lang:
        LANGUAGE_MAP["python"] = python_lang
    if c_lang:
        LANGUAGE_MAP["c"] = c_lang
        
    print(f"Available languages: {list(LANGUAGE_MAP.keys())}")
except Exception as e:
    print(f"Error building language map: {e}")

def extract_logic_expressions(code, language="python"):
    """
    Extract logic/conditional expressions from code using Tree-sitter AST.
    Supports: Python, C. Returns a list of expressions as strings.
    """
    print(f"Starting extraction for language: {language}")
    
    if language not in LANGUAGE_MAP:
        available = list(LANGUAGE_MAP.keys())
        raise ValueError(f"Unsupported language: {language}. Available: {available}")
    
    try:
        parser = Parser()
        print(f"Parser created: {type(parser)}")
        print(f"Parser methods: {[m for m in dir(parser) if not m.startswith('_')]}")
        
        # Try different ways to set language
        lang_obj = LANGUAGE_MAP[language]
        print(f"Language object: {type(lang_obj)}")
        
        # Method 1: Try .language property
        try:
            parser.language = lang_obj
            print("Successfully set language using .language property")
        except AttributeError:
            print("Failed to set language using .language property")
            # Method 2: Try .set_language method (older API)
            try:
                parser.set_language(lang_obj)
                print("Successfully set language using .set_language method")
            except AttributeError:
                raise AttributeError("Neither .language nor .set_language methods are available")
        
        # Parse the code
        code_bytes = code.encode() if isinstance(code, str) else code
        tree = parser.parse(code_bytes)
        print(f"Tree parsed successfully: {type(tree)}")
        
        root = tree.root_node
        print(f"Root node obtained: {type(root)}")
        
    except Exception as e:
        print(f"Error in parser setup: {e}")
        raise
    
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
    
    try:
        if language == "python":
            walk_python(root)
        elif language == "c":
            walk_c(root)
        
        print(f"Found {len(logic_expressions)} logic expressions")
        return [expr.strip() for expr in logic_expressions]
        
    except Exception as e:
        print(f"Error during AST walking: {e}")
        raise

# --- Demo/Test block ---
if __name__ == "__main__":
    py_code = '''
def foo(a, b):
    if (a ^ b) == 42:
        bar()
    if a and b:
        baz()
'''
    
    try:
        print("Testing Python code extraction...")
        result = extract_logic_expressions(py_code, "python")
        print("Python logic expressions:", result)
    except Exception as e:
        print(f"Test failed: {e}")
