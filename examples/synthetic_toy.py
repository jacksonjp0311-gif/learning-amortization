"""SYNTHETIC worked example: a toy library learner doing enumerative program search.

Everything produced by this script is synthetic. It is NOT a PacketLM result and
says nothing about any real system; it exists to show the metric, the cost
accounting and the statistics working end to end on a process whose costs are
actually counted (not simulated from a formula).

World. Inputs are Z_16. Six fixed primitive maps. A task is a hidden target map
given by 10 training input/output pairs; 6 held-out inputs form a sealed test
set that the learner never sees. A learner enumerates compositions breadth-first
(depth <= 5) and commits to the first one consistent with the training pairs.
Success means 100% accuracy on the sealed test inputs (alpha = 1.0).

Arms.
  base     empty-memory learner: primitives only, nothing carried between tasks.
  library  continual learner: committed solutions are stored and offered as
           extra building blocks on later tasks (DreamCoder-style, much simplified).

Curricula.
  compositional  each target composes two earlier targets/primitives, so reuse is possible.
  unrelated      each target is an independent depth-3 composition of primitives,
                 so the library can only add branching and overhead.

Cost (elementary operations, one unit price per declared component):
  acquisition   1 op per input when a candidate's outputs are computed
  verification  1 op per training pair compared (with early exit)
  retrieval     1 op each time a stored library entry is fetched for a candidate
  storage       0.01 op per stored table cell per task held (library only)
  maintenance   1 op per cell compared when de-duplicating an insertion
  execution     1 op per sealed test input when the committed map is applied
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from amortization import CostLog, CostRecord, estimate, trend_slope, break_even, tail_amortization  # noqa: E402
from amortization.metric import amortization_curve, component_contributions  # noqa: E402

M = 16
X = np.arange(M)
PRIMS = {
    "inc": (X + 1) % M,
    "dbl": (2 * X) % M,
    "sq": (X * X) % M,
    "xor5": X ^ 5,
    "aff": (3 * X + 1) % M,
    "half": X // 2,
}
MAX_DEPTH = 5
BUDGET = 400_000  # acquisition+verification+retrieval ops per task before censoring
STORAGE_PRICE = 0.01
N_TRAIN = 10


def make_curriculum(kind: str, n_tasks: int, rng: np.random.Generator):
    tables = list(PRIMS.values())
    targets = []
    for _ in range(n_tasks):
        if kind == "compositional":
            pool = tables + targets
            a, b = rng.integers(0, len(pool), size=2)
            t = pool[a][pool[b]]  # apply pool[b] then pool[a]
        elif kind == "unrelated":
            seq = rng.integers(0, len(tables), size=3)
            t = X.copy()
            for j in seq:
                t = tables[j][t]
        else:
            raise ValueError(kind)
        targets.append(t)
    return targets


def solve(target, train, test, blocks, n_lib):
    """Breadth-first search over compositions of ``blocks``.

    ``blocks[:6]`` are primitives, the rest are library entries. Returns
    (committed table or None, cost dict, censored flag).
    """
    cost = dict(acquisition=0.0, verification=0.0, retrieval=0.0)
    n_prim = len(blocks) - n_lib
    frontier = [X]
    spent = 0.0
    for depth in range(1, MAX_DEPTH + 1):
        nxt = []
        for parent in frontier:
            for j, blk in enumerate(blocks):
                if j >= n_prim:
                    cost["retrieval"] += 1
                cand = blk[parent]
                cost["acquisition"] += M if depth < MAX_DEPTH else len(train)
                # verification with early exit
                ok = True
                for x in train:
                    cost["verification"] += 1
                    if cand[x] != target[x]:
                        ok = False
                        break
                spent = cost["acquisition"] + cost["verification"] + cost["retrieval"]
                if ok:
                    return cand, cost, False
                if spent >= BUDGET:
                    return None, cost, True
                if depth < MAX_DEPTH:
                    nxt.append(cand)
        frontier = nxt
    return None, cost, True


def run_arm(arm, targets, splits, seed):
    recs = []
    library = []
    failures = 0
    for i, (t, (train, test)) in enumerate(zip(targets, splits), start=1):
        blocks = list(PRIMS.values()) + (library if arm == "library" else [])
        sol, cost, censored = solve(t, train, test, blocks, len(library) if arm == "library" else 0)
        correct = sol is not None and np.array_equal(sol[test], t[test])
        if not correct:
            censored = True
            failures += 1
        for comp, amt in cost.items():
            recs.append(CostRecord(arm, seed, i, comp, "ops", amt, censored))
        recs.append(CostRecord(arm, seed, i, "execution", "ops", float(len(test)), censored))
        if arm == "library":
            maint = 0.0
            if sol is not None and correct:
                dup = False
                for e in library:
                    maint += M
                    if np.array_equal(e, sol):
                        dup = True
                        break
                if not dup:
                    library.append(sol)
            recs.append(CostRecord(arm, seed, i, "maintenance", "ops", maint, censored))
            recs.append(CostRecord(arm, seed, i, "storage", "ops", STORAGE_PRICE * M * len(library), censored))
    return recs, failures


def experiment(kind, seeds, n_tasks):
    log = []
    fails = {"base": 0, "library": 0}
    for s in seeds:
        rng = np.random.default_rng([s, 0 if kind == "compositional" else 1])
        targets = make_curriculum(kind, n_tasks, rng)
        splits = []
        for _ in targets:
            perm = rng.permutation(M)
            splits.append((perm[:N_TRAIN], perm[N_TRAIN:]))
        for arm in ("base", "library"):
            r, f = run_arm(arm, targets, splits, s)
            log += r
            fails[arm] += f
        # one-time setup: both arms receive the same primitives at zero cost
        for arm in ("base", "library"):
            log.append(CostRecord(arm, s, 0, "acquisition", "ops", 0.0))
    return CostLog(log), fails


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--tasks", type=int, default=12)
    ap.add_argument("--outdir", type=Path, default=ROOT / "examples" / "results")
    ap.add_argument("--figure", type=Path, default=None)
    args = ap.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    seeds = list(range(1, args.seeds + 1))
    summary = {"WARNING": "SYNTHETIC toy example; not a PacketLM or any real-system result."}
    curves = {}
    for kind in ("compositional", "unrelated"):
        log, fails = experiment(kind, seeds, args.tasks)
        log.to_csv(args.outdir / f"{kind}_costs.csv")
        Cc, Cb = log.matrix("library"), log.matrix("base")
        est = estimate(Cc, Cb)
        slope, slope_ci = trend_slope(Cc, Cb)
        mean_c, mean_b = Cc.mean(axis=0), Cb.mean(axis=0)
        comps_c = {k: np.mean([log.component_costs("library", s)[k] for s in seeds], axis=0) for k in log.component_costs("library", 1)}
        comps_b = {k: np.mean([log.component_costs("base", s)[k] for s in seeds], axis=0) for k in log.component_costs("base", 1)}
        contrib = component_contributions(comps_c, comps_b)
        curves[kind] = amortization_curve(mean_c, mean_b)
        summary[kind] = {
            "S": len(seeds),
            "N": args.tasks,
            "A_N": est.point,
            "A_N_ci95": est.ci,
            "A_N_delta_se": est.se_delta,
            "sign_flip_p": est.p_value,
            "geometric_mean_form": est.geometric,
            "tail_A_last4": tail_amortization(mean_c, mean_b, 4),
            "break_even_n_mean_costs": break_even(mean_c, mean_b),
            "trend_slope_log_ratio_per_task": slope,
            "trend_slope_ci95": slope_ci,
            "component_contributions": contrib,
            "censored_or_failed_tasks": fails,
            "total_tasks_per_arm": len(seeds) * args.tasks,
        }
    (args.outdir / "summary.json").write_text(json.dumps(summary, indent=2, default=float))
    print(json.dumps(summary, indent=2, default=float))
    if args.figure is not None:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(5.2, 3.0))
        n = np.arange(1, args.tasks + 1)
        ax.axhline(0, color="0.5", lw=0.8)
        ax.plot(n, curves["compositional"], "o-", label="compositional curriculum")
        ax.plot(n, curves["unrelated"], "s--", label="unrelated curriculum")
        ax.set_xlabel("tasks seen, $n$")
        ax.set_ylabel("$A_n$ (seed-mean costs)")
        ax.set_title("SYNTHETIC toy example (not PacketLM)", fontsize=9)
        ax.legend(frameon=False, fontsize=8)
        fig.tight_layout()
        args.figure.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.figure)


if __name__ == "__main__":
    main()
