"""Reproduce every PacketLM number used in Section 10 of the paper.

Data: cost logs and part-S run summaries copied unmodified (gzip only) from
PacketLM branch g44-canonical-engine at 8994490, docs/evidence/g5*/ (see
SOURCES.md). The amortization values are recomputed with the pinned instrument
(``amortization.metric`` / ``amortization.stats``, unchanged since 70297af,
tag instrument-v1) with 5000 paired-bootstrap resamples, exactly as registered,
and compared with the values printed in PacketLM's docs/G5*.md.

Usage: python case_study/packetlm/reproduce.py [--quick]
  --quick  point estimates only (no bootstrap); used by tests/test_case_study.py
"""

from __future__ import annotations

import csv
import gzip
import io
import random
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from amortization.metric import CostLog  # noqa: E402
from amortization.stats import bootstrap_ci, point_estimate  # noqa: E402

DATA = Path(__file__).resolve().parent / "data"

# (experiment, curriculum, continual arm, reference arm, A, lo, hi, decimals, source)
# Values as printed in PacketLM docs at 8994490.
EXPECTED = [
    ("G51", "comp", "C+maint", "B", -2.872, -3.154, -2.561, 3, "docs/G51.md, Results, compositional table"),
    ("G51", "comp", "C+maint", "P+maint", -0.774, -0.866, -0.665, 3, "docs/G51.md, Results, compositional table"),
    ("G51", "unrel", "C+maint", "B", -5.080, -5.325, -4.859, 3, "docs/G51.md, Results, unrelated table"),
    ("G51", "unrel", "C", "B", -1.15, -1.18, -1.12, 2, "docs/G51.md, decision L3 (verify-cdb4828 G2 note)"),
    ("G53", "comp", "Cb+maint", "Bb", -0.885, -0.981, -0.790, 3, "docs/G53.md, Results"),
    ("G53", "comp", "Cb+maint", "C+maint", 0.534, 0.519, 0.551, 3, "docs/G53.md, Results"),
    ("G53", "comp", "Cb+maint", "Pb+maint", -0.160, -0.208, -0.110, 3, "docs/G53.md, Results"),
    ("G53", "unrel", "Cb+maint", "Bb", -5.065, -5.456, -4.666, 3, "docs/G53.md, Results"),
    ("G53", "unrel", "Cb+maint", "C+maint", 0.010, -0.004, 0.023, 3, "docs/G53.md, Results"),
    ("G54", "comp", "Cl+maint", "Bl", -0.845, -0.920, -0.773, 3, "docs/G54.md, Results"),
    ("G54", "comp", "Cl+maint", "Cb+maint", 0.174, 0.170, 0.178, 3, "docs/G54.md, Results"),
    ("G54", "comp", "Cl+maint", "Pl+maint", -0.305, -0.343, -0.270, 3, "docs/G54.md, Results"),
    ("G54", "unrel", "Cl+maint", "Bl", -3.312, -3.479, -3.163, 3, "docs/G54.md, Results"),
    ("G54", "unrel", "Cl+maint", "Cb+maint", 0.335, 0.322, 0.344, 3, "docs/G54.md, Results"),
    ("G56", "comp", "Cs+maint", "Bs", -1.126, -1.231, -1.039, 3, "docs/G56.md, Results, primary"),
    ("G56", "comp", "Cl+maint", "Bl", -0.698, -0.740, -0.660, 3, "docs/G56.md, Results, secondary"),
    ("G56", "comp", "Cs+maint", "Cl+maint", 0.396, 0.376, 0.417, 3, "docs/G56.md, Results, primary"),
    ("G56", "comp", "Cs+maint", "Ps+maint", -0.531, -0.606, -0.454, 3, "docs/G56.md, Results, primary"),
    ("G56", "comp", "Bs", "Bl", 0.518, 0.503, 0.533, 3, "docs/G56.md, Results, secondary"),
    ("G56", "unrel", "Cs+maint", "Bs", -16.99, -17.35, -16.65, 2, "docs/G56.md, Results, primary"),
    ("G56", "unrel", "Cl+maint", "Bl", -3.159, -3.346, -3.002, 3, "docs/G56.md, Results, secondary"),
    ("G56", "unrel", "Cs+maint", "Cl+maint", 0.704, 0.699, 0.710, 3, "docs/G56.md, Results, primary"),
    ("G56", "unrel", "Bs", "Bl", 0.932, 0.930, 0.933, 3, "docs/G56.md, Results, secondary"),
    ("G57", "comp", "Ci+maint", "Bi", -0.803, -0.904, -0.716, 3, "docs/G57.md, Results, primary"),
    ("G57", "comp", "Ci+maint", "Cs+maint", 0.041, 0.020, 0.062, 3, "docs/G57.md, Results, primary"),
    ("G57", "comp", "Ci+maint", "Pi+maint", -0.420, -0.502, -0.355, 3, "docs/G57.md, Results, secondary"),
    ("G57", "unrel", "Ci+maint", "Bi", -5.867, -6.436, -5.233, 3, "docs/G57.md, Results, primary"),
    ("G57", "unrel", "Ci+maint", "Cs+maint", 0.593, 0.584, 0.601, 3, "docs/G57.md, Results, primary"),
    ("G57", "unrel", "Cs+maint", "Bs", -16.08, -17.08, -15.18, 2, "docs/G57.md, Results, secondary"),
    ("G57b", "comp", "Cj+maint", "Bj", -0.677, -0.887, -0.489, 3, "docs/G57b.md, section 6b"),
    ("G57b", "comp", "Cj+maint", "Ci+maint", 0.041, 0.032, 0.049, 3, "docs/G57b.md, section 6b"),
    ("G57b", "comp", "Cj+maint", "Pj+maint", -0.394, -0.566, -0.226, 3, "docs/G57b.md, section 6b"),
    ("G57b", "comp", "Bj", "Bi", -0.030, -0.053, -0.005, 3, "docs/G57b.md, section 6b"),
    ("G57b", "unrel", "Cj+maint", "Bj", -2.213, -2.377, -2.037, 3, "docs/G57b.md, section 6b"),
    ("G57b", "unrel", "Cj+maint", "Ci+maint", 0.387, 0.378, 0.396, 3, "docs/G57b.md, section 6b"),
    ("G57b", "unrel", "Bj", "Bi", -0.171, -0.232, -0.111, 3, "docs/G57b.md, section 6b"),
    # Unrelated-curriculum reuse contrasts (C vs P), quoted as "at most 2.4%" in Table 4's caption.
    ("G51", "unrel", "C+maint", "P+maint", -0.024, -0.048, -0.001, 3, "docs/G51.md, Results, unrelated table"),
    ("G53", "unrel", "Cb+maint", "Pb+maint", -0.001, -0.013, 0.011, 3, "docs/G53.md, Results"),
    ("G54", "unrel", "Cl+maint", "Pl+maint", -0.015, -0.032, -0.003, 3, "docs/G54.md, Results"),
    ("G56", "unrel", "Cs+maint", "Ps+maint", -0.001, -0.026, 0.029, 3, "docs/G56.md, Results, primary (L2s)"),
    ("G57", "unrel", "Ci+maint", "Pi+maint", -0.001, -0.009, 0.007, 3, "docs/G57.md, Results, secondary"),
    ("G57b", "unrel", "Cj+maint", "Pj+maint", -0.020, -0.037, -0.004, 3, "docs/G57b.md, section 6b"),
]

