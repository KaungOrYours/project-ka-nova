# South Korea 1987 Constitution — Encoding Research Package

Researcher's workspace document (not code). Prepared by `senior-researcher`, 2026-10-20.
Target output: `config/constitution_southkorea.py` → registry key `SK`, `chain_type: "civilian"`.

Schema to mirror: `config/constitution_2008.py` (21 dataclasses). Because South Korea is a
civilian-supremacy case, the **field-name set to copy is `config/constitution.py` (MFU)**, not the
2008 file — see "Schema warning" at the bottom of this document.

---

## 0. Instrument definition (lock this before encoding)

| Item | Value | Source |
|---|---|---|
| Instrument | Constitution of the Republic of Korea, 1948, as wholly revised by the Ninth Amendment of 1987 | Constitute Project, "Korea (Republic of) 1948 (rev. 1987)" |
| Referendum | 28 October 1987 — 18,640,625 for (94.46%) / 1,092,702 against (5.54%); turnout 78.18% (20,028,672 of 25,619,648 registered) | Wikipedia, "1987 South Korean constitutional referendum" (figures are the officially reported NEC results; see §4 limitation L1) |
| Entry into force | 25 February 1988 | Widely documented; this is the date the Sixth Republic began |
| Amendments since | **Zero.** The 1987 text has never been amended. | No amendment has been promulgated since 1988 |
| Simulation year-zero | **1988** (recommend) | Constitution operative date |
| Real observation window | 1988–2026 = 38 years of the 50-year horizon | — |

Recommended label string for `SimulationConfig.CONSTITUTIONAL_FRAMEWORK`:
`"1987_republic_of_korea_constitution_sixth_republic"`.

---

## 1. Real constitutional structure, mapped to the config schema

