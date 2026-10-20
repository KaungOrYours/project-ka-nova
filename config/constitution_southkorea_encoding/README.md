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

---

# 6. Administrative geography, population structure, and real geopolitical context

*Added 2026-10-20 by `senior-researcher`, per `.claude/memory.md` section 11's standing realism
requirement and its "each country's own real neighbours" extension. This section is additive; nothing
above it has been changed. Every figure below carries its dataset, publisher, year, and access method.
Inferences are labelled INFERENCE and are never presented as observations.*

## 6.1 Real year-zero national population

| Quantity | Value | Source |
|---|---|---|
| Population, 1987 | **41,621,690** | World Bank World Development Indicators, indicator `SP.POP.TOTL`, country `KOR`, year 1987. Accessed 2026-10-20 via `https://api.worldbank.org/v2/country/KOR/indicator/SP.POP.TOTL?date=1987&format=json` |
| Population, 1988 | **42,031,247** | Same series, year 1988 |
| 1985 Population and Housing Census, national total | 40,466,577 | Statistics Korea (KOSIS) 1985 census, as tabulated by citypopulation.de |
| 1990 Population and Housing Census, national total | 43,410,899 | Statistics Korea (KOSIS) 1990 census, as tabulated by citypopulation.de |

**Which year to use.** The 1987 Constitution was promulgated 29 October 1987 and entered into force
25 February 1988. `config/constitution_southkorea.py`'s `YEAR_ZERO_CORRUPTION = 0.458` is sourced to
V-Dem **1988**. For internal consistency, year zero should be 1988 throughout → **42,031,247**.

**Citizen count at the confirmed 1:5000 ratio: 42,031,247 / 5000 = 8,406 citizens** (8,324 if 1987 is
used instead). Both are well below the locked 11,000 — see the cross-scenario statistical-power flag
in §6.7 F1.

## 6.2 Real administrative geography — `STATE_COUNT = 17` is anachronistic, the correct 1988 count is 14

17 is the **present-day** count of South Korean first-level divisions. It is not the count at year
zero, and three of the 17 did not exist in 1988.

Real timeline of first-level divisions (sourced: Wikipedia *List of provincial-level cities of South
Korea* / *Administrative divisions of South Korea*, cross-checked against the Library of Congress
*South Korea: A Country Study*, "Local Administration", which states that **in 1990** Korea had six
provincial-level cities — Seoul plus Busan, Daegu, Incheon, Daejeon and Gwangju — i.e. 15 units, one
more than in 1988):

| Unit | Status at year zero (Feb 1988) | Date of elevation |
|---|---|---|
| Seoul | Special City (*teukbyeolsi*) | 1946 |
| Busan | Directly-governed city (*jikhalsi*) | 1 Jan 1963 |
| Daegu | Directly-governed city | 1 Jul 1981 |
| Incheon | Directly-governed city | 1 Jul 1981 |
| Gwangju | Directly-governed city | 1 Nov 1986 |
| 9 provinces (*do*) | Gyeonggi, Gangwon, Chungcheongbuk, Chungcheongnam, Jeollabuk, Jeollanam, Gyeongsangbuk, Gyeongsangnam, Jeju | all pre-1948 |
| **Daejeon** | **part of Chungcheongnam** | became *jikhalsi* 1 Jan 1989 (simulated year 1) |
| **Ulsan** | **part of Gyeongsangnam** | became metropolitan city 15 Jul 1997 (simulated year 9) |
| **Sejong** | **part of Chungcheongnam** | became Special Autonomous City 2 Jul 2012 (simulated year 24) |

**Total at year zero: 14 first-level units.** (All *jikhalsi* were renamed *gwangyeoksi* /
metropolitan cities in 1995, a nomenclature change only.)

**Recommendation: encode 14 units, not 17.** Two independent reasons:
1. Period accuracy, which is the whole basis of this project's realism requirement.
2. It removes a confound. Myanmar A and C both run 14 states. If SK runs 17, any A-vs-SK difference
   is partly attributable to geographic granularity rather than to constitutional structure — exactly
   the "parameterisation-driven, not structural" objection Reviewer 2 raised. At 14 units, A, C and SK
   share state count and that channel is closed.

