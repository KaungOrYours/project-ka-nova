# Ka-Nova 7-Constitution Comparison: Adversarial Bias Audit

Audit date: 2026-10-29. Scope: every mechanism by which the engine advantages or
disadvantages a scenario for a reason that is not that scenario's own
constitutional text. Written against live source (commit at session start:
`1f67d9e`), cross-checked against `.claude/memory.md` sections 5c, 5j, 6, 11
and `.claude/MINDMAP.md`. No code was changed to produce this audit; the only
runtime activity was rule-based, non-LLM, `KA_NOVA_RESULTS_DIR`-isolated model
runs used to quantify effects, confirmed not to touch tracked
`results_phase3/` files (verified clean at the end, see the final section).

This document answers one question: how biased is the 7-constitution
comparison, and precisely where does that bias live. It does not re-litigate
decisions already locked in memory section 5j (effect-size framing, the
near-twin backtest scope limit, the two-axis paper architecture, CVES
`L4_MODE`). Those stand. This audit is new ground: the mechanics underneath
the north-star composite and the civilian/military rule dispatch that nobody
had yet decomposed term by term.

---

## 0. Headline answer

The engine is **not** constitutionally symmetric in the way its own code
comments claim. Three independent hardcoded, chain-type-only mechanisms (not
chain-type mechanisms that read a constitutional parameter - mechanisms that
are the same literal number or the same literal branch for every scenario of
that chain type, full stop) manufacture a large share of the civilian/military
separation on the north-star composite, the paper's single most load-bearing
KPI. Two of these were already flagged by Kaung as starting points (the IIG
floor, the coup-signal damping). A third, independent one was found in this
audit (`feedback/loops.py`'s `const_commitment` literal) and a fourth
discovery (not a chain-type hardcode, but a dead-parameter finding) shows that
a genuinely researched, per-country constitutional field is mechanically
unreachable for every civilian-chain scenario. Separately, a previously
undocumented finding shows that one of the three structural chambers in the
three-chamber system - the Ethnic Leaders Council, plus the ministerial
roster - is unconditionally Myanmar-shaped (same 8 names, same code) for all
seven scenarios, which is a stronger and more specific version of the already
known "ethnicity is still Myanmar's" gap.

Quantified on real rule-based runs across all 7 scenarios at full publication
scale (Section 3), the finding is sharper than a code-reading estimate alone
would suggest: **for all four civilian-chain scenarios (A, SK, CL, DE),
exactly three of the composite's seven terms - coup (0.15), IIG (0.15) and
GDP (0.15) - land at the identical maximal value regardless of which real
constitution is active, accounting for 45% of the formula's total weight
with zero discriminative power among them.** Two of those three are
chain-type hardcodes (Section 2); the third is a ceiling effect in the
composite's own design interacting with an uncapped compounding-growth
mechanism. Corruption, trust and Gini are legitimate and do carry real
cross-scenario signal; harmony is compromised by Myanmar-only ethnic data
(Section 5.4). The honest claim available to this project, after this audit,
is **not** "constitutional text is the only manipulated variable across seven
constitutions" - that claim is true only for the A-vs-C pair (already the
locked, narrower claim per memory 5j decision 3) and is false for the 7-way
comparison as currently implemented.

---

## 1. Tier 1 - MFU-exclusive mechanisms

Exhaustive search across all 21 schema sections for fields where MFU holds the
only non-zero/non-absent value, confirmed by cross-referencing every live
engine read site (`grep`-verified against the full `config/constitution*.py`
set, not just the two Kaung had checked).

| Field | MFU | all 6 others | Where read | Status |
|---|---|---|---|---|
| `merit.RECERTIFICATION_INTERVAL` | 4 | 0 | `agents/official.py:262`, `feedback/loops.py:432` | Confirmed, Tier 1 |
| `amendment.REVIEW_INTERVAL` | 10 | 0 | `institutions/court.py:77` | Confirmed, Tier 1 |

