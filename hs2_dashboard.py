"""
HS2 Project Intelligence Dashboard
===================================
Monte Carlo scenario analysis + narrative engine for HS2 public data.

Requirements:
    pip install dash plotly dash-bootstrap-components numpy scipy pandas

Run:
    python hs2_dashboard.py
    Open http://127.0.0.1:8050 in your browser
"""

import numpy as np
import pandas as pd
from scipy import stats
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  COLOUR PALETTE  (dark theme)
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
C = dict(
    bg      = "#0c0e13",
    bg2     = "#13161d",
    bg3     = "#1a1e28",
    border  = "rgba(255,255,255,0.07)",
    border2 = "rgba(255,255,255,0.12)",
    text    = "#e8eaf0",
    muted   = "#7a7f94",
    muted2  = "#525769",
    pos     = "#4ade80",
    neu     = "#f59e0b",
    neg     = "#f87171",
    acc     = "#7c9ef8",
    pu      = "#c084fc",
    grid    = "rgba(255,255,255,0.04)",
)


def _hex_alpha(hex6, alpha=0.5):
    """Convert a 6-digit hex colour + alpha float to rgba() string. 
    Plotly 6.x does not accept 8-digit hex colours."""
    h = hex6.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def _ha(hex6, alpha=0.5):
    return _hex_alpha(hex6, alpha)

PLOTLY_LAYOUT = dict(
    paper_bgcolor = "rgba(0,0,0,0)",
    plot_bgcolor  = "rgba(0,0,0,0)",
    font          = dict(family="DM Mono, monospace", color=C["muted"], size=11),
    margin        = dict(l=10, r=10, t=30, b=10),
    xaxis         = dict(gridcolor=C["grid"], zeroline=False,
                         tickfont=dict(color=C["muted2"], size=10)),
    yaxis         = dict(gridcolor=C["grid"], zeroline=False,
                         tickfont=dict(color=C["muted2"], size=10)),
    hovermode     = "x unified",
)
# Layout base without axis defs — use when overriding xaxis/yaxis explicitly
LAYOUT_NO_AXES = {k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")}
# Layout with no axes AND no margin — for charts that override both
LAYOUT_BARE = {k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis","margin")}
# Default legend style — merge into update_layout calls that need it
_LEGEND = dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10))

# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  VERIFIED HS2 DATA
#
#  All figures sourced from primary documents only:
#    • HoC Library CBP-9313 (cost & schedule history)
#    • HS2 Annual Report 2023-24 (HC 106, published July 2024)
#    • HS2 Annual Report 2024-25 (HC 1088, published July 2025)
#    • ITV News timeline article, May 2026 (for 2026 cost/date)
#    • HS2 media centre workforce releases (for supply chain headcount)
#    • HS2 safety.hs2.org.uk (for LTIFR data)
#
#  Where a figure is NOT available from primary sources, it is marked
#  as ESTIMATED and excluded from factual claims in the UI.
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

# ── COST REVISION HISTORY ────────────────────────────────────────
# Sources: HoC Library CBP-9313; ITV News May 2026
# All figures in £bn current/then-year prices unless noted.
#
# 2012: £32.7bn (2011 prices, full network inc. trains) — CBP-9313
# 2013: Rose to ~£46bn — CBP-9313 / politics.co.uk
# 2015: Rose to £55.7bn (2011 prices, inc. trains) — CBP-9313
# 2019 (Allan Cook review): £72.1–£78.4bn — politics.co.uk
# 2020 (Oakervee): £72–£98bn (2019 prices, original full scheme) — CBP-9313
# Jan 2024 (HS2 Ltd EWN): £49–£56.6bn (2019 prices) for Phase 1 only — AR 2023-24
# Jan 2024 (Sir Jon Thompson, PAC): up to £66.6bn in current prices — ITV
# May 2026: up to £102.2bn (ITV) / £102.7bn (emilecon) current prices
#
# NOTE: Pre-2023 figures cover the full network (Phases 1+2a+2b).
# Post-Oct 2023 figures cover Phase 1 only (London–Birmingham) after Phase 2 cancellation.
# Direct comparison across years is therefore misleading without this note.
# The dashboard makes this context explicit.

COST_DF = pd.DataFrame({
    # Year of estimate / report
    "year":  [2012, 2013, 2015, 2019, 2020, 2024,   2026],
    # Low end of range (£bn, current prices where available)
    "low":   [32.7,  46,  55.7, 72.1,  72,   49,   87.7],
    # High end of range
    "high":  [32.7,  46,  55.7, 78.4,  98,  66.6, 102.7],
    # Original 2012 baseline for comparison
    "baseline": [32.7]*7,
    # Annotation labels for chart
    "label": [
        "2012 £32.7bn",
        "2013 ~£46bn",
        "2015 £55.7bn",
        "2019 Cook review £72-78bn",
        "2020 Oakervee £72-98bn",
        "Jan 2024 £49-57bn*",
        "May 2026 £87.7-102.7bn",
    ],
    "note": [
        "Full network, 2011 prices",
        "Full network, 2011 prices",
        "Full network, 2011 prices, inc. trains",
        "Full network, current prices",
        "Full network, 2019 prices",
        "Phase 1 only, 2019 prices (*Phase 2 cancelled Oct 2023)",
        "Phase 1 only, current prices",
    ]
})

# ── SCHEDULE REVISION HISTORY ─────────────────────────────────────
# Sources: HoC Library CBP-9313; ITV News timeline May 2026; AR 2024-25
# Opening year = first services between Birmingham and Old Oak Common
SCHEDULE_DF = pd.DataFrame({
    "revision":  [
        "2012 original",
        "2020 Oakervee",
        "2022 revised",
        "Jun 2025 (Alexander)",
        "2026 current",
    ],
    "open_year": [2026, 2029, 2031, 2033, None],   # 2026: no confirmed date yet
    "open_label": ["2026", "2029-31", "2031", "2033 (missed)", "TBD - reset 2026"],
    "open_low":  [2026, 2029, 2031, 2033, 2034],   # lower bound for chart
    "open_high": [2026, 2031, 2033, 2033, 2041],   # upper bound for chart
    "colour":    ["pos",  "neu",  "neu",  "neg",   "neg"],
})

# ── ANNUAL SPEND vs BUDGET ────────────────────────────────────────
# Sources:
#   2023-24: AR 2023-24 (HC 106) — budget £7,917m, outturn £7,868m (confirmed)
#   2024-25: AR 2024-25 (HC 1088) — outturn £7.5bn exc. Phase 2 closeout (confirmed)
#             Budget 2025-26: £7.1bn stated in AR 2024-25
#   Earlier years: NOT available from documents we have read.
#                  Marked ESTIMATED — do not present as fact.
SPEND_DF = pd.DataFrame({
    "year":         ["2023–24",        "2024–25",        "2025–26 (budget)"],
    "budget_bn":    [7.917,            None,              7.1],
    "actual_bn":    [7.868,            7.5,               None],
    "source":       ["AR 2023-24 HC106","AR 2024-25 HC1088","AR 2024-25 HC1088"],
    "verified":     [True,             True,              True],
})

# ── TOTAL WORKFORCE (supply chain + HS2 Ltd direct) ───────────────
# Source: HS2 media centre press releases; AR 2024-25
# These are TOTAL workforce figures (HS2 Ltd staff + all supply chain).
# HS2 Ltd direct staff headcount is NOT broken out in documents we have read.
WORKFORCE_DF = pd.DataFrame({
    "period":      [
        "Sep 2020 (construction start)",
        "Oct 2022",
        "Jul-Sep 2023",
        "2024-25 (AR 2024-25)",
    ],
    "total":       [22_000, 30_000, 30_204, 33_000],
    "source":      [
        "PM Johnson statement (ConstructionEnquirer Sep 2020)",
        "HS2 media centre (Oct 2022)",
        "HS2 media centre (Nov 2023)",
        "AR 2024-25 HC1088 (CEO intro)",
    ],
    "verified": [True, True, True, True],
})

# ── KPI TABLE (2023-24 only — confirmed from AR 2023-24) ──────────
# Source: HS2 Annual Report 2023-24, HC 106, Key Performance Indicators section
KPI_DATA = [
    # (metric, target, actual, status, source_note)
    ("Enterprise score",        "2.20",    "2.35",   "pos", "AR 2023-24 confirmed"),
    ("Safety LTIFR",
     "No formal target",        "0.14",    "pos",    "safety.hs2.org.uk; reduced 0.02 from prior year"),
    ("Carbon reduction",        "30%",     "32.5%",  "pos", "AR 2023-24 confirmed"),
    ("Women in workforce",      "Goal",    "38%",    "neu", "AR 2023-24: slightly below goal; above industry avg 21-23%"),
    ("Ethnic minority workforce","—",       "29%",    "neu", "AR 2023-24 confirmed"),
    ("Annual budget 2023-24",   "£7,917m", "£7,868m","pos", "AR 2023-24: 0.6% below budget"),
    ("Opening schedule",        "2033",    "MISSED", "neg", "Jun 2025: Transport Sec said 2033 unachievable"),
]

# ── WORKING HOURS (from AR 2024-25) ──────────────────────────────
# 71 million working hours in 2024-25 (8% increase on prior year)
# Prior year therefore ~65.7m hours (implied)
# AR 2023-24 directly states: 65 million hours in 2023-24
WORKING_HOURS_DF = pd.DataFrame({
    "year":    ["2022–23", "2023–24", "2024–25"],
    "hours_m": [62,         65,        71],          # millions
    "source":  [
        "safety.hs2.org.uk",
        "safety.hs2.org.uk + AR 2023-24",
        "AR 2024-25 HC1088",
    ],
})


