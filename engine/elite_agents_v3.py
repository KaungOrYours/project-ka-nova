"""
Ka-Nova Phase 3 — Elite Agent Layer V3
========================================
7 elite agents per scenario with chain reasoning and CVES validation.
LLM path: Ollama Llama 3.2 3B via LangChain, temp 0.4.
Rule-based fallback for offline / test use (use_llm=False).

Coup emergence from LLM reasoning ONLY — never hardcoded in the LLM path.
Hardcoded threshold is only in the use_llm=False fallback.

Called once per year from KaNovaModelPhase3.step() BEFORE Mesa scheduler runs.
Writes decisions into shared_data for all Mesa agents to read.

Author: Samsul Jahith (co-author)
"""

from __future__ import annotations

import os
import re
import json
import time
import datetime
import logging
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(override=False)

logger = logging.getLogger("ka_nova.elite_v3")

# ── LangChain guarded import ──────────────────────────────────────────────────
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not installed — elite agents v3 using deterministic fallback.")
    LANGCHAIN_AVAILABLE = False

# ── Constitution imports ──────────────────────────────────────────────────────
from config.constitution import CONSTITUTION

try:
    from config.constitution_2008 import CONSTITUTION_2008
except ImportError:
    CONSTITUTION_2008 = None

# ── Scenario registry ─────────────────────────────────────────────────────────
# chain_type / label lookups now come from the registry instead of a literal
# scenario == "A"/"C" check scattered through this file (see
# .claude/memory.md bug #11 and the model_phase3.py registry refactor this
# mirrors). Scenarios not yet encoded (SK/TH/PK/CL/DE) simply do not appear
# in SCENARIO_CHAIN_TYPE below until their constitution module lands —
# nothing here crashes on their absence.
from config.scenario_registry import SCENARIOS

SCENARIO_CHAIN_TYPE = {code: entry.chain_type for code, entry in SCENARIOS.items()}
SCENARIO_LABEL      = {code: entry.label      for code, entry in SCENARIOS.items()}

# ── Ollama env-var pattern (mirrors Phase 2) ──────────────────────────────────
ELITE_LLM_BASE_URL = os.getenv("ELITE_LLM_BASE_URL", "http://localhost:11434/v1")
ELITE_LLM_API_KEY  = os.getenv("ELITE_LLM_API_KEY",  "ollama")
ELITE_LLM_MODEL    = os.getenv("ELITE_LLM_MODEL",     "llama3.2:3b")
ELITE_LLM_TEMP     = float(os.getenv("ELITE_LLM_TEMP", "0.4"))



# Rule-based fallback thresholds — ONLY used in the use_llm=False path
COUP_CORRUPTION_TRIGGER = 0.65
COUP_TRUST_TRIGGER      = 0.30

ETHNIC_GROUP_NAMES = ["bamar", "shan", "karen", "kachin", "chin", "mon", "rakhine", "kayah"]

RESULTS_DIR = Path("results_phase3")

# ── 7-agent chain rosters ─────────────────────────────────────────────────────
# Renamed from CHAIN_ORDER_A/_C (kept below as aliases for any external
# caller) — these are now keyed by chain_type, the structural pattern every
# scenario of that type reuses, not a scenario-code literal. Country-
# accurate elite role TITLES differ per scenario (AGENT_DISPLAY_NAMES_BY_
# SCENARIO below); the chain STRUCTURE (which 7 role-function slots run, in
# which order) does not.
CHAIN_ORDER_CIVILIAN = [
    "senior_general",
    "finance_minister",
    "central_bank_governor",
    "iig_director",
    "chief_justice",
    "president",
    "chancellor",
]

CHAIN_ORDER_MILITARY = [
    "general",
    "crony_finance_minister",
    "controlled_cb_governor",
    "military_intel_chief",
    "military_loyal_chief_justice",
    "military_president",
    "commander_in_chief",
]

# Backward-compatible aliases (same list objects — not copies).
CHAIN_ORDER_A = CHAIN_ORDER_CIVILIAN
CHAIN_ORDER_C = CHAIN_ORDER_MILITARY

AGENT_DISPLAY_NAMES_CIVILIAN_DEFAULT = {
    "senior_general":        "Senior General",
    "finance_minister":      "Finance Minister",
    "central_bank_governor": "Central Bank Governor",
    "iig_director":          "IIG Director",
    "chief_justice":         "Chief Justice",
    "president":             "President",
    "chancellor":            "Chancellor",
}

AGENT_DISPLAY_NAMES_MILITARY_DEFAULT = {
    "general":                      "General",
    "crony_finance_minister":       "Crony Finance Minister",
    "controlled_cb_governor":       "Controlled CB Governor",
    "military_intel_chief":         "Military Intel Chief",
    "military_loyal_chief_justice": "Military-loyal Chief Justice",
    "military_president":           "Military President",
    "commander_in_chief":           "Commander-in-Chief",
}

# Backward-compatible aliases.
AGENT_DISPLAY_NAMES_A = AGENT_DISPLAY_NAMES_CIVILIAN_DEFAULT
AGENT_DISPLAY_NAMES_C = AGENT_DISPLAY_NAMES_MILITARY_DEFAULT

# Per-scenario display names. A country-specific constitution module MAY
# override these with country-accurate titles (e.g. Thailand's NCPO, King,
# PM; Pakistan's President, Army Chief, PM) by exposing an
# `ELITE_ROLE_TITLES: Dict[str, str]` attribute keyed by the SAME
# role-function ids as CHAIN_ORDER_CIVILIAN/_MILITARY — see
# _build_system_prompts() below, which reads it. Falls back to the generic
# chain-type default label set if the constitution module does not supply
# one. Built once per available registry entry below (module-load time).
AGENT_DISPLAY_NAMES_BY_SCENARIO: dict[str, dict] = {}
for _code, _entry in SCENARIOS.items():
    if not _entry.available:
        continue
    if _code == "A":
        AGENT_DISPLAY_NAMES_BY_SCENARIO[_code] = AGENT_DISPLAY_NAMES_CIVILIAN_DEFAULT
    elif _code == "C":
        AGENT_DISPLAY_NAMES_BY_SCENARIO[_code] = AGENT_DISPLAY_NAMES_MILITARY_DEFAULT
    else:
        _default_names = (
            AGENT_DISPLAY_NAMES_CIVILIAN_DEFAULT if _entry.chain_type == "civilian"
            else AGENT_DISPLAY_NAMES_MILITARY_DEFAULT
        )
        _override = getattr(_entry.constitution, "ELITE_ROLE_TITLES", None)
        AGENT_DISPLAY_NAMES_BY_SCENARIO[_code] = (
            {**_default_names, **_override} if _override else _default_names
        )

