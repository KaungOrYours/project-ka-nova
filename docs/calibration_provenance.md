# Year-Zero Calibration Provenance, All Seven Constitutions

Prepared 2026-10-29 by `senior-researcher`, at the request of the parent agent, implementing the
recommendation carried in every encoding package's own flag list (South Korea package section 5 flag
F4, Thailand package section 5 flag F6: "Build the calibration table for all seven scenarios now").
This file is the single place where every `YEAR_ZERO_*` field on every constitution is traced to a
dataset, a version, a variable, an entity name, a year, a raw value, a transformation and an access
route.

Scope: one row per scenario per field. Seven scenarios times seven fields gives **49 rows**. Two of
those rows, Scenario A's coup risk and stability, document a field that the MFU constitution does not
define and that the engine fills in from Myanmar's literals; they are kept in the table rather than
omitted, because the inheritance is itself the finding (see note N1).

**Nothing in this file changes any encoded value.** It records what each value is traceable to and
what it is not. Where a value cannot be reproduced from the source its own code comment names, that
is stated as a finding, not softened.

Companion documents: `docs/manuscript_corrections_register.md` (not modified by this file) and the
per-country encoding packages at `config/constitution_<name>_encoding/README.md`.

---

## 0. Verdict legend

| Verdict | Meaning |
|---|---|
| **VERIFIED** | Reproducible to the stated precision from the named dataset, version, variable, entity and year. A third party with the access route can regenerate the number |
| **VERIFIED, RELEASE-SENSITIVE** | Reproducible from the dataset release the code comment used, but the current release of the same dataset gives a materially different raw value for the same variable, entity and year. See note N2 |
| **DERIVED, REPRODUCIBLE** | Not a dataset observation. A stated arithmetic computation over a named dataset, which reproduces |
| **DERIVED, DISCREPANT** | A stated computation over a named dataset, where the encoded value does not equal the result of that computation |
| **DOCUMENTED CHOICE** | Openly a modelling choice, with a real sourced range or rationale behind it, honestly labelled in the code |
| **NOT REPRODUCIBLE** | The code comment names a source, and the value cannot be obtained from that source for that entity and year under any documented transformation used elsewhere in this project. This is the corruption-field defect pattern repeating |
| **UNSOURCED PLACEHOLDER** | The code comment itself says the value is a guess and names no dataset. Honest, but must not appear in a manuscript table as sourced |
| **FIELD ABSENT, INHERITED** | The constitution module does not define the field; the engine silently substitutes another scenario's value. See note N1 |

---

## 1. Conventions that the table relies on

**C1, the WGI rescale.** Five of the seven constitutions convert a World Bank Worldwide Governance
Indicators point estimate, which runs on an approximately -2.5 to +2.5 scale, into Ka-Nova's [0, 1]
convention with the linear transform `(x + 2.5) / 5.0`. This transform is stated explicitly in the
code comments of `constitution_southkorea.py`, `constitution_thailand.py` and
`constitution_germany.py`. It is applied consistently in the table below wherever a WGI figure is
involved, including when testing values that do not reconcile.

**C2, V-Dem direction.** `v2x_corr`, the V-Dem political corruption index, runs 0 = clean to
1 = highly corrupt, the same direction as Ka-Nova's `corruption_index`, so no inversion is applied.

**C3, entity naming matters and is a real trap.** V-Dem treats **West Germany** as a distinct entity
for 1949 to 1990, separate from **Germany**. Using "Germany" for 1949 returns the wrong series.
Powell and Thyne's coup dataset spells South Korea as **South Korea**, not "Korea, South" or
"Korea, Rep.", and **does not contain Germany at all** (see note N4). World Bank API ISO3 codes are
MMR, KOR, THA, PAK, CHL, DEU. The "Entity name" column below gives the spelling each dataset
actually uses, not a normalised name.

**C4, Transparency International CPI is not used for any year-zero value and must not be.** The
original Scenario A and C corruption value of 0.72 was an inverted CPI score (28 of 100, the 2016,
2020 and 2021 figure), presented as a V-Dem baseline in one file and as "CPI 2023" in the other.
Both labels were wrong. CPI also does not exist before 1995, so it cannot serve year zero for
Myanmar 2008 is fine but is unavailable for South Korea 1988, Pakistan 1985, Chile 1990 or Germany
1949. CPI remains useful for backtesting trajectories, not for year-zero seeding.

**C5, brute-force matching is not provenance.** While verifying this table, the full Myanmar WGI
panel (6 indicators times 2 scale variants times 27 to 29 years) was scanned under four candidate
transformations for values rounding to 0.18, 0.22, 0.55, 0.58 and 0.68. Coincidental matches were
found in every case, on the wrong indicator, the wrong year, or both. **Those matches are recorded
nowhere in this table and must not be retrofitted as citations.** A search over roughly 2,000
candidate numbers will always hit a two-decimal target; hitting it is not evidence.

---

## 2. Master provenance table

Encoded values read directly from source on 2026-10-29. File and line references:
`config/constitution.py:1314-1318` (A), `config/constitution_2008.py:1071-1077` (C),
`config/constitution_southkorea.py:1479-1516` (SK), `config/constitution_thailand.py:1317-1349`
(TH), `config/constitution_pakistan.py:1340-1368` (PK), `config/constitution_chile.py:1388-1440`
(CL), `config/constitution_germany.py:1480-1521` (DE).