Change required: `FoundationalConfig.STATE_COUNT` 17 → 14, `FoundationalConfig.SIMULATION_STATE_COUNT`
17 → 14, `FederalConfig.STATE_COUNT` 17 → 14, and `SimulationConfig.SIMULATION_STATES` from the
current 17-name tuple to the 14 below. Document the three later creations as a known simplification.

### Population shares, 1990 census reconstructed onto the 14 units of 1988

Source: Statistics Korea 1990 Population and Housing Census, per-division figures as tabulated by
citypopulation.de (accessed 2026-10-20). Reconstruction: Daejeon (1,049,578) and the Sejong area
(90,502) folded back into Chungcheongnam; Ulsan (805,355) folded back into Gyeongsangnam. This is
arithmetic on published census figures, not an estimate. Flagged: 1990 is 2 years after year zero;
the 1985 census is nearer but I could not retrieve a complete 1985 per-division table online (see
§6.7 L1).

| Unit (encode as) | Real name | 1990 census pop. | Share | Citizens @1:5000 |
|---|---|---|---|---|
| `seoul` | Seoul Special City | 10,612,577 | 24.45% | 2,055 |
| `gyeonggi` | Gyeonggi-do | 6,050,943 | 13.94% | 1,172 |
| `busan` | Busan City | 3,854,960 | 8.88% | 746 |
| `gyeongnam` | Gyeongsangnam-do (incl. Ulsan) | 3,615,549 | 8.33% | 700 |
| `chungnam` | Chungcheongnam-do (incl. Daejeon, Sejong) | 3,063,504 | 7.06% | 593 |
| `gyeongbuk` | Gyeongsangbuk-do | 2,729,922 | 6.29% | 529 |
| `jeonnam` | Jeollanam-do | 2,507,439 | 5.78% | 486 |
| `daegu` | Daegu City | 2,359,713 | 5.44% | 457 |
| `jeonbuk` | Jeollabuk-do | 2,069,960 | 4.77% | 401 |
| `incheon` | Incheon City | 1,922,608 | 4.43% | 372 |
| `gangwon` | Gangwon-do | 1,580,430 | 3.64% | 306 |
| `chungbuk` | Chungcheongbuk-do | 1,389,686 | 3.20% | 269 |
| `gwangju` | Gwangju City | 1,139,003 | 2.62% | 221 |
| `jeju` | Jeju-do | 514,605 | 1.19% | 100 |
| | **total** | **43,410,899** | 100.00% | 8,406 |

(The "Citizens @1:5000" column applies each share to the 1988 national citizen count of 8,406, so it
sums correctly; it is not population/5000 per unit, which would use 1990 totals.)

**Note for whoever encodes this:** South Jeolla and Gwangju were merged into "Jeonnam-Gwangju Special
Metropolitan City" on 1 July 2026. This is irrelevant to the encoded window but will confuse anyone
who checks the present-day division list, so it is recorded here.

## 6.3 Per-unit composition — keep `ETHNIC_GROUPS = 1`, encode regional blocs instead

**Do not invent an ethnic array for Korea.** `ETHNIC_GROUPS = 1` is correct: the 1987 Constitution
recognises no ethnic-group structure and Korea is among the most ethnically homogeneous states in the
world. Fabricating an 8-slot array here would be exactly the kind of force-fit section 11 of
`.claude/memory.md` prohibits.

**But Korea does have a real, first-order, intensely documented political cleavage that is regional,
not ethnic:** *Yeongnam* (Gyeongsang) versus *Honam* (Jeolla) regionalism. It is the single most
studied variable in Korean electoral behaviour, and it was at its historical maximum in the exact year
zero. This is the defensible substitute for an ethnic composition array, and it has hard numbers.

### Real sourced data: 13th presidential election, 16 December 1987, by province

Source: 1987 South Korean presidential election results by province (National Election Commission
figures as tabulated on Wikipedia, accessed 2026-10-20). National: turnout 89.15%; Roh Tae-woo (DJP)
36.64%, Kim Young-sam (RDP) 28.04%, Kim Dae-jung (PDP) 27.05%, Kim Jong-pil (NDRP) 8.07%.