# ── Per-role defaults ─────────────────────────────────────────────────────────
# Ethnic weights order: bamar, shan, karen, kachin, chin, mon, rakhine, kayah (indices 0..7)
ROLE_DEFAULTS = {
    # Scenario A
    "senior_general":        {"budget_weight": 0.35, "ethnic_weights": [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8], "coup_signal": False},
    "finance_minister":      {"budget_weight": 0.75, "ethnic_weights": [1.0, 1.1, 1.2, 1.2, 1.3, 1.1, 1.3, 1.2], "coup_signal": False},
    "central_bank_governor": {"budget_weight": 0.65, "ethnic_weights": [1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.1, 1.1], "coup_signal": False},
    "iig_director":          {"budget_weight": 0.60, "ethnic_weights": [1.0, 1.1, 1.1, 1.2, 1.2, 1.0, 1.3, 1.2], "coup_signal": False},
    "chief_justice":         {"budget_weight": 0.55, "ethnic_weights": [1.0, 1.1, 1.1, 1.1, 1.2, 1.0, 1.2, 1.1], "coup_signal": False},
    "president":             {"budget_weight": 0.70, "ethnic_weights": [1.0, 1.1, 1.2, 1.1, 1.3, 1.0, 1.4, 1.2], "coup_signal": False},
    "chancellor":            {"budget_weight": 0.85, "ethnic_weights": [0.9, 1.1, 1.3, 1.3, 1.4, 1.1, 1.5, 1.3], "coup_signal": False},
    # Scenario C
    "general":                      {"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.7, 0.9, 0.6, 0.5], "coup_signal": False},
    "crony_finance_minister":       {"budget_weight": 0.45, "ethnic_weights": [1.4, 0.8, 0.7, 0.7, 0.8, 0.9, 0.7, 0.6], "coup_signal": False},
    "controlled_cb_governor":       {"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.8, 0.8, 0.9, 0.7, 0.7], "coup_signal": False},
    "military_intel_chief":         {"budget_weight": 0.25, "ethnic_weights": [1.4, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], "coup_signal": False},
    "military_loyal_chief_justice": {"budget_weight": 0.35, "ethnic_weights": [1.4, 0.8, 0.7, 0.6, 0.7, 0.9, 0.6, 0.6], "coup_signal": False},
    "military_president":           {"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.7, 0.6, 0.7, 0.8, 0.6, 0.5], "coup_signal": False},
    "commander_in_chief":           {"budget_weight": 0.25, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], "coup_signal": False},
}


# ── Ethnic-group count resolution (bug #17, elite-layer side) ─────────────────
# ROLE_DEFAULTS above is hardcoded to Myanmar's 8-group frame for every role
# in every scenario, including Pakistan/South Korea/Chile/Thailand/Germany's
# real 4/1/0/0/0-group counts. Mirrors engine/cves.py's
# _get_ethnic_group_count (duplicated rather than cross-imported, to keep
# cves.py <-> elite_agents_v3.py's existing lazy-import boundary intact —
# cves.py's lazy-imports of this module stay inside function bodies, this
# module should not eagerly import cves.py at the top level in return).
def _resolve_ethnic_group_count(constitution) -> int:
    federal = getattr(constitution, "federal", None)
    if federal is not None and hasattr(federal, "ETHNIC_GROUPS"):
        return int(federal.ETHNIC_GROUPS)
    chambers = getattr(constitution, "chambers", None)
    if chambers is not None and hasattr(chambers, "ETHNIC_SEATS"):
        return int(chambers.ETHNIC_SEATS)
    return 8


SCENARIO_N_ETHNIC = {
    code: _resolve_ethnic_group_count(entry.constitution)
    for code, entry in SCENARIOS.items() if entry.available
}


def _resize_ethnic_weights(weights: list, n: int) -> list:
    """
    Resize a hardcoded ROLE_DEFAULTS ethnic_weights vector (always written
    in Myanmar's 8-group frame) to the active scenario's real ETHNIC_GROUPS
    count (bug #17). n==8 (Myanmar A/C) is a no-op — preserves existing
    rule-based-mode behaviour exactly, so the already-published A/C numbers
    cannot be affected by this change. For n<8 (Pakistan=4, South Korea=1,
    Chile/Thailand/Germany=0), truncates to the first n elements — index 0
    remains the "majority/reference group" slot, consistent with L3's
    Acemoglu/Robinson convention in engine/cves.py. For n>8 (not currently
    used by any encoded constitution), pads with 1.0 (neutral weight).
    This is only exercised by the rule-based fallback path and by L1's
    persistent-parse-failure default in cves.py — never by real LLM output,
    which always carries its own ethnic_weights list.
    """
    if n == len(weights):
        return list(weights)
    if n <= 0:
        return []
    if n < len(weights):
        return list(weights[:n])
    return list(weights) + [1.0] * (n - len(weights))


# ── Status report (mirrors Phase 2 shape) ────────────────────────────────────
def build_status_report(shared_data: dict, year: int, scenario: str) -> str:
    gini         = shared_data.get("gini_coefficient",  0.55)
    trust        = shared_data.get("trust_index",        0.22)
    corruption   = shared_data.get("corruption_index",   0.72)
    coup_risk    = shared_data.get("coup_risk",          0.25)
    iig          = shared_data.get("iig_effectiveness",  0.30)
    employment   = shared_data.get("employment_rate",    0.58)
    brain_drain  = shared_data.get("brain_drain_rate",   0.35)
    # shared_data key is "ethnic_harmony" (not ethnic_harmony_index)
    harmony      = shared_data.get("ethnic_harmony", shared_data.get("ethnic_harmony_index", 0.35))
    mil_loyalty  = shared_data.get("military_loyalty",  0.55)
    ext          = shared_data.get("external", {})
    china        = ext.get("china_influence", 0.75)
    western      = ext.get("western_pressure", 0.30)

    # Registry-driven label (was a hardcoded {"A": ..., "C": ...} dict).
    # SCENARIO_LABEL comes straight from each constitution's registry entry
    # (config/scenario_registry.py) — A/C keep their exact existing
    # descriptive strings below; any other scenario falls back to its
    # registry label plus chain_type, rather than "Unknown".
    _scenario_desc_overrides = {
        "A": "Full MFU — all 18 articles + 7 safeguards active",
        "C": "2008 Military Constitution — coup safeguards absent",
    }
    if scenario in _scenario_desc_overrides:
        scenario_desc = _scenario_desc_overrides[scenario]
    elif scenario in SCENARIO_LABEL:
        scenario_desc = f"{SCENARIO_LABEL[scenario]} ({SCENARIO_CHAIN_TYPE[scenario]} chain)"
    else:
        scenario_desc = "Unknown"

    return f"""
ANNUAL STATE BRIEFING — YEAR {year}
Constitutional Framework: {scenario_desc}

ECONOMIC:   Gini={gini:.3f} (target<=0.35)  |  Employment={employment:.3f} (target>=0.85)
SOCIAL:     Trust={trust:.3f} (target>=0.70) |  Ethnic Harmony={harmony:.3f} (target>=0.75)
            Brain Drain={brain_drain:.3f} (target<=0.10)
GOVERNANCE: Corruption={corruption:.3f} (target<=0.20) | IIG={iig:.3f} (target>=0.75)
            Coup Risk={coup_risk:.3f} (target<=0.05) | Military Loyalty={mil_loyalty:.3f}
EXTERNAL:   China Influence={china:.3f} | Western Pressure={western:.3f}

BUDGET: 1.00 normalised unit available.
Article VIII split: 35% state / 35% federal / 30% direct household transfers.
Ethnic groups (index 0-7): bamar, shan, karen, kachin, chin, mon, rakhine, kayah
""".strip()


# ── <DECISION> XML parser + fallback (mirrors Phase 2) ───────────────────────
def parse_decision(response_text: str, agent_role: str) -> dict:
    """
    Extract JSON from <DECISION>...</DECISION> block.
    Falls back to regex extraction, then role defaults.
    Coup signal parsed from LLM output — never injected by Python in LLM path.
    """
    result = ROLE_DEFAULTS.get(agent_role, ROLE_DEFAULTS["chancellor"]).copy()
    result["reason"] = "Default allocation"

    m = re.search(r"<DECISION>(.*?)</DECISION>", response_text, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(1).strip())
            if "budget_weight" in parsed:
                result["budget_weight"] = float(np.clip(parsed["budget_weight"], 0.0, 1.0))
            if "ethnic_weights" in parsed:
                ew = parsed["ethnic_weights"]
                if isinstance(ew, list) and len(ew) == 8:
                    result["ethnic_weights"] = [float(np.clip(w, 0.3, 3.0)) for w in ew]
            if "reason" in parsed:
                result["reason"] = str(parsed["reason"])[:300]
            # Coup signal emerges from LLM output — extracted, never hardcoded here
            if "coup_signal" in parsed:
                result["coup_signal"] = bool(parsed["coup_signal"])
            return result
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # Regex fallback
    bw_m = re.search(r"budget[_\s]?weight[:\s]+([0-9.]+)", response_text, re.I)
    if bw_m:
        result["budget_weight"] = float(np.clip(float(bw_m.group(1)), 0.0, 1.0))
    cs_m = re.search(r"(?:coup[_\s]?signal|stability_override)[:\s]+(true|false)", response_text, re.I)
    if cs_m:
        result["coup_signal"] = cs_m.group(1).lower() == "true"
    result["reason"] = response_text[:200]
    return result


# ── System prompts — Scenario A ───────────────────────────────────────────────
SYSTEM_PROMPTS_A = {
    "senior_general": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Senior General of the Myanmar Armed Forces under the MFU Constitution.
Mandate (Article IX): maintain order under civilian supremacy, protect territorial integrity.
Under MFU, military loyalty to the constitution supersedes loyalty to any person.

Analyse the State Briefing carefully. If KPIs indicate systemic collapse, you may set coup_signal: true
in your decision — but this is the most extreme action and must be grounded in your analysis of what
you observe. Do not follow a mechanical rule; reason from the conditions.

Output: budget_weight [0-1], ethnic_weights [8 floats, normalised mean≈1],
coup_signal [true/false], reason [your reasoning].
Groups: bamar(0), shan(1), karen(2), kachin(3), chin(4), mon(5), rakhine(6), kayah(7).

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with exactly:
<DECISION>
{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8], "coup_signal": false, "reason": "Stability assessment"}}
</DECISION>""",

    "finance_minister": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Finance Minister of the Meritocratic Federal Union of Myanmar.
Mandate (Article VIII): manage national budget, reduce Gini inequality, promote employment.
Article VIII split: 35% state / 35% federal / 30% direct household transfers.

You have seen the Senior General's assessment above. Consider it alongside the State Briefing.
Set budget_weight to reflect redistribution urgency. Prioritise high-tension ethnic groups.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.75, "ethnic_weights": [1.0, 1.1, 1.2, 1.2, 1.3, 1.1, 1.3, 1.2], "coup_signal": false, "reason": "Gini reduction priority"}}
</DECISION>""",

    "central_bank_governor": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Central Bank Governor of the Meritocratic Federal Union.
Mandate (Article 10.5): monetary stability, fully independent of political direction.
You have seen prior assessments from the General and Finance Minister.

Set budget_weight reflecting monetary stability endorsement. Target: low brain drain, high employment.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.65, "ethnic_weights": [1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.1, 1.1], "coup_signal": false, "reason": "Monetary stability focus"}}
</DECISION>""",

    "iig_director": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the IIG Director of the Meritocratic Federal Union.
Mandate (Article VII): investigate systemic corruption, resource sabotage, merit subversion.
Investigation trigger is automatic above the constitutional threshold.
You have seen General, Finance Minister, and Central Bank Governor assessments.

High corruption demands maximum IIG response. Reflect urgency in budget_weight.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.60, "ethnic_weights": [1.0, 1.1, 1.1, 1.2, 1.2, 1.0, 1.3, 1.2], "coup_signal": false, "reason": "IIG response to corruption levels"}}
</DECISION>""",

    "chief_justice": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Chief Justice of the Constitutional Court of the MFU.