All article numbers below are verbatim from the Constitute Project rendering of
`Korea (Republic of) 1948 (rev. 1987)`
(https://www.constituteproject.org/constitution/Republic_of_Korea_1987), cross-read against the
2024 martial-law literature cited in §2.4.

### FoundationalConfig
- Unitary state with constitutional local autonomy (Art. 117–118). **Not federal.** `STATE_COUNT`
  has no constitutional basis — Korea's 17 first-level administrative divisions are statutory.
  Encoding note: use `STATE_COUNT: 17` as a *modelling* choice (9 provinces + 8 metropolitan-level
  cities as of 2012 onward) and say so in a comment, or keep 14 for cross-scenario comparability.
  This is an inference, not a constitutional number — flag in code.
- No constitutionally recognised ethnic-group structure. Korea is the one scenario where the
  MFU/2008 `ETHNIC_*` machinery has no real referent. Recommend setting ethnic seats/thresholds to
  neutral values and documenting that the ethnic channel is inert for `SK`, rather than inventing
  ethnic groups.

### RightsConfig
- Chapter II rights (Art. 10–39). Art. 37(2): rights may be restricted **by law** only for national
  security, order, or public welfare, and "no essential aspect of the freedom or right shall be
  violated" — i.e. an essence guarantee comparable to German Art. 19(2), stronger than Myanmar 2008
  s.414(b) but weaker than MFU's absolute non-suspendability.
- Art. 77(3): **under extraordinary martial law, special measures may be taken with respect to
  freedom of speech, press, assembly and association, and the powers of the courts.** So
  `RIGHTS_SUSPENDABLE` is **True** for South Korea — but with the critical difference that Art. 77(5)
  gives the legislature an unconditional lift power (see EmergencyConfig).
- Recommended: `RIGHTS_SUSPENDABLE: True`, `EMERGENCY_TOUCHES_RIGHTS: True`,
  `RIGHTS_ABSOLUTE_COUNT: 0` **plus a new/explicit "essence guarantee" flag** if the schema can take
  one, because flattening Korea to the same booleans as Myanmar 2008 loses the entire structural
  difference. Raise with `senior-simulation-engineer`.

### ExecutiveConfig
- Art. 67: President elected by **universal, equal, direct and secret ballot** (direct popular vote).
- Art. 70: **five-year term, shall not be reelected** — single non-renewable term.
- Art. 71: on vacancy/incapacity the **Prime Minister** or State Council members act, in statutory
  order of priority.
- Art. 86(1): Prime Minister appointed by the President **with the consent of the National Assembly**.
- Art. 86(3) / 87(4): **no active-duty military officer may serve as Prime Minister or as a member of
  the State Council.**
- Art. 65(2): presidential impeachment motion requires proposal by a **majority of total members** of
  the National Assembly and passage by **two-thirds or more of total members**.
- Art. 74(1): President is Commander-in-Chief of the Armed Forces.
- Art. 128(2) (anti-self-dealing entrenchment): an amendment extending the presidential term or
  altering re-election rules "shall not be effective for the President in office at the time of the
  proposal."

Mapping: this is a **semi-presidential, president-dominant civilian system**, not MFU's
ceremonial-President/executive-Chancellor split. Honest mapping to the MFU field names:
`PRESIDENT_ROLE = "head_of_state_and_executive"`, `PRESIDENT_EXECUTIVE_POWER = True`,
`PRESIDENT_TERM = 5`, `PRESIDENT_MAX_TERMS = 1`, `PRESIDENT_REELECTION = False`,
`CHANCELLOR_ROLE = "prime_minister_appointed_with_assembly_consent"` (the PM is a real office, unlike
Myanmar 2008 where it is `"none"`), `CHANCELLOR_ELECTION = "president_nominates_assembly_consents"`,
`PRESIDENT_REMOVAL_*` thresholds from Art. 65(2) (0.50 to charge, 0.667 to pass).

### ChamberConfig
- Art. 41: **unicameral** National Assembly, directly elected, **minimum 200 members** (actual size
  is statutory; 300 since 2012).
- Art. 42: four-year term.
- Art. 49: ordinary decisions by majority of members present with a majority-of-total-members quorum.
- **Zero reserved military seats.** This is the single cleanest structural contrast with Myanmar 2008
  (25%), Thailand 2017 (250 appointed senators incl. 6 ex-officio service chiefs), and Chile 1980
  (institutional senators). Encode `MILITARY_RESERVED_SEATS_* = 0`,
  `MILITARY_SEAT_PERCENTAGE = 0.0`.
- There is no second chamber and no Analysis-Council analogue. The nearest functional analogue to
  MFU's Analysis Council is the **Constitutional Court** (see JudiciaryConfig) — map
  `ANALYSIS_THRESHOLD` to the Court's 6-of-9 supermajority (0.667), and document the mapping.

### JudiciaryConfig
Two separate apex bodies — this matters and should not be collapsed:
- **Supreme Court**: Art. 104(1) Chief Justice appointed by the President **with National Assembly
  consent**; Art. 104(2) Justices appointed by the President on the Chief Justice's recommendation
  with Assembly consent. Art. 105: Chief Justice **six years, not reappointable**; Justices six
  years, reappointable.
- **Constitutional Court**: Art. 111(2) **nine adjudicators**; Art. 111(3) three selected by the
  National Assembly, three nominated by the Chief Justice, three by the President; Art. 111(4) its
  head appointed by the President with Assembly consent; Art. 112(1) six-year terms, reappointable.
  Decisions on unconstitutionality, impeachment, party dissolution and competence disputes require
  **six of nine** concurring (Art. 113(1)).
- Art. 103: judges independent, judging according to conscience and law. Art. 106: judges cannot be
  removed except by impeachment or criminal penalty.
- Art. 110: courts-martial exist as special courts, but **appeals go to the Supreme Court except for
  specified capital crimes under extraordinary martial law** (Art. 110(4)). Contrast Myanmar 2008
  s.293(b)/343(b), where the Commander-in-Chief's military-justice decision is final and conclusive.
  Encode `MILITARY_JUSTICE_FINAL: False`, `CIVILIAN_COURT_OVERRIDE_MILITARY: True`.
- `JUDGE_COUNT` (the field the engine actually reads) → 9 if mapping to the Constitutional Court,
  which is the body that performs the MFU Constitutional Court's role. `RULING_THRESHOLD` → 6.

### IIGConfig (anti-corruption body)
The 1987 Constitution has **no anti-corruption commission**. The constitutional audit body is:
- **Board of Audit and Inspection** (Art. 97–100): established under the President's direct
  jurisdiction; 5–11 members including the Chairman; Chairman appointed by the President with
  Assembly consent for a **four-year term, one reappointment maximum**; reports annually to the
  President and the National Assembly. BAI in its current form dates from the Board of Audit and
  Inspection Act 1963 (merged body established 20 March 1963).
Statutory (not constitutional) anti-corruption institutions, all post-1987 — relevant to backtesting
the *trajectory*, not to the constitutional parameters:
- Anti-Corruption Act enacted 24 July 2001; **KICAC** (Korea Independent Commission Against
  Corruption) established **25 January 2002**.
- **ACRC** (Anti-Corruption and Civil Rights Commission) launched **29 February 2008**, merging
  KICAC + Ombudsman + Administrative Appeals Commission.
- **Improper Solicitation and Graft Act** ("Kim Young-ran Act") passed 2015, in force **28 September
  2016**.
- **CIO** (Corruption Investigation Office for High-ranking Officials) formed **21 January 2021**.

Encoding recommendation: `REPORTS_TO: "president_with_assembly_consent"` (BAI, Art. 97–100),
`ANTI_CORRUPTION_OBJECTIVE: True`, `INITIAL_EFFECTIVENESS` low-to-moderate at year zero (1988) and
**rising**, because the real anti-corruption institutional build-out happened 2001→2021. If the
engine cannot take a time-varying effectiveness path, flag it: a static value will not reproduce
Korea's observed corruption decline (V-Dem political corruption 0.512 → 0.113, §2.3), and the data
analyst will see a flat-line mismatch.

### FederalConfig
Unitary. Art. 117–118: local governments handle local welfare, manage property, may enact local
autonomy provisions **within the limits of laws and regulations**; each local government shall have a
council; organisation/powers/elections determined by statute. No constitutional revenue-sharing
formula → the MFU 35/35/30 split has **no Korean counterpart**. Recommend encoding a high central
share with an explicit comment that this is a modelling proxy for a unitary state, not a
constitutional number.

### MilitaryConfig
- Art. 5(2): "The Armed Forces shall be charged with the sacred mission of national security and the
  defense of the land and **their political neutrality shall be maintained**."
- Art. 74(1): President is Commander-in-Chief; Art. 74(2) organisation/formation by statute.
- Art. 86(3)/87(4): active-duty officers barred from PM and State Council.
- Art. 39: duty of national defence; military service is statutory (Military Service Act), not a
  constitutional duration.
- **No coup mechanism, no reserved seats, no self-adjudication, no transitional immunity.**
  `COUP_LEGAL_MECHANISM: False`, `MILITARY_SELF_ADJUDICATION: False`, `CIVILIAN_COMMAND: True`.

### EconomicConfig / ScienceConfig
- Chapter IX "Economy" (Art. 119–127). Art. 119(1) market economy based on respect for individual
  freedom and creativity; Art. 119(2) state may regulate to maintain balanced growth, ensure income
  distribution, prevent market domination and abuse of economic power, **and democratise the
  economy**. Art. 126: private enterprises shall not be nationalised or transferred to public
  ownership except as provided by law to meet urgent necessities of national defence or the national
  economy.
- Art. 127(1): state shall strive to develop the national economy by developing **science and
  technology, information and human resources**; Art. 127(2) standards and measures; Art. 127(3) a
  presidential advisory organisation may be established. Art. 31(1)–(6) education, including Art.
  31(3) **free compulsory education** and Art. 31(4) **autonomy and political impartiality of
  education and university autonomy**.
- Reasonable mapping: `ACADEMIC_FREEDOM` high (Art. 31(4) is explicit), `PHD_TUITION_FREE: False`
  (free education is compulsory-level only), `RESEARCHER_ROYALTY_RATE` — no constitutional figure,
  must be a documented proxy or 0.0.

### AmendmentConfig
- Art. 128(1): proposal by a **majority of total members** of the National Assembly **or by the
  President**.
- Art. 129: public announcement for **20 days or more**.
- Art. 130(1): National Assembly must decide **within 60 days**, requiring **two-thirds of total
  members**.
- Art. 130(2): mandatory national referendum within 30 days, carried by **more than one half of all
  votes cast by more than one half of eligible voters** (i.e. a 50% turnout floor *and* a 50%
  majority).
- Art. 128(2): term-extension/re-election amendments cannot benefit the sitting President.
- No eternity clause (contrast German Art. 79(3)).
- **Observed record: zero successful amendments in 38 years.** The 2/3 + double-50% referendum rule is
  empirically extremely binding. `STANDARD_AMENDMENT_THRESHOLD: 0.667`,
  `ENTRENCHED_REQUIRES_REFERENDUM: True`, `REFERENDUM_MIN_TURNOUT: 0.50`,
  `AMENDMENT_INITIATION_THRESHOLD: 0.50`.

### TransitionConfig
The 1987 text's Addenda provide only for the first presidential election and the continuity of
existing officials — there is **no amnesty clause and no immunity clause**. Historically the opposite
happened: Chun Doo-hwan and Roh Tae-woo were **prosecuted and convicted in 1996** for the 1979
insurrection/1980 Gwangju events (later pardoned in December 1997). Encode
`AMNESTY_GRANTED: False`, `PRIOR_ACTIONS_IMMUNE: False`, `TATMADAW_IMMUNITY`-equivalent `False`.
This is a genuine, documented structural contrast with Myanmar 2008 s.445, Thailand 2017 s.279,
Pakistan Art. 270A and Chile's transitory Art. 24 — **this contrast is worth a paper sentence.**

### EmergencyConfig — the single most important South Korea parameter
- Art. 76: President may issue **emergency orders having the force of law** during internal turmoil,
  external threat, or natural calamity/financial-economic crisis when urgent measures are needed and
  the National Assembly cannot convene. Must notify the Assembly and **obtain its approval; without
  approval the orders lose effect**.
- Art. 77(1): President may proclaim **martial law** (extraordinary or precautionary) by statute when
  required by military necessity or to maintain public safety and order.
- Art. 77(3): under extraordinary martial law, special measures may be taken on speech, press,
  assembly, association and **the powers of the courts**.
- Art. 77(4): the President **must notify the National Assembly without delay**.
- **Art. 77(5): "When the National Assembly requests the lifting of martial law by a majority of the
  total members, the President shall comply."** No presidential veto. No judicial gatekeeping. No
  quorum escape hatch.

Encode this as a hard legislative kill-switch: `RIGHTS_UNTOUCHED: False`,
`TOTAL_POWER_TRANSFER_POSSIBLE: False`, `LEGISLATURE_SUSPENDED_DURING_EMERGENCY: False`, plus an
explicit `EMERGENCY_LEGISLATIVE_LIFT_THRESHOLD: 0.50` and
`EMERGENCY_LIFT_BINDING_ON_EXECUTIVE: True`. If the schema has no field for this, **add one** — it is
the mechanism that produced the 2024 outcome in §2.4, and it is the structural feature that
distinguishes `SK` from `TH`/`PK`/`CL`/`C`.

### ROEConfig / PsychConfig / CryptoJusticeConfig / NorthStarConfig
No Korean constitutional referent for Crypto-Justice or the MFU psychological-screening mandate.
Set to the same "absent" pattern used in `constitution_2008.py` (all `False`/0) and say so in
comments. For `NorthStarConfig`, Art. 4 (peaceful unification) and Art. 69 (presidential oath to
"pursue peaceful unification of the homeland") are the only constitutionally stated national
objectives; `PROGRESS_METRIC` is a modelling choice, not a constitutional one.

---

## 2. Real validation / backtesting data

### 2.1 Transparency International Corruption Perceptions Index
Access method used: TI's own per-year archive CSVs, downloaded from the download link on each
`https://www.transparency.org/en/cpi/<year>` page, plus `CPI2025_Results.xlsx` (sheet
`CPI Historical`) from `https://www.transparency.org/en/cpi/2025`.

**CPI does not exist before 1995**, and 1995–2011 scores are on a 0–10 scale that **TI itself says is
not comparable across years** (methodology change in 2012). Korea's constitution took effect in 1988,
so **there are no CPI observations for the first 7 years of the instrument.**

South Korea, 1995–2011 (0–10 scale, TI per-year archive CSVs):

| 1995 | 1996 | 1997 | 1998 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4.29 | 5.02 | 4.29 | 4.2 | 3.8 | 4.0 | 4.2 | 4.5 | 4.3 | 4.5 | 5.0 | 5.1 | 5.1 | 5.6 | 5.5 | 5.4 | 5.4 |

South Korea, 2012–2025 (0–100 scale, TI `CPI2025_Results.xlsx` → `CPI Historical`):

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 56 | 55 | 55 | 54 | 53 | 54 | 57 | 59 | 61 | 62 | 63 | 63 | 64 | 63 |

**Data-integrity warning (applies to all five packages).** TI publishes two different CSVs per
historical year. The files at `https://images.transparencycdn.org/images/CPI-Archive-<year>.csv`
contain **row-misalignment defects** in several years (an inserted or dropped country row shifts the
score/rank columns relative to the country name over a contiguous block). The files actually linked
from each year's archive page are clean. Confirmed defects affecting this project's countries:
Germany 2004 (3.6 vs correct 8.2), Germany 2008 (3.9 vs 7.9), Myanmar 2006 (4.1 vs 1.9), Thailand
2007 (3.2 vs 3.3), Pakistan 2008 (3.4 vs 2.5). Rank columns also disagree between variants for Korea
2010 (39 vs 41), Thailand 2010 (78 vs 87) and Pakistan 2010 (143 vs 146). **Use scores from the
page-linked CSVs; treat ranks as illustrative only.** This is worth one methodological sentence in
the manuscript's data appendix — it is exactly the kind of thing an adversarial reviewer spot-checks.

Secondary web tables (including the Wikipedia CPI list) disagreed with TI's own workbook in several
cells during cross-checking. **Cite TI's workbook, not aggregators.**

### 2.2 World Bank Worldwide Governance Indicators
Source: `Worldwide Governance Indicators, 2023 Update — Aggregate Governance Indicators 1996–2022`,
downloaded as `wgidataset.xlsx` from
`https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset.xlsx`
(www.govindicators.org). Scale approximately −2.5 (weak) to +2.5 (strong). Years available: 1996,
1998, 2000, then annual 2002–2022.

South Korea point estimates:

| Indicator | 1996 | 2000 | 2005 | 2010 | 2015 | 2020 | 2022 |
|---|---|---|---|---|---|---|---|
| Control of Corruption | 0.38 | 0.27 | 0.59 | 0.43 | 0.34 | 0.70 | 0.75 |
| Political Stability / No Violence | 0.57 | 0.40 | 0.49 | 0.33 | 0.16 | 0.61 | 0.56 |
| Voice & Accountability | 0.67 | 0.64 | 0.75 | 0.74 | 0.63 | 0.82 | 0.87 |
| Government Effectiveness | 0.47 | 0.61 | 0.92 | 1.15 | 0.98 | 1.37 | 1.35 |
| Rule of Law | 0.80 | 0.83 | 0.97 | 1.01 | 0.90 | 1.15 | 1.16 |

(Full annual series for 1996–2022 is in the workbook; the extraction script is trivial — the sheets
are `ControlofCorruption`, `Political StabilityNoViolence`, `VoiceandAccountability`,
`GovernmentEffectiveness`, `RuleofLaw`, header row 12, six columns per year: Estimate, StdErr,
NumSrc, Rank (percentile), Lower, Upper.)

WGI also starts after the instrument (1996 vs 1988) — 8 missing years.

### 2.3 V-Dem — the only source that covers the whole instrument window
**This is the dataset to build the Korea backtest on.** V-Dem v16 (2026) covers 1789–2025 annually,
so it spans 1988 → 2025 with no gaps, and it is the same family of measure the MFU file already
claims for its own year-zero corruption value.

Access method used: Our World in Data grapher CSV endpoints, which are V-Dem v16 processed by OWID:
```
https://ourworldindata.org/grapher/political-corruption-index.csv?csvType=full&useColumnShortNames=true
https://ourworldindata.org/grapher/electoral-democracy-index.csv?csvType=full&useColumnShortNames=true
https://ourworldindata.org/grapher/liberal-democracy-index.csv?csvType=full&useColumnShortNames=true
https://ourworldindata.org/grapher/rule-of-law-index.csv?csvType=full&useColumnShortNames=true
https://ourworldindata.org/grapher/judicial-constraints-on-the-executive-index.csv?csvType=full&useColumnShortNames=true
https://ourworldindata.org/grapher/legislative-constraints-on-the-executive-index.csv?csvType=full&useColumnShortNames=true
```
OWID's own citation string is: *V-Dem (2026) — processed by Our World in Data; V-Dem "Democracy
report v16" [original data].* **For the manuscript, cite V-Dem directly** (Coppedge et al., V-Dem
Dataset v16) and name OWID only as the access route; do not cite OWID as the source of record.

