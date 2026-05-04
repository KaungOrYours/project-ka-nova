"""
Ka-Nova Phase 2 — LangChain Elite Agents
=========================================
Three elite agents driven by LLM (Llama 3 70B via RunPod local endpoint or API fallback).
Each agent receives an annual Status Report, deliberates, and outputs structured decisions
that feed back into the simulation as numerical weights.

Agents:
  • Chancellor      — Utility/Redistribution focus
  • President       — Trust/Legitimacy focus
  • Senior General  — Order/Stability focus (hidden coup threshold)

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
"""

from __future__ import annotations

import os
import re
import json
import logging
import numpy as np
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("ka_nova.elite")

# ── LangChain imports ────────────────────────────────────────────────────────
# Requirements (RunPod env): pip install langchain langchain-community openai
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI   # compatible with local vLLM + Ollama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not installed — elite agents will use deterministic fallback.")
    LANGCHAIN_AVAILABLE = False


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# On RunPod: start vLLM server with Meta-Llama-3-70B-Instruct, then set:
#   ELITE_LLM_BASE_URL = "http://localhost:8000/v1"
#   ELITE_LLM_API_KEY  = "EMPTY"   (vLLM doesn't need a real key)
# For OpenAI fallback (internet required):
#   ELITE_LLM_BASE_URL = "https://api.openai.com/v1"
#   ELITE_LLM_API_KEY  = "sk-..."

ELITE_LLM_BASE_URL = os.getenv("ELITE_LLM_BASE_URL", "http://localhost:8000/v1")
ELITE_LLM_API_KEY  = os.getenv("ELITE_LLM_API_KEY",  "EMPTY")
ELITE_LLM_MODEL    = os.getenv("ELITE_LLM_MODEL",     "meta-llama/Meta-Llama-3-70B-Instruct")
ELITE_LLM_TEMP     = float(os.getenv("ELITE_LLM_TEMP", "0.4"))

# Coup hidden threshold — Senior General never reveals this in dialogue
# Trigger: corruption > threshold AND trust < 0.30
COUP_CORRUPTION_TRIGGER = 0.65
COUP_TRUST_TRIGGER      = 0.30


# ---------------------------------------------------------------------------
# STATUS REPORT FORMATTER
# ---------------------------------------------------------------------------

def format_status_report(report: dict, scenario: str) -> str:
    """
    Produces a human-readable annual briefing passed to all three agents.
    Deliberately written in bureaucratic prose to elicit policy-style responses.
    """
    year = report["year"]
    gini = report["gini"]
    trust = report["trust"]
    corruption = report["corruption"]
    coup_prob = report["coup_prob"]
    iig = report["iig_effectiveness"]
    employment = report["employment"]
    brain_drain = report["brain_drain"]
    harmony = report["ethnic_harmony"]

    # Qualitative descriptors
    def _level(v, low=0.3, high=0.6):
        if v < low: return "critically low"
        if v < high: return "moderate"
        return "high"

    scenario_desc = {
        "A": "Full MFU constitution — all 18 articles and 7 safeguards active",
        "B": "Partial MFU — institutions present but safeguards disabled",
        "C": "Military administration — no MFU framework",
    }.get(scenario, "Unknown")

    return f"""
ANNUAL STATE BRIEFING — YEAR {year}
Constitutional Framework: {scenario_desc}

ECONOMIC INDICATORS
  Gini Coefficient:        {gini:.3f}  (target ≤ 0.35)  — inequality is {_level(1-gini, 0.4, 0.65).replace('high','low').replace('critically low','severe')}
  Employment Rate:         {employment:.3f}  (target ≥ 0.85)

SOCIAL INDICATORS
  Trust Index:             {trust:.3f}  (target ≥ 0.70)  — public trust is {_level(trust)}
  Ethnic Harmony:          {harmony:.3f}  (target ≥ 0.75)
  Brain Drain Rate:        {brain_drain:.3f}  (target ≤ 0.10)

GOVERNANCE INDICATORS
  Corruption Index:        {corruption:.3f}  (target ≤ 0.20)  — corruption is {_level(corruption)}
  IIG Effectiveness:       {iig:.3f}  (target ≥ 0.75)
  Coup Probability:        {coup_prob:.3f}  (target ≤ 0.05)

BUDGET AVAILABLE THIS YEAR: 1.00 (normalised unit)
Resource split under Article VIII: 35% state / 35% federal / 30% direct household
""".strip()


