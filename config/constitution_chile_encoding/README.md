# Chile 1980 Constitution (Pinochet-era) — Encoding Research Package

Researcher's workspace document (not code). Prepared by `senior-researcher`, 2026-10-20.
Target output: `config/constitution_chile.py` → registry key `CL`, `chain_type: "military"`.

Intended role in the paper: **near-twin to the 2008 Myanmar military constitution** —
military-authored guardianship design. **Read §5 flag F1 before encoding.** Chile's real-world
outcome data contradicts the near-twin framing on the corruption and collapse axes more sharply than
any other scenario in this project, and that needs to be a deliberate analytical choice rather than a
surprise after a 24-30 hour pod run.

---

## 0. Instrument definition — this is the most important decision in this package

The 1980 Constitution exists in at least four materially different states. **They are not
interchangeable**, and the choice determines whether `CL` is an authoritarian scenario or a
democratic one.

| State | Period | Character |
|---|---|---|
| **(a) 1980 as enacted, under its 29 transitory articles** | 11 Mar 1981 – 11 Mar 1990 | Pinochet as President by transitory Art. 14; the Junta exercising legislative power; no Congress; Art. 8 banning "totalitarian" doctrines; states of exception at presidential discretion (transitory Art. 15, 24) |
| **(b) 1980 as reformed by the 54 reforms of July 1989** | 11 Mar 1990 – Aug 2005 | Elected Congress, but with **institutional (designated) senators, lifetime senators, irremovable service commanders (Art. 93), a military-majority COSENA (Art. 95–96), a COSENA-appointed share of the Constitutional Tribunal (Art. 81(c)), and the binominal electoral system** — the classic "authoritarian enclaves" configuration |
| **(c) 1980 as reformed by Law 20,050 (2005)** | Sep 2005 – present | Designated and lifetime senators abolished; presidential power to remove service commanders restored; COSENA reduced to an advisory body convened by the President; presidential term cut to 4 years |
| **(d) Current consolidated text** | — | Plus the 2019–2023 constitutional process and subsequent reforms; two replacement drafts rejected |

**Recommendation: encode state (a) with state (b) as the transition target, and label it
explicitly.** The scenario's analytical purpose is "military-authored guardianship constitution", and
that is states (a)/(b). If you encode state (c) or (d) you are encoding a democratic constitution
that happens to have authoritarian ancestry, which is a different experiment.

Because the article numbering changes between (b) and (c), the practical approach is: **work from the
1980-with-1989-reforms text**, which is the version whose article numbers the literature uses and
which I read in full for this package.

| Item | Value | Source |
|---|---|---|
| Approving plebiscite | **11 September 1980**; officially reported ~67% approve / 30% reject, no electoral registers, no opposition campaign, state of emergency in force | Wikipedia "1980 Chilean constitutional referendum" — see limitation L2 |
| Entry into force | **11 March 1981** | Transitory articles governed 1981–1990 |
| Text read for this package | 1980 Constitution **with the 1989 reforms**, Spanish text, Georgetown University Political Database of the Americas: `https://pdba.georgetown.edu/Constitutions/Chile/chile89.html` | Article text quoted below is verbatim Spanish from that source |
| Simulation year-zero | **1981** | Entry into force |
| Real observation window | 1981 → 2026 = 45 years, but the instrument changes character twice (1990, 2005) | — |

Recommended label: `"1980_chile_constitution_pinochet_era_with_1989_reforms"`.

---

## 1. Real constitutional structure, mapped to the config schema

All Spanish quotations below are verbatim from the Georgetown PDBA 1989-reform text. English is my
translation and is marked as such.

### FoundationalConfig
- Unitary republic; Chapter I "Bases de la Institucionalidad". Art. 1: the family is the fundamental
  nucleus of society; the State recognises and protects **grupos intermedios** and guarantees their
  adequate autonomy (the corporatist/subsidiarity doctrine that underwrites Art. 23).
- **Art. 8 (as enacted 1980)**: banned the propagation of doctrines attacking the family, advocating
  violence, or holding a "concepción de la sociedad, del Estado o del orden jurídico, de carácter
  totalitario o fundada en la lucha de clases" — read as banning Marxist parties; sanctions included
  10-year disqualification from public office, teaching, and media.
  **Repealed by the 1989 reforms.** The 1989 text reads simply: **"Art. 8. Derogado."** Its successor
  function moved to Art. 19 No. 15 (party regulation) and Art. 9 (terrorism).
- **Art. 9** (1989 text): terrorism is "por esencia contrario a los derechos humanos"; convicted
  persons are disqualified for **15 years** from public office, school/university direction, teaching,
  media ownership or direction, and union/political leadership.
- **Art. 23**: intermediate groups and their leaders who misuse their autonomy by "interviniendo
  indebidamente en actividades ajenas a sus fines específicos" shall be sanctioned by law; senior
  union office is **incompatible** with senior national/regional political-party office.
- 13 regions (`Art. 45` references "las trece regiones del país"). `STATE_COUNT: 13` is
  constitutionally grounded for this instrument (Chile now has 16; the change is later).

### RightsConfig
- **Art. 19** is a single long article containing the full rights catalogue (26 numbered guarantees),
  including Art. 19 No. 1 (life and physical/psychic integrity; protection of the unborn; death
  penalty only by qualified-quorum law; "se prohibe la aplicación de todo apremio ilegítimo"),
  No. 2–3 (equality, legal defence), No. 15 (association and political parties), No. 24 (property).
- **Art. 20** recurso de protección and **Art. 21** recurso de amparo — real judicial remedies on
  paper.
- **Art. 41** (states of exception, below) **expressly removes judicial review of the factual grounds**:
  *"Los tribunales de justicia no podrán, en caso alguno, entrar a calificar los fundamentos ni las
  circunstancias de hecho invocadas por la autoridad para adoptar las medidas en el ejercicio de las
  facultades excepcionales que le confiere esta Constitución."* (my translation: courts may in no case
  review the grounds or the factual circumstances invoked by the authority in exercising the
  exceptional powers the Constitution confers). This is the Chilean analogue of Pakistan's Art. 245(3)
  and Myanmar 2008's finality clauses, and it is **in the permanent text, not just the transitory
  articles**.
- `RIGHTS_SUSPENDABLE: True`, `EMERGENCY_TOUCHES_RIGHTS: True`, `RIGHTS_ABSOLUTE_COUNT: 0`, plus an
  explicit `EMERGENCY_GROUNDS_NON_JUSTICIABLE: True` (Art. 41).

### ExecutiveConfig
- **Art. 25** (1989 text, verbatim): *"El Presidente de la República durará en el ejercicio de sus
  funciones por el termino de ocho años y **no podrá ser reelegido para el período siguiente**."*
  — eight-year term, no immediate re-election. (The 1989 reforms cut the *first* democratic term to
  four years as a transitional measure; later reforms made it six, then four from 2006. Law 20,050
  (2005) set four years. **For state (a)/(b) encode 8.**)
