# Adversarial review: the revision plan and the minimum publishable claim set

Reviewer: `senior-reviewer`, 2026-10-29. Target: the six-item claim set, the eight
decisions in memory 5j, the run strategy, and `docs/gsa_scope.md`. Simulated against
the literal decision letter in memory 5k. Every finding below was verified against
live source or against the tracked audit trail in this repository, not against prose.

---

## VERDICT: REJECT

Not "reject the paper that does not exist yet". Reject the claim set as currently
specified. Four of the six claims are refuted by one file each, and the one claim the
whole empirical case rests on, claim (c), is refuted by a two-line `if` statement that
a reviewer with repository access finds in under two minutes.

The revision is honest, unusually so. It is not yet technically sound, which is
Reviewer 2's question 2, and he answered No to it once already.

---

## 1. Kill shots, ranked by how fast a hostile reviewer finds them

### K1. CVES L2 has exactly one reachable rule, and its article labels are MFU's own numbering applied to six foreign constitutions. (60 seconds, one file)

`engine/cves.py:378-437` contains three violation rules, each with a hardcoded article
string: Article 9.4 (coup signal on a civilian chain), Article 2.4 (`rights_violation`
when `RIGHTS_SUSPENDABLE` is False), Article 8.6 (`budget_weight` outside [0, 1]).

Two of the three are provably unreachable:

- **Article 2.4 is dead code.** The L1 decision schema (`engine/cves.py:139-160`)
  declares exactly four fields: `budget_weight`, `ethnic_weights`, `coup_signal`,
  `reason`. `l1_parse` returns `validated.model_dump()`, so the dict L2 inspects can
  never contain a `rights_violation` key. The non-Pydantic path is the same:
  `parse_decision` (`engine/elite_agents_v3.py:290-319`) whitelists the same four
  keys. `grep -rn rights_violation engine/` returns three hits, all three inside the
  dead rule itself. No prompt, no schema and no parser anywhere produces that field.
- **Article 8.6 is dead code.** `budget_weight` is clipped to [0, 1] at
  `elite_agents_v3.py:297` and `:314`, and again by `clamp_bw` at `cves.py:147-151`,
  before L2 ever sees it.

So L2 has one reachable rule, and it fires only on civilian chains. The tracked audit
trail confirms this exactly: across every CVES violation file in repository history,
4,176 + 13 = 4,189 rows, **100 percent are scenario A and 100 percent are
`"article_injected": "Article 9.4"`**. There is no `cves_violations_C.jsonl`,
`_TH`, `_PK`, `_SK`, `_CL` or `_DE` file at all.

Compounding it, L3's theory components (Acemoglu-Robinson inclusiveness, Lijphart
consensus) are skipped whenever `n_ethnic < 2` (`cves.py:496-534`), which is South
Korea (1), Thailand, Chile and Germany (0). Verified coverage:

| Scenario | L2 Art 9.4 | L2 Art 2.4 | L3 theory |
|---|---|---|---|
| A (self-designed) | live | dead (no schema field) | live |
| C | never (military) | dead | live |
| PK | never (military) | dead | live |
| TH | never (military) | dead | skipped (0 groups) |
| SK | live | dead | skipped (1 group) |
| CL | live | dead | skipped (0 groups) |
| DE | live | dead | skipped (0 groups) |

Thailand produces no constitutional CVES signal of any kind. Scenario A is the only
constitution for which the instrument is fully operational, and it is the one the
author wrote himself.

**Consequence for claim (a).** "CVES as a measurement instrument with per-article
attribution over real, historically enacted constitutions" is not supported. The
instrument has produced zero article attributions for any real constitution in its
entire history, has one reachable article, and labels that article with an MFU
article number regardless of which constitution is active. Note that the submitted
manuscript was *more careful* than this claim: its abstract scopes the 4,176 to
Scenario A and frames C as permission, not attribution. The proposed claim escalates
past what was already submitted and past what the code can do.

**Sentence Reviewer 2 writes:** *"The paper's primary claimed contribution is an
article-level runtime enforcement record. Inspection of `engine/cves.py` shows the
constitutional layer contains three article rules, of which one is reachable: the
second tests a decision field that the authors' own L1 schema (`cves.py:139-160`)
cannot produce, and the third tests a range that the parser has already clipped. All
4,189 enforcement events in the supplied repository cite the same article of the
authors' own designed constitution, and none arises from any of the six real
constitutions the paper claims to measure."*

### K2. The one surviving effect size is produced by a hardcoded chain-type literal, with no constitutional input on the failure side. (2 minutes, one function)

