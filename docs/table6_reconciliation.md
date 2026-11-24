# Table 6 reconciliation, 2026-11-24 (CORRECTED)

**This document previously claimed the opposite of what follows and was wrong.
The first version argued the 394-signal gap was a counting artifact that
shrank to 16 under a "strict" count. That is retracted in full. The 394 gap is
real, the originally published figures were correct, and the earlier
"correction" was counting what a broken parser accepted.** The error was
caught by adversarial review the same day and is recorded here rather than
quietly overwritten, because the retraction is itself the finding.

---

## 1. What the published table claimed, and why it was right

| quantity | published |
|---|---|
| Scenario A coup signals emitted | 4,570 |
| by role | Chief Justice 4,070, President 294, Senior General 148, IIG Director 57, Central Bank Governor 1 |
| Scenario A signals intercepted by CVES L2 | 4,176 |
| unreconciled | 394 (8.6%) |
| Scenario C coup signals emitted | 6,009 |

Re-deriving the decisions from the shipped logs with a correct parser:

| | re-derived | published |
|---|---|---|
| A total | **4,572** | 4,570 |
| Chief Justice | 4,072 | 4,070 |
| **President** | **294** | **294** |
| **Senior General** | **148** | **148** |
| **IIG Director** | **57** | **57** |
| **Central Bank Governor** | **1** | **1** |
| C total | 6,024 | 6,009 |

Three role figures reproduce to the unit and the totals agree within 0.05
percent. **The original analysis recovered the model's decisions accurately.
It did not count mentions.** Any claim that 4,570 or 6,009 were inflated by a
loose pattern is withdrawn.

## 2. The error in the retracted version

The retracted analysis counted only decisions wrapped in a literal
`<DECISION>...</DECISION>` block. In the shipped logs **1,480 Scenario A rows
and 205 Scenario C rows carry a bare `DECISION` delimiter instead**, and the
model also emits bare JSON objects with no delimiter at all. Excluding those
rows gave 4,192 for A, which was then published as the truth.

Those are precisely the rows where `parse_decision` also failed. So the
retracted "strict" count was not a stricter measure of the same quantity. **It
was a count of what the broken parser accepted, and it made the instrument's
own defect invisible by excluding every decision the defect destroyed.**

The retracted version also attributed the residual to CVES L2's reprompt
rewriting the logged text. That mechanism is impossible: `_l1_resolved_text`
is popped in `engine/elite_agents_v3.py` **before** `l2_constitutional` is
called, and `reasoning_text` is assigned from it beforehand. An L2 reprompt
can never replace the logged text. That explanation is withdrawn.

## 3. What the 394 gap actually measures

| | Scenario A |
|---|---|
| Coup signals the model decided | **4,570** |
| Signals the parser passed to CVES | ~4,176 plus a small residual |
| **Destroyed by the parser before CVES saw them** | **~394** |
| L2 interceptions logged | 4,176 |
| **Interception rate against what the model decided** | **91.4%** |

The gap is not noise and not a counting choice. It is the number of coup
signals the elite agents emitted that **the instrument silently deleted before
its own enforcement layer could evaluate them.**

Measured substitution rates in the published campaign, where `parse_decision`
returned a role default that CVES L1 then recorded as `status: pass` with
`parse_failure: false`, because `ROLE_DEFAULTS` is schema-valid:

| scenario / role | role-default decisions | share |
|---|---|---|
| A, all roles | 3,650 / 35,383 | 10.3% |
| **A, Senior General** (the one role with coup latitude) | 1,514 / 5,055 | **30.0%** |
| C, all roles | 4,623 / 12,033 | 38.4% |
| **C, Military Intel Chief** | 1,710 / 1,719 | **99.5%** |
| C, Military President | 977 / 1,719 | 56.8% |

The module comment asserting that the coup signal is "parsed from LLM output,
never injected by Python in LLM path" was therefore false for thousands of
published decisions.

## 4. The fix, and what it recovers

`parse_decision` now tries three extraction routes (the documented wrapper, a
bare `DECISION` delimiter, then the last JSON object in the response), uses
quote-tolerant fallback patterns, and sets an explicit flag when it genuinely
cannot read a decision. CVES L1 consumes that flag, so a substituted role
default can no longer be logged as a pass.

Re-running the published logs through the fixed parser drops unreadable rows
from **10.3% to 0.9%** for Scenario A and from **38.4% to 0.0%** for Scenario
C, and reproduces the published counts.

## 5. What the paper should say

**Publish 4,570 and 6,009.** They were correct. Do not publish 4,192 or 4,197.

**Publish the 394 gap and what causes it**, not as an unexplained discrepancy
but as a measured instrument defect with a named cause, a quantified rate, a
fix and a regression test. The honest headline figure is **4,176 interceptions
against 4,570 model-decided signals, 91.4 percent**, with the 394 attributed
to parser substitution.

**Do not write "100% corrected, zero uncorrected".** It was false before and
it is still false.

**Exact per-row reconciliation remains impossible on this dataset**, for a
reason unchanged by any of today's work: `cves_violations.jsonl` rows carry no
run identifier and no timestamp, so the two logs share no join key. The
re-run fixes this, since `run_id` is now threaded and the structured decision
is logged; reconciliation then becomes a join on `(run_id, year, agent)`
rather than a regex over prose.

**The retraction belongs in the paper.** An instrument that silently deleted
7.6 percent of the behaviour it exists to measure, found by auditing its own
counts and then found again when the first audit was itself wrong, is a more
useful contribution to the validation literature than a clean number would
have been. It should be reported that way, including the fact that the first
correction was mistaken.

## 6. Reproducing this

```
cd results_phase3
python3 - <<'EOF'
import json, collections, sys; sys.path.insert(0, "..")
from engine.elite_agents_v3 import parse_decision
role_of = {"Senior General":"senior_general","Chief Justice":"chief_justice",
           "President":"president","IIG Director":"iig_director",
           "Central Bank Governor":"central_bank_governor",
           "Finance Minister":"finance_minister","Chancellor":"chancellor"}
cs = sub = 0
for line in open("elite_decisions_A.jsonl"):
    d = json.loads(line)
    p = parse_decision(d.get("reasoning_text") or "", role_of.get(d.get("agent"), "chancellor"))
    if p.pop("_role_default_substituted", False): sub += 1
    elif p.get("coup_signal"): cs += 1
print(cs, sub)
EOF
```

Expected output: `4572 302`.