| Scenario | Field | Encoded | Dataset | Version | Variable | Entity (dataset spelling) | Year | Raw value | Transformation | Access route | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | `YEAR_ZERO_CORRUPTION` | 0.878 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | Myanmar | 2008 | 0.878 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED |
| C | `YEAR_ZERO_CORRUPTION` | 0.878 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | Myanmar | 2008 | 0.878 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED |
| SK | `YEAR_ZERO_CORRUPTION` | 0.458 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | South Korea | 1988 | 0.458 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED |
| TH | `YEAR_ZERO_CORRUPTION` | 0.683 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | Thailand | 2017 | 0.683 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED |
| PK | `YEAR_ZERO_CORRUPTION` | 0.637 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | Pakistan | 1985 | 0.637 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED |
| CL | `YEAR_ZERO_CORRUPTION` | 0.067 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | Chile | 1990 | 0.067 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED |
| DE | `YEAR_ZERO_CORRUPTION` | 0.020 | V-Dem | v16 (2026) | `v2x_corr` political corruption index | West Germany | 1949 | 0.020 | none, direction already matches (C2) | OWID grapher `political-corruption-index.csv`; cite V-Dem directly | VERIFIED (see N3) |
| A | `YEAR_ZERO_TRUST` | 0.22 | cited as "World Bank baseline", no dataset or variable named | n/a | none named | Myanmar | not stated | not found | none stated | n/a | **NOT REPRODUCIBLE**, see N5 |
| C | `YEAR_ZERO_TRUST` | 0.22 | cited as "World Bank Governance 2022" | n/a | none named | Myanmar | 2022 | not found | none stated | n/a | **NOT REPRODUCIBLE**, see N5 |
| SK | `YEAR_ZERO_TRUST` | 0.45 | V-Dem (used as a structural proxy, not a trust survey) | v16 (2026) | civil-liberties / polyarchy level 0.616 | South Korea | 1988 | 0.616 | undocumented rescale into the engine's trust range | OWID grapher CSVs | **UNSOURCED PLACEHOLDER**, self-labelled GUESS in code; the package's own L2 says "do not guess" |
| TH | `YEAR_ZERO_TRUST` | 0.29 | WGI 2023 Update (`wgidataset.xlsx`) | 2023 Update | Voice and Accountability, point estimate | Thailand | 2017 | -1.05 | `(-1.05 + 2.5) / 5 = 0.29` (C1) | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **VERIFIED, RELEASE-SENSITIVE**, see N2: current release gives -0.9032, which rescales to 0.32 |
| PK | `YEAR_ZERO_TRUST` | 0.25 | none; interpolated from V-Dem polyarchy 0.157 and liberal democracy 0.102 plus WGI 1996 PV -1.13 | n/a | several, no single variable | Pakistan | 1985 | n/a | undocumented interpolation | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, DERIVED NOT OBSERVED in code |
| CL | `YEAR_ZERO_TRUST` | 0.35 | none; CEP Encuesta Nacional named as the right source but no figure quoted | n/a | none | Chile | 1990 | not retrieved | none | registration required at cepchile.cl | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, package flag L6 |
| DE | `YEAR_ZERO_TRUST` | 0.55 | none; no trust survey reaches 1949 (ALLBUS from 1980, Politbarometer 1977, Eurobarometer 1974, EVS 1981) | n/a | none | West Germany | 1949 | does not exist | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, package flag L3 |
| A | `YEAR_ZERO_GINI` | 0.55 | cited as "World Bank baseline" | n/a | implied `SI.POV.GINI` | Myanmar | not stated | **30.7 for 2017, 38.1 for 2015** | none stated | World Bank API `SI.POV.GINI` | **NOT REPRODUCIBLE**, see N6 |
| C | `YEAR_ZERO_GINI` | 0.55 | cited as "World Bank 2017" | n/a | implied `SI.POV.GINI` | Myanmar | 2017 | **30.7** | none stated | World Bank API `SI.POV.GINI` | **NOT REPRODUCIBLE** and separately a unit mismatch, see N6 |
| SK | `YEAR_ZERO_GINI` | 0.39 | none; Korean income-distribution literature range 0.34 to 0.39 cited without a specific source | n/a | none | Korea, Rep. | 1988 | World Bank series begins 2006 | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS; no World Bank observation exists for 1988 |
| TH | `YEAR_ZERO_GINI` | 0.35 | World Bank PIP / WDI | PIP, accessed 2026-10-29 | `SI.POV.GINI` | Thailand | 2017 | **36.4** | divide by 100 gives 0.364 | World Bank API `SI.POV.GINI` | **NOW VERIFIABLE**, encoded 0.35 against a real 0.364, see N7 |
| PK | `YEAR_ZERO_GINI` | 0.33 | World Bank PIP / WDI | PIP, accessed 2026-10-29 | `SI.POV.GINI` | Pakistan | 1987 (nearest to 1985) | **33.3** | divide by 100 gives 0.333 | World Bank API `SI.POV.GINI` | **NOW VERIFIABLE**, encoded 0.33 matches the real 1987 observation to two decimals, see N7 |
| CL | `YEAR_ZERO_GINI` | 0.56 | World Bank PIP / WDI | PIP, accessed 2026-10-29 | `SI.POV.GINI` | Chile | 1990 | **57.2** | divide by 100 gives 0.572 | World Bank API `SI.POV.GINI` | **NOW VERIFIABLE**, encoded 0.56 against a real 0.572 at exactly year zero, see N7 |
| DE | `YEAR_ZERO_GINI` | 0.33 | none; code comment explicitly states this is NOT a 1949 figure | n/a | `SI.POV.GINI` has no pre-1991 German observation | Germany | 1949 | does not exist (series begins 1991 at 29.3) | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS; note 0.33 is closest to Germany 2021 (33.6), a modern figure |
| A | `YEAR_ZERO_EMPLOYMENT` | 0.58 | no citation at all in the code | n/a | none | Myanmar | not stated | n/a | none | n/a | **NOT REPRODUCIBLE**, no source named |
| C | `YEAR_ZERO_EMPLOYMENT` | 0.58 | cited as "Myanmar Census 2014" | n/a | none named | Myanmar | 2014 | **World Bank employment-to-population ratio 2014 = 64.3; labour force participation 2014 = 64.8** | none stated | World Bank API `SL.EMP.TOTL.SP.ZS`, `SL.TLF.CACT.ZS` | **NOT REPRODUCIBLE**, see N8 |
| SK | `YEAR_ZERO_EMPLOYMENT` | 0.68 | none | n/a | none | Korea, Rep. | 1988 | modelled ILO series begins 1991 | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS |
| TH | `YEAR_ZERO_EMPLOYMENT` | 0.95 | none; code comment reasons from Thailand's famously low unemployment rate | n/a | none | Thailand | 2017 | not retrieved | inverse framing of an unemployment rate | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS/external |
| PK | `YEAR_ZERO_EMPLOYMENT` | 0.58 | none; code comment says "reused convention", that is Myanmar's own value | n/a | none | Pakistan | 1985 | not retrieved | none | n/a | **UNSOURCED PLACEHOLDER**, and it is Myanmar's number carried across, see N9 |
| CL | `YEAR_ZERO_EMPLOYMENT` | 0.60 | none | n/a | none | Chile | 1990 | not retrieved | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS |
| DE | `YEAR_ZERO_EMPLOYMENT` | 0.90 | none; code comment reasons from commonly cited 10 to 11 percent West German unemployment circa 1950 | n/a | none | West Germany | 1949 | not retrieved | `1 - 0.10`, implied | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, direction defensible |
| A | `YEAR_ZERO_ETHNIC_TENSION` | 0.68 | no citation at all in the code | n/a | none | Myanmar | not stated | n/a | none | n/a | **NOT REPRODUCIBLE**, no source named |
| C | `YEAR_ZERO_ETHNIC_TENSION` | 0.68 | cited as "V-Dem Dataset", with no variable, no year and no entity | n/a | **none named** | Myanmar | not stated | not identifiable | none stated | n/a | **NOT REPRODUCIBLE AS CITED**, see N10 |
| SK | `YEAR_ZERO_ETHNIC_TENSION` | 0.0 | constitutional structure, not a dataset | n/a | n/a | South Korea | 1988 | n/a | set to zero because the 1987 Constitution recognises no ethnic-group structure | encoding package section 1 | **DOCUMENTED CHOICE**, structurally correct and inert by construction |
| TH | `YEAR_ZERO_ETHNIC_TENSION` | 0.10 | constitutional structure, not a dataset | n/a | n/a | Thailand | 2017 | n/a | set low because the 2017 Constitution recognises no ethnic-group structure | encoding package section 1 | **DOCUMENTED CHOICE**, direction confident, magnitude a guess |
| PK | `YEAR_ZERO_ETHNIC_TENSION` | 0.45 | none | n/a | none | Pakistan | 1985 | not retrieved | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, package limitation L8 |
| CL | `YEAR_ZERO_ETHNIC_TENSION` | 0.20 | none | n/a | none | Chile | 1990 | not retrieved | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, package limitation L8 |
| DE | `YEAR_ZERO_ETHNIC_TENSION` | 0.05 | none | n/a | none | West Germany | 1949 | not retrieved | none | n/a | **UNSOURCED PLACEHOLDER**, self-labelled GUESS/inert |
| A | `YEAR_ZERO_COUP_RISK` | **0.25 (not its own)** | none; the field does not exist on the MFU constitution | n/a | n/a | n/a | n/a | n/a | `getattr(sim, "YEAR_ZERO_COUP_RISK", 0.25)` at `model_phase3.py:399` substitutes Myanmar's literal | `model_phase3.py:399` | **FIELD ABSENT, INHERITED**, see N1 |
| C | `YEAR_ZERO_COUP_RISK` | 0.25 | cited as "Post-2021 estimate", naming no dataset, no year and no method | V2026.08.29 was checked | `coup` outcome code | Myanmar | 1948 to 2026 | **4 successful coups (1958, 1962, 1988, 2021) plus 1 failed (1976)** | any base-rate convention over these events gives 0.05 to 0.07, not 0.25 | `https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` | **NOT REPRODUCIBLE**, see N11 and section 3 |
| SK | `YEAR_ZERO_COUP_RISK` | 0.02 | Powell and Thyne, Coups d'etat 1950-present | V2026.08.29 | `coup` outcome code | South Korea | 1950 to 2026 | **1 successful coup, 1961-05; zero events since** | package's recommended range 0.00 to 0.02, upper bound deliberately used to avoid the withdrawn "zero coups" framing | `https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` | **DOCUMENTED CHOICE** within a sourced range |
| TH | `YEAR_ZERO_COUP_RISK` | 0.12 | Powell and Thyne, Coups d'etat 1950-present | V2026.08.29 | `coup` outcome code | Thailand | 1951 to 2014 | **8 successful, 4 failed, 12 events total** | `8 / 64 years = 0.125`, rounded to 0.12 | `https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` | **DERIVED, REPRODUCIBLE**, recomputed from the dataset and matches |
| PK | `YEAR_ZERO_COUP_RISK` | 0.086 | Powell and Thyne, Coups d'etat 1950-present | V2026.08.29 | `coup` outcome code | Pakistan | 1950 to 1985 | **3 successful by 1985 (1958, 1971, 1977); 4 total in the full series, 0 failed** | `3 / 35 years = 0.0857`, rounded to 0.086 | `https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` | **DERIVED, REPRODUCIBLE**, recomputed from the dataset and matches |
| CL | `YEAR_ZERO_COUP_RISK` | 0.05 | Powell and Thyne, Coups d'etat 1950-present | V2026.08.29 | `coup` outcome code | Chile | 1950 to 1990 | **1 successful (1973-09) and 1 failed (1973-06), both predating the 1980 Constitution** | code's own stated computation is 0.025 to 0.032; the encoded value is 0.05 | `https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` | **DERIVED, DISCREPANT**, see N12 |
| DE | `YEAR_ZERO_COUP_RISK` | 0.00 | Powell and Thyne, Coups d'etat 1950-present | V2026.08.29 | `coup` outcome code | **Germany does not appear in the dataset** | 1950 to 2026 | no coded events | zero | `https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` | **DERIVED, REPRODUCIBLE** with a wording correction, see N4 |
| A | `YEAR_ZERO_STABILITY` | **0.18 (not its own)** | none; the field does not exist on the MFU constitution | n/a | n/a | n/a | n/a | n/a | `getattr(sim, "YEAR_ZERO_STABILITY", 0.18)` at `model_phase3.py:400` substitutes Myanmar's literal | `model_phase3.py:400` | **FIELD ABSENT, INHERITED**, see N1 |
| C | `YEAR_ZERO_STABILITY` | 0.18 | cited as "World Bank Political Stability 2022" | WGI 2023 Update (`wgidataset.xlsx`) and current release both checked | Political Stability and Absence of Violence, point estimate | Myanmar | 2022 | **-2.2320** (current release); percentile rank about 2.8 | `(-2.2320 + 2.5) / 5 = 0.054`; score/100 gives 0.265; percentile rank/100 gives 0.028 | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **NOT REPRODUCIBLE**, see N13 and section 3 |
| SK | `YEAR_ZERO_STABILITY` | 0.61 | WGI 2023 Update (`wgidataset.xlsx`) | 2023 Update | Political Stability, point estimate | Korea, Rep. | 1996 (8 years after year zero; WGI does not cover 1988) | 0.57 | `(0.57 + 2.5) / 5 = 0.614`, rounded to 0.61 (C1) | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **VERIFIED, RELEASE-SENSITIVE**, see N2: current release gives 0.6700, which rescales to 0.63 |
| TH | `YEAR_ZERO_STABILITY` | 0.35 | WGI 2023 Update (`wgidataset.xlsx`) | 2023 Update | Political Stability, point estimate | Thailand | 2017 | -0.75 | `(-0.75 + 2.5) / 5 = 0.35` (C1) | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **VERIFIED, RELEASE-SENSITIVE**, see N2: current release gives -0.9841, which rescales to 0.30 |
| PK | `YEAR_ZERO_STABILITY` | 0.20 | WGI 2023 Update (`wgidataset.xlsx`) named but not applied | 2023 Update | Political Stability, point estimate | Pakistan | 1996 (11 years after year zero) | -1.13 as quoted in code; current release gives -1.4335 | `(-1.13 + 2.5) / 5 = 0.274`, which is **not** 0.20 | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **UNSOURCED PLACEHOLDER**, self-labelled GUESS DERIVED NOT OBSERVED; the rescale of the current release (0.21) is a numerical coincidence, see C5 |
| CL | `YEAR_ZERO_STABILITY` | 0.40 | WGI 2023 Update (`wgidataset.xlsx`) named but explicitly not applied | 2023 Update | Political Stability, point estimate | Chile | 1996 (6 years after year zero) | 0.68 as quoted in code; current release gives 0.6857 | `(0.68 + 2.5) / 5 = 0.636`, which is **not** 0.40; the code says so and declines to substitute | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **UNSOURCED PLACEHOLDER**, self-labelled GUESS, package flag L7, honestly declared |
| DE | `YEAR_ZERO_STABILITY` | 0.75 | WGI 2023 Update (`wgidataset.xlsx`) | 2023 Update | Political Stability, point estimate | Germany | 1996 (47 years after year zero) | 1.29 | `(1.29 + 2.5) / 5 = 0.758`, rounded to 0.75 (C1) | www.govindicators.org; current release also at World Bank API `source=3`, indicator `GOV_WGI_PV.EST` | **VERIFIED, RELEASE-SENSITIVE**, see N2: current release gives 1.3035, which rescales to 0.76 |

