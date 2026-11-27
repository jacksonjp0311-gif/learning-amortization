"""Estimation and inference for learning amortization over seeds (paper Section 6).

Inputs are cost matrices of shape (S, N+1): one row per independent seed, in
the per-task cost-vector convention of :mod:`amortization.metric`. Rows of the
continual and reference matrices must be *paired*: row s of both arms used the
same task sequence and evaluation sets generated from seed s.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np


def _check(Cc, Cb) -> Tuple[np.ndarray, np.ndarray]:
    Cc = np.atleast_2d(np.asarray(Cc, dtype=float))
    Cb = np.atleast_2d(np.asarray(Cb, dtype=float))
    if Cc.shape != Cb.shape:
        raise ValueError("cost matrices must be paired: same shape (S, N+1)")
    if Cc.shape[1] < 2:
        raise ValueError("need at least one task (N >= 1)")
    if np.any(~np.isfinite(Cc)) or np.any(~np.isfinite(Cb)) or np.any(Cc < 0) or np.any(Cb < 0):
        raise ValueError("costs must be finite and non-negative")
    return Cc, Cb


def _cum(C: np.ndarray, n: Optional[int]) -> np.ndarray:
    N = C.shape[1] - 1
    n = N if n is None else int(n)
    if not 1 <= n <= N:
        raise ValueError(f"n must be in [1, {N}]")
    return C[:, : n + 1].sum(axis=1)


def point_estimate(Cc, Cb, n: Optional[int] = None) -> float:
    """Ratio-of-means estimator  1 - sum_s C_cont^(s)(n) / sum_s C_base^(s)(n)  (Eq. 5)."""
    Cc, Cb = _check(Cc, Cb)
    x, y = _cum(Cc, n), _cum(Cb, n)
    if y.sum() <= 0:
        raise ValueError("reference cost must be positive")
    return 1.0 - x.sum() / y.sum()


def delta_method_se(Cc, Cb, n: Optional[int] = None) -> float:
    """First-order (delta-method) standard error of the ratio-of-means estimator (Eq. 6)."""
    Cc, Cb = _check(Cc, Cb)
    x, y = _cum(Cc, n), _cum(Cb, n)
    S = x.size
    if S < 2:
        return float("nan")
    R = x.sum() / y.sum()
    d = x - R * y  # residuals; they sum to zero by construction
    return float(np.sqrt((d @ d) / (S * (S - 1))) / y.mean())


def bootstrap_ci(
    Cc,
    Cb,
    n: Optional[int] = None,
    level: float = 0.95,
    B: int = 10_000,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[float, float]:
    """Paired percentile bootstrap CI for A_n, resampling whole seeds (Section 6.2)."""
    Cc, Cb = _check(Cc, Cb)
    if not 0 < level < 1:
        raise ValueError("level must be in (0, 1)")
    rng = np.random.default_rng(0) if rng is None else rng
    x, y = _cum(Cc, n), _cum(Cb, n)
    S = x.size
    idx = rng.integers(0, S, size=(B, S))
    ys = y[idx].sum(axis=1)
    if np.any(ys <= 0):
        raise ValueError("a bootstrap resample has zero reference cost")
    stats = 1.0 - x[idx].sum(axis=1) / ys
    lo, hi = np.quantile(stats, [(1 - level) / 2, (1 + level) / 2])
    return float(lo), float(hi)


def log_ratios(Cc, Cb, n: Optional[int] = None) -> np.ndarray:
    """Per-seed log cost ratio  l_s = log C_base^(s)(n) - log C_cont^(s)(n) (Section 6.2)."""
    Cc, Cb = _check(Cc, Cb)
    x, y = _cum(Cc, n), _cum(Cb, n)
    if np.any(x <= 0) or np.any(y <= 0):
        raise ValueError("log ratios need strictly positive cumulative costs")
    return np.log(y) - np.log(x)


def sign_flip_test(
    l: np.ndarray, B: int = 100_000, exact_max: int = 16, rng: Optional[np.random.Generator] = None
) -> float:
    """Two-sided paired sign-flip permutation test of H0: l is symmetric about 0.

    Statistic |mean(l)|. Exact enumeration of all 2^S sign patterns when
    S <= ``exact_max``; otherwise Monte Carlo with the (1 + count)/(1 + B) rule.
    """
    l = np.asarray(l, dtype=float)
    S = l.size
    if S == 0:
        raise ValueError("need at least one seed")
    obs = abs(l.mean())
    tol = 1e-12 * max(1.0, obs)
    if S <= exact_max:
        signs = np.array(list(itertools.product((1.0, -1.0), repeat=S)))
        stats = np.abs(signs @ l) / S
        return float(np.mean(stats >= obs - tol))
    rng = np.random.default_rng(0) if rng is None else rng
    signs = rng.choice((1.0, -1.0), size=(B, S))
    stats = np.abs(signs @ l) / S
    return float((1 + np.sum(stats >= obs - tol)) / (1 + B))


def trend_slope(
    Cc, Cb, B: int = 5_000, level: float = 0.95, rng: Optional[np.random.Generator] = None
) -> Tuple[float, Tuple[float, float]]:
    """OLS slope of the seed-averaged per-task log ratio on task index (Section 5.2).

    A positive slope means per-task savings grow along the sequence, the
    signature of compounding ("learning to learn") rather than a one-off gain.
    Returns (slope, bootstrap CI over seeds).
    """
    Cc, Cb = _check(Cc, Cb)
    if np.any(Cc[:, 1:] <= 0) or np.any(Cb[:, 1:] <= 0):
        raise ValueError("per-task costs must be strictly positive for log ratios")
    L = np.log(Cb[:, 1:]) - np.log(Cc[:, 1:])  # (S, N)
    N = L.shape[1]
    if N < 2:
        raise ValueError("need at least two tasks for a trend")
    t = np.arange(1, N + 1, dtype=float)
    tc = t - t.mean()

    def slope(rows):
        m = rows.mean(axis=0)
        return float(tc @ (m - m.mean()) / (tc @ tc))

    rng = np.random.default_rng(0) if rng is None else rng
    S = L.shape[0]
    boots = np.array([slope(L[rng.integers(0, S, size=S)]) for _ in range(B)])
    lo, hi = np.quantile(boots, [(1 - level) / 2, (1 + level) / 2])
    return slope(L), (float(lo), float(hi))


@dataclass
class AmortizationEstimate:
    n: int
    seeds: int
    point: float
    ci: Tuple[float, float]
    level: float
    se_delta: float
    p_value: float
    geometric: float = field(default=float("nan"))

    def __str__(self) -> str:  # pragma: no cover - formatting only
        lo, hi = self.ci
        return (
            f"A_{self.n} = {self.point:+.4f}  [{lo:+.4f}, {hi:+.4f}] ({self.level:.0%} paired bootstrap, "
            f"S={self.seeds}); delta-SE={self.se_delta:.4f}; sign-flip p={self.p_value:.4g}; "
            f"geometric-mean form={self.geometric:+.4f}"
        )


def estimate(Cc, Cb, n: Optional[int] = None, level: float = 0.95, B: int = 10_000, rng=None) -> AmortizationEstimate:
    """Bundle point estimate, paired bootstrap CI, delta-method SE and sign-flip p-value."""
    Cc, Cb = _check(Cc, Cb)
    N = Cc.shape[1] - 1
    n = N if n is None else int(n)
    l = log_ratios(Cc, Cb, n)
    return AmortizationEstimate(
        n=n,
        seeds=Cc.shape[0],
        point=point_estimate(Cc, Cb, n),
        ci=bootstrap_ci(Cc, Cb, n, level=level, B=B, rng=rng),
        level=level,
        se_delta=delta_method_se(Cc, Cb, n),
        p_value=sign_flip_test(l),
        geometric=float(1.0 - np.exp(-l.mean())),
    )
