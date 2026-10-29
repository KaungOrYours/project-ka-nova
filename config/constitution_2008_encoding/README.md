# 2008 Myanmar Constitution Encoding — D's Workspace

## Your task
Fill all ??? placeholders in constitution_2008_template.py.

## Steps
1. Open PDF: https://www.constituteproject.org/constitution/Myanmar_2008.pdf
2. Open constitution_2008_template.py
3. Find every ??? — the answer is in the comment next to it
4. Replace ??? with the value
5. Run: python3 config/constitution_2008_encoding/constitution_2008_template.py
6. Should print: constitution_2008.py loaded successfully and Validation: PASS
7. Copy completed file to config/constitution_2008.py
8. Push with commit message: feat: encode 2008 Myanmar military constitution (D)

## Questions
Ask Kaung directly — do not modify any other files.

---

# 7. Provenance: real personal income tax bracket structure at year zero (2008)

*Added 2026-10-29 by `senior-researcher`, per `.claude/memory.md` section 11's standing realism
requirement.*

**Note on numbering.** Everything above this line is Devy's original 17-line encoding task sheet from
the Scenario C encoding pass; this package has no sections 1 to 6. The section number 7 is used
deliberately so that cross-references line up with the five new-country packages
(`config/constitution_<name>_encoding/README.md` section 7 in each), all of which received the same
treatment on the same date. This is the first provenance section this package has ever had.

Reason this section exists: the `SCHEMA FIX 2026-10-29` tag in `config/constitution_2008.py`
(lines 618 to 636) added equal-width poverty-line bands (0 to 1x, 1 to 2x, and so on) around the
already-authored marginal rates purely to stop a `TypeError` crash once bug #11's
constitution-propagation fix made each scenario read its own `economic.TAX_BRACKETS` instead of
MFU's. The fix itself was correct and the rates were not altered, but the band widths are unsourced
placeholder content, and they reach a published metric: `agents/citizen.py:862-867` deducts tax from
citizen income, `:904` computes `gdp_contribution = productivity * income * 0.001` into state GDP,
and the live Gini (`agents/institutional.py:141`, `_calculate_gini`) is the dispersion of state GDP.
Scenario C is one of the two scenarios whose numbers are already published, so this matters more here
than anywhere else. No `config/constitution*.py` file is edited by this section; the tuples below are
a proposal for the encoding step.

## 7.1 What the consumer function actually requires

Read from `agents/citizen.py`, `_calculate_progressive_tax()` (line 869) and its caller
`_pay_taxes()` (line 838). Identical for all seven scenarios, so this subsection is repeated
verbatim in every encoding package.

| Requirement | Why | Consequence of getting it wrong |
|---|---|---|
| Schema is `Tuple[Tuple[float, float, float], ...]` = `(low_multiple, high_multiple, marginal_rate)` | The loop unpacks three values per band | A flat tuple of bare rates raises `TypeError` on unpack. This was the bug #11 follow-on crash |
| Bands must be sorted strictly ascending by `low_multiple` | The loop `break`s as soon as `taxable <= bracket_low` | An out-of-order band silently truncates the rest of the schedule, no error raised |
| Bands must be contiguous, `band[i].high == band[i+1].low` | `income_in_bracket = min(taxable, bracket_high) - bracket_low` | A gap leaves that income slice untaxed; an overlap taxes it twice. No validation catches either |
| The top band's `high_multiple` must be exactly `float("inf")` | `bracket_high` is set to infinity only on the literal test `high_mult != float('inf')` | A finite top band silently leaves all income above it untaxed |
| Any number of bands is fine | No `len()` assumption anywhere | 2-band and 18-band schedules both work |
| Multiples are of the live simulated poverty line, not currency | `bracket_low = poverty_line * low_mult` | |
| Income at or below 1.0x the poverty line is always untaxed | `if income <= poverty_line: return 0.0` guards the whole function | A non-zero rate on a band starting at 0.0 therefore applies to the first poverty-line slice only for citizens who are above the poverty line |
| `Constitution.validate()` does not inspect `TAX_BRACKETS` at all | Verified by grep | A malformed schedule passes validation and fails at runtime, or worse, silently miscomputes |

The poverty line itself is not constitutional. `agents/institutional.py:289` starts
`TaxSystemAgent.poverty_line` at 1000.0, `:303-311` updates it annually and clamps it to
[500, 5000], and `agents/citizen.py:861` falls back to 1000.0 if the key is missing. At the default
`gdp_growth_rate` of 0.02 the line grows about 0.4 percent a year, so roughly 1232 by year 50.

## 7.2 Critical engine finding: the simulated income distribution is far narrower than any real one

This is the most important thing in this section and it applies to all seven scenarios.