- **Art. 26**: direct election by absolute majority of valid votes, with a run-off 15 days after the
  Tribunal Calificador's declaration if no candidate exceeds half.
- **Art. 32**: enumerated special presidential powers, including: concurring in the formation of
  laws; convoking and closing extraordinary legislative sessions; issuing **decretos con fuerza de
  ley** on delegated matters; convoking plebiscites under Art. 117; **"Designar, en conformidad al
  artículo 45 de esta Constitución, a los integrantes del Senado que se indican en dicho precepto"**
  (appointing the designated senators specified in Art. 45); **"Declarar los estados de excepción
  constitucional"**.
- Impeachment: **Art. 48** — the Chamber of Deputies declares whether accusations lie, on the motion
  of **not fewer than 10 and not more than 20** of its members, against the President (for acts
  gravely compromising the honour or security of the Nation or openly infringing the Constitution or
  laws), Ministers, judges, the Contralor General, generals/admirals, and intendants/governors.
  **Art. 49**: the Senate acts as jury; conviction of **the President requires two-thirds of senators
  in office**, other officials a majority of senators in office; conviction removes the official and
  disqualifies from any public function for **five years**.
- No prime minister. `CHANCELLOR_ROLE: "none"` is correct for Chile (as it is for Myanmar 2008).
- `PRESIDENT_TERM: 8`, `PRESIDENT_MAX_TERMS: 1` (non-consecutive re-election permitted),
  `PRESIDENT_EXECUTIVE_POWER: True`, `PRESIDENT_TIEBREAKER: False`,
  `PRESIDENT_REMOVAL_THRESHOLD: 0.667` (Senate), impeachment initiation is a **fixed member count**
  (10–20 deputies), not a fraction — note it, because the schema expects a float.

### ChamberConfig — the designated-senator mechanism is the Chilean reserved-powers instrument
- **Art. 43** (verbatim): *"La Cámara de Diputados está integrada por **120 miembros** elegidos en
  votación directa por los distritos electorales que establezca la ley orgánica constitucional
  respectiva. La Cámara de Diputados se renovará en su totalidad **cada cuatro años**."*
- **Art. 45** (verbatim opening): *"El Senado se compone de miembros elegidos en votación directa por
  circunscripciones senatoriales, en consideración a las **trece regiones** del país. Cada región
  constituirá una circunscripción, excepto seis de ellas que serán divididas, cada una, en dos
  circunscripciones… **A cada circunscripción corresponde elegir dos senadores.** Los senadores
  elegidos por votación directa durarán **ocho años** en su cargo y se renovarán alternadamente cada
  cuatro años…"* → **38 directly elected senators** (19 constituencies × 2) under the 1989 text;
  26 under the 1980 text's 13-constituency scheme.
- **Art. 45 continues — the designated/institutional senators**, who "shall also form part of the
  Senate":
  - (a) **former Presidents of the Republic who served six continuous years — senators by own right,
    for life** (*"por derecho propio y con carácter vitalicio"*);
  - (b) **two former ministers of the Supreme Court**, elected by the Supreme Court;
  - (c) **one former Contralor General de la República**;
  - plus (per the standard accounts of the remaining paragraphs) **one former Commander-in-Chief of
    each of the Army, Navy and Air Force and one former Director General of Carabineros**, a **former
    university rector**, and a **former Minister of State** — totalling **nine designated senators on
    eight-year terms**, appointed by the President, the Supreme Court and the **National Security
    Council** (COSENA, acting on armed-forces nominations).
  So: **Senate = 38 elected + 9 designated + lifetime ex-Presidents.** In the 1990–1998 Senate the
  nine designated senators were ~26% of a 47-member chamber — **numerically almost identical to
  Myanmar 2008's 25% military bloc, and arrived at by a completely different mechanism.** That is a
  genuinely strong comparative point for the paper.
  *I verified the 38+9 structure and the COSENA/President/Supreme Court appointment routes from
  secondary sources (Senate of Chile, US Library of Congress Country Study "Chile — The Constitution
  of 1980") and read Art. 45 paragraphs (a)–(c) verbatim; paragraphs (d)–(g) were truncated in my
  extraction. **Verify the exact composition list before publication (L1).***
- **Art. 46**: senators must be ≥40, have 2 years' regional residence, and have completed secondary
  education.
- **Art. 47**: deputies and directly elected senators may be re-elected; vacancies are filled from
  the same electoral list (no by-elections) — a real constitutional rule with no MFU analogue.
- **The binominal electoral system** (two members per district, list-based, requiring a doubling of
  the runner-up list's vote to take both seats) was set by the Ley Orgánica Constitucional sobre
  Votaciones Populares y Escrutinios, not the Constitution itself, but it was **entrenched behind the
  organic-law supermajority**. It systematically over-represented the right. Treat as a parameter with
  a statutory-not-constitutional comment.
- Encode: `MILITARY_RESERVED_SEATS_*` → use a dedicated
  `UPPER_HOUSE_DESIGNATED_SEATS: 9` / `UPPER_HOUSE_DESIGNATED_APPOINTED_BY:
  "president_supreme_court_and_national_security_council"` /
  `UPPER_HOUSE_LIFETIME_SEATS: "former_presidents_six_continuous_years"`, and set
  `MILITARY_SEAT_PERCENTAGE` to the derived ~0.19 of the **Senate** (9/47) rather than of the whole
  Congress (9/167 ≈ 0.054). **Say which denominator you used** — this is exactly the kind of number a
  reviewer recomputes.

### JudiciaryConfig
- **Art. 75** (verbatim, abridged): Supreme Court ministers and fiscales are appointed by the
  President **from a five-person slate (nómina) proposed by the Supreme Court itself**; the most
  senior Court of Appeals minister on the merit list occupies one slate place, the other four on
  merit, and may include persons outside the judiciary. Appeals Court judges: presidential
  appointment from a Supreme-Court-proposed slate of three. **This is judicial self-co-optation plus
  presidential choice — no legislative confirmation at all** (contrast South Korea Art. 104, which
  requires National Assembly consent).
- **Art. 77**: judges hold office during good behaviour; **mandatory retirement at 75** (not
  applicable to the President of the Supreme Court during his term); removal for bad behaviour by a
  **majority of the whole Supreme Court** on the President's requerimiento, a party's request, or the
  Court's own motion.
- **Art. 81 — Constitutional Tribunal (verbatim)**: *"Habrá un Tribunal Constitucional integrado por
  **siete miembros**, designados en la siguiente forma: a) **Tres ministros de la Corte Suprema**,
  elegidos por ésta, por mayoría absoluta…; b) **Un abogado designado por el Presidente de la
  República**; c) **Dos abogados elegidos por el Consejo de Seguridad Nacional**; d) **Un abogado
  elegido por el Senado**, por mayoría absoluta de los senadores en ejercicio."* Members serve
  staggered eight-year terms.
  **Two of seven Constitutional Tribunal members were chosen by the military-majority COSENA.** That
  is a direct military veto channel into constitutional review with no analogue in Myanmar 2008
  (whose Tribunal is presidentially/Hluttaw-appointed) — Chile's design is in this respect *more*
  explicitly military-guardianship than Myanmar's.