Row count check: 49 rows, 7 scenarios times 7 fields, of which 2 (Scenario A's coup risk and
stability) record an absent-and-inherited field rather than an encoded value.

---

## 3. Notes

**N1, the MFU constitution is missing two of the seven fields, and silently inherits Myanmar's.**
`config/constitution.py`'s `SimulationConfig` defines only five `YEAR_ZERO_*` fields: CORRUPTION,
TRUST, GINI, EMPLOYMENT and ETHNIC_TENSION. It has no `YEAR_ZERO_COUP_RISK` and no
`YEAR_ZERO_STABILITY`. All six other constitutions define all seven.
`model_phase3.py:399-400` resolves the gap with
`getattr(sim, "YEAR_ZERO_COUP_RISK", 0.25)` and `getattr(sim, "YEAR_ZERO_STABILITY", 0.18)`, and
those two literals are **Myanmar's own numbers**, lifted from `constitution_2008.py:1076-1077`. The
code's own docstring describes this as "a no-op for Scenario A specifically", which is true of the
numeric result but misleading about its provenance: it means **Scenario A and Scenario C start from
identical year-zero coup risk and identical year-zero stability, and neither value is an MFU value.**
For a paper whose central question is whether divergence is structural or parameter-driven, two of
the seven year-zero conditions being shared by construction is a disclosable fact.
Also note: `.claude/memory.md` section 19 records the pre-deployment sweep as finding "zero gaps
across all 7 on ... `YEAR_ZERO_*`". That is true at the level of "the engine reads a value for every
scenario" and false at the level of "every scenario defines its own value". The memory wording should
be tightened.
Recommended fix, for `senior-simulation-engineer` and Kaung, not applied here: give
`config/constitution.py` its own two fields with MFU-specific documented values, and change the two
`getattr` calls to plain attribute reads so a future missing field fails loudly instead of
inheriting Myanmar's.

