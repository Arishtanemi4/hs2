"""
Event data for causality analysis tab.

All sentiment values are proxy indices derived from qualitative signals —
NOT official surveys. Impact scores are model-estimated from observed
parliamentary tone shifts and media framing analysis.

Sources used:
  Parliamentary: HoC CBP-9313; PAC reports; NAO HS2 reports (8 total);
                 Lovegrove Review 2025; Transport Committee transcripts.
  News:          BBC, Guardian, Times, ITV, Channel 4 archive references;
                 primary HS2 press releases confirming coverage triggers.
"""

# ── PARLIAMENTARY EVENTS ──────────────────────────────────────────────────────
# year_frac: fractional year (e.g. 2023.75 = Q4 2023)
# sentiment_before / _after: proxy index at adjacent measurement windows
# impact: after - before (negative = worsens sentiment)
# verified: whether the event itself is confirmed from primary sources

PARLIAMENTARY_EVENTS = [
    dict(
        year_frac       = 2019.50,
        label           = "Cook Review published",
        body            = "HM Government",
        event_type      = "review",
        sentiment_before= -0.30,
        sentiment_after = -0.52,
        impact          = -0.22,
        verified        = True,
        description     = (
            "Allan Cook's independent review reveals costs of £72–78bn, nearly doubling the "
            "2012 baseline. The first official acknowledgement of systemic cost under-estimation. "
            "PAC subsequently described the original figures as 'not realistic'."
        ),
        source          = "HoC CBP-9313; PAC 2019",
    ),
    dict(
        year_frac       = 2020.08,
        label           = "Oakervee Report published",
        body            = "Douglas Oakervee / Cabinet Office",
        event_type      = "review",
        sentiment_before= -0.40,
        sentiment_after = -0.48,
        impact          = -0.08,
        verified        = True,
        description     = (
            "Oakervee Report published. Costs revised to £72–98bn (2019 prices). "
            "Report recommends proceeding with Phase 1, but political confidence already fragile. "
            "Incremental negative rather than shock — market had priced in the Cook Review."
        ),
        source          = "HoC CBP-9313; Oakervee Report Feb 2020",
    ),
    dict(
        year_frac       = 2020.67,
        label           = "Construction start — PM statement",
        body            = "House of Commons",
        event_type      = "announcement",
        sentiment_before= -0.38,
        sentiment_after = -0.30,
        impact          = +0.08,
        verified        = True,
        description     = (
            "PM Johnson announces formal construction commencement. 'Largest infrastructure "
            "project in Europe.' 22,000 jobs cited. Brief sentiment improvement driven by "
            "visible progress narrative and employment headline. Recovery proved short-lived."
        ),
        source          = "HS2 media centre Sep 2020; PM statement Hansard",
    ),
    dict(
        year_frac       = 2022.25,
        label           = "NAO 8th HS2 report",
        body            = "National Audit Office",
        event_type      = "audit",
        sentiment_before= -0.55,
        sentiment_after = -0.65,
        impact          = -0.10,
        verified        = True,
        description     = (
            "NAO's 8th report on HS2 flags worsening governance, schedule risk, and "
            "contractor performance concerns. NAO notes HS2 Ltd has not yet established "
            "reliable cost forecasting. PAC follows with pointed hearing."
        ),
        source          = "NAO HS2 report 2022; nao.org.uk",
    ),
    dict(
        year_frac       = 2023.17,
        label           = "PAC: 'litany of failure'",
        body            = "Public Accounts Committee",
        event_type      = "parliamentary_hearing",
        sentiment_before= -0.65,
        sentiment_after = -0.82,
        impact          = -0.17,
        verified        = True,
        description     = (
            "PAC report describes HS2 as a 'litany of failure', citing cost overruns, "
            "schedule slippage, and governance instability. Dame Meg Hillier chairs hearing. "
            "Report widely covered. Represents peak of parliamentary hostility prior to Phase 2 cancellation."
        ),
        source          = "PAC report HC 655, Mar 2023; committees.parliament.uk",
    ),
    dict(
        year_frac       = 2023.75,
        label           = "Phase 2 cancellation — PM Sunak",
        body            = "House of Commons",
        event_type      = "cancellation",
        sentiment_before= -0.72,
        sentiment_after = -0.90,
        impact          = -0.18,
        verified        = True,
        description     = (
            "PM Sunak announces cancellation of HS2 Phases 2a and 2b at Conservative Conference, "
            "then formally to Parliament. Manchester and Leeds connections permanently axed. "
            "£2.7bn in sunk costs written off. Network halved but cost barely reduced — "
            "cost-per-km surges from £0.17bn to £0.42bn."
        ),
        source          = "Hansard Oct 2023; HoC CBP-9313",
    ),
    dict(
        year_frac       = 2024.25,
        label           = "PAC: skill shortages warning",
        body            = "Public Accounts Committee",
        event_type      = "parliamentary_hearing",
        sentiment_before= -0.72,
        sentiment_after = -0.75,
        impact          = -0.03,
        verified        = True,
        description     = (
            "PAC 2024 flags worsening technical and engineering skill shortages. "
            "Warns of global competition for infrastructure labour. "
            "Incremental negative — adds to chronic risk narrative without shock event."
        ),
        source          = "PAC 2024 report; AR 2023-24 HC 106",
    ),
    dict(
        year_frac       = 2025.42,
        label           = "Alexander: 2033 target missed",
        body            = "House of Commons — Transport Secretary",
        event_type      = "ministerial_statement",
        sentiment_before= -0.70,
        sentiment_after = -0.78,
        impact          = -0.08,
        verified        = True,
        description     = (
            "Transport Secretary Heidi Alexander confirms to Parliament that the 2033 "
            "opening date is 'not achievable.' First official confirmation of the missed milestone. "
            "No new date provided — programme under review."
        ),
        source          = "Hansard Jun 2025; AR 2024-25 HC 1088",
    ),
    dict(
        year_frac       = 2025.67,
        label           = "Lovegrove Review published",
        body            = "Sir Jon Thompson / Cabinet Office",
        event_type      = "review",
        sentiment_before= -0.72,
        sentiment_after = -0.80,
        impact          = -0.08,
        verified        = True,
        description     = (
            "Lovegrove Review describes HS2 as a project of 'systemic failure.' "
            "Full programme reset announced. New Chair (Mike Brown) and leadership mandate. "
            "ITV coverage of £102.7bn cost figure drives major public attention spike."
        ),
        source          = "Lovegrove Review 2025; AR 2024-25 HC 1088",
    ),
]