`agents/citizen.py:1222-1227`, `_init_income()`, is
`1000.0 * min(2.0, age/30) * (1 + education_level*1.5) * uniform(0.8, 1.2)`, with
`education_level` drawn by age band in `_init_education()` (max 1.0). Income thereafter changes only
by tax paid (`:865`) and the Article VIII elite transfer (`:925-926`), both small. Simulated over
200,000 working-age draws against the initial poverty line of 1000:

| quantile | p1 | p5 | p10 | p25 | p50 | p75 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|---|---|---|
| income / poverty line | 0.97x | 1.18x | 1.35x | 1.87x | 2.68x | 3.46x | 4.11x | 4.49x | 5.06x | 5.63x |

**There is zero probability mass above about 5.6x the poverty line.** Any real bracket boundary above
that is mechanically inert.

This is a limitation of the income generator, not of the tax encoding, and a reviewer can find it in
ten minutes. Two honest options, both requiring Kaung's decision:
- (a) encode the real brackets and disclose which real bands cannot fire in this engine;
- (b) widen `_init_income()`'s dispersion so real brackets can bind, which is a simulation-design
  change affecting every scenario including the locked Scenario A and C numbers.

Do **not** rescale the brackets to "fit" the engine. That would reintroduce exactly the invented
content this section exists to remove.

## 7.3 The real schedule in force in 2008: PARTIALLY ESTABLISHED

### What IS established

| Fact | Value | Source |
|---|---|---|
| Governing instrument | **Income Tax Law 1974** (Myanmar Income Tax Law, MITL), as amended by Ministry of Finance and Revenue notifications, administered by the Internal Revenue Department. In force throughout 2008 and until the 2012 reform | Internal Revenue Department of Myanmar; multiple professional tax summaries |
| Resident salary income rate range in force before 2012 | **Progressive, 3 percent to 30 percent** | DFDL, "Tax Reforms in Myanmar": "Under Notification 107/2012 dated 15 March 2012, salary income in local currency was reduced to a progressive rate of 1% to 20% from the previous progressive rate of 3% to 30%." Independently corroborated by the Myanmar Investment Commission / FAO country investment guide (FAO document AC901E, section 6.4): "progressive tax rates starting from 3 per cent to a maximum ceiling of 30 per cent is applicable" |
| Allowances in force under the 1974 law, pre-reform | Basic allowance of **20 percent of total income subject to a cap of K 6,000**; spouse relief **K 2,500**; child allowances **K 500 to K 1,000** depending on age | FAO / Myanmar Investment Commission guide, section 6.4 (same document) |
| Non-resident foreigners | Flat 35 percent, or the progressive rates, whichever is greater | Same |
| Structural character of the tax | The 1974 schedule's nominal thresholds and allowances were **never indexed.** A K 6,000 cap on the basic allowance against 2008 incomes is economically negligible, which means by 2008 the schedule's own top marginal rate was reached at a nominal income far below any realistic formal-sector salary. In practice the personal income tax behaved as a near-flat 30 percent levy on the small formal-sector population inside the tax net | **Researcher's inference from the sourced allowance magnitudes**, labelled as an inference and not as an observation |

### What could NOT be established