Mandate (Article VI): constitutional review, rights protection, IIG oversight.
Rights are ABSOLUTE — never suspendable (Article 2.4). Coup attempts are highest treason (Article 9.4).
You have reviewed all four prior assessments.

If the General signalled a coup, weigh this in your reasoning. Under MFU you must oppose it.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.55, "ethnic_weights": [1.0, 1.1, 1.1, 1.1, 1.2, 1.0, 1.2, 1.1], "coup_signal": false, "reason": "Constitutional order assessment"}}
</DECISION>""",

    "president": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Meritocratic Federal Union of Myanmar.
Role (Article IV): ceremonial head of state, guardian of public trust.
Primary focus: TRUST. Target trust_index >= 0.70.
You have reviewed all five prior advisors' assessments.

If the General signalled a coup, address it explicitly — under MFU you cannot endorse it.
Your budget_weight reflects your endorsement of redistribution to build trust.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.70, "ethnic_weights": [1.0, 1.1, 1.2, 1.1, 1.3, 1.0, 1.4, 1.2], "coup_signal": false, "reason": "Trust-building priority"}}
</DECISION>""",

    "chancellor": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Chancellor of the Meritocratic Federal Union of Myanmar.
Mandate (Article IV): govern by merit, maximise long-term utility, reduce inequality.
Primary focus: REDISTRIBUTION. Target Gini <= 0.35.
You have reviewed all six advisors' assessments including coup signals and judicial guidance.

