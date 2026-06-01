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

# Monte Carlo parameter definitions
# Impact scores are MODEL-DERIVED (sensitivity analysis), not from reports.
PARAMS = [
    dict(id="inflation",  label="Inflation rate (%/yr)",    min=2,   max=14,  step=0.5,  val=5.0,  impact=87, effect="neg"),
    dict(id="scope",      label="Scope change risk (%)",    min=0,   max=100, step=1,    val=35,   impact=72, effect="neg"),
    dict(id="political",  label="Political risk (%)",       min=0,   max=100, step=1,    val=40,   impact=68, effect="neg"),
    dict(id="kpi",        label="KPI enterprise score",     min=1.5, max=3.0, step=0.05, val=2.35, impact=61, effect="pos"),
    dict(id="workforce",  label="Workforce stability (%)",  min=0,   max=100, step=1,    val=55,   impact=54, effect="pos"),
    dict(id="euston",     label="Euston restart prob. (%)", min=0,   max=100, step=1,    val=30,   impact=48, effect="pos"),
]