- **Art. 82**: Tribunal powers — pre-promulgation review of organic constitutional laws and
  interpretive laws; constitutionality questions arising during the passage of bills, constitutional
  reforms and treaties; constitutionality of decretos con fuerza de ley; plebiscite convocation; and
  (under the 1980 text, via former Art. 8) declaring organisations and persons unconstitutional.
- Encode `JUDGE_COUNT: 7` (Constitutional Tribunal), `COURT_TERM_YEARS: 8`,
  `COURT_INDEPENDENCE: False` for state (a)/(b) **justified on the Art. 81(c) COSENA appointment
  route and Art. 41's non-justiciability of emergency grounds**, not on general impression.

### IIGConfig (anti-corruption body) — Chile genuinely has a strong one
- **Art. 87 (verbatim)**: *"Un organismo autónomo con el nombre de **Contraloría General de la
  República** ejercerá el control de la legalidad de los actos de la Administración, fiscalizará el
  ingreso y la inversión de los fondos del Fisco, de las municipalidades y de los demás organismos y
  servicios que determinen las leyes; examinará y juzgará las cuentas de las personas que tengan a su
  cargo bienes de esas entidades; llevará la contabilidad general de la Nación…"* The **Contralor
  General is appointed by the President with the agreement of the Senate** (majority of senators in
  office).
- **Art. 88**: the Contralor **tomar razón** power — he must register decrees and resolutions or
  represent their illegality; he must give them effect if the President insists with the signature of
  **all** his Ministers, in which case copies go to the Chamber of Deputies; **"En ningún caso dará
  curso a los decretos de gastos que excedan el límite señalado en la Constitución"** (he shall in no
  case give effect to expenditure decrees exceeding the constitutional limit).
- **Art. 89**: no Treasury payment without a competent-authority decree citing the authorising law or
  budget line.
- Statutory additions (post-instrument, for trajectory context): Consejo de Defensa del Estado;
  Ley 19,653 "Ley de Probidad Administrativa" (1999); Consejo para la Transparencia (Ley 20,285,
  operative 2009); Ley 20,393 corporate criminal liability (2009).

**This is the single most important encoding decision in the Chile package.** Chile's Contraloría is
a real, autonomous, constitutionally entrenched fiscal-control body with an **ex ante legality veto**
over executive acts — functionally stronger than anything in the MFU design's IIG on the
expenditure-control axis, and radically stronger than Myanmar 2008's absent body. If `CL` is encoded
with Myanmar-like IIG parameters it will produce a corruption explosion that **directly contradicts
the observed data** (V-Dem political corruption 0.283 under Pinochet, 0.055–0.075 since — among the
cleanest records in Latin America). Encode `ANTI_CORRUPTION_OBJECTIVE: True`,
`REPORTS_TO: "autonomous_constitutional_organ"`, `INITIAL_EFFECTIVENESS` **high**, and document the
Art. 87–89 basis.

### FederalConfig
Unitary with regions (Art. 99–115 in the 1989 text; Chapter XIII "Gobierno y Administración Interior
del Estado"). Intendants and governors were **presidentially appointed** throughout the instrument
(directly elected regional governors only from 2021). No constitutional revenue-sharing formula →
`RESOURCE_*_SHARE` values are proxies. Note the **Ley Reservada del Cobre** (Law 13,196, secret law)
which allocated 10% of CODELCO copper sales directly to the armed forces 1958–2019 — statutory, not
constitutional, but it is the single most important real fiscal-military fact about Chile in this
period and is worth a comment in `EconomicConfig` or `MilitaryConfig`. **Verify the 10% figure and
the 2019 repeal date before quoting (L5).**

### MilitaryConfig — the guardianship core
- **Art. 90 (verbatim, abridged)**: the forces under the Ministry of National Defence consist
  exclusively of the Armed Forces and the Forces of Order and Public Security. *"Las Fuerzas Armadas
  están integradas sólo por el Ejército, la Armada y la Fuerza Aérea, existen para la defensa de la
  patria, son esenciales para la seguridad nacional y **garantizan el orden institucional de la
  República**."* (my translation: …are essential to national security and **guarantee the
  institutional order of the Republic**.) Carabineros is additionally integrated with the Armed Forces
  in the mission of guaranteeing the institutional order.
  **This "garantizan el orden institucional" clause is Chile's direct textual equivalent of Myanmar
  2008 s. 20(f) ("safeguarding the Constitution") and s. 6(f).** It is the strongest single piece of
  evidence for the near-twin claim and should be quoted in the paper side by side with s. 20(f).
- **Art. 91**: entry into the Armed Forces and Carabineros may only be through **their own academies**
  (*"sólo podrá hacerse a través de sus propias Escuelas"*), except for specified professional and
  civilian-employee grades — constitutional insulation of military personnel policy.
- **Art. 92**: no person, group or organisation may possess arms without authorisation; the Defence
  Ministry supervises and controls arms.
- **Art. 93 (verbatim)**: *"Los Comandantes en Jefe del Ejército, de la Armada y de la Fuerza Aérea, y
  el General Director de Carabineros, serán designados por el Presidente de la República de entre los
  **cinco oficiales generales de mayor antigüedad** que reúnan las calidades que los respectivos
  estatutos institucionales exijan para tales cargos; **durarán cuatro años** en sus funciones, **no
  podrán ser nombrados para un nuevo período** y **gozarán de inamovilidad en su cargo**. En casos
  calificados, el Presidente de la República, **con acuerdo del Consejo de Seguridad Nacional**, podrá
  llamar a retiro a los Comandantes en Jefe…"*
  (my translation: service commanders are appointed by the President from the **five most senior**
  qualifying general officers, serve **four years**, cannot be reappointed, and **enjoy
  irremovability**; in qualified cases the President may retire them **only with the agreement of the
  National Security Council**.)
  Since COSENA had a **military voting majority** (see Art. 95), this made the service commanders
  effectively irremovable by civilians. **Repealed by Law 20,050 (2005)**, which restored the
  President's removal power.
- **Art. 94**: appointments, promotions and retirements of officers by supreme decree in conformity
  with the relevant organic constitutional law, which sets the basic rules on career, establishment,
  seniority, command, succession of command **and budget** of the Armed Forces and Carabineros — i.e.
  military budget and promotion rules entrenched behind an organic-law supermajority.