**N2, WGI point estimates are re-estimated with every release, so the release must be pinned.**
The WGI programme re-runs its unobserved-components model over the whole panel at each update, so the
same indicator, entity and year changes value between releases. Measured directly, Political
Stability point estimates, 2023 Update figure as quoted in the encoding comments versus the current
release pulled from the World Bank API on 2026-10-29:

| Entity | Year | As quoted in code (WGI 2023 Update) | Current release | Rescaled, code | Rescaled, current |
|---|---|---|---|---|---|
| Korea, Rep. | 1996 | 0.57 | **0.6700** | 0.61 | 0.63 |
| Thailand | 2017 | -0.75 | **-0.9841** | 0.35 | 0.30 |
| Pakistan | 1996 | -1.13 | **-1.4335** | 0.27 | 0.21 |
| Chile | 1996 | 0.68 | **0.6857** | 0.64 | 0.64 |
| Germany | 1996 | 1.29 | **1.3035** | 0.76 | 0.76 |
| Thailand (Voice and Accountability) | 2017 | -1.05 | **-0.9032** | 0.29 | 0.32 |

Thailand's stability value moves by 0.05 and its trust value by 0.03 purely from the release change.
**Consequence for the reproducibility package: every WGI-derived value must carry its release name,
and the reproducibility package should ship the WGI file it used rather than a download instruction.**
Flag to `senior-data-analyst` and `senior-devops-engineer`.

