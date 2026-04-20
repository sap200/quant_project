import random
import copy

from .mutation_config import *
from .node import (
    EXPR_INT,
    EXPR_FLOAT,
    EXPR_COL_NAME,
    EXPR_UNARY_OP,
    EXPR_BINARY_OP,
    EXPR_TERNARY_OP
)


# =========================================================
# GROUP RESOLUTION
# =========================================================

def get_group(op):
    for g, ops in GROUP_MAP.items():
        if op in ops:
            return g
    return None


# =========================================================
# PURE RE-SAMPLING HELPERS
# =========================================================

def sample_int():
    return random.randint(*INT_RANGE)

def sample_nonzero_float(eps=1e-1):
    while True:
        x = random.uniform(*FLOAT_RANGE)
        if abs(x) > eps:
            return x
        
# =========================================================
# NODE MUTATORS
# =========================================================

def mutate_constant(node):
    if node.expr_type == EXPR_INT:
        node.expr_value = sample_int()

    elif node.expr_type == EXPR_FLOAT:
        node.expr_value = sample_nonzero_float()

    return node


def mutate_column(node):
    node.expr_value = random.choice(COL_LIST)
    return node


def mutate_operator(node):
    op = node.expr_value
    group = get_group(op)

    if group is None:
        return node

    node.expr_value = random.choice(GROUP_MAP[group])
    return node


# =========================================================
# APPLY MUTATION TO A SINGLE NODE
# =========================================================

def mutate_node(node):

    if node.expr_type in [EXPR_INT, EXPR_FLOAT]:
        return mutate_constant(node)

    if node.expr_type == EXPR_COL_NAME:
        return mutate_column(node)

    if node.expr_type in [EXPR_UNARY_OP, EXPR_BINARY_OP, EXPR_TERNARY_OP]:
        return mutate_operator(node)

    return node


# =========================================================
# TREE TRAVERSAL
# =========================================================

def get_all_nodes(node):
    nodes = []

    def dfs(n):
        if n is None:
            return
        nodes.append(n)
        for c in n.children:
            dfs(c)

    dfs(node)
    return nodes


# =========================================================
# POINT MUTATION (COPY-BASED, SAFE GP)
# =========================================================

def point_mutation(tree):
    """
    Returns a NEW mutated tree.
    Parent tree remains unchanged.
    """

    new_tree = copy.deepcopy(tree)

    nodes = get_all_nodes(new_tree)

    if not nodes:
        return new_tree

    node = random.choice(nodes)

    mutate_node(node)

    return new_tree