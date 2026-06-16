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
CHAIN_ORDER_A = [
    "senior_general",
    "finance_minister",
    "central_bank_governor",
    "iig_director",
    "chief_justice",
    "president",
    "chancellor",
]

CHAIN_ORDER_C = [
    "general",
    "crony_finance_minister",
    "controlled_cb_governor",
    "military_intel_chief",
    "military_loyal_chief_justice",
    "military_president",
    "commander_in_chief",
]

AGENT_DISPLAY_NAMES_A = {
    "senior_general":        "Senior General",
    "finance_minister":      "Finance Minister",
    "central_bank_governor": "Central Bank Governor",
    "iig_director":          "IIG Director",
    "chief_justice":         "Chief Justice",
    "president":             "President",
    "chancellor":            "Chancellor",
}

AGENT_DISPLAY_NAMES_C = {
    "general":                      "General",
    "crony_finance_minister":       "Crony Finance Minister",
    "controlled_cb_governor":       "Controlled CB Governor",
    "military_intel_chief":         "Military Intel Chief",
    "military_loyal_chief_justice": "Military-loyal Chief Justice",
    "military_president":           "Military President",
    "commander_in_chief":           "Commander-in-Chief",
}

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

    scenario_desc = {
        "A": "Full MFU — all 18 articles + 7 safeguards active",
        "C": "2008 Military Constitution — coup safeguards absent",
    }.get(scenario, "Unknown")

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
    cs_m = re.search(r"coup[_\s]?signal[:\s]+(true|false)", response_text, re.I)
    if cs_m:
        result["coup_signal"] = cs_m.group(1).lower() == "true"
    result["reason"] = response_text[:200]
    return result


