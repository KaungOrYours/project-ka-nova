# Writing plan after the adversarial REJECT

Owner: `senior-research-paper-writer`. Date: 2026-10-29. Status: plan only, nothing drafted.
Inputs: `.claude/memory.md` 5b, 5c, 5j, 5k and the ADVERSARIAL REVIEW section;
`docs/adversarial_review_plan.md`; `docs/manuscript_corrections_register.md`.
Scope: writing decisions only. No code, no runs, no edits to other documents.

---

## 0. Honest assessment of the proposed headline reframe

**The claim.** Within the controlled A-vs-C pair, an identical generative decision stream
is differentially constrained by two article-level constitutional encodings: the same elite
act (a coup signal from an elite agent) is intercepted and annulled with article attribution
under one encoding and propagates uncontested under the other, 4,176 interceptions against
6,009 permissions, both recoverable from the shipped log.

**Is it strong enough to carry a paper?** It is strong enough to carry the *empirical core*
of a methods-and-measurement paper. It is not strong enough on its own to move Reviewer 2's
question 1 ("contributes to the body of knowledge") from No. Alone it reads as a demo of a
validator. It carries the paper only in a set of three: this claim, the mechanism audit
(north-star decomposition plus `docs/bias_audit.md` 3.1), and the GSA self-incrimination.

**Why it survives every kill shot in the review.**
- A-vs-C is the controlled pair: external layer verified identical, 0 mismatches on all 11
  output keys over 50 years (memory 5b finding 1). It needs none of the seven-constitution
  machinery, none of class (ii), no per-country realism.
- It is not an effect size, so K2 and K3 do not reach it.
- K1's hardcoded-article-label defect does not bite here. The only live label is Article 9.4
  and the only scenario producing it is A, whose constitution genuinely has an Article 9.4.
  The label problem is fatal to the seven-constitution instrument claim and inert for this one.
- It inverts P2's degeneracy exposure. Whether the Chief Justice's annual coup signal is
  governance insight or a prompt regularity is **irrelevant to this claim**, because the
  generative substrate is identical across both arms and only the encoding differs. That
  argument should be written explicitly; it is the strongest defensive move available.

**What it licenses.**
- That within the simulation, two article-level encodings differentially constrain an
  identical decision stream, with per-decision provenance and a reproducible aggregate count.
- That the validator's interceptions are article-attributable and auditable from a shipped
  artifact.

**What it does not license, and these must be written as explicit non-claims.**
- Any downstream outcome effect. A's 0.000 coup probability is produced partly by the
  civilian-chain damping at `model_phase3.py:521-529`, independent of CVES. Outcome
  materiality is the L2 ablation's question, and the ablation may show the validator rather
  than Article 9.4 produced that 0.000.
- "Lawful under the other." The 2008 encoding contains no provision that tests the signal;
  that is not the same as the real 2008 constitution permitting a coup. Correct wording:
  "no encoded provision renders it invalid, so it propagates."
- Per-article attribution over real enacted constitutions. Zero such attributions exist.
- Anything about generative agents in governance simulation generally (K5).
- **Hard precondition.** The numbers do not currently tie out: 4,570 A coup signals emitted
  against 4,176 intercepted, and Senior General 148 emitted against 163 intercepted, which is
  not a subset relation (K4). Leading with an unreconciled number is worse than leading with
  the 0.84. **This claim is contingent on remedy 3 (log the structured decision and a real
  `run_id`, then reconcile or correct Table 6).** If remedy 3 does not land, the headline must
  revert to the mechanism audit and this claim drops to a scoped Section V result.

---

## 1. The claim set I would submit

Five claims, down from six. Order is submission order.

