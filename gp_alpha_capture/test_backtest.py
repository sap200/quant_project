import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import copy

from data_collector import load_data, TICKERS
from backtest_roll import generate_rolling_windows, prepare_rolling_regression_data, train_xgboost_models, predict_with_xgboost
from gp_engine.build_alpha101 import get_seed_alphas
from gp_batch_runner import run_gp_batch
from gp_engine.individual import Individual

seed_alphas = get_seed_alphas()

def train_alpha_system(X_train, y_train, tickers, base_alphas):
    """
    PHASE 1: DISCOVERY
    Evolves GP alphas and trains XGBoost models on the training set once.
    """
    # 1. GP Evolution
    _, evolved_alpha_strs = run_gp_batch(base_alphas, X_train, y_train)
    gp_inds = [Individual(a) for a in evolved_alpha_strs]
    seed_inds = [Individual(a) for a in base_alphas]

    # 2. Train Set Evaluation
    for ind in gp_inds: ind.evaluate(X_train)
    for ind in seed_inds: ind.evaluate(X_train)
    
    train_gp_m = [ind.alpha_matrix.replace([np.inf, -np.inf], np.nan).fillna(0) for ind in gp_inds]
    train_seed_m = [ind.alpha_matrix.replace([np.inf, -np.inf], np.nan).fillna(0) for ind in seed_inds]

    # 3. XGBoost Training
    gp_data_dict = prepare_rolling_regression_data(X_train, train_gp_m, tickers, y_train, is_test=False)
    seed_data_dict = prepare_rolling_regression_data(X_train, train_seed_m, tickers, y_train, is_test=False)
    
    gp_models = train_xgboost_models(gp_data_dict, tickers)
    seed_models = train_xgboost_models(seed_data_dict, tickers)

    return (gp_models, gp_inds), (seed_models, seed_inds)

def execute_test_block(X_test_full, tickers, models_bundle, portfolio_state, horizon, fee_rate):
    """
    PHASE 2: EXECUTION
    Runs daily tracking and periodic rebalancing using pre-trained models.
    """
    (gp_models, gp_inds), (seed_models, seed_inds) = models_bundle
    cash_s, shares_s = portfolio_state['seed']
    cash_g, shares_g = portfolio_state['gp']
    shares_b = portfolio_state['bench']
    
    test_prices = X_test_full.xs('Close', axis=1, level=1)
    history = []
    
    for start_idx in range(0, len(test_prices), horizon):
        # Prediction Day (Signal Generation)
        X_test_day = X_test_full.iloc[start_idx : start_idx + 1]
        
        for ind in gp_inds: ind.evaluate(X_test_day)
        for ind in seed_inds: ind.evaluate(X_test_day)
        
        t_gp_m = [ind.alpha_matrix.replace([np.inf, -np.inf], np.nan).fillna(0) for ind in gp_inds]
        t_sd_m = [ind.alpha_matrix.replace([np.inf, -np.inf], np.nan).fillna(0) for ind in seed_inds]
        
        gp_preds = predict_with_xgboost(gp_models, prepare_rolling_regression_data(X_test_day, t_gp_m, tickers, is_test=True), tickers)
        sd_preds = predict_with_xgboost(seed_models, prepare_rolling_regression_data(X_test_day, t_sd_m, tickers, is_test=True), tickers)
        
        g_sig = gp_preds.iloc[0]
        s_sig = sd_preds.iloc[0]

        end_idx = min(start_idx + horizon, len(test_prices))
        chunk_prices = test_prices.iloc[start_idx : end_idx]
        
        for i, (date, prices) in enumerate(chunk_prices.iterrows()):
            nav_s = cash_s + sum(shares_s[t] * prices[t] for t in tickers)
            nav_g = cash_g + sum(shares_g[t] * prices[t] for t in tickers)
            nav_b = sum(shares_b[t] * prices[t] for t in tickers)
            
            if i == 0: # Rebalance Logic
                nav_s *= (1 - fee_rate)
                nav_g *= (1 - fee_rate)
                
                g_pos = g_sig[g_sig > 0]
                cash_g, shares_g = (nav_g, {t:0 for t in tickers}) if g_pos.empty else (0, {t: (nav_g/len(g_pos) if t in g_pos.index else 0)/prices[t] for t in tickers})
                
                s_pos = s_sig[s_sig > 0]
                cash_s, shares_s = (nav_s, {t:0 for t in tickers}) if s_pos.empty else (0, {t: (nav_s/len(s_pos) if t in s_pos.index else 0)/prices[t] for t in tickers})

            history.append({'Date': date, 'Seed_Strategy': nav_s, 'GP_Strategy': nav_g, 'Benchmark': nav_b, 'Is_Rebalance': (i == 0)})

        cash_s = nav_s - sum(shares_s[t] * prices[t] for t in tickers)
        cash_g = nav_g - sum(shares_g[t] * prices[t] for t in tickers)

    return history, (cash_s, shares_s), (cash_g, shares_g)