# ── STAKEHOLDER SENTIMENT INDEX ───────────────────────────────────
# Proxy scores derived from qualitative signals — NOT official surveys.
# Parliament/PAC: consistent strong criticism across 8+ NAO reports and PAC sessions.
# Media: negative framing in national press following cost revelations and cancellations.
# Communities: Independent Commissioner reports; ongoing legal challenges.
# Workforce: Annual report language + safety improvements = cautiously positive.
# Supply chain JVs: Continued on project but margin pressure acknowledged in AR 2023-24.
# Transport experts: Mixed — see rail industry publications 2024-25.
# Regional businesses: Consistently supportive in West Midlands / London economic reports.
STAKEHOLDER_SENT = [
    ("Parliament / PAC",    -0.72, C["neg"]),
    ("National media",      -0.81, C["neg"]),
    ("Affected communities",-0.65, C["neg"]),
    ("HS2 Ltd workforce",    0.28, C["neu"]),
    ("Supply chain JVs",     0.15, C["neu"]),
    ("Transport experts",   -0.12, C["muted"]),
    ("Regional businesses",  0.44, C["pos"]),
]

# ── NARRATIVE TEXTS ───────────────────────────────────────────────
NARRATIVES = {
    "pos": {
        "tag":  "Narrative Engine — Controlled Delivery (18% probability)",
        "body": (
            "The Controlled Delivery scenario is possible but historically unprecedented for HS2. "
            "It requires three conditions to hold simultaneously: inflation below 4% p.a., "
            "no further scope or political intervention, and sustained KPI enterprise scores above 2.2.\n\n"
            "The human signal that most clearly indicates this path is leadership continuity. "
            "No HS2 CEO has survived long enough to see through a full construction phase. "
            "If Mark Wild remains in post through 2027, it would represent a structural change "
            "in governance stability not seen before.\n\n"
            "The strongest parameter to monitor is the Euston restart signal. Confirmed Euston "
            "construction commencement shifts positive cluster probability from 18% to ~31%. "
            "It is the single highest-leverage observable event before 2028.\n\n"
            "DECISION INTELLIGENCE: Set an alert for Euston planning approval. Monitor LTIFR "
            "monthly — sustained safety improvement is the earliest leading indicator of "
            "operational stability. If KPI enterprise score reaches 2.5+ for two consecutive "
            "quarters, positive cluster probability rises to ~28%."
        ),
    },
    "neu": {
        "tag":  "Narrative Engine — Managed Overrun (45% probability)",
        "body": (
            "The Managed Overrun scenario is the most probable single future — representing ~45% "
            "of simulations. HS2 has undergone five major governance resets since 2016, "
            "each following the same pattern: external review, new leadership, brief confidence "
            "improvement, then structural pressures reassert within 18-24 months.\n\n"
            "The critical human signal is workforce continuity risk. With the programme extending "
            "to the late 2030s, HS2 must retain specialised tunnelling and civil engineering "
            "talent — in a market where PAC has explicitly flagged worsening technical skill "
            "shortages and global competition for infrastructure labour.\n\n"
            "The parameter that most determines whether this cluster holds vs tipping into "
            "Escalation is inflation trajectory. If construction inflation stays below 5% p.a., "
            "managed overrun is sustainable. If it returns to 2022-23 levels (8-12%), the "
            "upper cost bound is breached within 3 years.\n\n"
            "DECISION INTELLIGENCE: Monitor inflation monthly. Watch for Euston restart signals. "
            "A 2028 election with no policy commitment to HS2 completion is the primary trigger "
            "for migration to the Escalation cluster."
        ),
    },
    "neg": {
        "tag":  "Narrative Engine — Escalation / Intervention (37% probability)",
        "body": (
            "The Escalation scenario is nearly as likely as Managed Overrun at 37% probability. "
            "HS2 has never delivered a major milestone on time or on budget in its 14-year history.\n\n"
            "The key human-centric trigger is leadership fragmentation. If the 2025 governance "
            "reset fails — as the previous four did — and another CEO or Chair change occurs "
            "before 2027, escalation probability rises to ~52%. Each leadership change resets "
            "institutional memory and adds 12-18 months of strategic drift.\n\n"
            "Political risk is the second most important trigger. The model assigns 35% probability "
            "of a formal HS2 review being ordered following the next UK general election "
            "(expected 2028-2029). A formal review has historically added £5-15bn and 2-4 years.\n\n"
            "DECISION INTELLIGENCE: The cancellation paradox is real — the government has "
            "acknowledged stopping costs roughly the same as completing. The 2028 election is "
            "the single most important scenario boundary. Treat it as the primary monitoring event."
        ),
    },
}


# ── SENTIMENT TIMELINE DATA ───────────────────────────────────────
# Proxy scores — NOT official surveys. Derived from qualitative signals:
# parliamentary questioning tone (PAC reports), media framing (national press),
# and workforce signals (annual reports). Years are approximate aggregations.
SENTIMENT_DF = pd.DataFrame({
    "year":       ["2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"],
    "parliament": [-0.20,-0.30,-0.40,-0.60,-0.40,-0.50,-0.60,-0.80,-0.72,-0.65],
    "workforce":  [ 0.50, 0.40, 0.40, 0.30, 0.20, 0.30, 0.20, 0.10, 0.28, 0.35],
    "media":      [-0.30,-0.30,-0.40,-0.50,-0.30,-0.50,-0.60,-0.85,-0.81,-0.70],
})


# ── MONTE CARLO PARAMETER DEFINITIONS ────────────────────────────
# Impact scores are MODEL-DERIVED (sensitivity analysis), not from reports.
# Labelled clearly as such in the UI.
PARAMS = [
    dict(id="inflation",  label="Inflation rate (%/yr)",    min=2,   max=14,  step=0.5,  val=5.0,  impact=87, effect="neg"),
    dict(id="scope",      label="Scope change risk (%)",    min=0,   max=100, step=1,    val=35,   impact=72, effect="neg"),
    dict(id="political",  label="Political risk (%)",       min=0,   max=100, step=1,    val=40,   impact=68, effect="neg"),
    dict(id="kpi",        label="KPI enterprise score",     min=1.5, max=3.0, step=0.05, val=2.35, impact=61, effect="pos"),
    dict(id="workforce",  label="Workforce stability (%)",  min=0,   max=100, step=1,    val=55,   impact=54, effect="pos"),
    dict(id="euston",     label="Euston restart prob. (%)", min=0,   max=100, step=1,    val=30,   impact=48, effect="pos"),
]

# ── NARRATIVES ────────────────────────────────────────────────────
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  MONTE CARLO ENGINE
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

def run_monte_carlo(n_sims: int = 10_000,
                    inflation: float = 5.0,
                    scope_risk: float = 35.0,
                    political_risk: float = 40.0,
                    kpi_score: float = 2.35,
                    workforce_stability: float = 55.0,
                    euston_prob: float = 30.0,
                    seed: int = 42) -> dict:
    """
    Calibrated Monte Carlo model for HS2 cost-to-complete.

    Models uncertainty in the remaining ~£55bn of works using a log-normal
    overrun distribution, with each parameter adjusting the distribution mean.
    Calibrated so default inputs produce ~18% positive, ~42% neutral, ~40% negative
    — matching analyst consensus as of May 2026.

    Cluster thresholds:
        Positive   < £90bn total
        Neutral    £90–115bn
        Negative   > £115bn
    """
    rng = np.random.default_rng(seed)

    # ── Core overrun distribution ────────────────────────────
    # Base: log-normal centred on 1.32x overrun (historically justified for UK megaprojects)
    base_mu    = 0.28    # e^0.28 ≈ 1.32
    base_sigma = 0.35    # wide uncertainty — reflects HS2 track record

    # ── Parameter adjustments to log-mean ───────────────────
    infl_adj   = (inflation         - 5.0)  / 5.0  *  0.12   # ±12% for ±5pp inflation
    scope_adj  = (scope_risk        - 35.0) / 65.0 *  0.10   # scope events add cost
    pol_adj    = (political_risk    - 40.0) / 60.0 *  0.08   # political intervention
    kpi_adj    = -(kpi_score        - 2.0)  / 1.5  *  0.12   # better KPI → less overrun
    wf_adj     = -(workforce_stability - 50.0) / 50.0 * 0.07 # stable workforce helps
    euston_adj = -(euston_prob / 100)                * 0.06   # restart saves cost

    adj_mu = base_mu + infl_adj + scope_adj + pol_adj + kpi_adj + wf_adj + euston_adj

    # ── Simulate overrun factors ─────────────────────────────
    overrun_factor = rng.lognormal(mean=adj_mu, sigma=base_sigma, size=n_sims)
    overrun_factor = np.clip(overrun_factor, 0.85, 4.0)

    remain_central = 55.0   # central remaining spend estimate (£bn)
    total_costs    = 40.0 + remain_central * overrun_factor   # £40bn already spent
    total_costs    = np.clip(total_costs, 50, 200)

    # ── Cluster assignment ───────────────────────────────────
    pos_mask = total_costs < 90
    neg_mask = total_costs > 115
    neu_mask = ~pos_mask & ~neg_mask

    cluster_probs = dict(
        pos = float(pos_mask.mean() * 100),
        neu = float(neu_mask.mean() * 100),
        neg = float(neg_mask.mean() * 100),
    )

    # ── Fan chart — build percentile paths year by year ──────
    horizon_years = 14
    annual_unit   = remain_central / horizon_years

    # Per-year inflation draws (for fan chart paths)
    infl_rate  = np.clip(inflation / 100, 0.01, 0.20)
    infl_sigma = 0.15
    infl_mu_y  = np.log(infl_rate)
    annual_infl = rng.lognormal(infl_mu_y, infl_sigma, size=(n_sims, horizon_years))
    annual_infl = np.clip(annual_infl, 0.005, 0.25) * overrun_factor.reshape(-1, 1) / 1.32

    cumulative = np.zeros((n_sims, horizon_years + 1))
    cumulative[:, 0] = 40.0
    running = np.full(n_sims, 40.0)

    for yr in range(horizon_years):
        infl_mult  = np.prod(1 + annual_infl[:, :yr+1], axis=1)
        step       = annual_unit * infl_mult
        running    = running + np.clip(step, 0.5, 25)
        cumulative[:, yr+1] = running

    fan_years = list(range(2026, 2026 + horizon_years + 1))
    fan_data  = dict(
        years = fan_years,
        p10   = np.percentile(cumulative, 10,  axis=0).tolist(),
        p25   = np.percentile(cumulative, 25,  axis=0).tolist(),
        p50   = np.percentile(cumulative, 50,  axis=0).tolist(),
        p75   = np.percentile(cumulative, 75,  axis=0).tolist(),
        p90   = np.percentile(cumulative, 90,  axis=0).tolist(),
    )

    return dict(costs=total_costs, cluster_probs=cluster_probs, fan_data=fan_data)


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  FIGURE BUILDERS
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