Note on direction: `political-corruption-index` (`v2x_corr`) runs **0 = clean → 1 = highly corrupt**,
i.e. the **same direction and scale as Ka-Nova's `corruption` metric**. No transformation needed.

South Korea, V-Dem annual, 1987–2005:

| year | 1987 | 1988 | 1989 | 1990 | 1991 | 1992 | 1993 | 1994 | 1995 | 1996 | 1997 | 1998 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .380 | .616 | .646 | .647 | .647 | .651 | .724 | .731 | .731 | .736 | .743 | .804 | .811 | .829 | .833 | .833 | .835 | .834 | .834 |
| liberal dem. | .219 | .469 | .498 | .500 | .500 | .512 | .607 | .612 | .612 | .618 | .638 | .729 | .736 | .753 | .757 | .761 | .761 | .761 | .762 |
| pol. corruption | .512 | .458 | .458 | .458 | .458 | .441 | .293 | .308 | .308 | .290 | .290 | .257 | .256 | .237 | .237 | .201 | .147 | .132 | .132 |
| rule of law | .594 | .799 | .804 | .806 | .806 | .819 | .894 | .894 | .894 | .894 | .901 | .919 | .919 | .929 | .929 | .936 | .946 | .949 | .949 |
| judicial constr. | .500 | .829 | .835 | .835 | .835 | .835 | .865 | .865 | .865 | .865 | .881 | .886 | .886 | .886 | .886 | .900 | .894 | .894 | .894 |
| legislative constr. | .073 | .489 | .489 | .489 | .489 | .550 | .719 | .719 | .719 | .719 | .774 | .930 | .930 | .930 | .930 | .930 | .930 | .930 | .930 |

