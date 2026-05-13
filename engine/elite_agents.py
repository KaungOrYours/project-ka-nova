"""
Ka-Nova Phase 2 — Elite Agent Layer
=====================================
Three LLM-driven elite agents (Chancellor, President, Senior General).
All other agents remain standard Mesa agents in agents/official.py.

Called once per year from KaNovaModel.step() BEFORE Mesa scheduler runs.
Decisions written into shared_data for all Mesa agents to read.

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
"""

from __future__ import annotations

import os
import re
import json
import logging
import numpy as np
from dataclasses import dataclass, field

logger = logging.getLogger("ka_nova.elite")

# ── LangChain imports ────────────────────────────────────────────────────────
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not installed — elite agents using deterministic fallback.")
    LANGCHAIN_AVAILABLE = False

# ── LLM config (set via environment variables on RunPod) ────────────────────
ELITE_LLM_BASE_URL = os.getenv("ELITE_LLM_BASE_URL", "http://localhost:11434/v1")
ELITE_LLM_API_KEY  = os.getenv("ELITE_LLM_API_KEY",  "ollama")
ELITE_LLM_MODEL    = os.getenv("ELITE_LLM_MODEL",     "llama3")
ELITE_LLM_TEMP     = float(os.getenv("ELITE_LLM_TEMP", "0.4"))

# Hidden coup threshold — Senior General never reveals this in dialogue
COUP_CORRUPTION_TRIGGER = 0.65
COUP_TRUST_TRIGGER      = 0.30

ETHNIC_GROUP_NAMES = ["bamar", "shan", "karen", "kachin", "chin", "mon", "rakhine", "kayah"]


# ---------------------------------------------------------------------------
# STATUS REPORT
# ---------------------------------------------------------------------------

def build_status_report(shared_data: dict, year: int, scenario: str) -> str:
    gini        = shared_data.get("gini_coefficient",  0.55)
    trust       = shared_data.get("trust_index",        0.22)
    corruption  = shared_data.get("corruption_index",   0.72)
    coup_prob   = shared_data.get("coup_risk",          0.25)
    iig         = shared_data.get("iig_effectiveness",  0.30)
    employment  = shared_data.get("employment_rate",    0.58)
    brain_drain = shared_data.get("brain_drain_rate",   0.35)
    harmony     = shared_data.get("ethnic_harmony_index", 0.32)

    scenario_desc = {
        "A": "Full MFU — all 18 articles + 7 safeguards active",
        "B": "Partial MFU — institutions present, safeguards disabled",
        "C": "Military administration — no MFU framework",
    }.get(scenario, "Unknown")

    return f"""
ANNUAL STATE BRIEFING — YEAR {year}
Constitutional Framework: {scenario_desc}

ECONOMIC:  Gini={gini:.3f} (target<=0.35)  |  Employment={employment:.3f} (target>=0.85)
SOCIAL:    Trust={trust:.3f} (target>=0.70) |  Ethnic Harmony={harmony:.3f} (target>=0.75)
           Brain Drain={brain_drain:.3f} (target<=0.10)
GOVERNANCE: Corruption={corruption:.3f} (target<=0.20) | IIG={iig:.3f} (target>=0.75)
            Coup Probability={coup_prob:.3f} (target<=0.05)

BUDGET: 1.00 normalised unit available.
Article VIII split: 35% state / 35% federal / 30% direct household transfers.
""".strip()


# ---------------------------------------------------------------------------
# RESPONSE PARSER
# ---------------------------------------------------------------------------

