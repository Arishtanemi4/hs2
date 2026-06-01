import pandas as pd

# Sources: AR 2023-24 (HC 106); AR 2024-25 (HC 1088)
# Earlier years not available from primary sources — not included.
SPEND_DF = pd.DataFrame({
    "year":      ["2023–24",          "2024–25",          "2025–26 (budget)"],
    "budget_bn": [7.917,              None,                7.1],
    "actual_bn": [7.868,              7.5,                 None],
    "source":    ["AR 2023-24 HC106", "AR 2024-25 HC1088", "AR 2024-25 HC1088"],
    "verified":  [True,               True,                True],
})

# 71 million working hours in 2024-25 (AR 2024-25); 65m in 2023-24 (AR 2023-24)
WORKING_HOURS_DF = pd.DataFrame({
    "year":    ["2022–23",              "2023–24",                        "2024–25"],
    "hours_m": [62,                      65,                               71],
    "source":  ["safety.hs2.org.uk", "safety.hs2.org.uk + AR 2023-24", "AR 2024-25 HC1088"],
})
