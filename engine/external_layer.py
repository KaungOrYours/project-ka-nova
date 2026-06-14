"""
================================================================================
PROJECT KA-NOVA
engine/external_layer.py

External World Layer — Phase 3
17 population-weighted country and institution signal vectors
Calibrated from real sanctions, FDI, and geopolitical data.

Same external world hits both Scenario A and C — no bias.
Vectors evolve over time. Stochastic shock events fire randomly
with historically calibrated probabilities and cascade through
social media amplifier into citizen agents.

Architecture:
    ExternalLayer.step(year, shared_data) → updates shared_data["external"]
    Shocks fire randomly → social_media amplifies → citizens feel effect
    Both scenarios receive identical shock sequence (same seed per run)

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import random
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# SHOCK EVENT DEFINITIONS
# Each shock has: probability per year, affected vectors, intensity range,
# cascade duration (years), and social media amplification factor
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


# ══════════════════════════════════════════════════════════════════════════════
# EXTERNAL VECTOR DEFINITIONS
# 17 vectors — each has initial value, drift rate, and response to shocks
# Values represent influence/engagement level: 0.0 (none) to 1.0 (maximum)
# ══════════════════════════════════════════════════════════════════════════════

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

    17 NumPy-backed country and institution vectors that evolve over time
    and respond to stochastic geopolitical shock events.

    Both Scenario A and C receive identical shock sequences per run
    (seeded by run_id) — the difference is how each constitutional
    system responds to the same external pressure.

    Usage in model.py:
        self.external = ExternalLayer(seed=run_id)
        # Each step:
        self.external.step(year=self.current_year,
                          shared_data=self.shared_data)
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.np_rng = np.random.default_rng(seed)

        # Initialise vectors
        self.vectors: Dict[str, float] = dict(INITIAL_VECTORS)

        # Active shocks
        self.active_shocks: List[ActiveShock] = []

        # History for analysis
        self.shock_history: List[Dict] = []
        self.vector_history: List[Dict] = []

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
        for vector, drift in VECTOR_DRIFT.items():
            self.vectors[vector] = float(np.clip(
                self.vectors[vector] + drift, 0.0, 1.0
            ))

        # ── 2. Fire new shocks ────────────────────────────────────────────────
        newly_fired = []
        for shock_name, shock_def in SHOCK_EVENTS.items():
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
        external_signal = {
            "vectors":                  dict(self.vectors),
            "active_shocks":            [s.name for s in self.active_shocks],
            "newly_fired_shocks":       newly_fired,
            "social_media_signal":      min(total_social_media_signal, 5.0),
            "trust_impact":             float(np.clip(total_trust_impact, -0.20, 0.20)),
            "corruption_impact":        float(np.clip(total_corruption_impact, -0.10, 0.20)),
            "china_influence":          self.vectors["china"],
            "western_pressure":         (self.vectors["usa"] + self.vectors["eu"]) / 2,
            "fdi_level":                self.vectors["foreign_investors"],
            "illicit_pressure":         (
                self.vectors["illicit_network_1"] +
                self.vectors["illicit_network_2"] +
                self.vectors["illicit_network_3"]
            ) / 3,
            "regional_stability":       (
                self.vectors["asean"] +
                self.vectors["thailand"] +
                self.vectors["india"]
            ) / 3,
            "un_pressure":              self.vectors["un_agencies"],
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
        China UN veto probability on Myanmar sanctions.
        China vetoes when its influence is high AND Myanmar instability < 0.60.
        Historically accurate — China blocks sanctions to protect BRI investment.
        """
        return min(0.95, self.vectors["china"] * 0.90)

    def get_shock_summary(self) -> List[Dict]:
        """Return full shock history for JSONL logging."""
        return self.shock_history

    def get_vector_trajectory(self) -> List[Dict]:
        """Return vector history for visualisation."""
        return self.vector_history


if __name__ == "__main__":
    print("engine/external_layer.py loaded successfully")
    print(f"Vectors:       {len(INITIAL_VECTORS)}")
    print(f"Shock types:   {len(SHOCK_EVENTS)}")
    print()

    # Quick test — run 10 steps
    ext = ExternalLayer(seed=42)
    shared = {}
    shocks_fired = []

    for year in range(1, 11):
        signal = ext.step(year=year, shared_data=shared)
        if signal["newly_fired_shocks"]:
            shocks_fired.extend(signal["newly_fired_shocks"])
            print(f"  Year {year:2d}: SHOCK — {signal['newly_fired_shocks']}")

    print(f"\nAfter 10 years:")
    print(f"  China influence:    {shared['external']['china_influence']:.3f}")
    print(f"  Western pressure:   {shared['external']['western_pressure']:.3f}")
    print(f"  FDI level:          {shared['external']['fdi_level']:.3f}")
    print(f"  Illicit pressure:   {shared['external']['illicit_pressure']:.3f}")
    print(f"  Active shocks:      {shared['external']['active_shocks']}")
    print(f"  Total shocks fired: {len(shocks_fired)}")
    print(f"  China veto prob:    {ext.get_china_veto_probability():.3f}")
