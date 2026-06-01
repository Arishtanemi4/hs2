import pandas as pd
from ..config.theme import C

# Proxy scores — NOT official surveys. Derived from qualitative signals:
# parliamentary questioning tone (PAC reports), media framing, workforce signals (annual reports).
SENTIMENT_DF = pd.DataFrame({
    "year":       ["2016","2017","2018","2019","2020","2021","2022","2023","2024","2025"],
    "parliament": [-0.20,-0.30,-0.40,-0.60,-0.40,-0.50,-0.60,-0.80,-0.72,-0.65],
    "workforce":  [ 0.50, 0.40, 0.40, 0.30, 0.20, 0.30, 0.20, 0.10, 0.28, 0.35],
    "media":      [-0.30,-0.30,-0.40,-0.50,-0.30,-0.50,-0.60,-0.85,-0.81,-0.70],
})

# Proxy composite scores by stakeholder group (see source comment in original file for derivation)
STAKEHOLDER_SENT = [
    ("Parliament / PAC",     -0.72, C["neg"]),
    ("National media",       -0.81, C["neg"]),
    ("Affected communities", -0.65, C["neg"]),
    ("HS2 Ltd workforce",     0.28, C["neu"]),
    ("Supply chain JVs",      0.15, C["neu"]),
    ("Transport experts",    -0.12, C["muted"]),
    ("Regional businesses",   0.44, C["pos"]),
]