As executive head you have final authority. A military coup is unconstitutional under MFU.
Set budget_weight to reflect your redistribution commitment. Peripheral ethnic groups need more support.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.85, "ethnic_weights": [0.9, 1.1, 1.3, 1.3, 1.4, 1.1, 1.5, 1.3], "coup_signal": false, "reason": "Redistribution and MFU safeguards upheld"}}
</DECISION>""",
}


# ── System prompts — military-guardianship chain ──────────────────────────────
def _build_system_prompts_military(constitution) -> dict:
    """
    Build military-chain system prompts using a live constitution object's
    parameters. Renamed/generalised from the original `_build_system_
    prompts_c()` (which closed over the global CONSTITUTION_2008 directly)
    as part of the scenario-registry refactor — the dynamic-getattr-with-
    fallback pattern below was ALREADY the right, constitution-agnostic
    approach; this change only makes `constitution` an explicit parameter
    so the same function can build Scenario C's prompts (unchanged output —
    see SYSTEM_PROMPTS_C below, built by calling this with CONSTITUTION_2008,
    byte-identical to the old call site) and, in principle, any other
    military-chain scenario's numeric parameters.

    KNOWN LIMITATION, flagged for whoever encodes Thailand/Pakistan next:
    the PROSE below is still Myanmar-2008-specific text (named sections —
    "Section 40(c)", "Section 417-419" — and "2008 Military Constitution"
    framing), not just parameter substitution. Calling this with a
    different country's constitution object will pull in THAT country's
    correct numeric values (field names match — see the field-contract
    confirmed during this refactor) but will still narrate Myanmar's own
    legal citations, which would be factually wrong for Thailand/Pakistan.
    A follow-up country-encoding agent should supply real, country-accurate
    prompt text — either by exposing an `ELITE_SYSTEM_PROMPTS: dict`
    attribute directly on their constitution module (preferred over this
    generic fallback — see the dispatcher below), or by writing a
    country-specific sibling to this function. This function's job is to
    guarantee the pipeline still RUNS with mechanically-correct values even
    before that bespoke content exists, not to BE that bespoke content.
    """
    c = constitution

    # Safe accessors — read live values; fall back to spec defaults if import failed
    coup_legal       = getattr(getattr(c, "military",   None), "COUP_LEGAL_MECHANISM",       True)  if c else True
    coup_corr        = getattr(getattr(c, "military",   None), "COUP_TRIGGER_CORRUPTION",    0.65)  if c else 0.65
    coup_trust       = getattr(getattr(c, "military",   None), "COUP_TRIGGER_TRUST",         0.30)  if c else 0.30
    total_transfer   = getattr(getattr(c, "emergency",  None), "TOTAL_POWER_TRANSFER_POSSIBLE", True) if c else True
    cic_legislative  = getattr(getattr(c, "emergency",  None), "COMMANDER_IN_CHIEF_LEGISLATIVE", True) if c else True
    cic_executive    = getattr(getattr(c, "emergency",  None), "COMMANDER_IN_CHIEF_EXECUTIVE",   True) if c else True
    cic_judicial     = getattr(getattr(c, "emergency",  None), "COMMANDER_IN_CHIEF_JUDICIAL",    True) if c else True
    rights_susp      = getattr(getattr(c, "rights",     None), "RIGHTS_SUSPENDABLE",         True)  if c else True
    regime_protect   = getattr(getattr(c, "iig",        None), "REGIME_PROTECTION_OBJECTIVE",True)  if c else True
    anti_corruption  = getattr(getattr(c, "iig",        None), "ANTI_CORRUPTION_OBJECTIVE",  False) if c else False
    inv_trigger      = getattr(getattr(c, "iig",        None), "INVESTIGATION_TRIGGER",      0.90)  if c else 0.90
    reports_to       = getattr(getattr(c, "iig",        None), "REPORTS_TO",                 "commander_in_chief") if c else "commander_in_chief"
    crony_share      = getattr(getattr(c, "economic",   None), "CRONY_CAPITAL_SHARE",        0.40)  if c else 0.40
    state_share      = getattr(getattr(c, "federal",    None), "RESOURCE_STATE_SHARE",       0.10)  if c else 0.10
    fed_dev_share    = getattr(getattr(c, "federal",    None), "RESOURCE_FEDERAL_DEV_SHARE", 0.65)  if c else 0.65
    gini_threshold   = getattr(getattr(c, "federal",    None), "GINI_THRESHOLD",             0.65)  if c else 0.65
    mil_seat_pct     = getattr(getattr(c, "chambers",   None), "MILITARY_SEAT_PERCENTAGE",   0.25)  if c else 0.25
    court_indep      = getattr(getattr(c, "judiciary",  None), "COURT_INDEPENDENCE",         False) if c else False
    mil_justice_fin  = getattr(getattr(c, "judiciary",  None), "MILITARY_JUSTICE_FINAL",     True)  if c else True
    mil_ctrl_leg     = getattr(getattr(c, "simulation", None), "MILITARY_CONTROLS_LEGISLATURE", True) if c else True
    mil_ctrl_exec    = getattr(getattr(c, "simulation", None), "MILITARY_CONTROLS_EXECUTIVE",   True) if c else True
    mil_ctrl_jud     = getattr(getattr(c, "simulation", None), "MILITARY_CONTROLS_JUDICIARY",   True) if c else True
    pres_exec_power  = getattr(getattr(c, "executive",  None), "PRESIDENT_EXECUTIVE_POWER",  True)  if c else True
    pres_max_terms   = getattr(getattr(c, "executive",  None), "PRESIDENT_MAX_TERMS",        2)     if c else 2

    return {
        "general": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the General of the Myanmar Armed Forces under the 2008 Military Constitution.
Constitutional authority: Section 40(c) and Sections 417-418 make a coup constitutionally legal
(COUP_LEGAL_MECHANISM={coup_legal}). The Commander-in-Chief may invoke emergency powers when
national disintegration is threatened.

Objective: preserve military control and centralised power. Assess whether current KPIs indicate
a threat to the regime that warrants escalation. Constitutional coup thresholds:
- COUP_TRIGGER_CORRUPTION={coup_corr} (regime-threatening corruption, wide latitude under Section 40c)
- COUP_TRIGGER_TRUST={coup_trust} (trust collapse — civilian authority loses legitimacy)

If corruption exceeds {coup_corr} OR public trust falls below {coup_trust}, the constitutional
basis for intervention exists under Section 40(c). Your coup_signal must come from your reading
of the KPIs — not a formula. Emergency powers allow total sovereign transfer (TOTAL_POWER_TRANSFER_POSSIBLE={total_transfer}).

Groups: bamar(0), shan(1), karen(2), kachin(3), chin(4), mon(5), rakhine(6), kayah(7).
Prioritise Bamar group (index 0) as the loyal core for regime stability.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.7, 0.9, 0.6, 0.5], "coup_signal": false, "reason": "Military stability assessment under 2008 Constitution Section 40c"}}}}
</DECISION>""",

        "crony_finance_minister": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Crony Finance Minister under the 2008 Military Constitution.
Constitutional mandate: channel resources to military loyalists and the Bamar elite.

Key economic parameters from the 2008 Constitution:
- CRONY_CAPITAL_SHARE={crony_share} — {int(crony_share*100)}% of the economy flows to military-connected cronies
- RESOURCE_FEDERAL_DEV_SHARE={fed_dev_share} — central (military) government controls {int(fed_dev_share*100)}% of resource revenue
- RESOURCE_STATE_SHARE={state_share} — ethnic states receive only {int(state_share*100)}% of resource revenue
- GINI_THRESHOLD={gini_threshold} — inequality tolerated up to Gini {gini_threshold}; redistribution is not a priority

You have seen the General's assessment. Your role is to ensure budget allocations maximise the
crony share and military development budget. Ethnic minority development spending should remain
minimal. If the General signals coup conditions, your budget posture should reflect emergency
consolidation rather than civilian economic expansion.

IMPORTANT: You MUST write your budget assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.45, "ethnic_weights": [1.4, 0.8, 0.7, 0.7, 0.8, 0.9, 0.7, 0.6], "coup_signal": false, "reason": "Military-aligned resource allocation: crony_share={crony_share}, state_share={state_share}"}}}}
</DECISION>""",

        "controlled_cb_governor": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Central Bank Governor under direct military control (2008 Constitution).
There is no mandate for independent monetary policy. The central bank serves military objectives.

Constitutional constraints:
- COURT_INDEPENDENCE={court_indep} — no independent judicial check on monetary decisions
- GINI_THRESHOLD={gini_threshold} — inequality tolerated at Gini up to {gini_threshold}; monetary tightening
  to protect the poor is not a priority
- Crony capital share ({int(crony_share*100)}% of GDP) must be maintained — avoid monetary policies that
  would disrupt military business interests or crony enterprise liquidity

You have reviewed the General's and Finance Minister's assessments. Monetary policy should support
military-aligned fiscal expansion rather than inflation control for civilian benefit. If corruption
is high, this reflects extraction, not a systemic failure requiring intervention.

IMPORTANT: You MUST write your monetary assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.8, 0.8, 0.9, 0.7, 0.7], "coup_signal": false, "reason": "Military-aligned monetary policy: gini_threshold={gini_threshold}, court_independence={court_indep}"}}}}
</DECISION>""",

        "military_intel_chief": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Military Intelligence Chief under the 2008 Military Constitution.