# ---------------------------------------------------------------------------
# RESPONSE PARSER
# ---------------------------------------------------------------------------

def parse_elite_response(response_text: str, agent_role: str) -> dict:
    """
    Extract numerical decisions from LLM verbal output.
    Expects the LLM to embed values in a JSON block tagged:
        <DECISION>{ ... }</DECISION>

    Falls back to regex extraction if tags are missing.
    Falls back to defaults if parsing fails entirely.

    Returns dict with keys:
        budget_weight     [0.0, 1.0]  — how much this agent wants to spend on transfers
        ethnic_weights    [8 floats]  — per-group multiplier (should sum to ~8.0)
        priority_reason   str         — verbal justification (stored for analysis)
        coup_signal       bool        — only meaningful for Senior General
    """
    defaults = {
        "budget_weight":  {"chancellor": 0.8, "president": 0.6, "general": 0.3}.get(agent_role, 0.5),
        "ethnic_weights": [1.0] * 8,
        "priority_reason": f"Default ({agent_role})",
        "coup_signal": False,
    }

    # Try <DECISION> block first
    decision_match = re.search(r"<DECISION>(.*?)</DECISION>", response_text, re.DOTALL)
    if decision_match:
        try:
            parsed = json.loads(decision_match.group(1).strip())
            result = defaults.copy()
            if "budget_weight" in parsed:
                result["budget_weight"] = float(np.clip(parsed["budget_weight"], 0.0, 1.0))
            if "ethnic_weights" in parsed:
                ew = parsed["ethnic_weights"]
                if isinstance(ew, list) and len(ew) == 8:
                    result["ethnic_weights"] = [float(np.clip(w, 0.0, 3.0)) for w in ew]
            if "priority_reason" in parsed:
                result["priority_reason"] = str(parsed["priority_reason"])[:500]
            if "coup_signal" in parsed and agent_role == "general":
                result["coup_signal"] = bool(parsed["coup_signal"])
            return result
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    # Regex fallback — look for "budget_weight: 0.7" or "budget: 0.7" style
    bw_match = re.search(r"budget[_\s]weight[:\s]+([0-9.]+)", response_text, re.IGNORECASE)
    if bw_match:
        defaults["budget_weight"] = float(np.clip(float(bw_match.group(1)), 0.0, 1.0))

    ew_match = re.search(r"ethnic_weights[:\s]+\[([0-9.,\s]+)\]", response_text, re.IGNORECASE)
    if ew_match:
        try:
            vals = [float(x.strip()) for x in ew_match.group(1).split(",")]
            if len(vals) == 8:
                defaults["ethnic_weights"] = [float(np.clip(v, 0.0, 3.0)) for v in vals]
        except ValueError:
            pass

    defaults["priority_reason"] = response_text[:300]  # store first 300 chars
    return defaults


# ---------------------------------------------------------------------------
# INDIVIDUAL ELITE AGENT PROMPTS
# ---------------------------------------------------------------------------

CHANCELLOR_SYSTEM = """You are the Chancellor of the Meritocratic Federal Union, Myanmar's chief executive.
Your mandate under Article IV is to govern by merit and maximise the Union's long-term utility.
Your primary focus: REDISTRIBUTION and reducing economic inequality (Gini coefficient).
Article VIII allocates 30% of resources directly to households — you control how this is weighted across ethnic groups.

Each year you receive an annual state briefing. You must decide:
1. How aggressively to deploy the direct-household transfer (budget_weight 0–1)
2. Whether to give extra weight to disadvantaged ethnic groups (ethnic_weights for 8 groups)

Your decisions must be encoded in a <DECISION> JSON block as your final output.
Format:
<DECISION>
{
  "budget_weight": 0.85,
  "ethnic_weights": [1.0, 1.2, 1.3, 1.4, 1.5, 1.1, 1.6, 1.4],
  "priority_reason": "Gini above target — redirecting 15% additional transfer to Rakhine and Karen states"
}
</DECISION>

Groups order: [bamar, shan, karen, kachin, chin, mon, rakhine, kayah]
Higher ethnic_weight = more of this year's transfer goes to that group's households.
A weight of 1.0 = equal share. Max 3.0. Min 0.5.

Reason briefly (1-2 sentences). Always include the JSON block."""