# Part S (irrelevant-state scaling): (experiment, arm, baseline N, A-like key, value, lo, hi, source)
EXPECTED_SCALE = [
    ("G57", "Xi", 0, 91.9, 86.5, 95.7, "docs/G57.md, Part S (seeds 221-227)"),
    ("G57", "Xs", 0, 156.2, 150.4, 162.8, "docs/G57.md, Part S (seeds 221-227)"),
    ("G57", "Xi", 1000, 17.8296, 17.3312, 18.4131, "docs/G57b.md 4a (G57 files, N=1000 baseline)"),
    ("G57b", "Xs", 0, 160.1, 148.4, 169.1, "docs/G57b.md 6a"),
    ("G57b", "Xi", 0, 91.2, 81.6, 100.0, "docs/G57b.md 6a"),
    ("G57b", "Xj", 0, 3.75, 3.22, 4.20, "docs/G57b.md 6a"),
    ("G57b", "Xs", 1000, 19.59, 19.05, 20.31, "docs/G57b.md 6a"),
    ("G57b", "Xi", 1000, 17.48, 16.67, 18.41, "docs/G57b.md 6a"),
    ("G57b", "Xj", 1000, 2.90, 2.57, 3.20, "docs/G57b.md 6a"),
]


def load(exp: str, cur: str) -> CostLog:
    raw = gzip.decompress((DATA / f"{exp.lower()}_{cur}_total.csv.gz").read_bytes()).decode()
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write(raw)
        name = fh.name
    try:
        return CostLog.from_csv(name)
    finally:
        Path(name).unlink()


def packetlm_boot(vals, reps=5000, seed=0):
    """PacketLM's registered bootstrap for R (benchmarks/g57_scale.py `boot`), reproduced verbatim."""
    rng = random.Random(seed)
    m = sorted(sum(rng.choice(vals) for _ in vals) / len(vals) for _ in range(reps))
    return round(sum(vals) / len(vals), 4), [round(m[int(0.025 * reps)], 4), round(m[int(0.975 * reps) - 1], 4)]


