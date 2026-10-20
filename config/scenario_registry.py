"""
================================================================================
PROJECT KA-NOVA
config/scenario_registry.py

Scenario Registry — single source of truth for "which scenario code maps to
which constitution module, and which governance chain structure it uses."

Replaces the hardcoded A/C binary that used to live scattered across
model_phase3.py (constitution import switch + six `scenario == "A"/"C"`
branches), engine/elite_agents_v3.py (CHAIN_ORDER_A/_C,
AGENT_DISPLAY_NAMES_A/_C, SYSTEM_PROMPTS_A/_C), and run_phase3.py
(SCENARIO_DIRS, the scenario assert, argparse choices).

chain_type is the one axis that drives engine behaviour:
    "civilian" — civilian-supremacy chain of command (like MFU/A)
    "military" — military-guardianship chain of command (like 2008 Myanmar/C)
The constitution module supplies every PARAMETER; chain_type only selects
which of the two structural rule branches / elite-agent chain rosters apply.
This keeps the engine constitutionally agnostic — bias lives only in the
constitution layer's parameter values, never in a scenario-code literal
scattered through engine/institutions code (see .claude/memory.md locked
finding #7).

Fails gracefully per entry: a constitution module that does not exist yet
(SK/TH/PK/CL/DE, pending separate follow-up encoding work) does NOT prevent
this module from importing, and does NOT prevent scenarios that ARE fully
encoded (A, C) from running. Attempting to actually USE an unavailable
scenario raises a clear, loud ImportError via get_scenario() — deliberately
NOT a silent fallback (see model_phase3.py's old CONSTITUTION_2008_AVAILABLE
pattern, flagged in .claude/MINDMAP.md as "worth hardening," now superseded
by this module raising instead of silently substituting MFU).

Author: Kaung Htet (architecture) / Claude Code (registry implementation)
License: MIT
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScenarioEntry:
    """One registry row. `constitution` / `available` / `import_error` are
    populated at module-import time by _load_entry(); everything else comes
    straight from the _REGISTRY_SPEC literal below."""

    code: str
    constitution_path: str          # "module.path:ATTR_NAME"
    chain_type: str                 # "civilian" | "military"
    label: str                      # human-readable display label
    slug: str                       # stable machine-readable identifier,
                                     # written into results CSVs as the
                                     # "constitution" column (mirrors the
                                     # exact pre-existing strings for A/C —
                                     # "mfu_v7" / "2008_myanmar_military" —
                                     # so downstream analysis scripts that
                                     # may already filter on those literal
                                     # strings keep working unchanged)
    constitution: Optional[object] = field(default=None, repr=False)
    available: bool = False
    import_error: Optional[str] = None


# ── Registry spec ─────────────────────────────────────────────────────────────
# This literal dict is the ONLY place a new scenario code needs to be added.
# The 5 "pending" entries (SK/TH/PK/CL/DE) point at constitution modules that
# do not exist yet — that is expected and handled gracefully, see _load_entry.
_REGISTRY_SPEC = {
    "A": {
        "constitution": "config.constitution:CONSTITUTION",
        "chain_type":   "civilian",
        "label":        "MFU",
        "slug":         "mfu_v7",
    },
    "C": {
        "constitution": "config.constitution_2008:CONSTITUTION_2008",
        "chain_type":   "military",
        "label":        "2008 Myanmar",
        "slug":         "2008_myanmar_military",
    },
    "SK": {
        "constitution": "config.constitution_southkorea:CONSTITUTION_SOUTHKOREA",
        "chain_type":   "civilian",
        "label":        "South Korea 1987",
        "slug":         "south_korea_1987",
    },
    "TH": {
        "constitution": "config.constitution_thailand:CONSTITUTION_THAILAND",
        "chain_type":   "military",
        "label":        "Thailand 2017",
        "slug":         "thailand_2017",
    },
    "PK": {
        "constitution": "config.constitution_pakistan:CONSTITUTION_PAKISTAN",
        "chain_type":   "military",
        "label":        "Pakistan 1973+8th Amdt",
        "slug":         "pakistan_1973_8th_amendment",
    },
    "CL": {
        "constitution": "config.constitution_chile:CONSTITUTION_CHILE",
        # NOTE: "civilian", not "military" — Kaung confirmed 2026-10-20 the
        # 1990-2005 ELECTED-CONGRESS era is the period being encoded (an
        # elected legislature constrained by reserved-power enclaves), not
        # the 1981-1990 Junta era. See .claude/memory.md section 4a decision 4.
        "chain_type":   "civilian",
        "label":        "Chile 1990-2005",
        "slug":         "chile_1990_2005",
    },
    "DE": {
        "constitution": "config.constitution_germany:CONSTITUTION_GERMANY",
        "chain_type":   "civilian",
        # Encoded "as amended through 1968" per Kaung's decision 2026-10-20
        # (1956 armed-forces chapter + 1968 emergency-powers chapter
        # included; the Dec-2024 Art. 93 amendment excluded). Label reflects
        # that, not a bare "1949".
        "label":        "Germany as amended through 1968",
        "slug":         "germany_1968",
    },
}


def _load_entry(code: str, spec: dict) -> ScenarioEntry:
    module_path, attr_name = spec["constitution"].split(":")
    entry = ScenarioEntry(
        code=code,
        constitution_path=spec["constitution"],
        chain_type=spec["chain_type"],
        label=spec["label"],
        slug=spec["slug"],
    )
    try:
        module = importlib.import_module(module_path)
        entry.constitution = getattr(module, attr_name)
        entry.available = True
    except (ImportError, AttributeError) as exc:
        entry.available = False
        entry.import_error = f"{type(exc).__name__}: {exc}"
    return entry


# ── Built once at import time ─────────────────────────────────────────────────
SCENARIOS: dict[str, ScenarioEntry] = {
    code: _load_entry(code, spec) for code, spec in _REGISTRY_SPEC.items()
}

# Convenience: codes whose constitution module actually imported successfully.
AVAILABLE_SCENARIO_CODES = sorted(c for c, e in SCENARIOS.items() if e.available)

# Convenience: codes that are expected eventually but not encoded yet.
PENDING_SCENARIO_CODES = sorted(c for c, e in SCENARIOS.items() if not e.available)


def get_scenario(code: str) -> ScenarioEntry:
    """
    Resolve a scenario code to its registry entry.

    Raises KeyError for an unknown code (not in the registry spec at all),
    or ImportError for a known-but-not-yet-encoded code (SK/TH/PK/CL/DE
    before their constitution module exists) — deliberately loud, never a
    silent fallback to a different constitution.
    """
    if code not in SCENARIOS:
        raise KeyError(
            f"Unknown scenario code {code!r}. Known codes: {sorted(SCENARIOS)}"
        )
    entry = SCENARIOS[code]
    if not entry.available:
        raise ImportError(
            f"Scenario {code!r} ({entry.label}) is registered but its "
            f"constitution module is not available yet: {entry.import_error}. "
            f"Expected at {entry.constitution_path!r}. This scenario cannot "
            f"be run until that module is encoded."
        )
    return entry


if __name__ == "__main__":
    print("config/scenario_registry.py — self-test\n")
    for code, entry in SCENARIOS.items():
        status = "AVAILABLE" if entry.available else f"PENDING ({entry.import_error})"
        print(f"  {code:<3} {entry.label:<30} chain_type={entry.chain_type:<9} "
              f"slug={entry.slug:<28} {status}")
    print(f"\nAvailable now: {AVAILABLE_SCENARIO_CODES}")
    print(f"Pending (not yet encoded): {PENDING_SCENARIO_CODES}")
