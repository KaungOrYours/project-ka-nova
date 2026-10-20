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

---

# 6. Administrative geography, population structure, and real geopolitical context

*Added 2026-10-20 by `senior-researcher`, per `.claude/memory.md` section 11's standing realism
requirement and its "each country's own real neighbours" extension. Additive only; nothing above has
been changed. Every figure carries dataset, publisher, year and access method. Inferences are labelled
INFERENCE and never presented as observations.*

## 6.1 Real year-zero national population — and an unresolved year-zero inconsistency

| Quantity | Value | Source |
|---|---|---|
| Population, 1990 | **13,437,176** | World Bank World Development Indicators, indicator `SP.POP.TOTL`, country `CHL`, year 1990. Accessed 2026-10-20 via `https://api.worldbank.org/v2/country/CHL/indicator/SP.POP.TOTL?date=1990&format=json` |
| Population, 1981 | **11,678,717** | Same series, year 1981 |
| 1992 Census (22 April 1992), effectively-censused regional sum | 13,231,803 | Instituto Nacional de Estadísticas (INE) 1992 census, regional figures via statoids.com's INE-sourced population-history table (accessed 2026-10-20) |
| 1992 Census, published "población total" | 13,348,401 | INE 1992 census (the difference from the line above is the standard *población efectivamente censada* versus omission-adjusted total distinction) |
| 1982 Census (21 April 1982), regional sum | 11,275,440 | INE 1982 census, same table |

**INCONSISTENCY TO RESOLVE BEFORE ENCODING (flag F1).** Kaung's locked decision (memory.md §4a,
decision 4) was to encode the **1990-2005 elected-Congress era**. But
`config/constitution_chile.py`'s `YEAR_ZERO_CORRUPTION = 0.283` is sourced to **V-Dem Chile 1981**,
and this package's own §2.6 and flag F5 both treat 1981 as year zero. The two are nine years apart
and they give materially different populations (13,437,176 versus 11,678,717), different V-Dem values,
and different state-GDP baselines. The task brief for this appendix specifies **Chile 1990**, so 1990
is used below — but the corruption, trust, stability and GDP year-zero values in the Python file are
all still on the 1981 basis and must be moved to 1990 if 1990 is the chosen year zero. **Do not leave
the population on 1990 and the corruption on 1981.** This is the kind of mismatch a reviewer checking
the reproducibility package will find.

**Citizen count at the confirmed 1:5000 ratio: 13,437,176 / 5000 = 2,687 citizens** (2,336 if 1981 is
used instead). **This is by far the smallest of the seven scenarios — roughly one quarter of
Myanmar's locked 11,000 and one seventh of Pakistan's 19,646.** See flag F4; this is the most serious
problem surfaced by this whole task.

## 6.2 Real administrative geography — 13 regions is exactly correct for 1990-2005

Good news: `FoundationalConfig.STATE_COUNT = 13` and `FederalConfig.STATE_COUNT = 13` are **already
right**, and right for a real reason. Chile's regionalisation (DL 575 of 1974, completed by the 1976
reorganisation) created 12 numbered regions plus the Región Metropolitana de Santiago, and that
structure stood unchanged for the entire encoded window. The three later regions are all outside it:

| Later region | Created by | In force |
|---|---|---|
| Los Ríos (XIV), split from Los Lagos | Law 20,174 | 2 October 2007 |
| Arica y Parinacota (XV), split from Tarapacá | Law 20,175 | 2 October 2007 |
| Ñuble (XVI), split from Biobío | Law 21,033 | 6 September 2018 |

Two things to fix:
- **`FoundationalConfig.SIMULATION_STATE_COUNT = 14` is a Myanmar leftover** (its own comment says it
  was kept at 14 to avoid diverging from constitution_2008.py). It should be **13**.
- **`SimulationConfig.SIMULATION_STATES` still holds Myanmar's 14 state names verbatim**
  (`sagaing`, `mandalay`, ... `rakhine`). It must be replaced with the 13 real regions.

### Population shares, 1992 Census (the first census of the elected-Congress era)

Source: INE 1992 Census (22 April 1992), regional figures via statoids.com's INE-sourced population
history table (accessed 2026-10-20). Shares computed on the effectively-censused sum of 13,231,803.

