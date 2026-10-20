# West Germany 1949 Basic Law (Grundgesetz) — Encoding Research Package

Researcher's workspace document (not code). Prepared by `senior-researcher`, 2026-10-20.
Target output: `config/constitution_germany.py` → registry key `DE`, `chain_type: "civilian"`.

Intended role in the paper: **independently-sourced, externally-validated success case** — an
Allied-supervised constitution with no self-design bias, to be compared against Scenario A (MFU).
Pulled forward from the originally-separate Paper 2 per `.claude/memory.md` §4.

**Read §0 and §5 flag F1 first.** The phrase "Germany 1949" hides a real and consequential ambiguity:
the 1949 text as enacted had **no armed forces and no emergency constitution at all.** Encoding
"Germany 1949" without resolving that will produce either an empty `MilitaryConfig`/`EmergencyConfig`
or a mislabelled instrument.

---

## 0. Instrument definition — resolve this before anything else

| Item | Value | Source |
|---|---|---|
| Instrument | Grundgesetz für die Bundesrepublik Deutschland | Official English translation, Federal Ministry of Justice, `https://www.gesetze-im-internet.de/englisch_gg/englisch_gg.html` (read in full for this package) |
| Adopted | **8 May 1949** by the Parliamentary Council (Parlamentarischer Rat), Bonn | German History Documents (germanhistorydocs.org); Wikipedia "Basic Law for the Federal Republic of Germany" |
| Ratified | **16–22 May 1949** by the legislatures of more than two-thirds of the participating Länder; **Bavaria's Landtag rejected it** (but accepted its binding force) | Same |
| Promulgated | **23 May 1949**; in force from 24 May 1949 | Same |
| Amendments since | **around 70** | deutschland.de ("75 years of the Basic Law"); see limitation L1 for the exact count |
| Simulation year-zero | **1949** | — |
| Real observation window | 1949 → 1999 is **exactly 50 years** — the only scenario in the project whose real history matches Ka-Nova's simulated horizon one-for-one | — |

### The 1949-as-enacted problem

Four of the config categories the schema cares most about **did not exist in the 1949 text**:

| Feature | Added when | Instrument |
|---|---|---|
| **Armed forces** (Art. 87a) and **command authority** (Art. 65a) | **1956** | 7th amendment — the *Wehrverfassung*. In 1949 West Germany had **no army**, and the Basic Law contained no military provisions whatsoever |
| Bundestag Defence Committee / Parliamentary Commissioner for the Armed Forces (Art. 45a, 45b) | 1956 | 7th amendment |
| **State of defence / state of tension** (Art. 115a–115l, 80a), **Joint Committee** (Art. 53a), **internal emergency** (Art. 91), **right of resistance** (Art. 20(4)), armed-forces domestic support (Art. 87a(3)–(4)) | **1968** | 17th amendment — the *Notstandsverfassung*. In 1949 the Basic Law had **no emergency chapter at all** (a deliberate reaction to Weimar Art. 48) |
| Federal Constitutional Court detail: **16 justices, two senates of eight, 12-year terms, age 68, no re-election** (Art. 93(2)–(3)) | **December 2024** | The FCC-resilience amendment: Bundestag 19 Dec 2024 (**600 of 733** votes), Bundesrat 20 Dec 2024. Before this, these rules were in the *statutory* Bundesverfassungsgerichtsgesetz, not the Basic Law |

Also note: Art. 20a (protection of the natural foundations of life) 1994; Art. 87a(1a) (€100bn special
defence fund) 2022; Art. 143 (unification derogations) 1990; Art. 23 rewritten for the EU 1992.

**Recommendation.** Encode the **current consolidated Grundgesetz** and label the scenario honestly
as `"1949_basic_law_as_amended"` (or, if you want the historical instrument,
`"1949_basic_law_as_amended_through_1968"` — which captures the *Wehrverfassung* and
*Notstandsverfassung* and therefore gives you a non-empty military and emergency configuration while
excluding the 1990s/2020s changes). **Do not label it "Germany 1949" while encoding post-1956
military articles** — an adversarial reviewer who knows German constitutional history will catch it,
and it is an unnecessary own goal on a paper whose central vulnerability is already "are your
comparators honest?". Whichever you choose, put the "as amended through" date in
`SimulationConfig.CONSTITUTIONAL_FRAMEWORK` and in the manuscript table.

A clean third option, if Kaung wants the strongest version: **encode the 1949-as-enacted text and
state that `MilitaryConfig` is structurally empty because the 1949 Basic Law created a state with no
army and no emergency powers.** That is a genuinely striking comparative finding in its own right —
the most successful constitution in the set began by *omitting* the two chapters that Myanmar 2008
uses to legalise a coup.

---

## 1. Real constitutional structure, mapped to the config schema

All article numbers and quotations below are verbatim from the official English translation at
gesetze-im-internet.de, read in full for this package. Where a provision post-dates 1949, that is
marked.

### FoundationalConfig
- **Art. 20(1)**: "The Federal Republic of Germany is a democratic and social **federal** state."
  Art. 20(2): all state authority derives from the people, exercised through elections and other
  votes and through specific legislative, executive and judicial bodies. Art. 20(3): the legislature
  is bound by the constitutional order, the executive and judiciary by law and justice.
- **Art. 20(4)** (*1968*): "All Germans shall have the right to **resist** any person seeking to
  abolish this constitutional order if no other remedy is available."
- **Art. 1(1)**: "Human dignity shall be inviolable." Art. 1(3): the basic rights bind all three
  branches as directly applicable law.
- Art. 22(1): Berlin is the capital (as amended; Bonn in 1949). Art. 22(2): the federal flag is
  black, red and gold.
- Art. 116 citizenship; nationality law is statutory (StAG). Naturalisation residence requirements
  are statutory, **not** constitutional — any `NATURALIZATION_YEARS` value is a modelling choice
  (currently 5 years under the 2024 StAG reform; 8 before that; 15 under the pre-2000 regime).
