import pandas as pd

# Sources: HoC Library CBP-9313; ITV News May 2026
# Pre-2024 figures cover the full network (Phases 1+2a+2b).
# Post-Oct 2023 figures cover Phase 1 only (London–Birmingham) after Phase 2 cancellation.
COST_DF = pd.DataFrame({
    "year":     [2012, 2013, 2015, 2019, 2020, 2024,   2026],
    "low":      [32.7,  46,  55.7, 72.1,  72,   49,   87.7],
    "high":     [32.7,  46,  55.7, 78.4,  98,  66.6, 102.7],
    "baseline": [32.7] * 7,
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
    ],
})

# Sources: HoC Library CBP-9313; ITV News timeline May 2026; AR 2024-25
SCHEDULE_DF = pd.DataFrame({
    "revision": [
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
    "colour":     ["pos", "neu", "neu", "neg", "neg"],
})