| Unit (encode as) | Real name | 1992 census pop. | Share | Citizens @1:5000 (of 2,687) |
|---|---|---|---|---|
| `metropolitana` | Región Metropolitana de Santiago (RM) | 5,170,293 | 39.07% | 1,050 |
| `biobio` | Región del Biobío (VIII) | 1,729,920 | 13.07% | 351 |
| `valparaiso` | Región de Valparaíso (V) | 1,373,967 | 10.38% | 279 |
| `los_lagos` | Región de Los Lagos (X) | 953,330 | 7.20% | 194 |
| `maule` | Región del Maule (VII) | 834,053 | 6.30% | 169 |
| `araucania` | Región de La Araucanía (IX) | 774,959 | 5.86% | 157 |
| `ohiggins` | Región del Libertador General Bernardo O'Higgins (VI) | 688,385 | 5.20% | 140 |
| `coquimbo` | Región de Coquimbo (IV) | 502,460 | 3.80% | 102 |
| `antofagasta` | Región de Antofagasta (II) | 407,409 | 3.08% | 83 |
| `tarapaca` | Región de Tarapacá (I) | 341,112 | 2.58% | 69 |
| `atacama` | Región de Atacama (III) | 230,786 | 1.74% | 47 |
| `magallanes` | Región de Magallanes y de la Antártica Chilena (XII) | 143,058 | 1.08% | 29 |
| `aysen` | Región de Aysén del General Carlos Ibáñez del Campo (XI) | 82,071 | 0.62% | 17 |
| | **total** | **13,231,803** | 100.00% | 2,687 |

### The structural point this geography carries

**Santiago is 39.1% of the national population in a 13-region *unitary* state whose regional
*intendentes* were appointed by the President** (Art. 100-101 of the 1980 text), not elected. Chile's
"states" had no autonomous political authority whatsoever — the first direct election of regional
governors was in 2021, sixteen years after the encoded window closes. So:

- The MFU 35/35/30 federal-resource-share machinery has **no Chilean referent at all** and
  `FederalConfig` should be near-inert by design for CL. If it runs on MFU-like values, the simulation
  will model a decentralisation that did not exist.
- But the **geographic Gini** (memory.md bug #2: Phase 3's live Gini is computed from the 14 states'
  GDP levels, not citizen income) becomes *more* meaningful for Chile than for Myanmar, because
  Chile's regional output concentration — Santiago's services economy against Antofagasta/Atacama's
  copper enclaves against Araucanía's poverty — is extreme and well documented. Worth telling
  `senior-data-analyst`: the 13 real regions with real population weights make Chile's Gini
  interpretable in a way Myanmar's 14 equally-sized synthetic states are not.
- Aysén at 17 citizen agents and Magallanes at 29 are **very small samples**. At 2,687 total agents
  the smallest regions become statistically meaningless. This is a direct argument against
  ratio-derived N (flag F4).

## 6.3 `ETHNIC_GROUPS = 0` is correct — use socioeconomic strata instead, not a fabricated ethnic array

`ETHNIC_GROUPS = 0` is correct and should be preserved. The 1980 Constitution recognised **no**
indigenous peoples; the Ley Indígena 19,253 was enacted only on 5 October 1993 (simulated year 3-4 on
a 1990 start) and is ordinary legislation, not constitutional; and **constitutional recognition has
failed twice**, with voters rejecting the 2022 draft (which would have established a plurinational
state) and the 2023 draft. The 1992 Census was the first to ask an indigenous-identification question
at all, returning 998,385 self-identified Mapuche among respondents aged 14 and over (~10%). An
8-slot ethnic array for Chile would be a fabrication.

### Recommended primary composition: socioeconomic stratum

Chile's documented first-order cleavage in this window is **class**, not ethnicity. The file already
encodes `YEAR_ZERO_GINI = 0.56` — among the highest income Ginis in the world at the time, and the
highest in this seven-country set by a wide margin. That is the cleavage the composition array should
carry.

Real sources, both retrievable and both Chilean-official:
- **CASEN** (Encuesta de Caracterización Socioeconómica Nacional), MIDEPLAN / later Ministerio de
  Desarrollo Social, biennial from **1987**. Gives poverty headcount and income distribution **by
  region**, which is exactly the per-unit array shape needed, and it begins before year zero.
- The **ABC1 / C2 / C3 / D / E** socioeconomic classification standard in Chilean survey research,
  which gives a defensible 5-category stratum scheme.

Recommended per-unit array: 3-5 income/socioeconomic strata from CASEN, with CASEN 1990 as the
year-zero anchor. **I did not extract CASEN figures** — see §6.7 L2. Do not substitute invented
numbers; this is a genuine, closeable gap, not an unanswerable one.