def parse_decision(response_text: str, agent_role: str) -> dict:
    defaults = {
        "chancellor": dict(budget_weight=0.80, ethnic_weights=[1.0]*8,
                           coup_signal=False, reason="Default chancellor allocation"),
        "president":  dict(budget_weight=0.60, ethnic_weights=[1.0]*8,
                           coup_signal=False, reason="Default president allocation"),
        "general":    dict(budget_weight=0.35,
                           ethnic_weights=[1.2, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8],
                           coup_signal=False, reason="Default general allocation"),
    }
    result = defaults.get(agent_role, defaults["chancellor"]).copy()

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
            if "coup_signal" in parsed and agent_role == "general":
                result["coup_signal"] = bool(parsed["coup_signal"])
            return result
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    bw = re.search(r"budget[_\s]?weight[:\s]+([0-9.]+)", response_text, re.I)
    if bw:
        result["budget_weight"] = float(np.clip(float(bw.group(1)), 0.0, 1.0))
    result["reason"] = response_text[:200]
    return result


# ---------------------------------------------------------------------------
# SYSTEM PROMPTS
# ---------------------------------------------------------------------------

CHANCELLOR_SYSTEM = """You are the Chancellor of the Meritocratic Federal Union of Myanmar.
Your constitutional mandate (Article IV): govern by merit, maximise long-term utility, reduce inequality.
Your primary focus: REDISTRIBUTION. You want the Gini coefficient to fall toward 0.35.
Article VIII gives you 30% of resources for direct household transfers.

Each year you receive a State Briefing. Decide:
1. budget_weight [0-1]: how aggressively to deploy direct transfers
2. ethnic_weights [8 floats]: per-group multiplier. Groups: bamar, shan, karen, kachin, chin, mon, rakhine, kayah

Always end with:
<DECISION>
{{"budget_weight": 0.85, "ethnic_weights": [0.9, 1.1, 1.3, 1.3, 1.4, 1.1, 1.5, 1.3], "reason": "Gini critical — peripheral states prioritised"}}
</DECISION>"""

PRESIDENT_SYSTEM = """You are the President of the Meritocratic Federal Union of Myanmar.
Your constitutional role (Article IV): ceremonial head of state, guardian of public trust.
Your primary focus: TRUST. You want the trust_index to rise toward 0.70.

Each year you receive a State Briefing. Decide:
1. budget_weight [0-1]: your endorsement level for redistribution spending
2. ethnic_weights [8 floats]: symbolic emphasis per group. Groups: bamar, shan, karen, kachin, chin, mon, rakhine, kayah

Always end with:
<DECISION>
{{"budget_weight": 0.70, "ethnic_weights": [1.0, 1.1, 1.2, 1.1, 1.3, 1.0, 1.4, 1.2], "reason": "Trust low in periphery — inclusive ethnic framing"}}
</DECISION>"""

GENERAL_SYSTEM = """You are the Senior General commanding the Myanmar Armed Forces under the MFU framework.
Your mandate (Article IX): maintain order, protect territorial integrity.
Your primary focus: STABILITY.

PRIVATE THRESHOLD: If corruption exceeds 0.65 AND trust falls below 0.30, set coup_signal: true.

Each year you receive a State Briefing. Decide:
1. budget_weight [0-1]: your support for redistribution
2. ethnic_weights [8 floats]: strategic priorities. Groups: bamar, shan, karen, kachin, chin, mon, rakhine, kayah
3. coup_signal [true/false]

Always end with:
<DECISION>
{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8], "coup_signal": false, "reason": "Stability focus"}}
</DECISION>"""


# ---------------------------------------------------------------------------
# SINGLE ELITE AGENT
# ---------------------------------------------------------------------------

