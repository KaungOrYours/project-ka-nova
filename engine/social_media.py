"""
================================================================================
PROJECT KA-NOVA
engine/social_media.py

Social Media Amplification Channel — Phase 3

Models information flow from external shocks through social media
to citizen agents. Regime openness is decided by LLM elite agents,
not hardcoded. VPN floor rises with suppression attempts — suppression
is self-defeating over time (historically accurate, Myanmar post-2021).

Key mechanics:
- Openness: 0.0 (full shutdown) to 1.0 (fully open)
- LLM Commander-in-Chief/Chancellor decides openness each year
- Internet shutdown triggers when protest_rate > 0.15 in Scenario C
- VPN floor starts at 0.35, rises by 0.01 per shutdown attempt
- Maximum VPN floor: 0.70 (citizens always find a way)
- Ethnic word-of-mouth networks bypass suppression (+0.10 per group)
- Information speed: fast in A (open), slow but persistent in C (suppressed)

Architecture:
    SocialMediaChannel.step(year, shared_data, scenario) → citizen signals
    LLM elite writes shared_data["elite_internet_decision"] each step
    Channel reads decision, applies VPN floor, computes citizen exposure

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

VPN_FLOOR_INITIAL       = 0.35   # Post-2021 Myanmar VPN adoption baseline
VPN_FLOOR_MAX           = 0.70   # Ceiling — even under max suppression
VPN_FLOOR_RISE_PER_SHUTDOWN = 0.01  # Each shutdown attempt = more VPN adoption
ETHNIC_NETWORK_BONUS    = 0.10   # Word-of-mouth adds 0.10 per active ethnic group
SHUTDOWN_TRIGGER        = 0.15   # Protest rate threshold for Scenario C shutdown
OPENNESS_SCENARIO_A     = 1.00   # Scenario A default — LLM can adjust
OPENNESS_SCENARIO_C_DEFAULT = 0.10  # Scenario C default before VPN floor applied


@dataclass
class SocialMediaState:
    """Annual state of the social media channel."""
    year: int
    raw_openness: float          # LLM decision (0.0 to 1.0)
    vpn_floor: float             # Current VPN floor
    effective_openness: float    # max(raw_openness, vpn_floor)
    ethnic_network_active: bool  # Word-of-mouth active
    final_openness: float        # effective + ethnic bonus
    shutdown_attempted: bool     # Did regime attempt shutdown this year?
    information_speed: str       # "fast" / "moderate" / "slow" / "suppressed"
    citizen_exposure: float      # How much of external signal reaches citizens
    shock_amplification: float   # How much shocks are amplified


class SocialMediaChannel:
    """
    Phase 3 Social Media Amplification Channel.

    Bridges external world shocks and LLM elite decisions
    to citizen agent information exposure.

    In Scenario A: Chancellor/President keep openness high (1.0 default).
                   LLM may reduce during crisis but never below 0.60.
    In Scenario C: Commander-in-Chief suppresses to 0.10 default.
                   VPN floor prevents full shutdown.
                   More shutdowns → higher VPN floor → self-defeating.

    Ethnic word-of-mouth networks (Facebook, Viber, community radio)
    operate independently of internet — adds flat +0.10 bonus.
    """

    def __init__(self, scenario: str, seed: int = 42):
        self.scenario = scenario
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        # VPN floor — rises with each shutdown attempt
        self.vpn_floor = VPN_FLOOR_INITIAL
        self.shutdown_count = 0

        # History for analysis and FAIR evaluation
        self.history: List[SocialMediaState] = []
        self.total_information_suppressed = 0.0

    def step(self, year: int, shared_data: Dict) -> Dict:
        """
        Annual social media channel update.

        Reads:
            shared_data["elite_internet_decision"] — LLM openness decision
            shared_data["protest_rate"]            — triggers shutdown in C
            shared_data["external"]["social_media_signal"] — shock signal

        Writes:
            shared_data["social_media"] — full channel state
            shared_data["citizen_information_exposure"] — key citizen signal
        """

        # ── 1. Get LLM elite internet decision ───────────────────────────────
        elite_decision = shared_data.get("elite_internet_decision", None)

        if elite_decision is not None:
            raw_openness = float(np.clip(elite_decision, 0.0, 1.0))
        else:
            # Default by scenario if LLM hasn't decided yet
            raw_openness = (
                OPENNESS_SCENARIO_A if self.scenario == "A"
                else OPENNESS_SCENARIO_C_DEFAULT
            )

        # ── 2. Check shutdown trigger ─────────────────────────────────────────
        protest_rate = shared_data.get("protest_rate", 0.0)
        shutdown_attempted = False

        if self.scenario == "C" and protest_rate > SHUTDOWN_TRIGGER:
            # Commander-in-Chief triggers internet shutdown
            raw_openness = min(raw_openness, 0.05)  # Near-zero but not zero
            shutdown_attempted = True
            self.shutdown_count += 1

            # VPN floor rises — suppression teaches citizens to bypass it
            self.vpn_floor = min(
                VPN_FLOOR_MAX,
                self.vpn_floor + VPN_FLOOR_RISE_PER_SHUTDOWN
            )

            shared_data["internet_shutdown_active"] = True
            shared_data.setdefault("shutdown_history", []).append({
                "year": year,
                "protest_rate": protest_rate,
                "vpn_floor_after": self.vpn_floor
            })
        else:
            shared_data["internet_shutdown_active"] = False

        # ── 3. Apply VPN floor — suppression is self-defeating ────────────────
        effective_openness = max(raw_openness, self.vpn_floor)

        # ── 4. Ethnic word-of-mouth network bonus ─────────────────────────────
        # Each ethnic group has independent information network
        # (Facebook groups, Viber communities, community radio)
        # Active regardless of internet shutdown
        ethnic_groups_active = len(shared_data.get("active_ethnic_groups", [
            "Bamar", "Shan", "Karen", "Kachin", "Chin", "Mon", "Rakhine", "Kayah"
        ]))
        ethnic_bonus = min(
            ETHNIC_NETWORK_BONUS * (ethnic_groups_active / 8),
            ETHNIC_NETWORK_BONUS
        )
        ethnic_network_active = ethnic_groups_active > 0

        final_openness = min(1.0, effective_openness + ethnic_bonus)

        # ── 5. Information speed classification ───────────────────────────────
        if final_openness >= 0.80:
            information_speed = "fast"
        elif final_openness >= 0.55:
            information_speed = "moderate"
        elif final_openness >= 0.35:
            information_speed = "slow"
        else:
            information_speed = "suppressed"

        # ── 6. Compute citizen exposure ───────────────────────────────────────
        # How much of the external shock signal reaches citizens
        external_signal = shared_data.get("external", {}).get(
            "social_media_signal", 0.0
        )
        shock_amplification = final_openness * external_signal
        citizen_exposure = float(np.clip(
            final_openness * (1.0 + shock_amplification * 0.20), 0.0, 1.0
        ))

        # Track suppression for analysis
        suppressed = 1.0 - final_openness
        self.total_information_suppressed += suppressed

        # ── 7. Write to shared_data ───────────────────────────────────────────
        state = SocialMediaState(
            year=year,
            raw_openness=raw_openness,
            vpn_floor=self.vpn_floor,
            effective_openness=effective_openness,
            ethnic_network_active=ethnic_network_active,
            final_openness=final_openness,
            shutdown_attempted=shutdown_attempted,
            information_speed=information_speed,
            citizen_exposure=citizen_exposure,
            shock_amplification=shock_amplification,
        )
        self.history.append(state)

        social_media_signal = {
            "year":                     year,
            "raw_openness":             raw_openness,
            "vpn_floor":                self.vpn_floor,
            "effective_openness":       effective_openness,
            "ethnic_network_active":    ethnic_network_active,
            "final_openness":           final_openness,
            "shutdown_attempted":       shutdown_attempted,
            "shutdown_count":           self.shutdown_count,
            "information_speed":        information_speed,
            "citizen_exposure":         citizen_exposure,
            "shock_amplification":      shock_amplification,
            "total_suppressed":         self.total_information_suppressed,
        }

        shared_data["social_media"] = social_media_signal
        shared_data["citizen_information_exposure"] = citizen_exposure

        return social_media_signal

    def get_vpn_trajectory(self) -> List[Dict]:
        """Return VPN floor history — shows suppression backfire over time."""
        return [
            {
                "year": s.year,
                "vpn_floor": s.vpn_floor,
                "shutdown_attempted": s.shutdown_attempted,
                "final_openness": s.final_openness,
            }
            for s in self.history
        ]

    def get_suppression_summary(self) -> Dict:
        """Summary statistics for CVES and paper analysis."""
        if not self.history:
            return {}
        openness_values = [s.final_openness for s in self.history]
        return {
            "scenario":                 self.scenario,
            "total_shutdowns":          self.shutdown_count,
            "final_vpn_floor":          self.vpn_floor,
            "mean_openness":            float(np.mean(openness_values)),
            "min_openness":             float(np.min(openness_values)),
            "max_openness":             float(np.max(openness_values)),
            "total_suppressed":         self.total_information_suppressed,
            "suppression_backfired":    self.vpn_floor > VPN_FLOOR_INITIAL,
        }


if __name__ == "__main__":
    print("engine/social_media.py loaded successfully")
    print()

    import random

    for scenario in ["A", "C"]:
        print(f"Scenario {scenario} — 15 year simulation:")
        channel = SocialMediaChannel(scenario=scenario, seed=42)
        shared = {
            "external": {"social_media_signal": 1.5},
            "active_ethnic_groups": [
                "Bamar", "Shan", "Karen", "Kachin",
                "Chin", "Mon", "Rakhine", "Kayah"
            ]
        }

        for year in range(1, 16):
            # Simulate protest spike in years 3, 7, 11 for Scenario C
            shared["protest_rate"] = (
                0.20 if (scenario == "C" and year in [3, 7, 11]) else 0.05
            )
            # Simulate LLM decision
            shared["elite_internet_decision"] = (
                0.95 if scenario == "A" else 0.10
            )
            signal = channel.step(year=year, shared_data=shared)

            shutdown_marker = " [SHUTDOWN]" if signal["shutdown_attempted"] else ""
            print(
                f"  Year {year:2d}: openness={signal['final_openness']:.3f} "
                f"vpn_floor={signal['vpn_floor']:.3f} "
                f"speed={signal['information_speed']:<10}{shutdown_marker}"
            )

        summary = channel.get_suppression_summary()
        print(f"  Shutdowns: {summary['total_shutdowns']} | "
              f"Final VPN floor: {summary['final_vpn_floor']:.3f} | "
              f"Mean openness: {summary['mean_openness']:.3f}")
        print(f"  Suppression backfired: {summary['suppression_backfired']}")
        print()
