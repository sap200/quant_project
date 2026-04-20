import copy

from gp_engine.node import (
    EXPR_INT,
    EXPR_FLOAT,
    EXPR_COL_NAME,
    EXPR_UNARY_OP,
    EXPR_BINARY_OP,
    Node,
    print_tree
)

from gp_engine.mutation import point_mutation


# =========================================================
# BUILD SIMPLE ALPHA TREE (TEST CASE)
# =========================================================

def build_alpha(window=20):

    # -------------------------
    # LEAF NODES
    # -------------------------
    close = Node(EXPR_COL_NAME, "Close")
    volume = Node(EXPR_COL_NAME, "Volume")

    window_node = Node(EXPR_INT, window)
    neg_one = Node(EXPR_INT, -1)

    # -------------------------
    # TS MEAN (Volume, window)
    # -------------------------
    ts_mean_node = Node(
        EXPR_BINARY_OP,
        "ts_mean",
        [volume, window_node]
    )

    # -------------------------
    # DIFFERENCE: ts_mean - Close
    # -------------------------
    diff_node = Node(
        EXPR_BINARY_OP,
        "minus",
        [ts_mean_node, close]
    )

    # -------------------------
    # CROSS-SECTIONAL ZSCORE
    # -------------------------
    zscore_node = Node(
        EXPR_UNARY_OP,
        "cs_zscore",
        [diff_node]
    )

    # -------------------------
    # FINAL ALPHA: -1 * signal
    # -------------------------
    root = Node(
        EXPR_BINARY_OP,
        "multiply",
        [neg_one, zscore_node]
    )

    return root


# =========================================================
# TEST MUTATION
# =========================================================

def test_mutation():
    print("\n===== BUILD ORIGINAL TREE =====\n")
    tree = build_alpha()

    print_tree(tree)

    # keep original reference for comparison
    original_root_id = id(tree)

    print("\n===== APPLY MUTATION =====\n")

    mutated = point_mutation(tree)

    print_tree(mutated)

    # =====================================================
    # CHECKS
    # =====================================================

    print("\n===== CHECKS =====\n")

    print("Root changed object?", id(mutated) != original_root_id)

    print("Root value original:", original_root_id)
    print("Root value mutated :", id(mutated))

    print("\nDONE")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    test_mutation()