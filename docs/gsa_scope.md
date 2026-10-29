# GSA scope decision, 2026-10-29

Authored by `senior-data-analyst`. This is the senior-data-analyst decision
flagged in `.claude/memory.md` section 5j ("Open decision for
`senior-data-analyst`, not resolved here: whether a cross-scenario GSA needs
per-scenario bounds...") and in `docs/bias_audit.md` section 5.3. It governs
`analysis/kpi.py`'s `GSA_PROBLEM` / `GSA_PARAM_MAP` / `GSA_PARAM_CLASS` /
`run_sobol_gsa`.

## 0. What is being decided, and what is not

This note is about **sampling design**, not about any individual Sobol
number. Three questions, kept separate on purpose:

1. Is a published Sobol result correct given the bounds it was sampled
   under? (A code/design question, answered here.)
2. Does the bound set that produced it actually bracket the scenario it
   claims to describe? (A scope question, answered here, and now enforced
   in code.)
3. Is the resulting number itself still numerically right after other,
   unrelated fixes (year-zero correction, bug #11 bare-read fix)? (A
   recomputation question, answered per-run in Part 3 below, not reopened
   here.)

## 1. The verdict: three parameter classes, not two, not one shared bound set

Reviewer 1 point 2 and Reviewer 2 point 2 together ask one thing: demonstrate
the headline results are not mechanically induced by parameter bounds. A
single MFU-centred `GSA_PROBLEM` cannot honestly answer that question for
every scenario, because most of its fourteen parameters do not mean the same
thing on every scenario. Verified directly against every constitution's live
default (not spot-checked, the full 14x7 table is reproducible with
`analysis.kpi._gsa_scope_violations`):

| Class | Members | Why | Legitimate scope under the CURRENT bound set |
|---|---|---|---|
| **Institutional** (9) | `merit_performance_weight`, `analysis_threshold`, `state_share`, `ethnic_direct_share`, `trust_acceleration_multiplier`, `trust_acceleration_trigger_corruption`, `iig_investigation_trigger`, `iig_entry_merit_min`, `coup_trigger_loyalty` | MFU-authored constitutional design choices. On Scenario A these are genuinely free parameters (Kaung chose them when designing MFU). On every other scenario they are fixed, sourced facts of that country's own real constitutional text, Thailand's veto threshold is not a modelling assumption, it is 2017 Thai constitutional law. | **Scenario A only.** Measured: 0 of 9 fail to bracket A (bounds were authored around A by construction); 4-7 of 9 fail on every one of C/SK/TH/PK/CL/DE (C fails 6, confirming memory 5j exactly). |
| **Calibration** (2) | `year_zero_corruption`, `coup_risk` | Real-world initial-condition inputs, sourced (or explicitly disclosed as a deliberate calibration choice, as with Myanmar's `coup_risk`) separately per scenario. Not an institutional design choice, nobody "designed" Myanmar's 2008 V-Dem corruption score. | `year_zero_corruption`: **A and C only** (both anchored to the same real 0.878 value by the controlled-pair design; SK 0.458, TH 0.683, PK 0.637, CL 0.067, DE 0.020 all fail). `coup_risk`: currently brackets **every scenario that has the field** (A has none), but only because `[0.00, 0.50]` was deliberately built wide enough to span the whole historical range (SK 0.02 to C's disclosed-inflated 0.25), see caveat below, this is not structurally guaranteed. |
| **Modelling constant** (3) | `fear_compliance_trust_floor`, `civilian_coup_signal_damping`, `stability_rights_bonus` | Ka-Nova engine/feedback constants, confirmed **byte-identical across all seven real constitutions** (`docs/bias_audit.md` section 2.4). Nobody has ever researched a country-specific fear-compliance floor; these were backfilled as one modelling decision applied uniformly. | **Any scenario**, with the one shared bound set, this is the only class for which that claim is actually true, because there is no per-country real value a shared bound could exclude. |

**This refines, and partly corrects, the premise it was asked to verify.**
The instruction framed the non-institutional parameters as one bucket
("the others ... are Ka-Nova modelling choices ... legitimate on any
scenario") and named `coup_risk` as a fourth member of that bucket
alongside the three rights constants. That does **not** hold. `coup_risk`
is differentiated per country (SK 0.02, TH 0.12, PK 0.086, CL 0.05, DE 0.00,
C 0.25), exactly like `year_zero_corruption`, not uniform like the three
rights constants (0.10 / 0.05 / 0.20 everywhere, with no exception). It
happens to pass today's bracket check on every scenario that carries it
only because of how wide `[0.00, 0.50]` was deliberately drawn, not because
it is scenario-invariant by construction. Grouping it with the true
modelling constants would have been correct in its practical effect right
now, but wrong in its justification, and a wrong justification is exactly
the kind of thing that breaks silently the day an eighth constitution is
added with a real coup-risk calibration above 0.50. It is recorded here as
its own "calibration" class so the distinction survives into any future
scenario addition.

The three-way split (not the originally proposed four-way grouping) is the
verdict: **scope by parameter class, enforce it in code, do not collapse
calibration into modelling-constant just because they currently behave the
same.**

## 2. The manuscript scope sentence

Publication-ready, for the Methods/sensitivity-analysis subsection:

> We conduct the global sensitivity analysis (GSA) separately by parameter
> class. Nine constitutional design parameters (merit weighting, the
> Analysis Council veto threshold, the three resource-split and IIG
> parameters, the two trust-acceleration triggers, and the coup-trigger
> loyalty threshold) are perturbed on Scenario A only, because they are free
> design choices in the self-authored MFU constitution but fixed, sourced
> facts of each other scenario's own real constitutional text; perturbing
> them elsewhere would measure sensitivity to a hypothetical MFU-like
> constitution rather than to that country's own government. The year-zero
> corruption calibration is perturbed on Scenarios A and C only, the two
> scenarios that share its sourced value (V-Dem v2x_corr, Myanmar, 2008).
> Three feedback-layer constants, the fear-compliance trust floor, the
> civilian coup-signal damping, and the stability rights bonus, are
> Ka-Nova modelling choices rather than provisions of any constitution,
> confirmed identical across all seven encodings, and are perturbed on
> whichever scenario the metric under study is live for (the trust floor
> binds only on military chains). Sampling bounds for every perturbed
> parameter are verified computationally to bracket the live default of
> the scenario(s) on which it is perturbed before any result is reported;
> this check is enforced at runtime, not merely documented.

## 3. Per-run publishability verdict

| Run | File | Scope verdict (this note) | Numerical verdict | Overall |
|---|---|---|---|---|
| C / `trust_index`, n=64, k=13 | `results_phase3/sobol_sensitivity_C_trust_index.csv` | Headline parameter (`fear_compliance_trust_floor`) is "modelling constant" class, legitimately perturbed on C, bound `[0.00, 0.20]` correctly brackets the uniform 0.10 default. The other 12 parameters in that run include 6 "institutional" parameters whose bounds do **not** bracket C (confirmed: `analysis_threshold`, `state_share`, `trust_acceleration_trigger_corruption`, `iig_investigation_trigger`, `iig_entry_merit_min`, `coup_trigger_loyalty`), plus `year_zero_corruption` (fine, A/C-shared) and the other 2 modelling constants (fine). | Headline S1≈ST≈1.01 is a real, correctly-scoped result (also independent of memory 5i's bare-read bug, since `fear_compliance_trust_floor` was read through the `rights.*` path, not a bare MFU import). The already-flagged secondary claim ("the eleven genuine constitutional parameters together account for well under 1%") remains invalid for both of memory's existing reasons (bare-read + bound-scope) and must never be quoted. | **Publishable, headline only, with the caveat already locked in memory, no change needed to that verdict.** Do not re-run for publication purposes since the only thing being published is the headline; a fresh run would only be needed if the per-parameter table beyond the headline were ever wanted (not recommended). |
| A / `corruption_index`, n=64, k=13 | `results_phase3/sobol_sensitivity_A_corruption_index.csv` | Scope is correct: scenario A, all active parameters are either "institutional" (bracket A by construction) or `year_zero_corruption` (A/C class, A is in scope) or modelling constants. No scope defect. | **Must be re-run regardless** (explicit fact, not reopened here): `year_zero_corruption`'s bound moved from `[0.60, 0.85]` to `[0.75, 1.00]` and its value moved from the unsourced 0.72 to the real 0.878 after this run was produced; it was this run's dominant parameter (S1=0.65, ST=0.70). | **Must be re-run.** Scope was never the problem for this one; the calibration update is. |
| A / `coup_probability`, n=64, k=13 | `results_phase3/sobol_sensitivity_A_coup_probability.csv` | Scope correct (same as above). | All-NaN / zero output variance across all 960 samples, the metric is invariant to the entire 13-parameter space, including `year_zero_corruption`, so the year-zero change cannot move a result that has no variance regardless of input. | **Publishable as-is.** Report as a structural-invariance finding, never as an effect size. |
| A / `stability_index`, n=64, k=13 | `results_phase3/sobol_sensitivity_A_stability_index.csv` | Scope correct. Headline parameter (`stability_rights_bonus`) is "modelling constant" class, confirming it was never at risk of a scope artifact, the same class exemption that protects the C/trust headline. | `year_zero_corruption` sits at ST=0.0063 in this run, contributing essentially nothing, so its value being stale does not move the result. | **Publishable as-is.** |

No run in the four needs a scope-driven re-run; the one mandatory re-run
(A/corruption_index) is for a calibration-value reason already locked
elsewhere, not a scope defect this note identifies.

## 4. What changed in code, and why it is now structurally enforced

`analysis/kpi.py`:

- Added `GSA_PARAM_CLASS`, classifying every `GSA_PROBLEM` parameter as
  `"institutional"`, `"calibration"`, or `"modelling_constant"` per the
  table in Part 1.
- Added `_gsa_scope_violations(target_constitution, active_names, scenario)`,
  a pure function (no model runs) that compares each non-modelling-constant
  parameter's live default on the target scenario against its declared
  bound, returning every violation.
- `run_sobol_gsa` now calls this check immediately after resolving the
  active parameter set and **before drawing any Sobol samples or running
  the model**. By default it raises `ValueError` naming every violating
  parameter, its class, its bound, and the scenario's real value, a scope
  violation now fails in about a second, not after a 30-to-50-minute run
  that would otherwise produce a publishable-looking but wrongly-scoped
  CSV. An explicit `allow_unscoped_params=True` (CLI: `--gsa-allow-unscoped`)
  opts out with a loud warning instead of a silent pass, for a
  deliberately-disclosed exploratory run only.
- Updated `run_sobol_gsa`'s docstring to state the three-class scope
  directly (superseding the two-class version that incorrectly grouped
  `coup_risk` with the modelling constants).

Verified: `_gsa_scope_violations` reproduces the exact 6-of-14 failure
count for Scenario C and 0-of-13 for Scenario A found by direct
introspection of all seven constitutions' live defaults (not spot-checked).
`run_sobol_gsa(scenario="C", ...)` now raises in ~1 second with no model
runs; `run_sobol_gsa(scenario="A", ...)` proceeds unaffected; the
`allow_unscoped_params=True` override was exercised once to confirm it
still runs the model and writes a CSV rather than silently downgrading the
check. All verification used tiny smoke parameters (`n_sample=2`,
`n_citizens=50`, `n_steps=3`) under a throwaway `KA_NOVA_RESULTS_DIR`,
never `results_phase3/`, and is not itself a GSA result.

## 5. Open follow-up, not resolved here

- `coup_risk`'s current single bound set is empirically, not structurally,
  safe across all seven scenarios. If a future constitution's own
  `YEAR_ZERO_COUP_RISK` falls outside `[0.00, 0.50]`, `_gsa_scope_violations`
  will catch it automatically (it is classified `"calibration"`, not
  exempted), but the bound itself should be revisited the day that
  happens rather than widened reflexively.
- Per-scenario bound sets (rather than scenario-restricted sharing of one
  MFU-centred set) were considered and are not recommended for this
  revision: building six more bound sets, each requiring the same
  sourcing rigor as the MFU ten, is a research task comparable in size to
  work already explicitly deferred (see memory section 11's standing
  realism requirement), not a one-hour fix. Scoping by class is the
  correct cost/rigor trade-off for this resubmission; a genuine
  per-country GSA is reasonable future work, not a gap in this decision.
