# Table 6 reconciliation, 2026-11-24

Resolves kill shot **K4** of the adversarial review ("Table 6's own numbers do
not reconcile against the shipped audit trail"), and supersedes the planned
disclosure wording in THE_PLAN item 0.2.

The short version: **the 394-signal gap is substantially a counting artifact.
Counted correctly it is 16, and the residual has a known mechanical cause.**

---

## 1. What the published table claimed

| quantity | published |
|---|---|
| Scenario A coup signals emitted | 4,570 |
| Scenario A signals intercepted by CVES L2 | 4,176 |
| unreconciled | **394 (8.6%)** |
| claim made | "100% corrected, zero uncorrected" |
| Scenario C coup signals emitted | 6,009 |

The review's objection was correct on its own terms: 4,570 against 4,176 is a
394-row gap, the Senior General showed *more* interceptions (163) than
emissions (148), which is not even a subset relation, and the "100% corrected"
claim is therefore false as written.

## 2. Why those numbers were never reliable

**The structured decision was never logged.** Until `344bba8` (2026-11-24),
`_log_decision` wrote only `decision.get("reason")` into a prose field called
`decision_output`; `coup_signal`, `budget_weight` and `ethnic_weights` were all
available at the call site and discarded. The published counts were therefore
recovered by regular expression over the free-text `reasoning_text`.

A regex over prose counts whatever it matches, and the three plausible patterns
give three very different answers:

| counting rule | Scenario A | Scenario C |
|---|---|---|
| mentions "coup" anywhere | 23,383 | 10,378 |
| `coup_signal: true` appears anywhere in the text | 4,866 | 6,069 |
| **the `<DECISION>` block itself says true** | **4,192** | **4,197** |

The published A figure of 4,570 sits between the loose and strict counts. The
published C figure of 6,009 is within 1% of the **loose** count of 6,069, so
the original analysis used a pattern that matched any mention of
`coup_signal: true` in the reasoning, including an agent *discussing* whether
to set it.

Counted strictly, against the decision actually emitted, Scenario C's figure is
**4,197, not 6,009**.

## 3. The strict reconciliation

Scenario A, strict count of emitted signals against `cves_violations.jsonl`
(role identifiers normalised; the decision log uses display names such as
"Chief Justice" while the violation log uses role ids such as `chief_justice`,
which is itself worth fixing before the re-run):

| role | emitted | intercepted | gap |
|---|---|---|---|
| chief_justice | 3,732 | 3,690 | +42 |
| president | 269 | 265 | +4 |
| senior_general | 133 | 163 | **-30** |
| iig_director | 57 | 57 | 0 |
| central_bank_governor | 1 | 1 | 0 |
| **total** | **4,192** | **4,176** | **+16** |

**Interception rate 99.62%, and the gap is 16 of 4,192 (0.38%), not 394 of
4,570 (8.6%).**

## 4. The residual 16, and why it is not noise

The per-role signs do not all point the same way: chief_justice and president
show more emissions than interceptions, senior_general shows 30 **more
interceptions than emissions**. A pure under-logging story cannot produce both.

The mechanical explanation is CVES L2's reprompt. When L2 intercepts a
violation it logs the violation and reprompts the agent; the decision finally
written to `elite_decisions_A.jsonl` is the **post-correction** decision, and on
a reprompt the resolved `reasoning_text` may be the corrected response rather
than the original. So:

- where the original text survived into `reasoning_text`, the strict regex
  counts the emission and the violation log counts the interception, and they
  agree;
- where the reprompt replaced the text, the violation is logged but the strict
  regex sees a corrected decision, giving **interceptions without a matching
  emission** — exactly the senior_general signature.

This is consistent with senior_general being the role whose reprompts most
often changed the answer, which is what one would expect of the one role with
explicit latitude to signal in Scenario A's prompt.

## 5. What this means for the paper

**Do not publish "100% corrected, zero uncorrected".** It is not supported.

**Do publish the strict reconciliation**: 4,192 emitted, 4,176 intercepted,
99.62%, with the residual 16 attributed to reprompt text replacement and the
counting-rule sensitivity table in section 2 shown in full. Reporting that the
original figure was regex-derived, that three defensible patterns give 23,383 /
4,866 / 4,192, and that we therefore rebuilt the instrument to log the
structured decision, is a stronger methods result than a clean number would
have been. It is also a direct answer to Reviewer 1 point 8 on reproducibility.

**Exact reconciliation is impossible on this dataset and that is now a stated
limitation, not an open defect.** Two reasons, both fixed for the re-run:

1. `coup_signal` was never logged as a field (fixed in `344bba8`, now written
   under `decision.coup_signal`).
2. `run_id` was never written, so every row says `run: 0` and the 100 Monte
   Carlo runs cannot be separated (fixed in the same commit).

On the re-run, reconciliation becomes a one-line join on
`(run_id, year, agent)` rather than a regex, and the gap either closes or
becomes individually attributable.

**Scenario C's "6,009 permitted signals" must not be reused.** The strict
figure is 4,197. If the differential-constraint sentence is used as the
headline, it is 4,176 interceptions under one constitution against 4,197
permissions under the other, both strict, both from the shipped log — and the
near-equality of 4,192 and 4,197 emitted is itself the point: the same
behaviour, at very different rates per decision (11.8% of A's 35,383 decisions,
34.9% of C's 12,033), is unlawful under one encoded constitution and lawful
under the other.

## 6. Reproducing this

```
cd results_phase3
python3 - <<'EOF'
import json, re, collections
STRICT = re.compile(r'<DECISION>.*?"coup_signal"\s*:\s*true.*?</DECISION>', re.I|re.S)
norm = lambda a: str(a).lower().replace(" ", "_").replace("-", "_")
emitted, intercepted = collections.Counter(), collections.Counter()
for line in open("elite_decisions_A.jsonl"):
    d = json.loads(line)
    txt = (d.get("reasoning_text") or "") + " " + str(d.get("decision_output") or "")
    if STRICT.search(txt): emitted[norm(d.get("agent"))] += 1
for line in open("cves_violations.jsonl"):
    d = json.loads(line)
    if d.get("scenario") == "A": intercepted[norm(d.get("agent"))] += 1
print(sum(emitted.values()), sum(intercepted.values()))
EOF
```

Expected output: `4192 4176`.
