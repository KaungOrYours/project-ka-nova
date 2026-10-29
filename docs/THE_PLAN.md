# THE PLAN, 2026-10-29

Merged from the adversarial review (REJECT verdict) plus three specialist plans:
`docs/adversarial_review_plan.md`, `docs/writing_plan.md`, the simulation-engineering
remedy scoping, and the analysis scoping. This supersedes the run-first plan.

---

## 1. The one-line summary

**Fix the audit trail and the hidden branches first, then run once, then write.**
The paid campaign moves from "next" to "fourth". Nothing is lost by the delay,
because a run today would reproduce the same unreconcilable audit trail and the
same GSA blindness that just earned a REJECT.

---

## 2. What the paper is now

Not a comparative governance study. A **methods and instrument paper with a
negative result**, on a seven-constitution testbed.

**Headline claim**: the same elite behaviour is unlawful under one encoded
constitution and lawful under another, recoverable per-decision from a shipped
log. This is an A-vs-C claim on the controlled pair, so it survives every kill
shot in the review: it is not an effect size, and the only live article label
(9.4) belongs to the one constitution that genuinely has an Article 9.4.

**It is contingent.** Today the counts do not tie out (4,570 coup signals
emitted vs 4,176 intercepted, and Senior General at 148 emitted vs 163
intercepted, which is not even a subset relation). Leading with an unreconciled
count is worse than leading with the old 0.84. **The headline becomes available
only after the re-run with fixed logging.** If that fails, the headline reverts
to the mechanism audit.

**Second claim**: the mechanism audit itself. We built a seven-constitution
comparative design and established that the engine does **not** discriminate
between structurally similar constitutions, we can say precisely why, and we can
say what it would take. That is a real, publishable negative result.

**Cut**: corruption divergence as a contribution (demoted to a horizon-matched
descriptive with the mechanism disclosed), and mechanism-axis clustering (needs
neither the engine nor CVES, and has no coding scheme or reliability statistic).

**Title must change.** "Comparative Governance Simulation" no longer describes
the paper. A title change is visible to returning reviewers and must be
justified in the response preamble.

---

## 3. The sequence

Gates are hard. Do not skip forward.

### Phase 0, free, no compute, about 4 to 6 hours

| # | Item | Owner | Why it is first |
|---|---|---|---|
| 0.1 | **`run_id` threading plus structured-decision logging**, roughly 5 to 10 lines | simulation-engineer | `run_id` is never written anywhere; every logged row says `run: 0`, so the 100 Monte Carlo runs are unrecoverable. **Any run before this fix inherits the defect.** Also log `budget_weight`, `coup_signal`, `ethnic_weights`, which are in scope at the call site and currently dropped. |
| 0.2 | **Table 6 disclosure rewrite** | paper-writer | Delete "100% corrected, zero uncorrected", which is false. Publish 4,570 / 4,176 / 394 (8.6%) and name the two structural defects. Fastest reviewer kill shot, removed by writing alone. |
| 0.3 | **GSA `param_classes` subset kwarg** | data-analyst | The scope guard correctly blocks 9 institutional parameters on non-A scenarios but has no way to request a legitimate subset, so it also blocks two things we promised. Default `None` keeps every published CSV byte-identical. |
| 0.4 | **Two GSA re-runs under the new path** | data-analyst | C/`trust_index` at k=3 (320 runs) reproduces the published headline on a clean minimal problem. `coup_risk` on C at k=5 (448 runs) settles decision 6. Both free, minutes each. |

### Phase 1, free, about 8 to 10 hours

| # | Item | Owner | Note |
|---|---|---|---|
| 1.1 | **Promote the chain-type literals to constitutional fields at identical values** | simulation-engineer | Two corruption drifts, civilian IIG floor and ramp, `const_commitment`, military rights roll, military IIG cap, decay rate, plus three more found this pass (`loops.py:135`, `:142`, duplicate floor at `model_phase3.py:672-675`). **This does not make the near-twins separate.** It makes the hidden branch visible, named, disclosable and GSA-visible. That is the point. |
| 1.2 | **Fix the IIG floor ordering defect**, separate commit | simulation-engineer | The civilian floor is re-enforced after the corruption consumer reads it, so Scenario A's `iig_effectiveness` is 0.0 at read time and A's corruption is flat for five years. This is a real bug fix and is **not** byte-identical for A, which is why it must not share a commit with 1.1. |
| 1.3 | **A/`corruption_index` GSA re-run** with the new fields | data-analyst | Roughly 30 minutes. Must also be re-run anyway because year-zero changed today. |

### Phase 2, writing, about 18 to 22 hours, fully unblocked today

