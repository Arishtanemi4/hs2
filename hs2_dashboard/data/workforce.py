import pandas as pd

# Source: HS2 media centre press releases; AR 2024-25
# Total workforce figures (HS2 Ltd staff + all supply chain combined).
WORKFORCE_DF = pd.DataFrame({
    "period": [
        "Sep 2020 (construction start)",
        "Oct 2022",
        "Jul-Sep 2023",
        "2024-25 (AR 2024-25)",
    ],
    "total": [22_000, 30_000, 30_204, 33_000],
    "source": [
        "PM Johnson statement (ConstructionEnquirer Sep 2020)",
        "HS2 media centre (Oct 2022)",
        "HS2 media centre (Nov 2023)",
        "AR 2024-25 HC1088 (CEO intro)",
    ],
    "verified": [True, True, True, True],
})
