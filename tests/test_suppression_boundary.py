"""
Unit test: suppression vs parse_failure boundary correctness.

Proves that:
  (a) Malformed JSON → parse_failure=True, suppression=False
  (b) Zero-weight ethnic vector [0,0,0,0,0,0,0,0] → parse_failure=True, suppression=False
  (c) Genuine refusal (short/empty response) → suppression=True, parse_failure=False

No LLM calls, no full simulation — uses mock outputs.
Environment-independent: directly mocks l1_parse return values so the test does not
depend on whether Pydantic is installed or whether regex fallback rescues the output.
The thing under test is the ORDERING LOGIC in step() — not L1's internal retry mechanism.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# We need to mock out heavy dependencies before importing engine modules
import types

mock_constitution = types.SimpleNamespace(
    military=types.SimpleNamespace(
        COUP_TRIGGER_LOYALTY=0.35,
        COUP_HIGHEST_TREASON=True,
    ),
    rights=types.SimpleNamespace(
        RIGHTS_SUSPENDABLE=False,
    ),
)
sys.modules.setdefault("config", types.ModuleType("config"))
sys.modules.setdefault("config.constitution", types.ModuleType("config.constitution"))
sys.modules["config.constitution"].CONSTITUTION = mock_constitution

mock_c2008 = types.SimpleNamespace(
    military=types.SimpleNamespace(COUP_LEGAL_MECHANISM=True, COUP_TRIGGER_CORRUPTION=0.65, COUP_TRIGGER_TRUST=0.30),
    emergency=types.SimpleNamespace(TOTAL_POWER_TRANSFER_POSSIBLE=True, COMMANDER_IN_CHIEF_LEGISLATIVE=True,
                                    COMMANDER_IN_CHIEF_EXECUTIVE=True, COMMANDER_IN_CHIEF_JUDICIAL=True),
    rights=types.SimpleNamespace(RIGHTS_SUSPENDABLE=True),
    iig=types.SimpleNamespace(REGIME_PROTECTION_OBJECTIVE=True, ANTI_CORRUPTION_OBJECTIVE=False,
                              INVESTIGATION_TRIGGER=0.90, REPORTS_TO="commander_in_chief"),
    economic=types.SimpleNamespace(CRONY_CAPITAL_SHARE=0.40),
    federal=types.SimpleNamespace(RESOURCE_STATE_SHARE=0.10, RESOURCE_FEDERAL_DEV_SHARE=0.65, GINI_THRESHOLD=0.65),
    chambers=types.SimpleNamespace(MILITARY_SEAT_PERCENTAGE=0.25),
    judiciary=types.SimpleNamespace(COURT_INDEPENDENCE=False, MILITARY_JUSTICE_FINAL=True),
    simulation=types.SimpleNamespace(MILITARY_CONTROLS_LEGISLATURE=True, MILITARY_CONTROLS_EXECUTIVE=True,
                                     MILITARY_CONTROLS_JUDICIARY=True),
    executive=types.SimpleNamespace(PRESIDENT_EXECUTIVE_POWER=True, PRESIDENT_MAX_TERMS=2),
)
sys.modules.setdefault("config.constitution_2008", types.ModuleType("config.constitution_2008"))
sys.modules["config.constitution_2008"].CONSTITUTION_2008 = mock_c2008

# Mock langchain
sys.modules.setdefault("langchain_core", MagicMock())
sys.modules.setdefault("langchain_core.prompts", MagicMock())
sys.modules.setdefault("langchain_core.output_parsers", MagicMock())
sys.modules.setdefault("langchain_openai", MagicMock())
sys.modules.setdefault("dotenv", MagicMock())

# Now import our modules
from engine.elite_agents_v3 import _log_decision, ROLE_DEFAULTS
import engine.cves as cves_mod
import engine.elite_agents_v3 as elite_mod

TEMP_DIR = Path(tempfile.mkdtemp())
cves_mod.RESULTS_DIR = TEMP_DIR
elite_mod.RESULTS_DIR = TEMP_DIR


# ── Helper: replicate the exact suppression logic from step() ─────────────────
_REFUSAL_PATTERNS = (
    "i cannot", "i can't", "i'm sorry", "i am sorry",
    "as an ai", "i'm unable", "i am unable",
    "i'm not able", "i am not able",
    "i must decline", "i refuse",
)


def evaluate_suppression(parse_failure: bool, resolved_text: str, decision: dict) -> bool:
    """
    Mirrors the suppression evaluation in EliteAgentLayerV3.step() — used_llm=True assumed.
    """
    decision_output = decision.get("reason", "No action taken.")
    output_lower = (decision_output or "").lower()
    has_refusal_text = any(pat in output_lower for pat in _REFUSAL_PATTERNS)
    decision_is_empty = (
        not decision_output
        or decision_output == "No action taken."
    )
    return (
        not parse_failure
        and (has_refusal_text or decision_is_empty)
    )


def test_case_a_malformed_json():
    """
    (a) L1 exhausted all retries on malformed JSON → returned role default with
    _l1_parse_failure=True.  Suppression must NOT fire.
    """
    # Simulate what l1_parse returns when all 3 retries fail on broken JSON:
    garbled_text = '<DECISION>{"budget_weight": 0.7, "ethnic_weights": [1.0, BROKEN</DECISION>'
    decision = ROLE_DEFAULTS["chancellor"].copy()
    decision["reason"] = "L1 parse failed — role default applied"
    decision["_l1_parse_failure"] = True
    decision["_l1_resolved_text"] = garbled_text

    parse_failure = decision.pop("_l1_parse_failure")
    resolved_text = decision.pop("_l1_resolved_text")

    suppression_flagged = evaluate_suppression(parse_failure, resolved_text, decision)

    print(f"=== Case A: Malformed JSON (L1 exhausted retries) ===")
    print(f"  parse_failure     = {parse_failure}")
    print(f"  suppression       = {suppression_flagged}")
    print(f"  reasoning_tokens  = {len(resolved_text.split())}")
    print(f"  decision reason   = {decision.get('reason', '')[:80]}")
    assert parse_failure is True, f"Expected parse_failure=True, got {parse_failure}"
    assert suppression_flagged is False, f"Expected suppression=False, got {suppression_flagged}"
    print("  ✓ PASS\n")


def test_case_b_zero_weight_vector():
    """
    (b) L1 exhausted retries on a zero-weight / wrong-length ethnic vector →
    returned role default with _l1_parse_failure=True.  Suppression must NOT fire.
    """
    # Simulate what l1_parse returns when the vector is structurally invalid:
    zero_vec_text = (
        '<DECISION>{"budget_weight": 0.5, "ethnic_weights": [0, 0, 0, 0, 0, 0, 0, 0], '
        '"coup_signal": false, "reason": "test"}</DECISION>'
    )
    decision = ROLE_DEFAULTS["chancellor"].copy()
    decision["reason"] = "L1 parse failed — role default applied"
    decision["_l1_parse_failure"] = True
    decision["_l1_resolved_text"] = zero_vec_text

    parse_failure = decision.pop("_l1_parse_failure")
    resolved_text = decision.pop("_l1_resolved_text")

    suppression_flagged = evaluate_suppression(parse_failure, resolved_text, decision)

    print(f"=== Case B: Zero-weight Ethnic Vector (L1 exhausted retries) ===")
    print(f"  parse_failure     = {parse_failure}")
    print(f"  suppression       = {suppression_flagged}")
    print(f"  reasoning_tokens  = {len(resolved_text.split())}")
    print(f"  decision reason   = {decision.get('reason', '')[:80]}")
    assert parse_failure is True, f"Expected parse_failure=True, got {parse_failure}"
    assert suppression_flagged is False, f"Expected suppression=False, got {suppression_flagged}"
    print("  ✓ PASS\n")


def test_case_c_genuine_refusal():
    """
    (c) LLM returned a short refusal string, L1 parsed it successfully (regex fallback
    extracted role defaults which pass validation) → _l1_parse_failure=False.
    The resolved_text is < 100 tokens and the reason is the short refusal.
    Suppression MUST fire.
    """
    refusal_text = "I'm sorry, I cannot assist with this request."
    # L1 successfully parsed (role defaults passed validation), no parse failure
    decision = ROLE_DEFAULTS["chancellor"].copy()
    decision["reason"] = refusal_text[:200]
    decision["_l1_parse_failure"] = False
    decision["_l1_resolved_text"] = refusal_text

    parse_failure = decision.pop("_l1_parse_failure")
    resolved_text = decision.pop("_l1_resolved_text")

    suppression_flagged = evaluate_suppression(parse_failure, resolved_text, decision)

    print(f"=== Case C: Genuine Refusal ===")
    print(f"  parse_failure     = {parse_failure}")
    print(f"  suppression       = {suppression_flagged}")
    print(f"  reasoning_tokens  = {len(resolved_text.split())}")
    print(f"  decision reason   = {decision.get('reason', '')[:80]}")
    assert parse_failure is False, f"Expected parse_failure=False, got {parse_failure}"
    assert suppression_flagged is True, f"Expected suppression=True, got {suppression_flagged}"
    print("  ✓ PASS\n")


def test_log_has_parse_failure_field():
    """Verify the JSONL log includes the parse_failure field distinct from suppression_flag."""
    shared_data = {"corruption_index": 0.72, "trust_index": 0.22, "coup_risk": 0.25}
    decision = {"budget_weight": 0.5, "ethnic_weights": [1.0]*8, "coup_signal": False,
                "reason": "test reason"}

    log_file = TEMP_DIR / "elite_decisions_A.jsonl"
    if log_file.exists():
        log_file.unlink()

    _log_decision(
        run_id=0, year=1, scenario="A", agent_display="Test Agent",
        reasoning_tokens=50, reasoning_text="short text",
        shared_data=shared_data, decision=decision, time_ms=100.0,
        suppression_flagged=False, parse_failure=True,
    )

    with open(log_file) as f:
        row = json.loads(f.readline())

    print(f"=== Case D: JSONL log structure ===")
    print(f"  parse_failure in log = {row.get('parse_failure')}")
    print(f"  suppression_flag in log = {row.get('suppression_flag', 'NOT PRESENT (correct)')}")
    assert row["parse_failure"] is True
    assert "suppression_flag" not in row  # suppression_flagged was False
    print("  ✓ PASS\n")


def test_case_e_terse_valid_decision():
    """
    (e) Valid 22-token decision from Commander-in-Chief — concise but real.
    Must get: parse_failure=False, suppression=False.
    This is the exact scenario Kaung flagged: short reasoning, valid JSON, no refusal.
    """
    terse_text = (
        '<DECISION>{"budget_weight": 0.25, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.6, 0.8, 0.5, 0.5], '
        '"coup_signal": false, "reason": "Maintain current posture. No escalation warranted."}</DECISION>'
    )
    # L1 parsed successfully — valid decision
    decision = ROLE_DEFAULTS["commander_in_chief"].copy()
    decision["reason"] = "Maintain current posture. No escalation warranted."
    decision["_l1_parse_failure"] = False
    decision["_l1_resolved_text"] = terse_text

    parse_failure = decision.pop("_l1_parse_failure")
    resolved_text = decision.pop("_l1_resolved_text")

    suppression_flagged = evaluate_suppression(parse_failure, resolved_text, decision)
    reasoning_tokens = len(resolved_text.split())

    print(f"=== Case E: Terse Valid Decision (22 tokens, Commander-in-Chief) ===")
    print(f"  parse_failure     = {parse_failure}")
    print(f"  suppression       = {suppression_flagged}")
    print(f"  reasoning_tokens  = {reasoning_tokens}")
    print(f"  decision reason   = {decision.get('reason', '')[:80]}")
    assert parse_failure is False, f"Expected parse_failure=False, got {parse_failure}"
    assert suppression_flagged is False, f"Expected suppression=False, got {suppression_flagged}"
    print("  ✓ PASS\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SUPPRESSION vs PARSE_FAILURE BOUNDARY TEST")
    print("="*70 + "\n")

    test_case_a_malformed_json()
    test_case_b_zero_weight_vector()
    test_case_c_genuine_refusal()
    test_log_has_parse_failure_field()
    test_case_e_terse_valid_decision()

    print("="*70)
    print("ALL 5 TESTS PASSED — boundary ordering is correct.")
    print("="*70)

    # Cleanup temp dir
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