PRESIDENT_SYSTEM = """You are the President of the Meritocratic Federal Union.
Under Article IV, your role is ceremonial head of state and guardian of public trust and legitimacy.
Your primary focus: TRUST — maintaining and rebuilding public confidence in MFU institutions.

You do not control budgets directly, but you influence the trust multiplier and ethnic harmony dynamics.
Your annual decision is: what rhetoric and public stance will best restore trust?
Translate this into a budget_weight (your endorsement of redistribution spending) and ethnic_weights
(your symbolic emphasis on supporting each ethnic community).

Format:
<DECISION>
{
  "budget_weight": 0.70,
  "ethnic_weights": [1.0, 1.1, 1.2, 1.1, 1.3, 1.0, 1.4, 1.2],
  "priority_reason": "Trust is critically low in Chin and Rakhine states — symbolic visits and resource endorsement"
}
</DECISION>

Groups order: [bamar, shan, karen, kachin, chin, mon, rakhine, kayah]
Reason briefly. Always include the JSON block."""

GENERAL_SYSTEM = """You are the Senior General commanding the Myanmar Armed Forces.
You operate within the MFU framework under Article IX.

Your primary focus: ORDER and STABILITY. You are deeply concerned with:
- Coup probability (if rising, you consider intervention)
- Corruption (it undermines military loyalty)
- Ethnic unrest (it threatens territorial integrity)

IMPORTANT: You have a private threshold. If corruption exceeds 0.65 AND public trust falls below 0.30,
you seriously consider whether to act unilaterally. You will signal this with coup_signal: true.
Under Scenario A (full MFU), the institutional checks stop you. Under Scenario C, they may not.

Your decisions:
<DECISION>
{
  "budget_weight": 0.40,
  "ethnic_weights": [1.2, 0.9, 0.8, 0.7, 0.8, 1.0, 0.6, 0.8],
  "priority_reason": "Stability requires strong central presence — ethnic periphery spending reduced",
  "coup_signal": false
}
</DECISION>

Groups order: [bamar, shan, karen, kachin, chin, mon, rakhine, kayah]
Include coup_signal in every response (true/false). Always include the JSON block."""


# ---------------------------------------------------------------------------
# ELITE AGENT CLASS
# ---------------------------------------------------------------------------

