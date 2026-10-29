"""
Unit test: north-star composite decomposition sums to the composite.

Kaung's decision 7 (.claude/memory.md section 5j; docs/bias_audit.md
Section 3): the north-star composite is reported decomposed, term by term,
never as a single headline number, because about 45% of its weight is
decided by chain-type hardcodes and a ceiling effect (coup, IIG, GDP for
every civilian scenario). The composite is NOT re-weighted and NOT retired.

This test proves the seven published term reporters
(north_star_term_corruption / trust / coup / iig / gdp / harmony / gini)
sum to the pre-clip composite that north_star_progress is computed from, so
the decomposition can never silently drift from
model_phase3.KaNovaModelPhase3._update_north_star_progress's formula if
someone edits one side and not the other.

No LLM calls — rule-based only, KA_NOVA_RESULTS_DIR isolated to a throwaway
directory so no run output reaches the tracked results_phase3/ trail.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["WANDB_MODE"] = "disabled"

TERM_KEYS = [
    "north_star_term_corruption",
    "north_star_term_trust",
    "north_star_term_coup",
    "north_star_term_iig",
    "north_star_term_gdp",
    "north_star_term_harmony",
    "north_star_term_gini",
]

# Independent per-term rounding (4 decimals each, same convention as every
# other shared_data float in model_phase3.py) can introduce at most
# 7 * 0.00005 = 0.00035 of drift against the composite's own single
# rounding. This tolerance catches a real formula mismatch (any deliberate
# weight/term change would differ by orders of magnitude more) without
# flagging that harmless rounding noise.
TOLERANCE = 1e-3


def _run_years(scenario: str, n_years: int = 3, n_citizens: int = 40, seed: int = 7):
    from model_phase3 import KaNovaModelPhase3

    model = KaNovaModelPhase3(
        scenario=scenario,
        seed=seed,
        n_citizens=n_citizens,
        use_llm=False,
    )
    for _ in range(n_years):
        model.step()
        if model.shared_data.get("simulation_failed", False):
            break
    return model


def _check_scenario(scenario: str) -> bool:
    model = _run_years(scenario)

    term_sum = sum(model.shared_data.get(k, 0.0) for k in TERM_KEYS)
    composite = model.shared_data.get("north_star_progress", 0.0)

    ok = abs(term_sum - composite) <= TOLERANCE
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] scenario={scenario} term_sum={term_sum:.4f} "
          f"composite={composite:.4f} diff={abs(term_sum - composite):.6f}")

    # Also assert every term individually matches a fresh recomputation from
    # the same shared_data inputs the model used, so a weight typo in one
    # of the seven terms (not just a sum-level drift) is caught too.
    corruption = model.shared_data.get("corruption_index", 0.72)
    trust = model.shared_data.get("trust_index", 0.22)
    coup_risk = model.shared_data.get("coup_risk", 0.25)
    iig = model.shared_data.get("iig_effectiveness", 0.30)
    gdp_growth = model.shared_data.get("gdp_growth_rate", 0.0)
    harmony = model.shared_data.get(
        "ethnic_harmony_index", model.shared_data.get("ethnic_harmony", 0.35)
    )
    gini = model.shared_data.get("gini_coefficient", 0.55)

    expected = {
        "north_star_term_corruption": (1.0 - corruption) * 0.20,
        "north_star_term_trust": trust * 0.15,
        "north_star_term_coup": (1.0 - coup_risk) * 0.15,
        "north_star_term_iig": iig * 0.15,
        "north_star_term_gdp": min(gdp_growth * 5.0, 1.0) * 0.15,
        "north_star_term_harmony": harmony * 0.10,
        "north_star_term_gini": (1.0 - gini) * 0.10,
    }
    for key, expected_val in expected.items():
        actual_val = model.shared_data.get(key, 0.0)
        if abs(actual_val - expected_val) > TOLERANCE:
            print(f"    MISMATCH {key}: published={actual_val:.4f} "
                  f"expected={expected_val:.4f}")
            ok = False

    return ok


def main():
    scenarios = ["A", "C"]
    print("North-star decomposition test (Kaung's decision 7)")
    print(f"Scenarios: {scenarios}")

    results = {s: _check_scenario(s) for s in scenarios}
    passed = sum(results.values())
    total = len(results)
    print(f"\n{passed}/{total} scenarios: seven terms sum to the composite")

    if passed != total:
        print("FAIL: decomposition has drifted from the formula")
        sys.exit(1)

    print("PASS: decomposition matches the formula for all tested scenarios")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="kanova_northstar_test_") as tmpdir:
        os.environ["KA_NOVA_RESULTS_DIR"] = tmpdir
        main()