### Recommended secondary composition: indigenous share in the southern macrozone

Genuinely real and genuinely consequential within the window: the **Mapuche land conflict**,
concentrated in Araucanía (IX) with spillover into Biobío (VIII) and Los Lagos (X). Dated within or
just after the window: the Lumaco arson attacks (December 1997), the application of the Pinochet-era
Ley Antiterrorista (18,314) to Mapuche defendants, the killing of Matías Catrileo (2008) and Jaime
Mendoza Collío (2009), the killing of Camilo Catrillanca (14 November 2018), and the *macrozona sur*
state of emergency from 2021. Indigenous-population shares by region are available from the 1992
census question onward (INE).

Encode this as a **regional composition category explicitly labelled non-constitutional**, never as a
constitutional ethnic group — because the entire point about Chile is that the 1980 Constitution gave
indigenous peoples no standing, and encoding them as a recognised group would erase the finding.

## 6.4 Real neighbours and major-power relationships — replacing Myanmar's vector set

Chile's external situation is the most different in kind from Myanmar's of all five new countries.
There is no large neighbouring hegemon, no regional bloc that matters much, no significant illicit
economy, and the dominant external variable is **not a country at all** — it is the copper price.

| Vector | Real relationship in 1990 | Real nature | Notes for the engine |
|---|---|---|---|
| `copper_price` | **The single most important external variable, and it is a commodity, not a state.** Copper was ~30% of Chile's export value in 1991; Codelco's four mines produced 1.14 million tonnes in 1990. Critically: **Law 13,196 ("Ley Reservada del Cobre", 29 October 1958, amended under the military government and in force until its 2019 replacement) directed 10% of Codelco's gross copper sales directly to the armed forces, with a US$180m floor, bypassing Congress entirely** | Commodity dependence **coupled to the military budget by law** | **Strong recommendation to encode this explicitly as a vector.** It is the only case in the 7-constitution set where an external *price* is legally wired into the guardianship institution's budget. The military's fiscal autonomy from the elected Congress — the heart of the reserved-powers design — literally varied with the LME copper price |
| `argentina` | The primary historical security relationship, and a real near-war: the Beagle Channel dispute brought both to the brink in December 1978 (*Operativo Soberanía*), resolved by papal mediation and the Treaty of Peace and Friendship signed 29 Nov 1984, in force 2 May 1985. By 1990 the relationship had inverted into Chile's deepest bilateral tie, but 24 of 26 boundary disputes were still unresolved at year zero (settled through the 1990s: Laguna del Desierto arbitration 1994, Campo de Hielo Sur partial agreement 1998). Also Chile's largest import source (7.16% of imports in 1990, World Bank WITS) and its gas supplier | Former near-adversary turned partner and energy supplier | Must **invert** mid-run, and carries a real dated shock (the 2004-2008 gas cutoffs) |
| `peru_bolivia` | War of the Pacific (1879-83) legacy. **Bolivia has had no full diplomatic relations with Chile since 17 March 1978** — a standing severance across the entire simulated window — over the landlocked sea-access claim; Bolivia sued Chile at the ICJ in 2013 and lost on 1 October 2018. Peru sued Chile over the maritime boundary (2008-2014, judgment 27 January 2014) | **Low-trade, high-grievance, non-military-threat.** A relationship *type* Myanmar's vector set has no slot for | Low magnitude, persistent, occasionally spiking via legal rather than military channels |
| `usa` | A dated, two-directional relationship: the US imposed an arms embargo under the Kennedy Amendment (1976, following the 21 September 1976 Letelier car-bombing in Washington DC), lifted after the 1990 democratic transition; the US was then Chile's **largest export market, 16.76% in 1990** (World Bank WITS). US-Chile FTA in force 1 January 2004 | Sanctioner at the start of the preceding period, largest market at year zero | Should rise sharply at year zero — the democratic transition's main external dividend |
| `european_judicial` | **Unique to Chile and genuinely important.** Spain's Judge Baltasar Garzón issued the warrant that led to **Pinochet's arrest in London on 16 October 1998**, and the UK House of Lords ruled on 24 March 1999 that he had no head-of-state immunity for torture | **External judicial intervention against the regime's principals** | No analogue in any other scenario. Should be a *named shock type*, not folded into `sanctions`. It struck the Chilean constitutional settlement directly, at simulated year 8 |
| `japan_asia_pacific` | Japan was Chile's second-largest export market in 1990 (16.24%, World Bank WITS). Chile joined APEC in November 1994 | Market diversification | Rising |
| `global_trade_regime` | Chile's strategy was **unilateral opening plus bilateral FTAs, not bloc membership**: FTAs with Canada 1997, the EU 2002, the US 2004, China 2006; OECD accession 7 May 2010; **Mercosur associate member (1996) but never a full member** | Open-economy exposure | **The ASEAN-equivalent vector should be weak.** Chile deliberately avoided deep regional integration, the opposite of Myanmar's ASEAN entanglement |
| `foreign_investors` | High and rising — Chile was the Latin American FDI success case of the 1990s, largely into mining | FDI | High at year zero, unlike Myanmar's 0.20 |