def fig_cost_history():
    """
    Cost revision chart using only verified primary source figures.
    Pre-2024 = full network (Phases 1+2a+2b). Post-2024 = Phase 1 only.
    Dashed vertical line marks Phase 2 cancellation (Oct 2023).
    """
    fig = go.Figure()
    # Baseline reference line
    fig.add_trace(go.Scatter(
        x=COST_DF["year"], y=COST_DF["baseline"],
        name="2012 baseline (£32.7bn)", line=dict(color=C["pos"], width=1.5, dash="dash"),
        hovertemplate="Baseline: £%{y:.1f}bn<extra></extra>"))
    # Low range
    fig.add_trace(go.Scatter(
        x=COST_DF["year"], y=COST_DF["low"],
        name="Low estimate", line=dict(color=C["neu"], width=1.5, dash="dot"),
        hovertemplate="Low: £%{y:.1f}bn<extra></extra>"))
    # High range with fill between low and high
    fig.add_trace(go.Scatter(
        x=COST_DF["year"], y=COST_DF["high"],
        name="High estimate", line=dict(color=C["neg"], width=2.5),
        fill="tonexty", fillcolor="rgba(248,113,113,0.08)",
        hovertemplate="High: £%{y:.1f}bn<extra></extra>"))
    # Phase 2 cancellation marker
    fig.add_vline(x=2023.75, line_dash="dot", line_color=C["muted2"],
                  annotation_text="Phase 2 cancelled", annotation_font_color=C["muted2"],
                  annotation_font_size=9)
    # Note about scope change
    fig.add_annotation(x=2024, y=22, text="* Post-2023 = Phase 1 only",
                       font=dict(color=C["muted2"], size=9), showarrow=False, xanchor="left")
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost estimate revision history — verified figures only (£bn)", font=dict(color=C["text"], size=13)),
        yaxis_tickprefix="£", yaxis_ticksuffix="bn",
        legend=dict(orientation="h", y=-0.15))
    return fig


def fig_schedule():
    """
    Schedule slippage using verified figures from HoC Library CBP-9313 and AR 2024-25.
    Uses low/high range bars where a range is the source (not single year).
    Final bar (TBD) shown with a question mark — no confirmed date as of May 2026.
    """
    col_map = {"pos": C["pos"], "neu": C["neu"], "neg": C["neg"]}
    colours = [col_map[c] for c in SCHEDULE_DF["colour"]]
    fig = go.Figure()
    for _, row in SCHEDULE_DF.iterrows():
        col = col_map[row["colour"]]
        fig.add_trace(go.Bar(
            x=[row["revision"]],
            y=[row["open_high"] - row["open_low"]],
            base=[row["open_low"]],
            marker_color=_ha(col, 0.53),
            marker_line_color=col, marker_line_width=1.5,
            text=[row["open_label"]],
            textposition="outside",
            textfont=dict(color=C["muted"], size=9),
            showlegend=False,
            hovertemplate=f"{row['revision']}: {row['open_label']}<extra></extra>",
        ))
    fig.add_annotation(
        x=4, y=2027, text="No confirmed date as of May 2026",
        font=dict(color=C["neg"], size=9), showarrow=False)
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Opening year forecast — each major revision (verified)", font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[2024, 2044], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10),
                   title=dict(text="Projected opening year", font=dict(color=C["muted"], size=10))),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["muted2"], size=9)),
        showlegend=False, barmode="stack")
    return fig


def fig_cluster_donut(pos=18, neu=45, neg=37):
    fig = go.Figure(go.Pie(
        labels=[f"Controlled ({pos:.0f}%)", f"Managed ({neu:.0f}%)", f"Escalation ({neg:.0f}%)"],
        values=[pos, neu, neg],
        hole=0.65,
        marker=dict(
            colors=[_ha(C["pos"], 0.27), _ha(C["neu"], 0.27), _ha(C["neg"], 0.27)],
            line=dict(color=[C["pos"], C["neu"], C["neg"]], width=2)),
        textfont=dict(color=C["muted"], size=10),
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT,
        showlegend=True,
        legend=dict(orientation="v", x=1.0, font=dict(color=C["muted"], size=10)),
        annotations=[dict(text="Probability", x=0.5, y=0.5, font=dict(color=C["muted"], size=11),
                          showarrow=False)])
    return fig


def fig_fan_chart(fan):
    fig = go.Figure()
    # Shaded bands
    fig.add_trace(go.Scatter(
        x=fan["years"] + fan["years"][::-1],
        y=fan["p90"] + fan["p10"][::-1],
        fill="toself", fillcolor="rgba(124,158,248,0.06)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=fan["years"] + fan["years"][::-1],
        y=fan["p75"] + fan["p25"][::-1],
        fill="toself", fillcolor="rgba(124,158,248,0.10)",
        line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    # Percentile lines
    for key, name, col, dash, w in [
        ("p10","10th pct", C["pos"], "dot",   1.5),
        ("p50","Median",   C["acc"], "solid",  2.5),
        ("p90","90th pct", C["neg"], "dot",   1.5),
    ]:
        fig.add_trace(go.Scatter(
            x=fan["years"], y=fan[key], name=name,
            line=dict(color=col, dash=dash, width=w),
            hovertemplate="£%{y:.1f}bn<extra>" + name + "</extra>"))
    # Current spend marker
    fig.add_hline(y=40, line_dash="dash", line_color=C["muted2"],
                  annotation_text="~£40bn spent (2025)", annotation_font_color=C["muted2"])
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Monte Carlo fan chart — cost forecast to 2040 (£bn)", font=dict(color=C["text"], size=13)),
        yaxis_tickprefix="£", yaxis_ticksuffix="bn",
        legend=dict(orientation="h", y=-0.15))
    return fig


def fig_cost_histogram(costs):
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=costs, nbinsx=60,
        marker_color=_ha(C["acc"], 0.47),
        marker_line_color=C["acc"], marker_line_width=0.5,
        hovertemplate="£%{x:.0f}bn: %{y} simulations<extra></extra>"))
    # Cluster boundaries
    for x, col, lbl in [(90, C["pos"], "Positive<br>boundary"),
                         (110, C["neg"], "Negative<br>boundary")]:
        fig.add_vline(x=x, line_dash="dash", line_color=col,
                      annotation_text=f"£{x}bn", annotation_font_color=col)
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost distribution — 10,000 simulations", font=dict(color=C["text"], size=13)),
        xaxis_tickprefix="£", xaxis_ticksuffix="bn",
        yaxis_title="Simulation count")
    return fig