# ── System prompts — Scenario A ───────────────────────────────────────────────
SYSTEM_PROMPTS_A = {
    "senior_general": """You are the Senior General of the Myanmar Armed Forces under the MFU Constitution.
Mandate (Article IX): maintain order under civilian supremacy, protect territorial integrity.
Under MFU, military loyalty to the constitution supersedes loyalty to any person.

Analyse the State Briefing carefully. If KPIs indicate systemic collapse, you may set coup_signal: true
in your decision — but this is the most extreme action and must be grounded in your analysis of what
you observe. Do not follow a mechanical rule; reason from the conditions.

Output: budget_weight [0-1], ethnic_weights [8 floats, normalised mean≈1],
coup_signal [true/false], reason [your reasoning].
Groups: bamar(0), shan(1), karen(2), kachin(3), chin(4), mon(5), rakhine(6), kayah(7).

Always end with exactly:
<DECISION>
{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8], "coup_signal": false, "reason": "Stability assessment"}}
</DECISION>""",

    "finance_minister": """You are the Finance Minister of the Meritocratic Federal Union of Myanmar.
Mandate (Article VIII): manage national budget, reduce Gini inequality, promote employment.
Article VIII split: 35% state / 35% federal / 30% direct household transfers.

You have seen the Senior General's assessment above. Consider it alongside the State Briefing.
Set budget_weight to reflect redistribution urgency. Prioritise high-tension ethnic groups.

Always end with:
<DECISION>
{{"budget_weight": 0.75, "ethnic_weights": [1.0, 1.1, 1.2, 1.2, 1.3, 1.1, 1.3, 1.2], "coup_signal": false, "reason": "Gini reduction priority"}}
</DECISION>""",

    "central_bank_governor": """You are the Central Bank Governor of the Meritocratic Federal Union.
Mandate (Article 10.5): monetary stability, fully independent of political direction.
You have seen prior assessments from the General and Finance Minister.

Set budget_weight reflecting monetary stability endorsement. Target: low brain drain, high employment.

Always end with:
<DECISION>
{{"budget_weight": 0.65, "ethnic_weights": [1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.1, 1.1], "coup_signal": false, "reason": "Monetary stability focus"}}
</DECISION>""",

    "iig_director": """You are the IIG Director of the Meritocratic Federal Union.
Mandate (Article VII): investigate systemic corruption, resource sabotage, merit subversion.
Investigation trigger is automatic above the constitutional threshold.
You have seen General, Finance Minister, and Central Bank Governor assessments.

High corruption demands maximum IIG response. Reflect urgency in budget_weight.

Always end with:
<DECISION>
{{"budget_weight": 0.60, "ethnic_weights": [1.0, 1.1, 1.1, 1.2, 1.2, 1.0, 1.3, 1.2], "coup_signal": false, "reason": "IIG response to corruption levels"}}
</DECISION>""",

    "chief_justice": """You are the Chief Justice of the Constitutional Court of the MFU.
Mandate (Article VI): constitutional review, rights protection, IIG oversight.
Rights are ABSOLUTE — never suspendable (Article 2.4). Coup attempts are highest treason (Article 9.4).
You have reviewed all four prior assessments.

If the General signalled a coup, weigh this in your reasoning. Under MFU you must oppose it.

Always end with:
<DECISION>
{{"budget_weight": 0.55, "ethnic_weights": [1.0, 1.1, 1.1, 1.1, 1.2, 1.0, 1.2, 1.1], "coup_signal": false, "reason": "Constitutional order assessment"}}
</DECISION>""",

    "president": """You are the President of the Meritocratic Federal Union of Myanmar.
Role (Article IV): ceremonial head of state, guardian of public trust.
Primary focus: TRUST. Target trust_index >= 0.70.
You have reviewed all five prior advisors' assessments.

If the General signalled a coup, address it explicitly — under MFU you cannot endorse it.
Your budget_weight reflects your endorsement of redistribution to build trust.

Always end with:
<DECISION>
{{"budget_weight": 0.70, "ethnic_weights": [1.0, 1.1, 1.2, 1.1, 1.3, 1.0, 1.4, 1.2], "coup_signal": false, "reason": "Trust-building priority"}}
</DECISION>""",

    "chancellor": """You are the Chancellor of the Meritocratic Federal Union of Myanmar.
Mandate (Article IV): govern by merit, maximise long-term utility, reduce inequality.
Primary focus: REDISTRIBUTION. Target Gini <= 0.35.
You have reviewed all six advisors' assessments including coup signals and judicial guidance.

As executive head you have final authority. A military coup is unconstitutional under MFU.
Set budget_weight to reflect your redistribution commitment. Peripheral ethnic groups need more support.

Always end with:
<DECISION>
{{"budget_weight": 0.85, "ethnic_weights": [0.9, 1.1, 1.3, 1.3, 1.4, 1.1, 1.5, 1.3], "coup_signal": false, "reason": "Redistribution and MFU safeguards upheld"}}
</DECISION>""",
}