`state["corruption"]` is written at exactly two sites in the entire repository, both
inside a `chain_type` branch in `_update_states` (`model_phase3.py:785-793`):

```python
if self.chain_type == "civilian":
    state["corruption"] = float(np.clip(state["corruption"] - (iig * 0.02), 0.0, 1.0))
else:
    state["corruption"] = float(np.clip(state["corruption"] + 0.01, 0.0, 1.0))
```

`shared_data["corruption_index"]` is then overwritten from those states at `:799`,
which is the last write of the year (step 8, before data collection at step 9), so this
is the published series. The military branch reads **no constitutional field at all**.
Not the IIG floor, not the investigation trigger, nothing.

Verified empirically (rule-based, seed 42, n=60, `KA_NOVA_RESULTS_DIR` isolated), the
three military-chain scenarios' published corruption series are parallel straight
lines of slope exactly 0.0100 per year, differing only by their year-zero intercept:

| year | C (yz 0.878) | TH (yz 0.683) | PK (yz 0.637) |
|---|---|---|---|
| 1 | 0.9076 | 0.7151 | 0.6753 |
| 5 | 0.9475 | 0.7551 | 0.7153 |
| 10 | 0.9801 | 0.8051 | 0.7653 |
| 14 | 0.9917 | 0.8451 | 0.8053 |

This arithmetic reproduces every military-chain number in `docs/bias_audit.md` 3.1 to
within 0.01, including the three final-year corruption terms recovered there.

The civilian branch decays at exactly `iig * 0.02` per year. For Scenario A there is a
further verified defect, **missed by the bias audit**: the civilian IIG floor is
re-enforced at `model_phase3.py:800-806`, which runs *after* the corruption consumer at
`:788`. MFU is the only constitution with no encoded `EFFECTIVENESS_FLOOR`, so for
Scenario A `shared_data["iig_effectiveness"]` is **0.0** at the moment the corruption
term reads it, for every year from year 1 until real IIG cases begin resolving around
year 8. Traced live:

```
pre-_update_states iig= 0.31   (year 0)
pre-_update_states iig= 0.0    (year 1, end-of-year reported value 0.3002)
pre-_update_states iig= 0.0    (year 2, end-of-year reported value 0.3004)
```

So the published IIG column and the value the corruption mechanism consumes are
different numbers for Scenario A, and A's corruption is flat for the first five years
as a result.

**Consequence for claim (c).** The A-vs-C corruption gap is the difference between a
constant `+0.01` per year ramp that saturates at the variable's own clip, and a decay
whose rate is the hardcoded civilian IIG ramp for the scenarios that matter. This is
precisely Reviewer 1 point 2's wording: *"mechanically induced by thresholds, parameter
bounds, or deterministic relationships embedded in the model."* It is the same finding
that killed trust, coup and stability. Corruption is the fourth artifact, not the one
survivor.

**The GSA does not save it.** Section 5h's A/corruption run found `year_zero_corruption`
and `iig_investigation_trigger` dominant *within* Scenario A. The between-arm gap is
produced by `chain_type`, which was never a GSA parameter and cannot be. The GSA is
silent on the mechanism that produces the headline. "Both encode the same year zero and
still diverge" is true and proves nothing, because the divergence is the branch, not the
parameter.

**It also contradicts the paper's own stated mechanism.** Section VI-A: *"Regime-protective
oversight caps anti-corruption effectiveness, so corruption accumulates."* The military
branch never reads anti-corruption effectiveness. The published causal story for the
headline result is not the implemented mechanism.

### K3. The intended strongest sentence is horizon-mismatched, and it is a retreat from the submitted manuscript. (1 minute, arithmetic)

"Both constitutions encode the same year-zero corruption and still diverge by about
0.84 over fifty years" compares Scenario A at year 50 against Scenario C at its
collapse year (16 to 19). C does not exist at year 50.

The submitted manuscript already handled this honestly: *"Because Scenario C terminates
near year 16, we also report a horizon-matched comparison at year 15, where corruption
is 0.62 (A) versus 0.89 (C)"*, a gap of 0.27. After the year-zero correction the
horizon-matched gap is roughly 0.16 to 0.17 (A near 0.83, C near 1.00 at year 14 in the
verification run above). So the honest, horizon-matched divergence has roughly halved,
while the proposed headline sentence grows to 0.84 by dropping the horizon match that
the submitted paper supplied.

Reviewer 1 read that paragraph. Its disappearance is visible.

Related: **locked finding 2 is not sound as worded.** "Gap ~0.13 at year 10 to ~0.97 at
year 50, accelerating after year 20" describes a gap at year 50, and acceleration after
year 20, for a scenario that terminates at year 16.6. That is a dead scenario's terminal
value carried forward. Locked finding 4 was already corrected once for a comparable
reason; finding 2 needs the same treatment.

