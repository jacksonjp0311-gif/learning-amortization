"""Tests for amortization.diagnostics (paper Section 11, v0.2 additions)."""

import math

import numpy as np
import pytest

from amortization.diagnostics import (
    censoring_bounds,
    chain_amortization,
    cost_ratio,
    irrelevant_state_ratio,
    log_cost_ratio,
    protocol_cost_ratio,
    protocol_ratio_limits,
    reverse_amortization,
    scaling_amortization_bounds,
    tipping_point,
)
from amortization.metric import amortization
from amortization.stats import point_estimate


def test_interpretation_worked_example():
    # Remark (interpretation): G51 comp, 215.8 s vs 55.7 s.
    A = 1 - 215.8 / 55.7
    assert cost_ratio(A) == pytest.approx(215.8 / 55.7)
    assert cost_ratio(-2.872) == pytest.approx(3.872)
    assert log_cost_ratio(-2.872) == pytest.approx(math.log(3.872))
    assert reverse_amortization(-2.872) == pytest.approx(2.872 / 3.872)
    assert reverse_amortization(-2.872) == pytest.approx(amortization([0.0, 55.7], [0.0, 215.8]), rel=1e-3)
    assert abs(cost_ratio(-2.872) - math.exp(2.872)) > 10  # the misreading is far off


def test_chain_rule_point_estimates():
    rng = np.random.default_rng(1)
    X, Y, Z = (rng.uniform(1, 5, size=(7, 10)) for _ in range(3))
    lhs = point_estimate(X, Z)
    rhs = chain_amortization(point_estimate(X, Y), point_estimate(Y, Z))
    assert lhs == pytest.approx(rhs, abs=1e-12)
    assert chain_amortization(0.5) == pytest.approx(0.5)


def test_protocol_ratio_mediant_and_monotone():
    nuL, WL, nuR, WR = 911, 25.7, 407, 0.9  # G54 unrelated (rule S)
    rho = protocol_cost_ratio(0.0259, nuL, WL, nuR, WR)
    assert rho == pytest.approx(4.31, abs=0.02)
    w, m = protocol_ratio_limits(nuL, WL, nuR, WR)
    fs = np.linspace(0, 10, 200)
    vals = [protocol_cost_ratio(f, nuL, WL, nuR, WR) for f in fs]
    assert vals[0] == pytest.approx(w)
    assert np.all(np.diff(vals) < 0)  # mu < omega => decreasing in f
    assert min(vals) > m
    # mediant form
    f = 0.3
    lam = f * nuR / (f * nuR + WR)
    assert protocol_cost_ratio(f, nuL, WL, nuR, WR) == pytest.approx(lam * m + (1 - lam) * w)


def test_protocol_sign_flip():
    # mu < 1 < omega: A < 0 for small f, A > 0 for large f (Prop. protocol (iii)).
    nuL, WL, nuR, WR = 50, 20.0, 100, 10.0
    assert 1 - protocol_cost_ratio(0.0, nuL, WL, nuR, WR) < 0
    assert 1 - protocol_cost_ratio(10.0, nuL, WL, nuR, WR) > 0


def test_censoring_bounds_recover_prop6_and_are_sharp():
    cL = np.array([5.0, 6.0, 7.0])
    cR = np.array([3.0, 4.0, 2.0])
    none = np.zeros(3, bool)
    rec = 1 - cL.sum() / cR.sum()
    # only R censored, no upper bound: [recorded, 1]
    lo, hi = censoring_bounds(cL, cR, none, np.array([0, 0, 1], bool))
    assert lo == pytest.approx(rec) and hi == 1.0
    # only L censored: (-inf, recorded]
    lo, hi = censoring_bounds(cL, cR, np.array([1, 0, 0], bool), none)
    assert lo == -np.inf and hi == pytest.approx(rec)
    # with finite upper bounds, endpoints are attained by corner costs
    uL, uR = cL + [2, 0, 0], cR + [0, 0, 3]
    lo, hi = censoring_bounds(cL, cR, np.array([1, 0, 0], bool), np.array([0, 0, 1], bool), uL, uR)
    assert lo == pytest.approx(1 - uL.sum() / cR.sum())
    assert hi == pytest.approx(1 - cL.sum() / uR.sum())
    rng = np.random.default_rng(0)
    for _ in range(500):
        tL = cL + rng.uniform(0, 1, 3) * (uL - cL)
        tR = cR + rng.uniform(0, 1, 3) * (uR - cR)
        assert lo - 1e-12 <= 1 - tL.sum() / tR.sum() <= hi + 1e-12


def test_tipping_point():
    assert tipping_point(48.37, 28.84) == pytest.approx(19.53)
    assert tipping_point(1.0, 2.0) == 0.0


def test_irrelevant_state_ratio():
    base = np.array([1.0, 2.0, 1.5, 1.2])
    r, (lo, hi) = irrelevant_state_ratio(3 * base, base)
    assert r == pytest.approx(3.0) and lo == pytest.approx(3.0) and hi == pytest.approx(3.0)
    r, (lo, hi) = irrelevant_state_ratio(base * [2, 3, 4, 5], base)
    assert r == pytest.approx(3.5) and lo <= r <= hi
    with pytest.raises(ValueError):
        irrelevant_state_ratio([1.0], [1.0])


def test_scaling_bounds_contain_model_amortization():
    rng = np.random.default_rng(3)
    n = 30
    r = rng.uniform(1, 2, n)
    phi = rng.uniform(0.2, 0.6, n)
    K = np.cumsum(rng.integers(0, 50, n))
    h = 1 + 0.01 * np.sqrt(K)  # non-decreasing, h(K_0) = 1 with K_0 = 0
    hprev = np.concatenate([[1.0], h[:-1]])
    cL = np.concatenate([[3.0], phi * r * hprev])
    cR = np.concatenate([[0.0], r])
    A = amortization(cL, cR)
    rho_bar = (phi * r).sum() / r.sum()
    lo, hi = scaling_amortization_bounds(rho_bar, 1.0, hprev[-1], 3.0, 0.0, r.sum())
    assert lo - 1e-12 <= A <= hi + 1e-12


def test_unbounded_inflation_drives_A_down():
    # Prop. scaling (ii): h -> infinity makes A_n -> -infinity even when phi is small.
    n = np.arange(1, 20001)
    cR = np.concatenate([[0.0], np.ones_like(n, dtype=float)])
    cL = np.concatenate([[0.0], 0.1 * np.sqrt(n)])  # sublinear but unbounded inflation
    A = [amortization(cL, cR, k) for k in (10, 1000, 20000)]
    assert A[0] > 0 > A[1] > A[2]