- `STATE_COUNT`: **16** Länder today; **11** in 1949 (plus West Berlin's special status); 10 after
  the 1952 Baden-Württemberg merger; 16 from 1990. **Pick a number and comment the date.** For
  comparability with the other scenarios' 14, note that Germany's Land count is one of the few
  genuinely constitutional federal numbers in the set.
- No constitutionally recognised ethnic-group structure at federal level → all `ETHNIC_*` fields are
  inert for `DE`.

### RightsConfig — the strongest rights configuration in the set
- Arts. 1–19 "Basic Rights", directly binding (Art. 1(3)).
- **Art. 19(2): "In no case may the essence of a basic right be affected."** — an essence guarantee
  stronger than South Korea's Art. 37(2) and with no Myanmar/Thailand/Pakistan/Chile analogue.
- Art. 19(4): guaranteed recourse to the courts against any act of public authority.
- Art. 18: forfeiture of specified rights by persons who abuse them to combat the free democratic
  basic order — **decided by the Federal Constitutional Court only**.
- Art. 10(2): restrictions on privacy of correspondence may provide that the person is not informed
  and that judicial recourse is replaced by review by parliamentary-appointed agencies (the
  G10-Kommission) — the one notable rights carve-out.
- Art. 79(3) eternity clause protects the Art. 1 and Art. 20 principles (see AmendmentConfig).
- **Encode `RIGHTS_SUSPENDABLE: False`.** There is no provision permitting general suspension of
  basic rights. Even under a state of defence (Art. 115c(2)) deprivations of liberty are extended
  only within tightly specified limits and Art. 19(2)/79(3) continue to bind. This makes `DE` the
  only scenario other than MFU with `RIGHTS_SUSPENDABLE: False` — and unlike MFU, **Germany's value
  is sourced from an external, Allied-supervised text that Kaung did not design.** That is precisely
  why this scenario is worth the compute. `EMERGENCY_TOUCHES_RIGHTS: False`,
  `RIGHTS_ABSOLUTE_COUNT`: at minimum 2 (Art. 1 dignity, Art. 20 principles, via Art. 79(3)); a
  defensible higher count can be argued from Art. 19(2) applying to all of Arts. 1–19.
- **Art. 4(3)**: "No person shall be compelled against his conscience to render military service
  involving the use of arms" — constitutional conscientious objection. Military service itself was
  statutory (conscription 1956–2011, suspended since 1 July 2011). `NATIONAL_SERVICE_MANDATORY`: not
  a constitutional mandate; comment it.

### ExecutiveConfig — a true ceremonial-president / executive-chancellor split
This is the one scenario that maps onto MFU's `PRESIDENT_*`/`CHANCELLOR_*` field design **without
distortion**, because MFU's design is itself modelled on this pattern.
- **Art. 54(1)–(2)**: "The Federal President shall be elected by the **Federal Convention** without
  debate. Any German who is entitled to vote in Bundestag elections and has attained the age of
  **forty** may be elected… The term of office of the Federal President shall be **five years**.
  **Re-election for a consecutive term shall be permitted only once.**"
- **Art. 54(3)**: the Federal Convention consists of the Members of the Bundestag **and an equal
  number of members elected by the Land parliamentary assemblies** by proportional representation.
  **Art. 54(6)**: absolute majority of the Convention; if no candidate reaches it after two ballots,
  a plurality suffices on the third.
- Art. 58: presidential orders and instructions require **countersignature by the Chancellor or the
  competent Minister** (the ceremonial-office guarantee).
- Art. 61: presidential impeachment before the Federal Constitutional Court on application of **one
  quarter** of the Bundestag or one quarter of the Bundesrat votes, decided by **two thirds** of
  either body's members/votes.
- **Art. 63(1)–(2)**: "The Federal Chancellor shall be elected by the Bundestag without debate on
  the proposal of the Federal President… The person who receives the votes of a **majority of the
  Members of the Bundestag** shall be elected." (3): if the President's nominee fails, the Bundestag
  may elect within 14 days by absolute majority. (4): otherwise a new ballot in which a plurality
  elects; if the person elected has an absolute majority the President **must** appoint within seven
  days; if not, the President must either appoint or **dissolve** the Bundestag.
- Art. 64(1): Federal Ministers appointed and dismissed by the President **upon the proposal of the
  Chancellor**. Art. 65: the Chancellor determines policy guidelines (*Richtlinienkompetenz*) and
  bears responsibility for them. Art. 66: incompatibility with other salaried office or trade.
- **Art. 67(1) — the constructive vote of no confidence**: "The Bundestag may express its lack of
  confidence in the Federal Chancellor **only by electing a successor** by the vote of a majority of
  its Members and requesting the Federal President to dismiss the Federal Chancellor. The Federal
  President must comply with the request and appoint the person elected." Art. 67(2): 48 hours
  between motion and election.
- **Art. 68(1)**: if a confidence motion fails to win an absolute majority, the President may
  dissolve the Bundestag within 21 days on the Chancellor's proposal; the right lapses as soon as the
  Bundestag elects another Chancellor by absolute majority.
- Art. 69: deputy Chancellor; the Chancellor's and Ministers' tenure ends when a new Bundestag
  convenes.

Mapping: `PRESIDENT_ROLE: "ceremonial_head_of_state"`, `PRESIDENT_EXECUTIVE_POWER: False`,
`PRESIDENT_ELECTION: "federal_convention_bundestag_plus_equal_land_delegates"`, `PRESIDENT_TERM: 5`,
`PRESIDENT_MAX_TERMS: 2` (one consecutive re-election), `PRESIDENT_REMOVAL_CHAMBERS: 1` (either body
at 1/4 to apply, 2/3 to decide, **adjudicated by the Constitutional Court, not by the chambers** —
note this difference from MFU), `CHANCELLOR_ROLE: "executive_head_of_government"`,
`CHANCELLOR_ELECTION: "bundestag_absolute_majority_on_presidential_proposal"`, `CHANCELLOR_TERM: 4`
(tied to the Bundestag term, not a fixed personal term), **`CHANCELLOR_MAX_TERMS: 0` = unlimited**
(Germany has no chancellor term limit — Adenauer 14 years, Kohl 16, Merkel 16; this is a real and
important divergence from MFU's single-term design),
`CHANCELLOR_DISMISSAL_VETO`: effectively true, because Art. 67 requires a **constructive** majority.
`MINISTER_COUNT`: not fixed by the Basic Law — a modelling choice (currently 15 + Chancellor).

The **constructive vote of no confidence** is the single most distinctive mechanism here and has no
counterpart in any other scenario. It has been attempted twice in 76 years and succeeded once
(1972 against Brandt, failed; 1982 against Schmidt, succeeded — Kohl). If the schema cannot express
"no-confidence requires simultaneous election of a successor", add a
`NO_CONFIDENCE_REQUIRES_SUCCESSOR: True` flag — it is a cheap field and it encodes a real
stability-producing mechanism.

### ChamberConfig
- **Art. 38(1)**: Bundestag members "elected in general, direct, free, equal and secret elections…
  representatives of the whole people, not bound by orders or instructions and responsible only to
  their conscience." Art. 38(2): voting age 18. **Art. 38(3): details regulated by federal law** —
  so the mixed-member proportional system, the 5% threshold and the basic-mandate clause are
  **statutory** (Bundeswahlgesetz), not constitutional. Comment this; it matters because the 5%
  threshold is often described as constitutional and is not.
- **Art. 39(1)**: four-year term; new elections no sooner than 46 and no later than 48 months after
  the term begins; if dissolved, elections within 60 days.
- Art. 42(2): Bundestag decisions require a majority of votes cast unless the Basic Law provides
  otherwise.
- **Art. 50**: "The Länder shall participate through the **Bundesrat** in the legislation and
  administration of the Federation" and in EU affairs.
- **Art. 51(1)**: the Bundesrat consists of **members of the Land governments**, which appoint and
  recall them — not elected, not a senate. **Art. 51(2)**: each Land has **at least three votes**;
  more than two million inhabitants → four; more than six million → five; more than seven million →
  six. **Art. 51(3)**: a Land's votes may be cast **only as a unit**. Today: 69 votes total.
- Art. 52(3): Bundesrat decisions require at least a majority of its votes; Art. 52(1) one-year
  presidency.
- Arts. 70–74: distribution of legislative powers (exclusive federal, concurrent, Land residual);
  Art. 72 the *Bedürfnisklausel*; Art. 77 the Mediation Committee (*Vermittlungsausschuss*) between
  the two chambers; Art. 81 legislative emergency.
- **Zero reserved military seats; zero appointed seats; zero designated seats.** `DE` and `SK` are the
  two scenarios with a wholly elected/accountable legislature. `MILITARY_SEAT_PERCENTAGE: 0.0`.
- There is no Analysis-Council analogue. The functional analogue is the **Bundesverfassungsgericht** —
  map `ANALYSIS_THRESHOLD` to its senate majority (5 of 8 = 0.625) and document the mapping, or to
  the 2/3 required for Art. 18/21(2) forfeiture and party-ban decisions (BVerfGG §15(4)).

### JudiciaryConfig
- **Art. 92**: "The judicial power shall be vested in the judges; it shall be exercised by the
  **Federal Constitutional Court**, by the federal courts provided for in this Basic Law and by the
  courts of the Länder."
- **Art. 93(1)** (*as amended Dec 2024*): "The Federal Constitutional Court shall be a federal court
  of justice which is **autonomous and independent of all other constitutional organs**."
- **Art. 93(2)** (*Dec 2024*): "…shall consist of federal judges and other members; it shall be
  divided into **two Senates**. **Eight Justices shall be elected to each Senate, half by the
  Bundestag and half by the Bundesrat**; they may not be members of the Bundestag, of the Bundesrat,
  of the Federal Government or of any of the corresponding organs of a Land." It also contains an
  **anti-blockade substitution rule**: federal law may provide for the other electing organ to
  exercise the right of election if a successor is not elected within a specified time limit.
- **Art. 93(3)** (*Dec 2024*): "The term of office of members of the Federal Constitutional Court
  shall be **twelve years** but shall not extend beyond the end of the month in which they reach the
  age of **sixty-eight**. Upon expiry of their term of office, Justices shall continue to carry out
  their official functions until a successor is appointed. **Immediate or subsequent re-election of
  Justices shall not be possible.**"
  Election itself requires a **two-thirds majority** in the electing body under BVerfGG §6/§7 —
  statutory, forcing cross-party consensus.
- **Art. 94(1)**: jurisdiction — organ disputes; abstract review of federal/Land law on application of
  the Federal Government, a Land government or **one quarter of the Members of the Bundestag**;
  Art. 72(2) disputes; federal-Land disputes; constitutional complaints; concrete review on judicial
  referral; **Art. 21(4)** party unconstitutionality; **Art. 18** rights forfeiture; **Art. 61**
  presidential impeachment; **Art. 98(2)** judicial impeachment.
- Art. 97(1): "Judges shall be independent and subject only to the law." Art. 97(2): tenure
  protection.
- **Art. 101(1): "Extraordinary courts shall be inadmissible."** Art. 96(2): military criminal courts
  may be established for the armed forces **only** in a state of defence or for members serving
  abroad/on warships, and they belong to the Federal Minister of Justice's portfolio with civilian
  judges. **There is no standing military-justice system with jurisdiction over civilians.**
  `MILITARY_JUSTICE_FINAL: False`, `CIVILIAN_COURT_OVERRIDE_MILITARY: True`.
- `JUDGE_COUNT: 16` (or 8 per senate — **say which**), `COURT_TERM_YEARS: 12`,
  `RULING_THRESHOLD: 5` of 8 (senate majority), `COURT_INDEPENDENCE: True` sourced to Art. 93(1),
  97(1), 101(1).
- **Militant democracy / party bans** (real, exercised): SRP banned 1952, KPD banned 1956 — both by
  the Federal Constitutional Court under Art. 21(2); NPD ban applications **rejected** in 2003 and
  2017; NPD/Die Heimat excluded from state financing in 2024 under Art. 21(3). This is a real,
  documented constitutional-defence mechanism with an outcome record — useful validation material.

### IIGConfig (anti-corruption body)
Germany has **no dedicated constitutional anti-corruption commission**. The constitutional integrity
organ is:
- **Art. 114(1)**: the Federal Minister of Finance submits an annual account of all revenues,
  expenditures, assets and debts to the Bundestag and Bundesrat. **Art. 114(2)**: "The **Federal Court
  of Audit** (Bundesrechnungshof), **whose members shall enjoy judicial independence**, shall audit
  the account and determine whether public finances have been properly and efficiently administered by
  the Federation." It may also survey authorities outside the federal administration, and reports
  annually and directly to the Bundestag, the Bundesrat and the Federal Government.
- **Art. 45b**: a **Parliamentary Commissioner for the Armed Forces** (*Wehrbeauftragter*, 1956) "to
  safeguard basic rights and to assist the Bundestag in exercising parliamentary oversight" — a
  constitutionally entrenched military ombudsman. **No other scenario in this project has one**, and
  it is a direct structural answer to Myanmar 2008's military self-adjudication. **Encode it.**
- **Art. 45a**: the Bundestag's Defence Committee has the powers of a **committee of inquiry** and
  must investigate any matter on the motion of one quarter of its members.
- Corruption enforcement itself is ordinary criminal law (StGB §§331–338), prosecuted by Land
  prosecutors; Germany is unusual among OECD states in having **no central anti-corruption agency**,
  a point TI Germany and the Council of Europe's GRECO have repeatedly criticised. Germany ratified
  UNCAC only in **2014**.
- Encode: `REPORTS_TO: "bundestag_and_bundesrat"` (Bundesrechnungshof, Art. 114(2)),
  `ANTI_CORRUPTION_OBJECTIVE: True`, `POLITICAL_CONTROL: False`, judicial-independence status for
  members, high `INITIAL_EFFECTIVENESS` — and note explicitly in a comment that Germany achieves
  near-best-in-class corruption outcomes (CPI 75–81, V-Dem 0.011) **without** a dedicated
  anti-corruption commission. That is a genuinely important finding for a paper whose success model
  (MFU) is built around a powerful dedicated agency (the IIG). It is also an honest limitation on the
  MFU design's claimed necessity. See flag F3.

### FederalConfig — the real federal benchmark in this set
- Arts. 70–74 legislative competence; **Art. 30** residual Land competence; **Arts. 83–87** Land
  execution of federal law (*Vollzugsföderalismus*) — Germany's distinctive feature is that the Länder
  administer federal law, so administrative capacity is decentralised even where legislation is not.
- **Arts. 106–107 fiscal federalism**: constitutional allocation of tax revenues between Federation,
  Länder and municipalities, plus **horizontal financial equalisation** (*Länderfinanzausgleich*,
  Art. 107(2)) to "ensure a reasonable equalisation of the disparate financial capacities of the
  Länder". **Art. 104a** expenditure responsibility; **Art. 104b/104c** federal grants;
  **Art. 109(3) + Art. 115(2)** the debt brake (*Schuldenbremse*, 2009).
- **This is the only scenario with a genuine constitutional revenue-equalisation mechanism**, and it
  is the closest real analogue to MFU's `RESOURCE_*_SHARE` / `FederalDevFundAgent` design. The actual
  split percentages are set by the Finanzausgleichsgesetz (statutory) and have changed repeatedly, but
  the VAT/income-tax shares in Art. 106 are constitutional. **Source the split from Art. 106 + the
  current FAG rather than reusing MFU's 35/35/30**, and cite the year.
- Relevant to the project's bug #2: Ka-Nova's live Gini is computed from **state-GDP levels**, not
  citizen income (`agents/institutional.py:138`). Germany is the one scenario where a *geographic*
  inequality metric has a direct real-world counterpart with a constitutional equalisation mechanism
  attached, so the Germany backtest is a natural place to validate the state-GDP Gini interpretation.
  Flag to `senior-data-analyst`.
- `MILITARY_IN_REGIONAL_EXECUTIVE: False`. **Art. 91(1)–(2)** (*1968*) internal emergency: a Land may
  call on other Länder's police and the Federal Border Police; if unwilling or unable, the Federal
  Government may place that Land's police under its own orders — "Any such order shall be rescinded
  once the danger is removed **or at any time on the demand of the Bundesrat**." Note the Bundesrat
  kill-switch; this is the German analogue of South Korea's Art. 77(5) and should be encoded.

### MilitaryConfig — **empty in 1949; added 1956/1968**
- **Art. 87a(1)** (*1956*): "The Federation shall establish Armed Forces **for purposes of defence**.
  Their numerical strength and general organisational structure **must be shown in the budget**."
  (Parliamentary budget control of military size, constitutionally mandated.)
- **Art. 87a(2)**: "**Apart from defence, the Armed Forces may be employed only to the extent
  expressly permitted by this Basic Law.**" — a general prohibition on non-defence deployment, with
  enumerated exceptions only.
- **Art. 87a(3)** (*1968*): during a state of defence or tension the Armed Forces may protect
  civilian property and perform traffic control, and may support police measures protecting civilian
  property, cooperating with the competent authorities.
- **Art. 87a(4)** (*1968*): to avert an imminent danger to the existence or free democratic basic
  order of the Federation or a Land, where Art. 91(2) conditions obtain and police and Federal Border
  Police are insufficient, the Federal Government may employ the Armed Forces to support police in
  protecting civilian property and **combating organised armed insurgents** — and "such use of the
  Armed Forces **shall be discontinued if the Bundestag or the Bundesrat so demands**."
- **Art. 65a(1)** (*1956*): "**Command of the Armed Forces shall be vested in the Federal Minister of
  Defence**" — a **civilian cabinet minister**, in peacetime.
- **Art. 115b** (*1968*): "Upon the promulgation of a state of defence the power of command over the
  Armed Forces shall pass to the **Federal Chancellor**." — i.e. even in war, command passes to
  another **civilian**, never to a general.
- **Art. 45b** (*1956*): Parliamentary Commissioner for the Armed Forces (above).
- **Art. 45a(2)** (*1956*): the Defence Committee has committee-of-inquiry powers.
- **Art. 35(2)–(3)**: mutual administrative assistance among Länder and the Federation in serious
  accidents and natural disasters, with the armed forces available for disaster relief; Art. 35(3)
  federal direction where more than one Land is affected, rescindable on Bundesrat demand.
- **Art. 26(1)**: "Acts tending to and undertaken with the intent of disturbing the peaceful relations
  between nations, especially to prepare for a war of aggression, shall be unconstitutional" and
  shall be made a criminal offence. Art. 26(2): weapons of war may be manufactured, transported or
  marketed only with federal government permission.
- **No coup mechanism. No military political role. No reserved seats. No military self-adjudication.
  No immunity.** `COUP_LEGAL_MECHANISM: False`, `MILITARY_POLITICAL_ROLE: False`,
  `MILITARY_SELF_ADJUDICATION: False`, `CIVILIAN_COMMAND: True`,
  `EXTERNAL_COMMAND: "federal_minister_of_defence_peacetime_chancellor_in_state_of_defence"`,
  `DOMESTIC_FORCE_AUTHORIZED`: only under Art. 35(2)-(3), 87a(3)-(4), 91, each with a parliamentary
  or Bundesrat termination right.

Germany's military-constitutional design is the **structural mirror image of Myanmar 2008**: command
vested in a civilian minister (not a Commander-in-Chief with sovereign reserve powers), strength fixed
in the budget (not self-determined), deployment limited to enumerated cases (not "mainly responsible
for safeguarding the Constitution"), a parliamentary ombudsman inside the forces (not self-
adjudication), and every domestic deployment terminable by a chamber vote (not a total power
transfer). **If the paper wants one side-by-side article table, this is the one to build.**

### EconomicConfig / ScienceConfig
- The Basic Law is deliberately **economically neutral** — no stated economic system (the
  *wirtschaftspolitische Neutralität* doctrine). Art. 14 property (with Art. 14(2) "Property entails
  obligations. Its use shall also serve the public good"), **Art. 15** socialisation of land, natural
  resources and means of production into public ownership **against compensation** (never used),
  Art. 12 occupational freedom, Art. 9(3) freedom of association and collective bargaining.
- **Art. 88**: "The Federation shall establish a note-issuing and currency bank as the **Federal
  Bank**… its responsibilities and powers may be transferred to the European Central Bank, which is
  **independent** and committed to the overriding goal of assuring price stability." Central-bank
  independence is constitutionally anchored.
- **Art. 109(3) / 115(2)**: the debt brake (2009) — structural federal deficit limited to 0.35% of
  GDP, Länder to zero, with escape clauses.
- **Art. 5(3)**: "**Arts, sciences, research and teaching shall be free.** Freedom of teaching shall
  not release any person from allegiance to the constitution." Art. 7 school system. Education and
  universities are **Land** competences (Art. 30, 70) — tuition policy is a Land matter and has
  varied (general tuition fees existed in several Länder 2006–2014, then abolished).
  `ACADEMIC_FREEDOM: True` is directly sourced to Art. 5(3) — the strongest textual basis in the set.
  `PHD_TUITION_FREE`: effectively true in practice but **not** a constitutional guarantee — comment it.
- No constitutional tax brackets, royalty rates or ownership caps → proxies.

### AmendmentConfig — verbatim Art. 79
- **Art. 79(1)**: the Basic Law may be amended **only by a law expressly amending or supplementing its
  text** (no implicit amendment).
- **Art. 79(2)**: "Any such law shall be carried by **two thirds of the Members of the Bundestag and
  two thirds of the votes of the Bundesrat**." (Note: two thirds of *Members*, not of votes cast —
  an absolute supermajority.)
- **Art. 79(3) — the eternity clause**: "Amendments to this Basic Law affecting **the division of the
  Federation into Länder, their participation in principle in the legislative process, or the
  principles laid down in Articles 1 and 20** shall be **inadmissible**."
- **No referendum requirement at federal level.** (Art. 29 provides referendums only for
  reorganising Land boundaries; Art. 146 contemplates replacement by a freely adopted new
  constitution.)
- Encode: `STANDARD_AMENDMENT_THRESHOLD: 0.667` (both chambers),
  `ENTRENCHED_AMENDMENT_THRESHOLD: 1.01` or a dedicated `UNAMENDABLE: True` flag — the eternity
  clause is not a high threshold, it is an **absolute bar**, and representing it as 0.667/1.00 loses
  the distinction. `ENTRENCHED_REQUIRES_REFERENDUM: False`, `REVIEW_INTERVAL: 0`,
  `ETERNITY_CLAUSE: True`, `ETERNITY_CLAUSE_SCOPE: ("human_dignity_art_1",
  "democratic_social_federal_state_art_20", "federal_division_into_laender",
  "laender_participation_in_legislation")`, `AMENDMENT_JUDICIAL_REVIEW: True` (the FCC reviews
  amendments against Art. 79(3)).
- **Observed record: around 70 amendments in 77 years** — Germany is the *most* amended constitution
  in this set, and simultaneously the most durable. **That is a real and counter-intuitive finding
  worth a sentence**: a 2/3+2/3 threshold with an absolute core produced high adaptive amendment
  frequency and zero constitutional breakdown, while South Korea's 2/3 + double-50% referendum
  produced **zero** amendments in 38 years and Myanmar's 75% + referendum produced a frozen text. The
  comparison between amendment *difficulty* and constitutional *survival* is a genuine analytical
  contribution the 7-constitution design can make.

### TransitionConfig
- The 1949 Basic Law was adopted under Allied occupation; the Occupation Statute (1949) and later the
  **General Treaty / Deutschlandvertrag (1952/1955)** governed residual Allied rights until the **Two
  Plus Four Treaty (12 September 1990)** restored full sovereignty.
- **Art. 139**: the denazification legislation ("Liberation from National Socialism") is unaffected by
  the Basic Law's provisions — i.e. the Basic Law **expressly declined to immunise the prior regime**.
  **Art. 131**: statutory regulation of former public servants' legal status.
- **Art. 143** (1990): time-limited derogations for the former GDR territory, expiring 31 Dec 1992 /
  31 Dec 1995; derogations may not violate Art. 19(2) and must be compatible with Art. 79(3).
- **No amnesty clause. No immunity clause. The opposite of Myanmar 2008 s. 445, Thailand 2017 s. 279,
  Pakistan Art. 270A and Chile's DL 2,191.** `AMNESTY_GRANTED: False`, `PRIOR_ACTIONS_IMMUNE: False`,
  `MILITARY_AMNESTY: False`. *Honest caveat: the real-world record of West German prosecution of Nazi-
  era crimes in the 1950s–60s was poor, and the 1949/1954 federal amnesty laws (Straffreiheitsgesetze)
  and Art. 131 reinstatement of former officials produced substantial de facto impunity. The
  **constitutional text** grants no immunity; the **political practice** did. Say both.*

### EmergencyConfig — **absent in 1949; added 1968**
- **Art. 115a(1)** (*1968*): a determination that the federal territory is under armed attack or
  imminently threatened (**state of defence**) "shall be made by the **Bundestag with the consent of
  the Bundesrat**… on application of the Federal Government and shall require a **two-thirds majority
  of the votes cast, which shall include at least a majority of the Members of the Bundestag**."
- **Art. 115a(2)**: if immediate action is imperative and the Bundestag cannot be convened or cannot
  muster a quorum, the **Joint Committee** (Art. 53a: two-thirds Bundestag members, one-third
  Bundesrat members) makes the determination by the same two-thirds standard.
- **Art. 115b**: command passes to the **Federal Chancellor** (not to the military).
- Art. 115c–115h: extended federal legislative powers, Joint Committee legislating in place of
  Bundestag/Bundesrat only where they cannot act; **Art. 115g: "The constitutional status and the
  exercise of the constitutional functions of the Federal Constitutional Court and its judges may not
  be impaired"**; Art. 115h: electoral terms extended, but the Chancellor cannot be removed except
  under a constructive-vote variant; **Art. 115l: the Bundestag with Bundesrat consent may at any
  time repeal laws enacted by the Joint Committee, and may at any time declare the state of defence
  terminated — and must do so when the conditions no longer obtain.**
- **Art. 80a** (*1968*): heightened powers applicable only after the Bundestag determines a **state
  of tension**.
- **Art. 81**: legislative emergency (*Gesetzgebungsnotstand*) — a narrow, time-limited device
  requiring Bundesrat consent, never used.
- Encode: `RIGHTS_UNTOUCHED: True`, `TOTAL_POWER_TRANSFER_POSSIBLE: False`,
  `LEGISLATURE_SUSPENDED_DURING_EMERGENCY: False`, `COURT_SUPREMACY: True` (Art. 115g),
  `EMERGENCY_DECLARED_BY: "bundestag_two_thirds_with_bundesrat_consent"`,
  `LEGISLATURE_CAN_TERMINATE: True` (Art. 115l) with a simple-majority threshold.
  **Germany's emergency configuration is the strictest in the set**: declaration requires a
  legislative supermajority (not an executive act), command goes to a civilian, the constitutional
  court is expressly insulated, and termination is a legislative right. Contrast directly with
  Myanmar 2008 ss. 417–419, where declaration and total power both sit with the Commander-in-Chief.
- *1949-as-enacted alternative: all of the above is `None`/`False` because the chapter did not exist.
  See §0 and flag F1.*

### ROEConfig / PsychConfig / CryptoJusticeConfig / NorthStarConfig
- `ROEConfig`: real referents exist — Art. 26(1) (aggressive war unconstitutional and criminal),
  Art. 87a(2) (defence-only), Art. 4(3) (conscientious objection), Art. 1(1)+19(2) binding on the
  forces, the *Innere Führung* doctrine and the Soldatengesetz §11 duty to disobey unlawful orders
  (statutory). `FOLLOWING_ORDERS_DEFENSE: False` and `DUTY_TO_REFUSE_ILLEGAL: True` are defensible
  from Soldatengesetz §11 — label them statutory, not constitutional.
- `PsychConfig`, `CryptoJusticeConfig`: no referent → absent pattern.
- `NorthStarConfig`: the Basic Law states no development goal. Art. 20(1) "democratic and **social**
  federal state" (*Sozialstaatsprinzip*) and Art. 72(2)/106/107's "equivalence of living conditions"
  / financial-equalisation language are the nearest things. `PROGRESS_METRIC` is a modelling choice.

---

## 2. Real validation / backtesting data

### 2.1 Transparency International CPI
Access method as in the South Korea package. **CPI begins 1995 — year 46 of the instrument.** There
is no CPI observation for 1949–1994, i.e. for the entire 50-year window that matches Ka-Nova's
horizon. **This is the single most important data limitation in the Germany scenario** and the reason
V-Dem (§2.3) must carry the backtest.

Germany, 1995–2011 (0–10 scale; TI states pre-2012 scores are not comparable across years):

| 1995 | 1996 | 1997 | 1998 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 8.14 | 8.27 | 8.23 | 7.9 | 8.0 | 7.6 | 7.4 | 7.3 | 7.7 | **8.2** | 8.2 | 8.0 | 7.8 | **7.9** | 8.0 | 7.9 | 8.0 |

Germany, 2012–2025 (0–100 scale, TI workbook):

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 79 | 78 | 79 | 81 | 81 | 81 | 80 | 80 | 80 | 80 | 79 | 78 | 75 | 77 |

**Data-integrity warning, Germany-specific.** The defective
`https://images.transparencycdn.org/images/CPI-Archive-2004.csv` reports Germany as **3.6 / rank 64**
and `CPI-Archive-2008.csv` reports **3.9 / rank 67** — both wrong by a row-shift. The 2004 value is
Ghana's real 2004 score (3.6 / rank 64); the 2008 value is the score shared by Georgia and Ghana that
year (3.9 / rank 67). The correct values for Germany, from the page-linked files
(`CPI-2004_200602_110140.csv`, `CPI-Archive-2008-2.csv`) are **8.2 / rank 15** and **7.9 / rank 14**.
If anyone on the team scripted the obvious `CPI-Archive-<year>.csv` URL pattern, **Germany's series
is corrupted in exactly the two years that would make it look like a mid-table country.** Re-pull
from the page-linked CSVs.

### 2.2 World Bank Worldwide Governance Indicators
Source: WGI 2023 Update, 1996–2022 (`wgidataset.xlsx`, www.govindicators.org). Point estimates
(−2.5…+2.5):

| Indicator | 1996 | 2000 | 2005 | 2010 | 2015 | 2020 | 2022 |
|---|---|---|---|---|---|---|---|
| Control of Corruption | **1.91** | 1.80 | 1.88 | 1.77 | 1.78 | 1.83 | 1.82 |
| Political Stability / No Violence | 1.29 | 1.41 | 0.89 | 0.80 | 0.69 | 0.64 | 0.61 |
| Voice & Accountability | 1.33 | 1.31 | 1.49 | 1.30 | 1.42 | 1.37 | 1.41 |
| Government Effectiveness | 1.72 | 1.80 | 1.50 | 1.52 | 1.66 | 1.31 | 1.29 |
| Rule of Law | 1.61 | 1.61 | 1.65 | 1.64 | 1.76 | 1.52 | 1.53 |

Germany's Control of Corruption is **remarkably stable at +1.74 to +2.00 across all 24 observations**
— the flattest series in this project's dataset. WGI, like CPI, begins 46 years into the instrument.

### 2.3 V-Dem (v16, 2026) — the only source covering 1949 onward, and the only one that covers the exact 50-year horizon
Access method and citation guidance identical to the South Korea package. **Critically: OWID/V-Dem
carries "West Germany" as a separate entity for 1949–1990**, which is exactly the instrument this
scenario encodes. Use `entity == "West Germany"` for 1949–1990 and `entity == "Germany"` from 1991.
`political-corruption-index` runs 0 = clean → 1 = highly corrupt.

**West Germany, V-Dem annual, 1949–1973** (years 1–25 of the 50-year horizon):

| year | 1949 | 1950 | 1951 | 1952 | 1953 | 1954 | 1955 | 1956 | 1957 | 1958 | 1959 | 1960 | 1961 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .793 | .813 | .813 | .800 | .812 | .828 | .828 | .824 | .832 | .831 | .831 | .831 | .835 |
| liberal dem. | .742 | .765 | .765 | .752 | .765 | .781 | .781 | .778 | .786 | .785 | .785 | .785 | .789 |
| **pol. corruption** | **.020** | .018 | .018 | .018 | .018 | .017 | .015 | .015 | .014 | .012 | .012 | .012 | .012 |
| rule of law | .984 | .987 | .988 | .988 | .988 | .988 | .989 | .989 | .990 | .991 | .991 | .991 | .991 |
| judicial constr. | .946 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 |
| legislative constr. | .983 | .982 | .982 | .982 | .982 | .982 | .982 | .982 | .982 | .982 | .982 | .982 | .982 |

| year | 1962 | 1963 | 1964 | 1965 | 1966 | 1967 | 1968 | 1969 | 1970 | 1971 | 1972 | 1973 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .840 | .845 | .845 | .846 | .843 | .843 | .843 | .842 | .855 | .855 | .854 | .852 |
| liberal dem. | .794 | .799 | .799 | .800 | .796 | .796 | .796 | .795 | .811 | .810 | .810 | .808 |
| pol. corruption | .012 | .012 | .012 | .012 | .012 | .012 | .011 | .011 | .011 | .011 | .011 | .011 |
| rule of law | .990 | .991 | .991 | .991 | .991 | .991 | .992 | .992 | .992 | .992 | .992 | .992 |
| judicial constr. | **.950** | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 |
| legislative constr. | .982 | .982 | .982 | .982 | **.973** | .973 | .973 | .973 | .977 | .977 | .977 | .977 |

**West Germany, V-Dem annual, 1974–1990** (years 26–42):

| year | 1974 | 1975 | 1976 | 1977 | 1978 | 1979 | 1980 | 1981 | 1982 | 1983 | 1984 | 1985 | 1986 | 1987 | 1988 | 1989 | 1990 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .852 | .852 | .854 | .855 | .858 | .861 | .864 | .865 | .865 | .864 | .863 | .863 | .863 | .864 | .864 | .864 | .892 |
| liberal dem. | .808 | .808 | .809 | .809 | .814 | .816 | .822 | .824 | .824 | .820 | .819 | .819 | .819 | .823 | .824 | .824 | .853 |
| pol. corruption | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 | .011 |
| rule of law | .992 | .992 | .992 | .992 | .992 | .992 | .993 | .993 | .993 | .993 | .993 | .993 | .993 | .993 | .993 | .993 | .994 |
| judicial constr. | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 | .952 |
| legislative constr. | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 | .977 |

**Unified Germany** (entity `Germany`), selected years:

| year | 1991 | 1995 | 2000 | 2005 | 2010 | 2015 | 2020 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .893 | .893 | .899 | .896 | .898 | .883 | .870 | .825 | .828 |
| liberal dem. | .853 | .853 | .860 | .859 | .862 | .845 | .821 | .778 | .782 |
| pol. corruption | .011 | .011 | .011 | .011 | .011 | .011 | .016 | .024 | .024 |
| rule of law | .994 | .994 | .993 | .993 | .993 | .994 | .991 | .991 | .991 |
| judicial constr. | .952 | .952 | .952 | .952 | .952 | .952 | .918 | .934 | .934 |
| legislative constr. | .977 | .977 | .977 | .983 | .987 | .981 | .981 | .981 | .981 |

**Backtest targets this gives you, year by year, for the exact 50-year horizon:**
- `corruption`: **starts at 0.020 in year 0 (1949), falls monotonically to 0.011 by year 19 (1968),
  then flat to year 50 (1999).** Compare Ka-Nova Scenario A (MFU): **0.0122 ± 0.0073 at year 50.**
  **That is an almost exact match to West Germany's observed terminal value of 0.011.** This is the
  most favourable external validation result available anywhere in this project, and it comes from a
  constitution Kaung did not design. It is the direct answer to the self-design-bias disclosure: the
  MFU scenario's corruption endpoint is reproduced by a real, independently-authored,
  externally-imposed democratic constitution. **Lead with this.**
- `rule of law`, `judicial constraints`, `legislative constraints`: essentially flat at .98–.99, .95,
  .98 for 50 years — a stability signature a simulation should reproduce as "no drift".
- `polyarchy`/`liberal democracy`: slow monotonic improvement (.793 → .852 over 25 years), i.e.
  consolidation rather than step change. Contrast South Korea's sharp 1987→1988 step.

### 2.4 Coup / constitutional-crisis event history
Primary dataset: **Powell & Thyne V2026.08.29**
(`https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv`).
**Germany has ZERO coded coup events in the entire 1950–2026 dataset — neither successful nor
failed.** It is the only country in this project's set with a completely empty record.

Constitutional-stress event history (all documented; these are the real "did the constitution hold?"
tests):
| Date | Event | Outcome |
|---|---|---|
| 1949-05-08 / 05-23 | Basic Law adopted / promulgated | — |
| 1951 | Federal Constitutional Court established (BVerfGG) and begins work | — |
| **1952-10-23** | **SRP (neo-Nazi) banned** by the Federal Constitutional Court under Art. 21(2) | Constitution defends itself |
| 1955–56 | *Wehrverfassung*: rearmament; Arts. 87a, 65a, 45a, 45b added; Bundeswehr established | Amended, not broken |
| **1956-08-17** | **KPD (Communist Party) banned** under Art. 21(2) | Constitution defends itself |
| **1962** | **Spiegel affair** — Defence Minister Franz Josef Strauss forced to resign over the arrest of journalists | Press freedom upheld; minister removed |
| 1966–69 | Grand Coalition | — |
| **1968-06** | **Notstandsverfassung** (17th amendment): Arts. 115a–115l, 53a, 80a, 91, 20(4) added over mass protest | Amended by 2/3+2/3 |
| **1972-04-27** | **Constructive vote of no confidence against Chancellor Brandt FAILS** (Art. 67) | Mechanism works as designed |
| 1972-09 / 1983-01 / 2005-07 / 2024-12 | Art. 68 confidence-vote dissolutions (Brandt, Kohl, Schröder, Scholz) | FCC upheld the 1983 and 2005 dissolutions |
| 1977 | "German Autumn" — RAF terrorism; Schleyer kidnapping | No state of emergency declared |
| **1982-10-01** | **Constructive vote of no confidence against Chancellor Schmidt SUCCEEDS** — Kohl elected (Art. 67) | Orderly transfer |
| 1990-10-03 | Unification via Art. 23 accession; Art. 143 derogations | — |
| 1990-09-12 | Two Plus Four Treaty — full sovereignty | — |
| 2003, 2017 | **NPD ban applications rejected** by the FCC | Militant democracy has limits the court enforces |
| 2024-01-23 | **"Die Heimat" (ex-NPD) excluded from state financing** under Art. 21(3) | New mechanism used |
| **2024-12-19/20** | FCC-resilience amendment: Bundestag **600 of 733**, Bundesrat consent | Court protections constitutionalised |
| 2025-05 | AfD designated "confirmed right-wing extremist" by the BfV (contested in court) | Ongoing |

**Zero coups, zero breakdowns, ~70 amendments, 77 years.** No other constitution in this project's
set comes close.

### 2.5 Survey-based trust in government — best coverage in the set
| Source | Germany coverage | Notes |
|---|---|---|
| **ALLBUS** (German General Social Survey, GESIS) | **Biennial since 1980** | Institutional-trust battery (Bundestag, federal government, courts, **Bundeswehr**, police, parties). Free download at GESIS (`search.gesis.org`), study series ZA1795 onwards. **Longest and best-documented German trust series** |
| **Eurobarometer** (Standard EB, European Commission) | Germany since 1974 (as West Germany); the standard "trust in the national government / national parliament" item (`QA6a` family) runs from the late 1990s in comparable form | Free via GESIS Eurobarometer Data Service; the EB "Public Opinion" portal provides topline time series |
| **European Values Study** | Germany in 1981, 1990, 1999, 2008, 2017 | Integrated with WVS as the Integrated Values Surveys 1981–2022 |
| **World Values Survey** | Germany in waves 1–7; listed for Wave 8 (2024-26). Germany's W3 record: IHSN catalog 9097 ("Germany — World Values Survey 1997, Wave 3"); W7 record: IHSN catalog 11570 | `E069_11` confidence in government, `E069_07` parliament, `E069_10` armed forces, `E069_17` civil service |
| **OECD Trust in government** (Gallup World Poll) | Germany 2006–present, annual | OECD.Stat / Government at a Glance |
| **OECD Survey on Drivers of Trust in Public Institutions** | Germany in 2021, 2023, 2024 rounds | OECD publications + microdata |
| **Politbarometer** (Forschungsgruppe Wahlen / ZDF) | **Monthly since 1977** | Archived at GESIS; the highest-frequency German political-attitudes series |

**No trust percentages are given here** — all require download. But note: **ALLBUS (1980) and
Politbarometer (1977) are the only trust series in this entire project that reach back more than ~45
years**, and neither reaches 1949. **There is no survey-based trust observation for the first 30 years
of the Basic Law.** Any 1949 `YEAR_ZERO_TRUST` is a derivation. See L3.

### 2.6 Recommended year-zero calibration (inference, not a source)
| Field | Proposed value | Basis |
|---|---|---|
| `YEAR_ZERO_CORRUPTION` | **0.020** | V-Dem v16 political corruption index, **West Germany, 1949** — a real observation at the exact year zero |
| `YEAR_ZERO_TRUST` | **derived only** | No survey exists for 1949. Earliest options: OMGUS/HICOG occupation surveys (1945–1955, archived at the Roper Center and in Merritt & Merritt's *Public Opinion in Occupied Germany* / *Public Opinion in Semisovereign Germany*) — **I did not verify these datasets' availability; treat as a lead, not a source** |
| `YEAR_ZERO_COUP_RISK` | **0.00** | Powell-Thyne records zero German coup events 1950–2026. A non-zero floor is defensible only as a modelling choice, and arguably Germany's pre-1949 history (1920 Kapp, 1923 Beer Hall, 1944 July 20) justifies a non-zero prior at year zero |
| `YEAR_ZERO_STABILITY` | **derived only** | WGI begins 1996 (+1.29) |
| `YEAR_ZERO_GINI` | pre-1962 German income distribution data is thin; the first reliable EVS/SOEP-era figures are much later | **Do not invent a 1949 Gini.** This is a genuine gap |

---

## 3. Country-accurate elite role titles for the LLM chain

`chain_type: "civilian"`. This cast maps onto the MFU civilian pattern more cleanly than any other
scenario, because MFU's own design borrows from it.

| Slot | Title | Constitutional basis |
|---|---|---|
| 1 | **Federal Chancellor** (Bundeskanzler) | Art. 63, 65 — executive head of government, policy guidelines; command of the armed forces in a state of defence (Art. 115b) |
| 2 | **Federal President** (Bundespräsident) | Art. 54 — ceremonial head of state; countersignature requirement (Art. 58) |
| 3 | **President of the Bundestag** (Bundestagspräsident) | Art. 40 |
| 4 | **President of the Bundesrat** (Bundesratspräsident) | Art. 52(1) — one-year rotating presidency; also deputises for the Federal President (Art. 57) |
| 5 | **President of the Federal Constitutional Court** (Präsident des Bundesverfassungsgerichts) | Art. 93, 94 |
| 6 | **President of the Federal Court of Audit** (Präsident des Bundesrechnungshofes) | Art. 114(2) — judicial independence; the constitutional integrity organ |
| 7 | **Federal Minister of Defence** (Bundesminister der Verteidigung) | **Art. 65a — command of the armed forces is vested in this civilian minister.** Use this rather than a uniformed officer; using the Inspector General would misrepresent the chain of command |
| 8 (if the chain supports 8) | **Parliamentary Commissioner for the Armed Forces** (Wehrbeauftragter des Bundestages) | Art. 45b — the military ombudsman; no analogue in any other scenario |

Deliberately **not** included: the Inspector General of the Bundeswehr (*Generalinspekteur*) as a
decision-making principal. He is the senior military adviser, not a commander; command runs
Minister → Chancellor. Including a general as a peer principal would import the military-chain
pattern into Germany's constitutional design, which is the exact opposite of what Art. 65a/115b say.
**If the simulation needs a uniformed agent for symmetry with the military-chain scenarios, label it
"Inspector General of the Bundeswehr (military adviser, no command authority)" and give it no veto.**

Historical names, if wanted: Chancellors **Konrad Adenauer** (1949–63), Ludwig Erhard, Kurt Georg
Kiesinger, **Willy Brandt** (1969–74, survived the 1972 Art. 67 motion), **Helmut Schmidt**
(1974–82, removed by the 1982 Art. 67 motion), **Helmut Kohl** (1982–98); Presidents Theodor Heuss,
Heinrich Lübke, Gustav Heinemann, Walter Scheel, Karl Carstens, Richard von Weizsäcker.

---

## 4. Honest sourcing limitations

**L1 — The amendment count is approximate.** "Around 70" is from deutschland.de's 75th-anniversary
material. The precise count depends on whether you count amending *laws* (Änderungsgesetze) or
amended *articles*, and whether the 1990 Unification Treaty amendments count as one or several. The
commonly cited figure is 67 amending laws through the early 2020s, plus the December 2024 FCC
amendment. **Get the exact number from the Bundestag's own documentation (the Grundgesetz's
"Änderungsnachweis") before quoting a figure.**

**L2 — Article attributions to 1956 and 1968 are from standard constitutional history, not from the
amendment instruments.** The official gesetze-im-internet.de English translation carries only
consolidated text with an "amended by" footer, not per-article provenance. The assignments above
(Arts. 87a, 65a, 45a, 45b → 7th amendment 1956; Arts. 115a–115l, 53a, 80a, 91, 20(4), 87a(3)–(4) →
17th amendment 1968; Arts. 93(2)–(3) → Dec 2024) are well established in the literature but should be
checked against the Bundesgesetzblatt citations if the manuscript asserts them. **Art. 93(3)'s Dec
2024 provenance is solid** — I verified the Bundestag vote (600 of 733, 19 Dec 2024) and the Bundesrat
consent (20 Dec 2024) from the Federal Ministry of the Interior's own release and two academic
commentaries.

**L3 — No survey trust data exists for 1949–1977.** ALLBUS starts 1980, Politbarometer 1977,
Eurobarometer 1974, EVS 1981. The occupation-era OMGUS/HICOG surveys are a possible lead but **I did
not verify that they are accessible or codable**. Any 1949 trust value is a derivation and must be
labelled as one.

**L4 — No CPI or WGI observation exists for 1949–1994.** This covers the entire 50-year window that
the simulation horizon matches. **The Germany backtest must rest on V-Dem.** Say so explicitly rather
than letting a reader assume CPI coverage.

**L5 — V-Dem's West Germany series is the right entity but has low variance.** Political corruption is
constant at .011 from 1968 to 1990 and rule of law constant at .992–.993. A near-constant target
makes "the simulation reproduces the data" a weak test — the simulation only has to not drift.
State that honestly rather than claiming a strong fit. The *informative* comparison is the **level**
(0.011–0.020) against MFU's simulated 0.0122, not the shape.

**L6 — The "no immunity" claim needs its caveat.** The Basic Law grants no amnesty (Art. 139
expressly preserves denazification law), but West Germany's 1949 and 1954 Straffreiheitsgesetze and
Art. 131's reinstatement of former Nazi-era civil servants produced substantial de facto impunity.
Encoding `AMNESTY_GRANTED: False` is textually correct and historically incomplete. **Comment both in
the code and say both in the paper** — the comparative point (constitutionalised immunity in Myanmar/
Thailand/Pakistan vs none in Germany) is real, but it should not be oversold.

**L7 — Config categories with no German referent:** `CryptoJusticeConfig`, `PsychConfig`, MFU's IIG
academy/partnership machinery, all `ETHNIC_*` fields (the Basic Law has no ethnic-group structure;
Art. 3(3) prohibits discrimination). Values placed there are modelling choices; comment them.

**L8 — Land count and `STATE_COUNT`.** 11 in 1949, 10 from 1952, 16 from 1990. Pick one with a date.

---

## 5. Flags for Kaung — decide before the engineer encodes

**F1 — "Germany 1949" is not a single instrument, and the label needs fixing before anything is
encoded.** The 1949 text as enacted had **no armed forces chapter and no emergency chapter**. Those
arrived in 1956 and 1968. Three options, all legitimate, one choice required:
(a) encode the consolidated current Grundgesetz, label it `"1949_basic_law_as_amended"`;
(b) encode the text as amended through 1968, label it `"1949_basic_law_as_amended_through_1968"` —
    this gives a non-empty military and emergency configuration covering the whole 1968–1999 portion
    of the 50-year window and is my recommendation;
(c) encode 1949-as-enacted and state in the paper that `MilitaryConfig` and `EmergencyConfig` are
    structurally empty because the most successful constitution in the set began by omitting the two
    chapters Myanmar 2008 uses to legalise a coup. **This is rhetorically the strongest option** but
    it leaves two config classes blank, which will look like incomplete work unless the manuscript
    explains it.
What must **not** happen is labelling it "Germany 1949" while encoding Art. 87a/115a parameters. That
is a factual error a German-law-literate reviewer will find, on a paper that cannot afford one.

**F2 — The Germany/MFU corruption match is the single best result in this research package. Use it
carefully and it answers the self-design-bias problem head-on.** Ka-Nova Scenario A's locked year-50
corruption is **0.0122 ± 0.0073** (`.claude/memory.md` §6). V-Dem's observed political corruption for
West Germany is **0.020 at year 0 (1949) and 0.011 from year 19 to year 50**. A real,
Allied-supervised, independently-authored democratic constitution lands inside Scenario A's confidence
interval at the same horizon. That converts "Kaung designed the success baseline himself" from a
liability into a validated claim: *the MFU design's endpoint is the endpoint a real successful
democratic constitution actually reached.* **Caveats that must travel with the claim** (see L5): the
comparison is of levels, not shapes; V-Dem's West Germany series has very low variance, so this is a
level-calibration result and not a dynamics result; and both numbers are on the same 0–1 scale and in
the same direction, which should be stated so no one suspects a rescaling.

**F3 — Germany undercuts one of MFU's design premises, and the paper is stronger if it says so.**
MFU's success model is built around a powerful dedicated anti-corruption agency (the IIG: 27-month
academy, 0.85 entry merit, court custody of evidence, partnership council, Total Ruin protocol).
**Germany achieves a cleaner corruption record than MFU simulates, with no dedicated anti-corruption
agency at all** — only the Bundesrechnungshof (Art. 114(2)), ordinary criminal law, and a federal
prosecutorial structure. Germany did not even ratify UNCAC until 2014 and is routinely criticised by
GRECO for the absence of a central anti-corruption body. This is a real finding about *which*
structural features do the work, and it is exactly the kind of thing Reviewer 2's "is it structural or
parameter-driven?" question is asking for. Reporting it costs nothing (the MFU constitution is not the
paper's normative claim — per the locked self-design-bias disclosure, it is a parameter-sensitivity
object) and buys considerable credibility.