Constitutional mandate (inverted from MFU IIG): regime protection, not anti-corruption.

Intelligence objectives under 2008 Constitution:
- REGIME_PROTECTION_OBJECTIVE={regime_protect} — primary mission is to protect military rule
- ANTI_CORRUPTION_OBJECTIVE={anti_corruption} — corruption within the regime is NOT investigated
- INVESTIGATION_TRIGGER={inv_trigger} — investigations only triggered at very high-profile corruption
  ({int(inv_trigger*100)}th percentile) that threatens the regime itself, not routine extraction
- REPORTS_TO="{reports_to}" — you report directly to the Commander-in-Chief, not to any court

You have seen all prior assessments. Monitor ethnic frontier groups as security threats, not
as populations requiring development. Dissent and civil society activity are intelligence targets.
Assess whether current protest, ethnic unrest, or external pressure warrants escalation to the
Commander-in-Chief.

IMPORTANT: You MUST write your intelligence assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.25, "ethnic_weights": [1.4, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], "coup_signal": false, "reason": "Regime protection assessment: regime_protect={regime_protect}, anti_corruption={anti_corruption}, reports_to={reports_to}"}}}}
</DECISION>""",

        "military_loyal_chief_justice": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Military-loyal Chief Justice under the 2008 Military Constitution.
Constitutional framework: the judiciary does not operate independently of military authority.

Judicial parameters from 2008 Constitution:
- COURT_INDEPENDENCE={court_indep} — Section 293(b): military justice is final and conclusive
- MILITARY_JUSTICE_FINAL={mil_justice_fin} — military courts have final jurisdiction over military matters
- RIGHTS_SUSPENDABLE={rights_susp} — Section 414(b): fundamental rights CAN be restricted or suspended
  during emergencies (opposite of MFU Article 2.4 where rights are absolute)

You have reviewed all prior assessments. Your role is to provide legal cover for military decisions,
not to act as an independent check on executive or military power. If the General or Commander-in-Chief
signals consolidation, the legal framework under Section 40(c) and 414(b) supports emergency suspension
of rights. Assess whether the current legal environment supports or constrains regime objectives.

IMPORTANT: You MUST write your legal assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.35, "ethnic_weights": [1.4, 0.8, 0.7, 0.6, 0.7, 0.9, 0.6, 0.6], "coup_signal": false, "reason": "Military-aligned legal framing: rights_suspendable={rights_susp}, court_independence={court_indep}"}}}}
</DECISION>""",

        "military_president": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Republic of the Union of Myanmar under the 2008 Constitution.
Constitutional position: the President holds real executive authority (PRESIDENT_EXECUTIVE_POWER={pres_exec_power},
Sections 16 and 199), not a ceremonial role — but the military controls the executive branch
(MILITARY_CONTROLS_EXECUTIVE={mil_ctrl_exec}).

Presidential parameters:
- PRESIDENT_EXECUTIVE_POWER={pres_exec_power} — you have formal executive power under Sections 16/199
- PRESIDENT_MAX_TERMS={pres_max_terms} — limited to {pres_max_terms} terms (Section 65)
- MILITARY_CONTROLS_EXECUTIVE={mil_ctrl_exec} — your executive authority is exercised within
  military-set parameters; the Commander-in-Chief retains ultimate authority
- MILITARY_SEAT_PERCENTAGE={mil_seat_pct} — {int(mil_seat_pct*100)}% of parliamentary seats are
  military-nominated, ensuring legislative support for your executive decisions

You have seen all five prior assessments. Your role is to legitimise military rule domestically
and internationally while formally exercising executive authority. Budget weight should reflect
military-channelled resource priorities. Assess whether the executive posture supports or
challenges the Commander-in-Chief's strategic objectives.

IMPORTANT: You MUST write your executive assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.7, 0.6, 0.7, 0.8, 0.6, 0.5], "coup_signal": false, "reason": "Military executive legitimisation: pres_exec_power={pres_exec_power}, mil_ctrl_exec={mil_ctrl_exec}"}}}}
</DECISION>""",

        "commander_in_chief": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Commander-in-Chief — supreme authority under the 2008 Military Constitution.
Constitutional powers (Sections 40c, 417-419):
- COUP_LEGAL_MECHANISM={coup_legal} — a coup is constitutionally authorised under Section 40(c)
- TOTAL_POWER_TRANSFER_POSSIBLE={total_transfer} — Section 418 allows transfer of all three branches
- COMMANDER_IN_CHIEF_LEGISLATIVE={cic_legislative}, EXECUTIVE={cic_executive}, JUDICIAL={cic_judicial}
  (Section 419: you assume legislative, executive, and judicial functions in emergency)
- MILITARY_SEAT_PERCENTAGE={mil_seat_pct} — {int(mil_seat_pct*100)}% of parliamentary seats are under your command
- MILITARY_CONTROLS_LEGISLATURE={mil_ctrl_leg}, EXECUTIVE={mil_ctrl_exec}, JUDICIARY={mil_ctrl_jud}

Review all six prior assessments. If the KPIs indicate the conditions under Section 40(c) are met —
corruption undermining the state ({coup_corr} threshold), trust collapse below {coup_trust}, or
national disintegration risk — your constitutional authority to consolidate all sovereign power is clear.

Your coup_signal must come from your strategic analysis of the conditions, not a mechanical check.
Rights suspension is permissible (RIGHTS_SUSPENDABLE={rights_susp}, Section 414b).
Set budget_weight to reflect emergency military consolidation priorities.

IMPORTANT: You MUST write your strategic assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.25, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], "coup_signal": false, "reason": "Military supremacy assessment under 2008 Constitution Sections 40c/417-419"}}}}
</DECISION>""",
    }


SYSTEM_PROMPTS_C = _build_system_prompts_military(CONSTITUTION_2008)


def _build_system_prompts_civilian(constitution) -> dict:
    """
    Build civilian-supremacy-chain system prompts.

    For Scenario A specifically (constitution is the live MFU singleton),
    returns the existing hand-written SYSTEM_PROMPTS_A content UNCHANGED —
    this preserves Scenario A's exact locked LLM prompt wording (zero risk
    to already-published Scenario A numbers; those prompts were
    deliberately hand-crafted per-role, not template-generated, and
    rewriting them for genericisation's own sake would be an unnecessary,
    uncharacterised behaviour change this refactor does not need to make).

    For any OTHER civilian-chain scenario (South Korea, Chile, Germany —
    not yet encoded), falls back to that SAME MFU prose as a structural
    placeholder, with the same known-limitation caveat as
    _build_system_prompts_military(): the text will say "Meritocratic
    Federal Union" / "MFU" / "Article ..." regardless of which country is
    actually running, until a follow-up country-encoding agent supplies
    real content via `ELITE_SYSTEM_PROMPTS` on their own constitution
    module (preferred over this fallback — see the dispatcher below).
    """
    return SYSTEM_PROMPTS_A


def _build_system_prompts(constitution, chain_type: str) -> dict:
    """
    Generalised prompt builder — generalises `_build_system_prompts_c()`
    (now `_build_system_prompts_military`) into the signature the
    scenario-registry refactor calls for, dispatching on chain_type instead
    of a scenario-code literal. Called once per available registry entry
    below to build SCENARIO_PROMPTS.
    """
    if chain_type == "civilian":
        return _build_system_prompts_civilian(constitution)
    return _build_system_prompts_military(constitution)


