import numpy as np
import pandas as pd

OPERATOR_TYPE = {
    # UNARY
    "rank": "CS",
    "cs_zscore": "CS",
    "log": "TS_OR_CS",
    "neg": "TS_OR_CS",

    # TS INT
    "ts_sum": "TS",
    "ts_sma": "TS",
    "ts_stddev": "TS",
    "ts_rank": "TS",
    "ts_mean": "TS",
    "ts_min": "TS",
    "ts_max": "TS",
    "ts_argmax": "TS",
    "ts_argmin": "TS",
    "product": "TS",
    "delta": "TS",
    "delay": "TS",
    "scale": "TS",

    # FLOAT OPS
    "minus": "ARITH",
    "plus": "ARITH",
    "multiply": "ARITH",
    "divide": "ARITH",
    "signed_power": "ARITH",

    # COMPARISON
    "gt": "CMP",
    "lt": "CMP",
    "gte": "CMP",
    "lte": "CMP",
    "eq": "CMP",

    # PAIRWISE
    "correlation": "PAIRWISE",
    "covariance": "PAIRWISE",

    # CONDITIONAL
    "if_else": "COND"
}

CS_OPERATORS = {"rank", "cs_zscore"}

TS_OPERATORS = {
    "ts_sum", "ts_sma", "ts_stddev", "ts_rank",
    "ts_mean", "ts_min", "ts_max",
    "ts_argmax", "ts_argmin",
    "delta", "delay", "scale", "product"
}

ARITH_OPERATORS = {
    "minus", "plus", "multiply", "divide", "signed_power"
}

CMP_OPERATORS = {"gt", "lt", "gte", "lte", "eq"}

PAIRWISE_OPERATORS = {"correlation", "covariance"}

COND_OPERATORS = {"if_else"}



# =========================================================
# SAFE HELPERS
# =========================================================


def _clean(df):
    if isinstance(df, pd.DataFrame) or isinstance(df, pd.Series):
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        df = df.clip(-1e6, 1e6) # clipping
        
    return df


def _safe_div(a, b):
    b = b.replace(0, np.nan) if isinstance(b, (pd.Series, pd.DataFrame)) else (np.nan if b == 0 else b)
    out = a / b
    return _clean(out)




# =========================================================
# CROSS-SECTIONAL OPS
# =========================================================

def rank(df):
    df = _clean(df)
    return df.rank(pct=True)


def cs_zscore(df):
    df = _clean(df)

    mean = df.mean(axis=1)
    std = df.std(axis=1)

    std = std.replace(0, np.nan)

    out = df.sub(mean, axis=0).div(std, axis=0)

    return _clean(out)


def log(df):
    df = _clean(df)
    return np.log(np.clip(df, 1e-8, None))


def neg(df):
    return -_clean(df)


# =========================================================
# TIME SERIES OPS
# =========================================================

def ts_sum(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).sum()


def ts_sma(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).mean()


def ts_stddev(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).std().fillna(0)


def ts_mean(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).mean()


def ts_rank(df, w):
    df = _clean(df)

    return df.rolling(w, min_periods=w).apply(
        lambda x: np.argsort(np.argsort(x))[-1] if len(x) > 0 else 0,
        raw=True
    ).fillna(0)


def ts_argmax(df, w):
    df = _clean(df)

    return df.rolling(w, min_periods=w).apply(
        lambda x: np.argmax(x) if len(x) > 0 else 0,
        raw=True
    ).fillna(0)


def ts_argmin(df, w):
    df = _clean(df)

    return df.rolling(w, min_periods=w).apply(
        lambda x: np.argmin(x) if len(x) > 0 else 0,
        raw=True
    ).fillna(0)


def ts_min(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).min()


def ts_max(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).max()


def delta(df, p):
    df = _clean(df)
    return df.diff(p).fillna(0)


def delay(df, p):
    df = _clean(df)
    return df.shift(p).fillna(0)


def scale(df, k):
    df = _clean(df)
    denom = np.abs(df).sum()
    denom = denom if denom != 0 else 1
    return df * k / denom


def product(df, w):
    df = _clean(df)
    return df.rolling(w, min_periods=w).apply(
        lambda x: np.prod(x) if len(x) > 0 else 0,
        raw=True
    ).fillna(0)


# =========================================================
# ARITHMETIC OPS
# =========================================================

def minus(a, b):
    return _clean(a) - _clean(b)


def plus(a, b):
    return _clean(a) + _clean(b)


def multiply(a, b):
    return _clean(a) * _clean(b)


def divide(a, b):
    a = _clean(a)
    b = _clean(b)

    if isinstance(b, (pd.DataFrame, pd.Series)):
        b = b.replace(0, np.nan)

    return (a / b).replace([np.inf, -np.inf], np.nan).fillna(0)