| Unit | Roh (Daegu/Gyeongbuk base) | Kim Young-sam (Busan/Gyeongnam base) | Kim Dae-jung (Honam base) | Kim Jong-pil (Chungcheong base) |
|---|---|---|---|---|
| Seoul | 29.95 | 29.14 | 32.62 | 8.20 |
| Busan | 32.11 | **55.98** | 9.14 | 2.59 |
| Daegu | **70.70** | 24.28 | 2.64 | 2.05 |
| Incheon | 39.95 | 29.99 | 21.31 | 9.21 |
| Gwangju | 4.82 | 0.52 | **94.41** | 0.23 |
| Gyeonggi | 41.45 | 27.55 | 22.30 | 8.51 |
| Gangwon | 59.53 | 26.20 | 8.87 | 5.11 |
| Chungbuk | 46.90 | 28.23 | 10.98 | 13.53 |
| Chungnam | 26.22 | 16.06 | 12.43 | **45.03** |
| Jeonbuk | 14.14 | 1.51 | **83.46** | 0.76 |
| Jeonnam | 8.17 | 1.15 | **90.28** | 0.33 |
| Gyeongbuk | **66.39** | 28.17 | 2.38 | 2.59 |
| Gyeongnam | 41.17 | **51.26** | 4.51 | 2.66 |
| Jeju | 49.77 | 26.78 | 18.64 | 4.51 |

That the division list in this real electoral table has exactly 14 rows is independent confirmation of
the 14-unit finding in §6.2.

### Recommended encoding

A 5-element per-unit array over regional-identity blocs, in this slot order:
`[capital, yeongnam, honam, chungcheong, gangwon_jeju]`.

Korean regional identity is near-perfectly territorial **outside the capital region** — unlike
Myanmar's ethnicity, which is genuinely mixed within most states. So for 11 of the 14 units the array
is close to single-category, and the real mixing happens only in Seoul / Incheon / Gyeonggi, which
absorbed mass internal migration from every region during the 1960s-80s industrialisation.

For Seoul/Incheon/Gyeonggi, the 1987 vote shares above are the best available empirical proxy for
regional-origin composition, because Korean voters in 1987 voted overwhelmingly along region of
origin. **This is an INFERENCE from documented voting behaviour, not a census origin table.** The
better source, not yet retrieved, is Statistics Korea's census "population by place of birth"
(*출생지별 인구*) table, which gives the actual origin mix of Seoul's population directly — see §6.7 L2.

**Important caveat for the paper**: this regional-bloc array is *not* a drop-in substitute for
Myanmar's ethnic array in meaning. Myanmar's ethnic structure is constitutionally recognised (reserved
seats, ethnic transfers); Korea's regional structure has no constitutional status at all. The array
should therefore drive social/trust/grievance dynamics only, never a constitutional allocation
mechanism. Encoding it as a federal resource-share key would misrepresent the 1987 Constitution.

## 6.4 Real neighbours and major-power relationships — replacing Myanmar's vector set

Myanmar's 17-vector set (`china` 0.75, `india` 0.45, `thailand` 0.40, `bangladesh` 0.25, `asean` 0.50,
three illicit networks, three "China proxies", etc.) has almost no overlap with Korea's real external
situation. ASEAN in particular is not Korea's regional body and should not appear. Proposed replacement:

| Vector | Real relationship at year zero (1988) | Real nature | Notes for the engine |
|---|---|---|---|
| `north_korea` | **The defining relationship.** Existential military threat, zero trade. Rangoon bombing 9 Oct 1983 (21 killed incl. 17 ROK officials); KAL 858 bombing 29 Nov 1987 (115 killed) — 17 days before the founding election | Security threat / legitimacy competitor | Should be high and **non-monotonic**: Sunshine Policy 1998-2008 (summits 2000, 2007) genuinely lowered it; 2006 first nuclear test, 2010 Cheonan sinking (46 killed) and Yeonpyeong shelling, 2016 Kaesong closure raised it again |
| `usa` | Treaty ally (1953 Mutual Defense Treaty); **~43,000 troops in 1987** (Library of Congress / GlobalSecurity.org USFK strength figures, stable through 1988); operational control via Combined Forces Command; also the dominant export market and the external actor that pressed against martial law in June 1987 | Alliance + security guarantor + trade pressure | Dual-signed: security support and economic coercion (1988-89 Super 301 market-opening pressure) |
| `japan` | Colonial-legacy antagonist **and** the key capital/technology/intermediate-goods supplier. 1965 Normalization Treaty + US$800m claims settlement; chronic bilateral trade deficit | Economic dependency + historical grievance | Recurrent crisis events: comfort-women disputes, Dokdo, 2019 export-control restrictions |
| `china` | **At year zero: no diplomatic relations.** PRC was the DPRK's ally. Normalised 24 Aug 1992 (simulated year 4); became Korea's largest trade partner by 2004 | Relationship that inverts mid-run | Must be a scripted regime change, not a drift. Also the 2016-17 THAAD economic retaliation |
| `ussr_russia` | No relations at year zero; Nordpolitik target; normalised 30 Sept 1990. Soviet bloc attended the 1988 Seoul Olympics after boycotting 1980 and 1984 | Diplomatic-breakthrough channel | Low magnitude after 1991 |
| `imf` | **A real, dated, hard shock, not a background vector**: standby arrangement agreed 3 Dec 1997, US$58.4bn package (then the largest in IMF history), with chaebol, labour-law and financial-supervision conditionality | Conditional lender, one-time | Simulated year 10. Should fire as a scripted/high-probability shock, not drift |
| `multilateral_institutions` | **Korea had no UN seat at year zero.** ROK and DPRK both admitted 17 Sept 1991 (year 4). APEC founding member 1989; WTO founding member 1995; OECD acceded 12 Dec 1996; G20 from 2008, hosted 2010 | Status-acquisition channel | A rising, legitimacy-conferring vector — structurally the opposite of Myanmar's UN vector, which is humanitarian-pressure-shaped |
| `global_economy` | Export-led growth model, high trade/GDP ratio | Exposure | Keep |
| `foreign_investors` | Low at year zero (capital account largely closed); liberalised sharply post-1997 | FDI | Rises after the IMF shock, not before |

**Deliberately absent: illicit networks.** Korea has no real analogue of Myanmar's Golden Triangle
drug-production economy, arms smuggling, or hawala/crypto laundering at anything like comparable
salience. Myanmar runs three such vectors; **Korea should run zero.** The nearest real phenomena are
(a) chaebol-political corruption, which is domestic and already captured by the corruption channel,
and (b) DPRK illicit activity, which is another state's behaviour, not Korea's. Encoding a Korean
illicit vector to preserve schema symmetry would be a fabrication. This is a structural difference the
methodology section should state explicitly.

**Deliberately absent: ASEAN, India, Bangladesh, "China proxies".** No real Korean counterpart.

## 6.5 Historically-calibrated shock types for Korea, 1988-2038

Myanmar's 10 `SHOCK_EVENTS` mostly do not transfer. Real, dated Korean shocks within the window:

| Shock | Real basis (dated) | Comment vs Myanmar's set |
|---|---|---|
| `financial_crisis_imf_program` | Asian Financial Crisis; IMF standby 3 Dec 1997, US$58.4bn | Replaces `sanctions` as Korea's dominant external-coercion shock. Far better dated than Myanmar's |
| `dprk_military_provocation` | 1996 Gangneung submarine infiltration; 1999 and 2002 Yellow Sea clashes; 2010 Cheonan (46 dead) and Yeonpyeong shelling | No Myanmar analogue. Closest is `regional_conflict`, but the mechanism is different: a single hostile state, not refugee/trade spillover |
| `dprk_nuclear_crisis` | 1993-94 first nuclear crisis / Agreed Framework; 2006 first test; subsequent tests | Distinct from conventional provocation; drives alliance dependence, not trade |
| `global_recession` | 2008 global financial crisis | Transfers from Myanmar's set directly |
| `oil_price_shock` | 1990 Gulf War; 2008 spike. Korea imports essentially all its oil | Transfers; higher sensitivity than Myanmar |
| `pandemic` | 2015 MERS outbreak (186 confirmed cases, 38 deaths, KCDC); 2020 COVID-19 | Transfers |
| `economic_coercion_by_partner` | 2016-17 Chinese THAAD retaliation (tourism, retail, cultural bans); 2019 Japanese export controls on semiconductor materials | New type. Not sanctions by a hostile bloc but coercion by a major trade partner — structurally distinct and real |
| `executive_corruption_scandal` | 1995-96 Chun Doo-hwan and Roh Tae-woo trials; 2016-17 Park Geun-hye impeachment and removal; 2024-25 martial-law declaration, impeachment and removal | **This is the one that matters most for this paper.** See §2.4's 122-day self-correction finding. The engine should be able to produce "executive crisis, constitutional removal, continuity" as an outcome, not only "coup, collapse" |
| `status_legitimacy_gain` (positive) | 1988 Seoul Olympics; 1996 OECD accession; 2002 World Cup; 2012 KORUS FTA in force | Positive shock, analogous to Myanmar's `fdi_boom`/`technology_leap` but legitimacy-driven |
| `export_technology_boom` (positive) | Semiconductor and later Hallyu/cultural export booms | Positive |