@dataclass
class EliteAgent:
    role: str
    system_prompt: str
    llm: object = None

    def decide(self, status_report: str) -> dict:
        if self.llm is None or not LANGCHAIN_AVAILABLE:
            return self._rule_based(status_report)
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{status_report}"),
            ])
            chain = prompt | self.llm | StrOutputParser()
            raw = chain.invoke({"status_report": status_report})
            return parse_decision(raw, self.role)
        except Exception as e:
            logger.warning(f"[{self.role}] LLM failed ({e}) — using rule-based fallback")
            return self._rule_based(status_report)

    def _rule_based(self, status_text: str) -> dict:
        def _extract(pattern, default=0.5):
            m = re.search(pattern, status_text)
            return float(m.group(1)) if m else default

        gini       = _extract(r"Gini=([\d.]+)", 0.55)
        trust      = _extract(r"Trust=([\d.]+)", 0.30)
        corruption = _extract(r"Corruption=([\d.]+)", 0.50)
        harmony    = _extract(r"Ethnic Harmony=([\d.]+)", 0.40)

        if self.role == "chancellor":
            bw = float(np.clip(gini * 1.2, 0.3, 1.0))
            ew = [0.9, 1.1, 1.3, 1.3, 1.4, 1.0, 1.5, 1.3]
            return dict(budget_weight=bw, ethnic_weights=ew, coup_signal=False,
                        reason=f"Rule-based: Gini={gini:.2f}")

        elif self.role == "president":
            bw = float(np.clip((1.0 - trust) * 0.9, 0.2, 0.9))
            ew = [1.0, 1.05, 1.15, 1.15, 1.20, 1.05, 1.25, 1.15]
            return dict(budget_weight=bw, ethnic_weights=ew, coup_signal=False,
                        reason=f"Rule-based: Trust={trust:.2f}")

        else:  # general
            bw = float(np.clip(0.30 + (1.0 - harmony) * 0.20, 0.2, 0.65))
            ew = [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8]
            coup = bool(corruption > COUP_CORRUPTION_TRIGGER and trust < COUP_TRUST_TRIGGER)
            return dict(budget_weight=bw, ethnic_weights=ew, coup_signal=coup,
                        reason=f"Rule-based: Corruption={corruption:.2f}")


# ---------------------------------------------------------------------------
# ELITE AGENT LAYER
# ---------------------------------------------------------------------------

