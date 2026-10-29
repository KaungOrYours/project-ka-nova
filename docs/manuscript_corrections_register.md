# Ka-Nova Manuscript Corrections and Decisions Register

**Manuscript:** IEEE Access Access-2026-37966, submission UUID `b9e6f9b3-ed48-4565-836d-5633d52b89d3`
**Date of record:** 2026-10-29
**Owner:** `senior-research-paper-writer`
**Status:** authoritative. The manuscript revision and the Response to Reviewers are both built from this file.

## 0. How to use this file

This is not the Response to Reviewers, and it is not draft manuscript prose except where an entry explicitly contains replacement text. It is the single list of (a) framing decisions that are now settled and must not drift, (b) statements in the submitted manuscript that are factually wrong or indefensible against live code, and (c) positioning work that must land in the revision.

Every entry carries the same fields:

- **Currently says** quoted where a quote exists in the record, otherwise described.
- **Why it is wrong or indefensible**.
- **Must say instead**.
- **Reviewer point served**.
- **Evidence** a file, a line, a memory section, or a pending run. Nothing in this register rests on an assertion with no trace.
- **Status** SETTLED, ACTION REQUIRED, or PENDING with the blocking item named.

Provenance of every number quoted below: `.claude/memory.md` sections 4a, 5b, 5c, 5d, 5e, 5f, 5g, 5h, 5i, 6, 11, or live source read on 2026-10-29. Where a number is not yet known it is written as PENDING with a placeholder identifier from section 7.

## 0.1 Two global preconditions that gate every number in this file

