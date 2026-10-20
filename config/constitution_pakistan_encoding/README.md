# Pakistan — 1973 Constitution + Zia's Eighth Amendment (1985) — Encoding Research Package

Researcher's workspace document (not code). Prepared by `senior-researcher`, 2026-10-20.
Target output: `config/constitution_pakistan.py` → registry key `PK`, `chain_type: "military"`.

Intended role in the paper: **near-twin to the 2008 Myanmar military constitution.** Of the five new
scenarios, **Pakistan is the strongest near-twin and the strongest external anchor for Ka-Nova's
headline number** — see §5 flag F1. Do not let the instrument definition drift; it is confirmed and
not open for debate per `.claude/memory.md` §4.

---

## 0. Instrument definition (confirmed — do not change)

The instrument is a **composite of two 1985 acts operating on the 1973 Constitution**. Encode both
and label them both, because almost every parameter that matters comes from one or the other:

| Item | Value | Source |
|---|---|---|
| Base text | Constitution of the Islamic Republic of Pakistan, 1973 (in force 14 August 1973) | pakistani.org annotated text |
| Instrument A | **Revival of the Constitution of 1973 Order, 1985 (President's Order No. 14 of 1985)** — effective **2 March 1985**. Made "a large number of amendments" to the 1973 text before parliament reconvened | pakistani.org footnotes 8, 9, 80, 81, 92–96, 112, 121, 132–143, 850 etc., all citing "Revival of Constitution of 1973 Order, 1985 (President's Order No. 14 of 1985), Art 2, Sch. item N (with effect from March 2, 1985)" |
| Instrument B | **Constitution (Eighth Amendment) Act, 1985 (Act 18 of 1985)** — presidential assent **9 November 1985**, Gazette of Pakistan Extraordinary **11 November 1985**; s. 19 (Art. 270A) in force on revocation of the 5 July 1977 Proclamation | Full text at `https://www.pakistani.org/pakistan/constitution/amendments/8amendment.html` (read in full for this package) |
| Repeal | Art. 58(2)(b) **omitted by the Thirteenth Amendment, April 1997**; restored by LFO 2002 / 17th Amendment 2003; finally removed by the **Eighteenth Amendment, 19 April 2010** | pakistani.org; Wikipedia "Article 58(2)(b) of the Constitution of Pakistan" |
| Instrument lifespan | **2 March 1985 → April 1997** (58(2)(b) repealed) / **12 October 1999** (the order itself destroyed by coup) | — |
| Simulation year-zero | **1985** | RCO date |
| Real observation window | 1985 → 1999 = **14.6 years to constitutional collapse** | Powell & Thyne V2026.08.29 |

Recommended label: `"1973_constitution_as_revived_1985_with_eighth_amendment"`.

Precision point that is commonly got wrong in secondary literature: **Article 2A (Objectives
Resolution made a substantive part of the Constitution) was inserted by the RCO 1985, P.O. 14 of
1985, Sch. item 2, with effect from 2 March 1985 — NOT by the Eighth Amendment.** The Eighth
Amendment's own text (read in full) contains no Article 2A provision; it *affirmed and validated*
the RCO via the new Article 270A. Many sources conflate the two. Get this right in the manuscript.

---

## 1. Real constitutional structure, mapped to the config schema