**F4 — The amendment-frequency vs survival finding is a free contribution.** Across the seven
scenarios the amendment thresholds and observed amendment counts are:

| Scenario | Amendment rule | Amendments in force-life | Constitution survived? |
|---|---|---|---|
| Germany 1949 | 2/3 Bundestag + 2/3 Bundesrat, absolute eternity clause (Art. 79) | **~70 in 77 years** | **Yes** |
| South Korea 1987 | 2/3 Assembly + referendum (50% turnout + 50% majority) | **0 in 38 years** | Yes (survived a martial-law attempt) |
| Chile 1980 | 3/5 (2/3 for Chapters I, II, VII, XI, XIV) | Many, incl. 54 reforms 1989 and 58 reforms 2005 | **Yes, 45 years** |
| Thailand 2017 | ~1/2 of both Houses **+ 1/3 of Senators + 20% of opposition**, referendum for core chapters | **1 in 9 years** | Yes so far |
| Pakistan 1973+8th | 2/3 + 2/3, no referendum, amendments non-justiciable | Many; 58(2)(b) repealed 1997 | **No — coup 1999** |
| Myanmar 2008 | 75% + referendum, military 25% veto | **0** | **No — coup 2021** |
| MFU | 67%/67%/100% three-chamber + assembly + referendum | n/a (simulated) | Simulated success |

