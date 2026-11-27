"""Tests: every proposition in the paper has at least one executable check here."""

import math

import numpy as np
import pytest

from amortization import (
    CostLog,
    CostRecord,
    amortization,
    amortization_curve,
    break_even,
    component_contributions,
    marginal_amortization,
    novelty_stratified_amortization,
    probe_amortization,
    tail_amortization,
)

rng = np.random.default_rng(12345)


def rand_costs(N=10):
    return rng.uniform(0.1, 10, size=N + 1), rng.uniform(0.1, 10, size=N + 1)


def test_definition_and_parity():
    cb = np.array([0.0, 10, 10, 10])
    assert amortization(cb, cb) == 0.0
    assert amortization([0, 5, 5, 5], cb) == pytest.approx(0.5)
    assert amortization([0, 20, 20, 20], cb) == pytest.approx(-1.0)  # twice as expensive
    assert amortization([0, 0, 0, 0], cb) == 1.0  # upper bound attained only at zero cost


def test_range_upper_bound_and_unbounded_below():
    for _ in range(200):
        cc, cb = rand_costs()
        assert amortization(cc, cb) <= 1.0
    assert amortization([0, 1e9], [0, 1]) < -1e8


def test_unit_invariance():
    cc, cb = rand_costs()
    for lam in (1e-6, 3.7, 1e6):
        assert amortization(lam * cc, lam * cb) == pytest.approx(amortization(cc, cb), rel=1e-12)


def test_not_invariant_to_relative_prices():
    # Prop. 1(iii): changing relative resource prices can flip the sign.
    ops_c, ops_b = np.array([0, 1.0]), np.array([0, 10.0])
    mem_c, mem_b = np.array([0, 10.0]), np.array([0, 0.0])
    a_cheap_mem = amortization(ops_c + 0.1 * mem_c, ops_b + 0.1 * mem_b)
    a_dear_mem = amortization(ops_c + 10 * mem_c, ops_b + 10 * mem_b)
    assert a_cheap_mem > 0 > a_dear_mem


def test_weighted_average_identity():
    # A_n = sum_{i=0}^n w_i a_i with w_i = c_base,i / C_base(n), including the setup index 0.
    for _ in range(100):
        cc, cb = rand_costs(8)
        for n in range(1, 9):
            w = cb[: n + 1] / cb[: n + 1].sum()
            a = 1 - cc[: n + 1] / cb[: n + 1]
            assert amortization(cc, cb, n) == pytest.approx(float(w @ a), rel=1e-12, abs=1e-12)
            assert math.isclose(w.sum(), 1.0)


def test_weighted_average_identity_with_zero_reference_setup():
    # Prop. 1(v), general form: tasks with c_i(R) = 0 enter as -c_i(L)/C_R(n).
    for _ in range(100):
        cc, cb = rand_costs(8)
        cb[0] = 0.0
        cb[3] = 0.0
        n = 8
        P = [i for i in range(n + 1) if cb[i] > 0]
        Z = [i for i in range(n + 1) if cb[i] == 0]
        Cb = cb.sum()
        val = sum(cb[i] / Cb * (1 - cc[i] / cb[i]) for i in P) - sum(cc[i] / Cb for i in Z)
        assert amortization(cc, cb, n) == pytest.approx(val, rel=1e-12, abs=1e-12)


def test_curve_matches_pointwise():
    cc, cb = rand_costs(6)
    curve = amortization_curve(cc, cb)
    assert np.allclose(curve, [amortization(cc, cb, n) for n in range(1, 7)])


def test_component_decomposition_sums_to_A():
    comps = ["acquisition", "verification", "storage", "retrieval", "maintenance", "execution"]
    for _ in range(50):
        cc = {k: rng.uniform(0, 5, 7) for k in comps}
        cb = {k: rng.uniform(0, 5, 7) for k in comps[:3] + comps[5:]}  # base has no retrieval/maintenance
        D = component_contributions(cc, cb, n=4)
        tc, tb = sum(cc.values()), sum(cb.values())
        assert sum(D.values()) == pytest.approx(amortization(tc, tb, 4), rel=1e-12, abs=1e-12)
        assert D["retrieval"] <= 0 and D["maintenance"] <= 0  # pure overheads


@pytest.mark.parametrize("delta0,delta", [(0.0, 1.0), (5.0, 1.0), (5.5, 2.0), (100.0, 3.0), (-3.0, 1.0)])
def test_break_even_constant_costs(delta0, delta):
    # Prop. 4: upfront overhead delta0 >= 0, per-task saving delta > 0 => n* = floor(delta0/delta) + 1.
    N = 200
    gb = 10.0
    cb = np.r_[5.0, np.full(N, gb)]
    cc = np.r_[5.0 + delta0, np.full(N, gb - delta)]
    expected = 1 if delta0 < 0 else math.floor(delta0 / delta) + 1
    assert break_even(cc, cb) == expected


def test_break_even_none_when_never_positive():
    assert break_even([5, 10, 10], [1, 10, 10]) is None


def test_break_even_ignores_transient_crossing():
    # A_1 > 0 but A_2 <= 0 and A_3 > 0: break-even must be 3, not 1.
    cb = [0, 10, 10, 10]
    cc = [0, 5, 20, 1]
    A = amortization_curve(cc, cb)
    assert A[0] > 0 and A[1] <= 0 and A[2] > 0
    assert break_even(cc, cb) == 3