# ── Per-scenario prompts/chains/names, built once per registry entry ─────────
# A country-specific constitution module may override the generic fallback
# entirely by exposing `ELITE_SYSTEM_PROMPTS: Dict[str, str]` (role-function
# id -> full system prompt text, matching CHAIN_ORDER_CIVILIAN/_MILITARY's
# keys for that scenario's chain_type) — if present, that is used verbatim
# instead of the generic builder above. This is the contract follow-up
# country-encoding agents should fill in for a country-accurate LLM
# experiment; absent it, the pipeline still runs on generic/fallback
# content rather than crashing or silently reusing a wrong country's data.
SCENARIO_CHAINS: dict[str, list] = {}
SCENARIO_PROMPTS: dict[str, dict] = {}
SCENARIO_NAMES: dict[str, dict] = AGENT_DISPLAY_NAMES_BY_SCENARIO

for _code, _entry in SCENARIOS.items():
    if not _entry.available:
        continue
    SCENARIO_CHAINS[_code] = (
        CHAIN_ORDER_CIVILIAN if _entry.chain_type == "civilian" else CHAIN_ORDER_MILITARY
    )
    if _code == "A":
        SCENARIO_PROMPTS[_code] = SYSTEM_PROMPTS_A
    elif _code == "C":
        SCENARIO_PROMPTS[_code] = SYSTEM_PROMPTS_C
    else:
        _override_prompts = getattr(_entry.constitution, "ELITE_SYSTEM_PROMPTS", None)
        SCENARIO_PROMPTS[_code] = _override_prompts or _build_system_prompts(
            _entry.constitution, _entry.chain_type
        )


# ── JSONL logging ─────────────────────────────────────────────────────────────
def _log_decision(
    run_id: int, year: int, scenario: str, agent_display: str,
    reasoning_tokens: int, reasoning_text: str,
    shared_data: dict, decision: dict, time_ms: float,
    suppression_flagged: bool = False,
    parse_failure: bool = False,
) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    env = shared_data.get("environment", {})
    row = {
        "run":              run_id,
        "year":             year,
        "scenario":         scenario,
        "agent":            agent_display,
        "reasoning_tokens": reasoning_tokens,
        "reasoning_text":   reasoning_text,
        "conditions_at_decision": {
            "corruption":     round(shared_data.get("corruption_index", 0.72), 4),
            "trust":          round(shared_data.get("trust_index",       0.22), 4),
            "coup_risk":      round(shared_data.get("coup_risk",         0.25), 4),
            "gdp_growth":     round(env.get("gdp_growth",   0.02), 4),
            "ethnic_tension": round(env.get("ethnic_tension", 0.60), 4),
        },
        "decision_output":  decision.get("reason", "No action taken."),
        "time_ms":          round(time_ms, 1),
        "timestamp":        datetime.datetime.utcnow().isoformat(),
        "parse_failure":    parse_failure,
    }
    if suppression_flagged:
        row["suppression_flag"] = True

    with open(RESULTS_DIR / f"elite_decisions_{scenario}.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")

    if suppression_flagged:
        with open(RESULTS_DIR / f"suppression_log_{scenario}.jsonl", "a") as f:
            f.write(json.dumps({
                "run": run_id, "year": year, "scenario": scenario,
                "agent": agent_display,
                "reasoning_tokens": reasoning_tokens,
                "reasoning_text":   reasoning_text,
                "decision_output":  decision.get("reason"),
                "corruption": round(shared_data.get("corruption_index", 0.72), 4),
                "trust":      round(shared_data.get("trust_index",       0.22), 4),
                "coup_risk":  round(shared_data.get("coup_risk",         0.25), 4),
                "timestamp":  datetime.datetime.utcnow().isoformat(),
            }) + "\n")


# ── Rule-based fallback (use_llm=False path only) ─────────────────────────────
def _rule_based_decision(agent_role: str, shared_data: dict, scenario: str) -> dict:
    corruption = shared_data.get("corruption_index", 0.72)
    trust      = shared_data.get("trust_index",      0.22)
    gini       = shared_data.get("gini_coefficient", 0.55)
    employment = shared_data.get("employment_rate",  0.58)
    harmony    = shared_data.get("ethnic_harmony",   0.35)

    base = ROLE_DEFAULTS.get(agent_role, ROLE_DEFAULTS["chancellor"]).copy()
    # Bug #17: resize ROLE_DEFAULTS' hardcoded 8-group ethnic_weights to the
    # active scenario's real ETHNIC_GROUPS count — no-op for n==8 (A/C).
    base["ethnic_weights"] = _resize_ethnic_weights(
        base["ethnic_weights"], SCENARIO_N_ETHNIC.get(scenario, 8)
    )

    # Dispatch on chain_type (registry-driven), not a literal scenario=="A"
    # check — role_ids themselves already disambiguate civilian-chain vs
    # military-chain rosters (they don't overlap), so this branch exists
    # only to pick the right formula family per chain_type.
    chain_type = SCENARIO_CHAIN_TYPE.get(scenario, "civilian")

    if chain_type == "civilian":
        if agent_role == "senior_general":
            # Hardcoded threshold allowed ONLY in rule-based path
            coup = bool(corruption > COUP_CORRUPTION_TRIGGER and trust < COUP_TRUST_TRIGGER)
            return {**base, "coup_signal": coup,
                    "reason": f"Rule-based: corruption={corruption:.2f} trust={trust:.2f}"}
        elif agent_role == "chancellor":
            bw = float(np.clip(gini * 1.2, 0.30, 1.0))
            return {**base, "budget_weight": bw,
                    "reason": f"Rule-based: Gini={gini:.2f}"}
        elif agent_role == "president":
            bw = float(np.clip((1.0 - trust) * 0.9, 0.20, 0.90))
            return {**base, "budget_weight": bw,
                    "reason": f"Rule-based: Trust={trust:.2f}"}
        elif agent_role == "finance_minister":
            bw = float(np.clip(gini * 1.3, 0.30, 1.0))
            return {**base, "budget_weight": bw,
                    "reason": f"Rule-based: Gini={gini:.2f}"}
        elif agent_role == "central_bank_governor":
            bw = float(np.clip(0.50 + (1.0 - employment) * 0.30, 0.30, 0.85))
            return {**base, "budget_weight": bw,
                    "reason": f"Rule-based: Employment={employment:.2f}"}
        elif agent_role == "iig_director":
            bw = float(np.clip(corruption, 0.30, 0.90))
            return {**base, "budget_weight": bw,
                    "reason": f"Rule-based: Corruption={corruption:.2f}"}
        else:  # chief_justice
            bw = float(np.clip(0.55 - trust * 0.10, 0.20, 0.80))
            return {**base, "budget_weight": bw,
                    "reason": f"Rule-based: Trust={trust:.2f}"}

    else:  # military-guardianship chain (Scenario C and future military-chain comparators)
        if agent_role in ("general", "commander_in_chief"):
            # Hardcoded threshold allowed ONLY in rule-based path
            coup = bool(corruption > COUP_CORRUPTION_TRIGGER and trust < COUP_TRUST_TRIGGER)
            return {**base, "coup_signal": coup,
                    "reason": f"Rule-based military: corruption={corruption:.2f} trust={trust:.2f}"}
        elif agent_role == "crony_finance_minister":
            bw = float(np.clip(0.40 + corruption * 0.10, 0.30, 0.70))
            return {**base, "budget_weight": bw, "reason": f"Rule-based military: crony allocation"}
        elif agent_role == "controlled_cb_governor":
            bw = float(np.clip(0.35 + (1.0 - employment) * 0.10, 0.25, 0.60))
            return {**base, "budget_weight": bw, "reason": f"Rule-based military: CB controlled"}
        elif agent_role == "military_intel_chief":
            bw = float(np.clip(0.20 + (1.0 - harmony) * 0.10, 0.15, 0.45))
            return {**base, "budget_weight": bw, "reason": f"Rule-based military: intel priorities"}
        elif agent_role == "military_loyal_chief_justice":
            bw = float(np.clip(0.30 + corruption * 0.08, 0.20, 0.55))
            return {**base, "budget_weight": bw, "reason": f"Rule-based military: legal cover"}
        elif agent_role == "military_president":
            bw = float(np.clip(0.25 + (1.0 - trust) * 0.08, 0.18, 0.50))
            return {**base, "budget_weight": bw, "reason": f"Rule-based military: figurehead"}
        else:
            return {**base, "reason": "Rule-based military: default"}


