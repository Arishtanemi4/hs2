import numpy as np
import pandas as pd
from config.theme import C

COST_DF = pd.DataFrame({
    "year":     [2012, 2013, 2015, 2019, 2020, 2024,   2026],
    "low":      [32.7,  46,  55.7, 72.1,  72,   49,   87.7],
    "high":     [32.7,  46,  55.7, 78.4,  98,  66.6, 102.7],
    "baseline": [32.7]*7,
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

SCHEDULE_DF = pd.DataFrame({
    "revision":   [
        "2012 original",
        "2020 Oakervee",
        "2022 revised",
        "Jun 2025 (Alexander)",
        "2026 current",
    ],
    "open_year":  [2026, 2029, 2031, 2033, None],
    "open_label": ["2026", "2029-31", "2031", "2033 (missed)", "TBD - reset 2026"],
    "open_low":   [2026, 2029, 2031, 2033, 2034],
    "open_high":  [2026, 2031, 2033, 2033, 2041],
    "colour":     ["pos",  "neu",  "neu",  "neg",   "neg"],
})

SPEND_DF = pd.DataFrame({
    "year":         ["2023–24",          "2024–25",           "2025–26 (budget)"],
    "budget_bn":    [7.917,              None,                 7.1],
    "actual_bn":    [7.868,              7.5,                  None],
    "source":       ["AR 2023-24 HC106", "AR 2024-25 HC1088",  "AR 2024-25 HC1088"],
    "verified":     [True,               True,                 True],
})

WORKFORCE_DF = pd.DataFrame({
    "period": [
        "Sep 2020 (construction start)",
        "Oct 2022",
        "Jul-Sep 2023",
        "2024-25 (AR 2024-25)",
    ],
    "total":  [22_000, 30_000, 30_204, 33_000],
    "source": [
        "PM Johnson statement (ConstructionEnquirer Sep 2020)",
        "HS2 media centre (Oct 2022)",
        "HS2 media centre (Nov 2023)",
        "AR 2024-25 HC1088 (CEO intro)",
    ],
    "verified": [True, True, True, True],
})

KPI_DATA = [
    ("Enterprise score",         "2.20",             "2.35",   "pos", "AR 2023-24 confirmed"),
    ("Safety LTIFR",
     "No formal target",         "0.14",             "pos",    "safety.hs2.org.uk; reduced 0.02 from prior year"),
    ("Carbon reduction",         "30%",              "32.5%",  "pos", "AR 2023-24 confirmed"),
    ("Women in workforce",       "Goal",             "38%",    "neu", "AR 2023-24: slightly below goal; above industry avg 21-23%"),
    ("Ethnic minority workforce","—",                "29%",    "neu", "AR 2023-24 confirmed"),
    ("Annual budget 2023-24",    "£7,917m",          "£7,868m","pos", "AR 2023-24: 0.6% below budget"),
    ("Opening schedule",         "2033",             "MISSED", "neg", "Jun 2025: Transport Sec said 2033 unachievable"),
]

WORKING_HOURS_DF = pd.DataFrame({
    "year":    ["2022–23", "2023–24", "2024–25"],
    "hours_m": [62,         65,        71],
    "source":  [
        "safety.hs2.org.uk",
        "safety.hs2.org.uk + AR 2023-24",
        "AR 2024-25 HC1088",
    ],
})

STAKEHOLDER_SENT = [
    ("Parliament / PAC",     -0.72, C["neg"]),
    ("National media",       -0.81, C["neg"]),
    ("Affected communities", -0.65, C["neg"]),
    ("HS2 Ltd workforce",     0.28, C["neu"]),
    ("Supply chain JVs",      0.15, C["neu"]),
    ("Transport experts",    -0.12, C["muted"]),
    ("Regional businesses",   0.44, C["pos"]),
]

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

SENTIMENT_DF = pd.DataFrame({
    "year":       ["2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"],
    "parliament": [-0.20,-0.30,-0.40,-0.60,-0.40,-0.50,-0.60,-0.80,-0.72,-0.65],
    "workforce":  [ 0.50, 0.40, 0.40, 0.30, 0.20, 0.30, 0.20, 0.10, 0.28, 0.35],
    "media":      [-0.30,-0.30,-0.40,-0.50,-0.30,-0.50,-0.60,-0.85,-0.81,-0.70],
})

PARAMS = [
    dict(id="inflation",  label="Inflation rate (%/yr)",    min=2,   max=14,  step=0.5,  val=5.0,  impact=87, effect="neg"),
    dict(id="scope",      label="Scope change risk (%)",    min=0,   max=100, step=1,    val=35,   impact=72, effect="neg"),
    dict(id="political",  label="Political risk (%)",       min=0,   max=100, step=1,    val=40,   impact=68, effect="neg"),
    dict(id="kpi",        label="KPI enterprise score",     min=1.5, max=3.0, step=0.05, val=2.35, impact=61, effect="pos"),
    dict(id="workforce",  label="Workforce stability (%)",  min=0,   max=100, step=1,    val=55,   impact=54, effect="pos"),
    dict(id="euston",     label="Euston restart prob. (%)", min=0,   max=100, step=1,    val=30,   impact=48, effect="pos"),
]

BENEFITS_DATA = dict(
    journey_times = [
        dict(route="London → Birmingham",  current_min=81,  hs2_min=45,
             note="Current: 1hr 21min. HS2: 45min at 320km/h (42min at 360km/h). Source: HS2 project update May 2026"),
        dict(route="London → Manchester",  current_min=127, hs2_min=67,
             note="Via WCML currently 2hr 7min. HS2 Phase 1 + WCML: estimated 1hr 7min. Source: Galliard/DfT planning docs"),
        dict(route="London → Leeds",       current_min=130, hs2_min=80,
             note="Approximate benefit using Phase 1 + WCML. Phase 2 cancellation reduces benefit significantly"),
    ],
    capacity = dict(
        trains_per_hour          = 18,
        passengers_per_train     = 1100,
        daily_passengers         = 350000,
        euston_peak_seats_before = 12100,
        euston_peak_seats_after  = 31200,
        train_length_m           = 400,
        note="Capacity figures based on full Phase 1 design spec. 18tph is design maximum; actual service TBD after programme reset."
    ),
    speed = dict(
        original_design_kmh  = 360,
        current_design_kmh   = 320,
        fastest_europe_kmh   = 320,
        uk_existing_max_kmh  = 201,
        wcml_max_kmh         = 177,
        note="Speed reduced from 360 to 320km/h in 2026 reset. Adds ~3min to London-Birmingham journey (45 vs 42min)."
    ),
)

SCOPE_DATA = [
    dict(year=2012, label="2012 — Original approval",
         route_km=540, route_miles=340, stations=11, tunnels_km=36, viaducts=50,
         bridges=500, max_speed_kmh=360, cities_served=11,
         scope_note="Full Y-network: London → Birmingham → Manchester + Leeds. 351 miles of new track.",
         colour="pos"),
    dict(year=2021, label="2021 — Eastern leg cut",
         route_km=490, route_miles=305, stations=9, tunnels_km=52, viaducts=52,
         bridges=175, max_speed_kmh=360, cities_served=8,
         scope_note="Eastern leg (Leeds/Sheffield) cancelled. Western spine (Manchester) retained.",
         colour="neu"),
    dict(year=2023, label="2023 — Phase 2 cancelled",
         route_km=225, route_miles=140, stations=4, tunnels_km=52, viaducts=52,
         bridges=130, max_speed_kmh=360, cities_served=2,
         scope_note="All northern phases cancelled by PM Sunak. Phase 1 London-Birmingham only.",
         colour="neg"),
    dict(year=2026, label="2026 — Current (reset)",
         route_km=225, route_miles=140, stations=4, tunnels_km=52, viaducts=52,
         bridges=130, max_speed_kmh=320, cities_served=2,
         scope_note="Speed reduced 360→320km/h. Civil eng ~2/3 complete. Programme reset underway.",
         colour="neg"),
]

WORKFORCE_APPROVAL = dict(
    periods   = ["Sep 2020\n(construction start)", "Oct 2022\n(peak Phase 1)",
                 "Jul-Sep 2023\n(Phase 2 cancel)", "2024-25 (AR)"],
    wf_k      = [22,    30,    30.2,  33   ],
    parl      = [-0.40, -0.60, -0.85, -0.72],
    media     = [-0.30, -0.60, -0.85, -0.81],
    cost_bn   = [40.0,  85.0,  95.2,  95.2 ],
    network_km= [540,   490,   225,   225  ],
)

VIABILITY_DATA = dict(
    years       = [2012, 2013, 2015, 2019, 2020, 2024, 2026],
    cost_mid    = [32.7, 46.0, 55.7, 75.2, 85.0, 57.8, 95.2],
    cost_low    = [32.7, 46.0, 55.7, 72.1, 72.0, 49.0, 87.7],
    cost_high   = [32.7, 46.0, 55.7, 78.4, 98.0, 66.6, 102.7],
    network_km  = [540,  540,  540,  520,  490,  225,  225],
    sentiment   = [-0.10,-0.15,-0.20,-0.60,-0.40,-0.72,-0.72],
    verified    = [False, False, True, True, True, True, True],
    slope          = -0.3703,
    intercept      = -1.1239,
    r2             = 0.838,
    p_val          = 0.0038,
    threshold_sent = -0.40,
    threshold_cpkm = 0.142,
)