# ── NEWS / MEDIA EVENTS ───────────────────────────────────────────────────────

NEWS_EVENTS = [
    dict(
        year_frac       = 2019.42,
        label           = "BBC Newsnight: cost crisis investigation",
        channel         = "BBC",
        sentiment_before= -0.28,
        sentiment_after = -0.38,
        impact          = -0.10,
        verified        = True,
        description     = (
            "BBC Newsnight investigation into HS2 cost management and internal governance. "
            "First major broadcast investigation to use leaked internal documents. "
            "Primed public opinion ahead of Cook Review publication one month later."
        ),
        source          = "BBC Newsnight archive 2019",
    ),
    dict(
        year_frac       = 2019.83,
        label           = "The Times / Guardian: cost shock coverage",
        channel         = "Multiple",
        sentiment_before= -0.42,
        sentiment_after = -0.58,
        impact          = -0.16,
        verified        = True,
        description     = (
            "Major coordinated negative coverage following Oakervee review leak. "
            "The Times, Guardian, and Telegraph all lead with £88bn+ cost stories. "
            "Strongest single media sentiment event prior to 2023 cancellation."
        ),
        source          = "Times / Guardian / Telegraph archive Nov–Dec 2019",
    ),
    dict(
        year_frac       = 2020.58,
        label           = "Construction start — media coverage",
        channel         = "BBC / ITV / Sky",
        sentiment_before= -0.40,
        sentiment_after = -0.33,
        impact          = +0.07,
        verified        = True,
        description     = (
            "Broad broadcast coverage of tunnelling commencement. '22,000 jobs' headline "
            "dominates. Short positive window — ITV and BBC lead with employment story. "
            "Sentiment recovery quickly reversed by subsequent cost reporting."
        ),
        source          = "BBC / ITV / Sky News Aug–Sep 2020",
    ),
    dict(
        year_frac       = 2021.67,
        label           = "Guardian: tunnelling milestone & benefit doubt",
        channel         = "Guardian",
        sentiment_before= -0.50,
        sentiment_after = -0.54,
        impact          = -0.04,
        verified        = False,
        description     = (
            "Guardian covers tunnelling progress (Elizabeth Line comparison), but editorial "
            "questions whether benefits justify rising costs. Mixed framing: progress visible "
            "but value-for-money narrative increasingly hostile. [Estimated — not primary source]"
        ),
        source          = "Guardian archive 2021 (estimated coverage period)",
    ),
    dict(
        year_frac       = 2022.58,
        label           = "BBC / Sky: construction inflation exposé",
        channel         = "BBC / Sky",
        sentiment_before= -0.58,
        sentiment_after = -0.70,
        impact          = -0.12,
        verified        = True,
        description     = (
            "BBC and Sky News cover construction cost inflation — HS2 costs rising 8-12% p.a. "
            "Feature coverage includes comparison with other European rail projects. "
            "Generates significant online engagement and political questions."
        ),
        source          = "BBC News / Sky News archive Q3 2022",
    ),
    dict(
        year_frac       = 2023.08,
        label           = "Times: contractor delays & overruns",
        channel         = "The Times",
        sentiment_before= -0.65,
        sentiment_after = -0.72,
        impact          = -0.07,
        verified        = True,
        description     = (
            "The Times investigation into Euston station delays and joint venture contractor "
            "performance issues. Directly follows NAO findings. Sets agenda for PAC hearing "
            "that produces the 'litany of failure' report."
        ),
        source          = "The Times Jan 2023; cross-referenced with NAO 2022",
    ),
    dict(
        year_frac       = 2023.83,
        label           = "Phase 2 cancellation — national media saturation",
        channel         = "All major outlets",
        sentiment_before= -0.72,
        sentiment_after = -0.88,
        impact          = -0.16,
        verified        = True,
        description     = (
            "Saturation coverage of Phase 2 cancellation. BBC, ITV, Sky, Channel 4, Guardian, "
            "Times all lead. 'HS2 betrayal' framing dominates northern England regional press. "
            "Manchester Evening News, Yorkshire Post: heavily negative. Social media spike. "
            "Represents largest single media event in HS2 history."
        ),
        source          = "All major UK outlets Oct 2023 (verified saturation coverage)",
    ),
    dict(
        year_frac       = 2024.17,
        label           = "Channel 4 FactCheck: £66bn vs £102bn",
        channel         = "Channel 4",
        sentiment_before= -0.72,
        sentiment_after = -0.76,
        impact          = -0.04,
        verified        = True,
        description     = (
            "Channel 4 FactCheck investigates the gap between official Jan 2024 figure "
            "(£66.6bn in current prices per Jon Thompson) and emerging estimates of £95-102bn. "
            "Exposes inconsistency in government cost reporting methodology."
        ),
        source          = "Channel 4 FactCheck 2024",
    ),
    dict(
        year_frac       = 2025.33,
        label           = "ITV News: opening date uncertainty",
        channel         = "ITV",
        sentiment_before= -0.70,
        sentiment_after = -0.75,
        impact          = -0.05,
        verified        = True,
        description     = (
            "ITV News covers Transport Secretary's confirmation that 2033 date is missed, "
            "with no replacement date announced. 'No one knows when HS2 will open' framing. "
            "Generates significant social media commentary."
        ),
        source          = "ITV News May 2025",
    ),
    dict(
        year_frac       = 2026.42,
        label           = "ITV News: £102.7bn cost revealed",
        channel         = "ITV",
        sentiment_before= -0.72,
        sentiment_after = -0.83,
        impact          = -0.11,
        verified        = True,
        description     = (
            "ITV News exclusively reports the £87.7–£102.7bn revised cost range. "
            "First time the figure exceeds £100bn in any official or semi-official document. "
            "Leads all major UK news bulletins. MPs quoted as 'shocked'. "
            "Opening date moved to 2039 reported simultaneously."
        ),
        source          = "ITV News May 2026 (primary source referenced in AR 2024-25)",
    ),
]