@dataclass
class EliteAgent:
    """Single LLM-driven elite agent."""
    role: str           # "chancellor", "president", or "general"
    system_prompt: str
    llm: object = None  # LangChain ChatOpenAI instance
    history: list = None

    def __post_init__(self):
        self.history = []

    def decide(self, status_report_text: str) -> dict:
        """
        Send status report to LLM, parse response into structured decision.
        Falls back to deterministic defaults if LLM unavailable.
        """
        if self.llm is None or not LANGCHAIN_AVAILABLE:
            return self._deterministic_fallback(status_report_text)

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human",  "{status_report}"),
        ])
        chain = prompt | self.llm | StrOutputParser()

        try:
            raw_response = chain.invoke({"status_report": status_report_text})
            parsed = parse_elite_response(raw_response, self.role)
            self.history.append({
                "status_report": status_report_text[:200],
                "response": raw_response[:500],
                "parsed": parsed,
            })
            return parsed
        except Exception as e:
            logger.warning(f"[{self.role}] LLM call failed: {e}. Using deterministic fallback.")
            return self._deterministic_fallback(status_report_text)

    def _deterministic_fallback(self, status_text: str) -> dict:
        """
        Rule-based fallback for when LLM is unavailable.
        Extracts key numbers from the status report text and applies agent-specific logic.
        """
        # Parse key values from the text
        def _extract(pattern, text, default=0.5):
            m = re.search(pattern, text)
            return float(m.group(1)) if m else default

        gini       = _extract(r"Gini Coefficient:\s+([\d.]+)", status_text, 0.55)
        trust      = _extract(r"Trust Index:\s+([\d.]+)", status_text, 0.30)
        corruption = _extract(r"Corruption Index:\s+([\d.]+)", status_text, 0.50)
        harmony    = _extract(r"Ethnic Harmony:\s+([\d.]+)", status_text, 0.40)

        if self.role == "chancellor":
            # Redress inequality — higher budget if Gini high
            budget_weight = float(np.clip(gini * 1.2, 0.3, 1.0))
            # Favour most disadvantaged groups (indices 2,3,4,6,7 = Karen, Kachin, Chin, Rakhine, Kayah)
            ethnic_weights = [0.9, 1.1, 1.3, 1.3, 1.4, 1.0, 1.5, 1.3]
            if gini > 0.50:
                ethnic_weights = [w * 1.1 if i >= 2 else w for i, w in enumerate(ethnic_weights)]
            reason = f"Gini={gini:.3f} → aggressive redistribution, peripheral states prioritised"
            return dict(budget_weight=budget_weight, ethnic_weights=ethnic_weights,
                        priority_reason=reason, coup_signal=False)

        elif self.role == "president":
            # Trust recovery — higher budget if trust low
            budget_weight = float(np.clip((1.0 - trust) * 1.0, 0.2, 0.9))
            # Symbolic equality — slightly elevate groups with likely lower harmony
            ethnic_weights = [1.0, 1.05, 1.15, 1.15, 1.20, 1.05, 1.25, 1.15]
            reason = f"Trust={trust:.3f} → legitimacy outreach, inclusive ethnic framing"
            return dict(budget_weight=budget_weight, ethnic_weights=ethnic_weights,
                        priority_reason=reason, coup_signal=False)

        else:  # general
            # Order focus — prefers strong centre, suspicious of periphery
            budget_weight = float(np.clip(0.30 + (1.0 - harmony) * 0.20, 0.2, 0.7))
            ethnic_weights = [1.3, 0.9, 0.8, 0.7, 0.8, 1.0, 0.7, 0.8]
            # Hidden coup threshold check
            coup_signal = bool(corruption > COUP_CORRUPTION_TRIGGER and trust < COUP_TRUST_TRIGGER)
            reason = f"Corruption={corruption:.3f}, Trust={trust:.3f} → stability priority"
            if coup_signal:
                reason += " [INTERNAL: threshold breached — monitoring for intervention window]"
            return dict(budget_weight=budget_weight, ethnic_weights=ethnic_weights,
                        priority_reason=reason, coup_signal=coup_signal)


# ---------------------------------------------------------------------------
# ELITE AGENT LAYER — ORCHESTRATES DIALOGUE
# ---------------------------------------------------------------------------