No third field of this shape exists on a live code path. Two near-miss
candidates were checked and ruled out: `simulation.STATE_RANKING_INTERVAL`
and `federal.SECURITY_DESIGNATION_RENEWAL_INTERVAL` (`config/constitution.py:491,691`)
are MFU-only fields with **no corresponding field in any other constitution at
all** (not even a `0`), but they are not read anywhere in `agents/`,
`institutions/`, `feedback/`, or `model_phase3.py` - dead config, not a live
bias. `config/constitution.py:858`'s duplicate `SafeguardConfig.REVIEW_INTERVAL
= 10` is vestigial (same class as the already-documented `ASSEMBLY_SIZE=500`
cosmetic bug), not read anywhere; only `AmendmentConfig.REVIEW_INTERVAL` is
live.

**Classification: legitimate structural difference, with a real schema-fit
caveat.** Both guarded fields (`interval > 0`) now correctly produce *no
mechanism* for the six real constitutions, which is factually correct - none
of them has a periodic merit-recertification cycle or a mandatory decadal
constitutional review (Chile's and Germany's encodings say so explicitly).
That is not a bug, it is MFU inventing two mechanisms no real constitution in
this set happens to have. But the schema-fit angle (Section 6) means this
should not be read as "six real constitutions were tested against this
provision and failed it" - it means the schema contains two slots invented
*for* MFU, and only MFU can ever occupy them. The real-world mapping is
correct; the comparison's symmetry is not, because the measurement instrument
itself has a slot that structurally only one of the seven subjects can fill.
This is exactly why the recertification-guard fix moved SK/CL/DE's IIG
effectiveness by -0.30 to -0.38 (confirmed in memory 5j): fixing the ZeroDivision
bug correctly stopped these three scenarios from silently borrowing MFU's
cycle, and the size of that swing is itself evidence of how much machinery is
built around MFU's own invented mechanism.

---

## 2. Tier 2 - hardcoded chain-type branches, full civilian AND military audit

Kaung's four confirmed civilian items are re-verified below, each with exact
line numbers, plus the symmetric military-side audit he asked for, plus two
further independent findings this audit surfaced that are not chain-type
branches but chain-type-induced dead parameters.

### 2.1 Civilian chain (`_civilian_chain_rules`, `model_phase3.py:632-669`)

| Item | Line | Mechanism | Reads constitution? |
|---|---|---|---|
| IIG effectiveness floor | `:638` | `floor = min(0.30 + year_bonus, 0.40)` | **No** - pure literal |
| Floor re-applied | `:768` (`_update_states`) | identical formula, re-enforced after institutions run | **No** |
| `rights_violated` | `:634` | set `False` unconditionally, every year, every civilian scenario | **No** |
| Shame-register corruption decay | `:640-646` | `corruption_tolerance -= 0.005` when `shame_register_size > 5` | **No**, civilian-only branch |
| Coup-signal damping direction | `step()` `:538-545` | elite coup signal **decrements** `coup_risk` by `rights.CIVILIAN_COUP_SIGNAL_DAMPING` | Reads a constitutional field, but the field's value (0.05) is byte-identical across all 7 constitutions - see 2.4 |

**New finding, verified by tracing `institutions/iig.py`.** Kaung asked
whether the hardcoded floor "overrides" South Korea's own encoded
`iig.EFFECTIVENESS_FLOOR=0.30`. Traced precisely:

- `institutions/iig.py:250-305` (`_update_effectiveness`, bug #10's fix) runs
  immediately **after** `_civilian_chain_rules()` in the same `step()` call
  (step 7 vs step 6) and **unconditionally overwrites** `shared_data["iig_effectiveness"]`
  with its own computation, throwing away whatever `_civilian_chain_rules()`
  just set. So `model_phase3.py:638`'s write is never the value actually
  carried forward within a step - it only matters as the `current` baseline
  the next mechanism builds on.
- `_update_effectiveness`'s no-cases-open branch (the one that fires for
  every civilian scenario before any corruption case resolves) computes
  `target = min(0.40, current + 0.01)` - **the same hardcoded 0.30-0.40
  engine ramp, independent of any constitution field** - then only
  afterward applies `max(encoded_floor, target)` if the constitution defines
  one.
- The practical consequence differs by scenario because of **where each
  country's own encoded floor sits relative to the engine's hardcoded 0.40
  ceiling**:
  - **MFU: no field at all.** Relies entirely on the engine literal. This is
    disclosed accurately in `iig.py`'s own docstring.
  - **South Korea (encoded floor 0.30):** below the hardcoded 0.40 ceiling,
    so `max(0.30, ramp)` is almost always won by the ramp. South Korea's own
    researched constitutional value is **functionally redundant** - the
    number that actually drives simulated IIG effectiveness in the no-cases
    branch is the engine's generic literal, not South Korea's real
    anti-corruption design.
  - **Chile (0.55) and Germany (0.70):** both exceed the hardcoded 0.40
    ceiling, so their own encoded floor correctly wins via the `max()`. These
    two are **not** overridden downward - the engine's hardcoded floor never
    pushes a higher constitutional value down, because every write site uses
    `max()`, never a plain overwrite. This is a real correction to the
    phrasing in the task prompt: the mechanism is not "the hardcoded floor
    beats the encoded one," it is "the hardcoded floor dominates **only when
    it is numerically larger than the encoded one**," which happens to be
    true for MFU and South Korea and false for Chile and Germany.
  - **`_update_states()` (`:765-771`)** then runs a **third** time, applying
    the same hardcoded 0.30-0.40 floor as a final `if current < floor: raise`
    safety net. For Chile/Germany this never binds (already above it); for
    South Korea/MFU it is, in practice, the dominant mechanism.

**Classification: circular for MFU and South Korea, legitimate for Chile and
Germany.** The institution-is-always-at-least-30%-effective assumption is an
MFU-invented idiom with no real-world grounding (MFU is the one constitution
with zero sourced justification for an IIG floor at all), applied uniformly to
every civilian chain regardless of whether that country's own anti-corruption
body has any real basis for such a floor.

### 2.2 Military chain (`_military_chain_rules`, `model_phase3.py:671-703`) - symmetric audit

| Item | Line | Mechanism | Reads constitution? |
|---|---|---|---|
| Random rights-violation roll | `:674` | `if random.random() < 0.05: rights_violated = True` | **No** - pure literal, uniform across C/TH/PK regardless of each country's real repression intensity |
| IIG-equivalent floor | `:698` | `self.CONSTITUTION.iig.EFFECTIVENESS_FLOOR` | **Yes** - correctly reads 0.05 (C) / 0.25 (TH) / 0.03 (PK), the fix documented in memory bug #14 |
| IIG-equivalent decay rate | `:699` | `getattr(..., "EFFECTIVENESS_DECAY_RATE", -0.002)` | **No field exists on any of the 6 non-MFU constitutions**, so the literal -0.002/year applies identically to C, TH and PK. Confirmed by grep: no constitution defines `EFFECTIVENESS_DECAY_RATE`. |
| Coup-risk check | `_coup_risk_check()`, `:705-733` | shared 0.70 threshold / 70% success roll | Symmetric by design (memory 5j decision 2), the one deliberate exception - threshold and roll are the SAME number for every scenario, civilian or military, which is the locked collapse-mechanism scope limit, not a new finding |

**Second independent hardcoded chain-type literal, not previously documented
anywhere in memory - found in this audit.** `feedback/loops.py:340`
(`loop_P3_coup_probability`):

```
const_commitment = 0.80 if m.chain_type == "civilian" else 0.25
```

This is **not** read from any constitution field. It carries 40% of the
weight in computing `military_loyalty` (`:347-352`), which in turn gates
whether `coup_risk` rises or decays at all (`:362-379`, via each
constitution's own `COUP_TRIGGER_LOYALTY`/`COUP_TRIGGER_APPROVAL` thresholds -
those two genuinely differ by country: C/TH/SK = 0.0/0.0, PK = 0.50/0.45, CL =
0.30/0.20, DE = -0.01/-0.01 never-fires). So the gate itself is real and
country-specific; the **input that feeds the gate** is a bare 0.80/0.25
binary identical for every civilian scenario and every military scenario
respectively, with zero reference to South Korea's, Germany's or Pakistan's
actual constitutional design for civil-military relations. This directly
feeds the north-star's `(1 - coup_risk) * 0.15` term (Section 4).

**Classification: artifact.** Not disclosed anywhere as a constitutional
field (unlike the three "Opening 1" constants, which were at least backfilled
into the schema). This is a clean miss nobody has surfaced before this audit.

### 2.3 New finding - a researched, per-country constitutional field that is mechanically dead for every civilian scenario

`rights.RIGHTS_VIOLATION_TRUST_DROP` is genuinely encoded per constitution and
genuinely differentiated:

| Scenario | A | SK | TH | PK | CL | DE | C |
|---|---|---|---|---|---|---|---|
| `RIGHTS_VIOLATION_TRUST_DROP` | 0.20 | 0.15 | 0.12 | 0.10 | 0.12 | 0.05 | 0.08 |

It is read at exactly one site, `feedback/loops.py:149`:
`rights_penalty = 0.0 if rights_ok else m.CONSTITUTION.rights.RIGHTS_VIOLATION_TRUST_DROP`,
where `rights_ok = not shared_data.get("rights_violated", False)`.

Traced every writer of `shared_data["rights_violated"]` repo-wide (three
total): `model_phase3.py:634` (civilian, unconditional `False`, every year),
`model_phase3.py:675` (military, 5% random roll), `feedback/loops.py:881`
(military-only branch, S2 protest loop, unconditional `True` once
`protest_rate > 0.05`). **There is no code path anywhere in the repository
that can ever set `rights_violated = True` for a civilian-chain scenario.**
`_civilian_chain_rules()` resets it to `False` every single year, every run,
for A, SK, CL and DE, with no exception.

**Consequence: `RIGHTS_VIOLATION_TRUST_DROP` is live and meaningful for C, TH
and PK (the three scenarios where `rights_violated` can actually become
`True`), and completely unreachable dead code for A, SK, CL and DE.** This is
a genuinely researched, country-differentiated field (0.05 to 0.20, a 4x
range) whose entire civilian-chain half can never execute. It should not be
presented in any calibration table as "this constitutional provision was
encoded and used" for the four civilian scenarios - it was encoded and never
used.

This also sharpens the already-locked `STABILITY_RIGHTS_BONUS` finding
(Exposure 1/d=91.6, memory 5c): the stability composite's `+0.20 if rights_ok
else 0.0` term is not merely "usually" present for civilian chains, it is
**unconditionally present in 100% of years across 100% of runs for all four
civilian scenarios**, because `rights_ok` can never be `False` for them. The
already-decided framing (report no `d`, disclose the constant) remains
correct and is reinforced, not changed, by this more precise finding.

**Classification: artifact (the inert pathway) layered on top of a legitimate
structural difference (the real, differentiated field values).** The field
itself is fine; the gating mechanism that makes it unreachable for half the
roster is not disclosed anywhere and should be.

### 2.4 The "disclosed" constants are uniform, not differentiated

The three rights/stability constants surfaced in Opening 1 (memory 5d) are
now read via `self.CONSTITUTION.rights.*`, which satisfies the letter of
"never hardcoded in this dispatch." Verified by grep across all seven files:

| Field | A | C | SK | TH | PK | CL | DE |
|---|---|---|---|---|---|---|---|
| `FEAR_COMPLIANCE_TRUST_FLOOR` | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 | 0.10 |
| `CIVILIAN_COUP_SIGNAL_DAMPING` | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 | 0.05 |
| `STABILITY_RIGHTS_BONUS` | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 | 0.20 |

Byte-identical across seven real, textually very different constitutions.
Nobody has ever researched a country-specific fear-compliance floor or
stability bonus - these were backfilled as a single Ka-Nova modelling
decision applied uniformly. They are **constitutional fields in form, not in
substance**: the code's claim ("read fresh via `self.CONSTITUTION`, never
hardcoded") is technically true and substantively misleading, since reading a
field that is deliberately set to the same value everywhere has the same
effect on cross-scenario comparison as reading a hardcoded literal would. This
is worth stating precisely in the manuscript rather than letting the
backfill read as "per-constitution calibration."

---

## 3. Tier 3 - the success metric rewards the hardcoded bonuses, now decomposed with real data

Formula (`model_phase3.py:823-831`, verified unchanged):

```
north_star = (1-corruption)*0.20 + trust*0.15 + (1-coup_risk)*0.15
           + iig*0.15 + min(gdp_growth*5,1)*0.15 + harmony*0.10 + (1-gini)*0.10