| # | Was | Verdict | One-sentence form |
|---|---|---|---|
| 1 | new | **ADD, headline** | Within a controlled constitutional pair sharing population, shock sequence, external layer and generative substrate, an identical elite decision stream is differentially constrained by two article-level encodings, intercepted with article attribution under one and propagating uncontested under the other, with both counts recoverable from the published audit trail. |
| 2 | (b) encodings artifact | **KEEP, extend** | Seven machine-readable article-level constitutional encodings with per-field provenance and explicit CONFIDENT/GUESS labels, released with a documented account of which encoded provisions are mechanically reachable in the present engine and which are encoded but inert. |
| 3 | (f) self-audit | **KEEP, promote to second position** | A full mechanism audit of the model reporting, with file and line, which published metrics are driven by constitutional content, which by chain-type and feedback-layer constants, and which are pinned at a variable boundary. |
| 4 | (d) substrate invariance | **REWORD, demote** | Replacing the generative elite layer with a deterministic rule-based layer changes no headline KPI by more than 0.003, and we derive this from the coupling's own bounds rather than reporting it as a discovery. |
| 5 | (a) CVES instrument | **REWORD, narrow hard, subordinate to claim 1** | CVES is a runtime constitutional validator producing per-decision, article-attributed provenance; we demonstrate one reachable article-level pathway and state its coverage limits, including two rules that are unreachable under the current decision schema. |
| - | (c) corruption divergence | **CUT as a contribution** | Reported in Results as a horizon-matched descriptive comparison only, and its mechanism is disclosed inside claim 3. Not a contribution. |
| - | (e) mechanism-axis clustering | **CUT** | Retained as one paragraph of case-selection rationale in Related Work, with no contribution status, because it requires neither the engine nor CVES and has no coding scheme or reliability statistic (K7). |

Notes on the rewordings.
- **Claim 4 is an upgrade disguised as a demotion.** Deriving the invariance from
  `clip(mean*0.15, 0, 0.15)` plus a mean-normalised weight vector is more rigorous than
  reporting it as a finding, and it pre-empts K5 by stating it first. Credit the derivation to
  our own audit, never to "a negative result for the field."
- **Claim 5 must never appear without claim 1's scope attached.** Standing alone it is the
  sentence K1 kills in sixty seconds.
- **Claim 3 absorbs what used to be claims (c) and (e).** It is also the answer to the
  "was the original submission sound?" question, which is why it sits second.

**Empirical content that actually fills Section V**, in descending order of credibility:
north-star decomposition (3 of 7 terms at an identical ceiling for all four civilian
scenarios, 45 percent of composite weight); the four GSA runs; the military-side IIG term
tracking Thailand's real encoded floor at 9 to 10 times Myanmar's, the one clean positive;
external-layer inertness (every headline KPI bit-identical under an entirely different
geopolitical world); tax-schedule inertness (Pakistan's real 16.10x exemption unreachable by
a factor of 2.95). Four of the five are self-critical. That is the paper.

---

## 2. What the paper is now about

Two sentences:

> This paper presents a generative agent-based model in which real national constitutions are
> encoded at article level and enforced at runtime by a four-layer validator, and shows that
> two such encodings differentially constrain an identical elite decision stream with
> per-decision, article-attributed provenance. It then audits its own model to establish which
> of its published quantities are produced by constitutional content and which by engine-level
> constants, reporting that three of four previously headline effect sizes and a substantial
> share of its composite success score are determined by modelling choices rather than by any
> constitution.

**The title no longer fits.** "Comparative Governance Simulation" is the part that has to go:
the comparative-outcomes claim is cut, class (ii) has no validated output, and the near-twins
do not separate. "Runtime Constitutional Validation" is now the lead rather than the modifier.

Recommended:

> **Runtime Constitutional Validation in a Generative Agent-Based Model: Article-Level
> Enforcement, Substrate Invariance, and a Mechanism Audit**

Alternative if a shorter title is wanted:

> **Encoding Constitutions as Runtime Constraints in a Generative Agent-Based Model**

Recommend the first. It names claims 1, 4 and 3 in order and signals the self-audit, which
pre-empts the discontinuity question rather than inviting it. **A title change is itself
visible to returning reviewers and must be justified in the response preamble**, not slipped in.

---

## 3. Response to Reviewers plan

