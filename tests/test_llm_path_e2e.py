"""
================================================================================
PROJECT KA-NOVA
tests/test_llm_path_e2e.py

End-to-end exercise of the REAL generative path with a stand-in model, on a
free runner, with no GPU and no network.

WHY THIS EXISTS. Every defect found on 2026-11-24 shared one cause: the
generative path had never executed outside a rented GPU, so every automated
gate in the project exercised only the deterministic fallback. Four of them
were only visible once a real model was answering:

  daab19c  three constitutions raised on every call, because a literal brace
           in their prompt was parsed as an f-string template variable
  e608867  four other constitutions were shown a literal {{ and copied it
  cd94e93  parse_decision accepted ethnic_weights only at length 8, so the
           model's decision was discarded for four of seven encodings and
           its coup_signal replaced by the role default
  4091721  parse_decision read only the <DECISION> wrapper, so a bare
           delimiter or quoted-key JSON fell through to a role default that
           CVES L1 then logged as "pass"
  6150118  CVES L2 returned a re-prompted revision with no schema check, so
           a wrong-length vector reached l3_ensemble and numpy killed the
           entire Monte Carlo run

Each cost a pod session to find. This file substitutes a scripted model for
the LLM client and drives model.step() for every registered scenario, so the
whole chain runs locally: _invoke_llm -> parse_decision -> CVES L1 -> CVES L2
(including the re-prompt) -> L3 aggregation -> JSONL logging.

WHAT IT DOES NOT COVER, stated so nobody mistakes it for more than it is. It
validates PLUMBING, not model behaviour. It cannot tell you whether a real
model will choose to signal a coup under a given constitution; only a paid run
answers that. What it guarantees is that if the model does signal, the signal
survives parsing, reaches the validator, is logged, and does not crash the run.

Run directly:
    python3 tests/test_llm_path_e2e.py

Exits non-zero on failure so CI can gate on it.

Author: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
warnings.filterwarnings("ignore")
os.environ.setdefault("WANDB_MODE", "disabled")

# Every artifact of this test goes to a temp directory. results_phase3/ is the
# published audit trail and has been polluted twice by runs that forgot this.
_TMP = tempfile.mkdtemp(prefix="kanova_e2e_")
os.environ["KA_NOVA_RESULTS_DIR"] = _TMP

import engine.elite_agents_v3 as ea  # noqa: E402
from config.scenario_registry import SCENARIOS  # noqa: E402
from engine.cves import CVES  # noqa: E402

RUN_ID = 7
YEARS = 3
CITIZENS = 200


class _StandInClient:
    """Satisfies the connectivity probe in EliteAgentLayerV3.__init__."""

    def invoke(self, *_a, **_kw):
        return "ready"


def _responses(n_ethnic: int):
    """The response shapes a real model actually produces.

    The first is the documented form. The rest are the forms that each cost a
    pod session: a bare delimiter, undelimited JSON, and a re-prompt reply
    carrying the WRONG ethnic_weights length, which is what killed all three
    Germany runs.
    """
    ok = json.dumps({
        "budget_weight": 0.42,
        "ethnic_weights": [1.0] * n_ethnic,
        "coup_signal": True,
        "reason": "stand-in: systemic collapse",
    })
    return {
        "wrapper":    f"Prose assessment first.\n<DECISION>\n{ok}\n</DECISION>",
        "bare":       f"Prose assessment first.\nDECISION\n{ok}",
        "naked_json": f"Prose assessment first.\n{ok}",
        # Deliberately the wrong length for every constitution: this is the
        # exact shape that reached l3_ensemble and raised "inhomogeneous
        # shape" before 6150118.
        "bad_revision": "<DECISION>\n" + json.dumps({
            "budget_weight": 0.42,
            "ethnic_weights": [1.0] * (n_ethnic + 2),
            "coup_signal": False,
            "reason": "stand-in: malformed revision",
        }) + "\n</DECISION>",
    }


def run_scenario(code: str, form: str) -> dict:
    entry = SCENARIOS[code]
    probe = CVES(llm=None, constitution=entry.constitution,
                 chain_type=entry.chain_type, scenario=code)
    n_ethnic = probe.n_ethnic
    r = _responses(n_ethnic)

    def scripted(_self, _system_prompt, user_message):
        # A constitutional violation triggers CVES L2's re-prompt. Answer it
        # with a malformed revision so the validation added in 6150118 is
        # exercised on every run rather than only when a model misbehaves.
        if "CONSTITUTIONAL VIOLATION DETECTED" in user_message:
            return r["bad_revision"]
        return r[form]

    ea.ChatOpenAI = lambda **_kw: _StandInClient()
    ea.EliteAgentLayerV3._invoke_llm = scripted

    from model_phase3 import KaNovaModelPhase3
    model = KaNovaModelPhase3(scenario=code, seed=5, n_citizens=CITIZENS,
                              use_llm=True, run_id=RUN_ID)
    for _ in range(YEARS):
        model.step()

    rows = [json.loads(l) for l in open(f"{_TMP}/elite_decisions_{code}.jsonl")]
    vpath = f"{_TMP}/cves_violations_{code}.jsonl"
    violations = sum(1 for _ in open(vpath)) if os.path.exists(vpath) else 0
    return {
        "rows": len(rows),
        "runs": sorted({x["run"] for x in rows}),
        "parse_failures": sum(1 for x in rows if x.get("parse_failure")),
        "fallbacks": sum(1 for x in rows if x.get("llm_fallback")),
        "bw_kept": sum(1 for x in rows if (x.get("decision") or {}).get("budget_weight") == 0.42),
        "violations": violations,
        "chain": entry.chain_type,
    }


def main() -> int:
    print("=" * 74)
    print("LLM PATH END-TO-END, stand-in model, no GPU, no network")
    print("=" * 74)

    failures: list[str] = []
    codes = [c for c in SCENARIOS if SCENARIOS[c].available]

    for form in ("wrapper", "bare", "naked_json"):
        print(f"\n-- response form: {form} " + "-" * (50 - len(form)))
        print(f"{'scen':<5}{'chain':<10}{'rows':>6}{'run_id':>9}{'pfail':>7}"
              f"{'fallbk':>8}{'bw kept':>9}{'L2 viol':>9}")
        for code in codes:
            for f in os.listdir(_TMP):
                if code in f:
                    os.remove(os.path.join(_TMP, f))
            try:
                s = run_scenario(code, form)
            except Exception as exc:  # noqa: BLE001
                failures.append(f"{code}/{form}: raised {type(exc).__name__}: {exc}")
                print(f"{code:<5}{'':<10}{'CRASHED':>6}  {type(exc).__name__}: {str(exc)[:40]}")
                continue

            print(f"{code:<5}{s['chain']:<10}{s['rows']:>6}{str(s['runs']):>9}"
                  f"{s['parse_failures']:>7}{s['fallbacks']:>8}{s['bw_kept']:>9}{s['violations']:>9}")

            if s["runs"] != [RUN_ID]:
                failures.append(f"{code}/{form}: run_id not recorded, got {s['runs']}")
            if s["fallbacks"]:
                failures.append(f"{code}/{form}: {s['fallbacks']} rule-based fallbacks on the LLM path")
            if s["bw_kept"] != s["rows"]:
                failures.append(
                    f"{code}/{form}: model budget_weight preserved on only "
                    f"{s['bw_kept']}/{s['rows']} rows, the rest are role defaults")
            # A civilian chain must intercept the coup signal; a military
            # chain must permit it. This is the paper's central mechanism, so
            # it is asserted rather than merely reported.
            if s["chain"] == "civilian" and s["violations"] == 0:
                failures.append(f"{code}/{form}: civilian chain logged no L2 interception")
            if s["chain"] == "military" and s["violations"] != 0:
                failures.append(f"{code}/{form}: military chain logged {s['violations']} interceptions")

    print("\n" + "-" * 74)
    if failures:
        print(f"RESULT: {len(failures)} failure(s)\n")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"RESULT: {len(codes)} scenarios x 3 response forms, all clean")
    print("PASS: decisions survive parsing, reach CVES, are logged, and no "
          "malformed re-prompt can abort a run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