South Korea, V-Dem annual, 2006–2025:

| year | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .834 | .834 | .759 | .759 | .762 | .762 | .753 | .716 | .705 | .705 | .718 | .852 | .857 | .842 | .850 | .852 | .802 | .722 | .724 | .819 |
| liberal dem. | .762 | .759 | .661 | .662 | .665 | .665 | .658 | .609 | .600 | .599 | .620 | .791 | .794 | .777 | .782 | .775 | .718 | .620 | .627 | .739 |
| pol. corruption | .132 | .132 | .170 | .170 | .180 | .180 | .196 | .213 | .213 | .233 | .233 | .134 | .129 | .113 | .113 | .160 | .124 | .154 | .156 | .156 |
| rule of law | .949 | .948 | .908 | .908 | .904 | .904 | .894 | .860 | .860 | .834 | .834 | .951 | .951 | .950 | .952 | .937 | .937 | .893 | .877 | .917 |
| judicial constr. | .894 | .889 | .821 | .821 | .821 | .821 | .823 | .755 | .755 | .755 | .755 | .929 | .900 | .903 | .903 | .886 | .882 | .822 | .808 | .872 |
| legislative constr. | .930 | .930 | .882 | .882 | .882 | .882 | .882 | .874 | .874 | .880 | .931 | .957 | .966 | .969 | .961 | .932 | .920 | .872 | .954 | .942 |

