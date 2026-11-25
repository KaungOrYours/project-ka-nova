# Published artefacts, frozen

This directory holds the results and audit trail **as submitted** to IEEE
Access (Access-2026-37966). Nothing in the simulation writes here.

## Why this directory exists

These files used to live in `results_phase3/`, which is also where every
simulation run writes. That meant the shipped audit trail was tracked in git
*and* was an append target of any normal run. It was polluted twice:

- 2026-10-29, by test runs.
- 2026-11-25, by a verification run, which appended 427 lines to
  `elite_decisions_A.jsonl` and 350 to `elite_decisions_C.jsonl` and was
  initially misdiagnosed as pre-existing dirty state.

Two incidents in under a month meant the layout was the defect, not the
discipline. The invariant now is simple and mechanical:

> **`results_phase3/` contains nothing tracked. `published/` is never written
> to by code.**

`results_phase3/` is gitignored and holds live run output. If a run pollutes
something now, it pollutes an untracked file and `git status` stays clean.

## Reading these files

Analysis tooling (`analysis/kpi.py`, `charts/visualize.py`) defaults to
`results_phase3/`. To point it at this frozen snapshot instead:

```
KA_NOVA_RESULTS_DIR=published python3 -m analysis.kpi
```

## The pollution hazard, which still exists for live runs

`engine/elite_agents_v3.py` and `run_phase3.py` both read
`KA_NOVA_RESULTS_DIR` at **module import time**, and `run_phase3.py` has no
`--results-dir` flag. The environment variable is the only isolation
mechanism and must be exported **before** the process starts, not set from
inside it. Moving these files out of the write path means getting that wrong
can no longer damage anything tracked.

## Provenance and status

Produced July 2026: 100 Monte Carlo runs per scenario, 11,000 citizens, 50
years, `llama3.2:3b` on an RTX 4090. Scenarios A (self-designed, MFU) and C
(2008 Myanmar) only.

**These numbers are superseded and must not be quoted as current.** The
instrument audit of November 2026 found ten defects in the generative path,
several of which corrupt what is recorded here, including a parser defect
that discarded the model's decision for four of seven constitutions. Three of
the four headline effect sizes derived from this data are artifacts, the
Table 6 reconciliation drawn from it was retracted, and the violation records
here carry the old `article_injected` key, renamed to `article_attributed`
on 2026-11-25.

They are kept, unaltered, because the audit's claims are checkable only
against the exact files that were shipped. That is their entire remaining
purpose. The campaign will produce the replacement set; it will not overwrite
this one.
