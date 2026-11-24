# Manuscript working directory

**Status: DRAFT, not submittable. Two blocking inconsistencies, listed below.**

| file | what it is |
|---|---|
| `ka_nova_access_2026.tex` | IEEE Access manuscript, authored 2026-11-24 from scratch (no .tex had ever existed; the submitted paper exists only as a PDF) |
| `references.bib` | bibliography |
| `response_to_reviewers.md` | Response to Reviewers in IEEE's mandated template, all 12 concerns |

## Before this compiles

`ieeeaccess.cls` is not vendored. Download it from the IEEE Author Center and
drop it beside the .tex. `\todo{}` renders red and is toggled by
`\pendingvisibletrue`.

## BLOCKING: the manuscript and the response contradict each other

1. **Section VII-A still contains the RETRACTED reconciliation** (4,192
   emitted, gap of 16, "99.62 percent", and an L2-reprompt explanation the
   code cannot perform). `docs/table6_reconciliation.md` was rewritten on
   2026-11-24 to retract exactly this. The response document states the
   corrected position (4,570 emitted, 4,176 intercepted, 394 gap, 91.4
   percent). **Until the .tex is rewritten, submitting both would publish two
   contradictory accounts of the same table.**

2. **The .tex is still built on the A-vs-C controlled pair.** Scenarios A and
   B are dropped from the design. The abstract, `tab:scenarios`, Section
   III-B and Section VII-B all need re-basing onto South Korea and Pakistan.
   Counts of "seven encodings" and "49 role prompts" become six and 42.

3. **Line 630 asserts an absence**: "no scenario carries an output-fixing
   directive in any of its seven role prompts." That claim was falsified once
   already. Replace with the search-method-and-bound form used in the
   response: what was searched for, by what method, what the search did not
   cover.

## Two concerns that cannot honestly be claimed as addressed

- **R1 pt.6, figures.** They do not exist. The Author action line is a stub.
- **R1 pt.7, AI-use disclosure.** The underlying factual determination about
  how figures 1-4 were produced has never been made by the authors.

Neither needs compute or data. Both are explicit, visible, unmet requests in
a venue with a binary decision.