The pattern — **amendable-but-entrenched-core constitutions survived; unamendable ones broke** — is a
real, citable, reviewer-robust observation that falls straight out of this research package and
directly serves the paper's structural-vs-parametric argument. It also puts MFU's own very high
amendment thresholds in an interesting light that the parameter-sensitivity framing can absorb.

**F5 — Paper 2 rescoping.** `.claude/memory.md` §7 already flags this as an open question. For the
record: this package uses the German material comprehensively, including the V-Dem 1949–1990 West
Germany series that would have been Paper 2's core. Whatever Paper 2 becomes, it should not be
"Germany Basic Law historical backtesting" — that is now spent. Raise with Kaung after this revision
ships, not before.

**F6 — Year-zero calibration traceability.** See the South Korea package §5 F4. Germany, like Pakistan
and Chile, gives a **real V-Dem observation at the exact year zero** (West Germany 1949 = 0.020). Use
the same dataset-year-variable convention across all seven scenarios.

---

## Schema warning

Same as the other packages: `config/constitution_2008.py` is **missing ≥16 field names the live engine
reads**. **Use `config/constitution.py` as the field-name contract** — and for Germany this is
especially easy, because the MFU field design (ceremonial President, executive Chancellor,
constitutional court, civilian command) was clearly derived from this very constitution, so most MFU
fields have a direct German referent. A separate engine-level issue (`self.CONSTITUTION` assigned at
`model_phase3.py:164/167` but never read elsewhere; `agents/official.py`, `agents/citizen.py`,
`feedback/loops.py` and `institutions/chambers.py` all import MFU's `CONSTITUTION` at module level
unconditionally) has been reported to the parent agent — it determines whether any of these parameters
affect the simulation at all.