### Structure
1. **Preamble, three paragraphs, before any numbered point.**
   - P1, remedy 8: own the discontinuity. Every number changes; we commissioned an internal
     adversarial audit; name it; enumerate the defect classes it found (constitution
     propagation, chain-type literals, IIG floor ordering, the dead CVES rules, the
     unsourced year-zero citations, the boundary-pinned metrics); state that all values are
     recomputed and that the recomputation moved several numbers against us. One sentence
     naming the honest direction of travel, for example that the horizon-matched corruption
     gap roughly halved.
   - P2: the narrowed claim set and the title change, with the reason.
   - P3: a map table, twelve points to manuscript section to artifact (file, run, or citation).
2. **Point-by-point in the letter's own order, R1 1-8 then R2 1-4.** Do not reorder; a
   returning reviewer reads his own numbering. Each entry uses the mandated template fields
   a) concern, b) response, c) action taken, and each front-loads the concession before the
   remedy.
3. **No closing summary.** The preamble already carries it; a second one reads as padding.

### Order of weight, not of presentation
The three answers that carry the decision:

1. **R1 pt.2, the fulcrum.** Answer completely in the negative: four governing constants, not
   three, naming `model_phase3.py:785-793` alongside the three `rights.*` fields; no Cohen's d
   anywhere in the paper; the horizon-matched year-15 comparison restored. This single answer
   removes K2, K3 and K8, and converts the position from "caught claiming one survivor" to
   "answered completely, with our own numbers." Writing only, no compute.
2. **R2 pt.4, the hardest, and R2 is the blocker.** Instrument framing plus the derived
   invariance (claim 4) plus the L2 ablation reported either way. **Blocked on PEND-7.** The
   framing must be pre-committed before the result is seen, per the warning in memory: the
   ablation will probably show A's 0.000 coup probability was produced by the validator, not by
   Article 9.4, which contradicts Section VI-A as written.
3. **R2 pt.1, the dangerous inversion.** He asked how the approach performs on more similar
   constitutions; the engine currently does not separate them. Answer honestly: we measured
   it, the three guardianship encodings differ only by year-zero intercept and IIG floor and
   produce parallel corruption lines of identical slope, here is the one place separation does
   occur (the military-side IIG term at 9 to 10 times), and here is the change that is the only
   route to separation (promote the chain-type literals to constitutional fields). Whether
   remedy 4 lands decides whether this reads as "we found the limit" or "we fixed the limit."
   The second is worth materially more.

Deliberately short answers: **R1 pt.4** is finished and best-answered of the twelve; three
sentences with file and line, no elaboration. **R1 pt.6 and pt.7** are one short paragraph
each but are a rejection path if empty, and figures 1 to 4 need no run data, so they must be
done before the response is drafted, not after.

### What I need before drafting, blocking
1. **The response template attached to the decision letter.** Mandated by the letter. Not in
   the repo and not in memory. Without it I cannot guarantee field names, ordering or
   per-comment formatting, and a non-conforming response is an avoidable administrative risk.
2. **The Resubmission Checklist**, also attached to the letter.
3. **The "Request for Byline Change" form**, conditional on PEND-10 (Dr. Saifullah's
   determination on the Stage-8 acknowledgment edits).
4. Confirmation of which of R1's eight and R2's four will be answered as "not fully resolved,
   scoped as a limitation" rather than "addressed." On current evidence that set is at least
   R1 pt.5 and R2 pt.1, possibly R2 pt.4. Deciding this is Kaung's, not mine, and the response
   cannot be internally consistent until it is decided.

Standing rule for this document: no "this has been addressed" without a traceable code fix,
data result or citation. Where an artifact does not yet exist I will draft the entry marked
PLACEHOLDER in the draft itself.

---

## 4. Effort, writer-hours, after the underlying artifacts exist

These are hours of writing only. The critical path is the runs and remedies 1 to 4, not this.