Also: at 0.878 the C arm reaches the 1.0 clip around year 13, before its own mean
collapse year. And on the civilian side **Germany reaches corruption exactly 0.0 by
year 7 and Chile by year 13**, and both stay there. So the paper's only quantitative
metric is pinned at a boundary for three of seven scenarios. Any seven-scenario
corruption figure will show flat lines at 1.0 and at 0.0.

### K4. Table 6's own numbers do not reconcile against the shipped audit trail. (5 minutes, one regex)

The structured decision is not logged. `decision_output` in
`results_phase3/elite_decisions_{A,C}.jsonl` is a prose label
(`"Military stability assessment under 2008 Constitution Section 40c"`), and
`conditions_at_decision` holds five scalars. The actual decision survives only inside
the free-text `reasoning_text`. Parsing it:

| quantity | shipped log | Table 6 / paper |
|---|---|---|
| C coup signals emitted | 6,009 | 6,006 (reconciles) |
| **A coup signals emitted** | **4,570** | **4,176 intercepted, "100% corrected", "zero uncorrected"** |
| A, by Chief Justice | 4,070 emitted | 3,690 intercepted |
| A, by President | 294 emitted | 265 intercepted |
| A, by Senior General | 148 emitted | **163 intercepted** |

394 Scenario A coup signals (8.6 percent) have no corresponding L2 interception record,
and the Senior General has more interceptions logged than emissions, so the two counts
are not even a clean subset relation. 35,069 of 35,383 rows carry exactly one
`coup_signal` value and only one row carries two, so this is not a double-counting
artifact.

Further reproducibility gaps in the same files, all one command away:

- Every one of the 35,383 and 12,033 rows carries `"run": 0`. There are 350
  `(year, agent)` cells with 100 to 106 rows each, so the 100 Monte Carlo runs are in
  there but **cannot be separated**. Reviewer 1 point 8 names random seeds explicitly.
- 35,383 rows against a stated design of 35,000, with the excess concentrated in year 0
  (106 per agent).
- `results_phase3/` contains no `suppression_log_*` file, yet Table 6 reports a
  suppression rate.

This is the number the entire reframe is about to lead with, and it does not tie out
against the package the reviewer is being invited to clone.

### K5. Substrate invariance is entailed by the coupling design, not discovered. (3 minutes, two files)

The generative layer's total influence on the simulation is three values written at
`engine/elite_agents_v3.py:1158-1163`:

1. `elite_budget_impact = clip(mean(budget_weight) * 0.15, 0, 0.15)`, consumed at
   `agents/citizen.py:916-926` as `transfer = income * budget_impact * eth_weight * 0.30`.
2. `elite_ethnic_weights`, explicitly normalised to mean 1.0 at `:1124-1125`, so only
   relative dispersion survives. The consumer indexes it through a hardcoded Myanmar
   ethnic-name list (`citizen.py:919`) with `eth_idx = 0` fallback, so for the four
   scenarios with 0 or 1 encoded ethnic groups every citizen resolves to index 0.
3. `elite_coup_signal`, which the civilian chain suppresses unconditionally and
   double-locked (`:1137-1156` plus CVES L2).

A single scalar bounded to [0, 0.15], a mean-normalised vector whose mean is destroyed
by construction, and a boolean that is suppressed on four of seven scenarios. KPI
invariance below 0.003 is the arithmetic consequence of that coupling.

Claim (d) proposes to report this as "a negative result for the field", currently
"under-claimed". It is over-claimed. It is a property of this model's coupling, not a
finding about generative agents in governance simulation. And Reviewer 2 point 4
already said the quiet part: *"it also shows that the LLM is currently only weakly
connected to the main simulation results."* Answering that observation by promoting it
to a contribution will not move his No.

### K6. The GSA scope guard installed today blocks the GSA deliverables the same session promised. (3 minutes, one call)

`_gsa_scope_violations` now raises before sampling. Verified live, violations per
scenario: A 0, C 6, SK 5, TH 7, PK 6, CL 5, DE 7. So `run_sobol_gsa` refuses to run for
**all six non-A scenarios**.

That collides with two commitments made the same day:

- **Memory 5j decision 6**: `coup_risk` goes into the Sobol GSA so it can "quantify how
  much of Scenario C's collapse it drives". Requires a C run. Now raises.
- **Register PEND-3**: re-run C/`trust_index` after the propagation fix. Now raises.
  `docs/gsa_scope.md` Part 3 separately says do not re-run it. Two of today's
  authoritative documents disagree.

