import random
from .operators import COL_NAMES, TS_OPERATORS, CS_OPERATORS, ARITH_OPERATORS, CMP_OPERATORS, PAIRWISE_OPERATORS, COND_OPERATORS

# =========================================================
# COLUMN SPACE
# =========================================================
COL_LIST = COL_NAMES


# =========================================================
# PURE RE-SAMPLING RANGES
# =========================================================
INT_RANGE = (2, 60)         # rolling windows, delays
FLOAT_RANGE = (0.5, 3.5)     # scaling factors


# =========================================================
# OPERATOR GROUPS
# =========================================================

TS_OPS = list(TS_OPERATORS)

CS_OPS = list(CS_OPERATORS)

ARITH_OPS = list(ARITH_OPERATORS)

CMP_OPS = list(CMP_OPERATORS)

PAIRWISE_OPS = list(PAIRWISE_OPERATORS)

COND_OPS = list(COND_OPERATORS)


GROUP_MAP = {
    "TS": TS_OPS,
    "CS": CS_OPS,
    "ARITH": ARITH_OPS,
    "CMP": CMP_OPS,
    "PAIRWISE": PAIRWISE_OPS,
    "COND": COND_OPS
}