| Artifact | Hours | Notes |
|---|---|---|
| Response to Reviewers | 18 to 22 | Preamble 2; R1 pt.2 3; R2 pt.4 3; R2 pt.1 2.5; R1 pt.3 2; R1 pt.5 2; R1 pt.1 1.5; R1 pt.8 1.5; R2 pt.2 1; R2 pt.3 1; R1 pt.4 0.5; R1 pt.6 0.5; R1 pt.7 0.5; plus a 2h consistency pass against the register and the manuscript. |
| Manuscript rewrite | 40 to 48 | 27 existing edit locations at roughly 45 min each is about 20h; five new subsections: mechanism audit 6, GSA 4, comparative backtest with the collapse scope limit 4, effect-size robustness 3, L2 ablation 3. |
| Abstract | 4 to 6 | Short but the most-reread paragraph; carries the claim set, the title change and the A-vs-C scoping. Needs three passes and a read against the submitted abstract side by side. |
| Highlighted-changes PDF | 6 to 8 | Mechanical but large because every number changes; includes a diff-verification pass against the clean copy to confirm nothing changed silently. |
| Byline Change Request justification | 2 to 3 | Only if PEND-10 requires it. |
| **Total** | **70 to 87** | Excluding the Byline form. |

Sequencing note for the merge: roughly 18 to 22 of the manuscript hours are **unblocked today**
and need zero compute. Specifically the effect-size robustness subsection, the seven D3 scoping
edits, the Section VIII reproducibility corrections (C2 outcome B, C3, C7, D4), C9, C10, the
Germany C1 de-framing, figures 1 to 4 and the AI-provenance paragraph, and the response
preamble. Everything numerical is blocked on the campaign.

---

## 5. What I would not write

Claims that must not appear anywhere, in any draft, in any form.

**Quantitative.**
- Any Cohen's d, including for corruption and IIG effectiveness. Four governing constants, so
  the restriction is now total rather than partial.
- "diverge by approximately 0.84 over fifty years" (horizon-mismatched, C does not exist at
  year 50) and the superseded 0.88.
- "effect sizes are very large."
- Locked finding 2 as currently worded. It is unsound and needs replacing; proposed wording
  in section 7 below.
- 16.6 as Scenario C's collapse year. The measured value is **15.30** at N=20 full scale, itself
  provisional against the N=100 campaign. **15.6 is the internet-shutdown count and must never
  appear as a year.**
- Any Pakistan backtest sentence describing it as the strongest match. Simulated 23.60 against a
  real 14.61 is a 63 percent overshoot and the earlier match is gone.
- 4,176 or 6,009 quoted before remedy 3 reconciles 4,176 against 4,570.
- A seven-scenario corruption figure presented without its boundary pinning marked: Germany
  reaches exactly 0.0 by year 7, Chile by year 13, Scenario C reaches the 1.0 clip near year 13.
  Three of seven series are at a bound.

**Framing.**
- "per-article attribution over real, historically enacted constitutions."
- "the engine is constitutionally agnostic" or "bias lives only in the constitution layer."
  Locked finding 7 is false while the chain-type literals stand, and becomes true only if
  remedy 4 lands.
- "the constitution is the only manipulated variable" anywhere except the A-vs-C pair.
- "All runs are seeded."
- "a strong validation point" for Germany's 1949 corruption sitting inside Scenario A's year-50
  confidence interval. Different quantities, different times.
- "the GSA shows the constitution drives corruption."
- Substrate invariance as "a negative result for the field."
- Mechanism-axis clustering as a computational contribution.
- Any Thailand or Chile outcome backtest; any claim that this model predicts constitutional
  survival.
- Any cross-country claim involving ethnic harmony. Myanmar's census drives all seven.
- The real tax schedules described as "used" rather than "encoded and inert."
- Any statement that Reviewer 1 endorsed the instrument framing. His sentence is disjunctive and
  "an important result" attaches to the parity finding. Adopt the framing; never cite it as
  reviewer-endorsed.
- Anything that lets South Korea's or Germany's addition read as proving MFU's normative
  superiority. L-2 is locked and this is the specific drift risk it guards against.
- "This has been addressed" without a named file, run or citation behind it.

---

## 6. The three sentences most likely to get us rejected if they survive