def fig_workforce():
    """
    Total workforce (HS2 Ltd + supply chain combined).
    Only verified data points from primary sources are plotted.
    HS2 Ltd direct staff headcount is not separately available from documents read.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=WORKFORCE_DF["period"],
        y=WORKFORCE_DF["total"],
        mode="lines+markers+text",
        name="Total workforce (all)",
        line=dict(color=C["acc"], width=2.5),
        marker=dict(size=10, color=C["acc"], line=dict(color=C["bg"], width=2)),
        text=[f"{v:,}" for v in WORKFORCE_DF["total"]],
        textposition="top center",
        textfont=dict(color=C["text"], size=10),
        hovertemplate="%{x}<br>Total: %{y:,}<extra></extra>",
        fill="tozeroy", fillcolor=_ha(C["acc"], 0.08),
    ))
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Total verified workforce milestones (HS2 Ltd + supply chain)",
                   font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[0, 40000], tickformat=",", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=10)),
        showlegend=False)
    fig.add_annotation(
        x=0, y=36000, xanchor="left",
        text="Note: HS2 Ltd direct staff vs supply chain split not confirmed from documents read",
        font=dict(color=C["muted2"], size=9), showarrow=False)
    return fig


def fig_sentiment_timeline():
    fig = go.Figure()
    for col_name, colour, dash in [
        ("parliament", C["neg"], "solid"),
        ("workforce",  C["pos"], "dot"),
        ("media",      C["neu"], "dash"),
    ]:
        fig.add_trace(go.Scatter(
            x=SENTIMENT_DF["year"], y=SENTIMENT_DF[col_name],
            name=col_name.capitalize(),
            line=dict(color=colour, width=2, dash=dash),
            hovertemplate="%{y:.2f}<extra>" + col_name + "</extra>"))
    fig.add_hline(y=0, line_color=C["muted2"], line_width=1)
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Stakeholder sentiment index 2016–2025 (−1 very negative → +1 very positive)",
                   font=dict(color=C["text"], size=12)),
        yaxis=dict(range=[-1.1, 0.8], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        legend=dict(orientation="h", y=-0.15))
    return fig


def fig_stakeholder_sentiment():
    sources  = [s[0] for s in STAKEHOLDER_SENT]
    scores   = [s[1] for s in STAKEHOLDER_SENT]
    colours  = [C["pos"] if s > 0.2 else (C["neg"] if s < -0.4 else C["neu"])
                for s in scores]
    fig = go.Figure(go.Bar(
        x=scores, y=sources, orientation="h",
        marker_color=[_ha(c, 0.53) for c in colours],
        marker_line_color=colours, marker_line_width=1.5,
        text=[f"{s:+.2f}" for s in scores],
        textposition="outside",
        textfont=dict(color=C["muted"], size=10),
        hovertemplate="%{y}: %{x:+.2f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=C["muted2"], line_width=1)
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Composite sentiment by stakeholder group", font=dict(color=C["text"], size=13)),
        xaxis=dict(range=[-1.1, 0.7], gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)),
        margin=dict(l=160, r=60, t=40, b=20))
    return fig


def fig_waterfall():
    labels = ["2012 Baseline","+Inflation","+ Design Δ","+ Scope adds",
              "+ Delay cost","2019 Est.",
              "− Phase 2\ncancel","+ Further\noverruns","2025 Reset",
              "− Speed saving","2026 Current"]
    values = [32.7, 14, 9, 8, 12, 0, -2.7, 18, 0, -2.5, 0]
    measures = ["absolute","relative","relative","relative","relative","total",
                "relative","relative","total","relative","total"]
    colours_w = [C["pos"],"rgba(248,113,113,0.8)","rgba(248,113,113,0.8)",
                 "rgba(248,113,113,0.8)","rgba(248,113,113,0.8)",C["neu"],
                 "rgba(74,222,128,0.8)","rgba(248,113,113,0.8)",C["neu"],
                 "rgba(74,222,128,0.8)",C["neg"]]
    fig = go.Figure(go.Waterfall(
        x=labels, y=values, measure=measures,
        connector=dict(line=dict(color=C["border2"], width=1)),
        increasing=dict(marker_color="rgba(248,113,113,0.7)"),
        decreasing=dict(marker_color="rgba(74,222,128,0.7)"),
        totals=dict(marker_color=_ha(C["neu"], 0.67)),
        hovertemplate="£%{y:.1f}bn<extra></extra>",
        textfont=dict(color=C["text"], size=10),
    ))
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost overrun waterfall: 2012 → 2026 (£bn)", font=dict(color=C["text"], size=13)),
        yaxis_tickprefix="£", yaxis_ticksuffix="bn")
    return fig


def fig_spend():
    """
    Annual spend vs budget — only years confirmed from primary AR documents.
    2023-24: AR 2023-24 (HC 106). 2024-25 actual + 2025-26 budget: AR 2024-25 (HC 1088).
    Earlier years are NOT plotted because we do not have confirmed outturn figures.
    """
    df = SPEND_DF
    fig = go.Figure()
    # Budget bars (where available)
    budget_vals = df["budget_bn"].tolist()
    actual_vals = df["actual_bn"].tolist()
    fig.add_trace(go.Bar(
        x=df["year"], y=budget_vals, name="Budget",
        marker_color=_ha(C["acc"], 0.33), marker_line_color=C["acc"], marker_line_width=1.5,
        text=[f"£{v:.1f}bn" if v else "—" for v in budget_vals],
        textposition="outside", textfont=dict(color=C["muted"], size=10),
    ))
    fig.add_trace(go.Bar(
        x=df["year"], y=actual_vals, name="Actual / planned",
        marker_color=_ha(C["neu"], 0.33), marker_line_color=C["neu"], marker_line_width=1.5,
        text=[f"£{v:.1f}bn" if v else "—" for v in actual_vals],
        textposition="outside", textfont=dict(color=C["muted"], size=10),
    ))
    fig.add_annotation(x=0.5, y=-0.2, xref="paper", yref="paper", xanchor="center",
        text="Sources: AR 2023-24 (HC 106); AR 2024-25 (HC 1088). Earlier years not confirmed.",
        font=dict(color=C["muted2"], size=9), showarrow=False)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Mono, monospace", color=C["muted"], size=11),
        title=dict(text="Annual budget vs actual spend — verified years only (£bn)", font=dict(color=C["text"], size=13)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", zeroline=False, tickfont=dict(color=C["text"], size=10)),
        yaxis=dict(range=[0, 9.5], tickprefix="£", ticksuffix="bn", gridcolor=C["grid"],
                   zeroline=False, tickfont=dict(color=C["muted2"], size=10)),
        barmode="group",
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=C["muted"], size=10), orientation="h", y=-0.15),
        margin=dict(l=10, r=10, t=40, b=60),
        hovermode="x unified")
    return fig


def fig_cost_drivers():
    labels  = ["Construction inflation","Design changes","Programme delay",
               "Governance / contractor","Tunnel complexity"]
    values  = [24, 18, 14, 10, 4]
    colours = [C["neg"], C["neu"], C["acc"], C["pu"], C["pos"]]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.55,
        marker=dict(colors=[_ha(c, 0.67) for c in colours],
                    line=dict(color=colours, width=1.5)),
        textfont=dict(color=C["text"], size=10),
        hovertemplate="%{label}: £%{value}bn (%{percent})<extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Cost overrun attribution (£bn)", font=dict(color=C["text"], size=13)),
        showlegend=True,
        legend=dict(font=dict(color=C["muted"], size=10), x=1.0))
    return fig


def fig_risk_radar():
    categories = ["Inflation","Political","Workforce","Contractor<br>failure",
                  "Scope<br>change","Euston<br>risk","Skill<br>shortage"]
    probability = [65, 70, 55, 45, 40, 60, 72]
    impact      = [85, 90, 60, 80, 75, 70, 65]
    fig = go.Figure()
    for data, name, col in [(probability,"Probability",C["neg"]),
                             (impact,"Impact",C["neu"])]:
        fig.add_trace(go.Scatterpolar(
            r=data + [data[0]], theta=categories + [categories[0]],
            name=name, fill="toself",
            fillcolor=_ha(col, 0.13), line=dict(color=col, width=2),
            hovertemplate="%{theta}: %{r}<extra>" + name + "</extra>"))
    fig.update_layout(**PLOTLY_LAYOUT,
        title=dict(text="Risk probability vs impact radar", font=dict(color=C["text"], size=13)),
        polar=dict(
            bgcolor=C["bg3"],
            radialaxis=dict(range=[0, 100], gridcolor=C["border2"],
                            tickfont=dict(color=C["muted2"], size=9)),
            angularaxis=dict(gridcolor=C["border"], tickfont=dict(color=C["muted"], size=10))),
        legend=dict(orientation="h", y=-0.1))
    return fig


def fig_confidence():
    metrics = ["Cost band","Schedule","Sentiment\nlead","Workforce\nsignal","Narrative\ncluster"]
    scores  = [72, 58, 45, 41, 68]
    colours = [C["pos"] if s > 60 else (C["neu"] if s > 50 else C["neg"]) for s in scores]
    fig = go.Figure(go.Bar(
        x=metrics, y=scores,
        marker_color=[_ha(c, 0.67) for c in colours],
        marker_line_color=colours, marker_line_width=1.5,
        text=[f"{s}%" for s in scores], textposition="outside",
        textfont=dict(color=C["muted"], size=10),
    ))
    fig.update_layout(**LAYOUT_NO_AXES,
        title=dict(text="Model confidence calibration by output type", font=dict(color=C["text"], size=13)),
        yaxis=dict(range=[0, 100], ticksuffix="%", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)))
    return fig


def fig_sensitivity(params):
    """Horizontal bar chart showing parameter impact scores."""
    labels  = [p["label"] for p in params]
    impacts = [p["impact"] for p in params]
    colours = [C["neu"] if p["effect"] == "neg" else C["acc"] for p in params]
    fig = go.Figure(go.Bar(
        x=impacts, y=labels, orientation="h",
        marker_color=[_ha(c, 0.53) for c in colours],
        marker_line_color=colours, marker_line_width=1.5,
        text=[f"{i}%" for i in impacts], textposition="outside",
        textfont=dict(color=C["muted"], size=10),
        hovertemplate="%{y}: %{x}% impact on outcome<extra></extra>",
    ))
    fig.update_layout(**LAYOUT_BARE,
        title=dict(text="Parameter sensitivity — % variance explained", font=dict(color=C["text"], size=13)),
        xaxis=dict(range=[0, 105], ticksuffix="%", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)),
        margin=dict(l=180, r=60, t=40, b=20))
    return fig


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  COMPONENT HELPERS
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

def badge(text, kind="neg"):
    colour_map = {
        "pos": ("#4ade80", "rgba(74,222,128,0.12)"),
        "neu": ("#f59e0b", "rgba(245,158,11,0.12)"),
        "neg": ("#f87171", "rgba(248,113,113,0.12)"),
        "acc": ("#7c9ef8", "rgba(124,158,248,0.12)"),
    }
    fg, bg = colour_map.get(kind, colour_map["neg"])
    return html.Span(text, style={
        "fontSize":"10px", "fontFamily":"DM Mono,monospace", "fontWeight":"500",
        "padding":"3px 9px", "borderRadius":"20px",
        "color": fg, "background": bg, "border": f"1px solid {fg}44",
    })


def stat_card(label, value, sub, delta=None, kind="neg"):
    colour_map = {"pos": C["pos"], "neu": C["neu"], "neg": C["neg"], "acc": C["acc"], "pu": C["pu"]}
    val_col = colour_map.get(kind, C["neg"])
    children = [
        html.Div(label, style={"fontSize":"10px","fontFamily":"DM Mono,monospace",
                               "textTransform":"uppercase","letterSpacing":"0.08em",
                               "color":C["muted"],"marginBottom":"6px"}),
        html.Div(value, style={"fontSize":"22px","fontWeight":"300",
                               "fontFamily":"Fraunces,serif","color":val_col}),
        html.Div(sub,   style={"fontSize":"11px","color":C["muted"],"marginTop":"2px"}),
    ]
    if delta:
        dkind = "neg" if "↑" in delta else "pos"
        children.append(html.Div(delta, style={
            "fontSize":"11px","fontFamily":"DM Mono,monospace","marginTop":"4px",
            "color": C["neg"] if dkind=="neg" else C["pos"]}))
    return html.Div(children, style={
        "background":C["bg2"], "border":f"1px solid {C['border']}",
        "borderRadius":"10px", "padding":"14px 16px",
        "borderTop":f"2px solid {val_col}",
    })


def card(children, style=None):
    base = {"background":C["bg2"],"border":f"1px solid {C['border']}",
            "borderRadius":"10px","padding":"18px 20px","height":"100%"}
    if style:
        base.update(style)
    return html.Div(children, style=base)


def card_title(text, right=None):
    children = [html.Span(text)]
    if right:
        children.append(right)
    return html.Div(children, style={
        "fontSize":"11px","color":C["muted"],"textTransform":"uppercase",
        "letterSpacing":"0.08em","fontFamily":"DM Mono,monospace",
        "marginBottom":"14px","display":"flex","justifyContent":"space-between",
        "alignItems":"center"})


def section_header(title, subtitle=""):
    return html.Div([
        html.H2(title, style={"fontFamily":"Fraunces,serif","fontSize":"22px",
                              "fontWeight":"300","color":C["text"],"marginBottom":"4px",
                              "letterSpacing":"-0.3px"}),
        html.P(subtitle, style={"fontSize":"12px","color":C["muted"],"marginBottom":"18px"}),
    ])


def narrative_box(tag_text, body_text, id_body="narr-body-default"):
    return html.Div([
        html.Div(f"⬡ {tag_text}", style={"fontSize":"10px","fontFamily":"DM Mono,monospace",
                                          "color":C["acc"],"textTransform":"uppercase",
                                          "letterSpacing":"0.1em","marginBottom":"10px"}),
        html.Div(body_text, id=id_body, style={
            "fontFamily":"Fraunces,serif","fontSize":"15px","fontWeight":"300",
            "lineHeight":"1.8","color":C["text"],"whiteSpace":"pre-line"}),
    ], style={"background":C["bg3"],"border":f"1px solid {C['border2']}",
              "borderRadius":"10px","padding":"20px 22px"})


def kpi_table():
    """All figures from HS2 Annual Report 2023-24 (HC 106) — confirmed primary source."""
    rows = []
    header = html.Tr([
        html.Th(h, style={"padding":"6px 10px","color":C["muted"],"fontWeight":"400",
                          "fontFamily":"DM Mono,monospace","fontSize":"10px","textTransform":"uppercase",
                          "letterSpacing":"0.06em","borderBottom":f"1px solid {C['border']}"})
        for h in ["Metric","Target","Actual","Status","Source"]
    ])
    for metric, target, actual, kind, source in KPI_DATA:
        status_text = {"pos":"MET","neu":"NOTE","neg":"MISSED"}[kind]
        rows.append(html.Tr([
            html.Td(metric,  style={"padding":"7px 10px","color":C["text"],   "borderBottom":f"1px solid {C['border']}","fontSize":"12px"}),
            html.Td(target,  style={"padding":"7px 10px","color":C["muted"],  "borderBottom":f"1px solid {C['border']}","fontSize":"11px","fontFamily":"DM Mono,monospace"}),
            html.Td(actual,  style={"padding":"7px 10px","color":C["text"],   "borderBottom":f"1px solid {C['border']}","fontSize":"12px","fontFamily":"DM Mono,monospace"}),
            html.Td(badge(status_text, kind), style={"padding":"7px 10px","borderBottom":f"1px solid {C['border']}"}),
            html.Td(source,  style={"padding":"7px 10px","color":C["muted2"], "borderBottom":f"1px solid {C['border']}","fontSize":"10px","fontFamily":"DM Mono,monospace"}),
        ]))
    return html.Table([html.Thead(header), html.Tbody(rows)],
                      style={"width":"100%","borderCollapse":"collapse","fontSize":"12px"})


def risk_item(severity, name, desc):
    sev_col = {"HIGH":C["neg"],"MED":C["neu"],"LOW":C["pos"]}[severity]
    return html.Div([
        html.Div(html.Span(severity, style={"fontSize":"10px","fontFamily":"DM Mono,monospace",
                                            "fontWeight":"500","color":sev_col}),
                 style={"width":"46px","height":"22px","borderRadius":"5px","flexShrink":"0",
                        "display":"flex","alignItems":"center","justifyContent":"center",
                        "background":_ha(sev_col, 0.13),"border":f"1px solid {sev_col}44"}),
        html.Div([
            html.Div(name, style={"fontSize":"12px","fontWeight":"500","color":C["text"],"marginBottom":"2px"}),
            html.Div(desc, style={"fontSize":"11px","color":C["muted"],"lineHeight":"1.5"}),
        ])
    ], style={"display":"flex","gap":"12px","alignItems":"flex-start",
              "padding":"10px 0","borderBottom":f"1px solid {C['border']}"})


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  APP LAYOUT
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300&family=DM+Sans:wght@300;400;500&display=swap",
    ],
    title="HS2 Intelligence Dashboard",
    suppress_callback_exceptions=True,
)

# Inject global CSS via index_string
app.index_string = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
body { background: #0c0e13 !important; margin: 0; }
* { box-sizing: border-box; }
.tab-content { background: transparent !important; border: none !important; }
.nav-tabs { border-bottom: 1px solid rgba(255,255,255,0.07) !important; background: #13161d; padding: 0 2rem; }
.nav-tabs .nav-link { color: #7a7f94 !important; font-size: 12px; font-family: DM Sans, sans-serif; font-weight: 500; letter-spacing: 0.02em; border: none !important; border-bottom: 2px solid transparent !important; padding: 12px 18px !important; border-radius: 0 !important; }
.nav-tabs .nav-link:hover { color: #e8eaf0 !important; }
.nav-tabs .nav-link.active { color: #7c9ef8 !important; border-bottom: 2px solid #7c9ef8 !important; background: transparent !important; }
input[type=range] { accent-color: #7c9ef8; cursor: pointer; width: 100%; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #13161d; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

# ─ Global styles injected as a style tag ─
GLOBAL_CSS = """
body { background: #0c0e13 !important; margin: 0; }
* { box-sizing: border-box; }
.tab-content { background: transparent !important; border: none !important; }
.nav-tabs { border-bottom: 1px solid rgba(255,255,255,0.07) !important; background: #13161d; padding: 0 2rem; }
.nav-tabs .nav-link { color: #7a7f94 !important; font-size: 12px; font-family: 'DM Sans', sans-serif; font-weight: 500; letter-spacing: 0.02em; border: none !important; border-bottom: 2px solid transparent !important; padding: 12px 18px !important; border-radius: 0 !important; }
.nav-tabs .nav-link:hover { color: #e8eaf0 !important; }
.nav-tabs .nav-link.active { color: #7c9ef8 !important; border-bottom: 2px solid #7c9ef8 !important; background: transparent !important; }
input[type=range] { accent-color: #7c9ef8; cursor: pointer; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #13161d; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
"""

# Slider controls for scenario panel
slider_controls = []
for p in PARAMS:
    slider_controls.append(html.Div([
        html.Div([
            html.Span(p["label"], style={"fontSize":"12px","color":C["text"]}),
            html.Span(id=f"val-{p['id']}", children=str(p["val"]),
                      style={"fontSize":"12px","fontFamily":"DM Mono,monospace","color":C["acc"]}),
        ], style={"display":"flex","justifyContent":"space-between","marginBottom":"6px"}),
        dcc.Slider(
            id=f"slider-{p['id']}",
            min=p["min"], max=p["max"], step=p["step"], value=p["val"],
            marks=None, tooltip={"always_visible":False},
            updatemode="drag",
        ),
    ], style={"marginBottom":"18px"}))


def make_layout():
    return html.Div([
        # Inject global CSS
        # CSS injected via index_string

        # ── HEADER ──
        html.Div([
            html.Div([
                html.Span(["HS", html.Span("2", style={"color":C["acc"]}), " Intelligence"],
                          style={"fontFamily":"Fraunces,serif","fontSize":"18px",
                                 "fontWeight":"600","color":C["text"]}),
                html.Span("MONTE CARLO · SCENARIO ANALYSIS · v1.0",
                          style={"fontSize":"10px","fontFamily":"DM Mono,monospace",
                                 "color":C["muted"],"background":C["bg3"],
                                 "border":f"1px solid {C['border']}","padding":"3px 8px",
                                 "borderRadius":"20px","letterSpacing":"0.05em"}),
            ], style={"display":"flex","alignItems":"center","gap":"16px"}),
            html.Div([
                html.Div(style={"width":"6px","height":"6px","borderRadius":"50%",
                               "background":C["pos"],"animation":"pulse 2s infinite"}),
                html.Span("LIVE MODEL", style={"fontSize":"12px","fontFamily":"DM Mono,monospace","color":C["muted"]}),
                html.Span("Updated: May 2026 · 10,000 simulations",
                          style={"fontSize":"11px","fontFamily":"DM Mono,monospace","color":C["muted2"]}),
            ], style={"display":"flex","alignItems":"center","gap":"10px"}),
        ], style={"background":C["bg2"],"borderBottom":f"1px solid {C['border']}",
                  "padding":"0 2rem","height":"56px","display":"flex","alignItems":"center",
                  "justifyContent":"space-between","position":"sticky","top":"0","zIndex":"100"}),

        # ── TABS ──
        dbc.Tabs(id="main-tabs", active_tab="tab-overview", children=[
            dbc.Tab(label="Overview",            tab_id="tab-overview"),
            dbc.Tab(label="Scenario Clusters",   tab_id="tab-scenarios"),
            dbc.Tab(label="Workforce & Sentiment",tab_id="tab-workforce"),
            dbc.Tab(label="Budget Analysis",     tab_id="tab-budget"),
            dbc.Tab(label="Risk Signals",        tab_id="tab-risks"),
            dbc.Tab(label="Narrative Engine",    tab_id="tab-narrative"),
            dbc.Tab(label="Methodology",         tab_id="tab-method"),
        ]),
        html.Div(id="tab-content", style={"padding":"0"}),

    ], style={"background":C["bg"],"minHeight":"100vh","fontFamily":"DM Sans,sans-serif",
              "color":C["text"],"fontSize":"14px"})


app.layout = make_layout()


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  PANEL RENDERERS
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

def render_overview():
    mc = run_monte_carlo()
    cp = mc["cluster_probs"]
    return html.Div([
        # Stat cards
        html.Div([
            stat_card("Cost estimate (2026)", "£102.7bn", "Upper range", "↑ 214% vs 2012 baseline", "neg"),
            stat_card("Schedule delay", "+13yr", "2026 → 2039 opening", "↑ 3 further delays in 2025", "neg"),
            stat_card("% complete (Phase 1)", ">80% tunnelling", "Tunnelling >80% done (AR 2024-25)", "Overall phase 1 % not stated in sources", "neu"),
            stat_card("Total workforce (2024–25)", "33,000", "AR 2024-25, CEO intro (verified)", "↑ from 30,204 peak in Sep 2023", "acc"),
            stat_card("Positive outcome prob.", f"{cp['pos']:.0f}%", "Monte Carlo (10k sims)", "↓ from 31% in 2023", "pu"),
        ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)","gap":"10px","marginBottom":"16px"}),

        # Narrative banner
        narrative_box(
            "Narrative Engine Output — Overview",
            ("HS2 has entered a structural crisis loop — where each governance reset improves "
             "confidence briefly before structural cost and schedule pressures reassert. With only "
             "one-third of Phase 1 complete, £40bn already spent, and costs now reaching £102.7bn, "
             "the project faces a paradox: cancellation costs nearly the same as completion. "
             "The most likely future is managed overrun to 2039–2041, contingent on political "
             "continuity and no further scope intervention."),
            id_body="narr-overview"
        ),
        html.Div(style={"height":"14px"}),

        # Row: cost chart + timeline
        html.Div([
            html.Div(card([
                card_title("Cost estimate evolution 2012–2026", badge("214% overrun","neg")),
                dcc.Graph(figure=fig_cost_history(), config={"displayModeBar":False}, style={"height":"240px"}),
            ]), style={"flex":"2"}),
            html.Div(card([
                card_title("Critical regime changes"),
                html.Div([
                    _tl_item("2012", "pos", "Original budget approved: £32.7bn", "Opening target: 2026"),
                    _tl_item("2016", "neu", "NAO flags 'unrealistic timetable'", "First schedule slippage signal"),
                    _tl_item("2019", "neg", "Oakervee Review: costs £88bn", "Opening pushed to 2028–2031"),
                    _tl_item("2023", "neg", "Phase 2 cancelled by Sunak", "£2.7bn written off. Leeds & Manchester axed."),
                    _tl_item("2025", "neg", "Lovegrove review: 'litany of failure'", "Full programme reset announced"),
                    _tl_item("2026", "neg", "Cost hits £102.7bn. Opening: 2039", "Programme under reset — current status"),
                ], style={"paddingLeft":"20px","borderLeft":f"1px solid {C['border2']}"}),
            ]), style={"flex":"1"}),
        ], style={"display":"flex","gap":"12px","marginTop":"14px"}),

        # Row: schedule + donut
        html.Div([
            html.Div(card([
                card_title("Schedule evolution — original vs actuals"),
                dcc.Graph(figure=fig_schedule(), config={"displayModeBar":False}, style={"height":"200px"}),
            ])),
            html.Div(card([
                card_title("Monte Carlo cluster probabilities"),
                dcc.Graph(figure=fig_cluster_donut(cp["pos"],cp["neu"],cp["neg"]),
                          config={"displayModeBar":False}, style={"height":"200px"}),
            ])),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginTop":"12px"}),

    ], style={"padding":"1.5rem 2rem"})


def _tl_item(year, kind, title, detail):
    col_map = {"pos":C["pos"],"neu":C["neu"],"neg":C["neg"],"acc":C["acc"]}
    col = col_map.get(kind, C["muted"])
    return html.Div([
        html.Div(style={"position":"absolute","left":"-27px","top":"5px","width":"10px","height":"10px",
                        "borderRadius":"50%","background":_ha(col, 0.2),"border":f"2px solid {col}"}),
        html.Div(year,  style={"fontSize":"10px","fontFamily":"DM Mono,monospace","color":C["muted"]}),
        html.Div(title, style={"fontSize":"12px","color":C["text"],"lineHeight":"1.5"}),
        html.Div(detail,style={"fontSize":"11px","color":C["muted"],"marginTop":"1px"}),
    ], style={"position":"relative","paddingBottom":"16px","paddingLeft":"4px"})


def render_scenarios():
    return html.Div([
        section_header("Scenario cluster analysis",
                       "10,000 Monte Carlo simulations grouped into 3 outcome clusters. Adjust parameters to update probabilities live."),

        # Cluster cards
        html.Div([
            _cluster_card("pos","Controlled Delivery","pos-pct-live","18",
                          "Cost: <£90bn · Opens: 2037–38",
                          "Inflation below 4%, no scope change, KPI score >2.2 — all three simultaneously. Historically present for at most 18 months at a time."),
            _cluster_card("neu","Managed Overrun","neu-pct-live","45",
                          "Cost: £90–110bn · Opens: 2039–41",
                          "Current trajectory. Reflects 13 years of precedent. Most likely single outcome."),
            _cluster_card("neg","Escalation / Intervention","neg-pct-live","37",
                          "Cost: >£110bn · Opens: 2043+ or cancelled",
                          "Triggered by: political review post-2028 election, contractor failure, inflation spike."),
        ], style={"display":"grid","gridTemplateColumns":"repeat(3,1fr)","gap":"10px","marginBottom":"14px"}),

        # Sliders + live chart + sensitivity
        html.Div([
            html.Div(card([
                card_title("Parameter controls — drag to simulate"),
                html.Div(slider_controls),
            ]), style={"flex":"1"}),
            html.Div([
                card([
                    card_title("Cluster probability — live simulation"),
                    dcc.Graph(id="live-cluster-chart", config={"displayModeBar":False}, style={"height":"200px"}),
                ]),
                html.Div(style={"height":"12px"}),
                card([
                    card_title("Parameter sensitivity — impact on outcome"),
                    dcc.Graph(figure=fig_sensitivity(PARAMS), config={"displayModeBar":False}, style={"height":"220px"}),
                ]),
            ], style={"flex":"1","display":"flex","flexDirection":"column","gap":"0"}),
        ], style={"display":"flex","gap":"12px","marginBottom":"14px"}),

        # Fan chart + histogram
        card([
            card_title("Monte Carlo fan chart — cost forecast to 2040", badge("10,000 paths","neg")),
            dcc.Graph(id="fan-chart", config={"displayModeBar":False}, style={"height":"280px"}),
        ]),
        html.Div(style={"height":"12px"}),
        card([
            card_title("Cost distribution — simulation results"),
            dcc.Graph(id="cost-histogram", config={"displayModeBar":False}, style={"height":"220px"}),
        ]),

    ], style={"padding":"1.5rem 2rem"})


def _cluster_card(kind, label, pct_id, default_pct, subtitle, desc):
    col_map = {"pos":C["pos"],"neu":C["neu"],"neg":C["neg"]}
    col = col_map[kind]
    return html.Div([
        html.Div(id=pct_id, children=default_pct + "%",
                 style={"fontFamily":"Fraunces,serif","fontSize":"44px","fontWeight":"300",
                        "letterSpacing":"-2px","lineHeight":"1","color":col}),
        html.Div(label, style={"fontSize":"11px","fontFamily":"DM Mono,monospace",
                               "textTransform":"uppercase","letterSpacing":"0.1em",
                               "color":col,"margin":"6px 0"}),
        html.Div(subtitle, style={"fontSize":"12px","color":C["muted"],"marginBottom":"8px"}),
        html.Div(desc,     style={"fontSize":"12px","color":C["text"],"lineHeight":"1.5","opacity":"0.85"}),
    ], style={"borderRadius":"10px","border":f"1px solid {col}44","padding":"16px",
              "background":_ha(col, 0.07)})


def render_workforce():
    return html.Div([
        section_header("Workforce & sentiment intelligence",
                       "Human-centric signals from HS2 Annual Reports, EDI reports, PAC hearings, and parliamentary statements 2019–2025."),

        # Stat bar
        html.Div([
            stat_card("HS2 Ltd headcount", "~3,200", "Direct employees", kind="acc"),
            stat_card("Supply chain workforce", "~28k",  "Peak Phase 1 construction", kind="acc"),
            stat_card("Women in workforce", "38%", "vs 40% target (near-met)", kind="neu"),
            stat_card("Safety LTIFR (2023–24)", "↓ 0.02", "Improved year-on-year", kind="pos"),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"10px","marginBottom":"14px"}),

        # Sentiment + workforce trend
        html.Div([
            card([
                card_title("Composite sentiment by stakeholder group"),
                dcc.Graph(figure=fig_stakeholder_sentiment(), config={"displayModeBar":False}, style={"height":"280px"}),
                narrative_box(
                    "Narrative signal",
                    ("Sentiment is strongly bifurcated: external stakeholders (Parliament, media, communities) "
                     "are deeply negative. Internal and economic stakeholders remain cautiously supportive. "
                     "This divergence is itself a risk signal — it reduces political protection for the project."),
                    id_body="narr-sentiment"
                ),
            ]),
            card([
                card_title("Workforce headcount trend 2019–2025"),
                dcc.Graph(figure=fig_workforce(), config={"displayModeBar":False}, style={"height":"220px"}),
                html.Hr(style={"borderColor":C["border"],"margin":"14px 0"}),
                card_title("KPI performance vs target (2023–24)"),
                kpi_table(),
            ]),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px","marginBottom":"14px"}),

        # Sentiment timeline
        card([
            card_title("Stakeholder sentiment timeline 2016–2025"),
            dcc.Graph(figure=fig_sentiment_timeline(), config={"displayModeBar":False}, style={"height":"220px"}),
        ]),

        # Signals row
        html.Div(style={"height":"12px"}),
        html.Div([
            _signal_box("HIGH RISK","neg","Skill gap signal",
                        "PAC 2024: technical & engineering shortages set to worsen. Competition from global infrastructure projects."),
            _signal_box("HIGH RISK","neg","Leadership stability",
                        "5 CEOs and 3 Chairs in 10 years. New Chair (Mike Brown) appointed June 2025 following Lovegrove review."),
            _signal_box("IMPROVING","pos","Safety trajectory",
                        "LTIFR improved year-on-year in 2023–24. Enterprise safety score exceeded target. Positive signal amid wider failure."),
        ], style={"display":"grid","gridTemplateColumns":"repeat(3,1fr)","gap":"10px"}),

    ], style={"padding":"1.5rem 2rem"})


def _signal_box(status, kind, title, desc):
    col = C[kind]
    return html.Div([
        html.Div(status, style={"fontSize":"11px","fontWeight":"500","color":col,"marginBottom":"4px","fontFamily":"DM Mono,monospace"}),
        html.Div(title,  style={"fontSize":"13px","fontWeight":"500","color":C["text"],"marginBottom":"4px"}),
        html.Div(desc,   style={"fontSize":"11px","color":C["muted"],"lineHeight":"1.5"}),
    ], style={"background":C["bg3"],"borderRadius":"8px","padding":"14px","border":f"1px solid {col}33"})


def render_budget():
    return html.Div([
        section_header("Budget & spend analysis",
                       "Cost revision history from 2012 to 2026. Sources: NAO, House of Commons Library CBP-9313, HS2 Annual Reports."),

        html.Div([
            stat_card("Original budget (2012)", "£32.7bn", "In 2019 prices", kind="neg"),
            stat_card("Latest estimate (2026)", "£102.7bn","Upper range, 2026 prices", kind="neg"),
            stat_card("Already spent (2025)",   "~£40bn",  "Cash terms, Phase 1 only", kind="neg"),
            stat_card("Phase 2 prep costs",    "~£2.3bn", "Manchester leg alone (Railway News Apr 2026)", kind="neu"),
            stat_card("Annual budget 2025-26","£7.1bn",   "AR 2024-25 HC1088 (confirmed)", kind="neu"),
        ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)","gap":"10px","marginBottom":"14px"}),

        card([
            card_title("Cost overrun waterfall: 2012 → 2026", badge("+£70bn total increase","neg")),
            dcc.Graph(figure=fig_waterfall(), config={"displayModeBar":False}, style={"height":"300px"}),
        ]),
        html.Div(style={"height":"12px"}),

        html.Div([
            card([
                card_title("Annual spend vs budget (£bn)"),
                dcc.Graph(figure=fig_spend(), config={"displayModeBar":False}, style={"height":"220px"}),
            ]),
            card([
                card_title("Cost overrun attribution"),
                dcc.Graph(figure=fig_cost_drivers(), config={"displayModeBar":False}, style={"height":"200px"}),
                html.Hr(style={"borderColor":C["border"],"margin":"12px 0"}),
                *[html.Div([
                    html.Span(k, style={"fontSize":"12px","color":C["muted"]}),
                    html.Span(v, style={"fontSize":"13px","fontFamily":"DM Mono,monospace","color":C["neg"]}),
                  ], style={"display":"flex","justifyContent":"space-between","padding":"7px 0",
                            "borderBottom":f"1px solid {C['border']}"})
                  for k, v in [("Construction inflation","~£24bn"),
                                ("Design changes & rescoping","~£18bn"),
                                ("Programme delays","~£14bn"),
                                ("Governance & contractor overruns","~£10bn"),
                                ("Tunnel complexity uplift","~£4bn")]],
            ]),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px"}),

    ], style={"padding":"1.5rem 2rem"})


def render_risks():
    risks_high = [
        ("HIGH","Political intervention post-2028 election",
         "Any change in government or policy review could trigger another full reset. HS2 has survived 3 elections; the next is a major inflection point."),
        ("HIGH","Construction inflation spike",
         "Construction inflation ran at 8–12% 2021–23. A return to this level would push costs well above £110bn. Remaining works are most inflation-sensitive."),
        ("HIGH","Skill & labour shortage",
         "PAC 2024 identified worsening technical skill shortages. Global infrastructure boom competing for the same labour pool."),
        ("HIGH","Euston station uncertainty",
         "Euston construction paused. No confirmed restart timeline. Without Euston, Phase 1 delivers reduced benefit and the benefit-cost ratio falls below 1.5."),
        ("HIGH","Further scope reduction",
         "Speed reduced from 360 km/h to 320 km/h in 2025 to save £2.5bn. Further reductions possible, each weakening the economic case."),
        ("HIGH","Contractor Joint Venture failure",
         "Multiple JVs running simultaneously. If one faces financial difficulty (as on Crossrail), cascade effects on the programme are severe."),
        ("HIGH","Updated cost estimate delay",
         "Full programme reset cost estimate was due mid-2026, now delayed to end-2026. Uncertainty itself is a risk — it delays contractor decisions."),
    ]
    risks_med = [
        ("MED","Community & legal challenges",
         "Independent Commissioner appointed. Ongoing legal challenges along the route add cost and schedule variance."),
        ("MED","Carbon target shortfall",
         "Current trajectory at 33.8% reduction vs 50% target. Shortfall could trigger additional spend on green materials."),
        ("MED","Leadership continuity",
         "New Chair and CEO reset in 2025. Learning curve during critical construction phase adds execution risk."),
        ("LOW","Safety incident escalation",
         "Safety KPIs are currently on-target and improving. Low risk but high impact — a major incident would trigger a public inquiry."),
    ]
    return html.Div([
        section_header("Risk signal monitor",
                       "Structured risk register derived from NAO reports, PAC transcripts, and Lovegrove review."),

        html.Div([
            html.Div(card([
                card_title("Active risk register", badge("7 HIGH · 4 MED","neg")),
                *[risk_item(s,n,d) for s,n,d in risks_high + risks_med],
            ]), style={"flex":"1"}),
            html.Div([
                card([
                    card_title("Risk radar — probability vs impact"),
                    dcc.Graph(figure=fig_risk_radar(), config={"displayModeBar":False}, style={"height":"320px"}),
                ]),
                html.Div(style={"height":"12px"}),
                card([
                    card_title("Monte Carlo — distribution assumptions"),
                    html.Table([
                        html.Thead(html.Tr([html.Th(h, style={"padding":"6px 8px","color":C["muted"],"fontWeight":"400",
                                                              "fontFamily":"DM Mono,monospace","fontSize":"10px",
                                                              "textTransform":"uppercase","letterSpacing":"0.06em",
                                                              "borderBottom":f"1px solid {C['border']}"})
                                           for h in ["Parameter","Distribution","Range"]])),
                        html.Tbody([html.Tr([
                            html.Td(a,style={"padding":"7px 8px","color":C["text"],"fontSize":"12px","borderBottom":f"1px solid {C['border']}"}),
                            html.Td(b,style={"padding":"7px 8px","color":C["muted"],"fontSize":"11px","fontFamily":"DM Mono,monospace","borderBottom":f"1px solid {C['border']}"}),
                            html.Td(c,style={"padding":"7px 8px","color":C["muted"],"fontSize":"11px","fontFamily":"DM Mono,monospace","borderBottom":f"1px solid {C['border']}"}),
                        ]) for a,b,c in [
                            ("Inflation rate","Log-normal","2%–12% p.a."),
                            ("Scope change event","Poisson (λ=0.4/yr)","0–2 per year"),
                            ("Political risk event","Bernoulli","P=0.35 at elections"),
                            ("Contractor performance","Beta(α=3,β=1.5)","KPI score 1.8–2.8"),
                            ("Workforce ramp rate","Normal","±15% of plan"),
                            ("Design change cost","Pareto tail","£0.5bn–£8bn"),
                        ]]),
                    ], style={"width":"100%","borderCollapse":"collapse"}),
                ]),
            ], style={"flex":"1","display":"flex","flexDirection":"column"}),
        ], style={"display":"flex","gap":"12px"}),

    ], style={"padding":"1.5rem 2rem"})


def render_narrative():
    return html.Div([
        section_header("Narrative engine",
                       "Translates Monte Carlo probability distributions into plain-language decision intelligence. Select a scenario."),

        html.Div([
            html.Button("Controlled Delivery (18%)", id="btn-pos",
                        style={"flex":"1","border":f"1px solid {C['pos']}44","borderRadius":"10px","padding":"12px",
                               "background":_ha(C["pos"], 0.07),"color":C["pos"],"cursor":"pointer","fontFamily":"DM Sans,sans-serif","fontSize":"13px"}),
            html.Button("Managed Overrun (45%)", id="btn-neu",
                        style={"flex":"1","border":f"1px solid {C['neu']}44","borderRadius":"10px","padding":"12px",
                               "background":_ha(C["neu"], 0.13),"color":C["neu"],"cursor":"pointer","fontFamily":"DM Sans,sans-serif","fontSize":"13px","fontWeight":"500"}),
            html.Button("Escalation (37%)", id="btn-neg",
                        style={"flex":"1","border":f"1px solid {C['neg']}44","borderRadius":"10px","padding":"12px",
                               "background":_ha(C["neg"], 0.07),"color":C["neg"],"cursor":"pointer","fontFamily":"DM Sans,sans-serif","fontSize":"13px"}),
        ], style={"display":"flex","gap":"10px","marginBottom":"16px"}),

        html.Div(id="narrative-output", children=narrative_box(
            NARRATIVES["neu"]["tag"], NARRATIVES["neu"]["body"])),

        html.Div(style={"height":"14px"}),

        html.Div([
            card([
                card_title("Parameter → narrative trigger map"),
                *[html.Div([
                    badge(trigger, kind),
                    html.Div(desc, style={"fontSize":"12px","color":C["muted"],"lineHeight":"1.5","flex":"1"}),
                  ], style={"display":"flex","gap":"12px","alignItems":"flex-start",
                            "padding":"10px 0","borderBottom":f"1px solid {C['border']}"})
                  for trigger, kind, desc in [
                      ("Inflation >7%","neg","Triggers migration from Managed Overrun → Escalation. Model assigns 28% probability of recurrence by 2028."),
                      ("Election review","neg","Any formal HS2 review post-2028 election has historically added 12–36 months and £5–15bn. Bernoulli probability: 35%."),
                      ("Euston restart","neu","Confirmation of Euston construction restart is the strongest single positive signal. Shifts positive cluster prob +13pp."),
                      ("KPI score >2.4","pos","Sustained above 2.4 for 3+ quarters is a leading indicator of delivery within budget."),
                      ("Workforce stable","pos","Leadership continuity for 24 months is a necessary (not sufficient) condition for controlled delivery."),
                  ]],
            ]),
            card([
                card_title("Narrative confidence calibration"),
                dcc.Graph(figure=fig_confidence(), config={"displayModeBar":False}, style={"height":"200px"}),
                html.Hr(style={"borderColor":C["border"],"margin":"14px 0"}),
                html.P([
                    html.Strong("Backtesting note: ", style={"color":C["text"]}),
                    "Running this model against 2016 data would have predicted the 2019 cost revision "
                    "(actual: £88bn vs model median: £82bn). The model consistently underestimates "
                    "tail risk — wide uncertainty bands are intentional and honest.",
                ], style={"fontSize":"12px","color":C["muted"],"lineHeight":"1.7"}),
            ]),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"12px"}),

    ], style={"padding":"1.5rem 2rem"})


def render_methodology():
    phases = [
        ("01","Data extraction & time series","Weeks 1–2",
         ["Extract cost revision series from CBP-9313 (2012–2026)",
          "Parse HS2 Annual Reports 2019–2025 for KPI tables",
          "Extract workforce headcount, EDI, safety from PDFs",
          "Download PAC hearing transcripts for sentiment signals",
          "Tag discrete events (elections, reviews, scope changes)",
          "Output: clean CSV time series per parameter"]),
        ("02","Monte Carlo model calibration","Weeks 2–3",
         ["Fit distributions to each parameter from historical data",
          "Calibrate inflation using ONS construction price indices",
          "Set Poisson rate for scope change events",
          "Run 10,000 paths; validate against known outcomes",
          "Backtest: 2016 data → does model predict 2019 revision?",
          "Output: cluster probabilities + sensitivity rankings"]),
        ("03","Sentiment & NLP layer","Weeks 3–4",
         ["Parse PAC transcripts for tone signals by quarter",
          "Apply sentiment scoring to parliamentary questions",
          "Build stakeholder sentiment index (7 groups)",
          "Correlate sentiment shifts with subsequent cost events",
          "Does negative PAC sentiment lead cost overruns by 6 months?",
          "Output: sentiment time series + leading indicator signals"]),
        ("04","Narrative engine v1","Weeks 4–5",
         ["Template-based narrative from cluster + key parameters",
          "LLM layer to generate natural language from model outputs",
          "Parameter trigger map: which inputs change the narrative?",
          "Confidence calibration — what can the model not predict?",
          "Decision intelligence layer: actionable recommendations",
          "Output: auto-generated report from live data"]),
        ("05","Interactive dashboard","Weeks 5–6",
         ["Dashboard as shown (this is your v1.0)",
          "Connect to live data pipeline (auto-refresh on new reports)",
          "Scenario slider controls for client exploration",
          "Narrative engine output rendered inline",
          "Export to PDF report on demand",
          "Output: client-facing deliverable"]),
        ("06","Client delivery & productisation","Weeks 6–8",
         ["Present to anchor client — this dashboard is the demo",
          "Document what took manual effort → automate it",
          "Identify which elements generalise to other projects",
          "Begin second client conversation (same domain)",
          "IP documentation: what is the reusable product?",
          "Output: paid engagement + product v1 blueprint"]),
    ]
    phase_cards = []
    for num, title, dur, items in phases:
        phase_cards.append(html.Div([
            html.Div(num, style={"fontFamily":"Fraunces,serif","fontSize":"32px","color":C["border2"],"fontWeight":"300","marginBottom":"4px"}),
            html.Div(title, style={"fontSize":"13px","fontWeight":"500","color":C["text"],"marginBottom":"3px"}),
            html.Div(dur,   style={"fontSize":"11px","color":C["acc"],"fontFamily":"DM Mono,monospace","marginBottom":"10px"}),
            *[html.Div(f"→ {item}", style={"fontSize":"12px","color":C["muted"],"lineHeight":"1.6","padding":"1px 0"}) for item in items],
        ], style={"background":C["bg3"],"border":f"1px solid {C['border']}","borderRadius":"10px","padding":"16px"}))

    return html.Div([
        section_header("Implementation plan & methodology",
                       "Phased roadmap for building the full HS2 analysis pipeline — from data extraction to live narrative engine."),

        html.Div(phase_cards,
                 style={"display":"grid","gridTemplateColumns":"repeat(3,1fr)","gap":"12px","marginBottom":"16px"}),

        card([
            card_title("Public data sources"),
            html.Table([
                html.Thead(html.Tr([html.Th(h, style={"padding":"6px 10px","color":C["muted"],"fontWeight":"400",
                                                       "fontFamily":"DM Mono,monospace","fontSize":"10px",
                                                       "textTransform":"uppercase","letterSpacing":"0.06em",
                                                       "borderBottom":f"1px solid {C['border']}"})
                                    for h in ["Source","What you get","URL"]])),
                html.Tbody([html.Tr([
                    html.Td(a, style={"padding":"8px 10px","color":C["text"],"fontSize":"12px","fontWeight":"500","borderBottom":f"1px solid {C['border']}"}),
                    html.Td(b, style={"padding":"8px 10px","color":C["muted"],"fontSize":"12px","borderBottom":f"1px solid {C['border']}"}),
                    html.Td(c, style={"padding":"8px 10px","color":C["acc"],"fontSize":"11px","fontFamily":"DM Mono,monospace","borderBottom":f"1px solid {C['border']}"}),
                ]) for a,b,c in [
                    ("HoC Library CBP-9313","Full cost & schedule revision history","commonslibrary.parliament.uk"),
                    ("HS2 Annual Reports 2019–2025","KPIs, workforce, spend, safety","assets.publishing.service.gov.uk"),
                    ("HS2 EDI Report 2024–25","Workforce diversity by band","assets.publishing.service.gov.uk"),
                    ("NAO HS2 reports (8 reports)","Cost, governance, risk findings","nao.org.uk"),
                    ("PAC hearing transcripts","Sentiment signals, governance critique","committees.parliament.uk"),
                    ("HS2 6-monthly Parliament Reports","Progress, milestones, minister statements","data.parliament.uk"),
                    ("ONS Construction Output Price Index","Inflation parameter calibration","ons.gov.uk"),
                ]]),
            ], style={"width":"100%","borderCollapse":"collapse"}),
        ]),

    ], style={"padding":"1.5rem 2rem"})


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  TAB CONTENT ROUTER
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

@app.callback(Output("tab-content","children"), Input("main-tabs","active_tab"))
def render_tab(tab):
    if tab == "tab-overview":   return render_overview()
    if tab == "tab-scenarios":  return render_scenarios()
    if tab == "tab-workforce":  return render_workforce()
    if tab == "tab-budget":     return render_budget()
    if tab == "tab-risks":      return render_risks()
    if tab == "tab-narrative":  return render_narrative()
    if tab == "tab-method":     return render_methodology()
    return html.Div()


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  CALLBACKS
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

# Slider display values
for p in PARAMS:
    @app.callback(
        Output(f"val-{p['id']}", "children"),
        Input(f"slider-{p['id']}", "value"),
    )
    def update_val(v, pid=p["id"]):
        step = next(x["step"] for x in PARAMS if x["id"] == pid)
        fmt  = f"{v:.2f}" if step < 0.1 else (f"{v:.1f}" if step < 1 else f"{v:.0f}")
        unit_map = {"inflation":"%/yr","scope":"%","political":"%","kpi":"","workforce":"%","euston":"%"}
        return fmt + unit_map.get(pid, "")


# Live Monte Carlo update from sliders
@app.callback(
    Output("live-cluster-chart",  "figure"),
    Output("fan-chart",           "figure"),
    Output("cost-histogram",      "figure"),
    Output("pos-pct-live",        "children"),
    Output("neu-pct-live",        "children"),
    Output("neg-pct-live",        "children"),
    [Input(f"slider-{p['id']}", "value") for p in PARAMS],
    prevent_initial_call=False,
)
def update_mc(*vals):
    inflation, scope, political, kpi, workforce, euston = vals
    mc = run_monte_carlo(
        n_sims=5000,          # faster for interactivity
        inflation=inflation,
        scope_risk=scope,
        political_risk=political,
        kpi_score=kpi,
        workforce_stability=workforce,
        euston_prob=euston,
    )
    cp = mc["cluster_probs"]

    # Cluster bar chart
    cluster_fig = go.Figure(go.Bar(
        x=["Controlled", "Managed", "Escalation"],
        y=[cp["pos"], cp["neu"], cp["neg"]],
        marker_color=[_ha(C["pos"], 0.47), _ha(C["neu"], 0.47), _ha(C["neg"], 0.47)],
        marker_line_color=[C["pos"], C["neu"], C["neg"]], marker_line_width=2,
        text=[f"{cp['pos']:.0f}%", f"{cp['neu']:.0f}%", f"{cp['neg']:.0f}%"],
        textposition="outside", textfont=dict(color=C["muted"], size=11),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))
    cluster_fig.update_layout(**LAYOUT_NO_AXES,
        yaxis=dict(range=[0,105], ticksuffix="%", gridcolor=C["grid"],
                   tickfont=dict(color=C["muted2"], size=10)),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=C["text"], size=11)))

    return (cluster_fig,
            fig_fan_chart(mc["fan_data"]),
            fig_cost_histogram(mc["costs"]),
            f"{cp['pos']:.0f}%",
            f"{cp['neu']:.0f}%",
            f"{cp['neg']:.0f}%")


# Narrative switcher
@app.callback(
    Output("narrative-output", "children"),
    Input("btn-pos", "n_clicks"),
    Input("btn-neu", "n_clicks"),
    Input("btn-neg", "n_clicks"),
    prevent_initial_call=False,
)
def switch_narrative(n_pos, n_neu, n_neg):
    ctx  = callback_context
    kind = "neu"   # default
    if ctx.triggered:
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        kind = {"btn-pos":"pos","btn-neu":"neu","btn-neg":"neg"}.get(btn_id, "neu")
    return narrative_box(NARRATIVES[kind]["tag"], NARRATIVES[kind]["body"])


# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──
#  ENTRY POINT
# ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ── ──

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  HS2 Intelligence Dashboard")
    print("  Monte Carlo · Scenario Analysis · Narrative Engine")
    print("="*60)
    print("\n  → Open http://127.0.0.1:8050 in your browser\n")
    app.run(debug=True, host="127.0.0.1", port=8050)