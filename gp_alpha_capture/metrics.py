import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tabulate import tabulate

from gp_engine.evaluators import evaluate
from gp_engine.fitness import compute_fitness
from gp_engine.individual import Individual
from gp_engine.node import tree_to_formula


# =========================================================
# SAFE CORRELATION
# =========================================================

def safe_corr(a, b):
    mask = a.notna() & b.notna()

    if mask.sum() < 2:
        return np.nan

    a = a[mask]
    b = b[mask]

    if a.std() == 0 or b.std() == 0:
        return np.nan

    return np.corrcoef(a, b)[0, 1]


# =========================================================
# ALPHA SIMILARITY (TIME-AVERAGED IC)
# =========================================================

def alpha_similarity(alpha1, alpha2):

    assert alpha1.shape == alpha2.shape

    vals = []

    for t in range(len(alpha1)):
        c = safe_corr(alpha1.iloc[t], alpha2.iloc[t])
        if not np.isnan(c):
            vals.append(c)

    if len(vals) == 0:
        return 0.0

    return np.mean(vals)


# =========================================================
# EVALUATE INDIVIDUAL
# =========================================================

def eval_ind(tree, X, y):

    ind = Individual(tree)

    ind.alpha_matrix = evaluate(tree, X)
    compute_fitness(ind, y)

    return ind


# =========================================================
# MAIN COMPARISON FUNCTION
# =========================================================

def compare_alphas(seeds, evolved, X_train, X_test, y_train, y_test):
    train_rows = []
    test_rows = []
    train_corrs = []
    test_corrs = []
    formulas = []

    for i, (seed_node, evolved_node) in enumerate(zip(seeds, evolved)):
        # --- 1. WRAP NODES INTO INDIVIDUALS ---
        ind_s_train = Individual(seed_node)
        ind_e_train = Individual(evolved_node)

        # --- 2. EVALUATE & FITNESS (TRAIN) ---
        ind_s_train.evaluate(X_train)
        ind_e_train.evaluate(X_train)
        compute_fitness(ind_s_train, y_train)
        compute_fitness(ind_e_train, y_train)

        t_corr = alpha_similarity(ind_s_train.alpha_matrix, ind_e_train.alpha_matrix)
        train_corrs.append(t_corr)

        train_rows.append([
            i, ind_s_train.ic, ind_e_train.ic, ind_s_train.rank_ic, ind_e_train.rank_ic,
            ind_s_train.icir, ind_e_train.icir, ind_s_train.rank_icir, ind_e_train.rank_icir, t_corr
        ])

        # --- 3. EVALUATE & FITNESS (TEST) ---
        ind_s_test = Individual(seed_node)
        ind_e_test = Individual(evolved_node)
        ind_s_test.evaluate(X_test)
        ind_e_test.evaluate(X_test)
        compute_fitness(ind_s_test, y_test)
        compute_fitness(ind_e_test, y_test)

        te_corr = alpha_similarity(ind_s_test.alpha_matrix, ind_e_test.alpha_matrix)
        test_corrs.append(te_corr)

        test_rows.append([
            i, ind_s_test.ic, ind_e_test.ic, ind_s_test.rank_ic, ind_e_test.rank_ic,
            ind_s_test.icir, ind_e_test.icir, ind_s_test.rank_icir, ind_e_test.rank_icir, te_corr
        ])
        
        formulas.append({
            'Pair': i,
            'Seed Formula': tree_to_formula(seed_node),
            'GP Formula': tree_to_formula(evolved_node),
        })

    # --- 4. CALCULATE AVERAGE ROWS ---
    def get_mean_row(data_rows):
        # Slice from index 1 onwards to skip the 'Pair' ID, then calculate mean
        arr = np.array(data_rows)
        means = np.mean(arr[:, 1:], axis=0)
        return ["AVERAGE"] + means.tolist()

    train_rows.append(get_mean_row(train_rows))
    test_rows.append(get_mean_row(test_rows))

    # Header Definition
    headers = [
        "Pair", "Seed IC", "GP IC", "S. RankIC", "G. RankIC",
        "Seed ICIR", "GP ICIR", "S. RankICIR", "G. RankICIR", "corr"
    ]

    # --- PRINTING TABLES ---
    print("\n" + "╔" + "═"*40 + " TRAIN PERFORMANCE " + "═"*41 + "╗")
    print(tabulate(train_rows, headers=headers, tablefmt="fancy_grid", floatfmt=".4f"))

    print("\n" + "╔" + "═"*40 + " TEST PERFORMANCE " + "═"*42 + "╗")
    print(tabulate(test_rows, headers=headers, tablefmt="fancy_grid", floatfmt=".4f"))

    print("\n>>> EVOLVED FORMULAS")
    print(tabulate(formulas, headers='keys', tablefmt="simple"))

    # --- SUMMARY METRICS ---
    print("\n" + "="*25 + " SUMMARY STATISTICS " + "="*25)
    
    abs_mean_train_corr = np.mean(np.abs(train_corrs))
    abs_mean_test_corr = np.mean(np.abs(test_corrs))
    
    print(f"Mean Absolute Correlation (Train): {abs_mean_train_corr:.4f}")
    print(f"Mean Absolute Correlation (Test):  {abs_mean_test_corr:.4f}")
    
    # We take the mean G. RankIC from the TEST average row (index 4)
    avg_test_rank_ic = test_rows[-1][4]
    print(f"Aggregate Out-of-Sample Rank IC:   {avg_test_rank_ic:.4f}")

    # Interpretation
    if abs_mean_test_corr < 0.3:
        print("Insight: Alphas are largely 'Grey' (Orthogonal) - unique information.")
    elif abs_mean_test_corr > 0.7:
        print("Insight: Alphas are 'Warm' - high similarity to seed.")

    plot_heatmap(train_corrs, test_corrs)

# =========================================================
# HEATMAP
# =========================================================

def plot_heatmap(train_corrs, test_corrs):

    df = pd.DataFrame({
        "Train": train_corrs,
        "Test": test_corrs
    })

    plt.figure(figsize=(4, 3))

    sns.heatmap(
        df.T,
        annot=True,
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1
    )

    plt.title("Seed vs GP Alpha Similarity")
    plt.tight_layout()
    plt.savefig('./data/correlation.png')
    plt.close()
    print('\n')
    print("Figure saved to ./data/correlation.png")