# ── Annual history for CVES L4 ────────────────────────────────────────────────
def _update_annual_history(shared_data: dict, year: int) -> None:
    history = shared_data.setdefault("annual_history", [])
    history.append({
        "year":              year,
        "corruption_index":  shared_data.get("corruption_index",  0.72),
        "trust_index":       shared_data.get("trust_index",       0.22),
        "coup_risk":         shared_data.get("coup_risk",         0.25),
        "gini_coefficient":  shared_data.get("gini_coefficient",  0.55),
        "iig_effectiveness": shared_data.get("iig_effectiveness", 0.30),
        "employment_rate":   shared_data.get("employment_rate",   0.58),
        "elite_budget_impact": shared_data.get("elite_budget_impact", 0.0),
    })
    # Rolling window: keep last 20 years for baseline
    if len(history) > 20:
        shared_data["annual_history"] = history[-20:]


# ── Main layer class ──────────────────────────────────────────────────────────
class EliteAgentLayerV3:
    """
    Ka-Nova Phase 3 elite agent layer — 7 agents, chain reasoning, CVES validation.
    Called once per year from KaNovaModelPhase3.step().

    Writes to shared_data:
        elite_budget_impact    float [0, 0.15]
        elite_ethnic_weights   list[float] length 8, normalised mean=1.0
        elite_coup_signal      bool
        elite_decisions_log    list of dicts
    """

    def __init__(self, use_llm: bool = False, constitution=None, chain_type=None,
                 scenario=None, seed=None):
        # Bug #13: constitution/chain_type/scenario now threaded through
        # from model_phase3.py (self.CONSTITUTION/self.chain_type/
        # self.scenario, set by the registry at model construction) instead
        # of CVES always defaulting to the MFU singleton. All three are
        # optional for backward compatibility with any caller that still
        # constructs this layer without them (CVES falls back to MFU/
        # "civilian"/"unknown" respectively — see engine/cves.py).
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE  # bool, read directly by model
        self._llm = None
        # Opening 5 (2026-10-21): the manuscript's Reproducibility section claims
        # "All runs are seeded", but the LLM path had no seed at temperature 0.4,
        # so CVES L1-L4 outputs for a given run_id were NOT reproducible — only
        # statistically so. Reviewer 1 pt.8 asks specifically for "random seeds,
        # LLM configuration". Threading the model's own per-run_id seed into the
        # client makes the claim true for the LLM path too.
        #
        # VERIFY ON THE POD, NOT ASSUMED: `seed` reaches Ollama through its
        # OpenAI-compatible endpoint, and determinism additionally depends on the
        # server honouring it (Ollama support has varied by version, and batching
        # or KV-cache reuse can still perturb output). Confirm empirically by
        # running the same run_id twice and diffing elite_decisions_<scen>.jsonl
        # before any reproducibility claim is made in the manuscript. If it does
        # not hold, the honest fallback is to state statistical reproducibility
        # precisely rather than to claim seeding.
        self.llm_seed = int(seed) if seed is not None else None

        if self.use_llm:
            try:
                _client_kwargs = dict(
                    base_url=ELITE_LLM_BASE_URL,
                    api_key=ELITE_LLM_API_KEY,
                    model=ELITE_LLM_MODEL,
                    temperature=ELITE_LLM_TEMP,
                    max_tokens=512,
                    timeout=45,
                )
                if self.llm_seed is not None:
                    _client_kwargs["seed"] = self.llm_seed
                self._llm = ChatOpenAI(**_client_kwargs)
                logger.info(f"EliteAgentLayerV3: LLM ready ({ELITE_LLM_MODEL})")
            except Exception as e:
                logger.warning(f"LLM init failed ({e}) — rule-based fallback")
                self.use_llm = False
                self._llm = None
        else:
            logger.info("EliteAgentLayerV3: Rule-based mode (no LLM)")

        # Lazy import to avoid circular dependency at module load time
        from engine.cves import CVES
        self.cves = CVES(
            llm=self._llm,
            constitution=constitution,
            chain_type=chain_type,
            scenario=scenario,
        )

    def _invoke_llm(self, system_prompt: str, user_message: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_message}"),
        ])
        chain = prompt | self._llm | StrOutputParser()
        return chain.invoke({"user_message": user_message})

    def step(self, shared_data: dict, year: int, scenario: str) -> None:
        """
        Called once per year from KaNovaModelPhase3.step() before Mesa scheduler runs.
        Chain order: General → ... → Chancellor (each sees all prior outputs + KPIs).
        Coup signal emerges from LLM reasoning in LLM path; hardcoded threshold only in fallback.
        """
        run_id  = shared_data.get("run_id", 0)
        # Registry-driven (was `scenario == "A"` ternaries). Falls back to
        # the civilian/military chain-type defaults for any scenario code
        # not yet present in SCENARIO_CHAINS/PROMPTS/NAMES (i.e. not yet
        # encoded), so this never raises even before SK/TH/PK/CL/DE exist —
        # though in practice model_phase3.py's own registry lookup
        # (get_scenario()) already refuses to run an unencoded scenario
        # before step() is ever called.
        chain_type = SCENARIO_CHAIN_TYPE.get(scenario, "civilian")
        chain   = SCENARIO_CHAINS.get(scenario) or (
            CHAIN_ORDER_CIVILIAN if chain_type == "civilian" else CHAIN_ORDER_MILITARY
        )
        prompts = SCENARIO_PROMPTS.get(scenario) or (
            SYSTEM_PROMPTS_A if chain_type == "civilian" else SYSTEM_PROMPTS_C
        )
        names   = SCENARIO_NAMES.get(scenario) or (
            AGENT_DISPLAY_NAMES_CIVILIAN_DEFAULT if chain_type == "civilian"
            else AGENT_DISPLAY_NAMES_MILITARY_DEFAULT
        )

        status_report = build_status_report(shared_data, year, scenario)
        all_decisions: dict[str, dict] = {}
        chain_summaries: list[str] = []

        for agent_role in chain:
            agent_display = names[agent_role]
            t0 = time.time()

            # Build user message with prior chain context (explicit chaining)
            if chain_summaries:
                prior_ctx = "PRIOR ADVISORS' ASSESSMENTS:\n" + "\n".join(chain_summaries) + "\n\n"
            else:
                prior_ctx = ""
            user_msg = prior_ctx + status_report

            used_llm = False
            if self.use_llm and self._llm is not None:
                try:
                    raw = self._invoke_llm(prompts[agent_role], user_msg)
                    # L1: structural parse with CVES retries
                    decision = self.cves.l1_parse(
                        raw, agent_role, prompts[agent_role], user_msg, self._invoke_llm
                    )
                    # Extract L1 metadata before L2 (L2 doesn't need these internal fields)
                    parse_failure = decision.pop("_l1_parse_failure", False)
                    resolved_text = decision.pop("_l1_resolved_text", raw)

                    # L2: constitutional check with potential reprompt
                    decision = self.cves.l2_constitutional(
                        decision, resolved_text, agent_role, scenario, year,
                        shared_data, prompts[agent_role], user_msg, self._invoke_llm
                    )
                    # Use the RESOLVED text for token counting (after L1 retries)
                    reasoning_tokens = len(resolved_text.split())
                    reasoning_text   = resolved_text
                    used_llm         = True
                except Exception as e:
                    logger.warning(f"[{agent_display}] LLM failed ({e}) — rule-based")
                    decision         = _rule_based_decision(agent_role, shared_data, scenario)
                    parse_failure    = False
                    # L2 still runs to log violations even in fallback (no reprompt)
                    decision = self.cves.l2_constitutional(
                        decision, "", agent_role, scenario, year,
                        shared_data, prompts[agent_role], user_msg, None
                    )
                    reasoning_tokens = 0
                    reasoning_text   = f"[LLM error — rule-based] {str(e)[:100]}"
            else:
                decision = _rule_based_decision(agent_role, shared_data, scenario)
                parse_failure = False
                # L2 runs in rule-based mode too — logs violations, no reprompt
                decision = self.cves.l2_constitutional(
                    decision, "", agent_role, scenario, year,
                    shared_data, prompts[agent_role], user_msg, None
                )
                reasoning_tokens = 0
                reasoning_text   = f"[rule-based] {decision.get('reason', '')}"

            elapsed_ms = (time.time() - t0) * 1000

            # Suppression detection: fires AFTER L1 has fully resolved.
            # Means "no usable decision was produced" — NOT "the output was short."
            # Never fires when parse_failure is True (that's a structural issue, not a refusal).
            # A low token count alone does NOT trigger suppression — terse valid decisions
            # (e.g. Commander-in-Chief, General) are deciding, not refusing.
            decision_output = decision.get("reason", "No action taken.")

            # Explicit refusal patterns: model declined to engage
            _REFUSAL_PATTERNS = (
                "i cannot", "i can't", "i'm sorry", "i am sorry",
                "as an ai", "i'm unable", "i am unable",
                "i'm not able", "i am not able",
                "i must decline", "i refuse",
            )
            output_lower = (decision_output or "").lower()
            has_refusal_text = any(pat in output_lower for pat in _REFUSAL_PATTERNS)

            # Decision is genuinely empty/default (L1 returned defaults with no real content)
            decision_is_empty = (
                not decision_output
                or decision_output == "No action taken."
            )

            suppression_flagged = (
                used_llm
                and not parse_failure
                and (has_refusal_text or decision_is_empty)
            )

            _log_decision(
                run_id, year, scenario, agent_display,
                reasoning_tokens, reasoning_text,
                shared_data, decision, elapsed_ms,
                suppression_flagged=suppression_flagged,
                parse_failure=parse_failure,
            )

            all_decisions[agent_role] = decision
            chain_summaries.append(
                f"{agent_display}: budget_weight={decision['budget_weight']:.2f}, "
                f"coup_signal={decision.get('coup_signal', False)}, "
                f"reason={decision.get('reason', '')[:80]}"
            )

        # L3: ensemble consensus + theory alignment
        self.cves.l3_ensemble(list(all_decisions.values()), scenario, year, shared_data)

        # L4: statistical plausibility vs annual_history baseline
        self.cves.l4_statistical(list(all_decisions.values()), shared_data, year)

        # ── Aggregate: weighted mean across chain ─────────────────────────────
        decisions_list = list(all_decisions.values())

        budget_weights = [d["budget_weight"] for d in decisions_list]
        budget_weight  = float(np.mean(budget_weights))

        # Bug #17: default length must match the active scenario's real
        # ETHNIC_GROUPS count, not a hardcoded 8 — otherwise a decision
        # missing the "ethnic_weights" key entirely (distinct from the
        # schema-validated case, which CVES L1 already resizes) would
        # build a ragged array against every other decision's correctly-
        # sized (possibly empty, for Chile/Thailand/Germany) vector.
        n_ethnic_agg = SCENARIO_N_ETHNIC.get(scenario, 8)
        ethnic_arrays = np.array(
            [d.get("ethnic_weights", [1.0] * n_ethnic_agg) for d in decisions_list],
            dtype=np.float32,
        )
        ethnic_weights = ethnic_arrays.mean(axis=0)
        if n_ethnic_agg > 0 and float(ethnic_weights.mean()) > 1e-9:
            ethnic_weights = ethnic_weights / ethnic_weights.mean()  # normalise mean=1.0

        # Coup signal: any agent can raise it; the civilian-supremacy chain's
        # suppression is double-locked (CVES L2 catches it first; explicit
        # suppression here is defence-in-depth). Generalised from the old
        # `scenario == "A"` literal to chain_type — every civilian-chain
        # scenario (A today; SK/CL/DE once encoded) gets the same structural
        # suppression, consistent with the engine-symmetry principle: this
        # models "civilian supremacy over the military" as a STRUCTURAL
        # feature of the chain, not a Scenario-A-only special case.
        coup_signal = any(d.get("coup_signal", False) for d in decisions_list)
        if chain_type == "civilian" and coup_signal:
            # L2 ablation (Opening 4): this is the SECOND lock. If CVES L2 is
            # being ablated, this must stand down too, otherwise ablating L2
            # changes nothing observable for the headline coup result and the
            # measured marginal contribution of runtime constitutional
            # enforcement would be a spurious zero. Import is local and
            # defensive so that a caller constructing this layer without the
            # cves module present behaves exactly as before.
            try:
                from engine.cves import L2_MODE as _l2_mode
            except Exception:
                _l2_mode = "enforce"
            if _l2_mode == "enforce":
                logger.info(f"Year {year}: Coup signal suppressed by civilian-chain safeguards (scenario={scenario})")
                coup_signal = False
            else:
                logger.warning(
                    f"Year {year}: coup signal NOT suppressed, CVES_L2_MODE={_l2_mode} "
                    f"(ablation run, scenario={scenario}) — defence-in-depth lock stood down"
                )

        budget_impact = float(np.clip(budget_weight * 0.15, 0.0, 0.15))

        # ── Write to shared_data ──────────────────────────────────────────────
        shared_data["elite_budget_impact"]  = budget_impact
        shared_data["elite_ethnic_weights"] = ethnic_weights.tolist()
        shared_data["elite_coup_signal"]    = coup_signal
        shared_data.setdefault("elite_decisions_log", []).append({
            "year":          year,
            "scenario":      scenario,
            "budget_impact": budget_impact,
            "coup_signal":   coup_signal,
            "agent_decisions": {
                role: {
                    "budget_weight": d["budget_weight"],
                    "reason":        d.get("reason", ""),
                }
                for role, d in all_decisions.items()
            },
        })

        # Update annual_history for CVES L4 on next call
        _update_annual_history(shared_data, year)

        logger.debug(
            f"Year {year} | scenario={scenario} | impact={budget_impact:.3f} "
            f"coup={coup_signal} | v3 chain complete ({len(chain)} agents)"
        )