The 1987→1988 jump (legislative constraints .073 → .489; judicial constraints .500 → .829;
polyarchy .380 → .616) is the constitution's entry into force. **That step change is the single
cleanest "constitutional structure causes measurable governance change" data point available to this
paper**, and it is independent of anything Kaung designed.

### 2.4 Coup / transition / constitutional-crisis event history
Primary dataset: **Powell & Thyne, "Coups d'état, 1950–present", version V2026.08.29**, CSV at
`https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv` (project page
`https://jonathanmpowell.com/coups/`). Definition: "illegal and overt attempts by the military or
other elites within the state apparatus to unseat the sitting executive"; success = perpetrators
control power for at least 7 days. The dataset has 497 events total.

**South Korea has exactly one coded event in the entire 1950–2026 dataset: 1961-05-16, successful.**
Zero events after 1961, therefore zero after 1987.

Narrative event history (dates are documented facts; the coding judgements are flagged):
| Date | Event | Coded as coup by Powell-Thyne? |
|---|---|---|
| 1961-05-16 | Park Chung-hee military coup | **Yes, successful** |
| 1972-10-17 | Yusin self-coup (October Restoration) | No |
| 1979-12-12 | Chun Doo-hwan's "12.12 military insurrection" | **No** |
| 1980-05-17 | Nationwide martial law extension; Gwangju | **No** |
| 1987-06 | June Democracy Movement; 29 June declaration | n/a |
| 1987-10-28 | Constitutional referendum (94.46% for) | n/a |
| 1988-02-25 | Ninth-Amendment constitution in force | n/a |
| 1996 | Chun and Roh convicted (1979/1980 events); pardoned Dec 1997 | n/a |
| 2004-03-12 | President Roh Moo-hyun impeached by National Assembly; Constitutional Court **reinstated** him 14 May 2004 | n/a |
| 2016-12-09 | President Park Geun-hye impeached; Constitutional Court **upheld removal** 10 March 2017 | n/a |
| 2024-12-03 22:27 KST | President Yoon Suk Yeol declares martial law | **No** |
| 2024-12-04 01:02 KST | National Assembly resolution demanding lifting: **190–0**, 190 members present (Art. 77(5)) | — |
| 2024-12-04 ~04:30 KST | Cabinet approves lifting; Martial Law Command disbanded 04:49 | — |
| 2024-12-14 | National Assembly impeaches Yoon, **204 of 300** in favour (Art. 65(2) needs 200) | — |
| 2025-04-04 | Constitutional Court **unanimously** upholds impeachment; immediate removal | — |
| 2026-02-19 | Yoon convicted of insurrection; sentenced to **life imprisonment**; Kim Yong-hyun 30 years | — |