Article numbers verified against the annotated text at pakistani.org (which carries amendment
footnotes identifying each change's instrument and effective date) and the full text of the Eighth
Amendment Act. Where the current text differs from the 1985–1997 text, the 1985–1997 position is
given and marked.

### FoundationalConfig
- Art. 1: Islamic Republic of Pakistan, a **federation** of four provinces plus the Islamabad Capital
  Territory plus (until 2018) the Federally Administered Tribal Areas.
- Art. 2: Islam is the State religion. **Art. 2A (RCO 1985)**: "The principles and provisions set out
  in the Objectives Resolution reproduced in the Annex are hereby made **substantive part of the
  Constitution** and shall have effect accordingly."
- Art. 5(1) loyalty to the State is the basic duty of every citizen; Art. 5(2) obedience to the
  Constitution is the (1985: "basic"; now "inviolable") obligation of every citizen.
- Art. 6 **High treason**: abrogating or subverting the Constitution by force is high treason;
  Majlis-e-Shoora shall by law provide punishment. *Note the irony to record for the paper: Art. 6
  existed throughout and did not prevent 1977 or 1999; Art. 270A retroactively validated the 1977
  abrogation.*
- `STATE_COUNT`: 4 provinces (+ ICT + FATA). Unlike Korea/Thailand, Pakistan **is** genuinely
  federal, so `FederalConfig` is meaningful here.

### RightsConfig
- Part II Chapter 1 "Fundamental Rights" (Art. 8–28). Art. 8(1)–(2): laws inconsistent with
  fundamental rights are void.
- **Art. 8(3)(b) + the First Schedule**: laws listed in the First Schedule are **exempted from Art.
  8(1)-(2)** — i.e. a schedule of rights-immune statutes. The RCO/Eighth Amendment era expanded this
  mechanism. `RIGHTS_ABSOLUTE_COUNT` should therefore be **0** with a comment pointing at Art. 8(3).
- Art. 232–237 Emergency: Art. 233 permits suspension of named fundamental rights during a
  Proclamation of Emergency; **Art. 233(2) permits the President to suspend the right to move any
  court for enforcement of rights.** `RIGHTS_SUSPENDABLE: True`, `EMERGENCY_TOUCHES_RIGHTS: True`.
- Art. 199(3) + **Art. 245(3)–(4)** (inserted by the Seventh Amendment 1977, i.e. already in force in
  1985): "A High Court shall not exercise any jurisdiction under Article 199 in relation to any area
  in which the Armed Forces of Pakistan are, for the time being, acting in aid of civil power in
  pursuance of Article 245" and pending proceedings "shall remain suspended". **This is a judicial
  no-go zone wherever the army is deployed domestically — a structurally stronger exclusion than
  anything in Thailand 2017 and directly comparable to Myanmar 2008 s. 293(b)/343(b).**

### ExecutiveConfig — a semi-presidential design with a president-dominant tilt
- **Art. 41(1)**: President is Head of State and represents the unity of the Republic. Art. 41(2):
  must be a Muslim, ≥45 years old, qualified to be an NA member. **Art. 41(3)**: elected in accordance
  with the Second Schedule by an **electoral college consisting of the members of both Houses and the
  members of the Provincial Assemblies**. Art. 41(6): "The validity of the election of the President
  **shall not be called in question by or before any court or other authority**."
- **Art. 44(1)**: five-year term. Art. 44(2): re-eligible but **no more than two consecutive terms**.
- **Art. 47**: removal/impeachment of the President — resolution on grounds of physical/mental
  incapacity or violation of the Constitution/gross misconduct, requiring notice by **not less than
  one-half of the total membership of either House** and passage by **not less than two-thirds of the
  total membership of Majlis-e-Shoora in joint sitting**.
- **Art. 48 as amended by the Eighth Amendment, s. 2** — this is the core of the instrument:
  - (1) The President shall act "**on the advice of the Cabinet or the Prime Minister**", with a new
    proviso: "the President may require the Cabinet or, as the case may be, the Prime Minister to
    reconsider such advice, either generally or otherwise, and the President shall act in accordance
    with the advice tendered after such reconsideration."
  - (2) as amended: where the President acts in his discretion, "**and the validity of anything done
    by the President in his discretion shall not be called in question on any ground whatsoever**" —
    a non-justiciability clause for all discretionary presidential acts.
  - (3) omitted (removing a check).
  - (5)(a): referendum timing — "one hundred" changed to "**ninety**" days.
- **Art. 58(2) as substituted by the Eighth Amendment, s. 5(b)** — verbatim: *"Notwithstanding
  anything contained in clause (2) of Article 48, the President may **also dissolve the National
  Assembly in his discretion** where, in his opinion, (a) a vote of no-confidence having been passed
  against the Prime Minister, no other member of the National Assembly is likely to command the
  confidence of the majority…; or **(b) a situation has arisen in which the Government of the
  Federation cannot be carried on in accordance with the provisions of the Constitution and an appeal
  to the electorate is necessary.**"* This is the provision the instrument was selected for.
- **Art. 91 as amended by the Eighth Amendment, s. 10**:
  - new **(2-A)**: only *after 20 March 1990* must the President invite the member who commands the
    confidence of the NA majority. **Before that date the President's choice of PM was unconstrained**
    — a time-limited enhanced-discretion window of ~4.5 years from the amendment.
  - new **(5)**: "The Prime Minister **shall hold office during the pleasure of the President**, but
    the President shall not exercise his powers under this clause unless he is satisfied that the
    Prime Minister does not command the confidence of the majority…, in which case he shall summon
    the National Assembly and require the Prime Minister to obtain a vote of confidence."
- **Art. 95**: vote of no-confidence in the PM — resolution moved by not less than 20% of the total
  membership of the NA; carried by a **majority of the total membership**.
- Art. 101 (Eighth Amendment s. 11): Governors appointed by the President "**after consultation with
  the Prime Minister**" (previously "in his discretion"). Art. 105/112 (ss. 12, 14): the provincial
  mirror of 58(2)(b) — **Governor may dissolve a Provincial Assembly in his discretion subject to the
  previous approval of the President**, on 58(2)(b)-identical grounds.

Mapping advice: `PRESIDENT_ROLE = "head_of_state_with_discretionary_dissolution_power"`,
`PRESIDENT_EXECUTIVE_POWER = True`, `PRESIDENT_ELECTION = "electoral_college_both_houses_plus_provincial_assemblies"`,
`PRESIDENT_TERM = 5`, `PRESIDENT_MAX_TERMS = 2` (consecutive),
`PRESIDENT_REMOVAL_APPROVAL_THRESHOLD = 0.50` (notice) with a `0.667` joint-sitting passage threshold,
`CHANCELLOR_ROLE = "prime_minister_at_presidential_pleasure"`,
`CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT = True`, and a dedicated
`EXECUTIVE_DISCRETIONARY_DISSOLUTION: True` / `DISSOLUTION_NON_JUSTICIABLE: True` pair, because
58(2)(b) + 48(2) together is a mechanism the current schema cannot express.

### ChamberConfig
- Art. 50: Majlis-e-Shoora (Parliament) = **President + National Assembly + Senate** (the RCO 1985
  substituted this formulation for the 1973 original "a Parliament consisting of two houses").
  Constitutionally including the President in Parliament is itself a structural signal.
- **National Assembly 1985–1997: 237 seats — 207 general + 20 reserved for women + 10 for
  non-Muslims.** The RCO 1985 added 7 general seats and 10 women's seats. (Verified via the Inter-
  Parliamentary Union's archived 1985 Pakistan election report and the National Assembly's own
  history page; **not** verified verbatim from the 1985-era Art. 51 text — see limitation L1.)
- Art. 52: NA term five years from its first sitting unless sooner dissolved.
- **Senate 1985–1997: 87 members** (the RCO 1985 substituted this for the 1973 original
  "sixty-three"; footnote 132). Composition: 14 elected by each of the four Provincial Assemblies, 8
  by NA members from FATA, 3 from the Federal Capital, 5 more per Provincial Assembly. **Art. 59(3)
  as amended by the RCO: Senate term six years** (the 1973 original was four years, half retiring
  every two) with one-half retiring every three years; the Senate **is not subject to dissolution**.
- Art. 75 as amended by the Eighth Amendment, s. 8: presidential reference-back window cut from 45 to
  **30 days**; on reconsideration a **joint sitting** majority of members present and voting
  overrides and "the President **shall not** withhold assent".
- **Zero reserved military seats.** Pakistan's military influence under this instrument runs through
  the presidency, the non-justiciability clauses and Art. 270A immunity — **not** through reserved
  seats. This is the key structural difference from Myanmar 2008 (25%) and Thailand 2017 (6 ex-officio
  senators + 250 appointed). Encode `MILITARY_SEAT_PERCENTAGE: 0.0` and put the military's weight into
  the executive/immunity/judicial-exclusion parameters instead.

