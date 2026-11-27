"""Reference implementation of the learning-amortization metric.

See ``paper/whitepaper.pdf`` for the definitions. Every function here maps to a
numbered definition or proposition in the paper; the mapping is listed in the
README.
"""

from .metric import (
    COMPONENTS,
    CostLog,
    CostRecord,
    amortization,
    amortization_curve,
    break_even,
    cumulative_cost,
    component_contributions,
    marginal_amortization,
    novelty_stratified_amortization,
    probe_amortization,
    tail_amortization,
)
from .stats import (
    AmortizationEstimate,
    bootstrap_ci,
    delta_method_se,
    estimate,
    log_ratios,
    point_estimate,
    sign_flip_test,
    trend_slope,
)
from .transfer import auc_from_curve, forward_transfer_cw, threshold_cost_integral

__all__ = [
    "COMPONENTS",
    "CostLog",
    "CostRecord",
    "amortization",
    "amortization_curve",
    "break_even",
    "cumulative_cost",
    "component_contributions",
    "marginal_amortization",
    "novelty_stratified_amortization",
    "probe_amortization",
    "tail_amortization",
    "AmortizationEstimate",
    "bootstrap_ci",
    "delta_method_se",
    "estimate",
    "log_ratios",
    "point_estimate",
    "sign_flip_test",
    "trend_slope",
    "auc_from_curve",
    "forward_transfer_cw",
    "threshold_cost_integral",
]

__version__ = "0.1.0"