- **Art. 95 (verbatim, abridged) — Consejo de Seguridad Nacional (COSENA)**: *"Habrá un Consejo de
  Seguridad Nacional presidido por el Presidente de la República e integrado por los presidentes del
  Senado y de la Corte Suprema, por los **Comandantes en Jefe de las Fuerzas Armadas**, por el
  **General Director de Carabineros** y por el **Contralor General de la República**."* Ministers of
  interior, foreign affairs, defence and economy/finance participate **with voice but no vote**; the
  Chief of the National Defence Staff acts as Secretary. The Council may be convened by the President
  **or at the request of two of its members**; quorum is an absolute majority of its voting members.
  → Voting members: President + Senate President + Supreme Court President + Contralor (4 civilians)
  vs **4 military** (Army, Navy, Air Force commanders + Carabineros Director). *The commonly-cited
  claim that the military had an "absolute majority" on COSENA reflects the 1980 text before the
  Contralor was added by the 1989 reforms; in the 1989 text it is 4–4 with the President presiding.
  **State this carefully (L3) — do not repeat the "military absolute majority" claim without
  specifying which version of Art. 95 you mean.***
- **Art. 96**: COSENA functions — (a) advise the President on any national-security matter when
  asked; **(b) "Hacer presente al Presidente de la República, al Congreso Nacional o al Tribunal
  Constitucional, su opinión frente a algún hecho, acto o materia que, a su juicio, atente gravemente
  en contra de las bases de la institucionalidad o pueda comprometer la seguridad nacional"** (make
  known to the President, Congress or the Constitutional Tribunal its opinion on any act or matter
  that in its judgement gravely attacks the bases of the institutional order or may compromise
  national security); (c) prior report on Art. 60 No. 13 matters (war declaration); (d) demand any
  security-related information from officials, **whose refusal is legally sanctionable**; (e) elect
  two Constitutional Tribunal members (via Art. 81(c)) and designated senators (via Art. 45/32).
  **Law 20,050 (2005) reduced COSENA to an advisory body convened only by the President.**
- **No coup clause.** Chile's 1980 Constitution contains no emergency transfer of all powers to the
  Commander-in-Chief equivalent to Myanmar 2008 ss. 417–419. `COUP_LEGAL_MECHANISM: False`. The
  guardianship works through tutelary organs (COSENA, designated senators, Tribunal seats,
  irremovability), **not** through a coup authorisation.
- Encode: `MILITARY_POLITICAL_ROLE: True` (Art. 90), `MILITARY_SELF_ADJUDICATION`: partial — military
  courts had wide jurisdiction over civilians under the Code of Military Justice (statutory), and
  Art. 41 bars judicial review of emergency grounds; `COMMANDER_IN_CHIEF_APPOINTMENT:
  "president_from_five_most_senior_four_year_irremovable"`,
  `COMMANDER_REMOVAL_REQUIRES: "national_security_council_agreement"`.

### EconomicConfig / ScienceConfig
- Art. 19 No. 21 (right to undertake economic activity), No. 23 (freedom to acquire property),
  No. 24 (property right, expropriation only by law with prior cash compensation at market value),
  No. 25 (intellectual property). Art. 19 No. 21(2): the State and its organs may undertake business
  activity **only if authorised by a qualified-quorum law**.
- **Art. 97–98**: the Central Bank of Chile as an **autonomous organ with its own constitutional
  rank**, prohibited from acquiring documents issued by the State or granting direct or indirect
  credit to the State (Art. 98), *"salvo en caso de guerra exterior o peligro de ella"*. This is a
  genuinely strong constitutional-independence provision — comparable to MFU's
  `CENTRAL_BANK_INDEPENDENT: True` and in direct contrast to Myanmar 2008. **Encode it.**
- No constitutional tax brackets, royalty rates or research-funding provisions → proxies. Art. 19
  No. 10 (education) and No. 11 (freedom of teaching) are the education provisions; there is no
  PhD-economy analogue.

### AmendmentConfig — verbatim from Art. 116–119 (1989 text)
- **Art. 116**: reform bills may be initiated by presidential message or by any member of Congress,
  with the Art. 62(1) limitations. *"El proyecto de reforma necesitará para ser aprobado en cada
  Cámara el voto conforme de **las tres quintas partes** de los diputados y senadores en ejercicio.
  Si la reforma recayere sobre los capítulos **I, II, VII, XI o XIV**, necesitará, en cada Cámara, la
  aprobación de **las dos terceras partes** de los diputados y senadores en ejercicio."*
  → **3/5 (60%) of members in office in each chamber** for ordinary reforms; **2/3 (66.7%)** for
  Chapter I (Bases de la Institucionalidad), II (Nationality and Citizenship), VII (Constitutional
  Tribunal), XI (**Armed Forces** — i.e. the military chapter is entrenched at 2/3) and XIV (Reform).
- **Art. 117**: 60 days after chamber approval, both chambers meet in **Congreso Pleno** in public
  session, with a majority of total members present, take cognisance and vote **without debate**;
  what the majority of the Congreso Pleno approves goes to the President. If the President **totally
  rejects** a reform and Congress insists in its entirety by **2/3 of members in office in each
  chamber**, the President must promulgate it **unless he submits it to the citizenry by plebiscite**.
  Partial objections follow a parallel route.
- **Art. 118: "Derogado."** **Art. 119**: plebiscite convocation within 30 days of the chambers'
  insistence, by supreme decree fixing a voting date 30–60 days out; if the President fails to
  convoke, the congressional text is promulgated.
- Encode: `STANDARD_AMENDMENT_THRESHOLD: 0.60`, `ENTRENCHED_AMENDMENT_THRESHOLD: 0.667`,
  `ENTRENCHED_CHAPTERS` → `("chapter_1_bases_institucionalidad", "chapter_2_nationality",
  "chapter_7_constitutional_tribunal", "chapter_11_armed_forces", "chapter_14_reform")`,
  `ENTRENCHED_REQUIRES_REFERENDUM: False` (plebiscite is a *presidential option on veto override*, not
  a mandatory step), plus a `PRESIDENTIAL_VETO_OVERRIDE_THRESHOLD: 0.667` and
  `PRESIDENT_MAY_SUBSTITUTE_PLEBISCITE: True`. **No eternity clause.**
- Practical effect: with 9 designated senators + the binominal system, the right held a blocking
  minority against the 3/5 and 2/3 thresholds for 15 years. **This is Chile's functional equivalent of
  Myanmar's 25%-bloc amendment veto, achieved through designated seats + an entrenched electoral law
  rather than through reserved seats + a 75% threshold.** It is the best comparative sentence available
  for the paper's near-twin argument.

### TransitionConfig — the transitory articles (state (a))
Twenty-nine transitory articles governed 11 Mar 1981 – 11 Mar 1990. Key ones, from secondary sources
(the Georgetown 1989-reform text I read does not include them — limitation L4):
- **Transitory Art. 14**: Pinochet continues as President of the Republic for the (eight-year)
  transitional term.