def signed_power(x, p):
    x = _clean(x)
    return np.sign(x) * (np.abs(x) ** p)


# =========================================================
# COMPARISON OPS
# =========================================================

def gt(a, b): return _clean(a) > _clean(b)
def lt(a, b): return _clean(a) < _clean(b)
def gte(a, b): return _clean(a) >= _clean(b)
def lte(a, b): return _clean(a) <= _clean(b)
def eq(a, b): return _clean(a) == _clean(b)


# =========================================================
# PAIRWISE OPS
# =========================================================

def correlation(x, y, w):
    x = _clean(x)
    y = _clean(y)
    return x.rolling(w, min_periods=w).corr(y).fillna(0)


def covariance(x, y, w):
    x = _clean(x)
    y = _clean(y)
    return x.rolling(w, min_periods=w).cov(y).fillna(0)


# =========================================================
# CONDITIONAL OPS
# =========================================================

def if_else(cond, x, y):
    cond = _clean(cond)
    x = _clean(x)
    y = _clean(y)
    return x.where(cond, y).fillna(0)

ALL_OPERATORS = {
    "rank": rank,
    "cs_zscore": cs_zscore,
    "log": log,
    "neg": neg,

    "ts_sum": ts_sum,
    "ts_sma": ts_sma,
    "ts_stddev": ts_stddev,
    "ts_rank": ts_rank,
    "ts_mean": ts_mean,
    "ts_min": ts_min,
    'ts_argmax': ts_argmax,
    'ts_argmin': ts_argmin,
    
    "ts_max": ts_max,
    "delta": delta,
    "delay": delay,
    "scale": scale,
    "product": product,

    "minus": minus,
    "plus": plus,
    "multiply": multiply,
    "divide": divide,
    "signed_power": signed_power,

    "gt": gt,
    "lt": lt,
    "gte": gte,
    "lte": lte,
    "eq": eq,

    "correlation": correlation,
    "covariance": covariance,

    "if_else": if_else
}

# =========================================================
# OPERATOR ARITY MAP (CRITICAL FOR SAFETY)
# =========================================================

OP_ARITY = {
    # TS
    "ts_mean": 2,
    "ts_sma": 2,
    "ts_stddev": 2,
    "ts_rank": 2,
    "ts_sum": 2,
    "ts_min": 2,
    "ts_max": 2,
    'ts_argmax':2,
    'ts_argmin':2,
    "delay": 2,
    "delta": 2,
    "product": 2,

    # ARITH
    "minus": 2,
    "plus": 2,
    "multiply": 2,
    "divide": 2,
    "scale": 2,
    'signed_power': 2,

    # CMP
    "gt": 2,
    "lt": 2,
    "gte": 2,
    "lte": 2,
    "eq": 2,

    # CS / UNARY
    "rank": 1,
    "cs_zscore": 1,
    "log": 1,
    "neg": 1,

    # PAIRWISE
    "correlation": 3,
    "covariance": 3,

    # CONDITIONAL
    "if_else": 3
}

# =========================================================
# OPERATOR SCHEMA (TYPE SAFE + BROADCAST AWARE)
# =========================================================

OP_SCHEMA = {

    # ---------------- TS OPERATORS (df, int window) ----------------
    "ts_mean": ["df", "int"],
    "ts_sma": ["df", "int"],
    "ts_stddev": ["df", "int"],
    "ts_rank": ["df", "int"],
    "ts_min": ["df", "int"],
    "ts_max": ["df", "int"],
    "delta": ["df", "int"],
    "delay": ["df", "int"],
    "product": ["df", "int"],

    # ---------------- CS OPERATORS (df only) ----------------
    "rank": ["df"],
    "cs_zscore": ["df"],
    "log": ["df"],
    "neg": ["df"],

    # ---------------- ARITH (df, float scalar) ----------------
    "minus": ["df", "float"],
    "plus": ["df", "float"],
    "multiply": ["df", "float"],
    "divide": ["df", "float"],

    # ---------------- COMPARISON (df vs any) ----------------
    "gt": ["any", "any"],
    "lt": ["any", "any"],
    "gte": ["any", "any"],
    "lte": ["any", "any"],
    "eq": ["any", "any"],

    # ---------------- PAIRWISE (df, df, int) ----------------
    "correlation": ["df", "df", "int"],
    "covariance": ["df", "df", "int"],

    # ---------------- CONDITIONAL (df, df, df) ----------------
    "if_else": ["df", "df", "df"]
}

COL_NAMES = ['Open', 'Close', 'High', 'Low', 'Volume']