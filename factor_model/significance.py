import matplotlib.pyplot as plt
from scipy.stats import skew, kurtosis

# Now we do significance analysis
def is_significant(p_value, threshold=0.05):
    return p_value < threshold

def interpret_r_squared(r_squared):
    explaination = '''R-square measures how much of stock's return is explained by the market movement.
    If strong - stock's returns are strongly influenced by market returns.
    If moderate - stock's returns are moderatly influenced by market returns and the other returns are idiosyncratic returns of the stock.
    If weak - stock is weakly influenced by market, and usually market doesn't impact stock's return that much. Most of its returns are idosyncractic.
    '''
    
    if r_squared > 0.7:
        return "Strong", explaination
    elif r_squared >=0.4:
        return "Moderate", explaination
    else:
        return "Weak", explaination

def information_ratio(alpha, resid_std):
    # if we have high resid std more noise
    # alpha/resid_std more the better meaning
    explaination = '''alpha/resid_std is information ratio, higher it is the better the quality of alpha. It measures the quality of alpha
    
    “How much signal (alpha) do I get per unit of noise?”
    
    | IR value  | Meaning              |
    | --------- | -------------------- |
    | > 1.0     | very strong strategy |
    | 0.5 – 1.0 | decent               |
    | 0 – 0.5   | weak / noisy         |
    | < 0       | bad strategy         |
    
    For CAPM
    
    | Scenario                       | Meaning               |
    | ------------------------------ | --------------------- |
    | high alpha, low residual noise | strong pricing signal |
    | high alpha, high noise         | unreliable alpha      |
    | low alpha                      | no edge               |
    '''
    return alpha/resid_std, explaination


def compute_moments(residual):
    sk = skew(residual)
    ku = kurtosis(residual)
    
    return sk, ku


def plot_residual(residual, stock_name, ax=None):

    if ax is None:
        fig, ax = plt.subplots()

    ax.plot(residual.index, residual, linewidth=0.5)
    ax.set_title(stock_name)
    ax.axhline(0, color="black", linewidth=1)
    ax.tick_params(axis='x', rotation=90)
    ax.grid(True)

    return ax

def plot_residual_hist(residual, stock_name, ax=None, sk=None, ku=None):

    if ax is None:
        fig, ax = plt.subplots()

    label = None
    if sk is not None and ku is not None:
        label = f"skew={sk:.2f}, kurt={ku:.2f}"

    ax.hist(residual.values, bins=40, alpha=0.7, label=label)

    ax.set_title(f"{stock_name} Residual Histogram")
    ax.grid(True)

    if label:
        ax.legend()

    return ax

def plot_residual_vs_fitted(residual, fitted, stock_name, ax=None):

    if ax is None:
        fig, ax = plt.subplots()

    ax.scatter(fitted, residual, alpha=0.5, s=10)

    ax.axhline(0, color="black", linewidth=1)
    ax.set_title(f"{stock_name} Residuals vs Fitted")
    ax.set_xlabel("Fitted values")
    ax.set_ylabel("Residuals")
    ax.grid(True)

    return ax


def analyse_residuals(residual_dict, fitted_dict, filename="./data/residual_diagnostics.png"):

    stocks = list(residual_dict.keys())
    n = len(stocks)

    fig, axes = plt.subplots(nrows=n, ncols=3, figsize=(15, 4*n))

    if n == 1:
        axes = [axes]

    for i, name in enumerate(stocks):

        residual = residual_dict[name]
        fitted = fitted_dict[name]

        # --- 1. time series (use helper)
        plot_residual(residual, name, ax=axes[i][0])

        # --- 2. moments (computed ONCE)
        sk, ku = compute_moments(residual.values)

        # histogram WITH legend stats
        plot_residual_hist(
            residual,
            name,
            ax=axes[i][1],
            sk=sk,
            ku=ku
        )

        # --- 3. residual vs fitted (use helper)
        plot_residual_vs_fitted(
            residual,
            fitted,
            name,
            ax=axes[i][2]
        )

    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return fig

def summary_table(results, residuals):
    for _, row in results.iterrows():
        details = row['stock']
        ir, ex1 = information_ratio(row['alpha'], row['resid_std'])
        irsquared, ex2 = interpret_r_squared(row['r2'])
        sig = is_significant(row['alpha_pvalue'])
        print(details)
        print("IR: ", ir)
        print("-"*100)
        print(ex1)
        print("R2 interpretation: ", irsquared)
        print("-"*100)
        print(ex2)
        print("-"*100)
        print("is significant alpha: ", sig)
        print("="*120)
        
        
        