## 6.6 Citizen count summary

| Quantity | Value |
|---|---|
| Year zero | 1988 (constitution in force 25 Feb 1988) |
| Real population | 42,031,247 (World Bank WDI `SP.POP.TOTL`, KOR, 1988) |
| Ratio | 1:5000 (confirmed by Kaung) |
| **Citizen agents** | **8,406** |
| For comparison, locked Myanmar value | 11,000 (= 55,000,000 / 5000) |

## 6.7 Sourcing limitations and flags

**L1 — 1985 census per-division table not retrieved.** The 1985 census (1 Nov 1985) is nearer to year
zero than the 1990 census I used for shares. Its national total (40,466,577) and major-city figures
(Seoul 9,645,932; Busan 3,516,807; Daegu 2,030,672; Incheon 1,387,491; Gwangju 906,129; Daejeon
866,695) are sourced, but I could not retrieve a complete 14-division 1985 table online. KOSIS
(kosis.kr) holds it. Shares between 1985 and 1990 differ by at most a couple of percentage points
(Seoul 23.8% in 1985 vs 24.45% in 1990), so the effect on the simulation is small — but a human
should pull the real 1985 table before this appears in a manuscript table.

**L2 — Seoul's regional-origin mix is an inference, not an observation.** §6.3 uses 1987 vote shares
as a proxy. The real source is Statistics Korea's census "population by place of birth" table. Chase
this before the paper claims a sourced capital-region composition.

**L3 — `YEAR_ZERO_TRUST = 0.45` is still unsourced** (already flagged in `constitution_southkorea.py`
and in §2.6/L2 above). Nothing in this section fixes it. WVS Wave 2 (1990-94) Korea is still the
earliest usable survey reading and still requires primary microdata extraction.

**F1 — CROSS-SCENARIO STATISTICAL POWER, applies to all 7 scenarios, needs Kaung's decision.**
Applying 1:5000 to each country's own real year-zero population produces wildly unequal agent counts:
Pakistan 19,646, Thailand 14,232, Germany 9,969, **South Korea 8,406**, Chile 2,687, against Myanmar's
locked 11,000. Chile would run on roughly one seventh of Pakistan's population. Across 100 Monte Carlo
runs this means Chile's confidence intervals will be systematically wider than Pakistan's **for
reasons that have nothing to do with constitutional structure**. That is precisely Reviewer 2's
"parameterisation-driven, not structural" objection relocated into population size, and an adversarial
reviewer will find it. Three options, all of which need Kaung, not an agent:
(a) ratio-derived N everywhere — most realistic, worst for cross-scenario comparability;
(b) 11,000 everywhere — best statistically, abandons the realism rationale for the ratio;
(c) ratio-derived N **plus** explicit reporting of per-scenario N and effective sample size in every
    results table, with a note that CI width is partly N-driven — defensible, but it must be stated,
    not discovered by a reviewer.
Also note (b)/(c) interact with a further inconsistency: Myanmar's locked 11,000 corresponds to
55,000,000, but Myanmar's own World Bank 2008 population is 48,390,793, which at 1:5000 gives 9,678,
not 11,000. **The ratio rule as stated is not consistent with the already-published baseline.**

**F2 — `STATE_COUNT` change has engine consequences.** 17 → 14 touches `FoundationalConfig`,
`FederalConfig` and `SimulationConfig`, and `agents/citizen.py`'s `_assign_state()` independently
hardcodes Myanmar's 14 names with no constitution access (memory.md bug #16's deliberately-deferred
note). The state-name generalisation has to land in `citizen.py` before any of this takes effect, or
the new names will `KeyError` in `_assign_ethnicity()`.