The error message offers "restrict to the modelling constants only" as the way out.
**There is no such code path.** `run_sobol_gsa` has no parameter-subset argument; the
only escape is `allow_unscoped_params=True`, which publishes a result the project's own
documentation calls invalid.

Net position: the sensitivity analysis is a Scenario-A-only instrument. Reviewer 2
point 2 asks about "many manually chosen constitutional and feedback parameters". The
deliverable covers the one constitution that is entirely manually chosen and refuses to
cover the six real ones, and the three feedback constants it does cover are byte-identical
across all seven encodings (`docs/bias_audit.md` 2.4), so there is nothing per-country
to measure. That is answerable, but only by saying it out loud.

### K7. Experiment class (ii) currently produces no validated output at all.

The five-country class exists to answer Reviewer 1 point 5. Current best measurement
(`docs/bias_audit.md` 3.1, full scale, 15 runs, post-fix):

| scenario | simulated final year | real |
|---|---|---|
| C | 15.3 | ~12.68 (2008 to 2021) |
| TH | 19.3 | 9+ years, still in force, zero coups |
| PK | **23.8** | 14.61 (1985 RCO to 1999) |
| CL | 49.0 (survives) | still in force, 45 years |

Pakistan was the strongest backtest in the whole roster on the strength of a 15.6-versus-14.61
match. At full scale after the fixes it is 23.8 against 14.61, a 63 percent overshoot.
That match is gone, and the plan is still written as though it holds (register D2's
Pakistan sentence, PEND-12).

On the corruption axis, the subset of outputs most naturally backtested, Thailand's
simulated corruption rises to roughly 0.89 by year 19 against a real V-Dem series that
is flat to slightly improving from 0.683. Germany's and Chile's simulated corruption sit
at exactly 0.0 from years 7 and 13 onward. So there is no model output, for any of the
five new countries, that currently matches its real trajectory.

**Reviewer 1's literal wording matters here and the record has drifted.** He wrote
*"Historical backtesting, even for a restricted subset of model outputs, would
considerably strengthen the evidence."* A restricted subset of **outputs**, not a
restricted subset of **cases**. Memory 5j decision 2 and register D2 read it as licensing
the declination of two of five countries. It does not. It licenses backtesting fewer
metrics. Decision 2 declines the outcome axis for Thailand and Chile and the data shows
the corruption axis also fails for them, so what is actually on offer is a declination of
every available output for two of five cases, plus a failed match on the third.

And the surviving comparative claim, the two-axis finding, is a V-Dem and
constitutional-text reading of real countries (memory 4a). It requires neither the
engine nor CVES. Claim (e) concedes this by scoping it to "qualitative, text-level".
A qualitative clustering of constitutional provisions, hand-coded by the authors with no
coding scheme and no reliability statistic, is not a computational contribution and will
not move Reviewer 2's question 1.

### K8. The register's own strongest sentence is stated with two superseded numbers.

`docs/manuscript_corrections_register.md:68`, D1 guardrail 3, the sentence designated as
"the strongest single sentence available for corruption":

> both constitutions encode the same `YEAR_ZERO_CORRUPTION` = 0.72 ... and still diverge
> by approximately 0.88 over fifty years