---

# 6. Administrative geography, population structure, and real geopolitical context

*Added 2026-10-20 by `senior-researcher`, per `.claude/memory.md` section 11's standing realism
requirement and its "each country's own real neighbours" extension. Additive only; nothing above has
been changed. Every figure carries dataset, publisher, year and access method. Inferences are labelled
INFERENCE and never presented as observations.*

## 6.1 Real year-zero national population — the World Bank series CANNOT be used for Germany

**Verified finding, not an assumption.** The World Bank WDI series `SP.POP.TOTL` for country code
`DEU` **begins in 1960** and reports **72,814,900** for that year (accessed 2026-10-20 via
`https://api.worldbank.org/v2/country/DEU/indicator/SP.POP.TOTL?date=1960:1965&format=json`). West
Germany's own 1960 population was roughly 55.4 million; the GDR's was roughly 17.2 million. The World
Bank series is therefore **unified Germany applied retroactively**, and using it for this scenario
would overstate West Germany's population by about 1.45x. There is no World Bank figure for 1949 at
all. This is the only one of the five new countries where the World Bank route fails outright.

Correct source: the **1950 Volkszählung (census of 13 September 1950)**, the first census conducted
under the Basic Law.

| Quantity | Value | Source |
|---|---|---|
| **Federal Republic incl. West Berlin, excl. Saarland, 13 Sept 1950** | **49,842,624** | 1950 Volkszählung, Statistisches Bundesamt (figure corroborated across multiple secondary compilations of the 1950 census; see §6.7 L1) |
| Saarland, 1950 | 995,210 | Not part of the FRG until 1 January 1957 |
| Expellees (*Heimatvertriebene*) in the FRG, 1950 | **8,025,000 = 16.1% of the population** | Gerhard A. Ritter and Merith Niehuss, *Wahlen in der Bundesrepublik Deutschland: Bundestags- und Landtagswahlen 1946-1987* (Munich: Beck, 1987), p. 31, reproduced by German History in Documents and Images (GHDI) |