def run_triple_backtest(rolling_window_obj, tickers, initial_cash=100_000, cost_bps=6, horizon=5):
    fee_rate = cost_bps / 10000
    rw_list = list(rolling_window_obj)
    
    first_prices = rw_list[0]['X_test'].xs('Close', axis=1, level=1).iloc[0]
    bench_shares = {t: (initial_cash / len(tickers)) / first_prices[t] for t in tickers}
    
    s_state = (initial_cash, {t: 0 for t in tickers})
    g_state = (initial_cash, {t: 0 for t in tickers})
    
    full_history = []
    for r in tqdm(rw_list, desc='Rolling Windows'):
        gp_bundle, seed_bundle = train_alpha_system(r['X_train'], r['y_train'], tickers, seed_alphas)
        port_state = {'seed': s_state, 'gp': g_state, 'bench': bench_shares}
        block_hist, s_state, g_state = execute_test_block(r['X_test'], tickers, (gp_bundle, seed_bundle), port_state, horizon, fee_rate)
        full_history.extend(block_hist)

    return pd.DataFrame(full_history).drop_duplicates('Date').set_index('Date')

def print_strategy_analysis(df, initial_cash):
    print("\n" + "="*50)
    print("STRATEGY PERFORMANCE SUMMARY (RAW USD)")
    print("="*50)
    summary_data = []
    for col in ['Seed_Strategy', 'GP_Strategy', 'Benchmark']:
        final_val = df[col].iloc[-1]
        total_profit = final_val - initial_cash
        perc_return = (total_profit / initial_cash) * 100
        avg_daily_val = df[col].mean()
        summary_data.append({
            'Strategy': col,
            'Final Value': f"${final_val:,.2f}",
            'Total Profit': f"${total_profit:,.2f}",
            'Return (%)': f"{perc_return:.2f}%",
            'Mean Daily NAV': f"${avg_daily_val:,.2f}"
        })
    print(pd.DataFrame(summary_data).to_string(index=False))
    print("="*50)

def plot_triple_comparison(df):
    plt.figure(figsize=(5, 4))
    colors = ['#3498db', '#2ecc71', '#95a5a6']
    labels = ['Seed_Strategy', 'GP_Strategy', 'Benchmark']
    
    for col, color in zip(labels, colors):
        ls = '--' if col == 'Benchmark' else '-'
        plt.plot(df.index, df[col], label=col, color=color, linestyle=ls, linewidth=1.5)

    plt.ylim(df[['Seed_Strategy', 'GP_Strategy', 'Benchmark']].min().min() * 0.98, 
             df[['Seed_Strategy', 'GP_Strategy', 'Benchmark']].max().max() * 1.02)
    plt.gca().get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    plt.title('Daily Portfolio NAV', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=8)
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    initial_cap = 100_000
    df_data = load_data()
    results = run_triple_backtest(generate_rolling_windows(df_data), TICKERS, initial_cash=initial_cap)
    print_strategy_analysis(results, initial_cap)
    plot_triple_comparison(results)