0.72 is the value corrected today; 0.878 is live in both files (verified). 0.88 is the
pre-correction gap; 0.84 is the post-correction figure. The register is declared the
authoritative source the manuscript and the Response to Reviewers will both be built
from. Its global precondition G2 ("bug #11 is still partially unfixed ... writing cannot
begin") is also stale as of the same day. `docs/bias_audit.md` 5.6 and
`docs/calibration_provenance.md:338` both report `analysis/kpi.py:99` as a stale 0.72;
it was fixed to 0.878 hours later. Four documents written in one day already disagree
with the code and with each other.

### K9. Figures and AI disclosure: zero progress, and the schedule is wrong.

Reviewer 1 point 6 and point 7 remain at zero. The plan schedules them for "one to two
days after the runs" (PEND-11). The manuscript has 8 figures; **Figures 1 to 4 are
schematic diagrams** (architecture, annual sequence, elite chain, CVES pipeline) and do
not depend on run output at all. These are the most likely referents of *"some graphical
elements appear highly stylized or synthetic"*. They can be redrawn today and have not
been touched in two months. Point 7 needs a factual determination about how those
diagrams were produced, which nobody has made.

In a binary venue, an explicit, visible, unmet request is a rejection path on its own,
and the reviewer who made it is the one described as detailed and specific.

---

## 2. Specific questions asked, answered directly

**Is claim (c) safe?** No. See K2 and K3. The hole is not in the "same year zero"
argument, which is valid as far as it goes. The hole is that the argument is about a
parameter while the divergence is produced by a branch, and the GSA cannot see branches.
The ceiling effect is real and is the smaller problem; the larger one is that the C arm
has zero constitutional input to its corruption trajectory.

**Does the instrument framing survive the enforcement record?** No, and it is worse than
the degeneracy concern already recorded. The hostile reading is not merely "one
degenerate signal that the instrument suppresses". It is "the instrument has one
reachable rule, two provably dead rules, and has never attributed anything to any real
constitution". That is not survivable as claim (a) is worded. It is survivable as
"a single-rule runtime enforcement log with per-decision provenance", which is a much
smaller claim and probably not enough for Reviewer 2's first form question.

**Is the reading of Reviewer 1 point 3 too convenient?** Yes. His sentence is a
disjunctive question: *"whether the generative component materially contributes to the
simulation outcomes **or** primarily serves as a decision-provenance and runtime-validation
mechanism."* He names the alternative; he does not endorse it. The phrase *"an important
result"* attaches to the LLM-versus-rule-based parity finding, not to the instrument
role. Memory 5k Recalibration 1 reads "names the alternative" as "hands us the framing",
which is an inference, not the text. The equally natural reading is a weakness diagnosis
phrased as a question: if the answer is "provenance only", the follow-up is "then why is
the generative component in this paper, and why is it contribution 1?" That question gets
sharper, not softer, once K5 shows the coupling makes the invariance inevitable. Adopting
the instrument framing is defensible and is the right direction; claiming it is
reviewer-endorsed and therefore de-risked is not. (The characterisation of what the
reviewer would then ask is my speculation; the textual point about the disjunction is not.)

**Does the two-experiment-class split work?** As presentational honesty, yes, and it is
clearly better than the undifferentiated claim. As science, no, but not for the reason
anticipated. The "post-hoc partition" attack is available and weak, because the partition
follows a defensible principle (shared external layer versus per-country realism) and
memory 5f shows the choice changes no headline number. The strong attack is K7: class (ii)
has produced nothing that validates, and its headline finding does not come from the
simulation. A reviewer does not need to allege post-hoc partitioning when he can ask what
class (ii) demonstrated.

**Is decision 2 survivable?** The decision itself, keeping the engine symmetric, is right
and should not be reopened. The *disclosure* as currently drafted (register D2's
replacement paragraph) is good prose. What is not survivable is answering point 5 with a
declination for two of five cases while the third case's numerical match has silently
disappeared (23.8 against 14.61). Honest declination plus one failed match reads as
evasive. Honest declination plus one *disclosed* failed match plus a genuine
restricted-subset-of-outputs backtest on something that does work reads as rigorous.
Right now the first is on offer.

**The single fastest kill with repo access and thirty minutes?** K1. Three greps in
`engine/cves.py` plus one `jq`-equivalent over `cves_violations.jsonl`. It takes about
one minute, it lands on the paper's self-declared primary contribution, and it is the
claim the revision proposes to lead with.

---

## 3. Per-point verdicts against the twelve literal points

"Answered" means the deliverable exists and is responsive. "Hostile accepts" is the
separate and harder question.

### Reviewer 1

| # | Literal ask (abbrev.) | Verdict | Hostile accepts? |
|---|---|---|---|
| 1 | "Additional scenarios **and/or** systematic parameter sensitivity analysis ... not primarily determined by the selected parameterization" | **Answered.** Seven encodings plus four Sobol runs. The and/or means either suffices and both were attempted. | **Partially.** He gets breadth, then finds the GSA runs on one scenario and the seven scenarios do not share controls. He will not call this unanswered; he will call it incomplete. |
| 2 | "not mechanically induced by thresholds, parameter bounds, or deterministic relationships embedded in the model" | **Answered in the negative for three of four, NOT answered for the fourth.** K2 shows corruption is also mechanically induced. | **No.** The honest answer is now "all four are", and the plan still claims one survivor. Being caught claiming a survivor is worse than conceding all four. |
| 3 | "whether the generative component materially contributes ... or primarily serves as a decision-provenance and runtime-validation mechanism" | **Partially answered.** The instrument answer is chosen, which is responsive to the disjunction. | **No, as currently evidenced.** K1 (one reachable rule) and K5 (invariance entailed) together make "provenance mechanism" read as "unnecessary component". |
| 4 | "investigated more thoroughly rather than primarily deferred ... any discrepancy between theoretically expected parameter limits and simulated outcomes should be explained" | **Answered. The single best-answered point of all twelve.** IIG C = 0.722 traced to `institutions/iig.py:229-291`, fixed, explainable with file and line. | **Yes.** This one is genuinely done. Stop working on it. |
| 5 | "Historical backtesting, even for a restricted subset of model **outputs**" | **Not answered.** K7. Declination for 2 of 5 cases, the Pakistan match gone at 23.8 vs 14.61, no surviving output that matches reality for any of the five. | **No.** And the paraphrase drift ("subset of cases") must be corrected in the record before the response is drafted. |
| 6 | figures "regenerated directly from the underlying data/model as publication-quality vector or high-resolution ... Fonts, labels, symbols, line weights ... consistent" | **Not answered.** Zero progress, and Figures 1-4 never needed the runs. | **No.** This is the cheapest rejection to avoid and the one most certain to be checked. |
| 7 | "If generative-AI tools were used to create or substantially modify any figures ... transparently disclosed" | **Not answered.** The underlying fact has not even been established. | **No.** A one-paragraph fix that nobody has done. |
| 8 | "constitutional encodings, parameter values, **random seeds, LLM configuration, prompts, CVES rules**, and statistical procedures" | **Partially answered.** Encodings and CVES rules exist and are readable. Against it: "All runs are seeded" is still false and unresolved (PEND-6), the shipped logs carry `run: 0` on every row, the structured decision is not logged, Table 6's A column does not tie out (K4). | **No, not yet.** This point is closable at low cost and is currently open in three verifiable places. |

### Reviewer 2

| # | Literal ask (abbrev.) | Verdict | Hostile accepts? |
|---|---|---|---|
| 1 | "only one very extreme constitution pair, so it is still difficult to know how well the approach would work for **more similar constitutions**" | **Answered in form.** Three independently sourced guardianship constitutions is a direct hit on the wording. | **No, and this is the most dangerous inversion in the revision.** Within the engine the three near-twins differ only in year-zero intercept and IIG floor: identical collapse mechanism, parallel corruption lines of identical slope (K2). The revision therefore demonstrates that the approach does **not** discriminate among similar constitutions. He asked how well it works on similar constitutions and the answer the code gives is "it does not separate them". |
| 2 | "many manually chosen constitutional **and feedback** parameters drive the simulation" | **Answered. Cleanest conversion of the twelve.** The three feedback constants entered the GSA with lower bounds reaching zero, and the result (trust floor ST = 1.00, rights bonus S1 = 0.99) concedes his point with numbers. | **Partially.** He will note the GSA covers Scenario A only (K6) and that the feedback constants are uniform across all seven encodings, so no per-country sensitivity was measured. Still, this is the second-best-answered point. |
| 3 | "two metrics remain constant, and the reported IIG effectiveness under Scenario C does not match the expected behavior ... **resolved before publication**" | **Answered.** North star (bug #3), ethnic harmony (bug #22), IIG (bug #10), each with a named cause. | **Mostly yes.** Caveat: ethnic harmony is now live but driven by Myanmar's census for all seven scenarios, with two unresolved calibration mismatches (U3). "Unfrozen but miscalibrated and excluded from cross-country claims" is a partial resolution of a point that said "resolved before publication". |
| 4 | "The LLM and rule-based versions produce almost identical overall outcomes ... the LLM is currently only weakly connected ... The role and value of the generative-agent component should therefore be demonstrated more clearly" | **Not answered, and the planned answer restates his objection as a contribution.** K5. | **No.** The L2 ablation is the only lever and see the warning below about what it will actually show. |

**Score as a returning reviewer would tally it.** R1: one point fully answered (4), two
answered with material gaps (1, 2 in the negative), five open (3, 5, 6, 7, 8). R2: two
answered (2, 3), one answered in form and inverted in substance (1), one open (4).
That is not a resubmission that moves three No answers to Yes.

---

## 4. On the eight decisions in memory 5j

| Decision | Verdict |
|---|---|
| 1. d only where variance is two-sided | **Right, and now insufficient.** K2 adds a fourth governing constant (the corruption drift literals at `model_phase3.py:785-793`). The decision must extend to corruption, which means reporting no Cohen's d at all. That is survivable; claiming one survivor is not. |
| 2. Engine stays symmetric, no outcome backtest for TH/CL | **Right decision, wrong justification, and now resting on a dead number.** Keep the symmetry. Fix the Reviewer 1 point 5 paraphrase ("outputs", not "cases"). Re-measure and disclose Pakistan at 23.8 before any backtest sentence is drafted. |
| 3. Two labelled experiment classes | **Necessary and not sufficient.** Does the honesty job; does not give class (ii) a result. See K7. |
| 4. L4 "flag" | **Settled, correct, well evidenced from the spec.** Nothing to do. |
| 5. Real tax brackets plus inertness disclosure | **Correct call, and the inertness finding is a genuine strength.** The refusal to rescale brackets to fit the engine is exactly the right instinct. One warning: the disclosure must say the schedules are *encoded and inert*, not *used*, or it joins `RIGHTS_VIOLATION_TRUST_DROP` as encoded-but-unreachable content presented as live. |
| 6. `YEAR_ZERO_COUP_RISK = 0.25` stays, disclosed, plus GSA | **The disclosure half is right. The GSA half is currently undeliverable** (K6): `run_sobol_gsa(scenario="C")` raises. Either implement the parameter-subset path or drop the promise. Do not ship a `--gsa-allow-unscoped` result as the answer. |
| 7. North star decomposed, not re-weighted or retired | **Right, and the strongest of the eight.** Decomposition plus `docs/bias_audit.md` 3.1's term table is a better answer than any re-weighting. Publish the table that shows three of seven terms at an identical ceiling for all four civilian scenarios; it is the most credible thing in the revision. |
| 8. Source what is sourceable, label the rest | **Right.** The explicit refusal to retrofit coincidental matches as citations (`calibration_provenance.md`, the ~2,000-candidate scan note) is exactly the standard this paper needs. |

---

## 5. On the run strategy, the budget, and `docs/gsa_scope.md`

**The reallocation toward the L2 ablation and away from a fifth LLM scenario is correct,
and for a stronger reason than the one given.** The stated reason is that substrate
invariance makes a fifth scenario low-value. The real reason is K1: SK, CL and DE can
only ever reproduce Article 9.4 again, and TH and PK can produce no L2 record at all. The
marginal instrument value of all five new LLM runs is close to zero as the code stands.
Germany becomes worth paying for only if Article 2.4 is made reachable, since it is the
one other constitution with `RIGHTS_SUSPENDABLE=False`.

**Warning the plan does not contain: the L2 ablation will probably embarrass the paper's
own mechanism story, and the team should decide the framing before the run, not after.**
Section VI-A attributes Scenario A's zero coup probability to the constitution:
*"Article 9.4 - coup as highest treason - makes the terminal transition unreachable."*
The ablation disables that suppression, including the second lock at
`elite_agents_v3.py:1137-1156`. The expected result is that A's coup probability moves off
0.000, which demonstrates that a headline result was produced by the *validation harness*,
not by the constitutional provision. That is a real and interesting finding about CVES
materiality, and it is the single best available answer to Reviewer 2 point 4. It is also
a direct contradiction of VI-A as written. Run it. Pre-commit to reporting it either way.

**Budget mechanics.** The asymmetric-N disclosure is right. The throughput benchmark first
is right. One correction to the cost logic: the claim that the paid runs "do only what
they alone can do, produce a CVES enforcement record per constitution" is false for C, TH
and PK, which is about 11 to 13 dollars of the allocation producing zero L2 records by
construction. C still earns its money, because the 6,009 permitted signals are the
contrast, and that contrast is reproducible from the shipped log. TH and PK do not.

**`docs/gsa_scope.md` specifically.** The three-class split is correct analysis and the
correction of its own brief (refusing to fold `coup_risk` in with the modelling constants
because it is per-country differentiated) is exactly the kind of precision this project
needs. Two problems:

1. The per-run publishability table is sound for all four rows, but it is silent on the
   consequence that the guard blocks every non-A scenario, which breaks decision 6 and
   PEND-3. A scope note that makes a promised deliverable impossible must say so.
2. The published scope sentence in Part 2 describes perturbing the modelling constants
   "on whichever scenario the metric under study is live for". That sentence describes a
   capability the code does not have. Implement the subset path or change the sentence.

---

## 6. What would change my verdict, ranked by effort

**1. Extend decision 1 to corruption and disclose the fourth constant. Writing only, no
compute. Highest ratio of anything on this list.** State that there are four governing
constants, not three, and name `model_phase3.py:785-793` with its two literals alongside
the three `rights.*` fields. Report no Cohen's d at all. Replace the 0.84 sentence with
the horizon-matched comparison, which the submitted manuscript already contains. This
single change converts Reviewer 1 point 2 from "caught claiming a survivor" to "answered
completely in the negative", which is the only defensible position and is the one the
project has already taken three times. It also removes K2, K3 and K8 at a stroke.

**2. Make CVES L2 have more than one reachable rule. Small code change, re-run already
committed.** Add `rights_violation` to the decision schema (`cves.py:139-160`), to
`parse_decision`'s whitelist, and to the prompts; the L2 rule and every constitution's
`RIGHTS_SUSPENDABLE` field already exist, so the rule becomes live for A and DE
immediately. Then make the article label read from the active constitution instead of the
hardcoded MFU string at `:395,421,434`, so that an interception under the 2008
constitution cites a 2008 article. Without this, claim (a) must be narrowed to a
single-rule provenance log, and I do not think that narrowed claim carries Reviewer 2's
first form question.

**3. Log the decision. Five lines, re-run already committed.** Write the four structured
decision fields into the JSONL rows instead of a prose summary, and write a real `run_id`.
Then reconcile 4,176 against 4,570 and either correct Table 6 or explain the 394. A
reviewer who checks reproducibility checks this first, and right now he finds a number
that does not tie out and an audit trail he cannot partition by run.

**4. Promote the chain-type literals to constitutional fields. Medium code change, same
re-run.** The corruption drift rates, the civilian IIG floor and ramp, `const_commitment`
(`feedback/loops.py:340`), the military 5 percent rights roll, the military IIG cap
(`loops.py:266`), and the military IIG decay rate. Do exactly what Opening 1 did for the
three rights constants: same values, now readable and perturbable. This is the difference
between "the engine is constitutionally agnostic" being a false docstring and a true one,
it makes the GSA able to see the mechanism that produces the headline, and it is the only
route by which the near-twin comparison could ever separate Thailand from Myanmar. Also
fix the ordering defect at `model_phase3.py:800-806` so the floor is applied before the
corruption consumer at `:788`, or document why it is not.

**5. Figures 1 to 4 and the AI-provenance paragraph. One to two days, now, not after the
runs.** No compute, no intellectual risk, closes two explicit requests from the winnable
reviewer.

**6. Give experiment class (ii) one real output. Analysis work after the runs.** Pick the
restricted subset of model **outputs** that can be backtested and backtest it honestly
for all five, including the failures. Candidates: the IIG term on the military side,
which `docs/bias_audit.md` 3.2 shows genuinely tracks Thailand's real anti-corruption
floor at 9 to 10 times Myanmar's, and is the one clean positive counter-example in the
whole audit. Lead class (ii) with that and the Pakistan overshoot, not with the two-axis
reading.

**7. Resolve the GSA deliverability contradiction. Half a day.** Implement the
parameter-subset path so the modelling constants and `coup_risk` can be perturbed on C,
or delete decision 6's GSA promise and PEND-3 and state that the GSA is Scenario A only.

**8. Own the discontinuity in the first paragraph of the Response to Reviewers.** Memory
already says this; it is correct and it is not optional. Every number changes, the same
two reviewers return, and four documents written in one day already disagree with the
code. Enumerate the defects your own audit found, state that all values are recomputed,
and give the audit a name. Discovered by a reviewer this is fatal; declared first it is
the best thing about the paper.

---

## 7. What is genuinely strong, so effort stops going here

- **Reviewer 1 point 4 is finished.** Best-answered of the twelve. Do not polish it further.
- **Reviewer 2 point 2 is nearly finished** and the GSA self-incrimination is the most
  credible move in the revision. Write it in the order `docs/manuscript_corrections_register.md`
  P4 specifies: analysis, finding, consequence. Not criticism then defence.
- **The north-star decomposition (decision 7) plus `bias_audit.md` 3.1's term table** is
  the most publishable new artifact in the project. Three of seven terms at an identical
  ceiling for four different real constitutions, measured not argued, is exactly the kind
  of self-scrutiny both reviewers said was missing.
- **The tax-bracket inertness finding and the refusal to rescale**, and the
  calibration-provenance refusal to retrofit coincidental matches as citations. These are
  the two places where this project's standards are visibly above the venue's.
- **The one true headline claim that no finding in this review touches:** the same
  behaviour, a coup signal from an elite agent, is unlawful under one encoded constitution
  and lawful under the other, with 4,176 interceptions on one side and 6,009 permissions
  on the other, and both counts are recoverable from the shipped log. That is a real,
  reproducible, article-attributable contrast. It does not depend on the corruption
  divergence, the effect sizes, the external layer, the north star or the five new
  countries. If the paper has one sentence, it is that one, not the 0.84.

---

## Verification note

All runtime activity in this review used `KA_NOVA_RESULTS_DIR` pointed at a throwaway
directory outside the repository. No `--use-llm`. No source, constitution or other
agent's document was modified. Heaviest run was 60 citizens for 14 years.
`git status -- results_phase3/` confirmed clean after.
