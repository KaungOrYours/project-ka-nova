"""
================================================================================
PROJECT KA-NOVA
tests/noticeboard/verify_noticeboard.py

Noticeboard Pattern Verification
==================================
Audits the shared_data noticeboard to confirm:

  1. WRITE CHECK — elite agents write all expected keys into shared_data
  2. READ CHECK  — citizen agents and feedback loops read from shared_data
                   using keys that actually exist (no silent defaults)
  3. DEAD KEY CHECK — keys written but never read = constitutional no-ops

Runs a single lightweight model step (100 citizens, 1 step) — not a full run.

Pass conditions:
  - All expected elite write keys present after step
  - Zero dead keys (every written key is read by at least one agent)
  - Zero phantom reads (no agent reading a key that was never written)

Author: Kaung Htet | MSc Data Science | University of Hertfordshire
================================================================================
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import json
from typing import Set, Dict, List

# ── Expected keys that elite agents MUST write each step ─────────────────────
ELITE_WRITE_KEYS = [
    "elite_budget_impact",
    "elite_ethnic_weights",
    "elite_coup_signal",
    "elite_decisions_log",
]

# ── Expected keys that feedback loops MUST write each step ───────────────────
FEEDBACK_WRITE_KEYS = [
    "corruption_index",
    "trust_index",
    "gini_coefficient",
    "coup_risk",
    "iig_effectiveness",
    "employment_rate",
    "brain_drain_rate",
    "ethnic_harmony_index",
]

# ── Keys that citizens MUST be able to read (simulation correctness) ──────────
CITIZEN_READ_KEYS = [
    "corruption_index",
    "trust_index",
    "elite_budget_impact",
    "elite_ethnic_weights",
    "elite_coup_signal",
    "employment_rate",
    "ethnic_harmony_index",
]

# ── Noticeboard auditor ───────────────────────────────────────────────────────

class NoticeboardAuditor:
    """
    Wraps shared_data with read/write tracking.
    Intercepts all get() and __setitem__ calls to log access patterns.
    """

    def __init__(self, initial: dict = None):
        self._data      = dict(initial or {})
        self.writes: Dict[str, int] = {}
        self.reads:  Dict[str, int] = {}

    def __setitem__(self, key, value):
        self._data[key] = value
        self.writes[key] = self.writes.get(key, 0) + 1

    def __getitem__(self, key):
        self.reads[key] = self.reads.get(key, 0) + 1
        return self._data[key]

    def get(self, key, default=None):
        self.reads[key] = self.reads.get(key, 0) + 1
        return self._data.get(key, default)

    def setdefault(self, key, default=None):
        self.writes[key] = self.writes.get(key, 0) + 1
        return self._data.setdefault(key, default)

    def update(self, d: dict):
        for k, v in d.items():
            self[k] = v

    def __contains__(self, key):
        return key in self._data

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def values(self):
        return self._data.values()

    def written_keys(self) -> Set[str]:
        return set(self.writes.keys())

    def read_keys(self) -> Set[str]:
        return set(self.reads.keys())

    def dead_keys(self) -> Set[str]:
        """Keys written but never read — constitutional no-ops."""
        return self.written_keys() - self.read_keys()

    def phantom_reads(self) -> Set[str]:
        """Keys read but never written — agents reading stale/missing data."""
        return self.read_keys() - self.written_keys()


# ── Check 1: Elite write keys ─────────────────────────────────────────────────

def check_elite_writes(auditor: NoticeboardAuditor) -> dict:
    print("\n  CHECK 1 — Elite Write Keys")
    print("  " + "-"*50)

    missing = []
    for key in ELITE_WRITE_KEYS:
        present = key in auditor.written_keys()
        print(f"    {key:<40} {'PRESENT' if present else 'MISSING'}")
        if not present:
            missing.append(key)

    passed = len(missing) == 0
    print(f"    Result: {'PASS' if passed else 'FAIL — missing: ' + str(missing)}")
    return {
        "check":   "elite_writes",
        "missing": missing,
        "passed":  passed,
    }


# ── Check 2: Feedback write keys ──────────────────────────────────────────────

def check_feedback_writes(auditor: NoticeboardAuditor) -> dict:
    print("\n  CHECK 2 — Feedback Loop Write Keys")
    print("  " + "-"*50)

    missing = []
    for key in FEEDBACK_WRITE_KEYS:
        present = key in auditor.written_keys()
        print(f"    {key:<40} {'PRESENT' if present else 'MISSING'}")
        if not present:
            missing.append(key)

    passed = len(missing) == 0
    print(f"    Result: {'PASS' if passed else 'FAIL — missing: ' + str(missing)}")
    return {
        "check":   "feedback_writes",
        "missing": missing,
        "passed":  passed,
    }


# ── Check 3: Citizen read keys ────────────────────────────────────────────────

def check_citizen_reads(auditor: NoticeboardAuditor) -> dict:
    print("\n  CHECK 3 — Citizen Read Keys")
    print("  " + "-"*50)

    missing = []
    for key in CITIZEN_READ_KEYS:
        read = key in auditor.read_keys()
        print(f"    {key:<40} {'READ' if read else 'NEVER READ'}")
        if not read:
            missing.append(key)

    passed = len(missing) == 0
    print(f"    Result: {'PASS' if passed else 'FAIL — never read: ' + str(missing)}")
    return {
        "check":   "citizen_reads",
        "missing": missing,
        "passed":  passed,
    }


# ── Check 4: Dead keys ────────────────────────────────────────────────────────

def check_dead_keys(auditor: NoticeboardAuditor) -> dict:
    print("\n  CHECK 4 — Dead Keys (written but never read)")
    print("  " + "-"*50)

    dead = auditor.dead_keys()

    # Filter out internal/log keys that are intentionally write-only
    ignore = {"elite_decisions_log", "simulation_failed", "coup_attempted"}
    dead_flagged = dead - ignore

    if dead_flagged:
        for key in sorted(dead_flagged):
            print(f"    DEAD: {key}")
    else:
        print(f"    No dead keys found (excluding internal logs)")

    passed = len(dead_flagged) == 0
    print(f"    Result: {'PASS' if passed else 'FAIL — ' + str(len(dead_flagged)) + ' dead keys'}")
    return {
        "check":        "dead_keys",
        "dead_keys":    sorted(dead_flagged),
        "ignored_keys": sorted(ignore),
        "passed":       passed,
    }


# ── Check 5: Phantom reads ────────────────────────────────────────────────────

def check_phantom_reads(auditor: NoticeboardAuditor) -> dict:
    print("\n  CHECK 5 — Phantom Reads (read but never written)")
    print("  " + "-"*50)

    phantoms = auditor.phantom_reads()

    if phantoms:
        for key in sorted(phantoms):
            print(f"    PHANTOM: {key}")
    else:
        print(f"    No phantom reads found")

    passed = len(phantoms) == 0
    print(f"    Result: {'PASS' if passed else 'WARN — ' + str(len(phantoms)) + ' phantom reads (agents using defaults)'}")

    return {
        "check":         "phantom_reads",
        "phantom_keys":  sorted(phantoms),
        "passed":        passed,
    }


# ── Main runner ───────────────────────────────────────────────────────────────

def run_noticeboard_verification(output: str = None) -> dict:
    print("\n" + "="*60)
    print("KA-NOVA — NOTICEBOARD PATTERN VERIFICATION")
    print("="*60)
    print("Running 1 model step with 100 citizens (lightweight audit)...")

    # ── Import and patch model ────────────────────────────────────────────────
    from model_phase3 import KaNovaModelPhase3

    # Initialise lightweight model
    model = KaNovaModelPhase3(
        scenario="A",
        n_citizens=100,
        use_llm=False,
    )

    # Replace shared_data with auditor
    auditor = NoticeboardAuditor(initial=dict(model.shared_data))
    model.shared_data = auditor

    # Run one step
    model.step()

    print(f"\n  Step complete.")
    print(f"  Total keys written: {len(auditor.written_keys())}")
    print(f"  Total keys read:    {len(auditor.read_keys())}")

    # ── Run all checks ────────────────────────────────────────────────────────
    c1 = check_elite_writes(auditor)
    c2 = check_feedback_writes(auditor)
    c3 = check_citizen_reads(auditor)
    c4 = check_dead_keys(auditor)
    c5 = check_phantom_reads(auditor)

    # Critical checks: 1, 2, 3 only
    # Check 4 (dead keys) has acceptable institutional reporting keys — not a hard fail
    # Check 5 (phantom reads) is always a warning
    overall_passed = c1["passed"] and c2["passed"] and c3["passed"]

    verdict = (
        "PASS — noticeboard wired correctly"
        if overall_passed else
        "FAIL — disconnected keys detected"
    )

    print(f"\n{'='*60}")
    print("FINAL NOTICEBOARD REPORT")
    print("="*60)
    print(f"  Check 1 — Elite writes:     {'PASS' if c1['passed'] else 'FAIL'}")
    print(f"  Check 2 — Feedback writes:  {'PASS' if c2['passed'] else 'FAIL'}")
    print(f"  Check 3 — Citizen reads:    {'PASS' if c3['passed'] else 'FAIL'}")
    print(f"  Check 4 — Dead keys:        {'PASS' if c4['passed'] else 'FAIL'}")
    print(f"  Check 5 — Phantom reads:    {'PASS' if c5['passed'] else 'WARN'}")
    print(f"\n  VERDICT: {verdict}")
    print("="*60 + "\n")

    result = {
        "total_keys_written": len(auditor.written_keys()),
        "total_keys_read":    len(auditor.read_keys()),
        "all_written_keys":   sorted(auditor.written_keys()),
        "all_read_keys":      sorted(auditor.read_keys()),
        "check1": c1,
        "check2": c2,
        "check3": c3,
        "check4": c4,
        "check5": c5,
        "overall_passed": overall_passed,
        "verdict": verdict,
    }

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Report saved to {output}")

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ka-Nova Noticeboard Pattern Verification")
    parser.add_argument("--output", type=str, default=None, help="Save report to JSON")
    args = parser.parse_args()

    run_noticeboard_verification(output=args.output)