**Deliberately absent: illicit networks.** Chile has no real mid-window analogue of Myanmar's
drug-production economy. It is a cocaine-transit country via the northern border with Peru and Bolivia,
but at a scale and political salience nowhere near Myanmar's three-vector structure.
**Recommend 0, or at most 1 low-value vector, and state in the methods that this is a real structural
absence rather than missing data.** Myanmar runs three; copying them to Chile would manufacture a
similarity that does not exist, which is the exact failure mode section 11 warns about.

**Deliberately absent: China/India/ASEAN/UN-humanitarian as significant vectors.** China becomes
Chile's largest trade partner later (post-2006 FTA, overtaking the US around 2010) and should rise
late in the run, but at year zero it is minor.

## 6.5 Historically-calibrated shock types for Chile, 1990-2040

| Shock | Real basis (dated) | Comment |
|---|---|---|
| `copper_price_shock` | The dominant shock. Real troughs: the 1998-99 Asian-crisis collapse, the 2008-09 crisis, the 2015-16 decline | **Dual-channel for Chile uniquely**: hits both the fiscal/export economy *and*, via Law 13,196's 10% rule, the armed forces' budget. A copper crash mechanically weakens the guardianship institution |
| `earthquake_tsunami` | Chile is the most seismically active country in the set. 3 March 1985 Algarrobo M7.8 (just before the 1981-1990 window's end); **27 February 2010 Maule M8.8**, roughly 525 deaths and ~US$30bn in damage, on the order of 18% of GDP (World Bank); 1 April 2014 Iquique M8.2 | Replaces Myanmar's generic `natural_disaster` with a far higher real magnitude and a much higher base rate |
| `foreign_judicial_action` | Pinochet's London arrest 16 Oct 1998; House of Lords immunity ruling 24 Mar 1999 | **New type, no analogue elsewhere.** The real external test of this constitution's amnesty/immunity architecture — and note this package's own §5 F-flag finding: Chile's immunity was *decreed* (DL 2,191 of 1978), not constitutionalised, and it eroded, unlike Thailand's s.279 and Pakistan's Art. 270A |
| `gas_supply_cutoff` | Argentine natural-gas export restrictions and cutoffs, 2004-2008 | New type. Energy-security shock from a *partner*, not an adversary |
| `financial_contagion` | Asian financial crisis 1998-99 — Chile's only recession of the period | Transfers as `global_recession` but with a specific dated instance |
| `mass_protest_constitutional_crisis` | **18 October 2019 *estallido social*** → the 15 November 2019 cross-party Agreement for Peace and a New Constitution → the 25 October 2020 plebiscite (78% for a new constitution) → the 4 September 2022 draft rejected (62%) → the 17 December 2023 draft rejected (55%) | **The most important shock type for this scenario.** The real within-window stress test of the 1980 Constitution, and the constitution *survived it*. The engine must be able to produce "severe legitimacy crisis, constitution survives" as an outcome — otherwise Chile's documented anti-twin result (§2.4, zero coups in 45 years, constitution still in force) cannot be reproduced no matter what the parameters say |
| `indigenous_conflict_escalation` | Lumaco arson Dec 1997; Catrillanca killing 14 Nov 2018; *macrozona sur* state of emergency from 2021 | Localised to `araucania` / `biobio` / `los_lagos` |
| `pandemic` | COVID-19 | Transfers |
| `drought_water_rights` | The 1981 Water Code's fully tradeable private water rights, constitutionally protected via Art. 19 No. 24; central-Chile megadrought from 2010 | New type. A constitutional-property-rights mechanism meeting an environmental shock — directly relevant to the 2022 draft's water provisions |
| `fdi_boom` (positive) | 1990s mining FDI surge; OECD accession 2010 | Transfers |

## 6.6 Citizen count summary

| Quantity | Value |
|---|---|
| Year zero | **1990** per the task brief and Kaung's decision 4 (elected-Congress era) — but see flag F1, the Python file's own year-zero values are on a 1981 basis |
| Real population | 13,437,176 (World Bank WDI `SP.POP.TOTL`, CHL, 1990) |
| Ratio | 1:5000 (confirmed by Kaung) |
| **Citizen agents** | **2,687** |
| Alternative on a 1981 year zero | 2,336 (from 11,678,717) |
| For comparison, locked Myanmar value | 11,000 |

## 6.7 Sourcing limitations and flags

**L1 — 1992 regional figures are via statoids.com, which cites INE but is a secondary compiler.** The
13 regional figures sum to 13,231,803 against INE's published *población total* of 13,348,401, a
116,598 gap consistent with the standard effectively-censused-versus-adjusted distinction. citypopulation.de's
Chile page carries no 1992 column (its earliest is 2002), and the INE 1992 results are held by the
Biblioteca Nacional Digital (record BND:86209, "Resultados oficiales censo de población 1992:
población total país, regiones, comunas, por sexo y edad"), which I did not retrieve. **A human should
pull the INE 1992 regional table directly before these figures appear in a manuscript table.**

**L2 — no CASEN figures extracted.** §6.3's recommended socioeconomic-stratum composition is a
*method* recommendation with a named, real, retrievable source (CASEN, MIDEPLAN, biennial from 1987,
regional disaggregation), but **no numbers**. A commonly-cited CASEN 1990 national poverty headcount of
around 38-39% circulates; I did not verify it against the MIDEPLAN/Ministerio de Desarrollo Social
series and it should not be used until verified. This is the main closeable gap in Chile's package.

**L3 — indigenous shares by region not extracted.** Available from INE's 1992 census indigenous
question onward. Only the national Mapuche figure (998,385 aged 14+) is sourced here.

**L4 — `YEAR_ZERO_TRUST = 0.35` and `YEAR_ZERO_EMPLOYMENT = 0.60` remain unsourced** (already flagged
in `constitution_chile.py` and in this package's §4/L6). Nothing here fixes them. CEP's *Encuesta
Nacional* (from 1986) remains the right trust source and still requires registered download.

**F1 — YEAR-ZERO YEAR MISMATCH, must be resolved before encoding** (§6.1). Population on 1990 and
corruption/trust/stability on 1981 is not a defensible combination. Pick one year and apply it to
population, V-Dem, WGI-derived and state-GDP baselines together.

**F2 — fix `SIMULATION_STATE_COUNT` 14 → 13 and replace Myanmar's state names** in
`SimulationConfig.SIMULATION_STATES`.

**F3 — encode `FederalConfig` as near-inert for Chile** (§6.2). Chile's regions had zero autonomous
political authority until 2021. Running MFU-like resource-share values would model a federalism that
never existed.

**F4 — THE MOST SERIOUS FLAG FROM THIS WHOLE TASK. Chile at 2,687 agents is a statistical-power
problem, not a detail.** Ratio-derived N across the seven scenarios: Pakistan 19,646, Thailand 14,232,
Germany 9,969, South Korea 8,406, **Chile 2,687**, versus Myanmar's locked 11,000. Chile would run on
roughly **one seventh** of Pakistan's population and **one quarter** of Myanmar's. Across 100 Monte
Carlo runs this guarantees systematically wider confidence intervals for Chile **for reasons that have
nothing to do with constitutional structure** — which is exactly Reviewer 2's "divergence may be
parameterisation-driven rather than structural" objection relocated into population size, and it is
the kind of thing the Stage-5 adversarial reviewer simulation would have caught. It is made worse by
Chile's own geography: at 2,687 agents, Aysén gets ~17 agents and Magallanes ~29, which are not
samples in any meaningful sense. Three options, all needing Kaung:
(a) ratio-derived N everywhere — most realistic, worst comparability, and Chile becomes noisy;
(b) **11,000 agents for every scenario** — best statistically, abandons the ratio's realism rationale,
    and is the option this flag recommends on defensibility grounds;
(c) ratio-derived N **plus** mandatory reporting of per-scenario N and the N-driven component of CI
    width in every results table — defensible only if stated up front, never discovered by a reviewer.
Note also that the ratio rule does not reproduce the existing baseline: Myanmar's locked 11,000
implies 55,000,000, but Myanmar's own World Bank 2008 population is 48,390,793, i.e. 9,678 at 1:5000.