| # | Item |
|---|---|
| 2.1 | **Remedy 1**: extend the effect-size decision to corruption. Four governing constants, not three. Name `model_phase3.py:785-793`. **Quote no Cohen's d at all.** Restore the horizon-matched year-15 comparison (0.62 vs 0.89 = 0.27, now about 0.16 to 0.17) in place of the horizon-mismatched 0.84. |
| 2.2 | Reword locked finding 2, which describes year-50 behaviour for a scenario that dies at 15 to 17. |
| 2.3 | Response preamble owning the discontinuity: every number changes, here is why, here are the defects we found ourselves. |
| 2.4 | Rewrite the claim set and the title. |

### Phase 3, figures, about 1 to 2 days

Figures 1 to 4 are schematics that never needed the runs and are the likely
referents of "highly stylized or synthetic". **Do these now, not after the
campaign.** Plus the AI-provenance paragraph (R1 pt.7), currently at zero.

### Phase 4, the run. Benchmark first, about $0.30, then $36 to $45

Only after Phases 0 and 1. All 7 scenarios at N=50 (measured collapse years:
A 49.00, C 15.30, SK 49.00, TH 19.35, PK 23.60, CL 49.00, DE 49.00) plus the
L2 ablation on Scenario C. Leaves $35 to $44 margin on $80.

### Phase 5, in parallel with 2 and 3

**Remedy 2**, CVES L2 reachability. Wire `rights_violation` through schema,
parser and prompts; add machine-readable article-label fields to the seven
constitution files (none exist today, only comments). Makes Article 2.4
reachable for **A and Germany only**, the two constitutions with absolute
rights, producing a real `cves_violations_DE.jsonl` for the first time.
Blocked on `senior-llm-engineer` for prompt wording. Article 8.6 stays dead
by design and should be labelled structurally redundant, never engineered to
fire.

### Phase 6

Final writing, then `senior-reviewer` re-reviews the actual draft before
submission.

---

## 4. What we are deliberately not doing

- **Not sourcing per-country corruption drift rates from each country's own
  V-Dem series.** It would make the near-twins separate, but by fitting the
  model to the outcome it then claims to reproduce. Circular, and a reviewer
  catches it immediately. A non-circular version derives drift from encoded
  constitutional features, which is new modelling research, not a revision fix.
- **Not root-causing the remaining 394-signal anomaly** by git-bisect and
  replay. Two to three hours of archaeology on a dataset being fully
  superseded. Disclosure is sufficient and honest.
- **Not inferring `run_id` from timestamp clustering.** It is genuinely lost,
  and inferring it would be invented content in a reviewer-facing number.
- **Not building per-scenario GSA bound sets.** The class-based subset fix
  unblocks both deliverables without it.
- **Not removing the `budget_weight` clip** to make Article 8.6 fire.
- **Not claiming Reviewer 1 endorsed the instrument framing.** His point 3 is a
  disjunctive question; "an important result" attaches to the parity finding.
  Adopt the framing, do not claim it is reviewer-endorsed.

---

## 5. Decisions needed from Kaung

1. **Reviewer 2 point 1 cannot be fully answered.** The model does not separate
   structurally similar constitutions. Confirm we report that as a finding
   rather than continue trying to engineer a separation.
2. **Scenario C's collapse**: keep it central, keep the plausibility hedge, use
   15.30, **drop the "strongest finding" superlative**? Pakistan over-surviving
   by 63 percent means the symmetric-mechanism evidence no longer carries it.
3. **Which points are answered as "scoped as a limitation"** rather than
   "addressed". At minimum R1 pt.5 and R2 pt.1.
4. **Two attachments needed** from the decision letter: the response template
   and the Resubmission Checklist. The response must use their format.
5. `YEAR_ZERO_STABILITY` (0.18 matches nothing, 0.270 is defensible) and
   decision 8's four year-zero fields. Both change mechanics, both must land
   before Phase 4.

---

## 6. Effort and the real timeline driver

| Stream | Hours |
|---|---|
| Phase 0 | 4 to 6 |
| Phase 1 | 8 to 10 |
| Writing, total across all phases | **70 to 87** |
| Figures | 1 to 2 days |
| Compute | $36 to $45, about 1 day wall-clock across 4 pods |

**Writing is the critical path, not compute.** 70 to 87 writer-hours against
roughly 15 hours of engineering and one day of GPU time. Any plan that
front-loads the run has the dependency backwards.

**Acceptance cannot land before December 2026** regardless, so plan the
dissertation against "submitted, under review".

---

## 7. Three sentences that must never reach the draft

1. Any claim of per-article attribution over real, historically enacted
   constitutions. Today every logged attribution is Scenario A under one
   hardcoded MFU label.
2. "Diverge by about 0.84 over fifty years." Horizon-mismatched, comparing A at
   year 50 against C at collapse.
3. "The engine is constitutionally agnostic." Refuted by `model_phase3.py:785-793`.
