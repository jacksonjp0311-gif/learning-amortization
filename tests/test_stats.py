import numpy as np
import pytest

from amortization import (
    bootstrap_ci,
    delta_method_se,
    estimate,
    log_ratios,
    point_estimate,
    sign_flip_test,
    trend_slope,
)


def paired(S=30, N=5, ratio=0.7, noise=0.2, seed=0):
    rng = np.random.default_rng(seed)
    Cb = rng.lognormal(mean=2.0, sigma=0.5, size=(S, N + 1))
    Cc = Cb * ratio * rng.lognormal(0, noise, size=(S, N + 1))
    return Cc, Cb


def test_point_estimate_is_ratio_of_sums():
    Cc, Cb = paired()
    assert point_estimate(Cc, Cb) == pytest.approx(1 - Cc.sum() / Cb.sum())


def test_geometric_form():
    Cc, Cb = paired()
    l = log_ratios(Cc, Cb)
    est = estimate(Cc, Cb, B=500)
    assert est.geometric == pytest.approx(1 - np.exp(-l.mean()))


def test_delta_se_agrees_with_bootstrap_sd():
    Cc, Cb = paired(S=400)
    se = delta_method_se(Cc, Cb)
    rng = np.random.default_rng(1)
    x, y = Cc.sum(1), Cb.sum(1)
    idx = rng.integers(0, 400, size=(4000, 400))
    boot = 1 - x[idx].sum(1) / y[idx].sum(1)
    assert se == pytest.approx(boot.std(), rel=0.1)


def test_bootstrap_ci_contains_point_and_orders():
    Cc, Cb = paired()
    lo, hi = bootstrap_ci(Cc, Cb, B=2000)
    assert lo < point_estimate(Cc, Cb) < hi


def test_bootstrap_coverage_roughly_nominal():
    # Population A = 1 - E[C_c]/E[C_b]; with multiplicative lognormal noise E[ratio noise] = exp(noise^2/2).
    noise, ratio = 0.3, 0.7
    true_A = 1 - ratio * np.exp(noise**2 / 2)
    hits = 0
    reps = 200
    for r in range(reps):
        Cc, Cb = paired(S=40, ratio=ratio, noise=noise, seed=100 + r)
        lo, hi = bootstrap_ci(Cc, Cb, B=1000, rng=np.random.default_rng(r))
        hits += lo <= true_A <= hi
    assert hits / reps >= 0.88


def test_sign_flip_exact_values():
    assert sign_flip_test(np.ones(5)) == pytest.approx(2 / 32)
    assert sign_flip_test(np.array([1.0, -1.0])) == pytest.approx(1.0)
    p = sign_flip_test(np.r_[np.ones(30)], B=20000)
    assert p < 1e-3


def test_sign_flip_null_is_uniformish():
    rng = np.random.default_rng(7)
    ps = [sign_flip_test(rng.normal(size=10)) for _ in range(300)]
    assert 0.02 <= np.mean(np.array(ps) <= 0.05) <= 0.09


def test_trend_slope_recovers_planted_trend():
    S, N = 20, 15
    rng = np.random.default_rng(3)
    Cb = np.full((S, N + 1), 100.0)
    i = np.arange(N + 1)
    Cc = Cb * np.exp(-0.1 * i) * rng.lognormal(0, 0.05, size=(S, N + 1))
    slope, (lo, hi) = trend_slope(Cc, Cb, B=1000)
    assert slope == pytest.approx(0.1, abs=0.01)
    assert lo < 0.1 < hi


def test_pairing_enforced():
    with pytest.raises(ValueError):
        point_estimate(np.ones((3, 4)), np.ones((2, 4)))