def scale_values(exp: str):
    runs = {}
    with open(DATA / f"{exp.lower()}_scale_runs.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            runs[(r["arm"], int(r["n"]), int(r["seed"]))] = float(r["mean_task_cpu_s"])
    seeds = sorted({s for (_, _, s) in runs})
    out, means = {}, defaultdict(dict)
    for arm in sorted({a for (a, _, _) in runs}):
        for n in sorted({n for (a, n, _) in runs if a == arm}):
            means[arm][n] = 1000 * sum(runs[(arm, n, s)] for s in seeds) / len(seeds)
        nmax = max(means[arm])
        for base in (0, 1000):
            if base in means[arm]:
                out[(arm, base)] = packetlm_boot([runs[(arm, nmax, s)] / runs[(arm, base, s)] for s in seeds])
    return out, means


def derived_checks():
    """Numbers derived in Section 11 from the cost logs (not printed in PacketLM's docs)."""
    import numpy as np

    out = []
    g56u = load("G56", "unrel")
    mixed = point_estimate(g56u.matrix("Cs+maint"), g56u.matrix("Bl"))
    chain = 1 - (1 - point_estimate(g56u.matrix("Cs+maint"), g56u.matrix("Cl+maint"))) * (
        1 - point_estimate(g56u.matrix("Cl+maint"), g56u.matrix("Bl")))
    out.append(("G56 unrel mixed A(Cs+maint || Bl) [Prop. protocol (iv)]", mixed, -0.231, 3))
    out.append(("G56 unrel chain (Cs||Cl)(Cl||Bl) equals mixed", chain - mixed, 0.0, 9))
    g = load("G57b", "comp")
    X, Y = g.matrix("Cj+maint"), g.matrix("Bj")
    chain = 1 - (1 - point_estimate(X, g.matrix("Ci+maint"))) * (1 - point_estimate(g.matrix("Ci+maint"), g.matrix("Bi"))) * (
        1 - point_estimate(g.matrix("Bi"), Y))
    out.append(("G57b comp chain Cj||Ci||Bi||Bj equals A(Cj||Bj) [Prop. chain]", chain - point_estimate(X, Y), 0.0, 9))
    cens = np.array([g.censored("Bj", s) for s in g.seeds()])
    out.append(("G57b comp C_L total (s)", float(X.sum()), 48.37, 2))
    out.append(("G57b comp C_R total (s)", float(Y.sum()), 28.84, 2))
    out.append(("G57b comp B cost on its 5 censored tasks (s)", float(Y[cens].sum()), 2.84, 2))
    out.append(("G57b comp tipping point C_L - C_R (s) [Cor. tipping]", float(X.sum() - Y.sum()), 19.53, 2))
    g51 = load("G51", "comp")
    out.append(("G51 comp C+maint total (s)", float(g51.matrix("C+maint").sum()), 215.8, 1))
    out.append(("G51 comp B total (s)", float(g51.matrix("B").sum()), 55.7, 1))
    return out


def run_derived() -> int:
    bad = 0
    for name, got, want, dec in derived_checks():
        ok = abs(got - want) <= 0.5 * 10 ** (-dec) + 1e-12
        bad += not ok
        print(f"{name}: {got:.6g} (paper {want})  {'ok' if ok else 'MISMATCH'}")
    return bad


def main(argv) -> int:
    quick = "--quick" in argv
    logs, bad = {}, 0
    print(f"{'exp':5} {'cur':5} {'contrast':24} {'A':>9} {'95% CI':>22} {'ratio':>7} {'cens L/R':>9}  match")
    for exp, cur, a, b, A, lo, hi, dec, _src in EXPECTED:
        log = logs.setdefault((exp, cur), load(exp, cur))
        Cc, Cb = log.matrix(a), log.matrix(b)
        p = point_estimate(Cc, Cb)
        # PacketLM's docs round the instrument's 4-decimal report a second time, so allow
        # half a unit in the printed place plus half a unit in the 4th decimal.
        tol = 0.5 * 10 ** (-dec) + 0.5e-4 + 1e-9
        ok = abs(p - A) <= tol
        ci = ("", "")
        if not quick:
            l, h = bootstrap_ci(Cc, Cb, B=5000)
            ok = ok and abs(l - lo) <= tol and abs(h - hi) <= tol
            ci = (f"{l:+.4f}", f"{h:+.4f}")
        cl = sum(int(log.censored(a, s)[1:].sum()) for s in log.seeds())
        cr = sum(int(log.censored(b, s)[1:].sum()) for s in log.seeds())
        bad += not ok
        print(f"{exp:5} {cur:5} {a + ' || ' + b:24} {p:+9.4f} [{ci[0]:>9}, {ci[1]:>9}] {1 - p:6.2f}x {cl:>4}/{cr:<4}  {'ok' if ok else 'MISMATCH'}")
    for exp in ("G57", "G57b"):
        vals, means = scale_values(exp)
        for arm in sorted(means):
            print(exp, arm, "mean task CPU (ms) by N:", {n: round(v, 3) for n, v in sorted(means[arm].items())})
        for e, arm, base, v, lo, hi, _src in EXPECTED_SCALE:
            if e != exp:
                continue
            got = vals[(arm, base)]
            dec = max(len(str(x).split(".")[1]) if "." in str(x) else 0 for x in (v, lo, hi))
            tol = 0.5 * 10 ** (-dec) + 1e-9
            ok = abs(got[0] - v) <= tol and abs(got[1][0] - lo) <= tol and abs(got[1][1] - hi) <= tol
            bad += not ok
            print(f"{exp} {arm} R(16000 vs {base}) = {got[0]} {got[1]}  expected {v} [{lo}, {hi}]  {'ok' if ok else 'MISMATCH'}")
    bad += run_derived()
    print("ALL MATCH" if bad == 0 else f"{bad} MISMATCHES")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
