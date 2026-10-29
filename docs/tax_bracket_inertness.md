# Tax Bracket Inertness: Income-Distribution Reproduction and Per-Scenario Evidence

Prepared 2026-10-29 by `senior-simulation-engineer`, as the evidence record behind the disclosure
decided in `.claude/memory.md` section 5j, decision 5: encode the real statutory tax schedules for
all six non-MFU constitutions and disclose, rather than hide or "fix" by rescaling, the fact that
`agents/citizen.py`'s income generator cannot represent most of each real schedule's upper bands.

This file does not propose any value change. It independently reproduces the income distribution
the `senior-researcher` pass described in each `config/constitution_<name>_encoding/README.md`
section 7.2, reports where that reproduction agrees and disagrees with the figures already quoted
in those packages, and gives a per-scenario, per-band population-share table for all seven
constitutions (the six just re-encoded plus MFU, which is the same engine limitation under a
different, self-designed schedule).

---

## 1. The consumer contract, re-verified against live source

`agents/citizen.py:869-895`, `_calculate_progressive_tax()`, read directly rather than assumed:

```python
def _calculate_progressive_tax(self, income: float, poverty_line: float) -> float:
    if income <= poverty_line:
        return 0.0
    brackets = self.model.CONSTITUTION.economic.TAX_BRACKETS
    taxable = income
    tax = 0.0
    for (low_mult, high_mult, rate) in brackets:
        bracket_low = poverty_line * low_mult
        bracket_high = (poverty_line * high_mult
                        if high_mult != float('inf')
                        else float('inf'))
        if taxable <= bracket_low:
            break
        income_in_bracket = min(taxable, bracket_high) - bracket_low
        if income_in_bracket > 0:
            tax += income_in_bracket * rate
    return tax
```

Each of the six requirements the research pass asserted is confirmed true against this live code,
not assumed:

| # | Requirement | Confirmed from the code |
|---|---|---|
| 1 | Three-tuples required | `for (low_mult, high_mult, rate) in brackets` unpacks three values per band. A flat tuple of bare floats makes each `band` a bare `float`, and `float` has no `__len__`/is not iterable into three names, so this raises `TypeError` on unpack |
| 2 | Bands must be strictly ascending by `low_multiple` | `if taxable <= bracket_low: break` exits the loop the moment an out-of-order or already-passed band is reached, with no error, silently truncating every band after it |
| 3 | Bands must be contiguous | `income_in_bracket = min(taxable, bracket_high) - bracket_low` assumes the previous band's high is this band's low. A gap leaves that slice of income untaxed; an overlap taxes it twice. Nothing checks either |
| 4 | Top band's `high_multiple` must be literally `float('inf')` | `bracket_high` only becomes infinite on the exact test `high_mult != float('inf')`. A finite top band (e.g. a typo'd `999999.0`) silently leaves all income above it untaxed forever |
| 5 | Band count unconstrained | No `len()` assumption anywhere in the loop; 2-band and 18-band schedules both run |
| 6 | Income at or below 1.0x the poverty line is always untaxed | `if income <= poverty_line: return 0.0` guards the whole function before the loop runs at all |

All six are exactly as the research pass described. See section 3 below for the `Constitution.validate()`
structural check now added to close requirements 1 to 4 against silent failure (implemented in
`config/constitution*.py`, not this file; summarised here only as the thing this document's evidence
supports).

`_init_income()`, `agents/citizen.py:1222-1227`, re-read directly:

```python
def _init_income(self) -> float:
    base_income = 1000.0
    age_factor = min(2.0, self.age / 30.0) if self.age > 0 else 0.5
    education_factor = 1.0 + self.education_level * 1.5
    return base_income * age_factor * education_factor * random.uniform(0.8, 1.2)
```

`education_level` is drawn by `_init_education()` (`agents/citizen.py:1229-1240`), by age band:

```python
if self.age < 6:    return 0.0
elif self.age < 12:  return random.uniform(0.05, 0.20)
elif self.age < 18:  return random.uniform(0.20, 0.45)
elif self.age < 23:  return random.uniform(0.40, 0.65)
else:                return random.uniform(0.45, 0.85)
```