- **Transitory Art. 15**: presidential power to declare a state of emergency at discretion, and a
  state of siege with Junta approval, with suspension of amparo.
- **Transitory Art. 18 / 24**: continued exceptional powers including arrest, internal exile
  (relegación), expulsion and restriction of assembly and information, with limited or no judicial
  review.
- **Transitory Art. 21**: the Junta de Gobierno exercises **constituent and legislative power**;
  no Congress sits.
- **Transitory Art. 27**: the Art. 25 re-election prohibition is inapplicable to the transitional
  term, permitting the Junta's single candidate to stand.
- **Transitory Art. 28–29**: if the citizenry approves the Junta's proposed candidate in the
  plebiscite, he takes office at the end of the transitional term for the full eight years
  (i.e. to 11 March 1997); if rejected, the transitional term is extended by one year and open
  presidential and congressional elections follow.
- **Amnesty**: the regime's self-amnesty is **Decree Law 2,191 of 1978** — a decree law, *not* a
  constitutional provision. It covered acts between 11 Sep 1973 and 10 Mar 1978 and was never
  formally repealed, though Chilean courts increasingly disapplied it for crimes against humanity
  from the late 1990s (Supreme Court jurisprudence and the Inter-American Court's *Almonacid Arellano
  v. Chile* judgment of 2006).
- Encode: `TRANSITION_PERIOD_YEARS: 9` (1981–1990), `AMNESTY_GRANTED: True` with a comment that the
  source is DL 2,191/1978 and **not** the Constitution — an honest and important distinction from
  Myanmar 2008 s. 445, Thailand 2017 s. 279 and Pakistan Art. 270A, all three of which put immunity
  **in the constitutional text**. Chile is the one near-twin where immunity is extra-constitutional
  and was subsequently eroded by courts. `PRIOR_ACTIONS_IMMUNE: True` with that caveat.

### EmergencyConfig — verbatim from Art. 39–41 (1989 text)
- **Art. 39**: five situations permit the exercise of rights to be affected — *"guerra externa o
  interna, conmoción interior, emergencia y calamidad pública"*.
- **Art. 40**: four states of exception:
  - **estado de asamblea** (external war): declared by the President **with the agreement of COSENA**;
  - **estado de sitio** (internal war or internal commotion): declared by the President **with the
    agreement of Congress**, which must accept or reject without modification within **10 days**;
    silence = approval. **But**: *"Sin embargo, el Presidente de la República, previo acuerdo del
    Consejo de Seguridad Nacional, podrá aplicar el estado de sitio de inmediato, mientras el Congreso
    se pronuncia"* — the President may impose it immediately with COSENA's agreement while Congress
    deliberates. Congress may lift an approved state of siege at any time by **absolute majority of
    members in office in each chamber**. Maximum **90 days** per declaration (renewable).
  - **estado de emergencia** and **estado de catástrofe** (public-order disruption, public calamity).
- **Art. 41**: the specific powers under each state — under *asamblea*, suspension or restriction of
  personal liberty, assembly, information and opinion, and work; restriction of association and
  unionisation; censorship of correspondence and communications; requisition of goods; limits on
  property. Under *sitio*, internal transfer of persons, house arrest or detention in non-prison
  locations, suspension/restriction of assembly, and restriction of movement, information and
  opinion. **And the non-justiciability clause quoted under RightsConfig above.**
- **No total-power-transfer clause.** `TOTAL_POWER_TRANSFER_POSSIBLE: False`,
  `LEGISLATURE_SUSPENDED_DURING_EMERGENCY: False`, `EMERGENCY_MAX_DAYS: 90`,
  `EMERGENCY_REQUIRES_COSENA_AGREEMENT: True`, `LEGISLATURE_CAN_LIFT: True` with a 0.50-of-members
  threshold (note: this is a *weaker* legislative kill-switch than South Korea's Art. 77(5), because
  the Chilean President can impose immediately with COSENA agreement and the lift is per-chamber).

### ROEConfig / PsychConfig / CryptoJusticeConfig / NorthStarConfig
No Chilean referent for Crypto-Justice or psychological screening → absent pattern. The nearest thing
to a stated national objective is Art. 1's *bien común* and Art. 90's *garantizan el orden
institucional* — `PROGRESS_METRIC` is a modelling choice. Note the real Chilean "north star" of the
period was the Chicago-School economic programme, which is not in the constitutional text.

---

## 2. Real validation / backtesting data

### 2.1 Transparency International CPI
Access method as in the South Korea package. **CPI begins 1995 — i.e. year 15 of the instrument and
five years after the democratic transition.** There is no CPI observation for the Pinochet period at
all. Do not interpolate.

Chile, 1995–2011 (0–10 scale; TI states pre-2012 scores are not comparable across years):

| 1995 | 1996 | 1997 | 1998 | 1999 | 2000 | 2001 | 2002 | 2003 | 2004 | 2005 | 2006 | 2007 | 2008 | 2009 | 2010 | 2011 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **7.94** | 6.8 | 6.05 | 6.8 | 6.9 | 7.4 | 7.5 | 7.5 | 7.4 | 7.4 | 7.3 | 7.3 | 7.0 | 6.9 | 6.7 | 7.2 | 7.2 |

Chile, 2012–2025 (0–100 scale, TI workbook):

| 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 72 | 71 | 73 | 70 | 66 | 67 | 67 | 67 | 67 | 67 | 67 | 66 | 63 | 63 |

Chile's 1995 score of 7.94 (rank 14) is its all-time CPI high. Verified line by line against TI's
CPI 1995 file: Chile placed above the **United States** (7.79, rank 15), **France** (7.00, 18),
**Belgium** (6.85, 19) and **Japan** (6.72, 20), and immediately below Germany (8.14, 13).
**A military-authored constitution's successor state entered the CPI as one of the cleanest countries
in the index.** This is not a typo; I cross-checked it specifically. (Note: TI's published CPI 1995
covered 41 countries but the archive CSV contains only 40 rows — one row is missing from TI's own
file. Ranks run to 41.)

### 2.2 World Bank Worldwide Governance Indicators
Source: WGI 2023 Update, 1996–2022 (`wgidataset.xlsx`, www.govindicators.org). Point estimates
(−2.5…+2.5):

| Indicator | 1996 | 2000 | 2005 | 2010 | 2015 | 2019 | 2020 | 2022 |
|---|---|---|---|---|---|---|---|---|
| Control of Corruption | **1.45** | 1.54 | 1.42 | 1.44 | 1.18 | 0.98 | 1.11 | 0.97 |
| Political Stability / No Violence | 0.68 | 0.49 | 0.84 | 0.68 | 0.42 | −0.02 | 0.04 | 0.12 |
| Voice & Accountability | 0.72 | 0.89 | 1.29 | 1.10 | 1.00 | 0.98 | 0.99 | 0.97 |
| Government Effectiveness | 1.34 | 1.01 | 1.16 | 1.16 | 0.92 | 0.86 | 0.71 | 0.55 |
| Rule of Law | 1.11 | 1.26 | 1.21 | 1.23 | 1.22 | 0.92 | 0.93 | 0.69 |

