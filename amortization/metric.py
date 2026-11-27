"""Core learning-amortization quantities (paper Sections 3-4).

Conventions
-----------
A *per-task cost vector* ``c`` is a 1-D array of length ``N + 1``:

* ``c[0]`` is the one-time cost paid before the first task (setup, seeding a
  library, building indices, ...). It is never optional: a learner that ships
  with a pre-built library must charge its construction here.
* ``c[i]`` for ``i = 1..N`` is the full cost charged to task ``T_i`` until the
  learner first meets the accuracy target on that task (Definition 3).

All costs are non-negative scalars in one declared unit (Definition 2). Use
:meth:`CostLog.task_costs` to obtain such vectors from raw multi-resource logs.
"""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

import numpy as np

#: Cost components of Definition 2. Every record must use one of these.
COMPONENTS = (
    "acquisition",
    "verification",
    "storage",
    "retrieval",
    "maintenance",
    "execution",
)


# ---------------------------------------------------------------------------
# Array-level definitions
# ---------------------------------------------------------------------------

def _as_cost_vector(c: Sequence[float], name: str) -> np.ndarray:
    arr = np.asarray(c, dtype=float)
    if arr.ndim != 1 or arr.size < 2:
        raise ValueError(f"{name} must be 1-D with length N+1 >= 2 (index 0 = setup)")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite costs; record censored tasks at their budget")
    if np.any(arr < 0):
        raise ValueError(f"{name} contains negative costs")
    return arr


def _check_pair(c_cont, c_base):
    cc = _as_cost_vector(c_cont, "c_cont")
    cb = _as_cost_vector(c_base, "c_base")
    if cc.shape != cb.shape:
        raise ValueError("continual and reference cost vectors must cover the same task sequence")
    return cc, cb


def cumulative_cost(c: Sequence[float]) -> np.ndarray:
    """C(n) = sum_{i=0}^{n} c_i for n = 0..N (Definition 4)."""
    return np.cumsum(_as_cost_vector(c, "c"))


def amortization(c_cont: Sequence[float], c_base: Sequence[float], n: Optional[int] = None) -> float:
    """Learning amortization A_n = 1 - C_cont(n) / C_base(n) (Definition 5).

    ``n`` defaults to the full sequence length N. Requires C_base(n) > 0.
    """
    cc, cb = _check_pair(c_cont, c_base)
    N = cc.size - 1
    n = N if n is None else int(n)
    if not 1 <= n <= N:
        raise ValueError(f"n must be in [1, {N}]")
    Cb = cb[: n + 1].sum()
    if Cb <= 0:
        raise ValueError("reference cumulative cost must be positive")
    return 1.0 - cc[: n + 1].sum() / Cb


def amortization_curve(c_cont: Sequence[float], c_base: Sequence[float]) -> np.ndarray:
    """(A_1, ..., A_N)."""
    cc, cb = _check_pair(c_cont, c_base)
    Cc, Cb = np.cumsum(cc), np.cumsum(cb)
    if np.any(Cb[1:] <= 0):
        raise ValueError("reference cumulative cost must be positive for every n >= 1")
    return 1.0 - Cc[1:] / Cb[1:]


def marginal_amortization(c_cont: Sequence[float], c_base: Sequence[float]) -> np.ndarray:
    """Per-task savings a_i = 1 - c_cont,i / c_base,i for i = 1..N (Definition 6)."""
    cc, cb = _check_pair(c_cont, c_base)
    if np.any(cb[1:] <= 0):
        raise ValueError("reference per-task cost must be positive")
    return 1.0 - cc[1:] / cb[1:]


def tail_amortization(c_cont: Sequence[float], c_base: Sequence[float], k: int) -> float:
    """Windowed estimate of the asymptotic amortization A_infinity (Prop. 3).

    Uses only the last ``k`` tasks, so one-time costs (index 0) drop out:
    1 - sum_{i=N-k+1}^{N} c_cont,i / sum_{i=N-k+1}^{N} c_base,i.
    """
    cc, cb = _check_pair(c_cont, c_base)
    N = cc.size - 1
    if not 1 <= k <= N:
        raise ValueError(f"k must be in [1, {N}]")
    den = cb[N - k + 1 :].sum()
    if den <= 0:
        raise ValueError("reference tail cost must be positive")
    return 1.0 - cc[N - k + 1 :].sum() / den


def break_even(c_cont: Sequence[float], c_base: Sequence[float]) -> Optional[int]:
    """Smallest n >= 1 with A_m > 0 for every m in [n, N] (Definition 7).

    Returns ``None`` if A_N <= 0. Requiring positivity on the whole remaining
    horizon avoids reporting a transient crossing as a break-even point.
    """
    A = amortization_curve(c_cont, c_base)
    if A[-1] <= 0:
        return None
    nonpos = np.nonzero(A <= 0)[0]
    return 1 if nonpos.size == 0 else int(nonpos[-1]) + 2