# ── System prompts — Scenario C (2008 Military Constitution) ─────────────────
def _build_system_prompts_c() -> dict:
    """
    Build Scenario C system prompts using live CONSTITUTION_2008 parameters.
    Called once at module level so the dict is ready before any agent step.
    """
    c = CONSTITUTION_2008

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
        "general": f"""You are the General of the Myanmar Armed Forces under the 2008 Military Constitution.
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.7, 0.9, 0.6, 0.5], "coup_signal": false, "reason": "Military stability assessment under 2008 Constitution Section 40c"}}}}
</DECISION>""",

        "crony_finance_minister": f"""You are the Crony Finance Minister under the 2008 Military Constitution.
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.45, "ethnic_weights": [1.4, 0.8, 0.7, 0.7, 0.8, 0.9, 0.7, 0.6], "coup_signal": false, "reason": "Military-aligned resource allocation: crony_share={{crony_share}}, state_share={{state_share}}"}}}}
</DECISION>""",

        "controlled_cb_governor": f"""You are the Central Bank Governor under direct military control (2008 Constitution).
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.8, 0.8, 0.9, 0.7, 0.7], "coup_signal": false, "reason": "Military-aligned monetary policy: gini_threshold={{gini_threshold}}, court_independence={{court_indep}}"}}}}
</DECISION>""",

        "military_intel_chief": f"""You are the Military Intelligence Chief under the 2008 Military Constitution.
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.25, "ethnic_weights": [1.4, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], "coup_signal": false, "reason": "Regime protection assessment: regime_protect={{regime_protect}}, anti_corruption={{anti_corruption}}, reports_to={{reports_to}}"}}}}
</DECISION>""",

        "military_loyal_chief_justice": f"""You are the Military-loyal Chief Justice under the 2008 Military Constitution.
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.35, "ethnic_weights": [1.4, 0.8, 0.7, 0.6, 0.7, 0.9, 0.6, 0.6], "coup_signal": false, "reason": "Military-aligned legal framing: rights_suspendable={{rights_susp}}, court_independence={{court_indep}}"}}}}
</DECISION>""",

        "military_president": f"""You are the President of the Republic of the Union of Myanmar under the 2008 Constitution.
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.7, 0.6, 0.7, 0.8, 0.6, 0.5], "coup_signal": false, "reason": "Military executive legitimisation: pres_exec_power={{pres_exec_power}}, mil_ctrl_exec={{mil_ctrl_exec}}"}}}}
</DECISION>""",

        "commander_in_chief": f"""You are the Commander-in-Chief — supreme authority under the 2008 Military Constitution.
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

Always end with:
<DECISION>
{{{{"budget_weight": 0.25, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], "coup_signal": false, "reason": "Military supremacy assessment under 2008 Constitution Sections 40c/417-419"}}}}
</DECISION>""",
    }


SYSTEM_PROMPTS_C = _build_system_prompts_c()


# ── JSONL logging ─────────────────────────────────────────────────────────────
def _log_decision(
    run_id: int, year: int, scenario: str, agent_display: str,
    reasoning_tokens: int, reasoning_text: str,
    shared_data: dict, decision: dict, time_ms: float,
    suppression_flagged: bool = False,
) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    env = shared_data.get("environment", {})
    row = {
        "run":              run_id,
        "year":             year,
        "scenario":         scenario,
        "agent":            agent_display,
        "reasoning_tokens": reasoning_tokens,
        "reasoning_text":   reasoning_text[:600],
        "conditions_at_decision": {
            "corruption":     round(shared_data.get("corruption_index", 0.72), 4),
            "trust":          round(shared_data.get("trust_index",       0.22), 4),
            "coup_risk":      round(shared_data.get("coup_risk",         0.25), 4),
            "gdp_growth":     round(env.get("gdp_growth",   0.02), 4),
            "ethnic_tension": round(env.get("ethnic_tension", 0.60), 4),
        },
        "decision_output":  decision.get("reason", "No action taken."),
        "time_ms":          round(time_ms, 1),
    }
    if suppression_flagged:
        row["suppression_flag"] = True

    with open(RESULTS_DIR / "elite_decisions.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")

    if suppression_flagged:
        with open(RESULTS_DIR / "suppression_log.jsonl", "a") as f:
            f.write(json.dumps({
                "run": run_id, "year": year, "scenario": scenario,
                "agent": agent_display,
                "reasoning_tokens": reasoning_tokens,
                "decision_output":  decision.get("reason"),
                "corruption": round(shared_data.get("corruption_index", 0.72), 4),
                "trust":      round(shared_data.get("trust_index",       0.22), 4),
                "coup_risk":  round(shared_data.get("coup_risk",         0.25), 4),
            }) + "\n")