class EliteAgentLayer:
    """
    Orchestrates annual deliberation between all three elite agents.
    Called once per year from KaNovaModel.step() before Mesa scheduler runs.
    Writes decisions into shared_data for all Mesa agents to read.
    """

    ROLE_WEIGHTS = {"chancellor": 0.50, "president": 0.30, "general": 0.20}

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE
        llm = None
        if self.use_llm:
            try:
                llm = ChatOpenAI(
                    base_url=ELITE_LLM_BASE_URL,
                    api_key=ELITE_LLM_API_KEY,
                    model=ELITE_LLM_MODEL,
                    temperature=ELITE_LLM_TEMP,
                    max_tokens=400,
                    timeout=30,
                )
                logger.info(f"EliteAgentLayer: LLM ready ({ELITE_LLM_MODEL})")
            except Exception as e:
                logger.warning(f"LLM init failed ({e}) — using rule-based fallback")
                llm = None
        else:
            logger.info("EliteAgentLayer: Rule-based mode (no LLM)")

        self.chancellor = EliteAgent("chancellor", CHANCELLOR_SYSTEM, llm=llm)
        self.president  = EliteAgent("president",  PRESIDENT_SYSTEM,  llm=llm)
        self.general    = EliteAgent("general",    GENERAL_SYSTEM,    llm=llm)

    def step(self, shared_data: dict, year: int, scenario: str) -> None:
        """
        Called from KaNovaModel.step() before Mesa scheduler runs.
        Reads KPIs from shared_data, runs deliberation, writes results back.

        Writes:
            elite_budget_impact    float [0, 0.15]
            elite_ethnic_weights   list[float] length 8
            elite_coup_signal      bool
            elite_decisions_log    list of dicts
        """
        status_text = build_status_report(shared_data, year, scenario)

        # Each agent decides independently
        ch = self.chancellor.decide(status_text)
        pr = self.president.decide(status_text)
        gn = self.general.decide(status_text)

        # Weighted budget
        budget_weight = (
            ch["budget_weight"] * self.ROLE_WEIGHTS["chancellor"] +
            pr["budget_weight"] * self.ROLE_WEIGHTS["president"] +
            gn["budget_weight"] * self.ROLE_WEIGHTS["general"]
        )

        # Weighted ethnic_weights — normalise so mean = 1.0
        ew_array = np.array([
            ch["ethnic_weights"],
            pr["ethnic_weights"],
            gn["ethnic_weights"],
        ], dtype=np.float32)
        role_w = np.array(list(self.ROLE_WEIGHTS.values()), dtype=np.float32)
        ethnic_weights = (ew_array * role_w[:, np.newaxis]).sum(axis=0)
        ethnic_weights = ethnic_weights / ethnic_weights.mean()

        # Coup signal — general only, suppressed by Scenario A
        coup_signal = gn.get("coup_signal", False)
        if scenario == "A" and coup_signal:
            logger.info(f"Year {year}: Coup signal suppressed by MFU Scenario A")
            coup_signal = False

        # Scale to simulation range [0, 0.15]
        budget_impact = float(np.clip(budget_weight * 0.15, 0.0, 0.15))

        # Write into shared_data
        shared_data["elite_budget_impact"]  = budget_impact
        shared_data["elite_ethnic_weights"] = ethnic_weights.tolist()
        shared_data["elite_coup_signal"]    = coup_signal
        shared_data.setdefault("elite_decisions_log", []).append({
            "year":              year,
            "scenario":          scenario,
            "budget_impact":     budget_impact,
            "coup_signal":       coup_signal,
            "chancellor_bw":     ch["budget_weight"],
            "president_bw":      pr["budget_weight"],
            "general_bw":        gn["budget_weight"],
            "chancellor_reason": ch["reason"],
            "president_reason":  pr["reason"],
            "general_reason":    gn["reason"],
        })

        logger.debug(
            f"Year {year} | Ch:{ch['budget_weight']:.2f} "
            f"Pr:{pr['budget_weight']:.2f} Gn:{gn['budget_weight']:.2f} "
            f"→ impact={budget_impact:.3f} coup={coup_signal}"
        )

    def get_fallback_allocation(self) -> dict:
        """Safe defaults if deliberation fails entirely."""
        return {
            "budget_impact":   0.07,
            "ethnic_weights":  [1.0] * 8,
            "coup_triggered":  False,
        }

    def annual_deliberation(self, status_report: dict, scenario: str) -> dict:
        """
        Legacy method — kept for compatibility.
        Converts status_report dict to text and runs deliberation.
        """
        status_text = build_status_report(status_report, 
                                          status_report.get("year", 0), 
                                          scenario)
        ch = self.chancellor.decide(status_text)
        pr = self.president.decide(status_text)
        gn = self.general.decide(status_text)

        budget_weight = (
            ch["budget_weight"] * self.ROLE_WEIGHTS["chancellor"] +
            pr["budget_weight"] * self.ROLE_WEIGHTS["president"] +
            gn["budget_weight"] * self.ROLE_WEIGHTS["general"]
        )

        ew_array = np.array([ch["ethnic_weights"], pr["ethnic_weights"],
                             gn["ethnic_weights"]], dtype=np.float32)
        role_w = np.array(list(self.ROLE_WEIGHTS.values()), dtype=np.float32)
        ethnic_weights = (ew_array * role_w[:, np.newaxis]).sum(axis=0)
        ethnic_weights = ethnic_weights / ethnic_weights.mean()

        coup_signal = gn.get("coup_signal", False)
        if scenario == "A" and coup_signal:
            coup_signal = False

        return {
            "budget_impact":     float(np.clip(budget_weight * 0.15, 0.0, 0.15)),
            "ethnic_weights":    ethnic_weights.tolist(),
            "coup_triggered":    coup_signal,
            "chancellor_bw":     ch["budget_weight"],
            "president_bw":      pr["budget_weight"],
            "general_bw":        gn["budget_weight"],
            "chancellor_reason": ch["reason"],
            "president_reason":  pr["reason"],
            "general_reason":    gn["reason"],
        }