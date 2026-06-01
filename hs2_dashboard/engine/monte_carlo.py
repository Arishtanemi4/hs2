import numpy as np


def run_monte_carlo(
    n_sims: int = 10_000,
    inflation: float = 5.0,
    scope_risk: float = 35.0,
    political_risk: float = 40.0,
    kpi_score: float = 2.35,
    workforce_stability: float = 55.0,
    euston_prob: float = 30.0,
    seed: int = 42,
) -> dict:
    """
    Calibrated Monte Carlo model for HS2 cost-to-complete.

    Models uncertainty in the remaining ~£55bn of works using a log-normal
    overrun distribution, with each parameter adjusting the distribution mean.
    Calibrated so default inputs produce ~18% positive, ~42% neutral, ~40% negative
    — matching analyst consensus as of May 2026.

    Cluster thresholds:
        Positive  < £90bn total
        Neutral   £90–115bn
        Negative  > £115bn
    """
    rng = np.random.default_rng(seed)

    base_mu    = 0.28
    base_sigma = 0.35

    infl_adj   = (inflation              - 5.0)  / 5.0  *  0.12
    scope_adj  = (scope_risk             - 35.0) / 65.0 *  0.10
    pol_adj    = (political_risk         - 40.0) / 60.0 *  0.08
    kpi_adj    = -(kpi_score             - 2.0)  / 1.5  *  0.12
    wf_adj     = -(workforce_stability   - 50.0) / 50.0 *  0.07
    euston_adj = -(euston_prob / 100)                   *  0.06

    adj_mu = base_mu + infl_adj + scope_adj + pol_adj + kpi_adj + wf_adj + euston_adj

    overrun_factor = rng.lognormal(mean=adj_mu, sigma=base_sigma, size=n_sims)
    overrun_factor = np.clip(overrun_factor, 0.85, 4.0)

    remain_central = 55.0
    total_costs    = 40.0 + remain_central * overrun_factor
    total_costs    = np.clip(total_costs, 50, 200)

    pos_mask = total_costs < 90
    neg_mask = total_costs > 115
    neu_mask = ~pos_mask & ~neg_mask

    cluster_probs = dict(
        pos=float(pos_mask.mean() * 100),
        neu=float(neu_mask.mean() * 100),
        neg=float(neg_mask.mean() * 100),
    )

    horizon_years = 14
    annual_unit   = remain_central / horizon_years

    infl_rate  = np.clip(inflation / 100, 0.01, 0.20)
    infl_sigma = 0.15
    infl_mu_y  = np.log(infl_rate)
    annual_infl = rng.lognormal(infl_mu_y, infl_sigma, size=(n_sims, horizon_years))
    annual_infl = np.clip(annual_infl, 0.005, 0.25) * overrun_factor.reshape(-1, 1) / 1.32

    cumulative      = np.zeros((n_sims, horizon_years + 1))
    cumulative[:, 0] = 40.0
    running          = np.full(n_sims, 40.0)

    for yr in range(horizon_years):
        infl_mult    = np.prod(1 + annual_infl[:, :yr + 1], axis=1)
        step         = annual_unit * infl_mult
        running      = running + np.clip(step, 0.5, 25)
        cumulative[:, yr + 1] = running

    fan_years = list(range(2026, 2026 + horizon_years + 1))
    fan_data  = dict(
        years=fan_years,
        p10=np.percentile(cumulative, 10,  axis=0).tolist(),
        p25=np.percentile(cumulative, 25,  axis=0).tolist(),
        p50=np.percentile(cumulative, 50,  axis=0).tolist(),
        p75=np.percentile(cumulative, 75,  axis=0).tolist(),
        p90=np.percentile(cumulative, 90,  axis=0).tolist(),
    )

    return dict(costs=total_costs, cluster_probs=cluster_probs, fan_data=fan_data)
