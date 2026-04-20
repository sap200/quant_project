EXPR_UNARY_OP = "unary_operator"
EXPR_BINARY_OP = "binary_operator"
EXPR_TERNARY_OP = "ternary_operator"
EXPR_INT = "int"
EXPR_FLOAT = "float"
EXPR_COL_NAME = "column_name"

class Node:
    def __init__(self, expr_type, expr_value, children=None):
        self.expr_type = expr_type      # "operator", "feature", "constant"
        self.expr_value = expr_value              # operator name OR column name OR number
        self.children = children or []  # list of child nodes
    

def print_tree(node, indent="", is_last=True):
    if node is None:
        return

    # branch prefix
    prefix = indent + ("└── " if is_last else "├── ")

    # print current node
    print(prefix + str(node.expr_value) + ":" + str(node.expr_type))

    # update indentation for children
    new_indent = indent + ("    " if is_last else "│   ")

    # print children
    for i, child in enumerate(node.children):
        is_last_child = (i == len(node.children) - 1)
        print_tree(child, new_indent, is_last_child)
        
def trees_equal(n1, n2):
    """
    Recursively checks if two trees are structurally identical
    """

    if n1 is None and n2 is None:
        return True

    if n1 is None or n2 is None:
        return False

    # compare node type + value
    if n1.expr_type != n2.expr_type:
        return False

    if n1.expr_value != n2.expr_value:
        return False

    # compare children length
    if len(n1.children) != len(n2.children):
        return False

    # recursive check
    for c1, c2 in zip(n1.children, n2.children):
        if not trees_equal(c1, c2):
            return False

    return True

def tree_to_formula(node):
    # Base Case: Terminal/Operand
    if not hasattr(node, 'children') or not node.children:
        return str(node.expr_value)

    # 1. Recursive step: Convert all children first (Left to Right)
    child_exprs = [tree_to_formula(child) for child in node.children]

    # 2. Configuration for Translation
    math_map = {
        'plus': '+',
        'minus': '-',
        'multiply': '*',
        'divide': '/',
        'lt': '<',
        'gt': '>',
        'eq': '=',
        'lte': '<=',
        'gte': '>=',
        'signed_power': '^'
    }
    
    op = str(node.expr_value).lower()

    # --- Case A: Standard Math (Infix) ---
    if op in math_map:
        symbol = math_map[op]
        # Joins n-ary arguments: (a * b * c)
        joined = f" {symbol} ".join(child_exprs)
        return f"({joined})"

    # --- Case B: Unary Negation ---
    elif op == 'neg':
        return f"(-{child_exprs[0]})"

    # --- Case C: Java Ternary Operator (condition ? then : else) ---
    elif op == 'if_else' and len(child_exprs) == 3:
        # Format: (condition ? true_branch : false_branch)
        return f"({child_exprs[0]} ? {child_exprs[1]} : {child_exprs[2]})"

    # --- Case D: Generic Function ---
    else:
        args_string = ", ".join(child_exprs)
        return f"{node.expr_value}({args_string})"