def component_contributions(
    comp_cont: Mapping[str, Sequence[float]],
    comp_base: Mapping[str, Sequence[float]],
    n: Optional[int] = None,
) -> Dict[str, float]:
    """Additive decomposition A_n = sum_k D_k (Proposition 2).

    D_k = (C_base,k(n) - C_cont,k(n)) / C_base(n). A component absent from one
    side is treated as zero cost on that side; negative D_k is an overhead.
    """
    keys = sorted(set(comp_cont) | set(comp_base))
    lengths = {np.asarray(v).size for v in list(comp_cont.values()) + list(comp_base.values())}
    if len(lengths) != 1:
        raise ValueError("all component vectors must have the same length")
    L = lengths.pop()
    zero = np.zeros(L)
    cc = {k: _as_cost_vector(comp_cont.get(k, zero), f"cont[{k}]") for k in keys}
    cb = {k: _as_cost_vector(comp_base.get(k, zero), f"base[{k}]") for k in keys}
    N = L - 1
    n = N if n is None else int(n)
    if not 1 <= n <= N:
        raise ValueError(f"n must be in [1, {N}]")
    Cb = sum(v[: n + 1].sum() for v in cb.values())
    if Cb <= 0:
        raise ValueError("reference cumulative cost must be positive")
    return {k: (cb[k][: n + 1].sum() - cc[k][: n + 1].sum()) / Cb for k in keys}


# ---------------------------------------------------------------------------
# Raw cost logs
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CostRecord:
    """One measured cost increment.

    ``task`` = 0 marks a one-time cost paid before the first task. ``censored``
    marks a task on which the learner exhausted its budget without reaching the
    accuracy target (the recorded amount is then a lower bound, Section 6.3).
    """

    arm: str
    seed: int
    task: int
    component: str
    resource: str
    amount: float
    censored: bool = False

    def __post_init__(self):
        if self.component not in COMPONENTS:
            raise ValueError(f"unknown component {self.component!r}; expected one of {COMPONENTS}")
        if self.task < 0:
            raise ValueError("task index must be >= 0")
        if not (math.isfinite(self.amount) and self.amount >= 0):
            raise ValueError("amount must be finite and non-negative")


class CostLog:
    """A collection of :class:`CostRecord` with helpers to build cost vectors."""

    FIELDS = ("arm", "seed", "task", "component", "resource", "amount", "censored")

    def __init__(self, records: Iterable[CostRecord] = ()):  # noqa: D401
        self.records: List[CostRecord] = list(records)

    # -- I/O ---------------------------------------------------------------
    @classmethod
    def from_csv(cls, path: str | Path) -> "CostLog":
        out = []
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                out.append(
                    CostRecord(
                        arm=row["arm"],
                        seed=int(row["seed"]),
                        task=int(row["task"]),
                        component=row["component"],
                        resource=row["resource"],
                        amount=float(row["amount"]),
                        censored=str(row.get("censored", "0")).strip().lower() in {"1", "true", "yes"},
                    )
                )
        return cls(out)

    def to_csv(self, path: str | Path) -> None:
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(self.FIELDS)
            for r in self.records:
                w.writerow([r.arm, r.seed, r.task, r.component, r.resource, repr(r.amount), int(r.censored)])

    # -- views -------------------------------------------------------------
    def arms(self) -> List[str]:
        return sorted({r.arm for r in self.records})

    def seeds(self) -> List[int]:
        return sorted({r.seed for r in self.records})

    def resources(self) -> List[str]:
        return sorted({r.resource for r in self.records})

    def n_tasks(self) -> int:
        return max(r.task for r in self.records)

    def _price(self, resource: str, weights: Optional[Mapping[str, float]]) -> float:
        if weights is None:
            res = self.resources()
            if len(res) != 1:
                raise ValueError(
                    f"log has several resources {res}; pass weights={{resource: price}} declared in advance, "
                    "or filter to one resource"
                )
            return 1.0
        if resource not in weights:
            raise ValueError(f"no declared price for resource {resource!r}")
        p = float(weights[resource])
        if p < 0:
            raise ValueError("prices must be non-negative")
        return p

    def component_costs(
        self, arm: str, seed: int, weights: Optional[Mapping[str, float]] = None, N: Optional[int] = None
    ) -> Dict[str, np.ndarray]:
        """Scalarized cost per component, each an array of length N+1."""
        N = self.n_tasks() if N is None else N
        out = {k: np.zeros(N + 1) for k in COMPONENTS}
        found = False
        for r in self.records:
            if r.arm == arm and r.seed == seed:
                found = True
                if r.task > N:
                    continue
                out[r.component][r.task] += self._price(r.resource, weights) * r.amount
        if not found:
            raise KeyError(f"no records for arm={arm!r}, seed={seed}")
        return out

    def task_costs(
        self, arm: str, seed: int, weights: Optional[Mapping[str, float]] = None, N: Optional[int] = None
    ) -> np.ndarray:
        """Per-task scalar cost vector c (length N+1) for one arm and seed."""
        return sum(self.component_costs(arm, seed, weights, N).values())

    def matrix(self, arm: str, weights: Optional[Mapping[str, float]] = None, seeds=None) -> np.ndarray:
        """Stack task_costs over seeds -> array of shape (S, N+1)."""
        seeds = self.seeds() if seeds is None else seeds
        N = self.n_tasks()
        return np.vstack([self.task_costs(arm, s, weights, N) for s in seeds])

    def censored(self, arm: str, seed: int) -> np.ndarray:
        """Boolean array (length N+1): task censored for this arm and seed."""
        N = self.n_tasks()
        out = np.zeros(N + 1, dtype=bool)
        for r in self.records:
            if r.arm == arm and r.seed == seed and r.censored:
                out[r.task] = True
        return out