**Read this as a feature, not a bug.** The honest claim is not "South Korea has had no
constitutional stress since 1987" — it had a martial-law declaration 22 months ago. The claim is
that the 1987 Constitution's three distinct self-correction mechanisms (Art. 77(5) legislative lift,
Art. 65(2) impeachment, Art. 111/113 Constitutional Court adjudication) all fired, in sequence,
within **122 days**, and the constitution survived. That is a far stronger and far more
reviewer-proof success-case claim than a zero-coup count — see §5 flag F1.

### 2.5 Survey-based trust in government
No single series covers 1988–2026. Available real sources, with coverage:

| Source | Korea coverage | Variable / access |
|---|---|---|
| **World Values Survey** (Time-Series 1981–2022 + Wave 7) | Korea is in waves 1–7 (W1 1981-84, W2 1990-94, W3 1995-98, W4 1999-2004, W5 2005-09, W6 2010-14, W7 2017-22); Korea is also listed for WVS-8 (2024-26) | `E069_11` confidence: the government; `E069_07` parliament; `E069_10` armed forces; `E069_17` civil service; `A165` generalised trust. Access: free registration at worldvaluessurvey.org → Data and Documentation → Data Download → Timeseries (1981-2022). Korea's W7 study record: IHSN catalog 12304 ("South Korea — World Values Survey — Wave 7, 2018") |
| **Asian Barometer Survey** | Korea in all waves (W1 2001-03, W2 2005-08, W3 2010-12, W4 2014-16, W5 2018-21, W6 ongoing) | Institutional-trust battery (courts, national government, parliament, military, civil service). asianbarometer.org, registration required |
| **OECD "Trust in government"** (Gallup World Poll) | Korea 2006–present, annual | OECD.Stat / Government at a Glance |
| **OECD Survey on Drivers of Trust in Public Institutions** | Korea in 2021, 2023, 2024 rounds | OECD publication + microdata |
| **KIPA Social Integration Survey** (Korea Institute of Public Administration) | Annual since 2013, Korean-language | Institutional trust by body |

**I did not extract specific percentage values for these.** The WVS site is JavaScript-driven and the
country-wave matrix could not be scraped reliably; the Asian Barometer and KIPA microdata require
registration. What is listed above is dataset availability, variable names and access route — all
verified to exist. Any specific percentage quoted in the manuscript must be pulled from the
downloaded microdata or the published wave report and cited to that, **not to this document.** This
is flagged as limitation L2.

### 2.6 Recommended year-zero calibration (this is an inference, not a source)
| Field | Proposed value | Basis |
|---|---|---|
| `YEAR_ZERO_CORRUPTION` | **0.458** | V-Dem v16 political corruption index, South Korea, 1988 (documented value above) |
| `YEAR_ZERO_TRUST` | needs a real survey number | WVS W2 (1990-94) Korea `E069_11` is the earliest usable; **do not guess** |
| `YEAR_ZERO_COUP_RISK` | **0.00–0.02** | Powell-Thyne: zero events post-1961; a non-zero floor is defensible only as a modelling choice |
| `YEAR_ZERO_STABILITY` | WGI PV 1996 = **0.57** (−2.5..2.5), percentile ≈ rescale needed | WGI 2023 Update; note the 8-year gap from 1988 |
| `YEAR_ZERO_GINI` | Korea's income Gini is statutorily measured, not constitutional; use KOSIS/World Bank and cite the exact year | — |