1. **"CVES provides per-article attribution over real, historically enacted constitutions."**
   Sixty seconds and three greps. L2 has one reachable rule of three; all 4,189 logged
   attributions in repository history are Scenario A under one hardcoded MFU article label; no
   real constitution has ever produced one. It lands on the self-declared primary contribution.

2. **"Both constitutions encode the same year-zero corruption and still diverge by approximately
   0.84 over fifty years."**
   Horizon-mismatched against a scenario that terminates near year 15, and the divergence is
   produced by a two-line `chain_type` branch (`model_phase3.py:785-793`) that the GSA cannot
   see because `chain_type` was never a parameter. Worse, the submitted manuscript already gave
   the horizon-matched year-15 figure; its disappearance while the headline grows is visible to
   a reviewer who read that paragraph.

3. **"The engine is constitutionally agnostic and symmetric across scenarios, so bias resides
   only in the constitution layer."**
   Refuted by the corruption drift literals, the civilian-chain north-star hardcodes at 45
   percent of composite weight, `const_commitment` at `feedback/loops.py:340`, and the
   `RIGHTS_VIOLATION_TRUST_DROP` dead path. It is also the sentence every other claim in the
   paper is conditional on, so losing it loses them all at once.

Runners-up, in case any of the three above are already cut: "All runs are seeded" (directly
checkable, and R1 pt.8 names random seeds explicitly), and "the three guardianship
constitutions cluster toward the failure mode observed for the 2008 Myanmar constitution"
(the R2 pt.1 inversion: inside the engine they differ only by intercept and IIG floor).

---

## 7. Three corrections to the authoritative record, proposed not applied

I have not edited `docs/manuscript_corrections_register.md` or `.claude/memory.md`. These need
Kaung's sign-off, then an owner.

**(a) Register D2 and memory 5j decision 2 misread Reviewer 1 pt.5.** He wrote "a restricted
subset of model **outputs**." Both documents read it as licensing a restricted subset of
**cases**, and D2 uses that to decline Thailand and Chile. The corrected reading **obliges us to
report all five countries** on whichever narrow output set we choose, including the failures. The
practical consequence: pick the output set (the military-side IIG term is the one candidate with
a real positive match), report it for all five, and disclose the Pakistan overshoot inside the
same table rather than declining two countries. Declination plus a silently vanished match reads
as evasive; declination plus a disclosed failure plus one genuine match reads as rigorous.

**(b) Locked finding 2 needs replacing.** Current wording describes a gap at year 50 and
acceleration after year 20 for a scenario that terminates near year 15. Proposed replacement,
pending the campaign numbers:

> Within the simulation, Scenario A's and Scenario C's corruption trajectories separate from the
> first simulated year. At the horizon-matched year-15 comparison the gap is approximately 0.16
> to 0.17 (provisional, N=20, rule-based, full citizen scale). Scenario C reaches the variable's
> upper clip near year 13, before its own mean termination year, so no post-termination
> comparison is reported. The submitted manuscript's year-15 figures (0.62 against 0.89, a gap
> of 0.27) are superseded by the year-zero correction to 0.878.

**(c) Register L-5 and the locked framing of Scenario C's termination need a decision, not a
rewrite by me.** L-5 calls mean-year termination "the paper's strongest finding." Under the new
claim set the headline is claim 1, and the collapse mechanism is deliberately symmetric and
over-survives Pakistan by 63 percent, so calling termination the strongest finding is hard to
hold. My recommendation: **keep it as a central reported finding with the existing weak-plausibility
hedge intact and the 15.30 value, and stop calling it the strongest.** That preserves the lock on
the hedge and the framing-as-result while removing a superlative the evidence no longer carries.
Kaung's call, flagged rather than taken.

Also carried forward and unresolved, both affecting text I would otherwise write: U4, the Myanmar
anchor convention (12.68 against 10.01 years, and whichever is chosen must be applied identically
to Pakistan), and whether remedy 4 lands, which determines the wording of R2 pt.1 and of locked
finding 7.