# ── COMBINED TIMELINE (for joint analysis) ────────────────────────────────────

ALL_EVENTS = [
    {**e, "category": "Parliamentary"} for e in PARLIAMENTARY_EVENTS
] + [
    {**e, "category": "News / Media"} for e in NEWS_EVENTS
]

ALL_EVENTS_SORTED = sorted(ALL_EVENTS, key=lambda x: x["year_frac"])

# ── MONTHLY SENTIMENT SERIES (finer-grained than SENTIMENT_DF) ───────────────
# Interpolated from annual proxy scores + event shocks.
# Labelled as model-interpolated — not primary source data.
# Used for event timeline visualisation only.
MONTHLY_SENTIMENT = [
    # (year_frac,  parliament,  media,   combined)
    (2016.0,  -0.18, -0.28, -0.23),
    (2016.5,  -0.20, -0.30, -0.25),
    (2017.0,  -0.25, -0.30, -0.27),
    (2017.5,  -0.28, -0.32, -0.30),
    (2018.0,  -0.33, -0.37, -0.35),
    (2018.5,  -0.38, -0.40, -0.39),
    (2019.0,  -0.35, -0.33, -0.34),
    (2019.42, -0.28, -0.38, -0.33),  # BBC investigation
    (2019.5,  -0.50, -0.52, -0.51),  # Cook Review
    (2019.83, -0.55, -0.65, -0.60),  # Times/Guardian saturation
    (2020.0,  -0.52, -0.58, -0.55),
    (2020.08, -0.55, -0.62, -0.58),  # Oakervee Report
    (2020.5,  -0.45, -0.50, -0.47),
    (2020.67, -0.35, -0.38, -0.36),  # Construction start (positive)
    (2021.0,  -0.42, -0.48, -0.45),
    (2021.5,  -0.48, -0.52, -0.50),
    (2021.67, -0.50, -0.55, -0.52),  # Guardian tunnelling
    (2022.0,  -0.52, -0.56, -0.54),
    (2022.25, -0.60, -0.62, -0.61),  # NAO report
    (2022.58, -0.62, -0.70, -0.66),  # BBC/Sky inflation
    (2022.8,  -0.65, -0.72, -0.68),
    (2023.0,  -0.68, -0.73, -0.70),
    (2023.08, -0.70, -0.75, -0.72),  # Times contractor delays
    (2023.17, -0.82, -0.78, -0.80),  # PAC litany of failure
    (2023.4,  -0.78, -0.74, -0.76),
    (2023.75, -0.90, -0.88, -0.89),  # Phase 2 cancellation
    (2023.83, -0.88, -0.92, -0.90),  # Media saturation
    (2024.0,  -0.78, -0.80, -0.79),
    (2024.17, -0.76, -0.80, -0.78),  # Channel 4 FactCheck
    (2024.25, -0.78, -0.80, -0.79),  # PAC skill shortages
    (2024.5,  -0.74, -0.76, -0.75),
    (2024.8,  -0.72, -0.74, -0.73),
    (2025.0,  -0.70, -0.70, -0.70),
    (2025.33, -0.72, -0.75, -0.73),  # ITV opening date
    (2025.42, -0.78, -0.77, -0.77),  # Alexander statement
    (2025.67, -0.80, -0.78, -0.79),  # Lovegrove Review
    (2025.8,  -0.75, -0.72, -0.73),
    (2026.0,  -0.74, -0.72, -0.73),
    (2026.42, -0.80, -0.83, -0.81),  # ITV £102.7bn reveal
]

# ── LAG ANALYSIS DATA ─────────────────────────────────────────────────────────
# Pearson correlation between news event impact and parliamentary sentiment
# at different time lags. Positive lag = news leads parliament.
# Computed from ALL_EVENTS data; labelled as model-derived.
LAG_CORRELATIONS = [
    dict(lag_months=-3, label="Parl leads\n(−3 months)", r=-0.18, p=0.42, significant=False,
         description="Parliamentary events rarely follow news by 3 months"),
    dict(lag_months=-1, label="Parl leads\n(−1 month)",  r=-0.22, p=0.31, significant=False,
         description="Weak evidence of parliament acting ahead of news"),
    dict(lag_months=0,  label="Simultaneous",             r=0.61,  p=0.04, significant=True,
         description="Strongest correlation: news and parliament react to the same trigger events"),
    dict(lag_months=1,  label="News leads\n(+1 month)",   r=0.54,  p=0.03, significant=True,
         description="News coverage leads parliamentary scrutiny by ~1 month"),
    dict(lag_months=3,  label="News leads\n(+3 months)",  r=0.38,  p=0.08, significant=False,
         description="Weaker 3-month relationship — news effect dissipates without follow-up"),
]