Using V-Dem for year-zero corruption has the extra benefit of being internally consistent with the
MFU file's own stated basis ("V-Dem baseline Myanmar") — see §5 flag F4.

---

## 3. Country-accurate elite role titles for the LLM chain

`chain_type: "civilian"`. Seven roles to match the existing 7-agent chain. Real Korean institutional
titles, in a defensible decision order:

| Slot | Title | Constitutional basis |
|---|---|---|
| 1 | **President of the Republic of Korea** | Art. 66, 67, 70, 74 — head of state and executive, CinC |
| 2 | **Prime Minister** | Art. 86 — appointed by President with National Assembly consent |
| 3 | **Speaker of the National Assembly** | Art. 48 — presiding officer of the unicameral legislature |
| 4 | **Leader of the Opposition** (floor leader of the largest opposition negotiation group) | Not a constitutional office — statutory/parliamentary practice. **Flag as a modelling choice.** |
| 5 | **President of the Constitutional Court** | Art. 111(4) — appointed by President with Assembly consent |
| 6 | **Chairman, Board of Audit and Inspection** | Art. 98 — the constitutional audit/integrity office (use this, not the ACRC, if you want the role to be constitutionally grounded; use **Chairperson, Anti-Corruption and Civil Rights Commission** if you want the operative modern anti-corruption actor and are willing to label it statutory) |
| 7 | **Chairman of the Joint Chiefs of Staff** | Statutory; subordinate to the President as CinC (Art. 74) and barred from the State Council while on active duty (Art. 87(4)) |

Deliberately **not** included: any "Senior General" equivalent with independent political standing.
Korea's military has no constitutional political role (Art. 5(2) political neutrality) and including
one would import the military-chain pattern into a civilian-chain scenario.

Optional 8th role if the chain is ever widened: **Chief Justice of the Supreme Court** (Art. 104) —
distinct from the Constitutional Court president.

---

## 4. Honest sourcing limitations

**L1 — Referendum figures.** The 28 Oct 1987 vote counts (18,640,625 / 1,092,702 / 78.18% turnout)
were taken from the Wikipedia article on the referendum, which reports them as official NEC results.
I did not verify them against a NEC primary document. They are not load-bearing for any simulation
parameter; if the manuscript quotes them, verify against Korea's National Election Commission or
Nohlen/Grotz/Hartmann *Elections in Asia and the Pacific* before publication.

**L2 — Survey trust values are not in this document.** Dataset names, wave year-ranges, variable
codes and access routes are verified. **Specific trust percentages are not** — WVS/ABS/KIPA require
registration or non-scrapable interfaces. Do not let a percentage reach the manuscript sourced only
to this file.

**L3 — CPI and WGI both begin after the instrument.** CPI starts 1995 (7 years late), WGI starts 1996
(8 years late, and biennial until 2002). Pre-1995 CPI **does not exist**; do not interpolate it. V-Dem
is the only source covering 1988 onward continuously.

**L4 — WVS wave-by-country participation.** The wave year-ranges above (W1 1981-84 … W7 2017-22,
W8 2024-26) are verified. Korea's participation in *every* wave is reported by secondary sources and
is consistent with the per-wave study catalog records I saw, but I did not confirm it cell-by-cell
against the WVS Time-Series codebook. Treat "Korea is in waves 1–7" as high-confidence but
unverified-at-source.

**L5 — Several config categories have no Korean referent.** `CryptoJusticeConfig`, `PsychConfig`,
`IIGConfig`'s academy/partnership machinery, `FederalConfig`'s revenue split, and all `ETHNIC_*`
fields are MFU-specific inventions with no counterpart in the 1987 text. Any value placed in them is
a modelling choice, not a sourced constitutional parameter, and must be commented as such in the
Python file. If the paper reports cross-scenario parameter tables, these cells should read
"not applicable" rather than carry a number that looks sourced.

**L6 — `STATE_COUNT` / administrative divisions.** Korea's 17 first-level divisions are statutory,
not constitutional, and the number changed over the window (Sejong created 2012). Any value is a
modelling choice.

**L7 — 2026 events.** The February 2026 life sentence for Yoon is recent; verify the sentence and any
appeal status at submission time rather than relying on this document.

---

## 5. Flags for Kaung — decide before the engineer encodes