**N3, V-Dem entity naming for Germany.** `DE`'s year-zero corruption of 0.020 is correct **only**
against V-Dem's **West Germany** entity. V-Dem maintains West Germany as a separate unit for 1949 to
1990. Querying "Germany" for 1949 returns a different series. Any regeneration script must select the
West Germany entity by name, and the reproducibility package should state this, because the error is
silent.

**N4, Powell and Thyne does not contain Germany, which is not the same as recording zero.**
`config/constitution_germany.py:1509-1514` says "Powell-Thyne records zero German coup events
1950-2026". Verified directly against `pt_20260829.csv`: the dataset contains **no country row whose
name contains "German" at all**. Powell and Thyne code only country-years with at least one coded
event, so absence from the file is the dataset's way of representing zero, and the encoded 0.00 is
correct. But the wording should be precise, because "the dataset records zero events for Germany"
implies a Germany row exists. Suggested replacement wording: "Germany does not appear in
Powell and Thyne V2026.08.29, which lists only states with at least one coded coup event; the
resulting base rate is therefore zero." Same file also correctly declines to use the pre-1949 German
putsch history as a prior, which is the right call for an instrument encoded from 1949.
Separately, the dataset spells South Korea as **South Korea**; it has no "Korea, South" or
"Korea, Rep." row. Pinned spelling matters for any regeneration script.

**N5, `YEAR_ZERO_TRUST = 0.22` for A and C is not reproducible from "World Bank Governance 2022".**
Tested: under the project's own `(x + 2.5) / 5` convention (C1), Myanmar 2022 gives Voice and
Accountability 0.119, Political Stability 0.054 and Control of Corruption about 0.08. None rounds to
0.22. Under score/100 the 2022 values are 0.265 (PV) and lower elsewhere. The closest value anywhere
in the Myanmar WGI panel at 0.22 under any transform is Government Effectiveness for 1996 to 2000,
which is neither trust, nor 2022, nor a defensible derivation (C5). **The citation does not support
the number.** Note that this is the same field pair, A and C, that carried the 0.72 corruption
defect, and the same pattern: a real institution named, a real-sounding year attached, and no
retrievable observation behind it.

**N6, `YEAR_ZERO_GINI = 0.55` for A and C has two independent defects, not one.**
Defect one, already documented in `analysis/kpi.py:98-112` and `.claude/memory.md` bug #2: the
simulated Gini is dispersion of GDP across administrative units, not household income, so a household
income Gini is an incommensurable validation target. Defect two, new in this pass: **0.55 is not the
World Bank figure either.** World Bank `SI.POV.GINI` for Myanmar has exactly two observations,
**2015 = 38.1 and 2017 = 30.7**. The cited "World Bank 2017" value is 0.307, not 0.55. So the field
is wrong in measure and wrong in value. Resolving the measure question (source a subnational
GDP-dispersion benchmark, or report with no external target) does not fix the value question, and
vice versa. Both need to go to `senior-data-analyst`.