**The kyat slab thresholds of the 2008 schedule.** Attempted: the IRD's own Income Tax Law PDF; the
IMF's 2014 "Tax Systems in Myanmar" Ministry of Finance presentation; the ASEAN tax summary hosted by
the Thai Revenue Department (which gives only "3% - 50%" with no bands); the Myanmar Baptist
Convention / MBC Myanmar tax-structure compilation (its "Progressive Income Tax Rates On Salary"
table is the **post-2012** 1-to-20-percent schedule despite the document also citing MoFR
Notifications 120/2006 and 121/2006 nearby, and its allowance figures of "spouse max 300k, children
max 200k, maximum allowance K 10,000,000" confirm it is post-reform); the IGC / Abramovsky et al.
2019 effective-tax-rate study (post-2011 regime only); and the VDB Loi 2012 tax-reform note (dead
link). MoFR Notification 121/2006, "Income Tax on Individuals", is the instrument most likely to
contain the 2008 table and is not online.

### The nearest documented full schedule

MoFR **Notification 107/2012** of 15 March 2012, effective 1 April 2012, twelve bands:

| band | chargeable income per annum (kyat) | rate | | band | chargeable income per annum (kyat) | rate |
|---|---|---|---|---|---|---|
| 1 | 1 to 500,000 | 1% | | 7 | 4,000,001 to 6,000,000 | 7% |
| 2 | 500,001 to 1,000,000 | 2% | | 8 | 6,000,001 to 8,000,000 | 9% |
| 3 | 1,000,001 to 1,500,000 | 3% | | 9 | 8,000,001 to 10,000,000 | 11% |
| 4 | 1,500,001 to 2,000,000 | 4% | | 10 | 10,000,001 to 15,000,000 | 13% |
| 5 | 2,000,001 to 3,000,000 | 5% | | 11 | 15,000,001 to 20,000,000 | 15% |
| 6 | 3,000,001 to 4,000,000 | 6% | | 12 | above 20,000,000 | 20% |

Source: Myanmar tax-structure compilation hosted by MBC Myanmar
(`mbcmyanmar.org/wp-content/uploads/2019/04/myanmar-tax-structure.pdf`), retrieved and text-extracted
2026-10-29. This is **four years after year zero and after a deliberate re-denomination of the
thresholds**, so it is a proxy and nothing more.

### The currently encoded rates

`config/constitution_2008.py` holds `(0.00, 0.05, 0.10, 0.20, 0.30)`, the SCHEMA FIX comment
correctly noting the rates themselves were already labelled "Proxy, not specified in constitution".
Assessment against the real data: **the 0.30 top rate is correct** for the pre-2012 regime. The
0.00 entry band is **wrong in kind**: the real 1974-law schedule had no zero-rate band of any
material width, its entry rate was 3 percent, and the subsistence exemption lived in the K 6,000
allowance cap rather than in a zero band. The intermediate 0.05, 0.10 and 0.20 rates are not
attributable to any sourced Myanmar schedule.

## 7.4 Poverty line and the conversion

| Item | Value | Source and status |
|---|---|---|
| **IHLCA-I (2004/05) poverty line** | Food poverty line **118,402** kyat, non-food **43,734** kyat, **total poverty line 162,136 kyat per adult equivalent per year**, at November 2004 prices | **PRIMARY-SOURCE VERIFIED.** *Integrated Household Living Conditions Survey in Myanmar: Quantitative Survey Technical Report*, prepared by IDEA International Institute (Quebec) and the IHLCA Project Technical Unit (Yangon), with support from the Planning Department and Central Statistical Organization, Ministry of National Planning and Economic Development. Tables 6.2 and 6.3, pages 21 and 23. Retrieved 2026-10-29 from `monpifer.gov.mm/sites/default/files/upload_pdf/2020/08/IA1_Technical_Report_0.pdf` and read directly |
| **IHLCA-II (2009/10) poverty line** | **376,151 kyat per adult equivalent per year** | **SECONDARY-VERIFIED ONLY.** Widely cited for IHLCA-II (MNPED / UNDP / UNICEF / SIDA, 2011) and reported alongside the World Bank's 2014 reset to 440,345 kyat per adult equivalent per year. Not confirmed against the IHLCA-II report itself in this pass |
| **Used for the conversion** | **376,151 kyat per adult equivalent per year** | Year zero 2008 sits between the two surveys. Myanmar's inflation over 2005 to 2008 was high, so 2008 prices were much closer to 2009/10 than to November 2004, and IHLCA-II is the closer benchmark despite being one to two years late. The 2004/05 figure of 162,136 is the primary-verified alternative; using it instead would multiply every bracket multiple below by 2.32 |

Conversion is `threshold_kyat / 376,151`:

| threshold (kyat) | multiple | | threshold (kyat) | multiple |
|---|---|---|---|---|
| 500,000 | 1.3293 | | 6,000,000 | 15.9510 |
| 1,000,000 | 2.6585 | | 8,000,000 | 21.2681 |
| 1,500,000 | 3.9878 | | 10,000,000 | 26.5851 |
| 2,000,000 | 5.3170 | | 15,000,000 | 39.8776 |
| 3,000,000 | 7.9755 | | 20,000,000 | 53.1701 |
| 4,000,000 | 10.6340 | | | |

Base mismatch, disclosed and not corrected: Myanmar's schedule applies to chargeable income after the
basic, spouse and child allowances, while the engine applies the schedule to gross `self.income`.

## 7.5 Proposed `economic.TAX_BRACKETS` for `C`, two options, both labelled

**Option 1, recommended default: the 2012 twelve-band schedule as a dated proxy.** Conservative,
uses an actual documented schedule, and the bands that fall inside the engine's income range
(1.33x, 2.66x, 3.99x, 5.32x) genuinely bite across the distribution.

```python
    # PROXY, dated and labelled, 2026-10-29. The 2008 kyat slab thresholds of
    # the Income Tax Law 1974 COULD NOT BE SOURCED; see
    # config/constitution_2008_encoding/README.md section 7.3 for what was
    # attempted. What IS sourced for 2008: resident salary income was taxed
    # progressively at 3% to 30% (DFDL; FAO/Myanmar Investment Commission
    # guide s.6.4), with a basic allowance of 20% of income capped at
    # K 6,000. The bands below are the NEAREST DOCUMENTED FULL SCHEDULE,
    # MoFR Notification 107/2012 (15 Mar 2012, effective 1 Apr 2012), which
    # is FOUR YEARS AFTER year zero and follows a deliberate re-denomination,
    # converted to multiples of the IHLCA-II (2009/10) poverty line of
    # 376,151 kyat per adult equivalent per year. The real 2008 top rate was
    # 30%, not the 20% below, so this proxy UNDERSTATES the 2008 schedule's
    # progressivity at the top. Bands above about 5.6x are mechanically inert
    # in this engine (README section 7.2).
    TAX_BRACKETS: Tuple[Tuple, ...] = (
        (0.00,   1.33, 0.01),   # to 500,000 kyat
        (1.33,   2.66, 0.02),
        (2.66,   3.99, 0.03),
        (3.99,   5.32, 0.04),
        (5.32,   7.98, 0.05),
        (7.98,  10.63, 0.06),
        (10.63, 15.95, 0.07),
        (15.95, 21.27, 0.09),
        (21.27, 26.59, 0.11),
        (26.59, 39.88, 0.13),
        (39.88, 53.17, 0.15),
        (53.17, float("inf"), 0.20),   # above 20,000,000 kyat
    )
```

**Option 2: the sourced 2008 rate range encoded literally, accepting that unindexed thresholds had
collapsed.** Faithful to the one thing that IS sourced about 2008 (3 percent to 30 percent, with a
subsistence allowance capped at K 6,000 that was economically meaningless by 2008), and it needs no
2012 instrument at all. Its cost is that it rests on the inference in 7.3, and that given the engine's
sub-poverty-line guard it reduces in practice to a flat 30 percent tax on all income above the
poverty line.

```python
    TAX_BRACKETS: Tuple[Tuple, ...] = (
        (0.00, 1.00, 0.03),            # 3% entry rate, real; band suppressed
                                       # anyway by the engine's own
                                       # income <= poverty_line guard
        (1.00, float("inf"), 0.30),    # real pre-2012 maximum, reached at a
                                       # nominal income that unindexed 1974
                                       # thresholds had rendered trivial by 2008
    )
```

Measured effect, effective average tax rate at the engine's own income quantiles:

| income | 1.35x (p10) | 1.87x (p25) | 2.68x (p50) | 3.46x (p75) | 4.11x (p90) | 5.06x (p99) |
|---|---|---|---|---|---|---|
| current placeholder widths | 1.30% | 2.33% | 4.40% | 6.99% | 9.32% | 13.20% |
| Option 1 (2012 proxy) | 1.01% | 1.29% | 1.51% | 1.85% | 2.06% | 2.42% |
| Option 2 (flat 30% above the line) | 7.78% | 14.44% | 18.81% | 21.33% | 22.70% | 24.07% |

The two options bracket the placeholder in opposite directions, which is exactly why this needs
Kaung's decision rather than an agent's. **Either way Scenario C must be re-run, and because Scenario
C is already published, the manuscript's Gini column for C cannot be presented as continuous across
this change.** Flag to `senior-research-paper-writer` and `senior-data-analyst`.

## 7.6 Sourcing status

| Item | Status |
|---|---|
| Income Tax Law 1974 as the governing instrument in 2008 | **CONFIRMED** |
| Resident salary rate range 3 percent to 30 percent before 2012 | **CONFIRMED**, two independent sources |
| Allowance structure (20 percent capped at K 6,000; spouse K 2,500; children K 500 to 1,000) | **CONFIRMED** from the Myanmar Investment Commission / FAO guide |
| 2008 kyat slab thresholds | **COULD NOT ESTABLISH.** Seven routes attempted, listed in 7.3. MoFR Notification 121/2006 is the likely instrument and is not online |
| Notification 107/2012 twelve-band schedule | **CONFIRMED** as the post-reform schedule, used only as a dated proxy |
| IHLCA-I poverty line 162,136 kyat per adult equivalent per year (Nov 2004 prices) | **PRIMARY-SOURCE VERIFIED**, Tables 6.2 and 6.3 of the IHLCA technical report |
| IHLCA-II poverty line 376,151 kyat per adult equivalent per year (2009/10) | **SECONDARY-VERIFIED.** Needs one primary pull |
| "By 2008 the 1974 schedule was effectively a flat 30 percent on the formal-sector tax net" | **INFERENCE**, labelled. Derived from the sourced allowance magnitudes, not observed |
| Base mismatch (chargeable income after allowances versus gross income) | **DISCLOSED, NOT CORRECTED** |