**F1 — Reframe the South Korea claim away from "zero coups since 1987."**
`.claude/memory.md` §4 justifies South Korea partly as "a clean coup-event history (zero coups since
1987, genuine civilian-military transition)." That is literally true in Powell-Thyne, but a reviewer
who knows the region will immediately raise **3 December 2024**, when a sitting President declared
martial law and deployed troops to the National Assembly. "Zero coups" would look either naive or
evasive. The stronger, fully-sourced claim is the **122-day self-correction**: Art. 77(5) legislative
lift (190–0, 4 Dec 2024) → Art. 65(2) impeachment (204/300, 14 Dec 2024) → Art. 111/113 Constitutional
Court unanimous removal (4 Apr 2025) → criminal conviction (19 Feb 2026). Also note Powell-Thyne does
**not** code 1979-12-12 or 1980-05-17 as coups, which most Korean historians would dispute — so
leaning on a bare event count from that dataset is fragile in both directions. Recommend the paper
reports coup counts *and* names the coding boundary explicitly.

**F2 — The emergency kill-switch needs a schema field that does not currently exist.**
`EmergencyConfig` in `constitution_2008.py` can express "total power transfer to the CinC" but has no
field for "legislature can unilaterally terminate the emergency by simple majority and the executive
must comply." Without such a field, South Korea's single most important structural feature is
unrepresentable and `SK` will encode as a weaker version of `C` rather than a different mechanism.
Needs a decision: extend the schema, or accept that the SK/C contrast is carried only by
coup-probability parameters.

**F3 — Korea's anti-corruption trajectory is time-varying and the schema is static.**
Korea's corruption improvement (V-Dem .458 → .113) tracks a 2001–2021 institutional build-out that
did not exist in 1988. A single static `IIGConfig.INITIAL_EFFECTIVENESS` cannot generate that path.
Either (a) accept a flat trajectory and expect the data analyst to report a backtest mismatch, or
(b) add a time-varying effectiveness schedule, which is a real engine change. Decide before encoding,
not after the 24–30 hour pod run.

**F4 — The existing Scenario C year-zero values cannot be reproduced from the sources cited in the
code, and the new scenarios should not repeat that.** `config/constitution.py:1255` attributes
`YEAR_ZERO_CORRUPTION = 0.72` to "V-Dem baseline Myanmar"; `config/constitution_2008.py:692`
attributes the **same 0.72** to "Real Myanmar CPI 2023 (Transparency International)". Neither checks
out: V-Dem v16 political corruption for Myanmar is 0.878 (2008), 0.739 (2011), 0.330 (2020), 0.662
(2021), 0.859 (2024) — 0.72 matches no year exactly; CPI 2023 Myanmar is 20/100, i.e. 0.80 inverted.
Likewise `YEAR_ZERO_STABILITY = 0.18` cited to "World Bank Political Stability 2022" does not match
Myanmar's WGI PV percentile rank (2020: 10.4, 2021: 4.7, 2022: 2.8) or its point estimate (−2.21).
Reviewer 1's calibration point makes this a live risk. Recommend a single calibration table in the
reproducibility package giving, for every scenario, the exact dataset, year, variable and
transformation behind each `YEAR_ZERO_*` value — and fixing A/C's citations while the new five are
being encoded.

**F5 — Honest field-mapping disclosure.** South Korea is a semi-presidential unitary republic being
encoded into a schema built for a federal ceremonial-president/executive-chancellor design. The
mapping decisions in §1 (President→executive, PM→`CHANCELLOR_*`, Constitutional Court→`ANALYSIS_*`)
are defensible but are *my* mappings. They should be stated in the manuscript's methods, because an
unexplained `CHANCELLOR_ROLE` field in a Korean constitution file looks like sloppiness.

---

## Schema warning (read before writing the Python file)

`config/constitution_2008.py` does **not** mirror `config/constitution.py`'s field names, despite its
own docstring claiming it does. At least 16 field names that the live engine reads are present in the
MFU file and **absent** from the 2008 file, including `judiciary.JUDGE_COUNT`, `iig.ENTRY_MERIT_MIN`,
`military.COUP_TRIGGER_LOYALTY`, `military.COUP_TRIGGER_APPROVAL`,
`iig.PROCEED_PROSECUTION_THRESHOLD`, `iig.OPEN_INVESTIGATION_THRESHOLD`, `chambers.ANALYSIS_MERIT_MIN`,
`crypto_justice.COURT_SUPERMAJORITY_FOR_TOTAL_RUIN`, `emergency.TRIGGER_SCENARIOS`,
`science.RESEARCHER_ROYALTY_RATE`, `science.PHD_KNOWLEDGE_CAPITAL_BOOST`,
`federal.TRUST_ACCELERATION_MULTIPLIER`, `amendment.CITIZENS_ASSEMBLY_SIZE`, and the
`simulation.TIME_STEPS` / `CITIZEN_AGENTS` / `SIMULATION_STATES` block.

**Use `config/constitution.py` as the field-name contract** and fill every field, so `SK` does not
inherit the 2008 file's incompleteness. There is a related engine issue (`self.CONSTITUTION` is
assigned but never read; agent/feedback modules import the MFU constitution at module level
unconditionally) that is outside this document's scope but has been reported separately to the
parent agent and to `senior-simulation-engineer` — **it determines whether any of these parameters
actually affect the simulation.**