**N7, three Gini values are now verifiable and were previously flagged as unsourced.** Retrieved
2026-10-29 from World Bank API `SI.POV.GINI`:

| Scenario | Entity | Year | Real observation | Encoded | Delta |
|---|---|---|---|---|---|
| TH | Thailand | 2017, exactly year zero | **36.4** | 0.35 | 0.014 |
| PK | Pakistan | 1987, nearest to year zero 1985 | **33.3** | 0.33 | 0.003 |
| CL | Chile | 1990, exactly year zero | **57.2** | 0.56 | 0.012 |

All three code comments explicitly asked for exactly this verification
(`constitution_chile.py`: "verify the exact survey year before using"; `constitution_pakistan.py`:
"flagged for senior-data-analyst to source the exact HIES-1987 value"). **The verification is now
done and the real values are above.** Upgrading 0.35 to 0.364, 0.33 to 0.333 and 0.56 to 0.572 would
turn three UNSOURCED PLACEHOLDER rows into three VERIFIED rows at the cost of re-running TH, PK and
CL. That is an encoding decision, not a research one, so it is reported rather than applied. Note
the unit mismatch in N6 applies to these three as well: they are household-income Ginis being used to
seed a state-GDP dispersion metric. Correct values for the wrong measure is still only half a fix.

**N8, `YEAR_ZERO_EMPLOYMENT = 0.58` for C is not reproducible from "Myanmar Census 2014".**
World Bank modelled-ILO series for Myanmar 2014: employment-to-population ratio **64.3 percent**,
labour force participation rate **64.8 percent**. The 2014 Myanmar Population and Housing Census
itself reported a labour force participation rate near 67 percent for ages 15 to 64. None of these is
0.58. The nearest the employment-to-population series comes to 58 is 2020 (59.3) and 2021 (52.8),
both well after 2014 and both the wrong year for this scenario. **The citation does not support the
number.**

**N9, Pakistan's employment value is Myanmar's value.** `constitution_pakistan.py:1357` sets
`YEAR_ZERO_EMPLOYMENT = 0.58` with the comment "reused convention, not covered by the research
package". 0.58 is the Myanmar literal from `constitution_2008.py:1074`. This is the same
cross-contamination pattern as N1, carried by hand rather than by `getattr`. It should be either
sourced for Pakistan 1985 or disclosed as an intentionally shared parameter.

**N10, `YEAR_ZERO_ETHNIC_TENSION = 0.68` cites "V-Dem Dataset" with no variable.** V-Dem has several
candidate indices in this space (`v2clsocgrp`, `v2peapsecon`, `v2csgender`, the exclusion-by-social-
group family), and no variable name, year or entity is given, so the value is not checkable even in
principle. This field is the single least traceable entry in the table. It is also now a live
published column for all seven scenarios after bug #22 unfroze `ethnic_harmony`, and
`.claude/memory.md` section 35 already flags that every scenario's citizen ethnicity is Myanmar's. So
this row sits at the intersection of two known problems and should not appear in any cross-scenario
claim until both are resolved.

**N11 and N13 are the subject of section 4 below.**

**N12, Chile's coup-risk value exceeds its own stated computation.** `constitution_chile.py:1419-1431`
states the derivation as "1 success + 1 failure in 1950-1981 ... about 0.025 to 0.032/yr depending on
exact denominator" and then encodes 0.05, roughly 1.6 to 2.0 times that. Recomputed from
Powell and Thyne V2026.08.29: Chile has exactly two coded events, both in 1973, one failed in June and
one successful in September, and both predate the 1980 Constitution entirely. Over 1950 to 1990 the
successful-coup rate is `1 / 41 = 0.024`. The code is honest that the magnitude is a judgement call
("CONFIDENT direction, GUESS exact magnitude"), so this is a labelling question rather than a hidden
error: either encode 0.024 and call it derived, or keep 0.05 and call it a modelling floor, but do not
present 0.05 as the Powell and Thyne rate.

---

## 4. The two Scenario C fields that do not reconcile

This section answers the specific question put to this task: determine what
`config/constitution_2008.py`'s `YEAR_ZERO_STABILITY = 0.18` and `YEAR_ZERO_COUP_RISK = 0.25`
actually correspond to, and give each the same three-way verdict the corruption field received.
**No value is changed by this document.**

### 4.1 `YEAR_ZERO_STABILITY = 0.18`, cited "World Bank Political Stability 2022"

**Verdict: (c), it is a modelling calibration choice, and the citation is wrong on both the year and
the arithmetic.** Not (a), because the citation cannot be made to yield 0.18 by any documented route.
Not (b) in the strict sense, because there is no single "real" value to replace it with: the correct
replacement depends on which year the scenario intends.

Evidence, all recomputed on 2026-10-29 from the World Bank API, WGI source, indicator
`GOV_WGI_PV.EST` and `GOV_WGI_PV.SC`, entity Myanmar:

| Candidate reading of the citation | Raw value | Transformed | Equals 0.18? |
|---|---|---|---|
| 2022 point estimate, project's own `(x+2.5)/5` rescale (C1) | -2.2320 | **0.054** | No |
| 2022 rescaled governance score, /100 | 26.4974 | **0.265** | No |
| 2022 percentile rank, /100 | about 2.8 | **0.028** | No |
| **2008, the file's own year zero**, `(x+2.5)/5` | -1.1505 | **0.270** | No |
| 2008 governance score /100 | 45.4478 | **0.454** | No |
| Any year 1996 to 2025, `(x+2.5)/5` | min -2.2320, max -0.8230 | range **0.054 to 0.336** | **0.18 requires an estimate of exactly -1.60, which Myanmar's PV series never takes.** Nearest are 1996 at -1.5352 (0.193) and 2000 at -1.6874 (0.163) |