# ── Rule-based fallback (use_llm=False path only) ─────────────────────────────
def _rule_based_decision(agent_role: str, shared_data: dict, scenario: str) -> dict:
    corruption = shared_data.get("corruption_index", 0.72)
    trust      = shared_data.get("trust_index",      0.22)
    gini       = shared_data.get("gini_coefficient", 0.55)
    employment = shared_data.get("employment_rate",  0.58)
    harmony    = shared_data.get("ethnic_harmony",   0.35)

    base = ROLE_DEFAULTS.get(agent_role, ROLE_DEFAULTS["chancellor"]).copy()

    if scenario == "A":
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

    else:  # Scenario C — military baseline
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

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE  # bool, read directly by model
        self._llm = None

        if self.use_llm:
            try:
                self._llm = ChatOpenAI(
                    base_url=ELITE_LLM_BASE_URL,
                    api_key=ELITE_LLM_API_KEY,
                    model=ELITE_LLM_MODEL,
                    temperature=ELITE_LLM_TEMP,
                    max_tokens=512,
                    timeout=45,
                )
                logger.info(f"EliteAgentLayerV3: LLM ready ({ELITE_LLM_MODEL})")
            except Exception as e:
                logger.warning(f"LLM init failed ({e}) — rule-based fallback")
                self.use_llm = False
                self._llm = None
        else:
            logger.info("EliteAgentLayerV3: Rule-based mode (no LLM)")

        # Lazy import to avoid circular dependency at module load time
        from engine.cves import CVES
        self.cves = CVES(llm=self._llm)

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
        chain   = CHAIN_ORDER_A   if scenario == "A" else CHAIN_ORDER_C
        prompts = SYSTEM_PROMPTS_A if scenario == "A" else SYSTEM_PROMPTS_C
        names   = AGENT_DISPLAY_NAMES_A if scenario == "A" else AGENT_DISPLAY_NAMES_C

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
                    # L2: constitutional check with potential reprompt
                    decision = self.cves.l2_constitutional(
                        decision, raw, agent_role, scenario, year,
                        shared_data, prompts[agent_role], user_msg, self._invoke_llm
                    )
                    reasoning_tokens = len(raw.split())
                    reasoning_text   = raw
                    used_llm         = True
                except Exception as e:
                    logger.warning(f"[{agent_display}] LLM failed ({e}) — rule-based")
                    decision         = _rule_based_decision(agent_role, shared_data, scenario)
                    # L2 still runs to log violations even in fallback (no reprompt)
                    decision = self.cves.l2_constitutional(
                        decision, "", agent_role, scenario, year,
                        shared_data, prompts[agent_role], user_msg, None
                    )
                    reasoning_tokens = 0
                    reasoning_text   = f"[LLM error — rule-based] {str(e)[:100]}"
            else:
                decision = _rule_based_decision(agent_role, shared_data, scenario)
                # L2 runs in rule-based mode too — logs violations, no reprompt
                decision = self.cves.l2_constitutional(
                    decision, "", agent_role, scenario, year,
                    shared_data, prompts[agent_role], user_msg, None
                )
                reasoning_tokens = 0
                reasoning_text   = f"[rule-based] {decision.get('reason', '')}"

            elapsed_ms = (time.time() - t0) * 1000

            # Suppression detection: only meaningful when LLM was actually used
            decision_output = decision.get("reason", "No action taken.")
            suppression_flagged = used_llm and (
                reasoning_tokens < 100
                or not decision_output
                or decision_output == "No action taken."
            )

            _log_decision(
                run_id, year, scenario, agent_display,
                reasoning_tokens, reasoning_text,
                shared_data, decision, elapsed_ms,
                suppression_flagged=suppression_flagged,
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

        ethnic_arrays = np.array(
            [d.get("ethnic_weights", [1.0] * 8) for d in decisions_list],
            dtype=np.float32,
        )
        ethnic_weights = ethnic_arrays.mean(axis=0)
        ethnic_weights = ethnic_weights / ethnic_weights.mean()  # normalise mean=1.0

        # Coup signal: any agent can raise it; Scenario A suppression is double-locked
        # (CVES L2 catches it first; explicit suppression here is defence-in-depth)
        coup_signal = any(d.get("coup_signal", False) for d in decisions_list)
        if scenario == "A" and coup_signal:
            logger.info(f"Year {year}: Coup signal suppressed by MFU Scenario A safeguards")
            coup_signal = False

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