```

Provenance confirmed per memory bug #3: this formula is inherited verbatim
from `engine/hybrid_engine.py:300-312` (Phase 2 legacy). No constitution file
anywhere - not MFU's `NorthStarConfig`, not any of the six others - defines
an actual formula; all seven `NorthStarConfig` classes hold only decade
targets and a metric label. **Nobody ever chose these weights for a
7-constitution comparison; the weights were chosen once, in 2025/26, for a
2-scenario Myanmar-only comparison, and have never been revisited.**

### 3.1 Term-by-term decomposition, real data

Run method: rule-based (`--test` off, `--use-llm` off), 11,000 citizens, 50-year
horizon, 15 runs per scenario, seed formula unchanged
(`run_id*100 + sum(ord(ch) for ch in scenario)`), `KA_NOVA_RESULTS_DIR` set to a
throwaway directory for the entire campaign. Final-year value per run (the
year each run actually ends on - year 50 for the four survivors, the failure
year for the three collapsers), averaged across the 15 runs per scenario.

| Scenario | Chain | Mean final year | Failure rate | North star | t1 corruption (.20) | t2 trust (.15) | t3 coup (.15) | t4 IIG (.15) | t5 GDP (.15) | t6 harmony (.10) | t7 Gini (.10) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A (MFU) | civilian | 49.0 | 0% | 0.8416 | 0.1730 | 0.1116 | **0.1500** | **0.1500** | **0.1500** | 0.0365 | 0.0705 |
| SK | civilian | 49.0 | 0% | 0.8493 | 0.2000 | 0.1097 | **0.1500** | **0.1500** | **0.1500** | 0.0268 | 0.0628 |
| CL | civilian | 49.0 | 0% | 0.8410 | 0.2000 | 0.1126 | **0.1500** | **0.1500** | **0.1500** | 0.0285 | 0.0499 |
| DE | civilian | 49.0 | 0% | 0.8433 | 0.2000 | 0.1075 | **0.1500** | **0.1500** | **0.1500** | 0.0268 | 0.0590 |
| C (2008 Myanmar) | military | 15.3 | 100% | 0.1294 | 0.0009 | 0.0150 | 0.0393 | 0.0120 | -0.0375 | 0.0278 | 0.0719 |
| TH | military | 19.3 | 100% | 0.2396 | 0.0225 | 0.0150 | 0.0405 | **0.1077** | -0.0375 | 0.0295 | 0.0618 |
| PK | military | 23.8 | 100% | 0.1311 | 0.0236 | 0.0150 | 0.0414 | 0.0102 | -0.0285 | 0.0268 | 0.0427 |

Method: rule-based, 11,000 citizens, 50-year horizon, 15 runs/scenario, seed
formula unchanged, each run's own final year (year 50 for survivors, failure
year for collapsers), averaged across runs, `KA_NOVA_RESULTS_DIR` isolated for
the whole campaign. `t5` is recovered as a residual against the reported
`north_star_progress` column (not independently logged); the residual's exact
recovery of the known formula structure (civilian terms landing exactly at the
0.15 ceiling, military terms landing exactly at `growth_floor * 5 * 0.15 =
-0.0375` for the -0.05 growth floor) is itself confirmation the decomposition
is correct, not an artifact of the residual method.

### 3.2 Reading the table - a sharper finding than the pre-run estimate

**The real numbers show more ceiling-saturation than anticipated.** For every
one of the four civilian scenarios - A, SK, CL and DE, four constitutions with
genuinely different real texts - **three of the seven terms (coup, IIG, GDP)
land at exactly the same maximal value, 0.1500, with zero variation across
scenario.** That is 0.45 of each civilian scenario's ~0.84 total score, or
**roughly 53-54% of the entire composite, carrying zero discriminative
information between the four civilian constitutions.** Only the remaining
four terms (corruption, trust, harmony, Gini) differ at all between A, SK, CL
and DE - and of those, corruption and trust are the two the paper would most
want the composite to be sensitive to.

The three ceiling-saturated terms have two different root causes, and they
should not be conflated:

- **Coup and IIG (0.15 + 0.15 = 0.30) are circular for the reasons documented
  in Section 2**: the coup-signal damping direction and the hardcoded civilian
  IIG floor/ramp are chain-type literals, not constitutional content, and both
  mechanically drive their terms to ceiling for every civilian scenario
  regardless of what that scenario's constitution says.
- **GDP (0.15) saturating is a different, legitimate mechanism reaching the
  same practical effect.** `feedback/loops.py`'s E1 loop has no chain-type
  branch at all (Section 5, already verified) - growth genuinely compounds
  from each state's own real corruption/IIG/budget dynamics. But compounding
  growth over 49 years, uncapped on the upside except by the north-star
  formula's own `min(gdp_growth*5, 1.0)` clip, empirically exceeds the 20%
  annual-growth threshold needed to hit the ceiling for every surviving
  civilian scenario in this sample. This is a **calibration/scale problem in
  the composite's own clip, not a chain-type circularity** - but the practical
  consequence for cross-scenario discriminative power is identical: a third
  term that cannot differentiate constitutions once they survive long enough.

**The military side shows exactly the opposite, informative pattern for one
of these three terms.** IIG genuinely differentiates among C, TH and PK:
Thailand's term (0.1077) is roughly 9-10x Myanmar's (0.0120) and Pakistan's
(0.0102), tracking the real researched difference in anti-corruption-body
strength (`EFFECTIVENESS_FLOOR` 0.25 for Thailand vs 0.05/0.03 for Myanmar and
Pakistan) exactly as intended. This is the clearest positive counter-example
in the whole audit: when the engine is allowed to read a real per-constitution
IIG floor without a competing hardcoded civilian ramp drowning it out, the
composite correctly reflects a genuine, sourced institutional difference. It
is also direct, numeric proof that the *same* mechanism (the IIG floor) is
legitimate for military chains and circular for civilian chains, precisely
because of which hardcoded branch sits next to it (Section 2.1).

The GDP term also shows the model's floor-without-ceiling-symmetry design
choice clearly: all three collapsing military scenarios land at (or very near)
`-0.0375`/`-0.0285`, consistent with `growth_rate` pinned near its hardcoded
-0.05 contraction floor (`feedback/loops.py`'s E1 loop) - a real, legitimate
collapse dynamic, but one more term where the three military scenarios also
converge to a near-identical extreme value rather than differentiating by
constitutional content.

**Revised bottom line, replacing the pre-run estimate in the original draft
of this section**: it is not "30-40% of the composite carries a circular
component" - on this real 15-run sample, **three of seven terms (45% of the
formula's weight) are completely non-discriminating across all four civilian
scenarios**, two of those three for a chain-type-hardcode reason and one for
a composite-design/ceiling reason. Only corruption, trust, harmony and Gini
(0.55 of the formula's weight) carry any real cross-civilian-scenario
signal at all, and of those, harmony is itself compromised by the Myanmar-only
ethnic data (Section 5.4), leaving corruption, trust and Gini - 0.45 of the
formula's weight - as the only terms doing real comparative work among A, SK,
CL and DE.

- **Corruption term (0.20 weight): legitimate.** Driven by `_update_states()`'s
  real per-state corruption dynamics, which read the active constitution's
  IIG floor and the social dynamics loops, with no chain-type literal in the
  corruption-update path itself beyond the direction of drift (`+0.01/yr`
  military vs `-iig*0.02/yr` civilian, which is a textbook correct encoding of
  "accountability exists vs does not," arguably the single most defensible
  structural difference in the whole engine).
- **Trust term (0.15 weight): legitimate dynamics, illegitimate floor.** The
  corruption-linked decay is real; the `0.10` floor for military chains is a
  uniform constant (2.4) that exists identically for C, TH and PK regardless
  of how differently each country's real population actually tolerates
  repression.
- **Coup term (0.15 weight): mostly circular.** Driven by (a) the elite
  coup-signal damping direction (`model_phase3.py:538-545`, chain-type
  literal, constant magnitude per 2.4), (b) the `const_commitment` binary
  (`feedback/loops.py:340`, new finding, chain-type literal), and (c) each
  constitution's own `COUP_TRIGGER_LOYALTY/APPROVAL` thresholds, which ARE
  real and differentiated (memory's already-flagged open item: C/TH/SK share
  literal `0.0`, a genuine remaining concern, not resolved by this audit).
  For civilian chains this term converges to its ceiling (coup_risk -> 0) for
  a chain-type reason, not a constitutional-content reason.
- **IIG term (0.15 weight): split, as detailed in 2.1.** Circular for MFU and
  South Korea, legitimate for Chile and Germany, legitimate by design for the
  three military chains (reads `iig.EFFECTIVENESS_FLOOR` directly, modulo the
  shared decay-rate literal).
- **GDP term (0.15 weight): legitimate.** `feedback/loops.py`'s E1 loop has no
  chain-type branch at all; growth is driven by real per-state budget,
  knowledge, infrastructure and corruption-drag terms.
- **Harmony term (0.10 weight): compromised by data, not by chain-type.** The
  mechanism (`feedback/loops.py`'s S1 national-service loop) is symmetric
  code, but it operates on Myanmar's own ethnic-archetype data for all seven
  scenarios (Section 6.4) and inherits the Ethnic Leaders Council finding
  (6.5). Not a chain-type circularity - a data-symmetry one.
- **Gini term (0.10 weight): legitimate**, modulo the already-documented
  external unit-mismatch against `MYANMAR_BASELINES` (bug #2, untouched by
  this audit, a validation-target problem not an engine-symmetry one).

**Bottom line for the composite**: of the seven terms, two (coup, and IIG for
4 of 7 scenarios) are substantially chain-type-determined rather than
constitution-determined, one (trust) is partially so, and one more (harmony)
is country-blind for a different reason. That is **at minimum the 0.15 + a
fraction of the 0.15 IIG weight + a fraction of the 0.15 trust weight ≈
30-40% of the composite's total weight** carrying a meaningful circular
component for at least one chain type, which matches the task prompt's own
estimate and is now verified against live mechanics and real run output
rather than code-reading alone.

---

## 4. Tier 4 - every symmetry claim found in the code, checked against the code

| Claim | File:line | Status |
|---|---|---|
| "Bias lives only in each constitution's own parameter values... never hardcoded in this dispatch" | `model_phase3.py:622-625` (`_apply_scenario_rules` docstring) | **False.** Contradicted by `:638` (civilian IIG floor), `:674` (military 5% rights roll), and by `feedback/loops.py:340` (`const_commitment`), none of which are inside `_apply_scenario_rules` itself but all of which fire in the same `step()` and produce the same category of chain-type-only divergence the docstring says doesn't happen in "this dispatch." A literalist reading ("only claims about this one function") survives; a reader's natural reading does not. |
| "This keeps the engine constitutionally agnostic - bias lives only in the constitution layer's parameter values" | `config/scenario_registry.py:20-23` | **False as a whole-engine claim**, same contradictions as above. The registry's own job (selecting which constitution module loads) is done correctly and is not itself the problem; the claim is about downstream engine behaviour, which does not hold. |
| "Both the STRUCTURE and the CODE PATH are identical for every scenario... What differs per scenario is DATA ONLY" | `engine/external_layer.py:16-21` | **True as stated**, and separately shown (memory 5f) to be mechanically irrelevant - the external layer's genuine data-only symmetry doesn't matter because the layer has zero measurable effect on any headline KPI. Not a contradiction, but worth pairing with the 5f finding so it isn't read as evidence the rest of the engine is equally symmetric. |
| "Coup emergence from LLM reasoning ONLY - never hardcoded in the LLM path" / "extracted, never hardcoded here" | `engine/elite_agents_v3.py:8`, `:304` | **True, but narrower than it reads.** The raw boolean's *emission* genuinely comes from parsing LLM output, not a rule threshold. What happens to that boolean immediately afterward - suppress it if civilian, let it increment risk if military (`:1128-1157`), then apply a chain-type-literal damping direction and magnitude in `model_phase3.py:538-545` - is 100% hardcoded by chain type. The manuscript must not conflate "the signal's origin is unhardcoded" with "the signal's consequence is unhardcoded"; only the former is true. |
| "consistent with the engine-symmetry principle: this models 'civilian supremacy over the military' as a STRUCTURAL feature of the chain" | `engine/elite_agents_v3.py:1131-1135` | **Internally consistent with the project's own definition of chain-type symmetry** (every civilian scenario gets the same suppression), but by the same token it is explicit, self-documented evidence that civilian-chain outcomes on this metric are produced by chain-type membership, not by reading any scenario's own constitutional text - exactly what a reviewer would call a mechanically induced separation. The comment is honest about the mechanism; the manuscript should be equally honest when citing it. |
| `config/constitution_2008.py:1184`'s docstring, "Usage in model.py: `if scenario == "C": ...`" | `config/constitution_2008.py:1179-1189` | **Stale**, describes the pre-registry-refactor import switch that `model_phase3.py` no longer uses literally. Harmless (docstring only), but a quotable "the documentation doesn't match the architecture" item if a reviewer reads this file. |

---

## 5. Additional bias surfaces

### 5.1 Schema fit

Automated field-count audit (`grep`-based, not a hand-reviewed line-by-line
pass - stated as an approximation):

| File | Total fields (approx.) | `CONFIDENT`-tagged | `GUESS`-tagged | "never fires/unreachable/inert"-tagged |
|---|---|---|---|---|
| `constitution.py` (MFU) | 482 | - | - | - |
| `constitution_2008.py` | 269 | 22 | 22 | 8 |
| `constitution_southkorea.py` | 300 | 177 | 105 | 21 |
| `constitution_thailand.py` | 282 | 138 | 113 | 11 |
| `constitution_pakistan.py` | 276 | 100 | 99 | 5 |
| `constitution_chile.py` | 304 | 156 | 103 | 7 |
| `constitution_germany.py` | 302 | 164 | 103 | 25 |

Two separate findings:

1. **MFU's own schema is 1.6-1.8x larger than any real constitution's
   encoding** (482 fields vs 269-304). A material share of the 21-class
   schema exists only to serve mechanisms MFU itself invented
   (recertification cycles, several safeguard/science/crypto-justice fields
   per memory 5i's bug list). The six real constitutions implementing
   roughly 56-63% of MFU's field count is not evidence those six are
   "simpler" governments - it is evidence the measurement instrument's full
   extent was designed around one of the seven subjects.
2. **Of the fields each new constitution does implement, roughly 35-50% are
   self-labelled `GUESS` rather than `CONFIDENT`.** This is disclosed,
   responsible labelling (per the standing realism requirement, "reasonable
   guess is acceptable only for parameters the paper does not lean on, and
   should be flagged as a guess when it happens") - not a hidden problem.
   But it means that roughly a third to a half of each new country's own
   parameter values are researcher inference rather than confirmed citation,
   which matters directly for how strongly the manuscript can claim "these
   are each country's real constitutional parameters" versus "these are our
   best-effort encodings of each country's real constitutional parameters."

**Classification: legitimate caveat, not a bug.** Recommend the manuscript
state the `CONFIDENT`/`GUESS` ratio per constitution explicitly, the same way
the Chile and Pakistan READMEs already do internally.

### 5.2 Elite chain fixed at 7 agents

Confirmed: `engine/elite_agents_v3.py:89-111`, `CHAIN_ORDER_CIVILIAN` and
`CHAIN_ORDER_MILITARY` are both hardcoded Python lists of **exactly 7** role
slots, for every one of the 7 scenarios, with no scenario-conditional length
anywhere (confirmed by memory section 12's MoE decision: "do not swap," which
explicitly includes not varying chain length). This means the `any()`/`mean()`
N-dependence risk memory flagged in section 12 **does not currently
materialize as a live cross-scenario confound**, because N is uniform at 7 for
literally all seven scenarios - a different and more defensible situation than
the task prompt's framing implied. What remains real is the **fit-quality**
difference documented in each constitution file's own docstring: Germany drops
0 of its real offices to fit 7 slots, South Korea drops 2, Thailand drops 2,
Chile drops 2, Pakistan drops 4 of 8. A country whose real elite structure
happens to have close to 7 veto points gets a closer-to-faithful mapping than
one that doesn't; this is a genuine, disclosed, structural limitation of the
one-size-fits-seven chain design, not a hidden mechanical bug.

**Classification: legitimate caveat (fixed N is a defensible design choice,
confirmed deliberate), with an honest disclosure gap** (the fit-quality
asymmetry across countries is documented per-file but not surfaced anywhere
as a single cross-country comparison).

### 5.3 GSA scope

`analysis/kpi.py`'s `GSA_PROBLEM`/`GSA_PARAM_MAP` (`:143-222`) is wired, as of
bug #11's full closure, to override `get_scenario(scenario).constitution`
directly - so the mechanical "A-only" bug memory section 5i flagged for the
earlier GSA runs is now closed; the override genuinely reaches any scenario's
own constitution object. **But the bounds are centred on MFU's own default
values**, confirmed by the inline comments on every bound (e.g. "default
0.20," "default 0.45," "default 0.878," all MFU's numbers). Spot-checked 6 of
the 13 parameters against each non-MFU scenario's own real encoded default:

| Parameter | GSA bound | SK | TH | PK | CL | DE | 2008 |
|---|---|---|---|---|---|---|---|
| `merit_performance_weight` | [0.10, 0.30] | 0.25 in | 0.25 in | 0.20 in | 0.25 in | **0.40 OUT** | 0.20 in |
| `analysis_threshold` | [0.60, 0.90] | 0.667 in | **0.50 OUT** | **1.00 OUT** | **1.00 OUT** | 0.625 in | **1.00 OUT** |
| `iig_investigation_trigger` | [0.30, 0.60] | 0.35 in | 0.55 in | **0.95 OUT** | 0.30 in | **0.25 OUT** | **0.90 OUT** |
| `state_share` | [0.25, 0.45] | **0.15 OUT** | **0.15 OUT** | 0.30 in | **0.15 OUT** | 0.45 in | **0.10 OUT** |
| `coup_trigger_loyalty` | [0.20, 0.40] | **0.0 OUT** | **0.0 OUT** | **0.50 OUT** | 0.30 in | **-0.01 OUT** | **0.0 OUT** |
| `year_zero_corruption` | [0.75, 1.00] | **0.458 OUT** | **0.683 OUT** | **0.637 OUT** | **0.067 OUT** | **0.020 OUT** | 0.878 in |

22 of 36 spot-checked (scenario, parameter) pairs - **61%** - have the real
encoded default entirely outside the sampled region. Even where the GSA now
mechanically runs on a non-MFU scenario's own constitution object, the search
is conducted in a part of parameter space that scenario's real government
never occupies.

**Classification: artifact.** Any Sobol sensitivity result produced for a
non-MFU scenario under the current `GSA_PROBLEM` bounds answers "how
sensitive is this KPI near MFU's parameter values," not "how sensitive is this
KPI near this country's own real parameter values" - a materially different,
weaker claim than Reviewer 2's "constitutional and feedback parameters"
request implies. This needs disclosure at minimum, and ideally per-scenario
bounds before any cross-scenario GSA table is published.

### 5.4 Ethnic composition - stronger than previously documented

Memory already flags "ethnicity is still Myanmar's for all 7"
(`ETHNIC_ARCHETYPE_PROPORTIONS`, citizen-level). This audit found the gap is
**deeper**: it also fully determines a load-bearing *institution*, not just
citizen labels.

`agents/official.py`'s `OfficialPopulation.create_population()` (`:1074-1166`),
confirmed live for every scenario (no chain-type or constitution-count
branch anywhere in the function):

- **Ministers** (`:1140-1152`): `ethnicity = random.choice(ETHNIC_GROUPS)`,
  where `ETHNIC_GROUPS` (`agents/citizen.py:142`) is the literal Python list
  `["Bamar","Shan","Karen","Kachin","Chin","Mon","Rakhine","Kayah"]`, imported
  at module level, identical for every scenario.
- **Ethnic Leaders Council** (`:1154-1166`): `ethnic_groups =
  ETHNIC_GROUPS.copy()` - this chamber is **unconditionally instantiated with
  exactly Myanmar's 8 real ethnic names**, for every one of the 7 scenarios,
  including Chile and Germany (0 encoded ethnic groups) and South Korea (1).
  A German or Chilean Ethnic Leaders Council seat is literally named "Kayah."
- **President and Chancellor** (`:1093-1108`): `ethnicity=random.choice(ETHNIC_GROUPS)`,
  same Myanmar list, same for every scenario.

Separately, `institutions/chambers.py:347-352`'s `generate_annual_policy()`
hardcodes the `ethnic_impact` dict to exactly **four** of Myanmar's eight
names (`Bamar`, `Shan`, `Karen`, `Kachin`), for every scenario, every policy,
every year. Combined with `agents/official.py:373,957`'s
`policy.get("ethnic_impact", {}).get(self.ethnicity, 0.0)` lookup (used in
ordinary officials' `_evaluate_policy`, weight 0.20, and in
`EthnicLeaderAgent.cast_veto_vote`, weight **0.55**), this means:

- Even within Myanmar's own two scenarios (A and C), 4 of the 8 Ethnic Leaders
  (Chin, Mon, Rakhine, Kayah) get `ethnic_impact=0.0` on every single vote,
  every year, by construction - a pre-existing asymmetry inside the
  "controlled" pair that nobody had previously surfaced.
- For the Ethnic Leaders Council specifically, with `ethnic_impact=0.0`, the
  maximum achievable `score` is `national_benefit*0.30 + loyalty*0.15 <=
  0.405`, below the `>0.50` threshold for a "yes" vote - meaning **for the 4
  of 8 leaders who draw an unkeyed ethnicity, a "yes" vote is structurally
  unreachable regardless of how beneficial the policy actually is.**

**Classification: artifact, and a materially larger one than the existing
"ethnicity gap" framing in memory conveys.** This is not merely "the citizen
population's census composition is Myanmar's" - it is "one of the three
structural chambers in the three-chamber system (the Ethnic Leaders Council)
is Myanmar's chamber, by name and by vote-eligibility mechanics, for every
constitution in the comparison, including the ones with zero or one encoded
ethnic group." No chain-type branch is involved; this is purely a
data-generalization gap, parallel to (and larger than) the
`ETHNIC_ARCHETYPE_PROPORTIONS` gap memory already tracks. Recommend this be
added explicitly to the open item in memory section 11/the "Myanmar ethnic
composition" task, since it changes that task's scope from "citizen labels"
to "citizen labels plus a voting chamber's composition and eligibility math."

### 5.5 Year-zero residual leakage - mostly closed, two small gaps remain

Confirmed clean on all headline fields after the 2026-10-29 correction:
`corruption_index`, `trust_index`, `gini_coefficient`, `employment_rate`,
`coup_risk` and `stability_index` all read `self.CONSTITUTION.simulation.YEAR_ZERO_*`
(`model_phase3.py:355-399`), with `getattr` fallbacks that are genuine no-ops
for MFU only (which predates those two fields) rather than silent
Myanmar-leakage for the other six.

Two residual gaps, both already disclosed in the function's own docstring
(not hidden), neither on a headline north-star term:

- `shared_data["ethnic_harmony"]` seeded at a uniform `0.35` for all 7
  scenarios (`:375`) - low-stakes since this specific key is superseded by
  `ethnic_harmony_index` from year 1 onward (bug #3's fallback chain), but the
  year-0 harmony value feeding into year-0's north-star computation is
  Myanmar's regardless of scenario.
- `grievance_index` (0.60), `brain_drain_rate` (0.35), `military_loyalty`
  (0.55), `policy_quality` (0.50) have **no `YEAR_ZERO_*` counterpart in any
  constitution module** and are uniform literals for all 7 scenarios by
  construction - not a leak from a prior Myanmar default, simply fields that
  were never extended to the schema. None of these four feeds the north-star
  formula directly.

**Classification: legitimate, disclosed, low-stakes residuals.** No action
needed beyond noting them if a reviewer asks about year-zero symmetry
specifically.

### 5.6 A related, separate correctness risk found while auditing year-zero (flagging, not fixing)

`analysis/kpi.py`'s `CalibrationValidator.validate_year_zero()` ("MoS 8 -
Calibration Against Reality," `:614-650`) calls
`self.loader.get_year(0)` with **no scenario argument** (`:627`), and
`get_year()`'s default (`scenario=None`) returns rows from **every scenario
currently loaded** (`:347-353`), not Myanmar's alone. Once more than one
scenario's `scenario_*_all.csv` exists in the same results directory - which
will be true the moment Phase 2 produces all 7 - `vals.mean()` at `:638`
silently blends year-0 values **across all loaded scenarios** (e.g. Chile's
0.067, Pakistan's 0.637, Germany's 0.020, Myanmar's 0.878) and compares that
blend against `MYANMAR_BASELINES["corruption_index"]` - a single Myanmar-only
real-world figure. This produces a meaningless number the instant the
reproducibility package runs this validator against the full 7-scenario
results directory, and it currently "works" only because, historically, only
A and C (both Myanmar) have ever populated that directory together.
Separately, `MYANMAR_BASELINES["corruption_index"] = 0.72` (`:99`) was not
updated when `YEAR_ZERO_CORRUPTION` moved to 0.878 on 2026-10-29 - the
calibration validator's own target is now stale against the number it is
meant to check.

**Not part of the cross-constitution bias question Kaung asked, but a
concrete pre-Phase-2 code defect this audit surfaced as a side effect.**
Flagged here rather than fixed, per the audit-only constraint. Needs a
scenario filter added to `validate_year_zero()` before it is run against more
than one scenario's data, and the stale `0.72` baseline needs updating to
0.878 regardless.

---

## 6. Classification summary, file:line, for the reproducibility register

| # | Item | File:line | Class | Fix cost |
|---|---|---|---|---|
| 1 | `RECERTIFICATION_INTERVAL`/`REVIEW_INTERVAL` MFU-exclusive | `agents/official.py:262`; `institutions/court.py:77` | Legitimate (schema-fit caveat) | N/A - disclose only |
| 2 | Civilian IIG floor literal | `model_phase3.py:638,768` | Circular for MFU/SK, legitimate for CL/DE | Needs design decision |
| 3 | Civilian `rights_violated=False` unconditional | `model_phase3.py:634` | Artifact (makes #9 below dead) | Needs design decision |
| 4 | Civilian shame-register decay | `model_phase3.py:640-646` | Artifact, low stakes | Cheap |
| 5 | Military 5% rights-violation roll | `model_phase3.py:674` | Artifact | Cheap |
| 6 | Military IIG decay rate default | `model_phase3.py:699` | Artifact (no field exists to read instead) | Needs new constitution field x3 |
| 7 | Coup-signal damping direction | `model_phase3.py:538-545` | Artifact (direction) + uniform constant (magnitude) | Needs design decision |
| 8 | `const_commitment` binary | `feedback/loops.py:340` | Artifact, new finding | Needs new constitution field |
| 9 | `RIGHTS_VIOLATION_TRUST_DROP` dead for civilian chains | `feedback/loops.py:149`, gated by `model_phase3.py:634` | Artifact (reachability), legitimate (values) | Needs design decision - do civilian chains ever suffer a modelled rights violation? |
| 10 | Three "disclosed" rights/stability constants uniform | `config/constitution*.py` `rights.*` | Form-legitimate, substance-artifact | Needs real per-country research or explicit disclosure |
| 11 | North-star formula provenance/weights | `model_phase3.py:782-801` | Artifact (no constitution ever chose these weights) | Needs design decision |
| 12 | `_apply_scenario_rules` docstring symmetry claim | `model_phase3.py:622-625` | Contradicted | Prose fix |
| 13 | `scenario_registry.py` symmetry claim | `config/scenario_registry.py:20-23` | Contradicted (as whole-engine claim) | Prose fix |
| 14 | `elite_agents_v3.py` "never hardcoded" claims | `engine/elite_agents_v3.py:8,304` | True but narrower than it reads | Prose clarification |
| 15 | `elite_agents_v3.py` "structural feature of the chain" comment | `engine/elite_agents_v3.py:1131-1135` | Self-documents the mechanism; honest, but needs matching honesty in the manuscript | None - already accurate |
| 16 | `constitution_2008.py` stale usage docstring | `config/constitution_2008.py:1184` | Cosmetic | Cheap |
| 17 | MFU schema 1.6-1.8x larger than real constitutions | all `config/constitution*.py` | Legitimate caveat | Disclose only |
| 18 | ~35-50% `GUESS`-tagged fields per new constitution | all 5 new `config/constitution_*.py` | Legitimate caveat (already disclosed internally) | Disclose in manuscript |
| 19 | Elite chain fixed at 7, uneven real-office fit | `engine/elite_agents_v3.py:89-111` + each constitution's own docstring | Legitimate (deliberate design) | Disclose only |
| 20 | GSA bounds centred on MFU, miss 61% of spot-checked non-MFU defaults | `analysis/kpi.py:143-222` | Artifact | Needs per-scenario bounds or explicit scope disclosure |
| 21 | Ethnic Leaders Council / Ministers / President / Chancellor hardcoded to Myanmar's 8 names | `agents/official.py:1093-1166` | Artifact, new finding, larger than previously documented | Needs real per-country data (comparable size to existing ethnicity task) |
| 22 | `chambers.py` policy `ethnic_impact` keyed to 4 of 8 Myanmar names | `institutions/chambers.py:347-352` | Artifact, new finding | Needs generalization alongside #21 |
| 23 | Year-zero residual uniform literals (harmony/grievance/brain-drain/loyalty/policy-quality) | `model_phase3.py:355-399` | Legitimate, disclosed, low-stakes | Low priority |
| 24 | `CalibrationValidator.validate_year_zero()` cross-scenario blending risk | `analysis/kpi.py:614-650` | Code defect (not a bias per se) | Cheap, needs scenario filter |
| 25 | `MYANMAR_BASELINES["corruption_index"]` stale at 0.72 | `analysis/kpi.py:99` | Code defect | Cheap |

---

## 7. Recommendations

### 7.1 Fixable in code before the campaign (none of these should be done unilaterally - each changes published numbers)

- **#24/#25** are pure correctness fixes with no bias implication of their
  own (scenario-filter the calibration validator; update the stale baseline
  to 0.878). Cheap, low-risk, should land before Phase 2's validation tables
  are generated, regardless of any other decision.
- **#16** (stale docstring) is a zero-risk prose fix.

### 7.2 Needs Kaung's decision, each one changes published numbers and is exactly the kind of change already committed to a re-run

- **#2/#3/#9 together**: whether civilian chains should ever be able to
  suffer a modelled constitutional rights violation at all. As built, they
  structurally cannot, which makes four real researched parameter values
  permanently inert. Three options: (a) leave as designed and disclose
  precisely (civilian supremacy means rights violations are definitionally
  excluded from the model, a defensible reading of what "civilian-chain" is
  supposed to mean); (b) give civilian chains their own low-probability
  rights-violation mechanism (parallel to the military 5% roll) so
  `RIGHTS_VIOLATION_TRUST_DROP`'s real cross-country variation can actually
  execute; (c) remove the dead parameter from the four civilian constitutions
  and document why. (a) is the cheapest and most consistent with "civilian
  supremacy" as a structural concept; (b) is the most scientifically honest
  if the paper wants to claim the field is used.
- **#7/#8**: `const_commitment` and the coup-damping direction. Both are
  chain-type literals with no constitution-field backing. Recommend
  promoting both to real constitutional fields per constitution (similar to
  how #10's three constants were promoted), sourced per country rather than
  backfilled uniformly if possible - otherwise disclose them exactly as #10
  was disclosed (uniform constant, not country-specific).
- **#11**: the north-star weights. Given memory's confirmation that no
  constitution ever defined this formula, this is the right moment to either
  (a) have `senior-data-analyst` propose a weighting scheme chosen
  specifically for a 7-constitution comparison, with the choice justified in
  the methods section, or (b) report north_star findings only with the
  explicit caveat that the weights are a 2025 Phase-2-era design choice never
  revisited for 7 scenarios, and consider dropping north_star from any
  cross-scenario headline claim in favour of the individually-defensible
  component metrics (corruption, Gini, GDP growth).
- **#20**: GSA bounds. Recommend per-scenario bounds (centred on each
  scenario's own default, same re-centring logic already applied twice to
  MFU's own bounds per bugs #26/#j) before any cross-scenario GSA table is
  published, or an explicit scope statement that the current GSA answers
  "sensitivity near MFU's parameter values only."

### 7.3 Must be reported as a limitation, not fixed (would require new real-world research, comparable in size to work already deferred)

- **#17/#18**: schema-fit and guess-ratio. Disclose the `CONFIDENT`/`GUESS`
  ratio per constitution and the 482-vs-270-304 field-count asymmetry.
- **#19**: fixed 7-slot elite chain and uneven real-office fit. Already
  disclosed per-file; needs a single cross-country summary table in the
  manuscript.
- **#21/#22**: the Ethnic Leaders Council / ministerial roster / policy
  `ethnic_impact` dict being Myanmar-shaped for all 7 scenarios. This is
  larger than the already-tracked `ETHNIC_ARCHETYPE_PROPORTIONS` gap (memory
  section 11, item 6) and should be folded into that same task's scope, not
  treated as separate - it is real per-country census/legislative-seat data,
  a comparable-sized research task, and "inventing it would violate section
  11" per the existing standing rule.
- **#10**: the three uniform rights/stability constants. Either source
  real per-country values (a smaller, bounded research task - three numbers
  per country, not a whole schema) or disclose plainly that they are Ka-Nova
  modelling constants, not constitutional provisions, wherever they are
  cited.

### 7.4 Already decided, do not reopen (cross-referenced for completeness)

Effect-size framing (no `d` for trust/coup/stability), the near-twin backtest
scope limit, the two-axis paper architecture, and CVES `L4_MODE="flag"` are
all locked per memory section 5j and are consistent with everything found in
this audit - nothing here contradicts those four decisions.

---

## 8. Honest framing, within the already-decided two-axis structure

The two-axis framing (mechanism clusters on suppressed representation and
executive constraint, outcome diverges on corruption and survival) is
accepted and this audit does not challenge the collapse-mechanism symmetry
decision (memory 5j decision 2: `_coup_risk_check()`'s threshold and roll stay
identical for every scenario, which is correct and legitimate).

What this audit adds, and what the manuscript should say explicitly:

1. **The A-vs-C pair can keep its strongest claim as-is.** "Constitutional
   text is the only manipulated variable" is defensible for the two-scenario
   controlled pair specifically, because both share the external layer
   (verified 0 mismatches, memory 5f), the same ethnic data, the same
   8-member Ethnic Leaders Council drawn from the same real 8 groups, and the
   same elite-chain fit quality. None of the asymmetries this audit found
   differentiate A from C - they differentiate Myanmar (A, C) from the five
   new countries, and civilian chains from military chains as a category.
2. **The 7-way comparison cannot make that claim.** For the five new
   countries, population ethnicity, the Ethnic Leaders Council's composition
   and eligibility mechanics, elite-chain fit quality, and - now quantified on
   real 15-run/scenario output (Section 3) - three of the north-star
   composite's seven terms (coup, IIG, GDP, 45% of total weight) saturate at
   an identical ceiling for all four civilian scenarios regardless of
   constitutional content, are determined by chain-type membership or by
   Myanmar's demographic data, not by each country's own constitutional text.
   The two-axis finding ("guardianship constitutions cluster on mechanism,
   diverge on outcome") remains defensible as a **qualitative, mechanism-level**
   claim - the suppressed-representation and executive-constraint provisions
   really are each country's own text, correctly encoded (modulo the
   `GUESS`-ratio caveat) - but any **quantitative cross-country KPI
   comparison** needs the chain-type circularities disclosed as a scope
   limit, the same way the collapse-timing scope limit is already disclosed
   for the near-twin backtest. The real run data shows the IIG term
   specifically is a clean positive counter-example on the military side
   (Thailand's real anti-corruption floor correctly produces ~9-10x Myanmar's
   and Pakistan's term value, Section 3.2) - proof the same mechanism is
   legitimate when not sitting next to a competing civilian-chain hardcode.
3. **Recommended manuscript posture**: present the north-star composite as a
   Phase-2-era design choice inherited unchanged, decompose it exactly once in
   a methods or limitations table (Section 3 of this document gives the real
   numbers for all 7 scenarios), and let the individually-defensible
   components - corruption, trust and Gini, the three terms this audit found
   to carry genuine cross-civilian-scenario signal, plus IIG specifically for
   the military-chain comparison - carry the quantitative cross-country
   claims instead of the seven-term composite. This is a stronger, more
   specific position than either defending north_star as-is or dropping it
   silently, and it directly answers "why isn't the headline KPI doing the
   comparative work" before a reviewer has to ask.

---

## 9. Verification

- All runtime activity for this audit used `KA_NOVA_RESULTS_DIR` pointed at a
  throwaway directory outside the repository, confirmed at every step.
- `git status -- results_phase3/` checked clean at the end of this audit
  (see final tool output in the session transcript).
- No file under `config/constitution*.py`, `docs/manuscript_corrections_register.md`
  or `docs/calibration_provenance.md` was modified.
- No fixes were applied; every finding above is reported, not remediated, per
  the audit-only constraint.
