from data_collector import *
import statsmodels.api as sm
import pandas as pd
from tabulate import tabulate

'''
Download returns for: 
IWM (Russell 2000 small-cap ETF)  - Small Cap
and IWD (iShares Value ETF) - Value

'''

def get_SMB_and_HML_proxies(market_log_return):
    # Load data
    iwd_data = load_IWD_data_value() # value stock
    iwm_data = load_IWM_data_small_cap() # small cap stock
    
    
    # Load returns
    iwd_log_return = calculate_log_returns(iwd_data)
    iwm_log_return = calculate_log_returns(iwm_data)
    
    # calculate HMB AND SMB proxies
    
    # small minus big
    # use small cap stocks IWM
    SMB_proxy = iwm_log_return - market_log_return
    
    # HML high minus low
    # use value stock 
    HML_proxy = iwd_log_return - market_log_return
    return SMB_proxy, HML_proxy

def multi_factor_regression(excess_returns):
    input_cols = ['MARKET', 'SMB', 'HML']
    X = sm.add_constant(excess_returns[input_cols])
    
    results = []
    resid_vars = []
    
    for col in excess_returns.columns:
        if col in input_cols:
            continue
        
        y = excess_returns[col]
        result = sm.OLS(y, X).fit()
        
        alpha = result.params["const"]
        alpha_pvalue = result.pvalues["const"]
        
        beta_market = result.params["MARKET"]
        beta_market_pvalue = result.pvalues["MARKET"]
        
        beta_smb = result.params['SMB']
        beta_smb_pvalue = result.pvalues['SMB']
        
        beta_hml = result.params['HML']
        beta_hml_pvalue = result.pvalues['HML']
        
        results.append({
            'stock': col,
            'alpha': alpha,
            'alpha_pvalue': alpha_pvalue,
            'beta_market': beta_market,
            'beta_market_pvalue': beta_market_pvalue,
            'beta_smb': beta_smb,
            'beta_smb_pvalue': beta_smb_pvalue,
            'beta_hml': beta_hml,
            'beta_hml_pvalue': beta_hml_pvalue,
            'r2': result.rsquared
            })
        
        resid_vars.append({
            'stock': col,
            'residual_variance': result.resid.var().item()
            })
    
    return pd.DataFrame(results), resid_vars

def merge_stock_market_SMB_HML(stock_excess, market_excess, SMB_proxy, HML_proxy):
    ndf = pd.concat([stock_excess, market_excess], axis=1)
    ndf.rename(columns={'Close':'MARKET'}, inplace=True)
    ndf = pd.concat([ndf, SMB_proxy], axis=1)
    ndf.rename(columns={'Close': 'SMB'}, inplace=True)
    ndf = pd.concat([ndf, HML_proxy], axis=1)
    ndf.rename(columns={'Close': 'HML'}, inplace=True)
    return ndf

def print_result_df(result):
    print(tabulate(result, headers='keys', tablefmt='fancy_grid', showindex=False))

def return_decomposition(df, factor_means):
    df = df.copy()

    df["market_contrib"] = df["beta_market"] * factor_means["MARKET"]
    df["smb_contrib"] = df["beta_smb"] * factor_means["SMB"]
    df["hml_contrib"] = df["beta_hml"] * factor_means["HML"]

    df["expected_return"] = (
        df["alpha"]
        + df["market_contrib"]
        + df["smb_contrib"]
        + df["hml_contrib"]
    )

    return df[["stock", "alpha","market_contrib", "smb_contrib", "hml_contrib", "expected_return"]]

