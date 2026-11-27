"""Diagnostics added in v0.2 (paper Section 11). Additive module.

Nothing here changes the semantics of ``metric``, ``stats`` or ``transfer``;
those modules are the instrument pinned by downstream users at commit 70297af
(tag ``instrument-v1``). Every function maps to a numbered statement in the
paper:

* ``cost_ratio`` / ``log_cost_ratio`` / ``reverse_amortization`` -- Remark on
  interpreting A (cost ratio is exactly 1 - A).
* ``chain_amortization`` -- Lemma (chain rule for point estimates).
* ``protocol_cost_ratio`` / ``protocol_ratio_limits`` -- Proposition (protocol
  dependence of the cost ratio).
* ``censoring_bounds`` / ``tipping_point`` -- Proposition (partial
  identification under censoring) and its corollary.
* ``irrelevant_state_ratio`` -- Definition (irrelevant-state scaling ratio R_N).
* ``scaling_amortization_bounds`` -- Proposition (irrelevant-state scaling and
  the possibility of positive amortization), finite-horizon bounds.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "cost_ratio",
    "log_cost_ratio",
    "reverse_amortization",
    "chain_amortization",
    "protocol_cost_ratio",
    "protocol_ratio_limits",
    "censoring_bounds",
    "tipping_point",
    "irrelevant_state_ratio",
    "scaling_amortization_bounds",
]


def _finite_A(A: float) -> float:
    A = float(A)
    if not np.isfinite(A) or A > 1:
        raise ValueError("A must be a finite number <= 1")
    return A


def cost_ratio(A: float) -> float:
    """C_L / C_R = 1 - A. A = -2.87 means the learner paid 3.87x the reference."""
    return 1.0 - _finite_A(A)


def log_cost_ratio(A: float) -> float:
    """log(C_L / C_R) = -log(1 - A) = -ell_n (Prop. 1(iv)). Requires A < 1."""
    A = _finite_A(A)
    if A >= 1:
        raise ValueError("log cost ratio undefined for A = 1 (zero learner cost)")
    return float(np.log1p(-A))


def reverse_amortization(A: float) -> float:
    """A(R || L) from A(L || R): -A / (1 - A) (Prop. 1(iv)). Requires A < 1."""
    A = _finite_A(A)
    if A >= 1:
        raise ValueError("undefined for A = 1")
    return -A / (1.0 - A)


def chain_amortization(*As: float) -> float:
    """1 - prod_k (1 - A_k): A(X||Z) from A(X||Y), A(Y||Z), ... (chain-rule lemma).

    Exact for point estimates (ratios of sums) computed on the same seeds and
    horizon; not valid for interval endpoints.
    """
    if not As:
        raise ValueError("need at least one A")
    return 1.0 - float(np.prod([cost_ratio(a) for a in As]))


def protocol_cost_ratio(f: float, M_L: float, W_L: float, M_R: float, W_R: float) -> float:
    """rho(f) = (f M_L + W_L) / (f M_R + W_R) under the fixed-overhead protocol model.

    ``f`` is the protocol's fixed cost per charged invocation, ``M`` the number of
    invocations and ``W`` the work above that floor.
    """
    vals = np.array([f, M_L, W_L, M_R, W_R], dtype=float)
    if np.any(vals < 0) or not np.all(np.isfinite(vals)):
        raise ValueError("arguments must be finite and non-negative")
    den = f * M_R + W_R
    if den <= 0:
        raise ValueError("reference cost must be positive")
    return float((f * M_L + W_L) / den)


def protocol_ratio_limits(M_L: float, W_L: float, M_R: float, W_R: float) -> Tuple[float, float]:
    """(rho at f = 0, rho as f -> infinity) = (W_L / W_R, M_L / M_R); rho(f) is monotone between them."""
    if W_R <= 0 or M_R <= 0:
        raise ValueError("W_R and M_R must be positive")
    return float(W_L / W_R), float(M_L / M_R)


def censoring_bounds(
    c_L: Sequence[float],
    c_R: Sequence[float],
    cens_L: Sequence[bool],
    cens_R: Sequence[bool],
    upper_L: Optional[Sequence[float]] = None,
    upper_R: Optional[Sequence[float]] = None,
) -> Tuple[float, float]:
    """Sharp identification interval for A_n when censored costs are lower bounds.

    Recorded costs on censored tasks are lower bounds on the true cost-to-target;
    ``upper_*`` optionally gives upper bounds for them (``inf`` if none). Returns
    (A_lo, A_hi). With no upper bound on a censored learner task A_lo = -inf;
    with no upper bound on a censored reference task A_hi = 1.
    """
    cL, cR = np.asarray(c_L, float), np.asarray(c_R, float)
    dL, dR = np.asarray(cens_L, bool), np.asarray(cens_R, bool)
    if not (cL.shape == cR.shape == dL.shape == dR.shape) or cL.ndim != 1:
        raise ValueError("inputs must be 1-D arrays of equal length")
    if np.any(cL < 0) or np.any(cR < 0):
        raise ValueError("costs must be non-negative")
    uL = np.full_like(cL, np.inf) if upper_L is None else np.asarray(upper_L, float)
    uR = np.full_like(cR, np.inf) if upper_R is None else np.asarray(upper_R, float)
    uL = np.where(dL, uL, cL)
    uR = np.where(dR, uR, cR)
    if np.any(uL < cL) or np.any(uR < cR):
        raise ValueError("upper bounds must be >= recorded costs")
    lowR, highR = cR.sum(), uR.sum()
    lowL, highL = cL.sum(), uL.sum()
    if lowR <= 0:
        raise ValueError("recorded reference cost must be positive")
    A_lo = -np.inf if not np.isfinite(highL) else 1.0 - highL / lowR
    A_hi = 1.0 if not np.isfinite(highR) else 1.0 - lowL / highR
    return float(A_lo), float(A_hi)


def tipping_point(C_L: float, C_R_recorded: float) -> float:
    """Extra true reference cost (on its censored tasks) needed for A_n >= 0: C_L - C_R."""
    if C_L < 0 or C_R_recorded <= 0:
        raise ValueError("C_L must be >= 0 and C_R_recorded > 0")
    return float(max(C_L - C_R_recorded, 0.0))


def irrelevant_state_ratio(
    cost_N: Sequence[float],
    cost_base: Sequence[float],
    level: float = 0.95,
    B: int = 5000,
    rng: Optional[np.random.Generator] = None,
) -> Tuple[float, Tuple[float, float]]:
    """R_N = mean over seeds of (mean task cost at padding N) / (at baseline padding).

    Arrays are per seed and paired. Returns the point value and a percentile
    bootstrap interval over seeds. (Per-seed ratios averaged, the form used by
    PacketLM's registered rule F; a ratio of means is a valid alternative and
    should be labelled.)
    """
    a, b = np.asarray(cost_N, float), np.asarray(cost_base, float)
    if a.shape != b.shape or a.ndim != 1 or a.size < 2:
        raise ValueError("need paired 1-D arrays with at least 2 seeds")
    if np.any(b <= 0) or np.any(a < 0):
        raise ValueError("baseline costs must be positive and padded costs non-negative")
    if not 0 < level < 1:
        raise ValueError("level must be in (0, 1)")
    r = a / b
    rng = np.random.default_rng(0) if rng is None else rng
    boots = r[rng.integers(0, r.size, size=(B, r.size))].mean(axis=1)
    lo, hi = np.quantile(boots, [(1 - level) / 2, (1 + level) / 2])
    return float(r.mean()), (float(lo), float(hi))


def scaling_amortization_bounds(
    rho_bar: float, h_first: float, h_last: float, setup_L: float, setup_R: float, sum_r: float
) -> Tuple[float, float]:
    """Finite-horizon bounds on A_n under the factorized cost model.

    Model: c_i(L) = rho_i r_i h(K_{i-1}) with h non-decreasing and K non-decreasing,
    c_i(R) = r_i. ``rho_bar`` is the r-weighted mean of rho_i, ``h_first`` = h(K_0),
    ``h_last`` = h(K_{n-1}), ``sum_r`` = sum of r_i. Returns (lower, upper) for A_n.
    """
    if min(rho_bar, h_first, setup_L, setup_R) < 0 or h_last < h_first or sum_r <= 0:
        raise ValueError("invalid arguments")
    den = setup_R + sum_r
    lower = 1.0 - (setup_L + h_last * rho_bar * sum_r) / den
    upper = 1.0 - (setup_L + h_first * rho_bar * sum_r) / den
    return float(lower), float(upper)
