import numpy as np
import pytest

from amortization import auc_from_curve, forward_transfer_cw, threshold_cost_integral


def monotone_curve(rng, D):
    return np.sort(rng.uniform(0, 1, size=D)) * rng.uniform(0.3, 1.0)


def test_layer_cake_auc_identity():
    # Prop. 5(i): AUC = 1 - I(p)/D for non-decreasing curves.
    rng = np.random.default_rng(0)
    for _ in range(200):
        D = int(rng.integers(1, 60))
        p = monotone_curve(rng, D)
        assert auc_from_curve(p) == pytest.approx(1 - threshold_cost_integral(p) / D, abs=1e-12)


def test_cw_forward_transfer_is_an_amortization_ratio():
    # Prop. 5(ii): FT = 1 - I(p)/I(p_b).
    rng = np.random.default_rng(1)
    for _ in range(200):
        D = int(rng.integers(2, 60))
        p, pb = monotone_curve(rng, D), monotone_curve(rng, D)
        if auc_from_curve(pb) >= 1:
            continue
        ft = forward_transfer_cw(p, pb)
        assert ft == pytest.approx(1 - threshold_cost_integral(p) / threshold_cost_integral(pb), abs=1e-10)


def test_identity_needs_monotonicity():
    # A curve that reaches 1 and then collapses: AUC counts the collapse, first-hit cost does not.
    p = np.array([0.0, 1.0, 0.0, 0.0])
    assert auc_from_curve(p) != pytest.approx(1 - threshold_cost_integral(p) / p.size)


def test_step_curve_hand_computed():
    p = np.array([0.0, 0.5, 1.0])  # t(a)=1 for a in (0,0.5], t(a)=2 for a in (0.5,1]
    assert threshold_cost_integral(p) == pytest.approx(0.5 * 1 + 0.5 * 2)
