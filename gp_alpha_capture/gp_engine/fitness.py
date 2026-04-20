import numpy as np
import pandas as pd


# =========================================================
# SAFE CORRELATION (VECTORIZED CORE)
# =========================================================

def safe_corr_matrix(alpha_df, returns_df):
    """
    Returns:
    - daily pearson IC series (vectorized)
    - daily spearman IC series (vectorized)
    """

    # -------------------------
    # CLEAN INPUTS
    # -------------------------
    alpha_df = alpha_df.replace([np.inf, -np.inf], np.nan).fillna(0)
    returns_df = returns_df.replace([np.inf, -np.inf], np.nan).fillna(0)

    # -------------------------
    # REMOVE ZERO VARIANCE ROWS
    # -------------------------
    alpha_std = alpha_df.std(axis=1)
    ret_std = returns_df.std(axis=1)

    valid = (alpha_std != 0) & (ret_std != 0)

    alpha_df = alpha_df.loc[valid]
    returns_df = returns_df.loc[valid]

    # =========================================================
    # PEARSON IC (VECTORISED ROW-WISE CORRELATION)
    # =========================================================
    alpha_centered = alpha_df.sub(alpha_df.mean(axis=1), axis=0)
    returns_centered = returns_df.sub(returns_df.mean(axis=1), axis=0)

    numerator = (alpha_centered * returns_centered).sum(axis=1)

    denominator = (
        np.sqrt((alpha_centered ** 2).sum(axis=1)) *
        np.sqrt((returns_centered ** 2).sum(axis=1))
    )

    ic_series = numerator / denominator.replace(0, np.nan)

    # =========================================================
    # SPEARMAN IC (rank transform then same logic)
    # =========================================================
    alpha_rank = alpha_df.rank(axis=1)
    returns_rank = returns_df.rank(axis=1)

    a_centered = alpha_rank.sub(alpha_rank.mean(axis=1), axis=0)
    r_centered = returns_rank.sub(returns_rank.mean(axis=1), axis=0)

    numerator_r = (a_centered * r_centered).sum(axis=1)

    denominator_r = (
        np.sqrt((a_centered ** 2).sum(axis=1)) *
        np.sqrt((r_centered ** 2).sum(axis=1))
    )

    rank_ic_series = numerator_r / denominator_r.replace(0, np.nan)

    return ic_series.dropna(), rank_ic_series.dropna()


# =========================================================
# AGGREGATION METRICS
# =========================================================

def compute_metrics(series):
    if len(series) == 0:
        return -np.inf, -np.inf

    mean = series.mean()
    std = series.std()

    if std == 0 or np.isnan(std):
        return mean, -np.inf

    return mean, mean / std


# =========================================================
# MAIN FITNESS FUNCTION
# =========================================================

def compute_fitness(individual, returns_df):
    """
    Fitness = RankICIR
    Also computes IC, ICIR, RankIC, RankICIR
    """

    alpha = individual.alpha_matrix

    # -------------------------
    # INVALID CHECK
    # -------------------------
    if alpha is None:
        individual.ic = -np.inf
        individual.icir = -np.inf
        individual.rank_ic = -np.inf
        individual.rank_icir = -np.inf
        return -np.inf

    # -------------------------
    # VECTORISED IC COMPUTATION
    # -------------------------
    ic_series, rank_ic_series = safe_corr_matrix(alpha, returns_df)

    # -------------------------
    # METRICS
    # -------------------------
    ic_mean, icir = compute_metrics(ic_series)
    rank_ic_mean, rank_icir = compute_metrics(rank_ic_series)

    # -------------------------
    # STORE IN INDIVIDUAL
    # -------------------------
    individual.ic = ic_mean
    individual.icir = icir
    individual.rank_ic = rank_ic_mean
    individual.rank_icir = rank_icir

    # -------------------------
    # FITNESS
    # -------------------------
    return rank_icir