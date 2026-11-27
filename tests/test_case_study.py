"""Spot-check that the PacketLM case-study data reproduce the paper's numbers (fast subset).

The full check (all 42 contrasts with bootstrap intervals, 9 scaling ratios and the
derived numbers) is `python case_study/packetlm/reproduce.py`.
"""

import importlib.util
from pathlib import Path

import pytest

from amortization.stats import point_estimate

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reproduce", ROOT / "case_study" / "packetlm" / "reproduce.py")
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)


@pytest.mark.parametrize("exp,cur", [("G51", "comp"), ("G57b", "unrel")])
def test_primary_point_estimates(exp, cur):
    log = rep.load(exp, cur)
    rows = [r for r in rep.EXPECTED if r[0] == exp and r[1] == cur]
    assert rows
    for _, _, a, b, A, _, _, dec, _ in rows:
        assert point_estimate(log.matrix(a), log.matrix(b)) == pytest.approx(A, abs=0.5 * 10 ** (-dec) + 0.5e-4)


def test_scaling_ratios():
    vals, _ = rep.scale_values("G57b")
    assert vals[("Xj", 1000)][0] == pytest.approx(2.90, abs=0.005)
    assert vals[("Xi", 1000)][0] == pytest.approx(17.48, abs=0.005)
    assert vals[("Xj", 0)][0] == pytest.approx(3.75, abs=0.005)