def test_asymptotic_limit_and_tail():
    # Prop. 3: with per-task costs converging, A_n -> 1 - gamma_c / gamma_b regardless of setup cost.
    N = 20000
    i = np.arange(1, N + 1)
    cb = np.r_[0.0, 10 + 1 / i]
    cc = np.r_[5000.0, 4 + 3 / np.sqrt(i)]
    assert amortization(cc, cb) == pytest.approx(0.6, abs=0.03)
    assert tail_amortization(cc, cb, 1000) == pytest.approx(0.6, abs=0.005)
    assert amortization(cc, cb, 10) < 0  # early on the setup cost dominates


def test_marginal():
    assert np.allclose(marginal_amortization([9, 5, 10], [1, 10, 10]), [0.5, 0.0])


def test_input_validation():
    with pytest.raises(ValueError):
        amortization([0, -1], [0, 1])
    with pytest.raises(ValueError):
        amortization([0, 1, 1], [0, 1])
    with pytest.raises(ValueError):
        amortization([0, float("inf")], [0, 1])
    with pytest.raises(ValueError):
        amortization([0, 1], [0, 0])


def test_costlog_roundtrip_and_scalarization(tmp_path):
    recs = [
        CostRecord("cont", 1, 0, "acquisition", "ops", 3.0),
        CostRecord("cont", 1, 1, "acquisition", "ops", 2.0),
        CostRecord("cont", 1, 1, "storage", "bytes", 100.0),
        CostRecord("cont", 1, 2, "retrieval", "ops", 1.0, censored=True),
        CostRecord("base", 1, 1, "acquisition", "ops", 10.0),
        CostRecord("base", 1, 2, "acquisition", "ops", 10.0),
    ]
    log = CostLog(recs)
    p = tmp_path / "log.csv"
    log.to_csv(p)
    log2 = CostLog.from_csv(p)
    assert log2.records == recs
    with pytest.raises(ValueError):
        log2.task_costs("cont", 1)  # two resources and no declared prices
    w = {"ops": 1.0, "bytes": 0.01}
    assert np.allclose(log2.task_costs("cont", 1, w), [3.0, 3.0, 1.0])
    assert np.allclose(log2.task_costs("base", 1, w), [0.0, 10.0, 10.0])
    assert log2.censored("cont", 1).tolist() == [False, False, True]
    assert amortization(log2.task_costs("cont", 1, w), log2.task_costs("base", 1, w)) == pytest.approx(1 - 7 / 20)


def test_missing_task_records_are_rejected():
    log = CostLog([
        CostRecord("cont", 1, 1, "acquisition", "ops", 1.0),
        CostRecord("cont", 1, 3, "acquisition", "ops", 1.0),
        CostRecord("base", 1, 1, "acquisition", "ops", 1.0),
        CostRecord("base", 1, 2, "acquisition", "ops", 1.0),
        CostRecord("base", 1, 3, "acquisition", "ops", 1.0),
    ])
    with pytest.raises(ValueError, match="no cost records for tasks \\[2\\]"):
        log.task_costs("cont", 1)
    assert np.allclose(log.task_costs("base", 1), [0, 1, 1, 1])


def test_record_validation():
    with pytest.raises(ValueError):
        CostRecord("a", 1, 1, "thinking", "ops", 1.0)
    with pytest.raises(ValueError):
        CostRecord("a", 1, 1, "acquisition", "ops", -1.0)


def test_novelty_stratified():
    cc = [3, 1, 10, 1, 10]
    cb = [0, 10, 10, 10, 10]
    novel = [False, False, True, False, True]
    # only tasks 2 and 4 count; setup of both arms kept
    assert novelty_stratified_amortization(cc, cb, novel) == pytest.approx(1 - (3 + 20) / (0 + 20))
    # all-novel mask reduces to A_n
    assert novelty_stratified_amortization(cc, cb, [True] * 5) == pytest.approx(amortization(cc, cb))
    with pytest.raises(ValueError):
        novelty_stratified_amortization(cc, cb, [True] + [False] * 4)


def test_novelty_setup_conservativeness_condition():
    # Def. 8: keeping both setups is conservative (A_nov <= setup-free ratio) iff
    # c0(L) * X_R >= c0(R) * X_L. c0(L) >= c0(R) alone is not enough.
    novel = [False, True, True]

    def free(cc, cb):
        return 1 - (cc[1] + cc[2]) / (cb[1] + cb[2])

    # equal setups, learner worse on novel tasks: A_nov is LARGER (not conservative)
    cc, cb = [10, 50, 50], [10, 25, 25]  # X_L = 100, X_R = 50
    assert novelty_stratified_amortization(cc, cb, novel) > free(cc, cb)
    # reference with no setup: always conservative
    for _ in range(200):
        cc = list(rng.uniform(0, 10, size=3))
        cb = [0.0] + list(rng.uniform(0.1, 10, size=2))
        assert novelty_stratified_amortization(cc, cb, novel) <= free(cc, cb) + 1e-12
    # general case: the cross-multiplied condition decides
    for _ in range(500):
        cc, cb = list(rng.uniform(0, 10, size=3)), list(rng.uniform(0.1, 10, size=3))
        cond = cc[0] * (cb[1] + cb[2]) >= cb[0] * (cc[1] + cc[2])
        assert (novelty_stratified_amortization(cc, cb, novel) <= free(cc, cb) + 1e-12) == cond


def test_probe_curve():
    P = [[10, 20], [8, 16], [5, 10]]
    assert np.allclose(probe_amortization(P), [0.0, 0.2, 0.5])