### JudiciaryConfig
- Art. 175: Supreme Court, High Courts, and such other courts as may be established by law.
- Art. 177 (1985-era text): Chief Justice of Pakistan appointed by the President; other Supreme Court
  judges appointed by the President **after consultation with the Chief Justice**. (The modern Art.
  175A judicial-commission regime dates from the 18th/19th Amendments, 2010–2011; do **not** encode
  it for this instrument.)
- Art. 179 (1985-era): Supreme Court judges retire at **65**; High Court judges at **62** (Art. 195).
- **Art. 209 Supreme Judicial Council**: the only route to remove a judge. In the 1985-era text the
  Council comprised the Chief Justice of Pakistan, the two next most senior Supreme Court judges, and
  the two most senior High Court Chief Justices. (The current text is very different following the
  27th Amendment of November 2025 — do not copy today's composition.)
- **Chapter 3A, Articles 203A–203J — Federal Shariat Court.** Established by President's Order No. 1
  of 1980 and entrenched in the Constitution; Art. 203C: a court of **not more than eight Muslim
  judges including the Chief Justice**, appointed by the President; Art. 203D: power to examine and
  strike down any law repugnant to the Injunctions of Islam (with carve-outs in Art. 203B(c) for the
  Constitution itself, Muslim Personal Law, court procedure, and — for a period of years — fiscal
  laws, banking and insurance). **Judges of the FSC served at the President's pleasure and could be
  transferred back to their High Courts, which is why the FSC is treated in the literature as a
  presidentially-controlled parallel apex court.** This is a real structural feature with no MFU or
  Myanmar-2008 analogue; it needs either a new field or an explicit comment.
- **Art. 239(5)–(6) (see AmendmentConfig) strips courts of jurisdiction to review constitutional
  amendments.** Combined with Art. 48(2) (discretionary acts non-justiciable), Art. 41(6)
  (presidential election non-justiciable), Art. 245(2)–(4) (army-deployment areas non-justiciable),
  and Art. 270A (all 1977–1985 acts non-justiciable), this instrument contains **five separate
  jurisdiction-stripping clauses**. That cluster is the most defensible quantitative
  "judicial-independence" input for the encoding. `COURT_INDEPENDENCE: False` is justified here on
  textual grounds, not on vibes.
- `JUDGE_COUNT`: the Supreme Court's strength is fixed by Act of Parliament, not the Constitution
  (Art. 176). In 1985 it was 7 + CJ (verify before encoding, L1). Suggest `JUDGE_COUNT: 8` with a
  comment, or map to the FSC's 8.

### IIGConfig (anti-corruption body)
**The 1973 Constitution, as revived in 1985, contains no anti-corruption commission.** The nearest
constitutional integrity organ is the **Auditor-General of Pakistan** (Art. 168–171), appointed by
the President, reporting to the President who causes the reports to be laid before the NA.

Statutory history, for trajectory context only:
- Ehtesab (Accountability) Ordinance 1996 → Ehtesab Act 1997 (Nawaz Sharif era) — **post-dates** the
  58(2)(b) era.
- **National Accountability Bureau** created by the National Accountability Ordinance 1999,
  promulgated by General Musharraf's regime in November 1999 — i.e. **after** the instrument's
  collapse. NAB is widely documented as having been used selectively against opposition politicians.

Encoding recommendation: this scenario genuinely resembles `C` on the anti-corruption axis — a very
low `INITIAL_EFFECTIVENESS` is **defensible from the text** (no body exists) rather than assumed.
Document that justification explicitly so it does not look like the Myanmar values were copied.
`REPORTS_TO: "president"` (Auditor-General, Art. 171), `ANTI_CORRUPTION_OBJECTIVE: False` is too
strong — the Auditor-General has a real audit mandate; prefer a low effectiveness with a real
mandate rather than an inverted objective.

### FederalConfig — genuinely federal, unlike SK/TH/DE-at-1949 comparisons
- Art. 141–144: Federal Legislative List and **Concurrent Legislative List** (the Concurrent List was
  abolished only by the 18th Amendment in 2010, so in 1985 it existed and gave the federation broad
  reach). **Eighth Amendment s. 17 omitted Art. 144(2)**, further adjusting federal-provincial
  balance.
- Art. 160–161: **National Finance Commission** and the distribution of revenues between the
  Federation and provinces. Art. 161: net proceeds of the federal excise duty on natural gas and
  royalties on crude oil **go to the province in which the well-head is situated** — a real,
  constitutionally specified resource-sharing rule, unlike Korea/Thailand.
- Art. 232(2)(b)–(c): during a Proclamation of Emergency the Federation may **assume all or any of
  the functions of a provincial government** and suspend constitutional provisions relating to any
  provincial body or authority (except High Courts).
- Art. 234: proclamation in case of failure of constitutional machinery in a province.
- Encode a real `RESOURCE_*_SHARE` split derived from Art. 160/161 + the 1985-era NFC award if the
  data analyst can source the award percentages; otherwise flag the split as a documented proxy. Do
  not reuse MFU's 35/35/30.

### MilitaryConfig — the heart of the near-twin claim
- **Art. 243 as of 1985**: (1) "The Federal Government shall have control and command of the Armed
  Forces." **(1A), inserted by the RCO 1985 (P.O. 14 of 1985, Art. 2, Sch. item 50, w.e.f. 2 March
  1985): "Without prejudice to the generality of the foregoing provision, the Supreme Command of the
  Armed Forces shall vest in the President."** (2) The President shall, subject to law, have power to
  raise and maintain the forces, grant commissions, and **(2)(c) to appoint the Chairman Joint Chiefs
  of Staff Committee, the Chief of the Army Staff, the Chief of the Naval Staff and the Chief of the
  Air Staff, and determine their salaries and allowances.**
  *Honesty point:* the explicit words "**in his discretion**" attached to service-chief appointment
  only appear later, via **LFO 2002** (the 17th Amendment 2003 then substituted "in consultation with
  the Prime Minister"). Under the 1985 instrument, service-chief appointment formally ran through Art.
  243(2)(c) subject to Art. 48(1) advice. In **practice** Zia-ul-Haq (who was simultaneously
  President and Chief of Army Staff until 1988) and then Ghulam Ishaq Khan dominated these
  appointments. **Encode the formal position and describe the practice separately — do not state that
  58(2)(b) gave the President discretionary control of the army, because it did not.**
- **Art. 244**: every member of the Armed Forces shall make the Third Schedule oath. The Third
  Schedule military oath includes a commitment to "**not engage myself in any political activities
  whatsoever**" and to uphold the Constitution.
- **Art. 245 (with (2)–(4) from the Seventh Amendment 1977, in force throughout 1985–1999)**:
  (1) the Armed Forces shall, under the directions of the Federal Government, defend Pakistan and
  "subject to law, **act in aid of civil power when called upon to do so**"; (2) "The validity of any
  direction issued by the Federal Government under clause (1) **shall not be called in question in
  any court**"; (3)–(4) High Court Art. 199 jurisdiction excluded and pending proceedings suspended in
  any area where the Armed Forces are acting in aid of civil power.
- **Art. 152-A — the National Security Council article — was OMITTED by the Eighth Amendment, s. 18.**
  This is a genuinely counter-intuitive, well-documented fact worth stating in the paper: the Eighth
  Amendment *deleted* a constitutional National Security Council while simultaneously creating
  58(2)(b) and Art. 270A. Pakistan's military guardianship was built into the presidency and the
  immunity clauses, not into a COSENA-style organ (contrast Chile 1980, Art. 95–96).
- **No constitutional coup mechanism.** There is no Pakistani equivalent of Myanmar 2008 ss. 40(c)/
  417–419. `COUP_LEGAL_MECHANISM: False`. Pakistan's 1999 collapse came from an extra-constitutional
  coup, not from a clause.
- `MILITARY_SELF_ADJUDICATION`: partial — Art. 199(3) and Art. 245(3) exclude High Court jurisdiction
  in army-deployment areas, and the Pakistan Army Act 1952 (as later amended) provides military trial
  of civilians in defined cases. Encode `True` with the Art. 245(3) citation.

### EconomicConfig / ScienceConfig
- Art. 38 Principles of Policy (promotion of social and economic well-being, **elimination of riba
  "as early as possible"**, Art. 38(f)); Art. 37 promotion of social justice; Art. 23–24 property
  rights and protection from deprivation of property.
- Art. 29–40 Principles of Policy are explicitly **non-justiciable** (Art. 30(2)): "The validity of
  an action or of a law shall not be called in question on the ground that it is not in accordance
  with the Principles of Policy." That is a real and encodable fact about how much the economic
  chapter binds.
- Art. 37(b)–(c): removal of illiteracy, free and compulsory secondary education "within minimum
  possible period", technical and professional education made generally available. No PhD-economy
  analogue; `PHD_TUITION_FREE: False`, `RESEARCHER_ROYALTY_RATE: 0.0` with a comment.
- No constitutional tax brackets → proxies.

### AmendmentConfig
- **Art. 238**: "Subject to this Part, the Constitution may be amended by Act of Majlis-e-Shoora
  (Parliament)."
- **Art. 239(1)–(3)**: a Bill may originate in either House; requires **not less than two-thirds of
  the total membership** of the originating House, then **two-thirds of the total membership** of the
  other House (with a reconsideration loop if amended).
- **Art. 239(4)**: an amendment altering the limits of a Province additionally requires
  **two-thirds of the total membership of that Provincial Assembly**.
- **Art. 239(5)**: "no amendment of the Constitution shall be called in question in any court on any
  ground whatsoever"; **Art. 239(6)**: "the powers of the Majlis-e-Shoora to amend the Constitution
  are **unlimited**" (no basic-structure limit on the face of the text). *The "unlimited" and
  non-justiciability clauses of Art. 239(5)–(6) were themselves inserted by the Eighth Amendment era
  reform package — verify the precise instrument before quoting it as Eighth-Amendment text (L2).*
- **No referendum requirement. No eternity clause.** Pakistan's amendment rule is **2/3 + 2/3 and
  nothing else** — materially easier than Thailand's compound majorities, South Korea's
  2/3 + double-50% referendum, or Myanmar's 75% + referendum. And yet: the Eighth Amendment itself
  passed both Houses, which tells you how much of Parliament was aligned with the regime.
- Encode `STANDARD_AMENDMENT_THRESHOLD: 0.667`, `ENTRENCHED_AMENDMENT_THRESHOLD: 0.667`,
  `ENTRENCHED_REQUIRES_REFERENDUM: False`, `AMENDMENT_JUDICIAL_REVIEW: False` (Art. 239(5)),
  `MILITARY_VETO_ON_AMENDMENTS: False`.
- Also encode the **Seventh Schedule** mechanism (Eighth Amendment, s. 20): a new schedule listing
  President's Orders and Ordinances that "may be amended **in the manner provided for amendment of
  the Constitution**" — i.e. Zia's own decrees were given constitutional-amendment-level
  entrenchment. There is no MFU/Myanmar analogue; it needs a comment or a flag field.

### TransitionConfig — the broadest immunity clause in the five-country set
**Art. 270A as substituted by the Eighth Amendment, s. 19** (read verbatim for this package):
- (1) The Proclamation of 5 July 1977, **all President's Orders, Ordinances, Martial Law Regulations
  and Martial Law Orders** including the Referendum Order 1984 (under which Zia became President),
  the Revival of the Constitution of 1973 Order 1985, the Constitution (Second Amendment) Order 1985
  and the Constitution (Third Amendment) Order 1985, and **all other laws made between 5 July 1977
  and the date this Article comes into force**, "are hereby affirmed, adopted and declared,
  notwithstanding any judgment of any court, to have been validly made by competent authority and
  notwithstanding anything contained in the Constitution **shall not be called in question in any
  Court on any ground whatsoever**."
- (2) All orders made, proceedings taken and acts done by any authority or person in that period
  "shall, notwithstanding any judgment of any Court, be deemed to be and **always to have been
  validly made, taken or done** and shall not be called in question in any Court on any ground
  whatsoever."
- (4) "**No suit, prosecution or other legal proceedings shall lie in any Court against any authority
  or any person**" for anything done under those powers.
- (5) All such acts "shall be **deemed to have been made, taken or done in good faith**".
- (6) Seventh Schedule entrenchment (above).

Encode: `AMNESTY_GRANTED: True`, `PRIOR_LAWS_VALID: True`, `PRIOR_ACTIONS_IMMUNE: True`,
`TRANSITION_PERIOD_YEARS: 0` (immediate), plus an explicit
`IMMUNITY_SCOPE: "retrospective_and_deemed_good_faith_no_proceedings"`. Comparative note for the
paper: Myanmar 2008 s. 445 immunises past SPDC/SLORC acts; Thailand 2017 s. 279 immunises past and
future NCPO orders; **Pakistan Art. 270A immunises eight years of martial law *and* deems it all
good-faith *and* bars any proceedings against any person.** Art. 270A is the strongest of the three.

### EmergencyConfig
- **Art. 232(1)**: if the President is satisfied that a grave emergency exists in which the security
  of Pakistan is threatened by war, external aggression, or **internal disturbance beyond the power
  of a Provincial Government to control**, he may issue a **Proclamation of Emergency**. (The
  provincial-resolution and 10-day parliamentary-approval provisos in today's text were inserted by
  the 18th Amendment in 2010 — **in 1985 the President's power was unconstrained by them**; this is a
  concrete 1985-vs-today difference that must be encoded correctly, L3.)
- Art. 232(2): Parliament may legislate on provincial matters; the Federation may direct provincial
  executives; **the Federal Government may assume all or any provincial functions and suspend
  constitutional provisions relating to any provincial body or authority** (High Courts excepted).
- Art. 233: suspension of specified fundamental rights; **Art. 233(2)**: suspension of the right to
  move any court for their enforcement.
- Art. 234: proclamation on failure of constitutional machinery in a province.
- Art. 235–237: financial emergency; validation of acts done during emergency.
- **No total-power-transfer-to-the-army clause.** `TOTAL_POWER_TRANSFER_POSSIBLE: False`,
  `LEGISLATURE_SUSPENDED_DURING_EMERGENCY: False`, `RIGHTS_UNTOUCHED: False`,
  `EMERGENCY_SUSPENDS_RIGHTS_ENFORCEMENT: True` (Art. 233(2)).
- The functional emergency mechanism in this instrument is **Art. 58(2)(b)**, not Chapter X — the
  President dissolved assemblies four times in eight years without ever proclaiming an emergency.
  Model the dissolution power as the active failure channel.

### ROEConfig / PsychConfig / CryptoJusticeConfig / NorthStarConfig
No Pakistani referent for Crypto-Justice or psychological screening → absent pattern.
For `NorthStarConfig`, the Objectives Resolution (Annex, made substantive by Art. 2A) and the
Principles of Policy (Art. 29–40, non-justiciable per Art. 30(2)) are the stated national objectives.
`PROGRESS_METRIC` is a modelling choice.

---

## 2. Real validation / backtesting data

### 2.1 Transparency International CPI
Access method as in the South Korea package. **CPI begins in 1995 — i.e. in year 10 of a 14-year
instrument.** There is no CPI observation for 1985–1994. Do not interpolate.

Pakistan, 1995–2011 (0–10 scale; not comparable across years by TI's own statement):

| 1995 | 1996 | 1997 | 1998 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.25 | **1.0** | 2.53 | 2.7 | 2.2 | — | 2.3 | 2.6 | 2.5 | 2.1 | 2.1 | 2.2 | 2.4 | 2.5 | 2.4 | 2.3 | 2.5 |

Pakistan, 2012–2025 (0–100 scale, TI workbook):

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 27 | 28 | 29 | 30 | 32 | 32 | 33 | 32 | 31 | 28 | 27 | 29 | 27 | 28 |

Two data notes:
- **1996 = 1.00, rank 53 of 54** is *not* a file error. It is the genuine reported value in TI's CPI
  1996 (54 countries); Pakistan was second from bottom. I checked this specifically because it looks
  like an artefact.
- **2000 is missing** — Pakistan was not included in CPI 2000. Leave it null.
- **Pakistan 2008 is WRONG in `CPI-Archive-2008-2`-adjacent archive variants**: the defective
  `CPI-Archive-2008.csv` gives 3.4 / rank 85 (which is Panama's row). The correct value from the
  page-linked file is **2.5 / rank 134**. The 2010 rank also differs between TI's two files (143 vs
  146). Use the page-linked CSVs.

### 2.2 World Bank Worldwide Governance Indicators
Source: WGI 2023 Update, 1996–2022 (`wgidataset.xlsx`, www.govindicators.org). Point estimates
(−2.5…+2.5):

| Indicator | 1996 | 1998 | 2000 | 2002 | 2005 | 2010 | 2015 | 2020 | 2022 |
|---|---|---|---|---|---|---|---|---|---|
| Control of Corruption | −1.22 | −1.08 | −0.89 | −0.96 | −1.06 | −1.09 | −0.83 | −0.86 | −0.80 |
| Political Stability / No Violence | −1.13 | −1.12 | −1.10 | −1.64 | −1.75 | −2.68 | −2.47 | −1.79 | −1.90 |
| Voice & Accountability | −0.60 | −0.54 | −1.22 | −1.11 | −0.98 | −0.80 | −0.72 | −0.88 | −0.86 |
| Government Effectiveness | −0.62 | −0.49 | −0.49 | −0.55 | −0.46 | −0.78 | −0.71 | −0.57 | −0.62 |
| Rule of Law | −0.63 | −0.79 | −1.00 | −0.93 | −0.89 | −0.74 | −0.78 | −0.71 | −0.67 |

Note the Voice & Accountability step from −0.54 (1998) to −1.22 (2000) — the 1999 coup. WGI's 1996
and 1998 readings are the only two that fall inside the 58(2)(b) era, and both are already deeply
negative.

### 2.3 V-Dem (v16, 2026) — the only source covering 1973–1999
Access method and citation guidance identical to the South Korea package.
`political-corruption-index` runs 0 = clean → 1 = highly corrupt.

Pakistan, V-Dem annual, 1985–2000 (the instrument's full life plus the coup year):

| year | 1985 | 1986 | 1987 | 1988 | 1989 | 1990 | 1991 | 1992 | 1993 | 1994 | 1995 | 1996 | 1997 | 1998 | 1999 | 2000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .157 | .171 | .171 | .214 | .371 | .372 | .367 | .367 | .368 | .370 | .370 | .370 | .386 | .391 | **.340** | **.205** |
| liberal dem. | .102 | .113 | .115 | .127 | .202 | .198 | .196 | .196 | .201 | .201 | .201 | .201 | .196 | .199 | .167 | .094 |
| **pol. corruption** | **.637** | .656 | .656 | .731 | .804 | **.831** | .831 | .831 | .831 | .831 | .831 | .831 | .831 | .831 | .822 | .752 |
| rule of law | .329 | .329 | .335 | .271 | .271 | .249 | .249 | .249 | .261 | .260 | .260 | .260 | .230 | .228 | .204 | .258 |
| judicial constr. | .392 | .392 | .415 | .415 | .456 | .456 | .456 | .456 | .489 | .485 | .485 | .485 | .412 | .412 | .364 | .433 |
| legislative constr. | .440 | .440 | .440 | .440 | .488 | .418 | .418 | .418 | .418 | .418 | .418 | .418 | .418 | .418 | .443 | — |

Longer context: 1973 pol. corruption .778, 1977 .778; 2008 .929, 2018 .902, 2024 .818.

**This is the cleanest near-twin signature in the whole project.** Political corruption rose from
**.637 at year zero (1985) to .831 by 1990** and stayed pinned there for the rest of the instrument's
life — a monotonic +0.194 rise over five years, then saturation, then constitutional collapse. Rule of
law fell .329 → .204. Judicial constraints fell .489 (1993) → .364 (1999). That is a corruption-driven
institutional-decay trajectory of exactly the shape Ka-Nova's Scenario C produces.

### 2.4 Coup / dissolution / constitutional-collapse event history
Primary dataset: **Powell & Thyne V2026.08.29**
(`https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv`). Pakistan has **four coded
events, all successful, no failed attempts**:

| Date | Outcome |
|---|---|
| 1958-10-27 | **successful** (Ayub Khan) |
| 1971-12-19 | **successful** |
| 1977-07-05 | **successful** (Zia; the Proclamation later validated by Art. 270A) |
| **1999-10-12** | **successful** (Musharraf — destroys the instrument encoded here) |

**The functional failure mode of this instrument, however, is not the coup — it is Art. 58(2)(b)
dissolution.** Four dissolutions in eight years:

| Date | President | Government dismissed | Judicial outcome |
|---|---|---|---|
| **29 May 1988** | Zia-ul-Haq | PM Muhammad Khan Junejo | Dissolution held unlawful but elections allowed to proceed (Haji Saifullah case) |
| **6 August 1990** | Ghulam Ishaq Khan | PM Benazir Bhutto (1st term) | Upheld |
| **18 April 1993** | Ghulam Ishaq Khan | PM Nawaz Sharif (1st term) | **Assembly restored by the Supreme Court on 26 May 1993**; Assembly then dissolved on the PM's own advice 18 July 1993 |
| **5 November 1996** | Farooq Ahmad Khan Leghari | PM Benazir Bhutto (2nd term) | Upheld |

Then: **Thirteenth Amendment, April 1997** — Art. 58(2)(b) omitted (Nawaz Sharif's two-thirds
majority). **12 October 1999** — Musharraf coup; constitution held in abeyance under a Provisional
Constitutional Order.

Dates for the four dissolutions are from the National Assembly of Pakistan's own published history
(na.gov.pk/en/content.php?id=75) as reported through the Article 58(2)(b) literature; see limitation
L4.

**Survival-time arithmetic for the manuscript** (my computation, state it as such):
| Measured from | To | Elapsed |
|---|---|---|
| RCO, 2 Mar 1985 | Musharraf coup, 12 Oct 1999 | **14.61 years** |
| Eighth Amendment assent, 9 Nov 1985 | Musharraf coup, 12 Oct 1999 | **13.92 years** |
| Eighth Amendment assent, 9 Nov 1985 | 13th Amendment repeal of 58(2)(b), April 1997 | **11.4 years** |
| Eighth Amendment assent, 9 Nov 1985 | first 58(2)(b) dissolution, 29 May 1988 | **2.55 years** |

Compare Myanmar: 2008 Constitution ratified 29 May 2008 → coup 1 Feb 2021 = **12.68 years**; in force
31 Jan 2011 → 1 Feb 2021 = **10.01 years**. Compare Ka-Nova Scenario C: mean failure year **15.6**.

### 2.5 Survey-based trust in government — the weakest of the five countries
| Source | Pakistan coverage | Notes |
|---|---|---|
| **World Values Survey** | Wave 3 (1995-98, fieldwork 1997), Wave 4 (1999-2004, fieldwork 2001), Wave 6 (2010-14, fieldwork 2012); listed for Wave 8 (2024-26). **Not in waves 1, 2, 5, or 7.** | `E069_11` confidence in government, `E069_07` parliament, `E069_10` armed forces. WVS registration required |
| **Asian Barometer** | **Not covered** — ABS is East/Southeast Asia | — |
| **Pew Global Attitudes** | Pakistan surveyed in most years 2002–2015, then intermittently | Institutional-confidence and military-confidence items; pewresearch.org, free |
| **Gallup Pakistan / Gilani Research Foundation** | Long-running national polling | Commercial; methodology documentation is thinner than WVS |
| **PILDAT Public Opinion on Quality of Democracy** | Periodic since ~2010 | pildat.org |
| **World Bank WGI Voice & Accountability** | 1996–2022 | Best continuous proxy |
| **V-Dem** | 1789–2025 | Expert-coded |

**There is no survey-based trust observation for 1985–1996.** The earliest WVS reading (1997
fieldwork) falls in year 12 of a 14-year instrument. Any `YEAR_ZERO_TRUST` for Pakistan is therefore
necessarily derived, not observed — state this plainly. See L5.

### 2.6 Recommended year-zero calibration (inference, not a source)
| Field | Proposed value | Basis |
|---|---|---|
| `YEAR_ZERO_CORRUPTION` | **0.637** | V-Dem v16 political corruption index, Pakistan, **1985** — a real observation at the exact year zero, which is more than can be said for `C`'s 0.72 |
| `YEAR_ZERO_TRUST` | **derived only** | No survey exists for 1985. Either use WVS 1997 (`E069_11`) and label it as year-12, or derive from V-Dem/WGI and say so |
| `YEAR_ZERO_COUP_RISK` | **0.086** as a historical base rate | 3 successful coups in the 35 years 1950–1985 ≈ 0.086/yr (my computation from Powell & Thyne); a higher number is defensible if you weight the 1977 coup's recency |
| `YEAR_ZERO_STABILITY` | **derived only** | WGI begins 1996 (−1.13); no 1985 observation |
| `YEAR_ZERO_GINI` | Pakistan HIES/World Bank, earliest usable ~1987 | Cite the exact survey year |

---

## 3. Country-accurate elite role titles for the LLM chain

`chain_type: "military"`. Real titles for the 1985–1997 configuration, in the order power actually
flowed:

| Slot | Title | Basis |
|---|---|---|
| 1 | **President of the Islamic Republic of Pakistan** | Art. 41; Supreme Command of the Armed Forces (Art. 243(1A), RCO 1985); discretionary dissolution (Art. 58(2)(b)) |
| 2 | **Chief of Army Staff** | Art. 243(2)(c). Note: 1985–1988 the President *was* the COAS (Zia held both). Model the dual-hatting explicitly if the engine allows, or document it. |
| 3 | **Prime Minister** | Art. 91; holds office "during the pleasure of the President" (Art. 91(5), 8th Amdt s. 10) |
| 4 | **Speaker of the National Assembly** | Art. 53 |
| 5 | **Chairman of the Senate** | Art. 60; first in line to act as President (Art. 49) |
| 6 | **Chief Justice of Pakistan** | Art. 177; chairs the Supreme Judicial Council (Art. 209) |
| 7 | **Chief Justice of the Federal Shariat Court** | Art. 203C; presidentially appointed parallel apex court |
| 8 (if the chain supports 8) | **Auditor-General of Pakistan** | Art. 168–171 — the only constitutional integrity organ |

Deliberately **not** included: a National Security Council chair. Art. 152-A (NSC) was **omitted by
the Eighth Amendment, s. 18**, so a COSENA-style organ did not exist under this instrument. Including
one would import Chile's structure into Pakistan's.

Historical cast for prompt flavour, if named figures are wanted (all documented):
President/COAS **Zia-ul-Haq** (1978–88), PM **Muhammad Khan Junejo** (1985–88), President **Ghulam
Ishaq Khan** (1988–93), PMs **Benazir Bhutto** (1988–90, 1993–96) and **Nawaz Sharif** (1990–93,
1997–99), President **Farooq Leghari** (1993–97), COAS **Jehangir Karamat** then **Pervez Musharraf**.

---

## 4. Honest sourcing limitations

**L1 — 1985-era seat counts are from secondary sources.** The National Assembly's 237 seats
(207 + 20 + 10) and the Senate's 87 members are reported by the Inter-Parliamentary Union's archived
1985 Pakistan election report (`archive.ipu.org/parline-e/reports/arc/PAKISTAN_1985_E.PDF`) and the
National Assembly's own history page. I confirmed from the pakistani.org footnotes that the RCO 1985
*did* substitute the Senate figure for the 1973 original "sixty-three" and *did* extend the Senate
term from four to six years, but I could not extract the substituted numeral itself from the footnote
chain. **Verify 237 and 87 against the IPU PDF or the 1985 Gazette before they appear in print.**
Same caveat for the 1985 Supreme Court bench strength.

**L2 — Art. 239(5)–(6) attribution.** The "unlimited amendment power" and
"no-court-shall-question-an-amendment" clauses are in the current text with amendment footnotes I did
not fully resolve. They are commonly attributed to the Eighth Amendment / RCO package but may trace
to the Fifth or Eighth Amendment or to a later instrument. **Verify the instrument before stating
"the Eighth Amendment inserted Art. 239(5)".** The Eighth Amendment text I read in full does not
contain an Art. 239 provision.

**L3 — The current Art. 232 text is NOT the 1985 text.** Today's Art. 232(1) carries provincial-
resolution and 10-day parliamentary-approval provisos inserted by the Eighteenth Amendment (2010).
Under the 1985 instrument the President's emergency-proclamation power had no such checks. If the
engineer encodes from a current text without checking footnotes, Pakistan's emergency parameters will
be wrong in the direction of *understating* presidential power. Same risk applies to Art. 243 (18th
and 27th Amendment changes), Art. 51/59 (many later changes), Art. 175A/209 (18th, 19th, 26th and
27th Amendment changes) and Art. 6(2A) (18th Amendment).
**Use pakistani.org's footnoted text, not a clean consolidated text.**

**L4 — Dissolution dates.** The four 58(2)(b) dissolution dates (29 May 1988, 6 Aug 1990, 18 Apr
1993, 5 Nov 1996), the 26 May 1993 Supreme Court restoration and the 18 Jul 1993 advice-based
dissolution come from the National Assembly's published history as relayed through secondary
accounts. They are consistent across sources but I did not read a primary gazette notification for
each. Verify before publication; these dates are load-bearing if the paper uses the survival-time
arithmetic.

**L5 — No trust-survey data for 1985–1996.** Earliest WVS Pakistan fieldwork is 1997. Any Pakistani
year-zero trust value is a derivation. Do not present it as observed.

**L6 — Powell & Thyne codes four Pakistani coups and no failed attempts.** That is almost certainly an
under-count of attempts (e.g. the 1973 Attock conspiracy, the 1995 Zahirul Islam Abbasi plot). If the
paper uses coup *base rates*, note the coding boundary — attempted-coup under-coding biases the base
rate downward.

**L7 — The 27th Amendment (November 2025) has radically restructured Pakistan's judiciary** (a new
Federal Constitutional Court under Articles 175B–175L, abolition of the Chairman JCSC post effective
27 Nov 2025, a new "Chief of the Defence Forces" office). None of this is relevant to the 1985
instrument, but it means anyone reading a current Pakistani constitution will see a completely
different judiciary. Guard against contamination.

**L8 — Config categories with no Pakistani referent:** `CryptoJusticeConfig`, `PsychConfig`, MFU's
IIG academy/partnership machinery, all `ETHNIC_*` fields (Pakistan's constitutional minority
structure is religious — 10 reserved non-Muslim seats — not ethnic). Values placed there are
modelling choices; comment them.

---

## 5. Flags for Kaung — decide before the engineer encodes

**F1 — Pakistan, not Thailand or Chile, is the scenario that validates the 15.6-year headline. Build
the paper around it.** `.claude/memory.md` §6 locked finding 5 anchors Scenario C's mean failure year
of **15.6** against Myanmar's "~13-year historical timeline". Pakistan supplies a **second,
fully independent, military-guardianship anchor**:
- Pakistan 1973+8th Amendment: **14.6 years** from the RCO (2 Mar 1985) to constitutional collapse by
  coup (12 Oct 1999); **13.9 years** from the Eighth Amendment's assent.
- Myanmar 2008: **12.7 years** from ratification to coup (10.0 from entry into force).
- Ka-Nova Scenario C simulated mean: **15.6 years**.
Two independent real military constitutions collapsing at 12.7 and 14.6 years, bracketing a simulated
15.6, is a genuinely strong backtest — far stronger than a single-case anchor, and it is the single
most valuable thing in this research package. Also note Pakistan's corruption trajectory (V-Dem .637
→ .831 in five years, then saturation) is the right *shape* as well as the right *duration*.

**F2 — Fix the Myanmar anchor's precision while you are at it.** "~13 years" is defensible for
2008→2021 (12.68 years from the 29 May 2008 referendum) but **not** for the operative instrument
(31 Jan 2011 → 1 Feb 2021 = 10.01 years). A reviewer can and will ask which date you mean. State both
and pick one convention, then apply the same convention to Pakistan (adoption-date vs
entry-into-force) so the comparison is apples-to-apples. Using adoption dates throughout gives
Myanmar 12.7 / Pakistan 13.9–14.6 vs simulated 15.6 — a clean, consistent, defensible table.

**F3 — The 58(2)(b) mechanism has no representation in the current schema, and it is the whole point
of choosing this instrument.** The schema can express coup probability and emergency power transfer.
It cannot express "the head of state may dissolve the legislature at discretion, the act is
non-justiciable, and this happens roughly every two years without ever ending the constitutional
order." Pakistan's failure mode was **serial constitutional decapitation, not a single collapse
event** — four governments removed in eight years, every one of them before completing a term. If
`PK` is encoded with only a coup-probability channel, the simulation will produce one terminal event
at ~year 14 and miss the mechanism entirely. Recommend a new
`EXECUTIVE_DISSOLUTION_*` channel (discretionary trigger, non-justiciability, expected frequency,
trust penalty per dissolution) — it generalises usefully and would also let the paper report a
*mechanism-level* match, not just a duration match. This is a real engine-design request for
`senior-simulation-engineer`, and it is the highest-value one in this research package.

**F4 — Be precise about what the Eighth Amendment did and did not do.** Three claims commonly made
in the secondary literature that the primary text does **not** support:
1. "The Eighth Amendment inserted Article 2A" — **no**, the RCO 1985 (P.O. 14 of 1985) did, on 2
   March 1985. The Eighth Amendment affirmed it via Art. 270A.
2. "The Eighth Amendment created a National Security Council" — **no**, Eighth Amendment s. 18
   **omitted** Article 152-A.
3. "The Eighth Amendment gave the President discretionary control of service-chief appointments" —
   **no**, "in his discretion" entered Art. 243 via LFO 2002. In 1985 the RCO vested *Supreme
   Command* in the President (Art. 243(1A)) and Art. 243(2)(c) gave him the appointment power subject
   to Art. 48(1) advice; the practical dominance is a historical fact, not a textual one.
A reviewer who knows Pakistani constitutional law will check all three. Getting them right is cheap
credibility; getting them wrong is expensive.

**F5 — Pakistan is a real federation, so do not reuse MFU's resource split.** Art. 160–161 (National
Finance Commission; well-head royalties to the producing province) is a real constitutional
revenue-sharing rule. Either source the 1985-era NFC award percentages or label the split a proxy.

**F6 — Year-zero calibration traceability.** See the South Korea package §5 F4. Pakistan is the one
scenario where `YEAR_ZERO_CORRUPTION` can be taken from a **real observation at the exact year zero**
(V-Dem 1985 = 0.637). Use that, and use the same dataset-year-variable convention for all seven
scenarios so the calibration table in the reproducibility package is uniform.

---

## Schema warning

Same as the other packages: `config/constitution_2008.py` is **missing ≥16 field names the live
engine reads**. **Use `config/constitution.py` as the field-name contract.** A separate engine-level
issue (`self.CONSTITUTION` assigned at `model_phase3.py:164/167` but never read; `agents/official.py`,
`agents/citizen.py`, `feedback/loops.py` and `institutions/chambers.py` all import MFU's
`CONSTITUTION` at module level unconditionally) has been reported to the parent agent — it determines
whether any of these parameters affect the simulation at all.
