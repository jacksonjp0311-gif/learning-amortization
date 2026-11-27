"""Link between learning amortization and AUC-based forward transfer (paper Prop. 5).

For a learning curve p_0, ..., p_{D-1} in [0, 1] (performance after k units of
training cost), define the first-hit cost t(alpha) = min{k : p_k >= alpha}
(D if never reached). Then, for a non-decreasing curve,

    AUC = (1/D) sum_k p_k = 1 - (1/D) * integral_0^1 min(t(alpha), D) d alpha,

and the Continual World forward transfer (Wolczyk et al., 2021)

    FT = (AUC - AUC_b) / (1 - AUC_b) = 1 - I(p) / I(p_b),   I(p) = integral_0^1 min(t(alpha), D) d alpha,

is a learning-amortization ratio whose cost is training steps, averaged over
all accuracy thresholds and censored at the budget D.
"""

from __future__ import annotations

import numpy as np


def _curve(p) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    if p.ndim != 1 or p.size == 0:
        raise ValueError("curve must be a non-empty 1-D array")
    if np.any(p < 0) or np.any(p > 1):
        raise ValueError("performance must lie in [0, 1]")
    return p


def auc_from_curve(p) -> float:
    """Normalized area under a discrete learning curve, (1/D) sum_k p_k."""
    return float(_curve(p).mean())


def threshold_cost_integral(p) -> float:
    """Exact I(p) = integral_0^1 min(t(alpha), D) d alpha using first-hit times.

    t(alpha) is piecewise constant between consecutive distinct values of p, so
    the integral is evaluated exactly (no grid), for any curve, monotone or not.
    """
    p = _curve(p)
    D = p.size
    levels = np.unique(np.concatenate(([0.0, 1.0], p)))
    total = 0.0
    for a, b in zip(levels[:-1], levels[1:]):
        # On (a, b], p_k >= alpha  <=>  p_k >= b.
        hit = np.nonzero(p >= b)[0]
        t = hit[0] if hit.size else D
        total += (b - a) * min(t, D)
    return float(total)


def forward_transfer_cw(p, p_base) -> float:
    """Continual World forward transfer (AUC - AUC_b) / (1 - AUC_b)."""
    a, ab = auc_from_curve(p), auc_from_curve(p_base)
    if ab >= 1:
        raise ValueError("reference curve is already perfect; FT undefined")
    return (a - ab) / (1 - ab)