**G1. All published headline numbers are provisional until the Phase 2 re-run completes.** The constitution-propagation work (bug #11), the Constitutional Court wiring (bug #12), the year-zero initialisation fix (bug #16), the IIG effectiveness floor (bug #10), the north-star write path (bug #3) and the ethnic-harmony reporter (bug #22) all changed behaviour after the July data was produced. Memory section 4 states the consequence directly: a full A/C re-run plus first real runs of the five new scenarios are required before any number from any of the seven scenarios can be published. Consequently this register fixes **framing and factual claims**, not final values. Every effect size, confidence interval and collapse year quoted here is the submitted-manuscript value and is marked for recomputation.

**G2. Bug #11 is still partially unfixed and must be closed before the run.** Memory section 5i, verified 2026-10-23: 43 bare module-level MFU `CONSTITUTION.<section>` reads remain on live paths (`agents/official.py` 20, `agents/citizen.py` 12, `feedback/loops.py` 11). The most consequential is `agents/citizen.py:1179`, `_calculate_merit()`, which means every citizen, official and IIG agent in all seven scenarios currently computes the paper's most-cited formula from MFU weights. If the run happens before this is fixed, the seven-constitution design's premise does not hold and nothing in Part 2 of this register can be written truthfully. Writing cannot begin on the comparative sections until this is closed.

---

# Part 1. Settled framing decisions

These four were decided by Kaung Htet on 2026-10-29. They are settled. Do not reopen them in drafting, and do not soften them in response to a reviewer-facing convenience argument.

## D1. Effect-size reporting policy: d only for metrics with two-sided variance

**Status:** SETTLED.

**Currently says.** The abstract and the results section frame the headline finding in terms of very large effect sizes, reporting Cohen's d for five metrics: corruption 76.1, trust 84.2, coup probability 46.7, stability 91.6, IIG effectiveness 6.0. Section VI-A defends them as reflecting "a mechanism that compounds over time rather than a tuned parameter difference".

**Why it is wrong or indefensible.** Reviewer 1 point 2 asks the authors to "demonstrate that these results are robust and are not mechanically induced by thresholds, parameter bounds, or deterministic relationships embedded in the model". For three of the five the verified answer is that they are:

| Metric | Submitted d | Zero-variance arm | Governing constant |
|---|---|---|---|
| Trust | 84.2 | Scenario C, 0.1000 plus or minus 0.0000 | `rights.FEAR_COMPLIANCE_TRUST_FLOOR` = 0.10 |
| Coup probability | 46.7 | Scenario A, 0.0000 plus or minus 0.0000 | `rights.CIVILIAN_COUP_SIGNAL_DAMPING` = 0.05 |
| Stability index | 91.6 | inherits both clamps plus a fixed additive term | `rights.STABILITY_RIGHTS_BONUS` = 0.20 |

For trust the pooled standard deviation is sqrt((0.011^2 + 0^2)/2) = 0.00778, contributed entirely by Scenario A, so d measures the distance from Scenario A's trust to a constant. The Sobol GSA confirms this quantitatively: `fear_compliance_trust_floor` returns S1 = 1.0148 and ST = 1.0034 for Scenario C trust, with all twelve other parameters at or near zero (memory 5e, `results_phase3/sobol_sensitivity_C_trust_index.csv`, n_sample 64, 960 model runs).

**Must say instead.** Report Cohen's d for two metrics only:

- **Corruption.** Two-sided variance in both arms (0.007 and 0.015), and now GSA-supported. The A/corruption Sobol run (memory 5h, `results_phase3/sobol_sensitivity_A_corruption_index.csv`) finds variance carried by `year_zero_corruption` (S1 0.6487, ST 0.6972), a real sourced calibration input, and `iig_investigation_trigger` (ST 0.2095), a genuine MFU constitutional provision at 0.45. All three clamp constants sit at ST 0.12, 0.07 and 0.06 with confidence intervals covering those values, that is, no detectable contribution.
- **IIG effectiveness.** Honest as reported, two-sided variance.

For trust, coup probability and the stability composite, **quote no d value at all**. Instead disclose the three governing constants by their exact field names and values, state that the separation between arms is complete and by design, and report it as **discriminative validity** (the model separates the two constitutional encodings without overlap) rather than as an effect magnitude.

Remove the "effect sizes are very large" framing from the abstract and from the results section.

**Replacement text, for the formal effect-size robustness subsection:**

> Reported standardised effect sizes are restricted to metrics for which both scenario arms exhibit two-sided variance. For corruption and for IIG effectiveness this condition holds and Cohen's d is interpretable. For terminal trust, coup probability and the stability composite it does not: in each case one arm is bounded by an explicit modelling constant. `rights.FEAR_COMPLIANCE_TRUST_FLOOR` (0.10) fixes terminal trust on a military governance chain; `rights.CIVILIAN_COUP_SIGNAL_DAMPING` (0.05) drives coup probability on a civilian chain to its lower bound; and `rights.STABILITY_RIGHTS_BONUS` (0.20) contributes a fixed additive term to the stability composite whenever rights are non-suspendable. Where one arm has zero dispersion the pooled standard deviation is contributed by the other arm alone, and a standardised mean difference computed from it is not a measure of effect magnitude. We therefore report these three metrics as discriminative validity, meaning that the two constitutional encodings are separated without overlap within the simulation, and we state the governing constant in each case rather than quoting a d value. A global sensitivity analysis quantifying the dominance of the trust floor is reported in Section [GSA subsection].

**Two guardrails on this entry.**

1. Section VI-A's existing argument that the divergence "reflect[s] a mechanism that compounds over time rather than a tuned parameter difference" remains valid **for corruption only** and must not be reused for the clamped three. Reusing it there is the specific move a reviewer can refute by reading `feedback/loops.py:140`.
2. This decision does **not** upgrade corruption from a validity check to a discovery. Locked finding 6 stands: the effect sizes are validity checks confirming the model behaves as designed, not surprising findings. What the GSA adds is that corruption's variance is attributable to a real initial condition plus a real constitutional lever rather than to an arbitrary floor. Do not write "the GSA shows the constitution drives corruption".
3. The strongest single sentence available for corruption, and it is GSA-backed: both constitutions encode the same `YEAR_ZERO_CORRUPTION` = 0.72, so the two scenarios start identical on the parameter that dominates within-scenario variance and still diverge by approximately 0.88 over fifty years. That cannot be an initial-condition artifact.

**Reviewer point served.** Reviewer 1 point 2 (primary), Reviewer 2 point 2 (the GSA that was "still future work").

**Evidence.** `feedback/loops.py:140,184,880`; `model_phase3.py:536`; `config/constitution.py:118-120` and the identical backfill on all seven constitutions (verified by grep 2026-10-29); memory 5c Exposure 1, 5d Opening 1, 5e, 5h.

**Pending.** All d values recomputed after the Phase 2 re-run (PEND-5). The IIG d = 6.0 will move because bug #10 changes Scenario C's IIG trajectory (see C6). Trust-floor GSA requires the re-run in PEND-3 before its secondary claim is quotable.

## D2. Near-twin backtest: engine stays symmetric, and the paper claims the two-axis finding only

**Status:** SETTLED.

**Decision.** The engine is not modified. `_coup_risk_check()` keeps one shared 0.70 risk threshold and one shared conditional 70 percent success roll for every scenario, which is the mechanical basis of the experimental-control argument. The method's own docstring states the symmetry explicitly (`model_phase3.py:705-722`).

**Consequence that must be written down.** Within the simulation, the three guardianship encodings reach the shared threshold and terminate early. Thailand collapsed near year 15 in local testing. Historically, Thailand's 2017 constitution has recorded zero coups in nine years and remains in force; Chile's 1980 constitution, as amended, remains in force after more than four decades and survived two popular rejections of proposed replacements (memory 4a). A reviewer will notice this, and a backtest that fails is worse than no backtest because it argues the method does not capture real governance dynamics, which is Reviewer 1 point 5's exact concern.

**Must say instead.** The paper claims only the two-axis finding accepted on 2026-10-20: guardianship constitutions cluster tightly on suppressed representation and executive constraint, which is the mechanism their texts share, and diverge sharply on corruption trajectory and survival, which is the outcome. The paper **must not** present Thailand or Chile as outcome backtests and **must not** claim to predict constitutional survival.

**Replacement text, the explicit limitation paragraph this requires:**

> **Scope limit of the collapse mechanism.** The coup-attempt mechanism is deliberately symmetric across scenarios: one shared risk threshold and one shared conditional success probability apply to every constitution, so that no scenario receives a country-specific failure schedule. That symmetry is what licenses the controlled comparison in Section [IV], and it is preserved here without modification. It also imposes a scope limit which we state explicitly rather than leave to inference. Within the simulation, the guardianship encodings reach the shared risk threshold and terminate before the fiftieth year. The historical record for two of them does not: Thailand's 2017 constitution has recorded no coup and no replacement across nine years, and Chile's 1980 constitution, as amended, remains in force after more than four decades, having survived two popular rejections of proposed replacements. We therefore do not present Thailand or Chile as outcome backtests, and we make no claim that this model predicts constitutional survival. The comparative claim we do make is the two-axis result reported in Section [comparative section]: guardianship constitutions cluster tightly on suppressed representation and executive constraint, the mechanism their texts share, and diverge on corruption trajectory and survival, the outcome. Simulated termination timing for military-chain scenarios should be read as a property of a shared collapse mechanism under a guardianship parameterisation, not as a forecast for any particular state.

**Additional honesty note that belongs with this entry.** `config/constitution_pakistan.py:856` records, in the encoding's own source comments, that Pakistan's close simulated survival match is **not** evidence of Pakistan-specific calibration, because the country's own `COUP_TRIGGER_*` fields were demonstrably not being read by the live engine at the time of that measurement. Parts of that comment are now stale (year-zero initialisation was fixed by bug #16 and most loop reads were migrated), but the caution itself must survive into the manuscript: a timing match produced by shared machinery is not country-specific validation. Confirm the current read path and the current simulated survival time after the Phase 2 re-run before any Pakistan backtest sentence is finalised (PEND-12).

**Reviewer point served.** Reviewer 1 point 5 (external and historical backtesting), Reviewer 2 point 1 (only one extreme constitutional pair).

**Evidence.** `model_phase3.py:705-722`; memory 4a, 5c Exposure 2, 5i coup-trigger correction table; `config/constitution_pakistan.py:830-869`.

## D3. Paper architecture: two clearly labelled experiment classes

**Status:** SETTLED. This is the largest editing task in the revision.

**Currently says.** One undifferentiated controlled design, asserted in at least seven places. The exact quotes on record:

| Location | Quote |
|---|---|
| Abstract | "holding population, shock sequence and engine identical so that constitutional text is the only manipulated variable" |
| Introduction | "the same 11,000-agent population, the same eleven-vector external world, and the same ten shock types drive every run; only the constitution the elite layer reads changes" |
| Contribution 4 | "population, shocks and engine are held constant and constitutional text is the sole independent variable" |
| Section III-A | same claim, restated as design |
| Section III-E | "the same seeded shock sequence hits both scenarios, removing external stochasticity as a confound" |
| Section IV | same claim, restated as experimental setup |
| Threats to Validity | "the external layer and the population are held identical across scenarios, so these factors are controlled for, not ignored" |

**Why it is wrong or indefensible.** The standing per-country realism requirement (memory section 11) gives each new country its own real external vectors, its own real administrative geography, and its own year-zero conditions. Presenting seven constitutions with per-country context while retaining "constitutional text is the only manipulated variable" would mean the revision added confounds while claiming to have removed them, in the direction opposite to what Reviewer 1 point 1 and Reviewer 2 point 1 asked. Reviewer 2 answered No to all three core yes/no questions already; this would be an immediate kill.

**Must say instead.** Two clearly labelled experiment classes.

- **(i) Controlled experiment, A versus C.** Keeps its claim verbatim. This is legitimate: Myanmar's external layer was verified identical across the pair, zero mismatches on all eleven output keys over a fifty-year same-seed comparison (memory section 11). Scope every "sole independent variable" sentence to this pair explicitly.
- **(ii) Realism-maximised comparative backtest, the five new countries.** Each country's own geography, external vectors and year-zero context is a deliberate feature, not a confound, and the paper says so. This class answers Reviewer 1 point 5. It does not carry the controlled-variable claim, and no sentence anywhere should imply it does.

Both classes run from one engine. `KA_NOVA_EXTERNAL_MODE` = `real` (default, each country's own sourced context) or `controlled` (every scenario on one shared external world) exists in code for exactly this reason, and A and C are unaffected either way (memory 5d Opening 3).

**Every location that needs rewording.** Abstract, Introduction, contribution list (contribution 4 at minimum, check the others), Section III-A, Section III-E, Section IV, Threats to Validity. Flagged here so none is missed; see the edit map in Part 5.

**One useful empirical fact for this rewrite.** The architecture decision is now low-stakes mechanically, because the external layer does not move headline outcomes at all (see C4). That makes the distinction a presentational and honesty requirement rather than a numbers risk, but it does not reduce its necessity.

**Reviewer point served.** Reviewer 1 point 1, Reviewer 2 point 1, and defensively the Threats to Validity credibility of the whole paper.

**Evidence.** Memory 5b finding 1, 5c Exposure 3, 5d Opening 3, 5f, section 11.

## D4. CVES L4 mode is "flag"

**Status:** SETTLED, no further confirmation needed.

**Decision.** `L4_MODE = "flag"` stands, per `docs/Sam_Integration_Spec.md` dated 2026-06-15, which specifies "flag >3 sigma outliers, do NOT reject them". All 214 published L4 outlier rows were computed in flag mode; `strip` has never run in published data. Code already matches (`engine/cves.py:60`).

**Must say.** The reproducibility section states that L4 operates in flag mode, that flagged outliers are logged and the decision is retained, and that the mode was fixed before data collection rather than chosen afterwards. Also remove the residual "apply only if Kaung confirms" aside at `engine/cves.py:559`, which is now stale.

**Reviewer point served.** Reviewer 1 point 8 (reproducibility package), and the integrity of every CVES claim.

**Evidence.** `engine/cves.py:60,558-600`; memory section 5, L4 row; `git show 545db1c:docs/Sam_Integration_Spec.md`.

**Secondary L4 note for the manuscript.** L4's fixed three-sigma check gives fast-collapsing scenarios much less history for a rolling baseline than scenarios surviving to year fifty. If L4 flag rates are ever compared across the seven scenarios, that asymmetry in statistical power must be disclosed (memory section 5, clarification row).

---

# Part 2. Factual corrections

Twelve entries. All verified against live code or against the submitted PDF as recorded in memory 5b and 5c.

## C1. Germany validation argument is a category error

**Currently says.** The phrasing lives in the internal research record (memory section 4a and `config/constitution_germany_encoding/README.md`), not yet in the manuscript: Germany's year-zero 1949 corruption of 0.020 falling inside Scenario A's year-50 confidence interval of 0.0122 plus or minus 0.0073 is described as "a strong validation point".

**Why it is wrong.** Those are different quantities measured at different times: a real constitution's **starting** condition against a designed constitution's **fiftieth-year** result. It validates nothing. The Germany encoding package flags the same problem in its own text, noting that the comparison "flatters MFU by giving Germany an unrealistically benign start" (`config/constitution_germany_encoding/README.md:804-806`).

**Must say instead.** Real validation requires Germany's **simulated** year-50 result to land near Germany's **real observed** trajectory on the same metric. That is a Phase 3 analysis and cannot be written until the Germany run exists. Until then the 1949 value is reported as what it is, a sourced year-zero initial condition (V-Dem v16, West Germany, 1949), with no comparative claim attached to it. The phrase "strong validation point" must not reach any draft.

**Reviewer point served.** Reviewer 1 point 5.

**Status.** ACTION REQUIRED now (remove the framing), PENDING for the real validation (PEND-9).

## C2. "All runs are seeded" is false on the LLM path

**Currently says.** Section VIII Reproducibility: "All runs are seeded."

**Why it is wrong.** `engine/elite_agents_v3.py:66` sets `ELITE_LLM_TEMP` to 0.4 and the submitted configuration passed no seed to the LLM client, so CVES L1 to L4 outputs for a given `run_id` were not reproducible. Reviewer 1 point 8 asks explicitly for random seeds and LLM configuration, so a reviewer attempting reproduction finds the claim false. A per-`run_id` seed is now threaded into the `ChatOpenAI` client (`engine/elite_agents_v3.py:906,931,943-944`, memory 5d Opening 5), but determinism additionally requires the Ollama server to honour `seed`, which has varied by version and is **unconfirmed**. Test on the pod by running one `run_id` twice and diffing `elite_decisions_<scenario>.jsonl` (PEND-6).

**Must say instead, outcome A, seeding confirmed on the pod:**

> The mechanical simulation layer is deterministic: Mesa scheduling and all NumPy citizen updates derive from a single per-`run_id` seed, and re-executing a given `run_id` reproduces its fifty-year trajectory bit for bit. The elite-agent layer is served by a local Ollama instance (llama3.2:3b) at temperature 0.4, and the same per-`run_id` seed is passed to the inference client. We verified on the deployment hardware that re-executing one `run_id` reproduces the elite decision log exactly, so the full pipeline, including CVES layers L1 to L4, is reproducible per `run_id`. Seed derivation, model identifier, temperature, context configuration and the exact client parameters are listed in [Table X] and in the repository.

**Must say instead, outcome B, seeding not honoured by the server:**

> Reproducibility differs by layer and we state each precisely. The mechanical simulation layer is bit-for-bit reproducible: Mesa scheduling and all NumPy citizen updates derive from a single per-`run_id` seed, so re-executing a given `run_id` reproduces its fifty-year trajectory exactly. The elite-agent layer is not. Decisions are generated by a local Ollama instance (llama3.2:3b) at temperature 0.4; although a per-`run_id` seed is supplied to the inference client, we were unable to confirm that the server honours it, and we therefore claim statistical reproducibility only for that layer. A consequence we state explicitly: CVES L1 to L4 outputs for a given `run_id`, including the per-article enforcement counts, are not expected to reproduce exactly on re-execution, and the aggregate distributions over one hundred Monte Carlo runs are the reproducible quantity. Model identifier, temperature, seed derivation and all client parameters are listed in [Table X].

**Reviewer point served.** Reviewer 1 point 8.

**Status.** PENDING PEND-6. Both texts are drafted; pick one after the pod test. The false sentence must go either way.

## C3. External vector count: eleven stated, seventeen running

**Currently says.** Section III-E and Table 3 both say eleven vectors, and Section III-E names exactly eleven: China, India, Thailand, Bangladesh, USA, EU, ASEAN, UN agencies, IMF/World Bank, foreign investors, global economy.

**Why it is wrong.** The code runs seventeen for Myanmar: those eleven plus `china_proxy_1/2/3` and `illicit_network_1/2/3`. Six vectors are undisclosed in a reproducibility-critical place. Verified live 2026-10-29 at `engine/external_layer.py:189-194` and the shock-catalog references at `:115`.

**Must say instead.** Seventeen external vectors for Myanmar, enumerated in full, with the six additional ones described for what they are: three China-aligned proxy-state vectors (arms and veto cover, diplomatic support, arms channel) and three illicit-network vectors (including Golden Triangle narcotics). Correct the count in Section III-E and in Table 3. Note also that vector counts differ per country under the realism design (South Korea 9, Thailand 11, Pakistan 12, Chile 11, Germany 9, memory section 11), so Table 3 should carry a per-scenario column rather than one number.

**Correct in the manuscript, not in the code.** The seventeen vectors are the real, intended design.

**Reviewer point served.** Reviewer 1 point 8.

**Status.** ACTION REQUIRED.

## C4. The external layer is inert, and the Threats to Validity defence must say so

**Currently says.** Threats to Validity: "the external layer and the population are held identical across scenarios, so these factors are controlled for, not ignored".

**Why it is indefensible as written.** Measured across all seven scenarios at 50 runs each, 1,000 citizens, 50 years, comparing `KA_NOVA_EXTERNAL_MODE=real` against `=controlled` aligned on `(run_id, year)`: every headline KPI is bit-identical. For Germany, where the external world genuinely changed (9 vectors versus 17, `china_influence` differing by up to 1.0, `active_shocks` by up to 5, 17.9 versus 28.96 total shocks fired, a 62 percent difference), corruption, trust, coup probability, stability and IIG effectiveness all show mean and max absolute difference of 0.000000. Only Gini moves (mean 0.000085, max 0.000436) and north star only because it contains Gini. Thailand shows the same pattern. So the external factors are controlled for **because they are inert**, which is a much weaker and materially different claim from the one the paper makes.

**Must say instead.** Three things, plainly:

1. The external layer is held identical in the controlled A versus C comparison, and separately, a direct measurement shows that substituting an entirely different country's geopolitical world changes no headline KPI by more than 1e-6. The control is therefore not load-bearing for those metrics, and we report that as a measured property of the model rather than as a design virtue.
2. The per-country external research is real, sourced and correctly encoded, and it **currently does not drive outcomes**. It must not be presented as affecting results.
3. Caveat on scope: this was measured on the rule-based path at 1,000 citizens with 50 runs. The LLM path reads external vectors inside its status report, so the external layer could in principle matter more under `--use-llm`. That is untested, and no claim is made in either direction until it is checked on the pod (PEND-8).

**Reviewer point served.** Threats to Validity credibility; indirectly Reviewer 1 point 4 (investigate degenerate behaviours instead of deferring), since this is exactly such an investigation reported rather than deferred.

**Evidence.** Memory 5f, full table.

**Status.** ACTION REQUIRED, with the LLM-path caveat PENDING PEND-8.

## C5. Reviewer 2's "two metrics remain constant": correct attribution

**Currently says.** Section VI-D Limitations names them outright: "the North Star composite remained at 0.0 and ethnic harmony at 0.35 across all groups (indicating unfinished scoring paths rather than substantive findings)". Gini is listed separately as a third item, "differentiated only weakly, d=0.40".

**Why this entry exists.** The working assumption in this project's own notes had been that Gini was one of the two constants. It was not. Getting this wrong in the Response to Reviewers would be immediately visible to Reviewer 2, who raised the point.

**Must say instead.** The two constants were the North Star composite (0.0) and ethnic harmony (0.35). Both causes are identified and fixed:

- North Star: bug #3, a missing write path. Read in three places, never written in Phase 3. Fixed by `_update_north_star_progress()` at `model_phase3.py:538-597`, called from `step()`. Formula is the Phase 2 legacy weighting, the only formula that ever existed in the codebase: `0.20*(1-corruption) + 0.15*trust + 0.15*(1-coup_risk) + 0.15*iig_effectiveness + 0.15*min(gdp_growth*5,1) + 0.10*ethnic_harmony + 0.10*(1-gini)`, clipped to [0,1].
- Ethnic harmony: bug #22, the reporter read `shared_data["ethnic_harmony"]`, a key seeded at 0.35 and never written again, while the real trajectory was written to `shared_data["ethnic_harmony_index"]` by the S1 feedback loop. Fixed; the column now varies for every scenario.

Gini is a separate third item and does genuinely vary (observed moving from 0.0626 to 0.0802 within five years), and it is **state-GDP dispersion, not citizen income** (see C10's note and bug #2).

**Must also disclose.** Unfreezing ethnic harmony exposed two calibration mismatches which are open and must be reported honestly rather than hidden: year zero publishes 0.35 against `MYANMAR_BASELINES["ethnic_harmony"]` of 0.22 (V-Dem), and Scenario A reaches only about 0.355 at year 50 against a `NORTH_STAR_TARGETS` value of 0.75. Those magnitudes are n=300 smoke-test values, not predictions. Whether the North Star target is aspirational-and-unmet (a legitimate reportable finding), whether the S1 loop is undertuned, or whether year zero should seed at 0.22, is an open calibration decision (U3).

**Reviewer point served.** Reviewer 2 point 3, Reviewer 1 point 4.

**Evidence.** Memory 5b finding 2, bug #3, bug #22.

**Status.** ACTION REQUIRED, with real trajectories PENDING PEND-5.

## C6. IIG effectiveness mismatch is quoted in our own Limitations, and is fixed

**Currently says.** Section VI-D Limitations: "The measured IIG effectiveness under Scenario C (0.72) exceeds the near-inert ceiling implied by the encoding and warrants verification against the live parameterisation." Table 5 reports C at 0.722 plus or minus 0.065 and A at 1.000 plus or minus 0.001.

**Why it matters.** This is Reviewer 2's point 3 complaint, quoted almost verbatim in the paper's own limitations. The cause is bug #10: `institutions/iig.py:229-291` (`_update_effectiveness`) overwrote the value unconditionally, clobbering the constitutional floor. Now clamped with `effectiveness = max(floor, effectiveness)`, reading `EFFECTIVENESS_FLOOR` via `getattr` with a `None` fallback so Scenario A's behaviour is byte-for-byte unchanged (MFU's `IIGConfig` has no such field; every other constitution does).

**Must say instead.** State that the anomaly the submitted manuscript flagged for verification was traced to a specific implementation defect, name it, state the fix, and report the corrected values. Both Table 5 figures will move on re-run; do not reuse 0.722 or 1.000 without recomputation. The d = 6.0 for IIG effectiveness also changes.

**Reviewer point served.** Reviewer 2 point 3, Reviewer 1 point 4.

**Evidence.** Memory 5b finding 3, bug #10.

**Status.** PENDING PEND-5 for values; the narrative is writable now.

## C7. CVES log filenames in the reproducibility section are stale

**Currently says.** Reproducibility names `cves_violations.jsonl` and `cves_scores.jsonl`.

**Why it is wrong.** Bug #18 made these per-scenario: `cves_scores_<scenario>.jsonl` and `cves_violations_<scenario>.jsonl` (`engine/cves.py:124-135`). The same pass fixed a second, related root cause: `run_phase3.py`'s `run_single()` was resetting the old shared filenames at `run_id == 0`, which with A and C running on separate simultaneous pods is almost certainly the literal mechanism behind Scenario C's missing audit trail in the submitted data.

**Must say instead.** The per-scenario filenames, for all seven scenario codes, plus `elite_decisions_<scenario>.jsonl` and `suppression_log_<scenario>.jsonl`. Note that the per-scenario split is what makes a cross-scenario CVES audit trail possible at all, and that the submitted version's missing Scenario C trail is explained by the shared-filename reset.

**Reviewer point served.** Reviewer 1 point 8.

**Status.** ACTION REQUIRED.

## C8. Section III-F: L1 no longer validates "exactly eight ethnic weights"

**Currently says.** Section III-F describes CVES L1 as validating "exactly eight ethnic weights".

**Why it is wrong.** Bug #17 made the L1 schema dynamically sized from each constitution's real `ETHNIC_GROUPS` count via `_get_ethnic_group_count()` (`engine/cves.py:52-74`), with a cached per-count schema factory. Live counts: 0 for Chile, Thailand and Germany; 1 for South Korea; 6 for Pakistan; 8 for A and C. L3's Acemoglu-Robinson and Lijphart components are explicitly skipped, and documented as skipped, when the count is below 2.

**Must say instead.** L1 validates the ethnic-weight vector against the active constitution's own declared group count, which ranges from zero to eight across the roster, and L3's inclusiveness and consensus components are skipped by design where fewer than two groups are declared. Give the per-scenario counts in a table.

**Reviewer point served.** Reviewer 1 point 8, and the realism requirement.

**Status.** ACTION REQUIRED. Note that an earlier record gave Pakistan as 4; the live value is 6 after the decision to add Muhajirs and Saraikis (see U1).

## C9. Ethnicity is Myanmar's for every country, and that bounds what may be claimed

**Currently says.** Section III-C describes "eight census-proportional ethnic groups ... across fourteen states".

**Why it is wrong.** Geography is now per-country and genuinely live: German citizens are distributed across real Lander by population weight, Chile has 13 real regions, Pakistan 6 units with NWFP correctly named for the period, South Korea 14 real 1988 provinces, Thailand 9 aggregated DOPA regions, Germany 11 units including West Berlin. Ethnicity was **not** generalised. `agents/citizen.py`'s `_calculate_ethnic_archetype_counts()` reads a module-level `ETHNIC_ARCHETYPE_PROPORTIONS` dict that is 100 percent Myanmar-hardcoded, so a German citizen in Baden-Wurttemberg is ethnically Bamar. The gap is open, needs real per-country census and archetype data, and cannot be closed by inventing numbers (section 11's standing requirement forbids that).

**Must say instead.** Three things:

1. Describe geography per country, accurately, with the real unit counts.
2. Disclose the ethnicity gap as a named limitation: the archetype-to-ethnicity assignment matrix remains calibrated to Myanmar's census for all seven scenarios, because comparable per-country census and archetype data were not available within this revision's scope.
3. **No cross-country claim involving ethnic harmony may be made anywhere in the paper.** This interacts directly with C5: bug #22 unfroze `ethnic_harmony`, so it is now a live published column for all seven scenarios, and it is driven by Myanmar's composition in all seven. It may be reported for A versus C, where the composition is the correct one, and must be excluded from every cross-country comparison, table row and figure series.

**Reviewer point served.** Reviewer 1 point 5, Reviewer 2 point 1, and pre-empting a direct realism attack on the Germany case.

**Evidence.** Memory section 11 (geography DONE, archetype gap open), 5b finding 5c, 5c Exposure 9c, pre-deployment sweep item 2.

**Status.** ACTION REQUIRED. Gap itself remains OPEN (U2).

## C10. "11,000 Mesa agents at a 1:5,000 ratio" holds only for Myanmar

**Currently says.** "11,000 Mesa agents at a 1:5,000 ratio".

**Why it is wrong.** The uniform-11,000 decision makes the implied ratio 1:1,191 for Chile and 1:8,727 for Pakistan. The ratio was also never literally 1:5,000 for Myanmar itself: 48.4 million in 2008 at 1:5,000 would be 9,678 agents, not 11,000.

**Must say instead.** Restate as a **fixed-N design choice**, with the reasoning already on record in memory section 11: scaling strictly by real population at 1:5,000 produces a 7.3-fold gap between Pakistan (approximately 19,646) and Chile (approximately 2,687), which would reintroduce unequal statistical power across scenarios for reasons unrelated to constitutional structure, that is, precisely the parameterisation-driven-rather-than-structural confound Reviewer 2 raised. Every scenario therefore uses 11,000 citizens, matching Myanmar's already-locked design, and each country's real population shares are used only to distribute those 11,000 agents across that country's own real geographic units.

Add the thin-subpopulation caveat that was flagged with the decision: Myanmar's Kayah group at approximately 55 agents was already noted as statistically thin at this scale, so subgroup-level results for small units should be read with that in mind.

**Reviewer point served.** Reviewer 2 point 1, Reviewer 1 point 8.

**Status.** ACTION REQUIRED.

## C11. Locked numbers: collapse year is 16.6, not 15.6

**Currently says.** The submitted manuscript's Table 5 and abstract already say 16.6 plus or minus 0.96 and 50.0, and these are correct. The 15.6 figure circulated in this project's internal notes and must not be reintroduced.

**Why this entry exists.** 15.6 is a different quantity entirely: the mean number of internet shutdowns before collapse under Scenario C (manuscript Section V-D). It had been conflated with the collapse year.

**Must say.** Scenario C fails in 100 percent of runs at mean year **16.6 plus or minus 0.96**, with all runs between years 16 and 21. Scenario A reaches final year **50.0**. The historical anchor for real Myanmar is "roughly thirteen years" (2008 promulgation to the 2021 coup), and the manuscript correctly calls this **a weak plausibility check on the encoding rather than validation**. Keep that hedge exactly; do not upgrade it.

This early termination remains the paper's strongest finding and is framed as a result, not a bug: a constitution encoded from its real articles produces universal structural failure within a window containing the real instrument's own lifespan.

Note that 16.6 is a pre-re-run value and will be recomputed (PEND-5). Also note the Myanmar-anchor convention question is still open: 2008 ratification to 2021 coup gives 12.68 years, operative instrument 2011 to 2021 gives 10.01 years, and whichever is chosen must be applied identically to Pakistan's comparison (U4).

**Reviewer point served.** Reviewer 1 point 5.

**Evidence.** Memory locked finding 5, locked numbers table, section 4a item 6.

**Status.** SETTLED as a convention, values PENDING PEND-5.

## C12. Locked finding 4 is corrected: Scenario C trust is hardcoded, not emergent

**Currently says, in its old and wrong form.** Scenario C trust at 0.1000 plus or minus 0.0000 presented as an emergent attractor explained by corruption drag (0.445 per year against 0.15 per year).

**Why it is wrong.** `feedback/loops.py:140` applies the fear-compliance floor on the military chain, and `loops.py:880` independently applies the same floor to `shared_data["trust_index"]`. Both are now constitutional fields (`rights.FEAR_COMPLIANCE_TRUST_FLOOR` = 0.10) with unchanged values, verified live 2026-10-29. The corruption-drag explanation describes why trust falls **to** the floor; it does not explain the exact value 0.100 or the zero variance across one hundred runs. Those are the clamp.

**Must say instead.** Terminal trust on a military governance chain is bounded below by an explicit modelling constant representing fear compliance, and Scenario C reaches that bound in every run. The corruption-drag mechanism explains the descent; the terminal value and its zero dispersion are the bound. This is reported as discriminative validity under D1, with no d value quoted.

**Reviewer point served.** Reviewer 1 point 2.

**Evidence.** Memory locked finding 4 (corrected), 5c Exposure 1, 5e; `feedback/loops.py:140,880`.

**Status.** SETTLED. Never repeat the old form.

---

# Part 3. Positioning work

## P1. CVES novelty: cite the prior art, claim the unoccupied position, do it in the abstract

**Two framings are taken and must not be claimed.**

1. **Runtime validation and governance of LLM agents** is crowded for 2025 to 2026: "Runtime Governance for AI Agents: Policies on Paths" (arXiv 2603.16586); "Agent Behavioral Contracts" (arXiv 2602.22302, with a specification DSL and a sub-10ms enforcement library); ProbGuard (arXiv 2508.00500); "Fundamental Limits of Runtime Policy Enforcement in Multi-agent AGI Systems" (ACM, with impossibility results).
2. **Constitutional governance of agent systems** is also taken, and critically **AgentCity (arXiv 2604.07007, April 2026) predates our July submission**. It applies separation of powers to autonomous agent economies. CMAG, "LLM Constitutional Multi-Agent Governance" (arXiv 2603.13189), is also prior, along with agent-authored executable governance rules (arXiv 2609.22600) and Institutional AI (arXiv 2601.11369).

**The position that is genuinely ours**, verified by fetching AgentCity directly: every one of those works uses a constitution as an instrument of control **over artificial agents**, with the validator as a **guardrail**, and the constitution authored **for** the agents. Ka-Nova inverts both. We encode a **real, historically enacted national constitution** at article level, we use generative agents as **substrate rather than subject**, and we use CVES's enforcement log as a **measurement instrument rather than a safety mechanism**. The 4,176 Article 9.4 interceptions are evidence of a safeguard operating with per-article attribution, which is a measurement claim, not a safety claim. Nobody occupies that position.

**Required actions.**

1. **Cite and explicitly distinguish AgentCity and CMAG.** Silence reads worse than engagement, and one of them predates our submission. Two to three sentences each, in Related Work, naming what they do and what we do differently.
2. **Add the computational-legal-studies ABM line**, which is the literature this work actually extends and which is currently absent: the dedicated chapter in *Computational Legal Studies* (Elgar, ISBN 9781788977449), plus prior agent-based models of judicial review in comparative constitutional law. Reviewer 1 already nudged toward better recent-literature coverage.
3. **Make the distinction in the abstract**, not buried in Related Work. Lead with CVES as an instrument; scope the empirical claims to what the GSA supports.

**Reviewer point served.** Reviewer 1 point 3, Reviewer 2 point 4, and Reviewer 1's literature-coverage nudge.

**Evidence.** Memory 5g, CVES novelty position, literature checked 2026-10-21 with real searches.

**Status.** ACTION REQUIRED. Devy owns the Section 2 to 3 lit review and the supplementary systematic review, so route the citation insertions through her once the wording is fixed.

## P2. Reframe the CVES enforcement record honestly

**The exposure.** 4,176 interceptions, all cited to a single article (9.4), all one signal type, 88.4 percent from one agent (3,690 from the Chief Justice), 94.7 percent from two. Combined with L1's 100 percent structural validity and zero reprompts across 35,000 calls, a skeptic can argue that the LLM is so schema-constrained that it functions as a stochastic parameter generator whose only distinctive behaviour is one degenerate output that CVES then suppresses. The paper's existing claim that "a rule-based elite cannot emit a coup signal, whereas the LLM does, which is precisely why CVES is necessary" is vulnerable to the reply that the LLM's contribution is a self-created problem. A reviewer will also reasonably ask why, mechanically, emitting a coup signal makes a coup **less** likely on the civilian chain.

**Honest framing to write.**

> The enforcement record is concentrated rather than diverse, and we report its shape rather than its total. Of 4,176 logged interceptions, all cite Article 9.4, all concern a single signal type, 88.4 percent originate from one agent role and 94.7 percent from two. We do not interpret this as evidence that the constitution governs a broad range of elite misbehaviour. It is evidence of one reproducible, article-attributable interception pathway operating with per-article provenance, which is the property we claim for CVES as a measurement instrument. Two alternative readings must be acknowledged. First, a recurring single-signal output from one role is consistent with a prompt-level or model-level regularity rather than with a governance insight, and we cannot separate those two explanations from the enforcement log alone. Second, L1 recorded complete structural validity with zero reprompts across approximately 35,000 calls, which indicates that the schema constrains the generative layer tightly. Taken together these mean the enforcement total should not be read as a measure of how much governance work the constitutional layer performs. The quantity that answers that question is the marginal contribution of the constitutional layer itself, which we measure directly by ablation in Section [L2 ablation].

**The natural defence is the L2 ablation, and the capability now exists.** `CVES_L2_MODE` takes `enforce` (default, published behaviour), `observe` (detect and log identically, do not correct or reprompt, violating decisions propagate) or `off` (no detection). The non-obvious part, already handled in code: `observe` also stands down the defence-in-depth coup re-suppression at aggregation in `engine/elite_agents_v3.py`, without which the ablation would have measured L2's contribution as a spurious zero. The **run has not happened** (PEND-7). Nothing in the manuscript may claim an ablation result until it does. The submitted paper already promised this ablation in Future Work, in these words: "a targeted ablation of individual CVES layers, disabling the constitutional layer (L2) alone while leaving the structural, consensus and statistical layers active", so a reviewer who read that section will look for it.

**Reviewer point served.** Reviewer 1 point 3, Reviewer 1 point 4, Reviewer 2 point 4.

**Evidence.** Memory 5c Exposure 4, 5d Opening 4, 5b finding 6, locked finding 1.

**Status.** Framing ACTION REQUIRED now; ablation numbers PENDING PEND-7.

## P3. Preserve what already works, strengthen rather than redraft

Section VI-B already concedes Reviewer 1 point 3 explicitly: "We accept the premise: within the reported dynamics the LLM does not determine aggregate outcomes, and we do not claim it does", and it argues that the rule-based path is a load-bearing control rather than a defect. Section VI-C already carries the self-design-bias disclosure and the single-pairing limitation.

**Do not redraft either concession.** The reviewers read both and were still unconvinced, so the task is to **strengthen with new evidence**: seven constitutions instead of two, two completed Sobol GSAs with two more in flight, the L2 ablation once it runs, and the elite-to-citizen coupling work the paper itself called "a priority for the next iteration".

The LLM layer is a **control-condition and interpretability-provenance mechanism, not an outcome determinant**. Both reviewers independently flagged it, so this must be **foregrounded** in Section VI-B's expansion and reflected in the abstract, not left as a late concession. Locked finding 3 is the supporting number: LLM versus rule-based KPI delta below 0.003 across all metrics. That result is currently **under**-claimed; it is a real negative result for the field and should be reported as one.

Two deliverables the submitted paper promised in Future Work and which belong on the task list because a reviewer will look for them: the L2 ablation (P2 above) and strengthening the elite-to-citizen coupling. The coupling fix is the most direct possible answer to "the LLM is currently only weakly connected to the main simulation results".

**Reviewer point served.** Reviewer 1 point 3, Reviewer 2 point 4.

**Evidence.** Memory 5b findings 6 and 7, locked finding 3, 5g claims inventory.

**Status.** ACTION REQUIRED for the expansion; underlying evidence partly PENDING.

## P4. The GSA result is a strength, and must be written as one

**Recorded here so that no later revision softens it back into a defence.**

Finding the trust artifact ourselves, before resubmission, and reporting it as a number rather than an argument, is a far stronger posture than defending the effect size and being caught. "We ran a 960-sample Sobol global sensitivity analysis and found that the trust separation is dominated by a single modelling constant, S1 = 1.01, which we now disclose and bound" delivers Reviewer 2 point 2 (the sensitivity analysis that was "still future work") and Reviewer 1 point 2 (robustness of the effect sizes) simultaneously, and it demonstrates exactly the methodological self-scrutiny both reviewers said was missing.

Write it in that order: the analysis we ran, what it found, what we changed as a result. Not: the criticism, followed by a defence.

Two further GSA facts that belong in the same subsection.

- The GSA is now 13 parameters, not 10. The three clamp constants were added with lower bounds reaching zero, so the analysis answers what the separation looks like with each mechanism removed. Reviewer 2 point 2 named "constitutional **and feedback** parameters", and the original 10 were all constitutional; the three additions are the feedback-layer constants the point was asking about.
- Scope note for the paper: the 10 constitutional parameters are perturbed on Scenario A only, because Scenario C is a fixed historical encoding rather than a set of free design parameters. The three feedback constants are Ka-Nova modelling choices rather than provisions of any real constitution, so perturbing them on C, Thailand or Pakistan is legitimate, and for the trust floor it is only meaningful on a military chain.

**Statistical caveats that must travel with any GSA number.** On the A/corruption run: `S1_conf` on the top parameter is plus or minus 0.26 against an estimate of 0.65, so n_sample = 64 is marginal for that KPI; five S1 estimates are negative, which is estimator noise and must be reported as "not distinguishable from zero", never as a negative sensitivity; ST sums to approximately 1.67, consistent with interactions plus noise but another marginal-sample signal; and both completed runs are rule-based only.

**Reviewer point served.** Reviewer 1 point 1, Reviewer 1 point 2, Reviewer 2 point 2.

**Evidence.** Memory 5e, 5h, 5d Opening 8, bug #26.

**Status.** ACTION REQUIRED for the writing; two runs PENDING PEND-1 and PEND-2; one re-run PENDING PEND-3.

---

# Part 4. Locked language, reproduce exactly, never soften

**L-1. Contribution statement.** Reproduce exactly:

> K.H. conceived and designed the CVES framework. S.J. implemented the L1-L4 pipeline and conducted agent validation.

Never soften this toward giving Sam design credit. If anyone asks for the acknowledgments to be made "more generous", flag it rather than silently changing it. The wording is now provable from the repository: `docs/Sam_Integration_Spec.md`, dated 2026-06-15, "From: Kaung Htet", specifies the four layers by name and function, the L4 flag decision, the emergence principle with a worked wrong-versus-right code example, the JSONL logging schema with `conditions_at_decision` marked non-negotiable, the output filenames, the seven-agent roster and the interface contracts, all before any code existed, and Sam's implementation commit lands the same day (`git show 545db1c:docs/Sam_Integration_Spec.md`).

One seam to be aware of rather than to write about: the delivered CVES does not match the spec's layer semantics exactly (spec L1 "factual grounding" and L3 "causal coherence" versus shipped L1 structural/schema integrity and L3 ensemble plus Acemoglu-Robinson and Lijphart scoring). The four-layer frame is unambiguously Kaung's; who chose the L3 theory-alignment operationalisation is not answered by the written record. Sam's one genuine intellectual contribution, worth acknowledging accurately where acknowledgments are discussed, is the suppression-gate fix (refusal and empty detection replacing a token-count heuristic, plus the `parse_failure` flag), which corrected a flaw that would have inflated the suppression numbers.

**L-2. Self-design-bias disclosure.** Reproduce exactly:

> As the author of the MFU constitution, an inherent self-design bias exists. Results should be interpreted as demonstrating constitutional parameter sensitivity rather than normative superiority of any governance framework.

Never soften. Specific risk to watch in this revision: the addition of South Korea, and of Germany as an externally validated success case, must not be allowed to read as **proving** MFU's superiority. Germany's role is a backtest of the method, not a vindication of the MFU design, and C1 removes the one sentence that drifted in that direction.

**L-3. Causal scoping.** All causal language stays scoped to "within the simulation", per Dr. Saifullah's audit point. Applies to every new sentence in the comparative sections, the near-twin limitation paragraph in D2, and the Response to Reviewers.

**L-4. Effect-size framing.** Cohen's d values are validity checks confirming that the model behaves as designed, not surprising discoveries (locked finding 6). This framing is retained and now gets its own formal subsection under D1. D1 narrows which metrics get a d; it does not change this framing.

**L-5. Scenario C early termination.** Mean year 16.6 is the paper's strongest finding, not a bug, anchored against real Myanmar's roughly thirteen-year timeline as a weak plausibility check rather than as validation.

---

# Part 5. Section-by-section edit map

For the highlighted-changes PDF. Every row is an edit location; the register entry gives the content.

| Manuscript location | Entries applying | Nature of edit |
|---|---|---|
| Abstract | D1, D3, P1, P3 | Remove "effect sizes are very large"; scope the sole-independent-variable claim to A versus C; add the CVES-as-instrument distinction from the constitutional-AI cluster; foreground the LLM control-condition framing |
| Introduction | D3, C3 | Scope the controlled-design claim; correct "eleven-vector external world" to seventeen for Myanmar and per-country elsewhere |
| Contribution list, contribution 4 and any sibling making the same claim | D3 | Split into the two experiment classes |
| Related Work | P1 | Add AgentCity and CMAG with explicit distinction; add the computational-legal-studies ABM line |
| Section III-A | D3 | Scope the controlled claim; introduce the two experiment classes formally |
| Section III-C | C9, C10 | Per-country geography with real unit counts; ethnicity limitation; fixed-N design choice replacing the 1:5,000 ratio |
| Section III-E | D3, C3 | Scope "removing external stochasticity as a confound" to A versus C; correct the vector count and enumerate |
| Section III-F | C8, D4 | Dynamic ethnic-weight schema with per-scenario counts; L3 skip rule below two groups; L4 flag mode |
| Section IV | D3 | Two experiment classes in the experimental setup |
| Section V, results | D1, C5, C6, C11 | Remove "very large effect sizes"; d for corruption and IIG only; constants disclosed for the other three; corrected North Star and ethnic-harmony trajectories; corrected IIG values; 16.6 retained |
| Section V-D | C11 | Keep 15.6 as the internet-shutdown count, explicitly labelled, so it cannot be conflated again |
| New subsection, effect-size robustness | D1 | New formal subsection, text drafted in D1 |
| New subsection, global sensitivity analysis | P4 | New, with scope note and statistical caveats |
| New subsection, South Korea 1987 | PENDING PEND-5 | Cannot be drafted until real parameters and validation data exist |
| New subsection, comparative backtest and two-axis finding | D2, D3 | Includes the collapse-mechanism scope-limit paragraph drafted in D2 |
| New subsection, L2 ablation | P2, PEND-7 | Cannot be drafted until the run exists |
| Section VI-A | D1 | Restrict the compounds-over-time argument to corruption |
| Section VI-B | P2, P3 | Expand and foreground; do not redraft the concession |
| Section VI-C | L-2 | Preserve verbatim; confirm the Germany and South Korea additions have not made it read as a superiority proof |
| Section VI-D Limitations | C5, C6, C9, C4 | Resolve the two constants with causes named; resolve the IIG anomaly; add the ethnicity limitation; add the external-layer inertness finding |
| Threats to Validity | D3, C4 | Rewrite the external-layer defence honestly; scope the population and external control to A versus C |
| Section VIII Reproducibility | C2, C7, D4, C3 | Seeding statement replaced per the pod test; per-scenario log filenames; L4 flag mode; vector counts; env switches `CVES_L2_MODE`, `KA_NOVA_EXTERNAL_MODE`, `KA_NOVA_RESULTS_DIR` documented |
| Table 1 | C5 | Gini row already relabelled in code as state-GDP inequality; match the manuscript |
| Table 3 | C3 | Per-scenario external-vector counts |
| Table 5 | C6, C11, D1 | Recomputed IIG values; 16.6 retained; d column restricted to corruption and IIG |
| Future Work | P2, P3 | L2 ablation and elite-to-citizen coupling move from promised to delivered or to explicitly scoped |
| Figures, all | PEND-11 | Regeneration as vector or high-resolution with consistent styling, plus AI-provenance disclosure |

---

# Part 6. Pending inputs

Nothing in this section may be written as a result until the named item produces real output. If a draft is needed sooner, it is marked PLACEHOLDER in the draft itself, never presented as an outcome.

| ID | Item | Blocks | Expectation on record |
|---|---|---|---|
| PEND-1 | Sobol GSA, Scenario A, `coup_probability`, in flight 2026-10-29, result not yet known | D1's coup-probability paragraph, P4 | Expected to be an artifact (memory 5g, 5h). **A zero-variance output makes Sobol indices undefined and `run_sobol_gsa` will raise on the NaN check. That is a finding, not a failure: a metric invariant to the entire thirteen-parameter space is structurally determined by construction, and must be reported as such rather than as an effect size.** |
| PEND-2 | Sobol GSA, Scenario A, `stability_index`, in flight 2026-10-29, result not yet known | D1's stability paragraph, P4 | Expected to be an artifact: a composite inheriting both clamps plus the deterministic 0.20 rights step. Same zero-variance-is-a-finding rule applies. |
| PEND-3 | Re-run Sobol GSA for C/`trust_index` after the bug #11 propagation fix (G2) | Any table or RtR sentence comparing the trust floor against the constitutional parameters | The headline survives: `fear_compliance_trust_floor` is read through the fixed `rights.*` path, so its dominance of Scenario C trust is real. **What must not be quoted** is memory 5e's secondary sentence that "the eleven genuine constitutional parameters together account for well under 1%", because at least four of the thirteen were consumed through bare MFU reads and so never actually varied in that run. |
| PEND-4 | A/`corruption_index` GSA at a higher sample count | Putting the corruption S1 and ST figures in a table | n_sample 64 is marginal, `S1_conf` plus or minus 0.26 on an estimate of 0.65 |
| PEND-5 | Phase 2 re-run, all seven scenarios, full scale | Every number in the paper, every Cohen's d, South Korea's whole section, the comparative sections | Gated on G2 |
| PEND-6 | Ollama seed determinism test on the pod, one `run_id` twice, diff `elite_decisions_<scenario>.jsonl` | C2, choice between the two drafted reproducibility paragraphs | Unconfirmed; support has varied by Ollama version |
| PEND-7 | L2 ablation run via `CVES_L2_MODE=observe` | P2's quantitative half, the new ablation subsection | Capability verified in all three modes by direct injection; only the run is missing |
| PEND-8 | External-layer inertness under `--use-llm` | C4's scope caveat | Untested; the LLM path reads external vectors in its status report, so it could matter more |
| PEND-9 | Germany simulated year-50 against Germany's real observed trajectory | C1's replacement validation claim | Phase 3 analysis, requires the run |
| PEND-10 | Dr. Saifullah's confirmation of whether the Stage-8 acknowledgment edits require a Byline Change Request | The Byline Change Request justification draft | Administrative |
| PEND-11 | Figure regeneration and AI-provenance disclosure | Reviewer 1 points 6 and 7 | `analysis/kpi.py` and `charts/visualize.py` now default to `results_phase3` with a `KA_NOVA_RESULTS_DIR` override and both load all seven scenarios, so the work is now possible; the quality work itself needs real post-Phase-2 data |
| PEND-12 | Simulated survival times for Thailand, Chile and Pakistan after the re-run | D2's limitation paragraph wording and the Pakistan backtest sentence | Thailand collapsed near year 15 in local testing; Pakistan's 15.53-year local figure must not be presented as calibrated |

---

# Part 7. Unresolved items and internal contradictions found in the record

Reported rather than silently resolved.

**U1. Pakistan's ethnic-group count is recorded inconsistently.** Bug #17's entry says 4 groups for Pakistan; memory 5b finding 5 and the section 11 decision say 6, the latter explaining the expansion (Muhajirs at 7.60 percent and Saraikis at 9.84 percent were added to restore the real MQM and Karachi mechanism). **Resolved for writing purposes: 6 is current**, and bug #17's 4 is a pre-decision value. Confirm against `config/constitution_pakistan.py`'s `ETHNIC_GROUPS` immediately before the Section III-F table is finalised.

**U2. Chile's year-zero corruption is recorded three different ways and the live value is none of the two most frequently quoted.** Memory 4a and the Chile encoding README section 2.6 use **0.283** (V-Dem 1981, Pinochet era); bug #16's verification note records the live value as **0.283**; memory section 11 records it as corrected to **0.067** (the real 1990 step-function value, described as a real discontinuity in the data rather than an interpolation). **Verified live 2026-10-29: `config/constitution_chile.py:1377` is `YEAR_ZERO_CORRUPTION = 0.067`**, and the module's own self-test prints "V-Dem 1990, real observation, fixed 2026-10-20 from a prior 1981/1990 mismatch". Any manuscript sentence about Chile's year-zero corruption must use **0.067** and label it 1990. The separate comparative observation that Pinochet-era Chilean political corruption (0.283, 1981) was lower than democratic South Korea's (0.458, 1988) remains true and is unaffected, but the two numbers are different years and must never be used interchangeably. The Chile README also flags its own 1981-versus-1990 year-zero ambiguity, with materially different populations (13,437,176 versus 11,678,717), so the period label must be stated explicitly wherever Chile appears.

**U3. Ethnic-harmony calibration is unresolved.** Year zero publishes 0.35 against a stated `MYANMAR_BASELINES` target of 0.22; Scenario A reaches approximately 0.355 at year 50 against a `NORTH_STAR_TARGETS` value of 0.75. Three options are on the table (aspirational-and-unmet as a reportable finding, S1 undertuned, or reseed year zero at 0.22) and none is chosen. This needs `senior-data-analyst` plus Kaung before C5's text is final. Interacts with C9: whichever way it goes, no cross-country ethnic-harmony claim is permitted.

**U4. The Myanmar-anchor convention is unchosen.** 2008 ratification to the 2021 coup gives 12.68 years; operative instrument 2011 to 2021 gives 10.01 years; the manuscript's informal "roughly thirteen years" is consistent with the first. Whichever is adopted must be applied identically to Pakistan's comparison (14.61 years from the 1985 RCO to the 1999 coup, or 13.92 years from the Eighth Amendment) for an apples-to-apples anchor. Memory section 4a item 6.

**U5. Year-zero corruption calibration for A and C does not reproduce.** `config/constitution.py:1286` cites `YEAR_ZERO_CORRUPTION = 0.72` to a V-Dem Myanmar baseline and `config/constitution_2008.py:1038` cites the same 0.72 to a 2023 Transparency International CPI figure. Verified live 2026-10-29: neither attribution matches the real dataset values for those years, and the South Korea encoding package documents V-Dem v16 Myanmar political corruption as 0.878 in 2008, 0.739 in 2011, 0.330 in 2020 and 0.662 later. This predates the revision. It must be fixed as part of the reproducibility package, because D1's strongest corruption sentence depends on both scenarios encoding the same year-zero value and on that value having a defensible source. Flagged to `senior-data-analyst`; not resolvable by the writer.

**U6. Gini has no commensurable external benchmark.** The live Gini is state-GDP dispersion across administrative units, not citizen income (`agents/institutional.py:138-151`), and it is validated in `analysis/kpi.py` against `MYANMAR_BASELINES["gini_coefficient"] = 0.55`, a World Bank household income and consumption figure. These are incommensurable. Simulated values start near 0.06 to 0.08 because states begin near-identical. Either source a real subnational GDP-dispersion benchmark or report the metric with no external target and say so explicitly. Bug #2's open half.

**U7. Whether the three legacy Phase 2 runners ship in the reproducibility package.** `scenarios/run_a.py`, `scenarios/run_c.py` and `archive/run.py` each raise `ImportError` on their first import line. Each now carries a docstring notice saying so and pointing at `run_phase3.py`. A reviewer who clones the repository and runs one gets an immediate traceback. Ship-or-drop is Kaung's decision; the reproducibility section's wording depends on it.

**U8. Coup-trigger uniformity, narrowed but still open.** The record previously said Thailand's and Pakistan's `COUP_TRIGGER_*` are both 0.0 like Myanmar's. Verified 2026-10-23, that is stale for Pakistan. Live values, with "below equals coup risk" semantics: A 0.30/0.20, C 0.0/0.0, South Korea 0.0/0.0, Thailand 0.0/0.0, Pakistan 0.50/0.45, Chile 0.30/0.20, Germany -0.01/-0.01 (a deliberate never-fires idiom). Pakistan is therefore the most coup-prone encoding in the roster, above MFU, which is the right direction for the strongest backtest case but appears to have been set without being recorded. These fields are genuinely live, read through `m.CONSTITUTION` at `feedback/loops.py:362-363`, so **Thailand's collapse does not come from them**; it comes from `_military_chain_rules()` plus the shared `_coup_risk_check()`. D2 settles that the shared mechanism stays, so what remains open is only whether South Korea sitting at 0.0/0.0 on a civilian chain is intended for the democratisation case. Worth one sanity check before the run.

**U9. Not a contradiction, but a dependency worth stating.** Memory section 5g's claims inventory lists "collapse at year 16.6 against Myanmar's roughly thirteen years" as standing, and lists trust d = 84.2 as dead. Both are consistent with this register. The one place to watch is that the inventory also lists "the CVES enforcement record exists" as standing **but needing reframing**, which is exactly P2. Do not quote the 4,176 total without P2's framing attached.

---

# Part 8. Counts

| Category | Entries | IDs |
|---|---|---|
| Settled framing decisions | 4 | D1 to D4 |
| Factual corrections to manuscript text | 12 | C1 to C12 |
| Positioning and novelty items | 4 | P1 to P4 |
| Locked language blocks | 5 | L-1 to L-5 |
| Global preconditions | 2 | G1, G2 |
| Pending inputs | 12 | PEND-1 to PEND-12 |
| Unresolved items and contradictions | 9 | U1 to U9 |
| Manuscript edit locations identified | 27 rows | Part 5 |

Corrections by sub-type within C1 to C12: wrong count or value 3 (C3, C10, C11); stale against code 3 (C7, C8, C9); indefensible framing 4 (C1, C4, C5, C12); defect now fixed and reportable 2 (C5's two causes are shared with C6, counted once each as C5 and C6). New subsections required: 5 (effect-size robustness, GSA, South Korea 1987, comparative backtest with the collapse scope limit, L2 ablation).

Documents still to produce, in the locked execution order, after Phase 2 delivers real outcomes: South Korea 1987 section, effect-size robustness subsection, expanded LLM-role subsection building on VI-B, Response to Reviewers covering all eight Reviewer 1 points and all four Reviewer 2 points on the IEEE template, highlighted-changes PDF with all edits including grammar in yellow, clean final manuscript, and conditionally the Byline Change Request justification (PEND-10).
