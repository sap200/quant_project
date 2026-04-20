import numpy as np
import pandas as pd

from gp_engine.evaluators import evaluate
from gp_engine.node import Node
from data_collector import load_data

df = load_data()


# =========================================================
# ALPHA TREE (YOUR GP VERSION)
# =========================================================

def build_alpha(window=20):

    close = Node("column_name", "Close")
    high = Node("column_name", "Low")

    ts_mean_node = Node(
        "binary_operator",
        "ts_mean",
        [close, Node("int", window)]
    )

    diff_node = Node(
        "binary_operator",
        "minus",
        [high, ts_mean_node]
    )

    zscore_node = Node(
        "unary_operator",
        "cs_zscore",
        [diff_node]
    )

    return Node(
        "binary_operator",
        "multiply",
        [Node("int", -1), zscore_node]
    )


# =========================================================
# MANUAL (GROUND TRUTH IMPLEMENTATION)
# =========================================================

def cs_zscore_manual(x: pd.DataFrame):

    mean = x.mean(axis=1)
    std = x.std(axis=1)

    std = std.replace(0, np.nan)

    return x.sub(mean, axis=0).div(std, axis=0)


def manual_alpha(df, window=20):

    volume = df.xs("Low", axis=1, level=1)
    close = df.xs("Close", axis=1, level=1)

    ts_mean = close.rolling(window).mean()

    diff = volume - ts_mean

    z = cs_zscore_manual(diff)

    return -1 * z


# =========================================================
# COMPARISON ENGINE
# =========================================================

def compare(eval_out, manual_out):

    print("\n========== COMPARISON REPORT ==========\n")

    # align both outputs (important for rolling NaNs)
    eval_out, manual_out = eval_out.align(manual_out)

    diff = (eval_out - manual_out).abs()

    max_err = diff.max().max()
    mean_err = diff.mean().mean()

    print(f"Max absolute error : {max_err:.8f}")
    print(f"Mean absolute error: {mean_err:.8f}")

    # correlation sanity check
    corr = eval_out.corrwith(manual_out).mean()

    print(f"Avg column correlation: {corr:.6f}")

    print("\nNaN check:")
    print("Evaluator NaNs:", eval_out.isna().sum().sum())
    print("Manual NaNs   :", manual_out.isna().sum().sum())


# =========================================================
# MAIN TEST RUN
# =========================================================

def run_test(df):

    print("Running evaluator validation test...\n")

    # IMPORTANT: isolate copy
    df_copy = df.copy()

    # build tree
    tree = build_alpha(window=20)
    print(str(tree))

    # evaluate GP engine
    eval_out = evaluate(tree, df_copy)

    # manual ground truth
    manual_out = manual_alpha(df_copy, window=20)

    # compare
    compare(eval_out, manual_out)


# =========================================================
# EXECUTION (ASSUMES df ALREADY EXISTS)
# =========================================================

run_test(df)