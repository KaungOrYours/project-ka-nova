# Thailand 2017 Constitution — Encoding Research Package

Researcher's workspace document (not code). Prepared by `senior-researcher`, 2026-10-20.
Target output: `config/constitution_thailand.py` → registry key `TH`, `chain_type: "military"`.

Intended role in the paper: **near-twin to the 2008 Myanmar military constitution** —
military-drafted, guardianship/reserved-powers structure. See §5 flag F1: the real-world outcome
data only partly supports that framing, and the paper's clustering claim needs to be stated on the
right axis.

---

## 0. Instrument definition (lock this before encoding)

| Item | Value | Source |
|---|---|---|
| Instrument | Constitution of the Kingdom of Thailand, B.E. 2560 (2017) | Constitute Project, "Thailand 2017" (https://www.constituteproject.org/constitution/Thailand_2017) |
| Drafted by | Constitution Drafting Committee appointed under the 2014 interim constitution by the **National Council for Peace and Order (NCPO)**, the junta formed after the 22 May 2014 coup | — |
| Referendum | **7 August 2016** — approved **61.35%** for / 38.65% against; turnout **≈59%** | Wikipedia "2016 Thai constitutional referendum"; US Library of Congress Global Legal Monitor, "Thailand: New Constitution Approved in Referendum", 10 Aug 2016 |
| Promulgated | 6 April 2017 | — |
| Amendments since | **One** — Constitution Amendment (No. 1) B.E. 2564, promulgated 21 November 2021, restoring a two-ballot mixed electoral system (see §4 limitation L4) | — |
| Simulation year-zero | **2017** | Promulgation year |
| Real observation window | 2017–2026 = **9 years** of a 50-year horizon | — |

The 9-year window is the shortest of all five new scenarios. That is a real constraint on
backtesting, not a detail — see §5 flag F2.

---

## 1. Real constitutional structure, mapped to the config schema

Section numbers and quoted text below were extracted from the full Constitute Project rendering of
`Thailand 2017`. Where a section was read verbatim it is marked with a quotation.

### FoundationalConfig
- Unitary kingdom; constitutional monarchy. Section 1: Thailand is one and indivisible. Section 2:
  democratic regime with the King as Head of State.
- Section 255: an amendment "which amounts to changing the democratic regime of government with the
  King as Head of State or changing the form of the State **shall be prohibited**" — an eternity
  clause, structurally parallel to German Art. 79(3) but protecting the monarchy rather than human
  dignity.
- 76 provinces + Bangkok are statutory, not constitutional. Any `STATE_COUNT` is a modelling choice.
- No constitutionally recognised ethnic-group structure → all `ETHNIC_*` fields are inert for `TH`.

### RightsConfig
- Chapter III "Rights and Liberties of the Thai People" (ss. 25–49) and Chapter V "Duties of the
  State" (ss. 51–63). Section 25 frames rights residually ("whatever is not prohibited…").
- Section 26: restriction of rights must be by law, must not be contrary to the rule of law, must not
  "increase the burden or restrict the rights or liberties of a person unduly", and must state the
  necessity.
- Section 49: no person shall exercise rights to overthrow the democratic regime with the King as
  Head of State — a militant-democracy clause.
- Emergency decrees (s. 172) and martial law/emergency statutes (Martial Law Act 1914, Emergency
  Decree 2005) operate largely outside the constitutional-rights frame; `RIGHTS_SUSPENDABLE: True`.

### ExecutiveConfig
- Section 158: "The King appoints the Prime Minister and **not more than thirty-five other
  Ministers** to constitute the Council of Ministers." The PM must be a person approved by the House
  of Representatives under s. 159. **PM term cap: "shall not hold office for more than eight years in
  total, whether or not holding consecutive term."**
- Section 159: PM candidates must come from party-submitted lists (s. 88), from parties holding
  **≥5%** of existing House members; nomination endorsed by **≥1/10** of existing House members;
  House resolution by **more than one half of the total number of existing members**.
- **Section 272 (transitory, five years from the first National Assembly under this Constitution):**
  the approval under s. 159 para. 1 "shall be done by a **joint sitting of the National Assembly**"
  and the resolution requires "more than one-half of the total number of existing members of **both
  Houses**" — i.e. 376 of 750 with the 250 appointed senators voting. If no listed candidate can be
  appointed, **≥1/2 of both Houses** may petition and a **2/3 of both Houses** resolution permits an
  outsider ("unlisted") PM. **This is the Thai analogue of Myanmar's 25% reserved bloc: a
  military-appointed Senate with a decisive vote on who governs.** Expired in 2024.
- Head of state: the King (hereditary; Palace Law on Succession 1924, s. 21). The monarchy is
  **not** reducible to the MFU `PRESIDENT_*` fields in any clean way — flag as a mapping decision.

Mapping advice: `PRESIDENT_*` → the King (ceremonial-plus-reserve-powers head of state, hereditary,
no term), `CHANCELLOR_*` → Prime Minister with `CHANCELLOR_TERM` 4 (House term) and an 8-year
cumulative cap. Document that `PRESIDENT_ELECTION = "hereditary_succession"` is a real structural
fact, not a placeholder.

### ChamberConfig
- Section 83: House of Representatives of **500 members** — 350 constituency + 150 party-list (as
  originally enacted; the 2021 amendment changed this to 400 + 100 with two ballots — see L4).
- Section 85: constituency members by direct suffrage and secret ballot.
- Section 91: party-list allocation formula (total national votes ÷ 500, proportional, minus
  constituency wins) — the "mixed-member apportionment" system, removed by the 2021 amendment.
- Section 107 (permanent rule): "The Senate consists of **two hundred members** installed from a
  **selection by and among persons** having the knowledge, expertise, experience, profession, or
  characteristics or common interests or working or having worked in varied areas of the society."
  Not elected; group-based indirect self-selection.
- Section 109: Senate term **five years**.
- Section 113: "A Senator shall not align with or yield to the mandate of any political party."
- **Section 269 (transitory): "During the initial period, the Senate shall consist of two hundred
  and fifty members appointed by the King upon the advice of the National Council for Peace and
  Order."** Composition: EC selects 200 under s. 107 → NCPO picks **50**; a 9–12 member
  NCPO-appointed Senator Selection Committee shortlists ≤400 → NCPO picks **194**; plus **6 ex
  officio** — **Permanent Secretary of the Ministry of Defence, the Supreme Commander, and the
  Commanders-in-Chief of the Royal Thai Army, Navy and Air Force, and the Commissioner-General of the
  Royal Thai Police** — totalling 250.
- Section 151: no-confidence motions are **House-only** (≥1/5 of existing House members to move). The
  Senate has no no-confidence power.
- Section 270 (transitory): the s. 269 Senate additionally has the duty and power "to monitor,
  recommend and accelerate national reform" and the preparation/implementation of the **National
  Strategy**; reform bills go to a **joint sitting** of the National Assembly.
- Section 65: the State "should set out a **national strategy**" as a binding 20-year planning
  framework (National Strategy Act 2017 → 20-year National Strategy 2018–2037, which subsequent
  governments are legally obliged to follow).

Encoding: this is a **reserved-powers legislature without reserved seats in the lower house**.
Myanmar reserves 25% of seats in *both* chambers permanently; Thailand instead made the *entire upper
house* junta-appointed for five years and permanently non-elected thereafter. Suggested fields:
`MILITARY_RESERVED_SEATS_PYITHU: 0` (House), an explicit
`UPPER_HOUSE_APPOINTED_BY: "ncpo_during_transitory_period"`,
`UPPER_HOUSE_EX_OFFICIO_MILITARY_SEATS: 6`, `UPPER_HOUSE_ELECTED: False`, and a transitory flag with
a 5-year expiry. If the schema cannot express a time-limited provision, that is a real gap — flag F3.

### JudiciaryConfig
- **Constitutional Court — Section 200: nine judges appointed by the King**, drawn as: 3 Supreme
  Court presiding justices (elected by the Supreme Court plenary), 2 Supreme Administrative Court
  judges (elected by its plenary), 1 law professor, 1 political science/public administration
  professor, 2 senior officials (Director-General level or Deputy Attorney-General or above).
- **Section 203**: the Selection Committee for the professor/official seats is chaired by the
  **President of the Supreme Court**, with the **President of the House of Representatives**, the
  **Leader of the Opposition**, the **President of the Supreme Administrative Court**, and persons
  appointed by the Independent Organs. Appointment is then on the **advice of the Senate**.
- **Section 207: seven-year term, one term only.** Section 208: vacates at age 75, or by a
  **three-fourths** resolution of the Court itself, among other grounds.
- Ordinary courts and military courts are separate; the Constitutional Court has repeatedly dissolved
  political parties and removed Prime Ministers under this constitution (documented in the event
  history, §2.4).
- `JUDGE_COUNT: 9`, `COURT_TERM_YEARS: 7`, `COURT_INDEPENDENCE`: formally yes, but note the Senate
  consent route runs through the s. 269 appointed Senate during the transitory period — a documented
  structural dependency worth a comment rather than a boolean.

### IIGConfig (anti-corruption body) — Thailand actually has one, unlike Myanmar 2008
- **Section 232: "The National Anti-Corruption Commission shall consist of nine commissioners
  appointed by the King upon the advice of the Senate from persons selected by the selection
  committee."** Required qualifications: ≥5 years as Chief Justice / Chief Justice of an
  Administrative Court of First Instance / Chief Justice of the Central Military Court /
  Director-General of a State Attorney Department; or ≥5 years at Director-General level; or ≥5 years
  as a state-enterprise chief executive; or ≥5 years as a university professor; etc.
- NACC is one of the Chapter XII "Independent Organs" (ss. 215–247), alongside the Election
  Commission, Ombudsmen, State Audit, and National Human Rights Commission.
- This is a genuine structural difference from `C`: Myanmar 2008 has **no** anti-corruption body
  (`constitution_2008.py` sets `IIGConfig` to a near-zero military-intelligence proxy), whereas
  Thailand 2017 has a constitutionally entrenched nine-member NACC with investigative and
  asset-declaration powers. Encode `ANTI_CORRUPTION_OBJECTIVE: True`,
  `REGIME_PROTECTION_OBJECTIVE: False`, a real `INVESTIGATION_TRIGGER`, and a non-trivial
  `INITIAL_EFFECTIVENESS`. **Do not copy `C`'s 0.05 floor** — that would bake the near-twin
  conclusion into the input, which is precisely Reviewer 2's objection.

### FederalConfig
Unitary; Chapter XIV "Local Administration" (ss. 249–254). No constitutional revenue-sharing
formula. All MFU `RESOURCE_*_SHARE` values are modelling proxies.

### MilitaryConfig
- **Section 52**: the State shall protect the institution of kingship, independence, sovereignty,
  territorial integrity, honour and interests of the Nation, security of the State, and public
  order; "For these purposes, the State shall provide efficient military, diplomatic, and
  intelligence services. **Armed forces shall also be deployed for the purpose of developing the
  country.**" — a constitutional internal-development role for the military.
- **Section 265 (transitory): the NCPO "shall remain in office to perform duties until the new
  Council of Ministers appointed subsequent to the first general election under this Constitution
  takes office"**, retaining "the duties and powers as provided in the Constitution of the Kingdom of
  Thailand (Interim) B.E. 2557 (2014)" as amended — which includes the interim constitution's
  **Section 44** absolute-power clause.
- **Section 279 (transitory, the immunity clause): "All announcements, orders and acts of the
  National Council for Peace and Order or of the Head of the National Council for Peace and Order
  which are in force on the day prior to the date of promulgation of this Constitution or will be
  issued under section 265 paragraph two, irrespective of their constitutional, legislative,
  executive or judicial force, as well as the performance of acts in compliance therewith **shall be
  considered constitutional, lawful and effective under this Constitution**."** Repeal requires an
  Act (or a PM order / Cabinet resolution for executive-nature orders).
- No section authorises a coup, and there is no "safeguarding the Constitution" mandate equivalent to
  Myanmar 2008 s. 20(f)/40(c)/417–419. **Thailand's 2017 constitution does not contain a legal coup
  mechanism.** Encode `COUP_LEGAL_MECHANISM: False` and record that the Thai military's political
  role runs through appointment, immunity and Senate control rather than through an emergency
  power-transfer clause. **This is a material difference from `C` that the near-twin framing must
  acknowledge.**
- Service chiefs sit ex officio in the transitory Senate (s. 269) — the clearest direct
  military-legislative link.

### EconomicConfig / ScienceConfig
- Chapter VI "Directive Principles of State Policies" (ss. 64–78) including s. 65 (national
  strategy), s. 69 (research and development, science and technology), s. 73 (agriculture), s. 75
  (free market economy, prevention of unfair monopoly). Section 54: the State shall ensure every
  child receives 12 years of quality education free of charge, from pre-school to compulsory level.
- No constitutional tax brackets, royalty rates or foreign-ownership caps → all proxies.

### AmendmentConfig — the hardest real amendment rule in the five-country set
**Section 256**, read verbatim:
- (1) Motion by the Council of Ministers; **or ≥1/5 of existing House members**; or **≥1/5 of both
  Houses combined**; or **≥50,000 eligible voters**.
- (2) Three readings in the National Assembly.
- (3) **First reading**: roll-call open vote; requires **≥1/2 of the total existing members of both
  Houses**, *and within that number* **≥1/3 of existing Senators must vote in favour** (84 of 250
  during the transitory period).
- (4) Second reading: section-by-section, simple majority.
- (5) 15-day interval before third reading.
- (6) **Third reading**: requires **>1/2 of total existing members of both Houses**, *and within
  that*: (a) House members from parties holding no Minister/Speaker/Deputy-Speaker post must supply
  **≥20%** of the combined membership of all such parties, **and** (b) **≥1/3 of existing Senators**.
- (7) 15-day interval, then presented to the King (s. 81 applies).
- (8) **Mandatory referendum** if the amendment touches Chapter I (General Provisions), Chapter II
  (The King), Chapter XV (Amendment), or qualifications/prohibitions of office-holders, or the duties
  or powers of the Courts or an Independent Organ.
- Section 256 also permits **pre-promulgation Constitutional Court review** of an amendment.

Encode: `AMENDMENT_INITIATION_THRESHOLD: 0.20`, `STANDARD_AMENDMENT_THRESHOLD: 0.50` (of joint
sitting) **with a hard `SENATE_CONCURRENCE_REQUIRED: 0.333` gate** and an
`OPPOSITION_CONCURRENCE_REQUIRED: 0.20` gate, `ENTRENCHED_REQUIRES_REFERENDUM: True`,
`MILITARY_VETO_ON_AMENDMENTS: True` during the transitory period (the 1/3-Senate gate gave the
NCPO-appointed Senate an absolute veto, which is functionally identical to Myanmar's 25% bloc under a
75% threshold). The compound-majority structure is more complex than a single float and the schema
will need extra fields — flag F3.

### TransitionConfig
- s. 265 (NCPO continuation), s. 269 (appointed Senate, 5 years), s. 272 (joint-sitting PM, 5 years),
  s. 279 (blanket validation/immunity). `AMNESTY_GRANTED: True`, `PRIOR_ACTIONS_IMMUNE: True`,
  `PRIOR_LAWS_VALID: True`, `TRANSITION_PERIOD_YEARS: 5`.
- Note the asymmetry: Myanmar 2008 s. 445 immunises the *past* SPDC/SLORC; Thailand s. 279
  immunises the past **and** future NCPO orders issued under s. 265 para. 2. Thailand's immunity is
  the broader instrument.

### EmergencyConfig
- **Section 172**: for national/public safety, national economic security, or to avert public
  calamity, the King may issue an **Emergency Decree having the force of an Act**, only where the
  Council of Ministers deems it an unavoidable emergency of necessity and urgency. It must be
  submitted to the National Assembly "without delay" in the subsequent sitting; an extraordinary
  session must be convoked if out of session. It **lapses** if the House disapproves, or if the House
  approves but the Senate disapproves and the House's reaffirmation does not exceed one half of
  existing House members.
- Martial law and states of emergency in Thailand operate mainly under **ordinary statute** — the
  Martial Law Act B.E. 2457 (1914) and the Emergency Decree on Public Administration in Emergency
  Situations B.E. 2548 (2005) — not under a constitutional emergency chapter. There is **no
  constitutional total-power-transfer clause** equivalent to Myanmar 2008 ss. 417–419.
- Encode: `TOTAL_POWER_TRANSFER_POSSIBLE: False`, `LEGISLATURE_SUSPENDED_DURING_EMERGENCY: False`,
  `RIGHTS_UNTOUCHED: False`, and a comment that Thailand's emergency powers are statutory. **This is
  an important honest finding: on the emergency axis Thailand is structurally closer to South Korea
  than to Myanmar 2008.**

### ROEConfig / PsychConfig / CryptoJusticeConfig / NorthStarConfig
No Thai referent for Crypto-Justice or psychological screening → absent pattern. For `NorthStarConfig`
there **is** a real referent: the 20-year **National Strategy** (s. 65 + National Strategy Act 2017,
National Strategy 2018–2037) with six strategic pillars. This is the closest real-world analogue to
MFU's north-star construct in the whole five-country set and is worth using rather than zeroing out.
`PROGRESS_METRIC: "national_strategy_20_year_plan"`, `HORIZON_YEARS: 20`.

---

## 2. Real validation / backtesting data

### 2.1 Transparency International CPI
Access method as in the South Korea package (TI per-year archive CSVs linked from
`transparency.org/en/cpi/<year>`, plus `CPI2025_Results.xlsx` sheet `CPI Historical`).

Thailand, 1995–2011 (0–10 scale; **TI states pre-2012 scores are not comparable across years**):

| 1995 | 1996 | 1997 | 1998 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.79 | 3.33 | 3.06 | 3.0 | 3.2 | 3.2 | 3.2 | 3.2 | 3.3 | 3.6 | 3.8 | 3.6 | 3.3 | 3.5 | 3.4 | 3.5 | 3.4 |

Thailand, 2012–2025 (0–100 scale, TI workbook):

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 37 | 35 | 38 | 38 | 35 | 37 | 36 | 36 | 36 | 35 | 36 | 35 | 34 | 33 |

**Observation for the backtest:** under the 2017 constitution, Thailand's CPI has moved 37 → 33, a
slow 4-point decline over 9 years. It has **not** collapsed. Myanmar's CPI over the first nine years
of its 2008 instrument (2012–2021) went 15 → 28, i.e. *improved*, then collapsed to 16 by 2024 after
the coup. The two trajectories are not similar in shape. See flag F1.

Data-integrity note: Thailand 2005 is stored as `"3,8"` (comma decimal) in TI's own 2005 CSV, and
Thailand 2007 is **wrong** (3.2 / rank 94) in `CPI-Archive-2007.csv` versus the correct 3.3 / rank 84
in the page-linked `CPI-2007-new_200602_092501.csv`. The 2010 rank also differs between TI's two
files (78 vs 87); the correct value is 78 (Thailand's 3.5 cannot share rank 87 with Albania's 3.3).

### 2.2 World Bank Worldwide Governance Indicators
Source: WGI 2023 Update, 1996–2022 (`wgidataset.xlsx`, www.govindicators.org). Point estimates
(−2.5…+2.5):

| Indicator | 1996 | 2000 | 2005 | 2010 | 2014 | 2017 | 2020 | 2022 |
|---|---|---|---|---|---|---|---|---|
| Control of Corruption | −0.36 | −0.23 | −0.21 | −0.36 | −0.48 | −0.45 | −0.48 | −0.45 |
| Political Stability / No Violence | 0.47 | 0.45 | −0.87 | −1.44 | −0.91 | −0.75 | −0.58 | −0.38 |
| Voice & Accountability | 0.31 | 0.47 | −0.10 | −0.50 | −0.87 | −1.05 | −0.81 | −0.62 |
| Government Effectiveness | 0.18 | 0.18 | 0.34 | 0.08 | 0.26 | 0.26 | 0.20 | 0.13 |
| Rule of Law | 0.54 | 0.58 | −0.01 | −0.23 | −0.22 | 0.01 | 0.11 | 0.07 |

Note the shape: Voice & Accountability collapses across the 2006 and 2014 coups and is only partly
recovering; Control of Corruption is **flat**, not deteriorating.

### 2.3 V-Dem (v16, 2026) — covers the full instrument window
Access method and citation guidance identical to the South Korea package (OWID grapher CSVs; cite
V-Dem directly). `political-corruption-index` runs 0 = clean → 1 = highly corrupt, same direction as
Ka-Nova's `corruption`.

Thailand, V-Dem annual, 2014–2025 (2014 = the coup that produced this constitution):

| year | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .162 | .160 | .160 | .154 | .170 | .208 | .201 | .208 | .216 | .295 | .410 | .424 |
| liberal dem. | .116 | .105 | .105 | .102 | .110 | .184 | .187 | .187 | .195 | .246 | .306 | .314 |
| pol. corruption | .671 | .683 | .683 | .683 | .692 | .696 | .681 | .681 | .654 | .654 | .635 | .635 |
| rule of law | .325 | .305 | .312 | .311 | .337 | .355 | .365 | .380 | .380 | .418 | .435 | .416 |
| judicial constr. | .647 | .602 | .602 | .602 | .602 | .621 | .611 | .662 | .662 | .721 | .725 | .733 |
| legislative constr. | .292 | .059 | .050 | .048 | .059 | .677 | .772 | .704 | .762 | .827 | .862 | .916 |

Longer context (selected years): polyarchy 1990 .264, 1997 .348, 2000 .391, 2006 .166, 2007 .180;
political corruption 1990 .760, 1997 .694, 2000 .662, 2006 .662, 2007 .654.

**Two findings a reviewer will notice, and that the paper should state rather than hide:**
1. **Legislative constraints on the executive** collapse to **.048** in 2017 — the single lowest
   value in this five-country dataset outside of Myanmar — then recover to **.916** by 2025 as the
   transitory Senate provisions expired. That is the s. 269/272 reserved-powers effect appearing and
   disappearing exactly on schedule. **This is an excellent, mechanism-specific validation target.**
2. **Political corruption is essentially flat and slightly improving** (.683 → .635) across the same
   period. Thailand's 2017 constitution suppressed democratic representation without producing a
   corruption spiral. If Ka-Nova's engine drives failure primarily through corruption accumulation,
   the simulation will *not* reproduce Thailand's observed path. Decide how to handle this before the
   run, not after.

### 2.4 Coup / transition event history
Primary dataset: **Powell & Thyne, "Coups d'état, 1950–present", V2026.08.29**
(`https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv`). Thailand has **12 coded
events**, the most of any country in this project's set:

| Date | Outcome |
|---|---|
| 1951-06-29 | failed |
| 1951-11-29 | **successful** |
| 1957-09-16 | **successful** |
| 1958-10-20 | **successful** |
| 1976-10-06 | **successful** |
| 1977-03-26 | failed |
| 1977-10-20 | **successful** |
| 1981-04-01 | failed |
| 1985-09-09 | failed |
| 1991-02-23 | **successful** |
| 2006-09-19 | **successful** |
| 2014-05-22 | **successful** |

**Zero coups since the 2017 constitution (9 years).** Base rate context: 8 successful + 4 failed in
the 64 years 1951–2014 ≈ one successful coup every 8 years before 2017.

Constitutional-crisis events *under* the 2017 constitution (these are the Thai functional equivalent
of a coup, and the paper should treat them as the relevant failure-mode observable):

| Date | Event |
|---|---|
| 2016-08-07 | Referendum approves draft (61.35% / ~59% turnout) |
| 2017-04-06 | Constitution promulgated |
| 2019-03-24 | First general election under the constitution |
| 2019-06-05 | Prayut Chan-o-cha elected PM by joint sitting under s. 272 (500 of 750) |
| 2020-02-21 | Constitutional Court dissolves the Future Forward Party |
| 2021-11-21 | Constitution Amendment (No. 1) promulgated — electoral system changed to 400 constituency + 100 list, two ballots |
| 2023-05-14 | General election; Move Forward wins most seats |
| 2023-07-13 / 19 | Pita Limjaroenrat blocked from premiership by the s. 269 Senate in joint sitting |
| 2024-05-11 | s. 269 appointed Senate's five-year term ends; s. 272 joint-sitting PM rule expires |
| 2024-08-07 | Constitutional Court dissolves Move Forward |
| 2024-08-14 | Constitutional Court removes PM Srettha Thavisin |
| 2026 | Further constitutional-reform referendum process under way (see L5) |

I have **not** independently verified every 2023–2026 date against a primary source; the 2016
referendum, the 2017 promulgation and the 2021 amendment are solid, and the party-dissolution /
PM-removal events are well documented in Freedom House and HRW country chapters. Treat the 2024–2026
items as needing a verification pass before they appear in print (limitation L5).

### 2.5 Survey-based trust in government
| Source | Thailand coverage | Notes |
|---|---|---|
| **Asian Barometer Survey** | Thailand is in Wave 1 (2001-03), Wave 2 (2005-08), Wave 3 (2010-11) and later waves conducted in **2014, 2018 and 2022** (reported as Waves 4, 5, 6) | Institutional-trust battery incl. national government, parliament, courts, **military**. Registration required at asianbarometer.org. ABS Wave 3 study record: IHSN catalog 3001 |
| **World Values Survey** | Thailand in Wave 6 (2010-14) and Wave 7 (2017-22); listed for Wave 8 (2024-26) | `E069_11` confidence in government, `E069_07` parliament, `E069_10` armed forces |
| **World Bank WGI Voice & Accountability** | 1996–2022, continuous | Not a survey of trust, but the best continuous proxy |
| **V-Dem** | 1789–2025 | Expert-coded, not public-opinion |

**No trust percentages are given here** — all require registered microdata access. See L2.

A Thailand-specific caution: trust-in-government survey readings taken under the NCPO (2014–2019)
should be treated as measured under conditions of restricted expression (lèse-majesté prosecutions,
Article 44 orders). Do not present them as comparable to Korean or German readings without saying so.

### 2.6 Recommended year-zero calibration (inference, not a source)
| Field | Proposed value | Basis |
|---|---|---|
| `YEAR_ZERO_CORRUPTION` | **0.683** | V-Dem v16 political corruption index, Thailand, 2017 |
| cross-check | 0.63 | 1 − (CPI 2017 = 37)/100 |
| `YEAR_ZERO_TRUST` | needs a real ABS/WVS number | ABS 2018 wave is the closest to year zero |
| `YEAR_ZERO_COUP_RISK` | **0.12** as a historical base rate | 8 successes / 64 years (1951–2014) ≈ 0.125/yr; this is my computation from Powell-Thyne, flag as derived |
| `YEAR_ZERO_STABILITY` | WGI PV 2017 = **−0.75** | WGI 2023 Update; needs rescaling to [0,1] |

---

## 3. Country-accurate elite role titles for the LLM chain

`chain_type: "military"`. Thailand's real decision chain during the transitory period (2017–2019) and
after:

| Slot | Title | Basis |
|---|---|---|
| 1 | **The King** (His Majesty the King of Thailand) | Head of State, s. 2; appoints PM (s. 158), Senators (s. 269), Constitutional Court judges (s. 200), NACC commissioners (s. 232) |
| 2 | **Head of the National Council for Peace and Order (NCPO)** | s. 265 — holds interim-constitution powers until the first post-election Cabinet takes office. **Transitory role: expired 2019.** |
| 3 | **Prime Minister** | s. 158/159, 8-year cumulative cap |
| 4 | **President of the Senate** | s. 269 Senate during transitory period; s. 107 Senate thereafter |
| 5 | **President of the House of Representatives** | s. 80; countersigns the Royal Command appointing the PM (s. 158) |
| 6 | **President of the Constitutional Court** | s. 200/203/207 |
| 7 | **President of the National Anti-Corruption Commission** | s. 232 |
| 8 (if the chain supports 8) | **Commander-in-Chief of the Royal Thai Army** | ex officio Senator under s. 269; the real locus of coup capability historically |

Encoding note: the NCPO Head role **must** be time-limited or the scenario will misrepresent
2019–2026. If the engine cannot retire an agent mid-run, either (a) run `TH` as the transitory-period
configuration throughout and say so explicitly in the paper, or (b) drop the NCPO slot and use the
Army CinC. Option (a) overstates military control for 2019+; option (b) understates it for 2017–2019.
Pick deliberately and disclose. Flag F3.

---

## 4. Honest sourcing limitations

**L1 — Section text source.** All section numbers/quotes come from the Constitute Project's English
rendering of `Thailand 2017`. Constitute's text is a reputable English translation but is **not** the
Thai original; the authoritative text is the Royal Gazette version in Thai (and the Office of the
Council of State's official English translation). For a published paper, cite Constitute explicitly as
the translation used. I attempted the Constitute PDF and the Thai-language sources; the PDF is
CID-font-encoded and not machine-extractable, so the HTML rendering was used.

**L2 — No survey trust percentages in this document.** Asian Barometer and WVS require registered
access. Dataset names, wave years and variable codes are verified; values are not.

**L3 — Pre-1995 CPI does not exist**, and 1995–2011 CPI is not comparable across years by TI's own
statement. Thailand's instrument begins in 2017, so this is less limiting here than for the other
four countries.

**L4 — The 2021 amendment changes encoded parameters mid-window.** Constitution Amendment (No. 1)
B.E. 2564 (promulgated 21 Nov 2021) replaced the 350+150 single-ballot mixed-member apportionment
system with 400 constituency + 100 party-list and two ballots. If `TH` is encoded with the
as-promulgated 2017 electoral system, that is correct for 2017–2021 and wrong for 2021–2026. Decide
which snapshot you are encoding and label it (`"2017_as_promulgated"` vs
`"2017_as_amended_2021"`). I verified the amendment exists and its date; I did **not** read its
operative text.

**L5 — 2023–2026 event dates need a verification pass.** The party dissolutions, the Pita blocking,
the Srettha removal and the 2026 referendum process are documented in secondary sources (Freedom
House country reports, Prachatai, ConstitutionNet, ISEAS) but I did not confirm each date against a
primary document. Do not publish these dates without a check.

**L6 — Several config categories have no Thai referent**: `CryptoJusticeConfig`, `PsychConfig`,
MFU's IIG academy/partnership machinery, `FederalConfig`'s revenue split, and all `ETHNIC_*` fields.
Values placed there are modelling choices; comment them as such.

**L7 — Monarchy mapping.** Mapping the King onto `PRESIDENT_*` fields is a modelling decision with no
clean constitutional justification. The King's real powers under this constitution (appointments on
advice, royal assent, s. 2 status, and the extra-constitutional authority that the lèse-majesté
regime protects) do not reduce to any MFU field.

---

## 5. Flags for Kaung — decide before the engineer encodes

**F1 — The near-twin claim does not survive contact with Thailand's outcome data, on the axis the
paper currently uses.** `.claude/memory.md` §4 says the design works because "multiple real military
constitutions cluster toward the 2008-Myanmar-like failure mode under the same engine." For Thailand
the real record is:
- V-Dem political corruption **flat and slightly improving** (.683 → .635, 2017→2025);
- CPI **roughly flat** (37 → 33);
- **zero coups** in 9 years;
- the constitution **still in force**, amended once;
- but V-Dem legislative constraints on the executive at **.048** in 2017 — catastrophic — recovering
  to **.916** by 2025 as the transitory clauses expired.

So Thailand 2017 is a near-twin of Myanmar 2008 on **reserved powers, immunity and representation
suppression**, and a non-twin on **corruption dynamics and regime collapse**. If the paper claims
Thailand clusters with Myanmar on corruption/coup-probability trajectories, a reviewer with V-Dem
access can falsify it in ten minutes. The defensible version is a **two-axis** claim: military-drafted
guardianship constitutions cluster on *constrained-representation and entrenched-immunity* structure,
while their *failure trajectories* diverge according to other parameters — which, incidentally, is a
more interesting and more publishable result than uniform clustering, and it directly answers the
"is divergence structural or parameter-driven?" question with a real empirical answer. **Recommend
reframing before the runs, because the framing determines which metrics you need logged.**

**F2 — Nine years of real data against a 50-year simulated horizon.** Thailand has the thinnest
backtest window of the five. Any statement of the form "the simulation reproduces Thailand's observed
trajectory" can only be evaluated on years 1–9 of 50. Say so explicitly; don't let the comparison
table imply a 50-year validation.

**F3 — Thailand needs three schema features the current 21-class schema does not have.**
(a) *Time-limited transitory provisions* — ss. 265/269/272 expire after five years and their
expiry is visible in the V-Dem data (legislative constraints .048 → .916). A static encoding cannot
represent this and will mis-predict 2019+.
(b) *Compound amendment majorities* — s. 256's "≥1/2 of both Houses **and** ≥1/3 of Senators **and**
≥20% of non-government-party House members" cannot be stored in a single
`STANDARD_AMENDMENT_THRESHOLD` float.
(c) *A bicameral asymmetry where the upper house is wholly non-elected but is not "reserved seats"* —
different from Myanmar's 25% model.
These are real engine-design questions for `senior-simulation-engineer`, not encoding details.

**F4 — Do not copy `C`'s near-zero IIG parameters into `TH`.** Thailand has a constitutionally
entrenched nine-member NACC (s. 232) and six other Independent Organs. Setting
`IIGConfig.INITIAL_EFFECTIVENESS = 0.05` because "it's a military constitution" would be exactly the
input-driven-conclusion problem Reviewer 2 raised. Use a value defensible from Thailand's actual
anti-corruption performance (CPI ~35/100, WGI Control of Corruption ~−0.45, V-Dem .68) and document
the derivation.

**F5 — Thailand's emergency powers are statutory, not constitutional.** There is no analogue of
Myanmar 2008 ss. 417–419. On the emergency axis, Thailand resembles South Korea more than Myanmar.
Encoding Thailand with a Myanmar-style total-power-transfer flag would be factually wrong.

**F6 — Year-zero calibration traceability.** See the South Korea package §5 F4: the existing A/C
`YEAR_ZERO_*` values cannot be reproduced from the sources cited in their code comments. Build the
calibration table for all seven scenarios now.

---

## Schema warning

Same as the South Korea package: `config/constitution_2008.py` is **missing ≥16 field names that the
live engine reads** (`judiciary.JUDGE_COUNT`, `military.COUP_TRIGGER_LOYALTY`,
`military.COUP_TRIGGER_APPROVAL`, `iig.ENTRY_MERIT_MIN`, `iig.OPEN_INVESTIGATION_THRESHOLD`,
`iig.PROCEED_PROSECUTION_THRESHOLD`, `chambers.ANALYSIS_MERIT_MIN`,
`crypto_justice.COURT_SUPERMAJORITY_FOR_TOTAL_RUIN`, `emergency.TRIGGER_SCENARIOS`,
`simulation.TIME_STEPS` / `CITIZEN_AGENTS` / `SIMULATION_STATES`, and others). **Use
`config/constitution.py` as the field-name contract.** A separate engine-level issue
(`self.CONSTITUTION` never read; agent modules import MFU's `CONSTITUTION` at module level) has been
reported to the parent agent — it determines whether these parameters affect the simulation at all.

---

# 6. Administrative geography, population structure, and real geopolitical context

*Added 2026-10-20 by `senior-researcher`, per `.claude/memory.md` section 11's standing realism
requirement and its "each country's own real neighbours" extension. Additive only; nothing above has
been changed. Every figure carries dataset, publisher, year and access method. Inferences are labelled
INFERENCE and never presented as observations.*

## 6.1 Real year-zero national population — two legitimate figures that differ by ~5 million

| Quantity | Value | Source |
|---|---|---|
| Population, 2017 (de facto residents) | **71,160,187** | World Bank World Development Indicators, indicator `SP.POP.TOTL`, country `THA`, year 2017. Accessed 2026-10-20 via `https://api.worldbank.org/v2/country/THA/indicator/SP.POP.TOTL?date=2017&format=json` |
| Registered population, December 2017 (Thai civil registration) | **66,188,506** | Thailand Department of Provincial Administration (DOPA) household-registration statistics, sum of the seven official regional totals (see §6.2), as reported by CEIC |

**The gap is real and it matters.** The ~5.0 million difference is dominated by non-citizen residents
not in the Thai household-registration system — principally Burmese, Cambodian and Lao migrant
workers, routinely estimated at 2-4 million. Which denominator is correct depends on what the
simulation's citizen agents represent:
- If they represent **people with political standing under the 2017 Constitution**, DOPA's 66,188,506
  is the right denominator → **13,238 citizens**.
- If the 1:5000 ratio is meant as "simulation agents per resident human", matching how it was derived
  for Myanmar (total population), World Bank's 71,160,187 is the consistent choice → **14,232
  citizens**.

**Recommendation: use the World Bank figure (14,232) for cross-scenario consistency**, because every
other scenario's ratio is being applied to a total-population figure, and document the DOPA figure and
the reason for the gap. Flag F3 in §6.7 — this needs Kaung's confirmation, not an agent's.

## 6.2 Real administrative geography — 77 provinces is far above the target range; use the official regional scheme

Thailand has 76 provinces (*changwat*) plus Bangkok Metropolitan Administration (a special
administrative area, not a province), i.e. 77 first-level units. That is four to five times the target
range of roughly 8-20 and five times Myanmar's 14. Municipal and sub-district administration is
statutory, not constitutional (as `FoundationalConfig`'s own note above already records), so any
aggregation is a modelling choice — but it should be a **real official** aggregation, not an invented
one.

### Option A (fully sourced, 7 units) — the official DOPA/NESDC regional scheme

Source: DOPA household-registration statistics, December 2017, regional aggregates as reported by
CEIC (series "Thailand Population: By Region", accessed 2026-10-20).

| Unit | Real name | Dec 2017 registered pop. | Share |
|---|---|---|---|
| `northeastern` | Northeastern region (Isan), 20 provinces | 21,989,480 | 33.22% |
| `northern` | Northern region | 12,098,164 | 18.28% |
| `bangkok_and_vicinity` | Bangkok + Nonthaburi, Pathum Thani, Samut Prakan, Samut Sakhon, Nakhon Pathom | 10,831,988 | 16.37% |
| `southern` | Southern region, 14 provinces | 9,399,578 | 14.20% |
| `eastern` | Eastern region | 4,743,840 | 7.17% |
| `western` | Western region | 3,831,952 | 5.79% |
| `central` | Central region (excl. Bangkok and vicinity) | 3,293,504 | 4.98% |
| | **total** | **66,188,506** | 100.00% |

### Option B (RECOMMENDED, 9 units) — Option A with two politically-real splits

7 units sits just under the target range, and Option A hides the two most politically consequential
distinctions in modern Thai geography. Two splits, both using real sourced province figures:

1. **Bangkok split from its vicinity.** Bangkok Metropolitan Administration alone, Dec 2017 =
   **5,682,415** (DOPA via CEIC, "Population: By Province: Bangkok"). Vicinity = 10,831,988 −
   5,682,415 = 5,149,573. Bangkok is the yellow-shirt/anti-Thaksin electoral core and the site of
   every coup; its vicinity is industrial and electorally mixed. Collapsing them erases the
   capital-versus-everywhere-else cleavage that the 2017 Constitution's appointed Senate was designed
   around.
2. **Deep South split from the rest of the South.** Pattani 709,796 + Yala 527,295 + Narathiwat
   796,239 = **2,033,330** (DOPA via CEIC, 2017). Southern remainder = 9,399,578 − 2,033,330 =
   7,366,248. These three provinces are ~80% Malay-Muslim and the site of an active insurgency with
   **7,700+ deaths since January 2004** (figure from academic/press summaries of the Deep South
   Watch dataset; see §6.7 L3 for the sourcing caveat). The adjoining Malay-Muslim districts of
   Songkhla are conventionally included in the conflict zone but are left in `southern` here to keep
   the unit boundaries identical to real province boundaries.

| Unit | Real name | Dec 2017 registered pop. | Share | Citizens @1:5000 (of 14,232) |
|---|---|---|---|---|
| `northeastern` | Northeastern / Isan | 21,989,480 | 33.22% | 4,728 |
| `northern` | Northern | 12,098,164 | 18.28% | 2,601 |
| `southern` | Southern (excl. Deep South) | 7,366,248 | 11.13% | 1,584 |
| `bangkok` | Bangkok Metropolitan Administration | 5,682,415 | 8.59% | 1,222 |
| `bangkok_vicinity` | Nonthaburi, Pathum Thani, Samut Prakan, Samut Sakhon, Nakhon Pathom | 5,149,573 | 7.78% | 1,107 |
| `eastern` | Eastern | 4,743,840 | 7.17% | 1,020 |
| `western` | Western | 3,831,952 | 5.79% | 824 |
| `central` | Central (excl. Bangkok + vicinity) | 3,293,504 | 4.98% | 709 |
| `deep_south` | Pattani, Yala, Narathiwat | 2,033,330 | 3.07% | 437 |
| | **total** | **66,188,506** | 100.00% | 14,232 |

Change required: `FoundationalConfig.STATE_COUNT` and `SIMULATION_STATE_COUNT` 14 → 9,
`FederalConfig.STATE_COUNT` 14 → 9, and **`SimulationConfig.SIMULATION_STATES` currently still holds
Myanmar's 14 state names verbatim** (`sagaing`, `mandalay`, ... `rakhine`) — it must be replaced.

**Also worth encoding, not a geography question but a federalism one:** Thailand is a unitary state.
Provincial governors are appointed by the Ministry of Interior, not elected (Bangkok's governor is the
sole elected exception). So the 35/35/30 federal-resource-share machinery inherited from MFU has no
Thai referent at all, and the regional units above should carry no autonomous fiscal or political
authority. `FederalConfig` for Thailand should be near-inert by design, and the paper should say so.

## 6.3 Per-unit composition — keep `ETHNIC_GROUPS = 0`, and do NOT convert the Isan cleavage into one

`ETHNIC_GROUPS = 0` is correct and should be preserved. The 2017 Constitution recognises no
ethnic-group structure (README §1 above, verbatim), Thai national ideology is explicitly assimilationist,
and there are no reserved seats, ethnic transfers or ethnic chambers of any kind. Fabricating an
8-slot ethnic array here would directly contradict this package's own constitutional finding.

**Thailand nevertheless has two entirely real socio-regional cleavages** with first-order political
consequences, and the honest question is how to represent them without misrepresenting the
constitution:

1. **Isan (Northeastern) regional-political bloc.** 33.2% of the registered population — the single
   largest bloc, Lao-speaking, poorest by region, and the electoral base that delivered a plurality or
   majority to every Thaksin-aligned party from 2001 onward (TRT 2001 and 2005, PPP 2007, Pheu Thai
   2011, and Pheu Thai again in 2019 and 2023 on seat count in the region). The appointed Senate of
   s.269 and the joint-sitting PM selection of s.272 exist in large part to neutralise exactly this
   bloc's electoral weight. This is the mechanism the simulation most needs to represent.
2. **Deep South Malay-Muslim population.** ~80% of Pattani, Yala and Narathiwat; distinct language
   (Patani Malay), religion, and an active armed conflict.

**Recommendation: represent both at the *unit* level, not with within-unit composition arrays.**
Reasoning, and this is a genuine structural difference from Myanmar rather than a convenience: Myanmar's
ethnicity is **mixed within states** (Yangon is `[75, 5, 6, 2, 2, 5, 2, 3]`), which is why per-state
arrays are the right shape there. Thailand's cleavages are **between regions, not within them** —
Isan is overwhelmingly Isan, Bangkok overwhelmingly Central Thai, the Deep South overwhelmingly
Malay-Muslim. The information therefore belongs in unit-level year-zero values (trust, grievance,
GDP, political alignment), which the engine already supports via `_initialize_states()`, and not in a
composition array that would be near-degenerate in 8 of 9 units.

If a composition array is wanted anyway for schema parity, use **socio-regional categories, explicitly
labelled non-constitutional**: `[central_thai, isan_lao, northern_lanna, southern_thai_buddhist,
malay_muslim]`. Do **not** rename `ETHNIC_GROUPS` to a non-zero value to carry this — that field means
"constitutionally recognised ethnic groups" everywhere else in the project, and changing its meaning
for one country would break the cross-scenario interpretation and re-trigger the CVES L1 schema and
`ELITE_SYSTEM_PROMPTS` few-shot work that bug #19 just fixed.

## 6.4 Real neighbours and major-power relationships — replacing Myanmar's vector set

Thailand is the one new country whose vector set genuinely overlaps Myanmar's, because they are each
other's neighbours. Note the pleasing realism point for the methodology section: **`thailand` is
already a vector in Myanmar's Scenario A/C set at 0.40, so A/C and TH are mutual neighbours** — the
first reciprocal pair in the 7-constitution design.

| Vector | Real relationship in 2017 | Real nature | Notes for the engine |
|---|---|---|---|
| `china` | **Thailand's largest trade partner** (since roughly 2013) and largest tourist source (~10m arrivals/yr pre-COVID). Post-2014-coup security pivot is concrete and dated: the S26T *Yuan*-class submarine contract signed 2017, VT-4 main battle tank purchases, and the Thai-Chinese high-speed rail project | Trade dependence + post-coup security realignment | The single most consequential external change *caused by* the constitutional order being encoded. Should rise through the run |
| `myanmar` | 2,416 km border. Largest migrant-labour source (commonly estimated 1.5-2m+ Burmese workers, part of the 5m registration gap in §6.1); ~90,000 refugees in nine Tak / Mae Hong Son border camps; cross-border conflict spillover | Labour supply + refugee/conflict spillover | Should spike post-Feb-2021 (real: large new inflows after Myanmar's coup) |
| `usa` | Treaty ally on paper (1954 Manila Pact, 1962 Thanat-Rusk communiqué) but **deliberately downgraded** after the 2014 coup: ~US$4.7m in security assistance suspended, Cobra Gold scaled back. Partially restored from 2017 (Prayut's White House visit, October 2017) | Formal alliance with sharply reduced real engagement | Structurally interesting: a *treaty ally* whose engagement fell *because of* the constitutional order. Low value at year zero, rising |
| `asean` | Founding member (Bangkok Declaration, 8 Aug 1967); ASEAN's non-interference norm is precisely why the 2014 coup carried essentially no regional cost | Regional shield | **Opposite sign to Myanmar's ASEAN vector.** ASEAN constrained Myanmar (Five-Point Consensus, leader exclusion); it insulated Thailand. Same institution, inverse function — a strong point for the paper |
| `eu` | Official visits and FTA negotiations suspended after the 2014 coup; Council conclusions of 11 Dec 2017 resumed political contacts; FTA talks relaunched 2023. Separately, the IUU-fishing **yellow card** issued April 2015, lifted January 2019 | Conditional trade pressure | The yellow card is a real, dated, bounded economic-pressure event — a far better-specified `sanctions` analogue than Myanmar's generic one |
| `japan` | Largest cumulative FDI stock in Thai manufacturing, especially automotive; anchor investor base for the Eastern Economic Corridor | Investment dependence | Stable, high, apolitical — contrast with China's politically-contingent rise |
| `malaysia` | Deep South border; facilitator of the Barisan Revolusi Nasional / MARA Patani peace process from 2013 | Border security + mediator | Links directly to the `deep_south` unit |
| `cambodia_laos` | Preah Vihear temple dispute with Cambodia, with real armed border clashes 2008-2011; ICJ interpretation judgment 11 Nov 2013. Mekong water/dam issues with Laos | Low-intensity border friction | Low magnitude, non-zero |
| `global_economy` | Tourism-dependent (directly ~11-12% of GDP, ~20% including indirect effects) and export-dependent | High exposure | Higher sensitivity than Myanmar's |
| `illicit_transit_networks` | **Real, but structurally different from Myanmar's.** Thailand is primarily a **transit and destination** state: methamphetamine inflow from Shan State, trafficking in the fishing sector (the basis of the 2015 EU yellow card and the 2014 US TIP Tier 3 downgrade), and the migrant-labour brokerage economy | Transit/destination, not production | **Recommend 1-2 vectors, not Myanmar's 3**, and label them transit/destination. Thailand is the demand-and-corridor side of the same regional economy Myanmar produces for |

**Deliberately absent: India, Bangladesh, "China proxies".** No real Thai counterpart at meaningful magnitude.

## 6.5 Historically-calibrated shock types for Thailand, 2017-2067

| Shock | Real basis (dated) | Comment |
|---|---|---|
| `royal_succession_legitimacy` | King Bhumibol died 13 Oct 2016, **13 months before this constitution's promulgation**; Vajiralongkorn's accession and the 2017 pre-promulgation royal amendments to the draft text | **No analogue in any other scenario.** The single largest real legitimacy variable in the Thai window and it sits immediately before year zero |
| `coup` | 13 successful coups since 1932; README §2.6's own Powell-Thyne computation gives ≈0.125/yr for 1951-2014. But the **observed** record under this instrument is zero coups in nine years | Directly connected to the open question in memory.md §4a/bug #14: Thailand's encoded `COUP_TRIGGER_*` are both 0.0, same as Myanmar's, and Thailand collapsed at year 15-16 in testing — flattening exactly this contrast |
| `pandemic` | COVID-19. Thailand's tourism-dependent economy contracted 6.1% in 2020 (World Bank/NESDC) | Transfers from Myanmar's set but with much higher intensity, because of tourism share |
| `flooding` | The 2011 floods cost roughly 1.4 trillion baht / ~US$46bn (World Bank damage and loss assessment) — before the window, but establishes the real base rate and magnitude | Replaces Myanmar's generic `natural_disaster`, with a real Thai magnitude |
| `insurgency_escalation` | Deep South, 7,700+ deaths since Jan 2004; Tak Bai incident 25 Oct 2004 (7 shot, 78 asphyxiated in custody) | Localised to the `deep_south` unit, not national |
| `trade_sanction_equivalent` | EU IUU yellow card Apr 2015 - Jan 2019; US TIP Tier 3 downgrade 2014; EU FTA suspension 2014-2023 | Thailand's real `sanctions` analogue: conditional, reversible, sector-specific — not Myanmar's banking isolation |
| `tourism_demand_shock` | Chinese arrivals collapse (2020-22); the 2018 Phuket boat disaster's effect on Chinese bookings | New type, no Myanmar analogue, large for Thailand |
| `mekong_drought` | Upstream dam operation and recurring Mekong low-flow events from the late 2010s | Regional environmental, affects `northeastern` disproportionately |
| `migrant_influx` | Post-Feb-2021 inflows from Myanmar | Reciprocal with Scenario A/C's own outflows |
| `global_recession`, `oil_price_shock`, `fdi_boom` | Transfer from Myanmar's existing set | Keep |

## 6.6 Citizen count summary

| Quantity | Value |
|---|---|
| Year zero | 2017 (constitution promulgated 6 April 2017) |
| Real population (recommended) | 71,160,187 (World Bank WDI `SP.POP.TOTL`, THA, 2017) |
| Real registered population (alternative) | 66,188,506 (DOPA civil registration, Dec 2017) |
| Ratio | 1:5000 (confirmed by Kaung) |
| **Citizen agents (recommended)** | **14,232** (13,238 on the DOPA denominator) |
| For comparison, locked Myanmar value | 11,000 |

## 6.7 Sourcing limitations and flags

**L1 — regional figures come via CEIC, not directly from DOPA.** The underlying publisher is Thailand's
Department of Provincial Administration and CEIC states this explicitly, but I retrieved the regional
and provincial numbers through CEIC's series pages (ceicdata.com returned HTTP 403 to direct fetch;
values were obtained through search result snippets). The `central` figure in particular (3,293,504)
is low enough to look wrong at first glance — it is correct only under the 7-region scheme where
Bangkok-and-vicinity, Eastern and Western are separate regions. Verification: the seven regional
figures sum to 66,188,506, which is consistent with Thailand's known 2017 registered total. A human
should re-pull these from DOPA's own annual statistics before they enter a manuscript table.

**L2 — the 9-unit scheme in Option B is my aggregation, not an official Thai one.** The 7-region base
is official (DOPA/NESDC); the Bangkok and Deep South splits are mine, justified above but still a
modelling decision. Label it as such in the methods section.

**L3 — the 7,700+ Deep South death toll is a widely-repeated figure traceable to Deep South Watch
(Prince of Songkla University), but I did not retrieve the primary dataset.** Cite Deep South Watch
directly, with an accessed-date, before this number appears in the manuscript.

**L4 — `YEAR_ZERO_GINI` and `YEAR_ZERO_EMPLOYMENT` remain unsourced** (already flagged in
`constitution_thailand.py`). Nothing in this section fixes them. Note that if the regional units above
are encoded, the state-GDP Gini (memory.md bug #2: Phase 3's live Gini is *geographic*, computed from
state GDP levels) becomes much more meaningful for Thailand than for Myanmar, because Thai regional
income inequality (Bangkok versus Isan) is one of the largest regional gaps in Southeast Asia. Worth
telling `senior-data-analyst`.

**F1 — `ETHNIC_GROUPS` must stay 0.** Raising it to carry the Isan or Malay-Muslim cleavage would
change the field's meaning for one scenario only, break cross-scenario interpretation, and re-trigger
the CVES L1 schema-length and `ELITE_SYSTEM_PROMPTS` few-shot work that bug #19 just completed.

**F2 — the unitary-state point should be encoded, not just noted.** Thailand's regional units must
carry no autonomous fiscal/political authority. If `FederalConfig`'s resource-share machinery runs on
Thailand with MFU-like values, the simulation will model a decentralisation that does not exist.

**F3 — population denominator needs Kaung's call** (World Bank 71.16m versus DOPA 66.19m, §6.1).

**F4 — CROSS-SCENARIO STATISTICAL POWER, all 7 scenarios, needs Kaung's decision.** See the South
Korea package §6.7 F1 for the full statement. Short version: ratio-derived N gives Pakistan 19,646,
**Thailand 14,232**, Germany 9,969, South Korea 8,406, Chile 2,687, against Myanmar's locked 11,000.
Unequal N means systematically unequal CI widths for reasons unrelated to constitutional structure —
Reviewer 2's objection relocated into population size. Thailand at 14,232 also increases compute cost
by ~29% per run relative to 11,000, and Pakistan by ~79%; flag to `senior-devops-engineer` for the
RunPod budget estimate in memory.md §4.