**Correction to the research pass, found on this re-verification.** Every encoding package's
section 7.2 describes `education_level` as drawn "(max 1.0)" and states the resulting hard ceiling
on simulated income as **6.0x the poverty line** (`2.0 age_factor x 2.5 education_factor x 1.2
noise`). The live code's oldest age band (23 and over, which is also the band that produces every
income-maximising draw) is `random.uniform(0.45, 0.85)`, whose maximum is **0.85, not 1.0**. The
true education_factor ceiling is therefore `1 + 0.85*1.5 = 2.275`, not `2.5`, and the true hard
ceiling on simulated income is:

```
2.0 (age_factor cap) x 2.275 (true education_factor cap) x 1.2 (noise cap) = 5.46x the poverty line
```

**not 6.0x.** This is a small correction (5.46x vs. 6.0x, about 9 percent) and it does not change
any policy conclusion in this document or in the six encoding packages: it makes the inertness
finding slightly *more* severe, not less, since the real reachable ceiling is lower than the figure
quoted. It is recorded here because section 11 of `.claude/memory.md` requires re-verification
rather than restatement of the research pass's own figures, and this is the one place that
re-verification turned up a (minor, non-reversing) discrepancy.

---

## 2. Independent reproduction of the income distribution

Reproduced directly from the two live functions above, `random.seed(20261029)`, N = 500,000 draws,
quantiles against the initial poverty line of 1000.0. Two methods, because the research pass's own
"200,000 working-age draws" does not specify its age-sampling convention and the live engine's real
population generator (`CitizenPopulation._assign_age()`) samples a full-population age pyramid
(Myanmar's, used for every scenario; see the separate, already-tracked `ETHNIC_ARCHETYPE_PROPORTIONS`
gap) rather than an adults-only range:

**Method A, working-age only** (`age ~ Uniform{18, ..., 65}`, the convention that reproduces the
research pass's own quoted table almost exactly and is used here as the closest honest match to it):

| quantile | p1 | p5 | p10 | p25 | p50 | p75 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| **This reproduction** | 0.96x | 1.17x | 1.36x | 1.90x | **2.68x** | 3.45x | 4.04x | 4.38x | 4.90x | 5.45x |
| **Encoding packages' quoted table** | 0.97x | 1.18x | 1.35x | 1.87x | **2.68x** | 3.46x | 4.11x | 4.49x | 5.06x | 5.63x |

The median matches exactly (2.68x both). The lower half matches to within 0.03x throughout. The
upper tail (p90 upward) runs 1.5 to 3 percent below the quoted table, consistent with the education
ceiling correction in section 1: a true maximum draw of 0.85 rather than 1.0 slightly compresses the
reachable top of the distribution relative to a generator that could reach education_level = 1.0.
The quoted table's own maximum, 5.63x, in fact **exceeds the true mathematical ceiling of 5.46x**
derived in section 1, which is independent confirmation that the "(max 1.0)" education description
in each encoding package is the source of the small discrepancy, not a different age-sampling
convention or random seed.

**Method B, the real live population generator** (every age 0 to 80, sampled via the actual
`CitizenPopulation._assign_age()` Myanmar population pyramid that every one of the seven scenarios
uses to build its citizen population; this is what the engine actually simulates, including children
and retirees, not an analyst's adults-only slice):

| quantile | p1 | p5 | p10 | p25 | p50 | p75 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| income / poverty line | 0.03x | 0.11x | 0.22x | 0.62x | 1.72x | 2.92x | 3.80x | 4.20x | 4.84x | 5.45x |

Under Method B, **34.4 percent of the whole simulated population sits at or below 1.0x the poverty
line** and is tax-exempt purely by `_calculate_progressive_tax()`'s own early-return guard,
regardless of which constitution is active (this guard runs identically for all seven; it is an
engine mechanic, not a constitutional parameter). Both methods agree on the one number that matters
most for this document: **the maximum ever observed, across 500,000 draws each, is 5.45x**,
matching the corrected theoretical ceiling of 5.46x to within sampling noise. There is no
realistic age/education combination that reaches far beyond this, in either method.

---

## 3. Per-scenario, per-band inertness table

For each constitution's `TAX_BRACKETS` (the schedules now encoded in `config/constitution*.py`,
replacing both the 2026-10-29 "SCHEMA FIX" placeholder widths and, where the research found them
wrong, the placeholder rates), the population share landing in each band, computed against Method B
(the real whole-population draw, N = 500,000, the most representative of what the live engine
actually simulates). A band with population share exactly 0.000% across half a million draws is
reported as **NEVER FIRES**; this is a measurement, not a projection, since no draw in a sample this
size reached that band and the sample's own observed maximum (5.45x) sits below the band's own low
threshold in every such case.

### A (MFU), 6 bands, for comparison; this schedule was not touched

| band | range (x poverty line) | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 1.00 | 0% | 34.403% | fires |
| 2 | 1.00 to 2.00 | 10% | 22.045% | fires |
| 3 | 2.00 to 5.00 | 20% | 43.053% | fires |
| 4 | 5.00 to 10.00 | 30% | 0.500% | fires (thinly) |
| 5 | 10.00 to 20.00 | 40% | 0.000% | **NEVER FIRES** |
| 6 | 20.00 to inf | 50% | 0.000% | **NEVER FIRES** |

MFU's own self-designed schedule is affected by the identical engine limitation: its top two bands
(40 percent and 50 percent marginal rates) can never fire on any simulated citizen. This is worth
stating plainly because it shows the inertness finding is a property of the income generator shared
by all seven scenarios, not an artefact introduced by encoding the six new schedules.

### C (Myanmar 2008), 12 bands, Option 1 (2012 proxy, see `config/constitution_2008_encoding/README.md` section 7.5)

| band | range | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 1.33 | 1% | 41.271% | fires |
| 2 | 1.33 to 2.66 | 2% | 28.837% | fires |
| 3 | 2.66 to 3.99 | 3% | 22.517% | fires |
| 4 | 3.99 to 5.32 | 4% | 7.332% | fires |
| 5 | 5.32 to 7.98 | 5% | 0.041% | fires (thinly) |
| 6-12 | 7.98 to inf | 6% to 20% | 0.000% each | **NEVER FIRE (7 of 12 bands)** |

### SK, 16 bands

| band | range | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 1.62 | 6% | 47.682% | fires |
| 2 | 1.62 to 2.25 | 8% | 14.308% | fires |
| 3 | 2.25 to 3.15 | 10% | 17.165% | fires |
| 4 | 3.15 to 4.32 | 12% | 16.904% | fires |
| 5 | 4.32 to 5.68 | 15% | 3.941% | fires |
| 6-16 | 5.68 to inf | 18% to 55% | 0.000% each | **NEVER FIRE (11 of 16 bands)** |

South Korea is the schedule that survives this engine limitation best: 5 of its 16 real bands fire,
more than any other non-MFU scenario, because its real 1988 thresholds are themselves tightly
bunched in the 0 to 5.7x range (bracket creep from an unindexed 1982 schedule still in force in
1988).

### TH, 8 bands

| band | range | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 4.65 | 0% | 98.225% | fires (exempt band) |
| 2 | 4.65 to 9.31 | 5% | 1.775% | fires (thinly) |
| 3-8 | 9.31 to inf | 10% to 35% | 0.000% each | **NEVER FIRE (6 of 8 bands)** |

### PK, 2 bands

| band | range | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 16.10 | 0% | 100.000% | fires (exempt band; this is the entire population) |
| 2 | 16.10 to inf | 35% (FLAGGED GUESS) | 0.000% | **NEVER FIRES** |

**Pakistan's exemption threshold is provably unreachable, and by a wide margin.** The real sourced
exemption multiple is 16.10x the 1984-85 poverty line (section 7.4 of
`config/constitution_pakistan_encoding/README.md`). The engine's own corrected hard ceiling is
5.46x (section 1 above), so the real exemption threshold sits at **2.95 times the maximum income any
simulated citizen can ever draw**. No simulated Pakistani citizen agent, in any run, at any seed, can
ever reach this threshold; the 35 percent top rate is mathematically dead code for the lifetime of
the simulation. This is exactly what the flagged GUESS on that rate was deliberately placed to be
safe against (`config/constitution_pakistan.py`'s inline comment), and this table is the proof that
the placement succeeds: the one unsourced number in the Pakistan schedule cannot affect any
published value, because it never executes.

### CL, 8 bands

| band | range | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 4.72 | 0% | 98.561% | fires (exempt band) |
| 2 | 4.72 to 14.16 | 5% | 1.439% | fires (thinly) |
| 3-8 | 14.16 to inf | 10% to 50% | 0.000% each | **NEVER FIRE (6 of 8 bands)** |

### DE, 18 bands

| band | range | rate | population share | status |
|---|---|---|---|---|
| 1 | 0.00 to 1.00 | 0% | 34.403% | fires |
| 2 | 1.00 to 1.60 | 10% | 12.831% | fires |
| 3 | 1.60 to 3.20 | 15% | 32.831% | fires |
| 4 | 3.20 to 4.80 | 20% | 18.814% | fires |
| 5 | 4.80 to 6.40 | 25% | 1.121% | fires (thinly) |
| 6-18 | 6.40 to inf | 30% to 95% | 0.000% each | **NEVER FIRE (13 of 18 bands)** |

Germany fires the most bands of any schedule in absolute terms (5 of 18) because its real 1949
thresholds are, like Korea's, bunched low relative to its own benchmark (the 750 DM Grundfreibetrag
is a true zero-rate band matching the engine's own guard almost exactly). But the real 1949 top
marginal rate of 95 percent, the single most dramatic number sourced in this whole pass, **never
once applies to a simulated citizen**, because its band starts at 333.33x the poverty line, 61 times
the engine's reachable ceiling.

### Summary across all seven

| scenario | bands total | bands that fire | bands that never fire | population share paying any tax at all |
|---|---|---|---|---|
| A (MFU) | 6 | 4 | 2 | 65.6% |
| C (Myanmar) | 12 | 5 | 7 | 58.7% |
| SK | 16 | 5 | 11 | 52.3% |
| TH | 8 | 2 | 6 | 1.8% |
| PK | 2 | 1 | 1 | 0.0% |
| CL | 8 | 2 | 6 | 1.4% |
| DE | 18 | 5 | 13 | 65.6% |

"Population share paying any tax at all" is `1 - (share in the lowest, 0%-rate or exempt band)`.
Thailand, Pakistan and Chile converge on essentially the same number (0.0 to 1.8 percent) because
all three real 2017/1985/1990 exempt thresholds sit well above the engine's own income ceiling, the
exact finding each encoding package's section 7.2 anticipated. Germany and MFU pay tax most widely
not because their real top rates are reachable (they are not), but because their bottom bands happen
to start low relative to the poverty line.

---

## 4. Effective average tax rate, before versus after, confirmed

Computed directly with `_calculate_progressive_tax()`'s own logic (not approximated), at the
engine's own median simulated income (2.68x the poverty line, Method A above), comparing the
2026-10-29 "SCHEMA FIX" placeholder schedule (equal-width poverty-line bands, carrying over whatever
rates were already authored) against the schedule now encoded:

| scenario | before (placeholder widths) | after (real schedule) |
|---|---|---|
| C (Myanmar) | 4.40% | 1.51% |
| SK | 13.93% | 7.11% |
| TH | 4.40% | 0.00% |
| PK | 4.40% | 0.00% |
| CL | 4.40% | 0.00% |
| DE | 11.31% | 8.28% |

**All six figures match the research pass's own measured values exactly**, re-derived independently
here rather than copied. Thailand, Pakistan and Chile go to exactly zero because their real exempt
thresholds (4.65x, 16.10x, 4.72x respectively) sit above or near the top of the engine's reachable
income range, so the entire simulated tax-paying population that previously fell inside the
placeholder's narrow equal-width bands now falls inside the real, much wider zero-rate band. South
Korea and Germany fall by roughly half (13.93 to 7.11, 11.31 to 8.28) rather than to zero, because
their real entry rates and first few thresholds are genuinely low and reachable, so some real
progressivity still shows up in the simulated population, just less than the placeholder implied.
Myanmar falls from 4.40 to 1.51 percent because the real 2012-proxy schedule's bottom bands carry
much lower rates (1 to 4 percent) than the placeholder's borrowed rates (5 to 20 percent) ever did.

**Gini, measured directly, before versus after, small-scale diagnostic run** (seed 42, 300 citizens,
15 years, rule-based, `use_llm=False`, the same "de-risk before applying" method used earlier this
session for the corruption year-zero change; NOT the locked N=100/11,000-citizen/50-year publication
design, and not a substitute for the full re-run every affected scenario still needs before any
number is published):

| scenario | Gini before | Gini after | delta | tax revenue before | tax revenue after |
|---|---|---|---|---|---|
| C | 0.1598 | 0.1673 | +0.0075 | 972.8 | 449.3 |
| SK | 0.1323 | 0.1387 | +0.0064 | 2368.7 | 2607.6 |
| TH | 0.2004 | 0.2081 | +0.0077 | 1479.9 | 0.0 |
| PK | 0.3618 | 0.3725 | +0.0107 | 1286.7 | 0.0 |
| CL | 0.1608 | 0.1688 | +0.0080 | 149.8 | 0.0 |
| DE | 0.1338 | 0.1387 | +0.0049 | 0.0 | 9.1 |

At this toy scale, every scenario's Gini moves by a small positive amount (0.005 to 0.011), in the
same direction, regardless of whether that scenario's tax revenue collapsed to zero (TH, PK, CL) or
not (SK, DE). This is because the published Gini is state-GDP dispersion
(`.claude/memory.md` bug #2), fed by each citizen's post-tax income via `gdp_contribution`, and the
schedule change shifts more than just the tax line itself; it also changes which citizens keep more
of their income to spend, save or owe as debt in subsequent years, which compounds through the
state-GDP growth loop over the simulated horizon. Do not read these six deltas as the real, locked
effect size. They are a directional, small-N sanity check, exactly as this session's earlier
corruption year-zero de-risking exercise was; the real deltas require the full N=100,
11,000-citizen, 50-year run that is now owed for all six affected scenarios, and the Gini column
"cannot be presented as continuous across this change" (the exact wording already fixed by Kaung's
decision 5 in `.claude/memory.md` section 5j).

---

## 5. Scenario A is unaffected, proven two ways

**(a) Code inspection.** `config/constitution.py`'s `EconomicConfig.TAX_BRACKETS` tuple (MFU's own
schedule) was not edited by this work; `git diff config/constitution.py` shows the only changes in
this file are a new `_tax_brackets_structurally_valid()` staticmethod and one new line appended to
`validate()`'s checks list. Both are new code, not a changed value. Independently, `validate()` is
never called anywhere in the live simulation path (`model_phase3.py`, `run_phase3.py`,
`agents/*.py`, `engine/*.py`, `institutions/*.py`, confirmed by direct grep returning zero matches),
so even if it were somehow wrong it could not affect any simulated trajectory; it is reachable only
from a human or a test calling `.validate()` directly.

**(b) Same-seed hashed KPI comparison.** Scenario A was run for 15 simulated years (seed 42, 300
citizens, rule-based) under two file states: (i) the fully-edited `config/constitution.py` as it
ships from this work, and (ii) a reconstruction of this file with only this work's own two additions
(the staticmethod and the validate() check line) removed, leaving every other line, including the
corruption year-zero correction applied earlier the same session by other work, untouched. A
`sha256` hash of the full 15-year trajectory (`corruption_index`, `coup_risk`, `stability_index`,
`iig_effectiveness`, `gini_coefficient`, `north_star_progress`, `ethnic_harmony`, `tax_revenue`,
every year) was identical in both cases:

```
81b41af2cd5952b49e4a221f6c15ffa2f1d559d0cac01aac68fc72b4a3fa1907
```

This isolates this specific task's contribution from the rest of today's session (whose own,
separate changes to `config/constitution.py` are not this task's to re-verify) and confirms Scenario
A's simulated behaviour is byte-for-byte unaffected by anything done here.

---

## 6. What this document does not establish

- **No full-scale re-run.** Every number in section 4's Gini table is a 300-citizen, 15-year,
  single-seed diagnostic, not the locked N=100/11,000-citizen/50-year publication design. The six
  affected scenarios (C, SK, TH, PK, CL, DE) still need that full re-run before any Gini or
  effective-tax number from this change can be published.
- **No claim about whether the income generator should be widened.** Section 11's standing realism
  requirement and this session's decision 5 explicitly reject rescaling the brackets to fit the
  engine; widening `_init_income()`'s dispersion instead was considered and declined for this
  resubmission, as a separate simulation-design change touching the locked A/C numbers
  (`.claude/memory.md` section 5j, decision 5). This document only measures the consequence of the
  decision already made, it does not revisit it.
- **No new finding about Gini's own unit mismatch.** The state-GDP-dispersion-versus-household-
  income-Gini issue (bug #2) is unchanged by this work and is tracked separately.
