import math
import numpy as np
from data.hs2_data import VIABILITY_DATA


def pred_sentiment(cost_bn, km, slope=-0.3703, intercept=-1.1239):
    cpkm = cost_bn / max(km, 1)
    return float(np.clip(slope * np.log(max(cpkm, 0.001)) + intercept, -1.0, 0.1))


def _combined_approval(workforce_k, cost_bn, network_km=400):
    cpkm        = cost_bn / max(network_km, 1)
    base        = -0.3703 * math.log(max(cpkm, 0.001)) - 1.1239
    job_bonus   = min(0.15, max(0, (workforce_k - 15) / 10 * 0.05))
    cpw         = cost_bn / max(workforce_k, 1)
    eff_penalty = max(0, (cpw - 2.0) * 0.08)
    return float(np.clip(base + job_bonus - eff_penalty, -1.0, 0.2))


def _build_viability_scenarios():
    V = VIABILITY_DATA
    scenarios = [
        {"name": "Original full network", "km": 540},
        {"name": "Reduced network",       "km": 400},
        {"name": "Phase 1 only (current)","km": 225},
        {"name": "Core spine only",       "km": 160},
    ]
    for sc in scenarios:
        sc["max_cost"]     = round(V["threshold_cpkm"] * sc["km"], 1)
        sc["current_cpkm"] = round(V["cost_mid"][-1] / sc["km"], 3)
        sc["current_sent"] = max(-1.0, min(0.1, round(
            float(V["slope"] * math.log(max(V["cost_mid"][-1] / sc["km"], 0.001))
                  + V["intercept"]), 2)))
    return scenarios