So 0.18 is not any Myanmar Political Stability observation under any transform used anywhere in this
project, and in particular it is roughly **a third** of the value the file's own year zero (2008)
would give, and roughly **three times** the value its stated year (2022) would give. The number sits
between Myanmar's 1996 and 2000 readings, a period this scenario does not model.

**Honest wording for the code, proposed and not applied:**

> `YEAR_ZERO_STABILITY: float = 0.18`
> MODELLING CALIBRATION CHOICE, not a dataset observation. The previous citation,
> "World Bank Political Stability 2022", does not reconcile: WGI's Myanmar Political Stability and
> Absence of Violence point estimate for 2022 is -2.232, which rescales to 0.054 under this project's
> own `(x + 2.5) / 5` convention, and the percentile rank of about 2.8 gives 0.028. The file's own
> year zero, 2008, gives -1.1505, which rescales to 0.270. 0.18 corresponds to a point estimate of
> about -1.60, which Myanmar's series never takes in any year from 1996 to 2025. The value is
> retained because Scenario C's published results were generated with it; it is relabelled rather
> than changed. If a sourced value is wanted, the defensible one is **0.270**, WGI Political
> Stability, Myanmar, 2008, WGI 2025 release, rescaled per C1, and changing to it would move every
> published Scenario C stability number.

**What changes if the value is corrected.** `stability_index` is a live published KPI
(`analysis/kpi.py:89` KPI_COLUMNS, `charts/visualize.py` in four panels) and it is written every
year by `feedback/loops.py:191` as
`legitimacy*0.50 + (1 - coup_risk)*0.30 + rights_bonus`, so year zero is a seed rather than a
constant. It also feeds three internal-consistency checks at `analysis/kpi.py:935-940`. Changing the
seed from 0.18 to 0.270 would move Scenario C's whole stability trajectory and the reported A-versus-C
stability effect size (d = 91.6), which `feedback/loops.py:178-186` already discloses is partly a
flat deterministic `STABILITY_RIGHTS_BONUS` term. **This is a published-number change and needs
Kaung's decision.**

**A second, separate instance of the same defect, found while verifying this one.**
`analysis/kpi.py:115` carries `"stability_index": 0.18, # World Bank political stability 2022` in
`MYANMAR_BASELINES`, and `analysis/kpi.py:683` repeats the same string as the reviewer-facing
validation source label. So the unreconcilable citation appears **twice**, once as a constitutional
parameter and once as a published calibration target. Both need the same treatment.

**A third instance, and this one is a live inconsistency rather than just a bad label.**
`analysis/kpi.py:99` still carries `"corruption_index": 0.72, # Transparency International CPI 2023`
in `MYANMAR_BASELINES`. That is exactly the value and exactly the citation that was already corrected
to **0.878 (V-Dem v16, Myanmar 2008)** in `config/constitution_2008.py:1071` and
`config/constitution.py:1314`. **The correction was applied to the constitution files and not to the
KPI calibration baseline.** The result is that the engine now seeds Scenario C's corruption at 0.878
while the calibration-validation table it is scored against still targets 0.72, a 0.158 gap that will
appear in `results/calibration_validation.csv` as a spurious calibration error. Also note
`analysis/kpi.py:120`, `"coup_probability": 0.45, # Estimated post-2021`, which is a third different
unsourced "post-2021" number alongside the 0.25 in section 4.2. Route all of this to
`senior-data-analyst` as a single coherent piece of work; it is a reproducibility-package blocker, not
a cosmetic one.

### 4.2 `YEAR_ZERO_COUP_RISK = 0.25`, cited "Post-2021 estimate"

**Verdict: (c), it is a modelling calibration choice, and it is inconsistent with the convention
every other scenario in the project uses.** Not (a): "Post-2021 estimate" names no dataset, no
variable, no year and no method, so there is no citation to repair. Not (b) in the sense of a simple
substitution, because the real question is whether Scenario C should use the same base-rate
convention as the other six.

Evidence, recomputed on 2026-10-29 from Powell and Thyne V2026.08.29. Myanmar has five coded events:
1958-09 successful, 1962-03 successful, 1976-07 failed, 1988-09 successful, 2021-02 successful.

| Base-rate convention | Computation | Result |
|---|---|---|
| Successful coups over independence to present | 4 / 78 years (1948 to 2026) | **0.051** |
| Successful coups to the 2021 coup | 4 / 74 years (1948 to 2022) | **0.054** |
| All coded events over independence to present | 5 / 78 years | **0.064** |
| Successful coups up to year zero | 3 / 60 years (1948 to 2008) | **0.050** |
| Under this instrument only | 1 / 18 years (2008 to 2026) | **0.056** |
| **Encoded value** | | **0.25** |

Every convention gives 0.05 to 0.07. The encoded value is **four to five times** the base rate, and
the gap is not explained anywhere in the file.

This matters because the **same Powell and Thyne convention is what the other six scenarios use, and
they use it correctly**: Thailand 0.12 from 8/64, Pakistan 0.086 from 3/35, South Korea 0.02 from a
stated 0.00-to-0.02 range, Chile 0.05 against a stated 0.024-to-0.032 (see N12), Germany 0.00 from
absence. So the cross-scenario picture is that **Myanmar, the designated failure case, is the one
scenario whose coup-risk seed is not derived from the shared convention, and it is set roughly 2x
above the most coup-prone scenario in the set (Thailand at 0.12) despite having a lower real base
rate than Thailand.** An adversarial reviewer asking "is the divergence structural or
parameter-driven" has a clean target here.

