import pandas as pd
import numpy as np
from .operators import (
    CS_OPERATORS,
    TS_OPERATORS,
    ARITH_OPERATORS,
    CMP_OPERATORS,
    PAIRWISE_OPERATORS,
    COND_OPERATORS,
    ALL_OPERATORS,
    OP_ARITY
)

from gp_engine.node import (
    EXPR_INT,
    EXPR_FLOAT,
    EXPR_COL_NAME
)


def safe_clean(df):
    return df.replace([np.inf, -np.inf], np.nan).fillna(0)


# =========================================================
# FEATURE RESOLUTION
# =========================================================

def get_feature_matrix(df, feature):
    return df.xs(feature, axis=1, level=1)


# =========================================================
# OPERATOR CLASSIFICATION
# =========================================================

def get_op_group(op):

    if op in CS_OPERATORS:
        return "CS"

    if op in TS_OPERATORS:
        return "TS"

    if op in ARITH_OPERATORS:
        return "ARITH"

    if op in CMP_OPERATORS:
        return "CMP"

    if op in PAIRWISE_OPERATORS:
        return "PAIRWISE"

    if op in COND_OPERATORS:
        return "COND"

    return None


# =========================================================
# MAIN EVALUATOR
# =========================================================

def evaluate(node, df, tickers=None):

    if node is None:
        raise ValueError("Node is None")

    # -------------------------
    # LEAF NODES
    # -------------------------
    if node.expr_type == EXPR_INT:
        return node.expr_value

    if node.expr_type == EXPR_FLOAT:
        return node.expr_value

    if node.expr_type == EXPR_COL_NAME:
        return get_feature_matrix(df, node.expr_value)

    # -------------------------
    # RECURSIVE EVAL
    # -------------------------
    args = [evaluate(c, df, tickers) for c in node.children]

    op = node.expr_value

    if op not in ALL_OPERATORS:
        raise ValueError(f"Unknown operator: {op}")

    func = ALL_OPERATORS[op]

    expected = OP_ARITY.get(op, None)

    if expected is not None and len(args) != expected:
        raise ValueError(
            f"{op} expects {expected} args, got {len(args)}"
        )

    group = get_op_group(op)

    # =====================================================
    # DISPATCH BY OPERATOR GROUP
    # =====================================================

    # -------------------------
    # CS OPERATORS (cross-sectional)
    # -------------------------
    if group == "CS":
        return func(args[0])

    # -------------------------
    # TS OPERATORS
    # -------------------------
    if group == "TS":
        df_in, window = args
        return df_in.apply(lambda col: func(col, window), axis=0)

    # -------------------------
    # ARITHMETIC
    # -------------------------
    if group == "ARITH":
        return func(args[0], args[1])

    # -------------------------
    # COMPARISON
    # -------------------------
    if group == "CMP":
        return func(args[0], args[1])

    # -------------------------
    # PAIRWISE
    # -------------------------
    if group == "PAIRWISE":
        x, y, window = args
        return func(x, y, window)

    # -------------------------
    # CONDITIONAL
    # -------------------------
    if group == "COND":
        cond, x, y = args
        return func(cond, x, y)

    # -------------------------
    # FALLBACK
    # -------------------------
    result = func(*args)
    
    if isinstance(result, pd.DataFrame):
        result = safe_clean(result)
    
    return result