Chile's Control of Corruption at **+1.45 in 1996** is higher than South Korea's at any point in the
series (Korea's max is +0.75 in 2022) and within ~0.45 of Germany's. **Chile is a low-corruption
state, and has been for the entire period in which corruption is measurable.**

### 2.3 V-Dem (v16, 2026) — the only source covering the Pinochet period
Access method and citation guidance identical to the South Korea package.
`political-corruption-index` runs 0 = clean → 1 = highly corrupt.

Chile, V-Dem annual, 1981–2005 (the instrument's authoritarian phase and the enclave phase):

| year | 1981 | 1982 | 1983 | 1984 | 1985 | 1986 | 1987 | 1988 | 1989 | **1990** | 1991 | 1993 | 1995 | 1997 | 2000 | 2003 | 2005 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .075 | .075 | .075 | .075 | .078 | .078 | .082 | .111 | .135 | **.721** | .816 | .813 | .850 | .850 | .876 | .880 | .877 |
| liberal dem. | .044 | .045 | .047 | .048 | .048 | .049 | .052 | .060 | .075 | **.630** | .750 | .746 | .783 | .784 | .810 | .817 | .821 |
| **pol. corruption** | **.283** | .283 | .283 | .283 | .283 | .283 | .283 | .283 | .283 | **.067** | .061 | .061 | .061 | .061 | .061 | .061 | .061 |
| rule of law | .375 | .384 | .384 | .384 | .389 | .389 | .389 | .389 | .442 | **.940** | .957 | .957 | .957 | .957 | .958 | .958 | .958 |
| judicial constr. | .315 | .315 | .315 | .315 | .317 | .317 | .317 | .317 | .280 | **.915** | .940 | .940 | .940 | .940 | .940 | .940 | .940 |
| legislative constr. | — | — | — | — | — | — | — | — | — | **.939** | .939 | .939 | .939 | .939 | .939 | .972 | .972 |

Chile, V-Dem annual, 2006–2025:

| year | 2006 | 2008 | 2010 | 2013 | 2015 | 2017 | 2018 | 2019 | 2020 | 2022 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| polyarchy | .894 | .894 | .888 | .894 | .886 | .889 | .870 | .829 | .837 | .833 | .845 | .839 |
| liberal dem. | .839 | .841 | .837 | .846 | .839 | .842 | .803 | .761 | .766 | .776 | .786 | .781 |
| pol. corruption | .061 | .061 | .068 | .076 | .085 | .073 | .055 | .055 | .055 | .064 | .075 | .075 |
| rule of law | .958 | .960 | .960 | .958 | .950 | .950 | .946 | .942 | .944 | .953 | .948 | .951 |
| judicial constr. | .940 | .940 | .947 | .965 | .962 | .962 | .902 | .913 | .931 | .946 | .941 | .941 |
| legislative constr. | .974 | .982 | .982 | .969 | .978 | .980 | .980 | .983 | .982 | .977 | .976 | .976 |

Pre-instrument context: 1970 (Allende) polyarchy .453, pol. corruption .067; 1973 polyarchy .191,
pol. corruption .118.

**The central finding: political corruption under the 1980 Constitution's authoritarian phase was
.283 — lower than South Korea's .458–.512 under its 1987 democratic constitution, and less than half
of Thailand's .683 or Pakistan's .831.** Chile 1980 was a *high-repression, low-corruption*
authoritarian constitution. Polyarchy .075 and liberal democracy .044 are among the lowest values in
this entire dataset; judicial constraints .315 and rule of law .375 are low. **The authoritarianism is
unmistakable in the democracy and constraint indices; it is simply not visible in the corruption
index.** See flag F1.

### 2.4 Coup / transition / constitutional-change event history
Primary dataset: **Powell & Thyne V2026.08.29**
(`https://jonathanmpowell.com/wp-content/uploads/2026/08/pt_20260829.csv`). Chile has **two coded
events**, both in 1973:

| Date | Outcome |
|---|---|
| 1973-06-29 | failed (the *Tanquetazo*) |
| 1973-09-11 | **successful** (Pinochet) |

**Zero coups since 1973. Zero coups under the 1980 Constitution across 45 years.** The 1980
Constitution — a military-authored guardianship document — is, on the coup-survival metric, the
**most successful constitution in this project's entire set after Germany's.**

Constitutional event history:
| Date | Event |
|---|---|
| 1980-09-11 | Approving plebiscite (officially ~67% yes; no registers, no opposition campaign) |
| 1981-03-11 | Constitution enters into force; transitory articles govern |
| **1988-10-05** | Plebiscite on the Junta's single candidate: **"No" 55.99% / "Yes" 44.01%** — Pinochet rejected |
| **1989-07-30** | Reform plebiscite: **54 constitutional reforms approved with 91.25%** |
| 1989-12-14 | Presidential and congressional elections; **Patricio Aylwin 3,850,023 votes (55.17%)** vs Hernán Büchi 29.40% |
| **1990-03-11** | Aylwin takes office; democratic government restored; Pinochet **remains Commander-in-Chief of the Army** (until 1998, then senator for life) |
| 1991 | Rettig Commission report |
| 1998-10-16 | Pinochet arrested in London |
| 2004 | Valech Commission report |
| **2005-08/09** | **Law 20,050** — 58 reforms: designated and lifetime senators abolished; presidential power to remove service commanders restored; COSENA reduced to presidentially-convened advisory status; presidential term cut to four years. *Signed by President Lagos, who declared Chile finally had a democratic constitution.* |
| 2019-10 | *Estallido social* protests |
| **2020-10-25** | Referendum: **78.28%** approve drafting a new constitution |
| **2022-09-04** | First draft **rejected, 61.89% / 38.11%** |
| **2023-12-17** | Second draft **rejected, 55.76% / 44.24%** |
| 2026 | The 1980 Constitution (as amended) remains in force — **45 years and counting** |

Percentages for 1988 (55.99/44.01), 1989 (91.25%), the 1989 election (55.17%), and the 2022/2023
rejections (62/38 and 55.8/44.2) were taken from the Wikipedia articles on the Chilean transition and
the 1989 referendum; the 2020 figure (78.28%) is from the same family of sources. **Verify against
SERVEL (Chile's electoral service) before publication (L2).**

### 2.5 Survey-based trust in government — Chile has the best coverage of the five
| Source | Chile coverage | Notes |
|---|---|---|
| **Latinobarómetro** | **Annual/near-annual 1995–2024**, Chile in every round | `confianza en el gobierno`, plus confidence in congress, judiciary, armed forces, police, political parties. Free registration at latinobarometro.org → Data bank. A published secondary synthesis exists: *Reporte FARO UDD, "Confianza institucional en Chile, 1995–2023"* (faro.udd.cl), which reports 27,593 Chilean observations across the period |
| **CEP (Centro de Estudios Públicos) Encuesta Nacional** | **Since 1986** — the only series that reaches back into the Pinochet period | Institutional-confidence battery. cepchile.cl, free. **This is the single most valuable trust source in the whole project** because it predates the transition |
| **LAPOP AmericasBarometer** | Chile 2006, 2008, 2010, 2012, 2014, 2016/17, 2018/19, 2021, 2023 | System support, trust in institutions. vanderbilt.edu/lapop, free |
| **World Values Survey** | Chile in W2 (1990-94), W3 (1995-98), W4 (1999-2004), W5 (2005-09), W6 (2010-14), W7 (2017-22); listed for W8 (2024-26) | `E069_11`, `E069_07`, `E069_10` |
| **OECD Trust in government** (Gallup World Poll) | Chile since OECD accession (2010); Gallup World Poll covers Chile from 2006 | OECD.Stat |
| **OECD Survey on Drivers of Trust in Public Institutions** | Chile in the 2021, 2023, 2024 rounds, plus the 2025 Latin America and Caribbean round | OECD publications |

**No trust percentages are given here.** All require registered download. See L6.

### 2.6 Recommended year-zero calibration (inference, not a source)
| Field | Proposed value | Basis |
|---|---|---|
| `YEAR_ZERO_CORRUPTION` | **0.283** | V-Dem v16 political corruption index, Chile, **1981** — a real observation at the exact year zero. **Encode this even though it undercuts the near-twin hypothesis; see F1.** |
| `YEAR_ZERO_TRUST` | derive from **CEP 1986** (earliest available) and label it as year-5 | CEP Encuesta Nacional |
| `YEAR_ZERO_COUP_RISK` | needs a judgement call | Powell-Thyne gives 1 success + 1 failure in 1950–1981 ≈ 0.032/yr success rate, which is **low**. Chile was not a chronically coup-prone state; it had one catastrophic coup |
| `YEAR_ZERO_STABILITY` | derive only | WGI begins 1996 (+0.68); no 1981 observation |
| `YEAR_ZERO_GINI` | Chile CASEN survey (from 1987) / World Bank | Chile's income Gini was ~0.56 around 1990 — **verify the exact survey year before using** |

---

## 3. Country-accurate elite role titles for the LLM chain

`chain_type: "military"`. Chile has **two distinct real casts** depending on the instrument state.

**State (a), 1981–1990 (authoritarian phase):**
| Slot | Title | Basis |
|---|---|---|
| 1 | **President of the Republic and Commander-in-Chief of the Army** | Transitory Art. 14; the two offices were held by one person |
| 2 | **Junta de Gobierno** (collectively; members: Commanders-in-Chief of the Navy and Air Force and the Director General of Carabineros) | Transitory Art. 21 — exercised constituent and legislative power |
| 3 | **President of the Supreme Court** | Art. 75, 79 |
| 4 | **President of the Constitutional Tribunal** | Art. 81 |
| 5 | **Contralor General de la República** | Art. 87–88 — the ex ante legality veto |
| 6 | **Minister of the Interior** | Art. 33; the state-of-exception enforcement ministry |
| 7 | **Minister of Finance** (the Chicago-School economic programme's locus) | Art. 33 |

**State (b), 1990–2005 (democratic phase with authoritarian enclaves):**
| Slot | Title | Basis |
|---|---|---|
| 1 | **President of the Republic** | Art. 24–25 |
| 2 | **Commander-in-Chief of the Army** | Art. 93 — four-year, irremovable without COSENA agreement |
| 3 | **President of the Senate** | Art. 45; also a COSENA voting member (Art. 95) |
| 4 | **President of the Chamber of Deputies** | Art. 43, 48 |
| 5 | **President of the Supreme Court** | Art. 75; also a COSENA voting member (Art. 95) |
| 6 | **President of the Constitutional Tribunal** | Art. 81 — two of its seven members chosen by COSENA |
| 7 | **Contralor General de la República** | Art. 87–88; also a COSENA voting member under the 1989 text |
| 8 (if the chain supports 8) | **Designated Senators bloc** (collectively) | Art. 45 — nine seats, the amendment-blocking minority |

**Pick one cast and label the scenario accordingly.** Running state (b)'s cast with state (a)'s
parameters (or vice versa) produces an internally inconsistent scenario. See flag F3.

Historical names, if wanted: **Augusto Pinochet Ugarte** (President 1981–1990, Army CinC to 1998),
Junta members **José Toribio Merino** (Navy), **Fernando Matthei** (Air Force), **Rodolfo Stange**
(Carabineros); Presidents **Patricio Aylwin** (1990–94), **Eduardo Frei Ruiz-Tagle** (1994–2000),
**Ricardo Lagos** (2000–2006, signed Law 20,050).

---

## 4. Honest sourcing limitations

**L1 — Article 45's designated-senator list is partially unverified.** I read Art. 45's opening and
paragraphs (a)–(c) verbatim in Spanish (lifetime ex-Presidents; two former Supreme Court ministers;
one former Contralor General). Paragraphs (d)–(g) — the former service commanders, the former
university rector and the former Minister of State — were truncated in my extraction and are taken
from secondary sources (Senate of Chile; US Library of Congress Chile Country Study). **The total of
nine designated senators and the 38 directly elected senators under the 1989 text are secondary-source
figures.** Verify against the Biblioteca del Congreso Nacional's official text before publication.
Same caveat for the Supreme Court bench strength in the 1980s.

**L2 — Referendum/plebiscite percentages come from Wikipedia-family sources, not SERVEL.** The 1980
plebiscite (~67% yes), 1988 (55.99/44.01), 1989 (91.25%), the 1989 election (55.17%), 2020 (78.28%),
2022 (61.89%) and 2023 (55.76%) all need a primary check against SERVEL or the Tribunal Calificador
de Elecciones. The 1980 figure in particular is contested in the literature because there were no
electoral registers and the vote was held under a state of emergency — **if the paper quotes it,
quote the contestation too.**

**L3 — The "military absolute majority on COSENA" claim depends on which text you mean.** The 1980
text's Art. 95 is commonly described as giving the military an absolute majority. The **1989 text I
read** lists seven voting members: President, Senate President, Supreme Court President, three
service commanders, Carabineros Director General, and the Contralor General — i.e. four civilians and
four uniformed members (counting the Carabineros Director as uniformed), with the President presiding.
Do **not** assert "military majority" without stating which version. The *functional* point —
that Art. 93 removal required COSENA agreement, which the military could block — holds under both.

**L4 — The transitory articles were not read verbatim.** The Georgetown PDBA 1989-reform text does not
include the 29 transitory articles. Everything in TransitionConfig above about transitory Arts. 14,
15, 18, 21, 24, 27, 28, 29 comes from secondary sources (ConstitutionNet's Chile constitutional
history, the International Commission of Jurists' 1992 report *Chile: A Time of Reckoning*, the
Inter-American Commission's 1985 Chile country report, Harvard's Pinochet evidence archive). **If the
paper quotes a transitory article, get the Spanish text from the Biblioteca del Congreso Nacional
first.**

**L5 — Ley Reservada del Cobre.** The 10%-of-CODELCO-sales military funding law (Law 13,196) and its
2019 replacement are widely reported but I did not verify the percentage, the exact legal history or
the repeal date. Do not quote the figure without checking.

**L6 — No trust percentages in this document.** Latinobarómetro, CEP, LAPOP and WVS all require
registered download. Dataset names, coverage years and access routes are verified; values are not.

**L7 — No CPI or WGI observation exists for the Pinochet period.** CPI starts 1995, WGI 1996. The
entire 1981–1990 authoritarian phase is measurable **only** through V-Dem and the CEP survey (from
1986). This is the single biggest data gap in the Chile backtest and it must be stated.

**L8 — Config categories with no Chilean referent:** `CryptoJusticeConfig`, `PsychConfig`, MFU's IIG
academy/partnership machinery, all `ETHNIC_*` fields (the 1980 Constitution made **no** mention of
indigenous peoples; constitutional recognition of the Mapuche and other peoples was precisely what the
2022 draft proposed and voters rejected). Values placed there are modelling choices; comment them.

---

## 5. Flags for Kaung — decide before the engineer encodes

**F1 — Chile is a near-twin on structure and an anti-twin on outcome, and this is the single biggest
analytical risk in the whole 7-constitution design.** The textual case for the near-twin framing is
genuinely strong — arguably stronger than Thailand's:
- Art. 90: the Armed Forces *"garantizan el orden institucional de la República"* — a near-verbatim
  match to Myanmar 2008 s. 20(f)/6(f);
- Art. 93: service commanders irremovable without COSENA agreement;
- Art. 95–96: a tutelary National Security Council with a right to address Congress and the
  Constitutional Tribunal on threats to "the bases of the institutional order";
- Art. 81(c): two of seven Constitutional Tribunal members chosen by COSENA;
- Art. 45: nine designated senators ≈ 26% of the Senate, an amendment-blocking minority against
  Art. 116's 3/5 and 2/3 thresholds;
- Art. 41: emergency grounds expressly non-justiciable;
- a military-drafted text ratified in a plebiscite with no electoral registers under a state of
  emergency.

But the outcome data says:
- **political corruption .283 under Pinochet — lower than democratic South Korea's .458**;
- **CPI 7.94 in 1995, rank 14 of 41 — cleaner than France, Japan and the USA that year**;
- **WGI Control of Corruption +1.45 in 1996 — higher than South Korea has ever recorded**;
- **zero coups in 45 years; the constitution is still in force, having survived two replacement
  attempts that voters rejected (62%, 56%)**;
- the authoritarian enclaves were dismantled **by constitutional amendment** (Law 20,050, 2005), not
  by collapse.

If the manuscript claims Chile clusters with Myanmar 2008 on corruption or collapse trajectories, a
reviewer with V-Dem or CPI access falsifies it immediately. **The recommendation is the same as for
Thailand, and it is stronger here: state the clustering claim on the dimension where it is true.**
Military-authored guardianship constitutions cluster tightly on **suppressed representation and
executive constraint** (Chile 1981: polyarchy .075, liberal democracy .044, judicial constraints .315
— the lowest non-Myanmar values in the set) and **diverge sharply on corruption and survival**. That
is a genuinely interesting, publishable, reviewer-robust finding: *guardianship structure predicts
democratic deficit, not state failure.* It also happens to be a much better answer to Reviewer 2's
"is the divergence structural or parameter-driven?" than uniform clustering would be, because it
identifies **which** structural features drive **which** outcome.

**F2 — Do not copy `C`'s IIG parameters into `CL`.** Chile has an autonomous, constitutionally
entrenched Contraloría General with an *ex ante* legality veto over executive acts (Art. 87–88) and a
constitutionally independent Central Bank barred from lending to the State (Art. 97–98). Setting
`IIGConfig.INITIAL_EFFECTIVENESS = 0.05` because "it's a military constitution" would bake the
conclusion into the input and would be factually wrong. This is the clearest instance in the whole
project where the self-design-bias disclosure logic applies to a *comparator*: the comparator's
parameters must be sourced from its own text, not inherited from the failure baseline.

**F3 — Pick one instrument state and label it.** State (a) (1981–1990, transitory articles, Junta
legislating, no Congress) and state (b) (1990–2005, elected Congress with enclaves) are different
constitutions for simulation purposes. A 50-year run cannot be both. Options:
- encode state (a) and label the scenario `"Chile 1980 (authoritarian phase, 1981–1990)"` — maximum
  contrast, but only 9 years of real instrument life to backtest against, and the transitory articles
  are the part I could not read verbatim (L4);
- encode state (b) and label it `"Chile 1980 as reformed 1989 (authoritarian enclaves, 1990–2005)"` —
  15 years of real life, full verbatim article text available, and the designated-senator/COSENA/
  Tribunal mechanisms are exactly the reserved-powers features the paper wants to test;
- **recommended: state (b)**, because the article text is verifiable, the mechanisms are the ones the
  comparative argument rests on, and the backtest window is longer.

**F4 — Chile's immunity is extra-constitutional and that is a real finding.** Myanmar 2008 s. 445,
Thailand 2017 s. 279 and Pakistan Art. 270A all put regime immunity **in the constitutional text**.
Chile's self-amnesty is Decree Law 2,191 of 1978 — a decree law, progressively disapplied by Chilean
courts and condemned by the Inter-American Court (*Almonacid Arellano*, 2006). Chile is therefore the
one near-twin whose immunity **eroded**, and the one whose generals were eventually prosecuted. That
is a mechanism-level observation worth a paragraph: constitutionalised immunity survives; decreed
immunity does not.

**F5 — Year-zero calibration traceability.** See the South Korea package §5 F4. Chile, like Pakistan,
gives a **real V-Dem observation at the exact year zero** (1981 = 0.283). Use it, and use the same
convention across all seven scenarios.

---

## Schema warning

Same as the other packages: `config/constitution_2008.py` is **missing ≥16 field names the live
engine reads**. **Use `config/constitution.py` as the field-name contract.** A separate engine-level
issue (`self.CONSTITUTION` assigned at `model_phase3.py:164/167` but never read elsewhere; agent and
feedback modules import MFU's `CONSTITUTION` at module level unconditionally) has been reported to
the parent agent — it determines whether any of these parameters affect the simulation at all.