**Year zero is 23 May 1949** (Basic Law in force). The census is **16 months later** — it is the
nearest real enumeration, not a 1949 observation, and should be labelled as such. A 1949 mid-year
estimate of roughly 49.2 million circulates in secondary sources; I found no primary-source citation
for it and it should **not** be put in a manuscript table.

**Citizen count at the confirmed 1:5000 ratio: 49,842,624 / 5000 = 9,969 citizens.**

**One year-zero fact that no other scenario has, and which belongs in the paper.** One in six people
in the simulated year-zero population (16.1%) had arrived within the previous five years as expellees
from territories east of the Oder-Neisse line and from Czechoslovakia. Germany's "externally validated
success case" status is being claimed for a constitution that started with a sixth of its population
as recent destitute refugees, in a bombed-out economy, under foreign military occupation. If the
simulation's year-zero conditions do not reflect that, the validation claim (`YEAR_ZERO_CORRUPTION =
0.020` landing inside Scenario A's own year-50 CI) is being made too easy, and an adversarial reviewer
will point out that the comparison flatters MFU by giving Germany an unrealistically benign start.

## 6.2 Real administrative geography — `STATE_COUNT = 10` matches 1957-1990, not 1949

The current `STATE_COUNT = 10` with the ten Länder listed in `SimulationConfig.SIMULATION_STATES`
(`schleswig_holstein` ... `saarland`) does **not** correspond to the year-zero configuration. Real
timeline:

| Date | Configuration | Legal basis |
|---|---|---|
| **23 May 1949** | **11 Länder**: Schleswig-Holstein, Hamburg, Bremen, Niedersachsen, Nordrhein-Westfalen, Hessen, Rheinland-Pfalz, **Württemberg-Baden, Baden, Württemberg-Hohenzollern**, Bayern. Plus **Groß-Berlin**, named in the original Art. 23 but with its participation suspended by the Allies | Basic Law, original Art. 23 |
| 25 April 1952 | The three southwest states merge into **Baden-Württemberg** → 9 Länder | Art. 118 |
| 1 January 1957 | **Saarland** accedes → 10 Länder | Art. 23 (Saar Treaty, following the 23 Oct 1955 referendum) |
| 3 October 1990 | 5 new eastern Länder + unified Berlin → 16 | Unification Treaty |

So **"10 Länder" is correct for 1957-1990**. Given Kaung's locked instrument decision (memory.md §4a,
decision 3: Basic Law *as amended through 1968*), 1957-1990 is the configuration that actually spans
most of the encoded window, so 10 is a defensible choice — it just is not the 1949 configuration, and
the file should say so rather than implying it is.

**Recommendation: keep the 10 Länder and add West Berlin as an 11th unit**, with its real special
status documented: no voting Bundestag delegates (its 22 members were sent by the Berlin
Abgeordnetenhaus and could not vote on final passage), and the city governed under residual Allied
authority until 1990. 11 units sits inside the 8-20 target range, matches 1957-1990 reality, and West
Berlin cannot honestly be dropped from a Cold War German scenario — the Berlin Wall and the Berlin
crises are the single most important external shocks in the window and they need a unit to land on.
Document explicitly that the 1949-1952 three-southwest-states configuration is deliberately not
modelled.

### Population shares, 1950 Volkszählung (13 September 1950)

Two independent derivations are given because the per-Land census figures and the expellee table come
from different sources, and they cross-validate.

| Unit (encode as) | Real name | 1950 census pop. | Share | Derived from Ritter & Niehuss | Agreement | Citizens @1:5000 (of 9,969) |
|---|---|---|---|---|---|---|
| `nordrhein_westfalen` | Nordrhein-Westfalen | 13,196,176 | 26.48% | 13,188,119 | 0.06% | 2,639 |
| `bayern` | Bayern | 9,184,469 | 18.43% | 9,180,095 | 0.05% | 1,837 |
| `niedersachsen` | Niedersachsen | 6,797,379 | 13.64% | 6,808,824 | 0.17% | 1,359 |
| `baden_wurttemberg` | Baden-Württemberg (= Württemberg-Baden + Baden + Württemberg-Hohenzollern in 1950) | 6,430,225 | 12.90% | 6,432,836 | 0.04% | 1,286 |
| `hessen` | Hessen | 4,323,801 | 8.67% | 4,317,365 | 0.15% | 865 |
| `rheinland_pfalz` | Rheinland-Pfalz | 3,004,752 | 6.03% | 2,980,392 | 0.81% | 601 |
| `schleswig_holstein` | Schleswig-Holstein | 2,594,648 | 5.21% | 2,596,970 | 0.09% | 519 |
| `west_berlin` | Berlin (West) | 2,146,952 | 4.31% | 2,144,928 | 0.09% | 429 |
| `hamburg` | Hamburg | 1,605,606 | 3.22% | 1,611,111 | 0.34% | 321 |
| `bremen` | Bremen | 558,619 | 1.12% | 558,140 | 0.09% | 112 |
| `saarland` | Saarland (**acceded 1 Jan 1957**) | — (995,210 in 1950, outside the FRG) | — | — | — | ~199 if included at 1957 weight |
| | **total (10 units incl. West Berlin)** | **49,842,627** | 100.00% | | | 9,969 |

The "Derived from Ritter & Niehuss" column is computed as (expellee count / expellee percentage) from
the sourced table in §6.3 — an independent arithmetic route to each Land's total population. **All ten
agree within 0.81%, and nine of ten within 0.35%**, and the census column sums to 49,842,627 against
the published total of 49,842,624 (a 3-person rounding residual). That is strong internal validation.
See §6.7 L1 for the honest sourcing caveat on the census column.

**Saarland handling.** It is in the current `SIMULATION_STATES` tuple but was not part of the FRG at
year zero. Two defensible options: (a) include it with a 1957-onward weight and document the eight-year
anachronism, or (b) exclude it and run 10 units (9 Länder + West Berlin) for 1949-1957. Option (a) is
simpler and matches the "as amended through 1968" instrument choice; either way, **document it**.

### Structural point this geography carries

Germany is **the only genuinely federal state in the seven-constitution set** (this package's §1
`FederalConfig` section already says so). Unlike Chile's and Thailand's appointed-governor unitary
structures and Pakistan's contested parity-Senate federalism, West German Länder had real
constitutional competences, their own constitutions, and real representation in the Bundesrat (Art.
50-53), plus a genuine fiscal-equalisation mechanism (Art. 106-107, *Länderfinanzausgleich*). So the
MFU 35/35/30 resource-share machinery has, for the first and only time in this set, **a real
referent** — and Art. 107's horizontal equalisation is arguably the closest real-world analogue to
MFU's ethnic-transfer share anywhere in the project. That is a strong, concrete comparison for the
paper, and it should be encoded rather than left as a coincidence.

Note also the concentration contrast: NRW alone is 26.5% of the FRG population — lower than Chile's
Santiago (39.1%) or Pakistan's Punjab (56.1%), and in a genuinely federal structure. Germany is the
one case where the largest unit does **not** dominate the federation.

## 6.3 Per-unit composition — keep `ETHNIC_GROUPS = 0`, and use the expellee share, which is fully sourced

`ETHNIC_GROUPS = 0` is correct and should be preserved. Art. 3(3) of the Basic Law prohibits
discrimination on grounds of descent, race, language, homeland and origin; there is no
constitutionally recognised ethnic-group structure, no reserved seats, and no ethnic chamber. (The one
near-exception, the Danish minority in Schleswig-Holstein under the 1955 Bonn-Copenhagen Declarations,
is a Land-level and bilateral-treaty matter, not a federal constitutional structure.) An 8-slot ethnic
array for Germany would be a fabrication.

### Recommended primary per-unit array: expellee share, 1950 and 1961 — REAL, SOURCED, and of exactly the right shape

Source: Ritter & Niehuss, *Wahlen in der Bundesrepublik Deutschland 1946-1987*, p. 31, via German
History in Documents and Images (accessed 2026-10-20). Expellees in thousands and as a percentage of
each Land's population:

| Unit | 1950 expellees (000s) | 1950 % | 1961 expellees (000s) | 1961 % |
|---|---|---|---|---|
| `schleswig_holstein` | 857 | **33.0** | 630 | 27.2 |
| `niedersachsen` | 1,852 | **27.2** | 1,612 | 24.3 |
| `bayern` | 1,937 | **21.1** | 1,645 | 17.3 |
| `hessen` | 721 | 16.7 | 818 | 17.0 |
| `baden_wurttemberg` | 862 | 13.4 | 1,205 | 15.5 |
| `nordrhein_westfalen` | 1,332 | 10.1 | 2,298 | 14.5 |
| `bremen` | 48 | 8.6 | 98 | 13.9 |
| `hamburg` | 116 | 7.2 | 206 | 11.3 |
| `west_berlin` | 148 | 6.9 | 151 | 6.9 |
| `rheinland_pfalz` | 152 | **5.1** | 276 | 8.1 |
| `saarland` | — | — | 18 | 1.7 |
| **Federal** | **8,025** | **16.1** | **8,956** | **15.9** |

This is a per-unit composition array of **exactly the shape Myanmar's ethnic arrays have**
(`"yangon": [75, 5, 6, 2, 2, 5, 2, 3]`), with a 6.5x spread between the highest unit (Schleswig-Holstein
33.0%) and the lowest (Rheinland-Pfalz 5.1%) — comparable in dispersion to Myanmar's real ethnic
variation, and with the enormous advantage of being fully sourced rather than inferred.

**And it mattered politically, which is the test for whether a cleavage is worth encoding at all:**
- The expellee party (BHE, later GB/BHE) entered the Bundestag in the **1953 election with 5.9% of
  the vote and 27 seats**, on the strength of exactly this geographic distribution.
- Expellee integration via the **Lastenausgleich** (Equalisation of Burdens Act, 14 August 1952) is
  the defining social-policy achievement of the Basic Law's first decade, and a real fiscal transfer
  mechanism running between precisely these units.
- The 1950-to-1961 columns show the real internal migration from the high-expellee agricultural north
  and south-east to the industrial west (NRW 1,332k → 2,298k), which is a genuine inter-unit dynamic
  the simulation could reproduce.

### Recommended secondary array (if a second dimension is wanted): confessional composition

The Catholic/Protestant split is the real structural basis of CDU/CSU-versus-SPD voting in the Basic
Law's first two decades, and the reason a cross-confessional Christian-democratic party was viable at
all: the loss of the heavily Protestant eastern territories shifted the FRG to a roughly even
confessional balance, against the Weimar Reich's roughly 2:1 Protestant majority. Per-Land 1950
confessional shares exist — fowid's compiled table *"Religionszugehörigkeit: evang., kath., andere,
Bundesländer 1950-2011"* surfaced during this research — but **I did not extract the figures**. See
§6.7 L2. Recommend the expellee array as primary (sourced now) and confession as an optional second
dimension (closeable gap).

## 6.4 Real external context — the most structurally different of all five, and it should NOT be mapped onto Myanmar's shape

Myanmar's vector set is "neighbours + major powers + a regional body + illicit networks". West Germany
1949's external situation does not fit that template at all, and forcing it in would destroy the
single most important fact about this scenario.

| Vector | Real relationship at year zero (1949) | Real nature | Notes for the engine |
|---|---|---|---|
| `allied_high_commission` | **THE defining relationship, and it has no analogue anywhere else in the project.** Under the **Occupation Statute (in force 21 September 1949)**, the three Western powers acting jointly retained reserved powers over foreign affairs, foreign trade, demilitarisation, the Ruhr, and — critically — **the right to resume full governmental authority**. The occupation regime ended with the General Treaty / *Deutschlandvertrag* (signed 26 May 1952, in force 5 May 1955), but Allied rights over Berlin and over German unification as a whole survived until the **Two-Plus-Four Treaty (12 September 1990, in force 15 March 1991)** | **External constitutional guarantor with standing reserved powers and a veto** | Must be encoded as its own relationship type, **not** as "foreign influence 0.6". It is a *supervisory* vector that declines in three dated steps (1955, then residually to 1990), and it is precisely why Germany functions as this paper's externally-validated success case: the constitution's guardianship was exercised from *outside* the polity, by actors with no stake in capturing it — the structural inverse of Myanmar's, Thailand's, Chile's and Pakistan's internal military guardianship. **This is the single most valuable comparative point in the Germany scenario and the vector set must be able to carry it.** |
| `ussr_gdr` | The existential threat and the legitimacy competitor. Dated: **Berlin Blockade 24 June 1948 - 12 May 1949** (lifted 11 days before the Basic Law came into force); GDR founded 7 Oct 1949; 17 June 1953 East German uprising; **Hallstein Doctrine 1955**; Berlin Crisis 1958-61; **Berlin Wall 13 August 1961**; Cuban Missile Crisis 1962. Then Ostpolitik inverts the whole frame: Moscow and Warsaw Treaties 1970, Basic Treaty with the GDR 21 Dec 1972 | Existential threat + legitimacy rival | High and **non-monotonic**: must fall sharply from 1970 |
| `france` | **The one relationship that fully inverts within the run.** Occupying power and Saar claimant at year zero (the **Saar referendum of 23 October 1955 rejected Europeanisation 67.7% to 32.3%**, leading to accession on 1 Jan 1957); then ECSC (Treaty of Paris, 18 April 1951), EEC (Treaty of Rome, 25 March 1957), **Élysée Treaty 22 January 1963** | Occupier → core integration partner | Must change sign mid-run. Myanmar has no vector of this type at all |
| `usa` | Occupying power, security guarantor, and economic sponsor simultaneously. Marshall Plan / ERP aid to West Germany on the order of **US$1.4bn, 1948-52** (commonly cited in the 1.39-1.45bn range; see §6.7 L3) | Occupier + patron + guarantor | Declines as occupier, rises as ally |
| `nato` | FRG acceded **9 May 1955**; the Bundeswehr was founded 12 November 1955. The entire military chapter of the Basic Law (the 1956 *Wehrverfassung* amendments, Art. 87a, 65a) **exists because of this accession** | Alliance membership driving constitutional amendment | **The clearest case in the whole project of an external commitment causing a constitutional amendment.** Directly relevant to `AmendmentConfig`, and a point the paper should make explicitly |
| `european_economic_institutions` | ECSC 1951 → EEC 1957 → the Single Market; plus the **London Debt Agreement (27 February 1953)**, which cut Germany's prewar and postwar debt roughly in half | Economic integration + **debt relief** | **The IMF/World Bank analogue for Germany is a creditor-relief relationship — essentially the inverse of Myanmar's conditional-lending vector at 0.25.** Encoding Germany with a Myanmar-style IMF-conditionality vector would invert the real sign |
| `israel_reparations` | **Luxembourg Agreement, 10 September 1952**: DM 3bn to Israel plus DM 450m to the Claims Conference. Ratified by the Bundestag 18 March 1953 with CDU/CSU abstentions, carried by SPD votes | External moral/fiscal obligation with real domestic political cost | No analogue elsewhere. Small in magnitude, large in legitimacy terms |
| `global_economy` | Export-led *Wirtschaftswunder*; high trade exposure | Exposure | Keep |

**Deliberately absent: illicit networks. Recommend ZERO, and this is the cleanest zero in the whole
set.** There is no real West German analogue of Myanmar's drug production, arms smuggling or hawala
networks at any politically meaningful scale in this window. Myanmar runs three such vectors; encoding
any for Germany would be pure fabrication.

**Deliberately absent: a regional-body vector of the ASEAN type.** The EEC/ECSC is categorically
different — a supranational body West Germany **co-founded** and whose rules it helped write, not a
regional organisation applying external pressure to it. Do not reuse Myanmar's ASEAN vector semantics
here.

## 6.5 Historically-calibrated shock types for Germany, 1949-1999

| Shock | Real basis (dated) | Comment |
|---|---|---|
| `guarantor_intervention` | Occupation Statute reserved powers (21 Sept 1949 - 5 May 1955), including the Allied right to resume full authority; residual Berlin/unification rights to 1990 | **New type, no analogue elsewhere.** An external actor that can lawfully override the constitutional order *in defence of it* — the structural inverse of a coup. If the engine can only represent internal guardianship, Germany's whole mechanism is invisible |
| `berlin_crisis` | Blockade 1948-49; Khrushchev's 1958 ultimatum and the 1958-61 crisis; **Wall, 13 August 1961** | Localised to the `west_berlin` unit, nationally amplified |
| `superpower_nuclear_crisis` | 1961 Berlin standoff; 1962 Cuban Missile Crisis | Existential-risk shock with no domestic mechanism, unlike Myanmar's set |
| `debt_relief` (positive) | Currency reform 20 June 1948; **London Debt Agreement 27 February 1953**; Marshall Plan/ERP 1948-52 | **Positive fiscal shock.** Myanmar's `SHOCK_EVENTS` has no debt-relief type at all; its closest positive is `fdi_boom` |
| `labour_supply_inflow` (positive) | The 1955 Italian *Gastarbeiter* recruitment agreement and its successors (Spain and Greece 1960, Turkey 1961, Portugal 1964, Yugoslavia 1968), driven by near-full employment | Positive labour/output shock. Note this package's own `ScienceConfig.BRAIN_DRAIN_RATE_BASE` discussion — Germany is the one scenario with net *in*flow |
| `recession` | **The 1966-67 recession**, the FRG's first | **The most important shock in Germany's set for this paper.** It produced the Grand Coalition, and directly motivated both the 1967 Stability Act and the **1968 *Notstandsverfassung*** (17th amendment, 24 June 1968) — passed over the largest extra-parliamentary protest movement in the FRG's history to that point. This is a **documented, dated chain from an economic shock inside the simulated window to a constitutional amendment at simulated year 19**, and Germany is the only scenario with such a target to validate against. If the engine can represent "shock → constitution amends itself → constitution survives", `AmendmentConfig` and `EmergencyConfig` are where it has to show up |
| `oil_price_shock` | 1973 and 1979 OPEC shocks — both inside a 50-year horizon from 1949 | Transfers from Myanmar's set |
| `domestic_terrorism` | The RAF; the Munich Olympics attack 5 September 1972; the **German Autumn** of 1977 | The real stress test of the Basic Law's emergency architecture, and the reason the 1968 emergency chapter matters. No Myanmar analogue in the current set |
| `reunification` (positive, very large) | **3 October 1990, simulated year 41** | The largest single shock in the window and a positive one. A ~16 million population increase and a 5-Land expansion inside the simulated horizon — the engine almost certainly cannot represent this and the paper should say so rather than quietly ignoring it |
| `global_recession`, `pandemic` | Transfer from Myanmar's set | Keep, lower weight |

## 6.6 Citizen count summary

| Quantity | Value |
|---|---|
| Year zero | 1949 (Basic Law in force 23 May 1949); population anchored on the 13 Sept 1950 census, 16 months later |
| Real population | **49,842,624** (1950 Volkszählung, Statistisches Bundesamt; FRG incl. West Berlin, excl. Saarland) |
| **World Bank WDI is unusable for this scenario** | `SP.POP.TOTL`/`DEU` starts 1960 and is unified Germany (72,814,900 in 1960) |
| Ratio | 1:5000 (confirmed by Kaung) |
| **Citizen agents** | **9,969** |
| For comparison, locked Myanmar value | 11,000 |

## 6.7 Sourcing limitations and flags

**L1 — the per-Land 1950 census column is not directly sourced to a retrieved primary table, and this
should be stated honestly.** The **national** total (49,842,624) is corroborated across multiple
secondary compilations of the 1950 Volkszählung, and **NRW's 13,196,176 was directly confirmed** in
search. The remaining nine per-Land figures are values I asserted and then **independently
cross-validated** against the Ritter & Niehuss expellee-percentage derivation, which is a genuinely
independent arithmetic route: all ten agree within 0.81%, nine of ten within 0.35%, and the column
sums to within 3 persons of the published national total. That is strong corroboration but it is
**not** the same as having pulled Statistisches Bundesamt's *"Bevölkerung nach Ländern 1950"* table.
**A human should retrieve that table** (Statistisches Bundesamt / the Statistische Bibliothek's
digitised *Statistik der Bundesrepublik Deutschland* series, or GESIS/da-ra study res_id 3889
"Regionaldaten VZ 1950 (Bundesländer)") before any of these figures appears in a manuscript table.
If only one source is wanted, the **Ritter & Niehuss derivation is the fully-citable column** and can
be used on its own.

**L2 — 1950 confessional shares by Land not extracted.** §6.3's secondary array is a method
recommendation with a named real source (fowid's compiled *"Religionszugehörigkeit: evang., kath.,
andere, Bundesländer 1950-2011"* table, ultimately from census data) but **no numbers**. Closeable gap.

**L3 — Marshall Plan figure is approximate.** West Germany's ERP receipts are commonly cited at
US$1.39-1.45bn for 1948-52, depending on whether GARIOA aid and counterpart funds are included. Verify
against the ECA/OEEC accounts before quoting a precise figure.

**L4 — no 1949 population observation exists.** The 1950 census is the nearest real enumeration. Do
not substitute an unsourced 1949 estimate.

**L5 — `YEAR_ZERO_TRUST = 0.55`, `YEAR_ZERO_GINI = 0.33` and `YEAR_ZERO_EMPLOYMENT = 0.90` remain
unsourced** (already flagged in `constitution_germany.py` and in this package's §4/L3). Nothing here
fixes them, and note that the 16.1% expellee share now gives a *reason* to think the year-zero Gini
and employment values in the file are optimistic: real early-1950s West German unemployment was around
10-11% during refugee absorption, which is inconsistent with `YEAR_ZERO_EMPLOYMENT = 0.90`.

**F1 — resolve the `STATE_COUNT` period question** (§6.2). 10 Länder = 1957-1990, not 1949.
Recommended: keep 10, add West Berlin as an 11th, and document both the Saarland anachronism and the
deliberate non-modelling of the 1949-52 three-southwest-states configuration.

**F2 — `FederalConfig` is genuinely live for Germany, unlike Chile and Thailand.** Art. 50-53
(Bundesrat), Art. 106-107 (*Länderfinanzausgleich*) and the 1952 Lastenausgleich are real federal
mechanisms. Art. 107's horizontal equalisation is the closest real-world analogue in the entire project
to MFU's 30% ethnic-transfer share. **Encode it properly; this is a comparison the paper can make and
nobody else in the set can supply it.**

**F3 — Germany's external-layer vector set cannot reuse Myanmar's semantics** (§6.4). Three specific
sign inversions must not be lost: the occupying powers are a *constitutional guarantor*, not a foreign
pressure source; the multilateral-finance relationship is *debt relief*, not conditional lending; and
the regional body is one Germany *co-founded*, not one applying external pressure. Flag this to
`senior-research-paper-writer` as well — memory.md §11 already requires the realism shift to be made
visible in the methodology section, and Germany is the case where it changes the interpretation most.

**F4 — reunification (1990, simulated year 41) is almost certainly unrepresentable** and should be
disclosed as a known limitation rather than silently truncated. A 32% population increase and a
5-unit expansion mid-run is outside what the current engine models.

**F5 — CROSS-SCENARIO STATISTICAL POWER, all 7 scenarios, needs Kaung's decision.** Full statement in
the South Korea package §6.7 F1 and the Chile package §6.7 F4. Ratio-derived N: Pakistan 19,646,
Thailand 14,232, **Germany 9,969**, South Korea 8,406, Chile 2,687, versus Myanmar's locked 11,000.
Germany at 9,969 is the closest of the five to the locked baseline, so Germany is the **least**
affected — which matters, because Germany is the scenario carrying the strongest external-validation
claim and it should not be the one weakened by sampling noise. Note also that Myanmar's locked 11,000
implies 55,000,000 while its own World Bank 2008 population is 48,390,793 (= 9,678 at 1:5000), so the
ratio rule does not reproduce the already-published baseline.