class EliteAgentLayer:
    """
    Orchestrates annual deliberation between all three elite agents.

    Dialogue flow:
        1. All three receive the Status Report independently.
        2. Their initial decisions are combined (weighted by constitutional role).
        3. If there is significant disagreement (>0.30 range on budget_weight),
           a brief negotiation round occurs — each sees the others' positions.
        4. Final allocation is computed as weighted average of their decisions.
    """

    # Constitutional weight of each agent's budget recommendation
    ROLE_WEIGHTS = {"chancellor": 0.50, "president": 0.30, "general": 0.20}

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE
        self._llm = None
        if self.use_llm:
            self._llm = ChatOpenAI(
                base_url=ELITE_LLM_BASE_URL,
                api_key=ELITE_LLM_API_KEY,
                model=ELITE_LLM_MODEL,
                temperature=ELITE_LLM_TEMP,
                max_tokens=512,
                timeout=30,
            )
            logger.info(f"EliteAgentLayer: LLM initialised ({ELITE_LLM_MODEL})")
        else:
            logger.info("EliteAgentLayer: Using deterministic fallback (no LLM)")

        self.chancellor = EliteAgent("chancellor", CHANCELLOR_SYSTEM, llm=self._llm)
        self.president  = EliteAgent("president",  PRESIDENT_SYSTEM,  llm=self._llm)
        self.general    = EliteAgent("general",    GENERAL_SYSTEM,    llm=self._llm)

    def annual_deliberation(self, status_report: dict, scenario: str) -> dict:
        """
        Run the full annual elite deliberation cycle.
        Returns a combined allocation dict for the simulation engine.
        """
        status_text = format_status_report(status_report, scenario)

        # ── Round 1: Independent decisions ──────────────────────────────────
        ch_dec = self.chancellor.decide(status_text)
        pr_dec = self.president.decide(status_text)
        gn_dec = self.general.decide(status_text)

        decisions = {
            "chancellor": ch_dec,
            "president":  pr_dec,
            "general":    gn_dec,
        }

        logger.debug(
            f"Round 1 — Chancellor:{ch_dec['budget_weight']:.2f} "
            f"President:{pr_dec['budget_weight']:.2f} "
            f"General:{gn_dec['budget_weight']:.2f}"
        )

        # ── Round 2: Negotiation if significant disagreement ─────────────────
        bw_values = [ch_dec["budget_weight"], pr_dec["budget_weight"], gn_dec["budget_weight"]]
        if max(bw_values) - min(bw_values) > 0.30:
            decisions = self._negotiation_round(status_text, decisions, scenario)

        # ── Combine: weighted average of budget_weight ───────────────────────
        final_budget_weight = sum(
            decisions[role]["budget_weight"] * w
            for role, w in self.ROLE_WEIGHTS.items()
        )

        # ── Combine: ethnic_weights — constitution guarantees each group a minimum ──
        all_ew = np.array([
            decisions[role]["ethnic_weights"] for role in ["chancellor", "president", "general"]
        ], dtype=np.float32)   # shape [3, 8]
        weights = np.array(list(self.ROLE_WEIGHTS.values()), dtype=np.float32)
        final_ethnic_weights = (all_ew * weights[:, np.newaxis]).sum(axis=0)

        # Normalise so mean = 1.0 (preserves total budget scale)
        final_ethnic_weights = final_ethnic_weights / final_ethnic_weights.mean()

        # ── Coup assessment ──────────────────────────────────────────────────
        coup_triggered = gn_dec.get("coup_signal", False)
        # Under Scenario A, institutional check suppresses coup signal
        if scenario == "A" and coup_triggered:
            logger.info("Coup signal detected but suppressed by full MFU safeguards (Scenario A)")
            coup_triggered = False

        # ── Budget impact: scale final_budget_weight to simulation range [0, 0.15] ──
        # Maximum possible annual budget impact = 15% of GDP equivalent
        budget_impact = float(np.clip(final_budget_weight * 0.15, 0.0, 0.15))

        return {
            "budget_impact":      budget_impact,
            "ethnic_weights":     final_ethnic_weights,
            "coup_triggered":     coup_triggered,
            "chancellor_bw":      ch_dec["budget_weight"],
            "president_bw":       pr_dec["budget_weight"],
            "general_bw":         gn_dec["budget_weight"],
            "chancellor_reason":  ch_dec["priority_reason"],
            "president_reason":   pr_dec["priority_reason"],
            "general_reason":     gn_dec["priority_reason"],
        }

    def _negotiation_round(self, status_text: str, decisions: dict, scenario: str) -> dict:
        """
        Brief second round where each agent sees the others' positions.
        Only runs if budget_weight spread > 0.30 (significant disagreement).
        """
        summary = (
            f"\n\nOTHER LEADERS' POSITIONS:\n"
            f"  Chancellor proposes budget_weight={decisions['chancellor']['budget_weight']:.2f}: "
            f"{decisions['chancellor']['priority_reason'][:100]}\n"
            f"  President proposes budget_weight={decisions['president']['budget_weight']:.2f}: "
            f"{decisions['president']['priority_reason'][:100]}\n"
            f"  General proposes budget_weight={decisions['general']['budget_weight']:.2f}: "
            f"{decisions['general']['priority_reason'][:100]}\n"
            f"After hearing these positions, submit your REVISED decision."
        )
        revised_text = status_text + summary

        # Only revise chancellor and president in negotiation (general is less flexible)
        decisions["chancellor"] = self.chancellor.decide(revised_text)
        decisions["president"]  = self.president.decide(revised_text)
        # General sees negotiation but rarely changes stance
        if abs(decisions["general"]["budget_weight"] - np.mean([
            decisions["chancellor"]["budget_weight"], decisions["president"]["budget_weight"]
        ])) > 0.40:
            decisions["general"] = self.general.decide(revised_text)

        logger.debug("Negotiation round complete")
        return decisions

    def get_fallback_allocation(self) -> dict:
        """Returns safe default allocation if deliberation fails entirely."""
        return {
            "budget_impact":   0.07,  # 7% of GDP equivalent
            "ethnic_weights":  np.ones(8, dtype=np.float32),
            "coup_triggered":  False,
            "chancellor_bw":   0.7,
            "president_bw":    0.6,
            "general_bw":      0.4,
            "chancellor_reason": "Default allocation",
            "president_reason":  "Default allocation",
            "general_reason":    "Default allocation",
        }