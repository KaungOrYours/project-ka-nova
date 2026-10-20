"""
================================================================================
PROJECT KA-NOVA
engine/external_layer.py

External World Layer — Phase 3
Per-scenario, population-weighted country and institution signal vectors.
Calibrated from real sanctions, FDI, trade, security and treaty data —
each scenario's OWN real geopolitical context, not Myanmar's relabelled.

Architecture (generalized 2026-10-20 — "per-country realism" standing
requirement, .claude/memory.md section 11):
    ExternalLayer(scenario, seed).step(year, shared_data)
        -> updates shared_data["external"]

    Both the STRUCTURE (drift -> stochastic shocks -> cascade -> derived
    signals) and the CODE PATH are identical for every scenario — this is
    the same "engine stays agnostic, bias lives only in the parameter
    layer" principle already applied to the constitution layer
    (config/scenario_registry.py, bug #11). What differs per scenario is
    DATA ONLY: which countries/institutions exist as vectors, their
    year-zero values and drift rates, which shock types are historically
    real for that country/window, and which real vector feeds each of the
    six generic derived-signal keys the rest of the engine reads
    (china_influence / western_pressure / fdi_level / illicit_pressure /
    regional_stability / un_pressure — key NAMES kept literal for
    backward-compatible CSV columns and Prometheus gauges; see
    SIGNAL_MAP docstring below for what they mean per scenario).

    A and C (Myanmar) are UNCHANGED: SHOCK_EVENTS / INITIAL_VECTORS /
    VECTOR_DRIFT below are the original, byte-for-byte untouched Myanmar
    data, and EXTERNAL_LAYER_REGISTRY["A"] / ["C"] both point at the exact
    same dict objects — not re-transcribed copies — so there is zero
    opportunity for a transcription drift to change Scenario A/C behaviour.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union


# ══════════════════════════════════════════════════════════════════════════════
# MYANMAR (Scenario A / C) — ORIGINAL DATA, UNCHANGED
# Every literal value below is identical to the pre-refactor module-level
# globals. Do not "improve" these as part of touching this file; A/C's
# already-published numbers depend on them being exactly this.
# ══════════════════════════════════════════════════════════════════════════════

SHOCK_EVENTS = {
    "pandemic": {
        "probability":      0.02,   # ~once per 50 years historically
        "duration_years":   3,
        "intensity":        (0.30, 0.60),
        "affected_vectors": ["china", "india", "usa", "eu", "asean",
                             "imf_world_bank", "global_economy"],
        "social_media_amp": 2.0,    # High amplification — fear spreads fast
        "description":      "Global pandemic — trade collapse, aid influx, brain drain spike",
        "trust_impact":     -0.05,
        "corruption_impact": 0.03,  # Emergency spending = corruption opportunity
    },
    "regional_conflict": {
        "probability":      0.05,
        "duration_years":   2,
        "intensity":        (0.15, 0.40),
        "affected_vectors": ["china", "india", "thailand", "asean"],
        "social_media_amp": 1.8,
        "description":      "Regional armed conflict — refugee flows, trade disruption",
        "trust_impact":     -0.03,
        "corruption_impact": 0.02,
    },
    "global_recession": {
        "probability":      0.08,
        "duration_years":   2,
        "intensity":        (0.20, 0.45),
        "affected_vectors": ["usa", "eu", "imf_world_bank", "global_economy",
                             "foreign_investors"],
        "social_media_amp": 1.5,
        "description":      "Global recession — FDI freeze, remittance drop",
        "trust_impact":     -0.04,
        "corruption_impact": 0.01,
    },
    "natural_disaster": {
        "probability":      0.10,
        "duration_years":   1,
        "intensity":        (0.10, 0.35),
        "affected_vectors": ["asean", "china", "india", "un_agencies"],
        "social_media_amp": 2.5,    # Disaster spreads fastest on social media
        "description":      "Cyclone/earthquake/flood — humanitarian crisis, aid influx",
        "trust_impact":     -0.02,
        "corruption_impact": 0.04,  # Disaster aid = high corruption risk
    },
    "sanctions": {
        "probability":      0.15,   # Higher — Myanmar already under sanctions
        "duration_years":   3,
        "intensity":        (0.20, 0.50),
        "affected_vectors": ["usa", "eu", "foreign_investors", "imf_world_bank"],
        "social_media_amp": 1.3,
        "description":      "International sanctions — FDI collapse, banking isolation",
        "trust_impact":     0.02,   # Citizens may rally against sanctions narrative
        "corruption_impact": 0.05,  # Sanctions = black market = more corruption
    },
    "oil_price_shock": {
        "probability":      0.08,
        "duration_years":   2,
        "intensity":        (0.15, 0.40),
        "affected_vectors": ["china", "india", "global_economy",
                             "illicit_network_1", "illicit_network_2"],
        "social_media_amp": 1.2,
        "description":      "Oil price shock — energy costs, inflation, illicit trade spike",
        "trust_impact":     -0.03,
        "corruption_impact": 0.02,
    },
    "fdi_boom": {
        "probability":      0.06,
        "duration_years":   3,
        "intensity":        (0.20, 0.50),  # Positive shock — vectors increase
        "affected_vectors": ["foreign_investors", "china", "asean",
                             "global_economy"],
        "social_media_amp": 1.1,
        "description":      "FDI boom — investment surge, knowledge transfer",
        "trust_impact":     0.04,
        "corruption_impact": -0.01,  # More formal economy = less corruption opportunity
        "positive":         True,
    },
    "coup_in_neighbor": {
        "probability":      0.04,
        "duration_years":   2,
        "intensity":        (0.15, 0.35),
        "affected_vectors": ["asean", "china", "india", "thailand"],
        "social_media_amp": 2.0,
        "description":      "Coup in neighboring country — regional instability contagion",
        "trust_impact":     -0.05,
        "corruption_impact": 0.01,
    },
    "technology_leap": {
        "probability":      0.05,
        "duration_years":   5,
        "intensity":        (0.10, 0.30),
        "affected_vectors": ["usa", "eu", "china", "foreign_investors"],
        "social_media_amp": 1.0,
        "description":      "Global tech leap — knowledge capital opportunity",
        "trust_impact":     0.02,
        "corruption_impact": -0.01,
        "positive":         True,
    },
    "internet_shutdown_pressure": {
        "probability":      0.07,
        "duration_years":   1,
        "intensity":        (0.10, 0.25),
        "affected_vectors": ["usa", "eu", "un_agencies"],
        "social_media_amp": 3.0,    # Shutdown attempts cause massive social media spike
        "description":      "International pressure on internet freedom",
        "trust_impact":     0.01,
        "corruption_impact": 0.00,
    },
}

INITIAL_VECTORS = {
    # Neighbours — highest baseline influence
    "china":            0.75,   # BRI, trade, border, veto power
    "india":            0.45,   # Trade, Kaladan corridor, NE India
    "thailand":         0.40,   # Refugee flows, trade, Mae Sot corridor
    "bangladesh":       0.25,   # Rohingya crisis, border trade

    # Major powers
    "usa":              0.35,   # Sanctions, democracy promotion
    "eu":               0.30,   # Sanctions, GSP trade preferences

    # Regional bodies
    "asean":            0.50,   # Regional governance, Five-Point Consensus
    "un_agencies":      0.40,   # Humanitarian aid, UNHCR, WFP

    # Economic institutions
    "imf_world_bank":   0.25,   # Conditional lending, structural reform pressure
    "foreign_investors": 0.20,  # FDI baseline — low post-2021

    # Global economy signal
    "global_economy":   0.60,   # Trade conditions, commodity prices

    # China proxy states (support military government)
    "china_proxy_1":    0.30,   # Russia — arms, veto cover
    "china_proxy_2":    0.20,   # Belarus-equivalent — diplomatic support
    "china_proxy_3":    0.15,   # North Korea-equivalent — arms channel

    # Illicit networks
    "illicit_network_1": 0.35,  # Drug trade — Golden Triangle
    "illicit_network_2": 0.25,  # Arms smuggling
    "illicit_network_3": 0.20,  # Money laundering — hawala, crypto
}

# Annual drift rates — how each vector naturally evolves without shocks
# Positive = growing influence, negative = declining
VECTOR_DRIFT = {
    "china":            0.005,   # China influence grows over 50 years
    "india":            0.003,
    "thailand":         0.001,
    "bangladesh":       0.001,
    "usa":              -0.002,  # US influence in SEA slowly declining
    "eu":               -0.001,
    "asean":            0.002,
    "un_agencies":      0.000,
    "imf_world_bank":   0.001,
    "foreign_investors": 0.004,  # FDI grows as region develops
    "global_economy":   0.000,
    "china_proxy_1":    0.002,
    "china_proxy_2":    0.001,
    "china_proxy_3":    0.000,
    "illicit_network_1": -0.003, # Drug trade declines with development
    "illicit_network_2": -0.002,
    "illicit_network_3": -0.001,
}

# ── Derived-signal map — how the 6 generic downstream keys are built ───────────
# The rest of the engine (model_phase3.py, engine/social_media.py,
# engine/elite_agents_v3.py, run_phase3.py/monitor/metrics_exporter.py's
# Prometheus gauge) reads exactly six generic keys off shared_data["external"]:
# china_influence, western_pressure, fdi_level, illicit_pressure,
# regional_stability, un_pressure. Those literal key NAMES are kept everywhere
# (backward-compatible CSV columns / Grafana panels), but what each one MEANS
# is now scenario-data, not a Myanmar-only hardcoded vector lookup.
#   - a string value   -> that single vector's current value
#   - a list of strings -> the mean of those vectors' current values
#   - missing/None/[]   -> 0.0 (the signal genuinely does not apply to this
#     scenario; see each country's block below for why, sourced from
#     config/constitution_<country>_encoding/README.md section 6.4)
MYANMAR_SIGNAL_MAP = {
    "great_power_influence": "china",
    "external_pressure":     ["usa", "eu"],
    "fdi":                    "foreign_investors",
    "illicit":                ["illicit_network_1", "illicit_network_2", "illicit_network_3"],
    "regional":                ["asean", "thailand", "india"],
    "multilateral":             "un_agencies",
}


# ══════════════════════════════════════════════════════════════════════════════
# SOUTH KOREA 1987 — year zero 1988
# Source: config/constitution_southkorea_encoding/README.md section 6.4/6.5.
# Chain type: civilian. ETHNIC_GROUPS: 1 (not relevant here).
# ══════════════════════════════════════════════════════════════════════════════

SOUTHKOREA_VECTORS = {
    # The defining relationship — existential threat, zero trade at year
    # zero. Real history is non-monotonic (Sunshine Policy lowers it
    # 1998-2008, Cheonan/Yeonpyeong/nuclear tests raise it again). A single
    # flat drift cannot carry a non-monotonic path, so this vector is kept
    # FLAT (drift 0.000) and its real variance is carried entirely by the
    # dprk_military_provocation / dprk_nuclear_crisis shocks below — a
    # deliberate modelling choice, not an oversight.
    "north_korea":              0.70,
    # Treaty ally, ~43,000 USFK troops (1988), also the Super 301 trade
    # coercion channel and the external actor that pressed against martial
    # law in June 1987.
    "usa":                      0.55,
    # Colonial-legacy antagonist AND the key capital/technology supplier.
    "japan":                    0.45,
    # No diplomatic relations at year zero (PRC was DPRK's ally).
    # Normalised 24 Aug 1992 (~sim year 4); largest trade partner by 2004.
    # README flags this as "a scripted regime change, not a drift" — the
    # engine has no scripted-year mechanism (would violate the
    # constitutionally-agnostic/symmetric engine principle to hand-code a
    # Korea-only "if year==4" branch), so this is approximated as a single
    # elevated linear drift across the window instead. Flagged limitation,
    # not hidden.
    "china":                     0.00,
    # No relations at year zero; normalised 30 Sept 1990.
    "ussr_russia":               0.00,
    # Real, dated, one-time IMF standby (3 Dec 1997, US$58.4bn) — carried by
    # the financial_crisis_imf_program shock below, not by drift.
    "imf":                       0.10,
    # No UN seat at year zero (admitted 17 Sept 1991); OECD 1996; G20 host
    # 2010 — a rising, legitimacy-conferring channel, structurally the
    # OPPOSITE of Myanmar's humanitarian-pressure-shaped UN vector.
    "multilateral_institutions": 0.10,
    "global_economy":            0.65,
    "foreign_investors":         0.15,
}

SOUTHKOREA_DRIFT = {
    "north_korea":              0.000,
    "usa":                      -0.001,
    "japan":                     0.001,
    "china":                     0.013,   # see note above re: scripted-vs-drift
    "ussr_russia":               0.004,
    "imf":                       0.000,
    "multilateral_institutions": 0.012,
    "global_economy":            0.000,
    "foreign_investors":         0.006,
}

SOUTHKOREA_SHOCKS = {
    "financial_crisis_imf_program": {
        "probability": 0.03, "duration_years": 3, "intensity": (0.35, 0.60),
        "affected_vectors": ["imf", "foreign_investors", "global_economy", "usa"],
        "social_media_amp": 1.6, "trust_impact": -0.05, "corruption_impact": 0.02,
        "description": "Asian Financial Crisis — IMF standby 3 Dec 1997, US$58.4bn, chaebol/labour/financial-supervision conditionality",
    },
    "dprk_military_provocation": {
        "probability": 0.10, "duration_years": 1, "intensity": (0.20, 0.45),
        "affected_vectors": ["north_korea", "usa"],
        "social_media_amp": 2.2, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "DPRK military provocation — submarine infiltration / Yellow Sea clashes / Cheonan-Yeonpyeong-scale incident",
    },
    "dprk_nuclear_crisis": {
        "probability": 0.05, "duration_years": 2, "intensity": (0.25, 0.50),
        "affected_vectors": ["north_korea", "china", "usa"],
        "social_media_amp": 2.0, "trust_impact": -0.04, "corruption_impact": 0.00,
        "description": "DPRK nuclear crisis — 1993-94 Agreed Framework episode / weapons test",
    },
    "economic_coercion_by_partner": {
        "probability": 0.04, "duration_years": 2, "intensity": (0.15, 0.35),
        "affected_vectors": ["china", "japan", "foreign_investors"],
        "social_media_amp": 1.4, "trust_impact": -0.02, "corruption_impact": 0.01,
        "description": "Coercion by a major trade partner — THAAD-style retaliation / export-control restriction, not a hostile-bloc sanction",
    },
    "executive_corruption_scandal": {
        "probability": 0.05, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["multilateral_institutions", "usa"],
        "social_media_amp": 1.8, "trust_impact": -0.02, "corruption_impact": -0.02,
        "description": "Executive corruption scandal resolved via impeachment/removal, not collapse — the 1995-96 and 2016-17 and 2024-25 pattern; corruption_impact is net NEGATIVE (improving) because impeachment is itself anti-corruption enforcement, the key mechanic behind the 122-day self-correction finding",
    },
    "global_recession": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["usa", "foreign_investors", "global_economy"],
        "social_media_amp": 1.5, "trust_impact": -0.04, "corruption_impact": 0.01,
        "description": "Global recession — transfers from Myanmar's set",
    },
    "oil_price_shock": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["global_economy", "foreign_investors"],
        "social_media_amp": 1.2, "trust_impact": -0.03, "corruption_impact": 0.02,
        "description": "Oil price shock — Korea imports essentially all its oil, higher sensitivity than Myanmar",
    },
    "pandemic": {
        "probability": 0.02, "duration_years": 2, "intensity": (0.25, 0.50),
        "affected_vectors": ["usa", "japan", "china", "global_economy"],
        "social_media_amp": 2.0, "trust_impact": -0.05, "corruption_impact": 0.02,
        "description": "2015 MERS outbreak / 2020 COVID-19",
    },
    "export_technology_boom": {
        "probability": 0.05, "duration_years": 4, "intensity": (0.15, 0.35),
        "affected_vectors": ["foreign_investors", "global_economy", "japan"],
        "social_media_amp": 1.0, "trust_impact": 0.02, "corruption_impact": -0.01,
        "description": "Semiconductor / Hallyu cultural export boom", "positive": True,
    },
    "status_legitimacy_gain": {
        "probability": 0.05, "duration_years": 3, "intensity": (0.15, 0.35),
        "affected_vectors": ["multilateral_institutions", "foreign_investors", "global_economy"],
        "social_media_amp": 1.1, "trust_impact": 0.03, "corruption_impact": -0.01,
        "description": "1988 Seoul Olympics / 1996 OECD accession / 2002 World Cup / 2012 KORUS FTA", "positive": True,
    },
}

SOUTHKOREA_SIGNAL_MAP = {
    "great_power_influence": "china",
    "external_pressure":     ["usa"],
    "fdi":                    "foreign_investors",
    "illicit":                [],   # Deliberately zero — no real Korean illicit-economy analogue (README 6.4)
    "regional":                [],   # No ASEAN-style regional-stability analogue; DPRK tension carried directly
    "multilateral":             "multilateral_institutions",
}


# ══════════════════════════════════════════════════════════════════════════════
# THAILAND 2017 — year zero 2017
# Source: config/constitution_thailand_encoding/README.md section 6.4/6.5.
# Chain type: military. ETHNIC_GROUPS: 0.
# Note: Thailand is Myanmar's own real neighbour (Myanmar's "thailand"
# vector = 0.40) — the first reciprocal pair in the 7-constitution design.
# This does NOT create a circular dependency: Thailand's "myanmar" vector
# below is TH's own independent geopolitical-context number, read only by
# TH's own ExternalLayer instance, never by Myanmar's.
# ══════════════════════════════════════════════════════════════════════════════

THAILAND_VECTORS = {
    "china":                    0.55,   # Largest trade partner + post-2014-coup security pivot (submarines, tanks, rail)
    "myanmar":                  0.30,   # 2,416km border, largest migrant-labour source, refugee/conflict spillover
    "usa":                      0.20,   # Treaty ally deliberately downgraded post-coup, partially restored from Oct 2017
    "asean":                    0.60,   # Regional SHIELD (non-interference norm insulated the 2014 coup from cost) — opposite sign to Myanmar's ASEAN-as-constraint
    "eu":                        0.15,   # Suspended political/FTA contacts post-coup; IUU "yellow card" Apr 2015
    "japan":                     0.55,   # Largest cumulative FDI stock (automotive), stable and apolitical
    "malaysia":                  0.20,   # Deep South border + peace-process mediator
    "cambodia_laos":             0.10,   # Preah Vihear-era low-intensity border friction
    "global_economy":            0.65,   # Tourism (~11-12% GDP direct) + export dependence
    "illicit_transit_networks":  0.20,   # Transit/destination state (meth inflow, fishing-sector trafficking) — NOT Myanmar's production-side 3-vector structure
    "foreign_investors":         0.25,
}

THAILAND_DRIFT = {
    "china":                    0.004,
    "myanmar":                  0.002,
    "usa":                      0.003,   # Partial restoration from 2017
    "asean":                    0.001,
    "eu":                        0.004,   # Yellow card lifted 2019, FTA talks relaunched 2023
    "japan":                     0.001,
    "malaysia":                  0.001,
    "cambodia_laos":             0.000,
    "global_economy":            0.000,
    "illicit_transit_networks": -0.002,
    "foreign_investors":         0.003,
}

THAILAND_SHOCKS = {
    # Deliberately NO "coup" shock type here: Thailand's actual coup
    # mechanism lives in model_phase3.py's chain-type/COUP_TRIGGER logic
    # (shared across every military-chain scenario), not in the external
    # layer. Adding a second, external-layer coup channel here would
    # double-count the same mechanism and risk exactly the kind of
    # parameterization-driven-not-structural confound section 11 warns
    # against — flagged to the parent agent, see final report.
    "royal_succession_legitimacy": {
        "probability": 0.03, "duration_years": 3, "intensity": (0.20, 0.45),
        "affected_vectors": ["asean", "usa", "eu"],
        "social_media_amp": 1.8, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "Royal succession legitimacy strain — no analogue elsewhere in the 7-scenario set",
    },
    "pandemic": {
        "probability": 0.02, "duration_years": 3, "intensity": (0.35, 0.65),
        "affected_vectors": ["global_economy", "china", "japan"],
        "social_media_amp": 2.2, "trust_impact": -0.06, "corruption_impact": 0.03,
        "description": "COVID-19 — tourism-dependent economy contracted 6.1% in 2020",
    },
    "flooding": {
        "probability": 0.06, "duration_years": 1, "intensity": (0.20, 0.45),
        "affected_vectors": ["global_economy", "asean"],
        "social_media_amp": 2.0, "trust_impact": -0.03, "corruption_impact": 0.04,
        "description": "2011-scale flooding (real base: ~1.4 trillion baht / ~US$46bn)",
    },
    "insurgency_escalation": {
        "probability": 0.10, "duration_years": 2, "intensity": (0.10, 0.30),
        "affected_vectors": ["malaysia", "asean"],
        "social_media_amp": 1.3, "trust_impact": -0.02, "corruption_impact": 0.01,
        "description": "Deep South insurgency escalation (7,700+ deaths since 2004)",
    },
    "trade_sanction_equivalent": {
        "probability": 0.10, "duration_years": 3, "intensity": (0.15, 0.35),
        "affected_vectors": ["eu", "usa"],
        "social_media_amp": 1.3, "trust_impact": 0.01, "corruption_impact": 0.02,
        "description": "EU IUU yellow card / US TIP Tier-3 downgrade — conditional, reversible, sector-specific",
    },
    "tourism_demand_shock": {
        "probability": 0.06, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["china", "global_economy"],
        "social_media_amp": 1.6, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "Chinese arrivals collapse",
    },
    "mekong_drought": {
        "probability": 0.06, "duration_years": 2, "intensity": (0.10, 0.30),
        "affected_vectors": ["global_economy"],
        "social_media_amp": 1.0, "trust_impact": -0.01, "corruption_impact": 0.00,
        "description": "Upstream dam operation / recurring Mekong low-flow",
    },
    "migrant_influx": {
        "probability": 0.05, "duration_years": 2, "intensity": (0.15, 0.35),
        "affected_vectors": ["myanmar", "malaysia"],
        "social_media_amp": 1.5, "trust_impact": -0.02, "corruption_impact": 0.01,
        "description": "Post-coup inflow from Myanmar — reciprocal with Scenario A/C's own outflows",
    },
    "global_recession": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["japan", "usa", "eu", "global_economy"],
        "social_media_amp": 1.5, "trust_impact": -0.04, "corruption_impact": 0.01,
        "description": "Global recession — transfers from Myanmar's set",
    },
    "fdi_boom": {
        "probability": 0.05, "duration_years": 3, "intensity": (0.20, 0.45),
        "affected_vectors": ["japan", "foreign_investors", "china"],
        "social_media_amp": 1.1, "trust_impact": 0.03, "corruption_impact": -0.01,
        "description": "FDI boom — transfers from Myanmar's set", "positive": True,
    },
}

THAILAND_SIGNAL_MAP = {
    "great_power_influence": "china",
    "external_pressure":     ["usa", "eu"],
    "fdi":                    "foreign_investors",
    "illicit":                ["illicit_transit_networks"],
    "regional":                ["asean", "malaysia", "cambodia_laos"],
    "multilateral":             None,   # No UN-humanitarian-pressure analogue in the research package; TH's multilateral channel runs through ASEAN (captured in "regional")
}


# ══════════════════════════════════════════════════════════════════════════════
# PAKISTAN 1973 + 8th Amendment (1985) — year zero 1985
# Source: config/constitution_pakistan_encoding/README.md section 6.4/6.5.
# Chain type: military. ETHNIC_GROUPS: 6 (per memory.md 2026-10-20 decision).
# ══════════════════════════════════════════════════════════════════════════════

PAKISTAN_VECTORS = {
    "india":              0.75,   # Defining existential rival — 3 prior wars, Siachen, Brasstacks, Kargil
    "afghanistan_ussr":   0.60,   # Frontline-state rent: 2.3m+ refugees, ISI mujahideen pipeline — collapses after 1989
    "usa":                0.65,   # Conditional patron — Pressler Amendment enacted 8 Aug 1985 (= year zero)
    "china":              0.70,   # "All-weather" strategic patron — the one relationship stable regardless of regime type
    "saudi_gulf":         0.40,   # Dominant 1980s remittance source + Zia-era Islamisation patronage
    "imf":                0.30,   # Recurrent conditional lender (SAF 1988, 1993, 1995, ESAF 1997)
    "saarc":              0.15,   # Founded 8 Dec 1985 (= year zero) — the real ASEAN analogue, but chronically paralysed/inert
    "global_economy":     0.55,   # Cotton/textile export concentration, energy importer
    "illicit_network_1":  0.45,   # Golden Crescent heroin — production + transit (genuinely transfers from Myanmar's structure)
    "illicit_network_2":  0.35,   # Arms leakage — "Kalashnikov culture" from the Afghan pipeline
    "illicit_network_3":  0.30,   # Hawala / informal finance
    "foreign_investors":  0.15,   # Low historical FDI — aid/remittance-dependent, not FDI-dependent
}

PAKISTAN_DRIFT = {
    "india":              0.001,
    "afghanistan_ussr":   -0.025,  # Decays sharply post-Soviet-withdrawal (1989); clipped at 0.0 floor by step()'s clip
    "usa":                -0.004,
    "china":               0.002,
    "saudi_gulf":          0.001,
    "imf":                 0.000,
    "saarc":               0.000,
    "global_economy":      0.000,
    "illicit_network_1":   0.004,
    "illicit_network_2":   0.002,
    "illicit_network_3":   0.001,
    "foreign_investors":   0.002,
}

PAKISTAN_SHOCKS = {
    "patron_sanctions": {
        "probability": 0.06, "duration_years": 3, "intensity": (0.30, 0.55),
        "affected_vectors": ["usa"],
        "social_media_amp": 1.3, "trust_impact": 0.02, "corruption_impact": 0.03,
        "description": "Pressler certification withheld (1 Oct 1990) / Glenn Amendment (1998) — the cleanest sanctions analogue in the 7-country set",
    },
    "interstate_war_or_crisis": {
        "probability": 0.07, "duration_years": 2, "intensity": (0.25, 0.55),
        "affected_vectors": ["india"],
        "social_media_amp": 2.0, "trust_impact": -0.05, "corruption_impact": 0.01,
        "description": "Brasstacks 1986-87 / 1990 Kashmir nuclear crisis / Kargil 1999 — Kargil is the real proximate cause of the 12 Oct 1999 coup; a genuinely different collapse channel from Scenario C's internally-driven failure",
    },
    "refugee_influx": {
        "probability": 0.08, "duration_years": 3, "intensity": (0.25, 0.50),
        "affected_vectors": ["afghanistan_ussr"],
        "social_media_amp": 1.6, "trust_impact": -0.02, "corruption_impact": 0.02,
        "description": "2.3m rising past 3m Afghan refugees — no Myanmar analogue (Myanmar's set has no inbound-refugee shock)",
    },
    "proxy_war_rent_collapse": {
        "probability": 0.04, "duration_years": 4, "intensity": (0.30, 0.55),
        "affected_vectors": ["afghanistan_ussr", "usa"],
        "social_media_amp": 1.2, "trust_impact": -0.02, "corruption_impact": 0.04,
        "description": "Soviet withdrawal complete 15 Feb 1989 / US aid conditionality lapses 1990 — a positive external rent that VANISHES, a competing explanation for the real 0.637->0.831 corruption jump worth keeping distinct from the constitutional mechanism",
    },
    "head_of_state_death": {
        "probability": 0.02, "duration_years": 1, "intensity": (0.20, 0.40),
        "affected_vectors": ["usa", "china"],
        "social_media_amp": 2.0, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "Zia-ul-Haq, C-130 crash, 17 Aug 1988 — the instrument's designer dies ~3 years in and it survives 11 more",
    },
    "imf_program": {
        "probability": 0.12, "duration_years": 2, "intensity": (0.20, 0.40),
        "affected_vectors": ["imf"],
        "social_media_amp": 1.1, "trust_impact": -0.01, "corruption_impact": 0.00,
        "description": "Recurrent IMF conditionality (1988/1993/1995/1997/1998) — higher probability than Myanmar's single sanctions mechanism, by design",
    },
    "remittance_shock": {
        "probability": 0.04, "duration_years": 1, "intensity": (0.20, 0.40),
        "affected_vectors": ["saudi_gulf"],
        "social_media_amp": 1.3, "trust_impact": -0.02, "corruption_impact": 0.00,
        "description": "1990-91 Gulf War — mass expulsion/return of Pakistani workers from Kuwait/Iraq",
    },
    "ethnic_urban_violence": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["global_economy"],
        "social_media_amp": 1.7, "trust_impact": -0.03, "corruption_impact": 0.02,
        "description": "Karachi Sindhi/Muhajir violence (1985 Bushra Zaidi riots onward) — the real case for the 6-ethnic-group encoding; localisation to a `sindh` unit is out of this file's scope",
    },
    "nuclear_test": {
        "probability": 0.02, "duration_years": 2, "intensity": (0.20, 0.40),
        "affected_vectors": ["usa", "india"],
        "social_media_amp": 1.5, "trust_impact": 0.04, "corruption_impact": 0.00,
        "description": "Chagai-I, 28 May 1998 — domestic legitimacy gain, external sanction cost",
    },
    "oil_price_shock": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["global_economy", "saudi_gulf"],
        "social_media_amp": 1.2, "trust_impact": -0.03, "corruption_impact": 0.02,
        "description": "1990 Gulf War spike — Pakistan is a net energy importer",
    },
}

PAKISTAN_SIGNAL_MAP = {
    "great_power_influence": "china",
    "external_pressure":     ["usa"],
    "fdi":                    "foreign_investors",
    "illicit":                ["illicit_network_1", "illicit_network_2", "illicit_network_3"],
    "regional":                ["saarc"],   # Real but weak/inert, kept at its honest low value rather than zeroed
    "multilateral":             None,   # No UN-humanitarian-pressure analogue distinct from the IMF channel already carried separately
}


# ══════════════════════════════════════════════════════════════════════════════
# CHILE 1980 (1990-2005 elected-Congress era) — year zero 1990
# Source: config/constitution_chile_encoding/README.md section 6.4/6.5.
# Chain type: civilian (per scenario_registry.py's decision 4). ETHNIC_GROUPS: 0.
# ══════════════════════════════════════════════════════════════════════════════

CHILE_VECTORS = {
    # The single most important external variable, and it is a commodity,
    # not a state: Law 13,196 (Ley Reservada del Cobre) sends 10% of
    # Codelco's gross copper sales straight to the armed forces outside
    # congressional control — the only case in the 7-country set where an
    # external PRICE is legally wired into the guardianship institution's
    # budget.
    "copper_price":        0.55,
    "argentina":            0.30,   # Near-war (Beagle Channel, 1978) at the preceding period's end; inverts into Chile's deepest bilateral tie by year zero's aftermath
    "peru_bolivia":         0.15,   # War-of-the-Pacific-legacy: low-trade, high-grievance, non-military-threat (a relationship TYPE Myanmar's set has no slot for)
    "usa":                  0.55,   # Arms-embargo sanctioner (1976-90) -> largest export market (16.76%, 1990) at the democratic-transition dividend
    "european_judicial":    0.05,   # Low baseline; the real content (Pinochet's 1998 London arrest) is carried by a dedicated shock, not drift
    "japan_asia_pacific":    0.35,   # Second-largest export market (16.24%, 1990)
    "global_trade_regime":   0.30,   # Unilateral opening + bilateral FTAs, deliberately NOT bloc membership — the weak "ASEAN-equivalent"
    "foreign_investors":     0.45,   # High and rising — the Latin American FDI success case of the 1990s
    "global_economy":        0.55,
    "china":                 0.10,   # Minor at year zero; becomes largest trade partner post-2006 FTA
    "illicit_transit":       0.10,   # Cocaine-transit country (Peru/Bolivia border) — real but low-salience, deliberately NOT a 3-vector structure
}

CHILE_DRIFT = {
    "copper_price":        0.000,   # Volatility carried by copper_price_shock, not drift
    "argentina":            0.006,
    "peru_bolivia":         0.000,
    "usa":                  0.003,
    "european_judicial":    0.000,
    "japan_asia_pacific":    0.003,
    "global_trade_regime":   0.004,
    "foreign_investors":     0.004,
    "global_economy":        0.000,
    "china":                 0.011,   # Reaches ~largest-trade-partner magnitude by ~sim year 20, approximating the real post-2006 inversion
    "illicit_transit":       0.000,
}

CHILE_SHOCKS = {
    "copper_price_shock": {
        "probability": 0.10, "duration_years": 2, "intensity": (0.25, 0.50),
        "affected_vectors": ["copper_price", "global_economy"],
        "social_media_amp": 1.4, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "LME copper price trough (1998-99 / 2008-09 / 2015-16) — dual-channel for Chile uniquely: hits the export economy AND, via Law 13,196's 10% rule, the armed forces' own budget. That military-budget linkage is NOT separately modelled in this file; flagged as a cross-file follow-up (model_phase3.py's military/budget mechanics), not silently dropped",
    },
    "earthquake_tsunami": {
        "probability": 0.08, "duration_years": 1, "intensity": (0.25, 0.55),
        "affected_vectors": ["global_economy", "foreign_investors"],
        "social_media_amp": 2.3, "trust_impact": -0.03, "corruption_impact": 0.04,
        "description": "Most seismically active country in the set — real base: 2010 Maule M8.8, ~525 deaths, ~18% of GDP in damage",
    },
    "foreign_judicial_action": {
        "probability": 0.02, "duration_years": 2, "intensity": (0.20, 0.40),
        "affected_vectors": ["european_judicial", "usa"],
        "social_media_amp": 1.6, "trust_impact": -0.02, "corruption_impact": 0.00,
        "description": "Pinochet's London arrest (16 Oct 1998) / House of Lords immunity ruling (24 Mar 1999) — no analogue elsewhere, tests the regime's amnesty/immunity architecture from OUTSIDE",
    },
    "gas_supply_cutoff": {
        "probability": 0.05, "duration_years": 2, "intensity": (0.15, 0.35),
        "affected_vectors": ["argentina", "global_economy"],
        "social_media_amp": 1.1, "trust_impact": -0.02, "corruption_impact": 0.00,
        "description": "Argentine natural-gas export restrictions, 2004-08 — energy-security shock from a PARTNER, not an adversary",
    },
    "financial_contagion": {
        "probability": 0.06, "duration_years": 2, "intensity": (0.20, 0.40),
        "affected_vectors": ["foreign_investors", "global_economy", "usa"],
        "social_media_amp": 1.4, "trust_impact": -0.03, "corruption_impact": 0.01,
        "description": "1998-99 Asian financial crisis — Chile's only recession of the period",
    },
    "mass_protest_constitutional_crisis": {
        "probability": 0.03, "duration_years": 3, "intensity": (0.30, 0.55),
        "affected_vectors": ["global_trade_regime"],
        "social_media_amp": 2.0, "trust_impact": -0.04, "corruption_impact": 0.00,
        # Deliberately modest magnitude: the 18 Oct 2019 estallido social is
        # the real within-window stress test of this constitution, and it
        # SURVIVED (two replacement drafts rejected by referendum, zero
        # coups). A harsher magnitude here would risk mechanically
        # overriding that locked real-world finding (.claude/memory.md
        # section 4a) regardless of what the constitutional parameters say.
        "description": "Estallido social (18 Oct 2019) -> Agreement for Peace and a New Constitution -> two rejected replacement drafts (2022, 2023) — the constitution SURVIVES this",
    },
    "indigenous_conflict_escalation": {
        "probability": 0.06, "duration_years": 2, "intensity": (0.10, 0.30),
        "affected_vectors": ["global_economy"],
        "social_media_amp": 1.2, "trust_impact": -0.02, "corruption_impact": 0.01,
        "description": "Araucania/Biobio/Los Lagos Mapuche-conflict escalation",
    },
    "pandemic": {
        "probability": 0.02, "duration_years": 3, "intensity": (0.30, 0.55),
        "affected_vectors": ["global_economy", "usa", "foreign_investors"],
        "social_media_amp": 2.0, "trust_impact": -0.05, "corruption_impact": 0.03,
        "description": "COVID-19",
    },
    "drought_water_rights": {
        "probability": 0.06, "duration_years": 3, "intensity": (0.10, 0.30),
        "affected_vectors": ["global_economy"],
        "social_media_amp": 1.0, "trust_impact": -0.01, "corruption_impact": 0.00,
        "description": "Central-Chile megadrought from 2010 meeting the 1981 Water Code's constitutionally-protected tradeable private water rights",
    },
    "fdi_boom": {
        "probability": 0.05, "duration_years": 3, "intensity": (0.20, 0.45),
        "affected_vectors": ["foreign_investors", "japan_asia_pacific", "global_trade_regime"],
        "social_media_amp": 1.1, "trust_impact": 0.03, "corruption_impact": -0.01,
        "description": "1990s mining FDI surge / 2010 OECD accession", "positive": True,
    },
}

CHILE_SIGNAL_MAP = {
    "great_power_influence": "china",
    "external_pressure":     ["usa"],
    "fdi":                    "foreign_investors",
    "illicit":                ["illicit_transit"],
    "regional":                ["global_trade_regime"],   # Weak-bloc-engagement magnitude, the deliberate "ASEAN-equivalent" per README
    "multilateral":             None,   # No UN-humanitarian-pressure analogue salient in the research package
}


# ══════════════════════════════════════════════════════════════════════════════
# GERMANY (West Germany Basic Law, as amended through 1968) — year zero 1949
# Source: config/constitution_germany_encoding/README.md section 6.4/6.5.
# Chain type: civilian. ETHNIC_GROUPS: 0.
# Structurally the inverse case of the other six: the dominant external
# actor is a constitutional GUARANTOR, not a pressure source.
# ══════════════════════════════════════════════════════════════════════════════

GERMANY_VECTORS = {
    # THE defining relationship, no analogue anywhere else in the project:
    # the Occupation Statute (in force 21 Sept 1949) gives the three
    # Western powers jointly-held reserved powers AND the right to resume
    # full governmental authority — a supervisory vector, not a pressure
    # vector. See also the guarantor_intervention shock below.
    "allied_high_commission":       0.70,
    "ussr_gdr":                     0.65,   # Existential threat + legitimacy rival — Berlin Blockade ends 11 days before year zero
    "france":                       0.60,   # Occupier/Saar claimant AT year zero -> core EEC integration partner; the vector's MAGNITUDE stays comparable, only its qualitative character inverts (a methodology-section point, not something a scalar can carry — flagged, not hidden)
    "usa":                          0.65,   # Occupier + security guarantor + Marshall Plan patron simultaneously
    "nato":                         0.00,   # FRG not yet a member at year zero; accedes 9 May 1955 (~sim year 6)
    "european_economic_institutions": 0.20,   # ECSC (1951) founding era; FRG CO-FOUNDS this, doesn't receive pressure from it
    "israel_reparations":            0.05,   # Luxembourg Agreement 1952/53 — small magnitude, large legitimacy weight; no analogue elsewhere
    "global_economy":                0.60,   # Export-led Wirtschaftswunder
    # NOT named "foreign_investors": the real mechanism is debt relief
    # (London Debt Agreement 1953) and Marshall Plan reconstruction aid,
    # structurally the INVERSE of Myanmar's conditional-lending vector —
    # reusing the "foreign_investors" label would misrepresent a creditor-
    # relief relationship as ordinary conditional FDI.
    "reconstruction_finance":        0.25,
}

GERMANY_DRIFT = {
    "allied_high_commission":        -0.090,  # Fast decline to the clip(0) floor by ~sim year 8, approximating the Occupation Statute's 1955 end (the smaller 1955-1990 residual tail is lost to this simplification — flagged)
    "ussr_gdr":                      -0.004,
    "france":                         0.003,
    "usa":                            -0.003,
    "nato":                            0.015,
    "european_economic_institutions":  0.012,
    "israel_reparations":              0.000,
    "global_economy":                  0.002,
    "reconstruction_finance":          0.015,
}

GERMANY_SHOCKS = {
    "guarantor_intervention": {
        # The one shock in the entire 7-country set engineered to be
        # STABILISING when it fires, not destabilising: an external
        # guarantor acting in DEFENCE of the constitutional order — the
        # structural inverse of a coup. Low probability by design: the
        # whole point of a credible reserved power is that it rarely has
        # to actually be exercised.
        "probability": 0.01, "duration_years": 1, "intensity": (0.05, 0.15),
        "affected_vectors": ["allied_high_commission"],
        "social_media_amp": 1.0, "trust_impact": 0.02, "corruption_impact": 0.00,
        "positive": True,
        "description": "Allied reserved-power intervention in defence of the Basic Law — Occupation Statute, 21 Sept 1949 to 5 May 1955, residual Berlin/unification rights to 1990",
    },
    "berlin_crisis": {
        "probability": 0.03, "duration_years": 2, "intensity": (0.25, 0.50),
        "affected_vectors": ["ussr_gdr", "usa"],
        "social_media_amp": 1.8, "trust_impact": -0.04, "corruption_impact": 0.00,
        "description": "Blockade 1948-49 / 1958 ultimatum / Wall, 13 Aug 1961 — localised to a west_berlin unit, nationally amplified",
    },
    "superpower_nuclear_crisis": {
        "probability": 0.02, "duration_years": 1, "intensity": (0.20, 0.40),
        "affected_vectors": ["ussr_gdr", "usa"],
        "social_media_amp": 1.6, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "1961 Berlin standoff / 1962 Cuban Missile Crisis — existential-risk shock with no domestic mechanism",
    },
    "debt_relief": {
        "probability": 0.03, "duration_years": 3, "intensity": (0.20, 0.45),
        "affected_vectors": ["reconstruction_finance", "european_economic_institutions"],
        "social_media_amp": 1.1, "trust_impact": 0.04, "corruption_impact": -0.01,
        "positive": True,
        "description": "Currency reform 1948 / London Debt Agreement 27 Feb 1953 / Marshall Plan — Myanmar's SHOCK_EVENTS has no debt-relief type at all",
    },
    "labour_supply_inflow": {
        "probability": 0.05, "duration_years": 4, "intensity": (0.15, 0.35),
        "affected_vectors": ["global_economy", "reconstruction_finance"],
        "social_media_amp": 1.0, "trust_impact": 0.02, "corruption_impact": -0.01,
        "positive": True,
        "description": "1955 Gastarbeiter recruitment agreements — Germany is the one scenario with net LABOUR INFLOW",
    },
    "recession": {
        "probability": 0.05, "duration_years": 2, "intensity": (0.20, 0.40),
        "affected_vectors": ["global_economy", "reconstruction_finance"],
        "social_media_amp": 1.3, "trust_impact": -0.03, "corruption_impact": 0.01,
        "description": "1966-67 recession — real, dated chain to the 1968 Notstandsverfassung emergency-powers amendment at ~sim year 19",
    },
    "oil_price_shock": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.15, 0.40),
        "affected_vectors": ["global_economy"],
        "social_media_amp": 1.2, "trust_impact": -0.03, "corruption_impact": 0.02,
        "description": "1973 / 1979 OPEC shocks",
    },
    "domestic_terrorism": {
        "probability": 0.03, "duration_years": 2, "intensity": (0.15, 0.35),
        "affected_vectors": ["usa", "ussr_gdr"],
        "social_media_amp": 1.5, "trust_impact": -0.03, "corruption_impact": 0.00,
        "description": "RAF / Munich 1972 / German Autumn 1977 — the real stress test of the 1968 emergency architecture",
    },
    "global_recession": {
        "probability": 0.08, "duration_years": 2, "intensity": (0.20, 0.45),
        "affected_vectors": ["usa", "global_economy", "european_economic_institutions"],
        "social_media_amp": 1.5, "trust_impact": -0.04, "corruption_impact": 0.01,
        "description": "Global recession — transfers from Myanmar's set",
    },
    "pandemic": {
        "probability": 0.02, "duration_years": 3, "intensity": (0.30, 0.60),
        "affected_vectors": ["global_economy", "usa"],
        "social_media_amp": 2.0, "trust_impact": -0.05, "corruption_impact": 0.03,
        "description": "Pandemic — transfers from Myanmar's set",
    },
    # Deliberately EXCLUDED: "reunification" (3 Oct 1990, ~sim year 41).
    # The README itself flags this as a ~16m-population/5-Land territorial
    # discontinuity the engine "almost certainly cannot represent" and asks
    # that this be stated rather than quietly ignored. This is that
    # statement: it is not encoded as a shock here (a one-time population/
    # territory jump is not a geopolitical-pressure event, and forcing it
    # into this schema would misrepresent it), and it is not silently
    # dropped — flagged in the final report for whoever owns demographic/
    # population mechanics next.
}

GERMANY_SIGNAL_MAP = {
    "great_power_influence": None,   # Deliberately zero — no real China relationship in this era (README 6.4, "deliberately absent")
    "external_pressure":     [],      # Deliberately zero — the Allied powers are a GUARANTOR, not a pressure source; see allied_high_commission instead
    "fdi":                    "reconstruction_finance",
    "illicit":                [],      # Deliberately zero — "the cleanest zero in the whole set" (README 6.4)
    "regional":                [],      # The EEC/ECSC is co-founded, not an external shield/constraint of the ASEAN type — not folded into this generic signal
    "multilateral":             None,   # Not covered in the research package; left unset rather than guessed
}


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRY — one row per scenario code, matching config/scenario_registry.py
# A and C deliberately point at the SAME dict objects as the Myanmar
# constants above (not copies) — zero transcription-drift risk.
# ══════════════════════════════════════════════════════════════════════════════

EXTERNAL_LAYER_REGISTRY: Dict[str, Dict] = {
    "A": {
        "label": "Myanmar (MFU)", "vectors": INITIAL_VECTORS, "drift": VECTOR_DRIFT,
        "shocks": SHOCK_EVENTS, "signal_map": MYANMAR_SIGNAL_MAP,
    },
    "C": {
        "label": "Myanmar (2008 military)", "vectors": INITIAL_VECTORS, "drift": VECTOR_DRIFT,
        "shocks": SHOCK_EVENTS, "signal_map": MYANMAR_SIGNAL_MAP,
    },
    "SK": {
        "label": "South Korea 1987", "vectors": SOUTHKOREA_VECTORS, "drift": SOUTHKOREA_DRIFT,
        "shocks": SOUTHKOREA_SHOCKS, "signal_map": SOUTHKOREA_SIGNAL_MAP,
    },
    "TH": {
        "label": "Thailand 2017", "vectors": THAILAND_VECTORS, "drift": THAILAND_DRIFT,
        "shocks": THAILAND_SHOCKS, "signal_map": THAILAND_SIGNAL_MAP,
    },
    "PK": {
        "label": "Pakistan 1973+8th Amdt", "vectors": PAKISTAN_VECTORS, "drift": PAKISTAN_DRIFT,
        "shocks": PAKISTAN_SHOCKS, "signal_map": PAKISTAN_SIGNAL_MAP,
    },
    "CL": {
        "label": "Chile 1990-2005", "vectors": CHILE_VECTORS, "drift": CHILE_DRIFT,
        "shocks": CHILE_SHOCKS, "signal_map": CHILE_SIGNAL_MAP,
    },
    "DE": {
        "label": "Germany as amended through 1968", "vectors": GERMANY_VECTORS, "drift": GERMANY_DRIFT,
        "shocks": GERMANY_SHOCKS, "signal_map": GERMANY_SIGNAL_MAP,
    },
}


@dataclass
class ActiveShock:
    """A shock event currently in progress."""
    name: str
    year_started: int
    duration: int
    intensity: float
    affected_vectors: List[str]
    social_media_amp: float
    trust_impact: float
    corruption_impact: float
    positive: bool = False

    @property
    def is_positive(self) -> bool:
        return self.positive


class ExternalLayer:
    """
    Phase 3 External World Layer.

    Each scenario gets its own real, sourced set of country/institution
    signal vectors, drift rates and shock types (EXTERNAL_LAYER_REGISTRY
    above), but the mechanism — drift, stochastic shock firing, cascade,
    derived signals — is the single shared code path for every scenario.
    This is deliberate: bias lives in the DATA (per-scenario, sourced from
    each constitution's own research package), never in a scenario literal
    inside this class's logic. A and C keep Myanmar's original 17-vector/
    10-shock data unchanged.

    Usage in model.py:
        self.external_layer = ExternalLayer(scenario=self.scenario, seed=seed)
        # Each step:
        self.external_layer.step(year=self.current_year,
                                  shared_data=self.shared_data)
    """

    def __init__(self, scenario: str = "A", seed: int = 42):
        self.scenario = scenario
        self.seed = seed
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        if scenario not in EXTERNAL_LAYER_REGISTRY:
            # Loud, not a silent fallback to Myanmar's vectors — same
            # philosophy as config/scenario_registry.py's get_scenario().
            raise KeyError(
                f"ExternalLayer has no geopolitical vector set registered "
                f"for scenario {scenario!r}. Known codes: "
                f"{sorted(EXTERNAL_LAYER_REGISTRY)}. Add an entry to "
                f"EXTERNAL_LAYER_REGISTRY in engine/external_layer.py "
                f"(vectors/drift/shocks/signal_map) before running this "
                f"scenario."
            )

        entry = EXTERNAL_LAYER_REGISTRY[scenario]
        self.label = entry["label"]
        self._vector_drift = entry["drift"]
        self._shock_events = entry["shocks"]
        self._signal_map = entry["signal_map"]

        # Initialise vectors (mutable per-instance copy)
        self.vectors: Dict[str, float] = dict(entry["vectors"])

        # Active shocks
        self.active_shocks: List[ActiveShock] = []

        # History for analysis
        self.shock_history: List[Dict] = []
        self.vector_history: List[Dict] = []

    # ── Derived-signal helper ───────────────────────────────────────────────
    def _signal_value(self, signal_key: str) -> float:
        """
        Resolve one of the six generic derived-signal keys
        (great_power_influence / external_pressure / fdi / illicit /
        regional / multilateral) against this scenario's own signal_map.
        A string maps to that one vector's value; a list maps to the mean
        of those vectors' values; None/missing/empty resolves to 0.0 —
        a real "this channel does not apply to this country" result, not
        a missing-data artefact.
        """
        target = self._signal_map.get(signal_key)
        if not target:
            return 0.0
        if isinstance(target, (list, tuple)):
            values = [self.vectors[name] for name in target if name in self.vectors]
            return float(np.mean(values)) if values else 0.0
        return float(self.vectors.get(target, 0.0))

    def step(self, year: int, shared_data: Dict) -> Dict:
        """
        Annual external layer update.
        1. Apply drift to all vectors
        2. Fire new stochastic shocks
        3. Apply active shock effects
        4. Expire finished shocks
        5. Write signals to shared_data
        6. Return external signal summary
        """

        # ── 1. Annual drift ───────────────────────────────────────────────────
        for vector, drift in self._vector_drift.items():
            self.vectors[vector] = float(np.clip(
                self.vectors[vector] + drift, 0.0, 1.0
            ))

        # ── 2. Fire new shocks ────────────────────────────────────────────────
        newly_fired = []
        for shock_name, shock_def in self._shock_events.items():
            # Don't fire same shock twice simultaneously
            already_active = any(s.name == shock_name for s in self.active_shocks)
            if already_active:
                continue

            if self.rng.random() < shock_def["probability"]:
                intensity = self.rng.uniform(*shock_def["intensity"])
                duration = shock_def["duration_years"]

                shock = ActiveShock(
                    name=shock_name,
                    year_started=year,
                    duration=duration,
                    intensity=intensity,
                    affected_vectors=shock_def["affected_vectors"],
                    social_media_amp=shock_def.get("social_media_amp", 1.0),
                    trust_impact=shock_def.get("trust_impact", 0.0),
                    corruption_impact=shock_def.get("corruption_impact", 0.0),
                    positive=shock_def.get("positive", False),
                )
                self.active_shocks.append(shock)
                newly_fired.append(shock_name)

                self.shock_history.append({
                    "year": year,
                    "shock": shock_name,
                    "intensity": intensity,
                    "duration": duration,
                    "description": shock_def["description"]
                })

        # ── 3. Apply active shock effects ─────────────────────────────────────
        total_social_media_signal = 0.0
        total_trust_impact = 0.0
        total_corruption_impact = 0.0

        for shock in self.active_shocks:
            direction = 1.0 if shock.is_positive else -1.0
            for vector in shock.affected_vectors:
                if vector in self.vectors:
                    delta = direction * shock.intensity * 0.10
                    self.vectors[vector] = float(np.clip(
                        self.vectors[vector] + delta, 0.0, 1.0
                    ))

            # Accumulate cascade signals
            total_social_media_signal += shock.intensity * shock.social_media_amp
            total_trust_impact += shock.trust_impact
            total_corruption_impact += shock.corruption_impact

        # ── 4. Expire finished shocks ─────────────────────────────────────────
        self.active_shocks = [
            s for s in self.active_shocks
            if (year - s.year_started) < s.duration
        ]

        # ── 5. Write to shared_data ───────────────────────────────────────────
        # Key NAMES kept generic/literal for backward-compatible CSV columns
        # and Prometheus gauges (china_influence/western_pressure/fdi_level);
        # what each one MEANS is resolved per-scenario via _signal_value().
        external_signal = {
            "vectors":                  dict(self.vectors),
            "active_shocks":            [s.name for s in self.active_shocks],
            "newly_fired_shocks":       newly_fired,
            "social_media_signal":      min(total_social_media_signal, 5.0),
            "trust_impact":             float(np.clip(total_trust_impact, -0.20, 0.20)),
            "corruption_impact":        float(np.clip(total_corruption_impact, -0.10, 0.20)),
            "china_influence":          self._signal_value("great_power_influence"),
            "western_pressure":         self._signal_value("external_pressure"),
            "fdi_level":                self._signal_value("fdi"),
            "illicit_pressure":         self._signal_value("illicit"),
            "regional_stability":       self._signal_value("regional"),
            "un_pressure":              self._signal_value("multilateral"),
            "year":                     year,
        }

        shared_data["external"] = external_signal

        # Store vector snapshot for analysis
        self.vector_history.append({
            "year": year,
            **dict(self.vectors)
        })

        return external_signal

    def get_china_veto_probability(self) -> float:
        """
        China UN veto probability on sanctions against the active scenario.
        China vetoes when its influence is high AND instability < 0.60.
        Historically accurate for Myanmar (China blocks sanctions to
        protect BRI investment); resolves to 0.0 for scenarios with no
        real "china" vector (e.g. Germany) rather than KeyError-ing.
        """
        return min(0.95, self.vectors.get("china", 0.0) * 0.90)

    def get_shock_summary(self) -> List[Dict]:
        """Return full shock history for JSONL logging."""
        return self.shock_history

    def get_vector_trajectory(self) -> List[Dict]:
        """Return vector history for visualisation."""
        return self.vector_history


if __name__ == "__main__":
    print("engine/external_layer.py self-test — all 7 registered scenarios\n")

    for code, entry in EXTERNAL_LAYER_REGISTRY.items():
        print(f"=== {code}: {entry['label']} ===")
        print(f"  Vectors:     {len(entry['vectors'])}")
        print(f"  Shock types: {len(entry['shocks'])}")

        ext = ExternalLayer(scenario=code, seed=42)
        shared = {}
        shocks_fired = []
        for year in range(1, 11):
            signal = ext.step(year=year, shared_data=shared)
            if signal["newly_fired_shocks"]:
                shocks_fired.extend(signal["newly_fired_shocks"])

        print(f"  After 10 years:")
        print(f"    china_influence (great_power_influence): {shared['external']['china_influence']:.3f}")
        print(f"    western_pressure:                        {shared['external']['western_pressure']:.3f}")
        print(f"    fdi_level:                                {shared['external']['fdi_level']:.3f}")
        print(f"    illicit_pressure:                         {shared['external']['illicit_pressure']:.3f}")
        print(f"    regional_stability:                       {shared['external']['regional_stability']:.3f}")
        print(f"    un_pressure:                               {shared['external']['un_pressure']:.3f}")
        print(f"    Shocks fired in 10yr test: {len(shocks_fired)}")
        print(f"    China veto prob: {ext.get_china_veto_probability():.3f}")
        print()
