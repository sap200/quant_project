from gp_engine.node import (
    EXPR_INT,
    EXPR_FLOAT,
    EXPR_COL_NAME,
    EXPR_UNARY_OP,
    EXPR_BINARY_OP,
    Node,
    print_tree
)

from gp_engine.operators import ALL_OPERATORS  # if needed later

from gp_engine.crossover import restricted_crossover
from gp_engine.mutation import point_mutation


import random
from gp_engine.crossover import restricted_crossover



# =========================================================
# BASE ALPHA BUILDER (STRUCTURALLY IDENTICAL)
# =========================================================

def build_alpha(close_col="Close", vol_col="Volume", window=20, scale_const=-1):

    close = Node("column_name", close_col)
    vol = Node("column_name", vol_col)

    window_node = Node("int", window)
    const_node = Node("int", scale_const)

    ts_mean = Node(
        "binary_operator",
        "ts_mean",
        [vol, window_node]
    )

    diff = Node(
        "binary_operator",
        "minus",
        [ts_mean, close]
    )

    zscore = Node(
        "unary_operator",
        "cs_zscore",
        [diff]
    )

    root = Node(
        "binary_operator",
        "multiply",
        [const_node, zscore]
    )

    return root


# =========================================================
# TEST SCRIPT
# =========================================================

def test_crossover():

    random.seed(42)  # reproducibility

    print("\n================ PARENT 1 ================\n")
    p1 = build_alpha(close_col="Close", vol_col="Volume", window=20, scale_const=-1)
    print_tree(p1)

    print("\n================ PARENT 2 ================\n")
    p2 = build_alpha(close_col="High", vol_col="Volume", window=30, scale_const=-2)
    print_tree(p2)

    print("\n================ CROSSOVER ================\n")

    child1, child2 = restricted_crossover(p1, p2, debug=False)

    print("\n================ FINAL CHILD 1 ================\n")
    print_tree(child1)

    print("\n================ FINAL CHILD 2 ================\n")
    print_tree(child2)

    # =====================================================
    # STRUCTURE CHECK
    # =====================================================

    print("\n================ CHECKS ================\n")

    print("Parent unchanged:", p1.expr_value == "multiply")
    print("Children different objects:",
          child1 is not p1 and child2 is not p2)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    test_crossover()