It is also load-bearing in a way the stability field is not. `shared_data["coup_risk"]` is read at
`model_phase3.py:103, 539-544, 598, 724, 815` and at `feedback/loops.py:188`; it drives the coup
check in `_military_chain_rules`, and Scenario C's 100 percent failure rate at mean year
16.6 plus or minus 0.96 is the paper's headline finding. **And Scenario A inherits the same 0.25 via
the `getattr` default described in N1**, so the value is not even specific to Scenario C.

**Honest wording for the code, proposed and not applied:**

> `YEAR_ZERO_COUP_RISK: float = 0.25`
> MODELLING CALIBRATION CHOICE, not an estimate from any dataset. The previous label,
> "Post-2021 estimate", named no source. For reference, the convention used by the other six
> scenarios, successful coups per year from Powell and Thyne V2026.08.29, gives Myanmar
> **0.050 to 0.064** depending on the window (4 successful coups in 1958, 1962, 1988 and 2021 over
> 74 to 78 years). 0.25 is deliberately far above that, representing the 2008 Constitution's
> structurally ever-present coup capability (ss. 20(f), 40(c), 417 to 419) rather than a historical
> frequency. This is a design decision about what the seed represents and it should be stated in the
> methodology, because it is not commensurable with the other six scenarios' historically derived
> seeds. The value is retained because Scenario C's published results, including the mean collapse
> year of 16.6, were generated with it.

**Recommendation on which way to resolve it.** Do **not** quietly change 0.25 to 0.054 to make the
convention uniform. Scenario C's collapse-year result is published, and the adversarial exposure
audit in `.claude/memory.md` section 5c already identifies "mechanically induced by thresholds,
parameter bounds, or deterministic relationships" as Reviewer 1's live objection. The defensible move
is the one the project already took for trust: **disclose the mechanism openly**, state that
Scenario C's coup-risk seed is a structural design parameter rather than a historical rate, state the
historical rate alongside it, and let the Sobol GSA show how sensitive the collapse year is to it.
If the GSA has not yet perturbed `coup_risk`, it should: that single number is the clearest candidate
for "the result is parameter-driven" in the whole model.

---

## 5. Summary of findings, by severity

**Blocking the reproducibility package:**
1. `analysis/kpi.py:99` still targets corruption 0.72 cited to CPI 2023, while the constitutions now
   seed 0.878 cited to V-Dem v16. The correction was half-applied. (Section 4.1)
2. `YEAR_ZERO_STABILITY = 0.18` and `YEAR_ZERO_COUP_RISK = 0.25` carry citations that do not
   reconcile, and 0.18 is duplicated in `analysis/kpi.py:115` and `:683`. (Section 4)
3. WGI-derived values do not pin a release, and the release materially changes them. (N2)

**Provenance defects that a reviewer can find:**
4. `YEAR_ZERO_TRUST = 0.22` (A and C) not reproducible from "World Bank Governance 2022". (N5)
5. `YEAR_ZERO_GINI = 0.55` (A and C) not reproducible from "World Bank 2017", which is 30.7, on top
   of the already-documented unit mismatch. (N6)
6. `YEAR_ZERO_EMPLOYMENT = 0.58` (C) not reproducible from "Myanmar Census 2014", which gives about
   64. (N8)
7. `YEAR_ZERO_ETHNIC_TENSION = 0.68` (A and C) cites "V-Dem Dataset" with no variable, year or
   entity, so it is uncheckable in principle. (N10)
8. MFU defines only five of the seven fields and silently inherits Myanmar's coup risk and
   stability, so A and C share two year-zero conditions by construction. (N1)
9. Pakistan's employment value is Myanmar's value, carried by hand. (N9)
10. Chile's coup-risk value is about twice its own stated derivation. (N12)

**Free upgrades available:**
11. Three Gini values are now verifiable against World Bank `SI.POV.GINI`: Thailand 2017 = 36.4,
    Pakistan 1987 = 33.3, Chile 1990 = 57.2. Three UNSOURCED PLACEHOLDER rows can become VERIFIED
    rows. (N7)

**Wording precision:**
12. Germany's coup-risk comment implies a Powell and Thyne Germany row that does not exist. (N4)
13. `.claude/memory.md` section 19's "zero gaps across all 7 on `YEAR_ZERO_*`" is true of engine
    reads and false of per-scenario definitions. (N1)

---

## 6. What this document does not cover

- **Fields with no `YEAR_ZERO_*` counterpart anywhere.** `model_phase3.py:390-404` seeds
  `grievance_index` 0.60, `ethnic_harmony` 0.35, `iig_effectiveness` 0.30, `brain_drain_rate` 0.35,
  `north_star_progress` 0.0 and others from bare literals for every scenario, with no constitutional
  field to read. Those are outside this table's scope by its own definition, but they are the same
  class of problem and `ethnic_harmony` in particular is a live published column.
- **`gdp_growth` and `resource_revenue` per-state ranges**, which `_initialize_states()` leaves as
  literals because no encoded value exists.
- **The economic parameters**, including `TAX_BRACKETS`, which are covered in section 7 of each
  encoding package rather than here.
- **Whether any of these values should change.** This document establishes traceability. Every
  value-change decision is Kaung's, and each one listed in section 5 moves published numbers.
