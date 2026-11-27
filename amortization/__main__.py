"""Command-line report: ``python -m amortization costs.csv --cont ARM --base ARM``."""

from __future__ import annotations

import argparse
import json

import numpy as np

from .metric import CostLog, amortization_curve, break_even
from .stats import estimate, trend_slope


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="python -m amortization", description="Learning-amortization report from a cost log CSV.")
    ap.add_argument("csv", help="cost log with columns arm,seed,task,component,resource,amount,censored")
    ap.add_argument("--cont", required=True, help="arm name of the continual learner")
    ap.add_argument("--base", required=True, help="arm name of the reference (e.g. empty-memory) learner")
    ap.add_argument("--n", type=int, default=None, help="horizon n (default: full sequence)")
    ap.add_argument("--weights", default=None, help='JSON price vector, e.g. \'{"ops": 1, "bytes": 0.001}\'')
    ap.add_argument("--level", type=float, default=0.95)
    ap.add_argument("--bootstrap", type=int, default=10_000)
    args = ap.parse_args(argv)

    log = CostLog.from_csv(args.csv)
    w = json.loads(args.weights) if args.weights else None
    Cc, Cb = log.matrix(args.cont, w), log.matrix(args.base, w)
    est = estimate(Cc, Cb, n=args.n, level=args.level, B=args.bootstrap)
    print(est)
    cens_c = sum(log.censored(args.cont, s)[1:].sum() for s in log.seeds())
    cens_b = sum(log.censored(args.base, s)[1:].sum() for s in log.seeds())
    print(f"censored tasks: {args.cont}={cens_c}, {args.base}={cens_b}")
    if cens_c:
        print("  note: continual-arm censoring makes the reported A an UPPER bound (optimistic).")
    if cens_b:
        print("  note: reference-arm censoring makes the reported A a LOWER bound (pessimistic).")
    if Cc.shape[1] > 2 and np.all(Cc[:, 1:] > 0) and np.all(Cb[:, 1:] > 0):
        slope, ci = trend_slope(Cc, Cb, B=min(args.bootstrap, 5000))
        print(f"trend of per-task log ratio: {slope:+.4f} per task  [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    mc, mb = Cc.mean(axis=0), Cb.mean(axis=0)
    print("A_n curve (seed-mean costs):", np.array2string(amortization_curve(mc, mb), precision=3))
    print("break-even n (seed-mean costs):", break_even(mc, mb))


if __name__ == "__main__":
    main()
