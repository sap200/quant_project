from gp_engine.node import Node


# =========================================================
# ALPHA 1 (Alpha101-style momentum reversal hybrid)
# Equivalent form:
# rank(- (ts_mean(close, 5) - ts_mean(close, 20)))
# =========================================================

def build_alpha_1():

    close = Node("column_name", "Close")

    ts_mean_5 = Node(
        "binary_operator",
        "ts_mean",
        [close, Node("int", 5)]
    )

    ts_mean_20 = Node(
        "binary_operator",
        "ts_mean",
        [close, Node("int", 20)]
    )

    diff = Node(
        "binary_operator",
        "minus",
        [ts_mean_5, ts_mean_20]
    )

    neg = Node(
        "unary_operator",
        "neg",
        [diff]
    )

    return Node(
        "unary_operator",
        "rank",
        [neg]
    )


# =========================================================
# ALPHA 2 (Alpha101-style volatility-normalized trend)
# Equivalent form:
# rank( ts_mean(close, 20) / ts_stddev(close, 20) )
# =========================================================

def build_alpha_2():

    close = Node("column_name", "Close")

    ts_mean_20 = Node(
        "binary_operator",
        "ts_mean",
        [close, Node("int", 20)]
    )

    ts_std_20 = Node(
        "binary_operator",
        "ts_stddev",
        [close, Node("int", 20)]
    )

    vol_adjusted = Node(
        "binary_operator",
        "divide",
        [ts_mean_20, ts_std_20]
    )

    return Node(
        "unary_operator",
        "rank",
        [vol_adjusted]
    )

def build_alpha_3():

    close = Node("column_name", "Close")

    # delta(close, 1)
    delta_1 = Node(
        "binary_operator",
        "delta",
        [close, Node("int", 1)]
    )

    # ts_rank(delta(close,1), 5)
    ts_rank_delta = Node(
        "binary_operator",
        "ts_rank",
        [delta_1, Node("int", 5)]
    )

    # cs_rank(-close)
    neg_close = Node(
        "unary_operator",
        "neg",
        [close]
    )

    cs_rank_neg = Node(
        "unary_operator",
        "rank",
        [neg_close]
    )

    # interaction
    interaction = Node(
        "binary_operator",
        "multiply",
        [ts_rank_delta, cs_rank_neg]
    )

    # final ranking (cross-sectional stabilization)
    return Node(
        "unary_operator",
        "rank",
        [interaction]
    )





def build_alpha_conditional():

    close = Node("column_name", "Close")
    returns = Node("column_name", "Returns")  # assume you have this feature

    # stddev(returns, 20)
    ret_std_20 = Node(
        "binary_operator",
        "ts_stddev",
        [returns, Node("int", 20)]
    )

    # condition: returns < 0
    cond = Node(
        "binary_operator",
        "lt",
        [returns, Node("float", 0)]
    )

    # (returns < 0 ? stddev(returns,20) : close)
    conditional = Node(
        "ternary_operator",
        "if_else",
        [cond, ret_std_20, close]
    )

    # signed_power(..., 2)
    powered = Node(
        "binary_operator",
        "signed_power",
        [conditional, Node("int", 2)]
    )

    # ts_argmax(powered, 5)
    ts_argmax_node = Node(
        "binary_operator",
        "ts_argmax",
        [powered, Node("int", 5)]
    )

    # rank(...)
    ranked = Node(
        "unary_operator",
        "rank",
        [ts_argmax_node]
    )

    # final shift: -0.5
    return Node(
        "binary_operator",
        "minus",
        [ranked, Node("float", 0.5)]
    )




# =========================================================
# OPTIONAL: seed list
# =========================================================

def get_seed_alphas():
    return [
        build_alpha_1(),
        build_alpha_2(),
        build_alpha_3(),
        build_alpha_conditional()
    ]