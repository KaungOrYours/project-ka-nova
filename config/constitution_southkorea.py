"""
================================================================================
PROJECT KA-NOVA
config/constitution_southkorea.py

South Korea 1987 Democratization Constitution — Parameter Registry
Ka-Nova Simulation Engine — Scenario SK (chain_type: "civilian")

Instrument encoded: Constitution of the Republic of Korea, 1948, as wholly
revised by the Ninth Amendment of 1987 ("1987 Constitution", Sixth Republic).
Referendum: 28 October 1987 (94.46% in favour). In force: 25 February 1988.
Zero amendments since. Simulation year-zero = 1988.

Source: Constitute Project, "Korea (Republic of) 1948 (rev. 1987)"
        https://www.constituteproject.org/constitution/Republic_of_Korea_1987
Research package (article citations, CPI/V-Dem/WGI validation tables, elite
role sourcing, honest limitations L1-L7, flags F1-F5):
        config/constitution_southkorea_encoding/README.md
Structural template: config/constitution_2008.py (confirmed complete 86-field
engine-read contract as of 2026-10-20 per .claude/memory.md bug #11).
Author: Kaung Htet (architecture) / Claude Code (encoding, 2026-10-20)
License: MIT
================================================================================

TAGGING CONVENTION (matches constitution_2008.py)
--------------------------------------------------
CONFIDENT — directly supported by an article citation, a named V-Dem/CPI/WGI
            figure, or a well-documented real-world fact with no plausible
            alternative reading.
GUESS      — a modelling proxy, a statutory (not constitutional) figure not
            independently re-verified against a primary source, or a value
            Ka-Nova itself must choose because no real figure exists for this
            schema slot. Direction may still be CONFIDENT even where
            magnitude is a GUESS; both are called out explicitly per field.

CORRECTED FRAMING — DO NOT USE "ZERO COUPS SINCE 1987"
--------------------------------------------------------
.claude/memory.md previously justified South Korea partly on a "zero coups
since 1987" claim. This is withdrawn per the research package's explicit
instruction (README §5, flag F1): a sitting President (Yoon Suk Yeol)
declared martial law on 2024-12-03 and deployed troops to the National
Assembly. The defensible claim used throughout this file instead is the
**122-day self-correction**: Art. 77(5) legislative lift (National Assembly
190-0, 2024-12-04) -> Art. 65(2) impeachment (204/300, 2024-12-14) ->
Art. 111/113 Constitutional Court unanimous removal (2025-04-04) -> criminal
conviction (2026-02-19). Three independent constitutional mechanisms fired in
sequence and the constitution survived without rupture. This is the framing
this file's MilitaryConfig / EmergencyConfig / TatmadawTransitionConfig
sections encode — low-but-nonzero coup risk, a genuinely binding legislative
emergency kill-switch, and no amnesty — never an absolute-zero risk floor.

KNOWN ENGINE WIRING GAP — DISCOVERED WHILE ENCODING THIS FILE, 2026-10-20
--------------------------------------------------------------------------
.claude/memory.md's bug #11 entry records model_phase3.py's own self.CONSTITUTION
dispatch and agents/official.py's _build_official_roles() as fixed to read the
live, scenario-correct constitution object. Verified true. BUT every other
module that reads constitutional parameters — agents/citizen.py,
agents/oversight.py, agents/institutional.py, agents/foreign.py,
institutions/chambers.py (all paths except the trust-read bug and
CITIZENS_ASSEMBLY_SIZE, both already fixed), institutions/court.py,
institutions/iig.py, feedback/loops.py, engine/cves.py, analysis/kpi.py — all
still contain an unconditional `from config.constitution import CONSTITUTION`
at module level (confirmed by direct grep, 2026-10-20) and read that bare MFU
singleton directly, NOT model.CONSTITUTION. This means the large majority of
the parameter values encoded below (chamber vote thresholds, IIG mechanics,
judiciary mechanics, economic/science/psychology/crypto-justice fields, rights
grievance/trust-drop deltas, military COUP_TRIGGER_LOYALTY/APPROVAL, federal
resource shares, SIMULATION_STATES, ARCHETYPES) are CURRENTLY INERT for every
scenario including the already-"fixed" Scenario C, not just SK — the engine
will run SK correctly at the level of chain_type dispatch
(_civilian_chain_rules, the coup-risk roll, the tatmadaw_transition trust
gain, and official-agent term/merit floors via _build_official_roles), but
most of the deeper, real South-Korea-specific parameters below will have NO
mechanical effect until that broader wiring gap is fixed in agents/engine/
institutions/feedback (out of this file's scope — this is a config file, not
an engine file). Each field below is still filled with a real, sourced value
regardless, both because the contract requires it and because it will
silently start mattering correctly the moment that gap is fixed, with zero
further edits needed to this file.

SCHEMA-MAPPING DISCLOSURE (per research README §5 flag F5)
-------------------------------------------------------------
South Korea is a semi-presidential unitary republic encoded into a schema
built for Myanmar's federal, ceremonial-president/executive-chancellor,
multi-ethnic design. Mapping choices made throughout this file:
  - President (Art. 66/67/70/74) -> ExecutiveConfig.PRESIDENT_* (real
    executive power, not ceremonial, unlike MFU's own President).
  - Prime Minister (Art. 86) -> ExecutiveConfig.CHANCELLOR_* fields (PM is a
    real office here, unlike constitution_2008.py where it is "none").
  - Constitutional Court (Art. 111-113) -> ChamberConfig.ANALYSIS_* and
    JudiciaryConfig fields (the Court, not a second chamber, performs the
    MFU Analysis Council's constitutional-review function).
  - Board of Audit and Inspection (Art. 97-100) -> IIGConfig (the
    constitutionally-grounded anti-corruption/audit body; Korea has no
    Myanmar-style IIG or MFU-style academy-trained anti-corruption agency).
  - Impeachment-to-Constitutional-Court-removal pathway (Art. 65, 111, 113)
    -> CryptoJusticeConfig.TOTAL_RUIN_* (a real "total removal from office"
    mechanism, just not blockchain-based — repurposed field names, not a
    literal crypto-justice system).
These are Ka-Nova's own mapping decisions, defensible but not neutral; they
should be stated in the manuscript's methods per the research package's own
instruction, not left as unexplained field choices.

ETHNIC CHANNEL IS INERT FOR THIS SCENARIO
--------------------------------------------
Korea has no constitutionally recognised multi-ethnic structure (research
README §1 FoundationalConfig note). Every ETHNIC_* field, ethnic resource
share, and ethnic_weights default in this file is set to a neutral/zero/
unreachable value and documented as such, rather than inventing an ethnic
cleavage structure that has no real referent. This mirrors the same
"mechanism absent, nullify via parameter value, not a code branch" idiom
constitution_2008.py already uses for MFU-specific mechanisms Myanmar lacks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL — Art. 1-9, 117-118
# Maps to: constitution.py / constitution_2008.py -> FoundationalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Art. 1-9 (basic principles), 117-118 (local autonomy)"""

    # CONFIDENT — Art. 1.
    STATE_NAME: str = "Republic of Korea"
    # CONFIDENT real-world fact; GUESS re: no explicit constitutional
    # language article found in the research package's article rendering.
    OFFICIAL_LANGUAGE: str = "Korean"
    # CONFIDENT — no constitutionally recognised ethnic-minority language
    # protection clause exists; Korea's structure is fundamentally different
    # from Myanmar's multi-ethnic federal design (research §1 note).
    ETHNIC_LANGUAGES_PROTECTED: bool = False
    # CONFIDENT real-world fact. GUESS on constitutional status: Seoul's
    # status as capital was held by the Constitutional Court (2004,
    # "capital relocation case") to be an unwritten constitutional custom,
    # not explicit 1987 text — not independently re-verified against a
    # primary source in the research package.
    CAPITAL: str = "Seoul"
    # GUESS — real-world fact (Taegeukgi), not covered by the research
    # package's article citations.
    FLAG: str = "taegeukgi"
    # CONFIDENT direction — Art. 2(1): "The requirements for being a citizen
    # of the Republic of Korea shall be prescribed by Act" (delegates to the
    # Nationality Act, outside the constitutional text and outside this
    # research package's scope). GUESS on the exact enumerated modes.
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "jus_sanguinis_nationality_act",
        "naturalization_by_law_article_2",
    )
    # GUESS — real-world Nationality Act figure (5-year continuous
    # residence), statutory not constitutional, not independently verified
    # against a primary source in the research package.
    NATURALIZATION_YEARS: int = 5
    # CONFIDENT — no merit-exam-gated naturalization exists.
    NATURALIZATION_MERIT_MIN: float = 0.0
    # CONFIDENT — Art. 3: "The territory of the Republic of Korea shall
    # consist of the Korean peninsula and its adjacent islands."
    TERRITORY_BASIS: str = "korean_peninsula_and_adjacent_islands_article_3"
    # CORRECTED 2026-10-20 per research README §6.2: 17 is the PRESENT-DAY
    # count of Korea's first-level administrative divisions, not the count
    # at simulation year zero (Feb 1988). Daejeon did not become a directly
    # governed city until 1 Jan 1989 (simulated year 1), Ulsan not until
    # 15 Jul 1997 (simulated year 9), Sejong not until 2 Jul 2012 (simulated
    # year 24) — all three postdate the 1988 scenario start and were still
    # part of Chungcheongnam-do / Gyeongsangnam-do respectively at year
    # zero. The real year-zero count is 14 (Seoul Special City + Busan/
    # Daegu/Incheon/Gwangju directly-governed cities + 9 provinces),
    # independently confirmed by the 13th presidential election's
    # (16 Dec 1987) province-level results table having exactly 14 rows
    # (README §6.3). GUESS-tagged modelling choice (STATE_COUNT itself has
    # no constitutional basis, Art. 117-118 is unitary, not federal) but
    # CONFIDENT on the real-world count being 14, not 17, at year zero.
    # 14 also removes a cross-scenario confound: Myanmar A/C both run on 14
    # states, so an A-vs-SK difference is no longer partly attributable to
    # geographic granularity (exactly the "parameterisation-driven, not
    # structural" objection Reviewer 2 raised, relocated into state count).
    STATE_COUNT: int = 14
    SIMULATION_STATE_COUNT: int = 14


# ══════════════════════════════════════════════════════════════════════════════
# RIGHTS — Chapter II, Art. 10-39
# Maps to: constitution.py / constitution_2008.py -> RightsConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Chapter II — Rights and Duties of Citizens (Art. 10-39)"""

    # CONFIDENT — direct article citations.
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "human_dignity_and_pursuit_of_happiness_article_10",
        "equality_before_the_law_article_11",
        "personal_liberty_article_12",
        "freedom_of_conscience_and_religion_articles_19_20",
        "freedom_of_speech_press_assembly_association_article_21",
        "right_to_education_article_31",
        "right_to_work_article_32",
        "right_to_healthy_environment_article_35",
    )
    # CONFIDENT — Art. 77(3): under extraordinary martial law, special
    # measures may be taken re: speech, press, assembly, association, and
    # the powers of the courts. Research README explicitly recommends True
    # (not MFU's absolute non-suspendability).
    RIGHTS_SUSPENDABLE: bool = True
    # CONFIDENT direction — no right is literally unsuspendable the way
    # MFU's Article 2.4 rights are. See RIGHTS_ESSENCE_GUARANTEE below for
    # the real, different safeguard Korea has instead.
    RIGHTS_ABSOLUTE_COUNT: int = 0
    # CONFIDENT — Art. 77(3).
    EMERGENCY_TOUCHES_RIGHTS: bool = True
    # CONFIDENT — Art. 39: "All citizens shall have the duty of national
    # defense under the conditions as prescribed by Act" + real, universal,
    # well-documented mandatory conscription (Military Service Act).
    NATIONAL_SERVICE_MANDATORY: bool = True
    # GUESS — real-world Military Service Act registration age proxy, not
    # a constitutional figure (same idiom as constitution_2008.py's own
    # NATIONAL_SERVICE_AGE proxy).
    NATIONAL_SERVICE_AGE: int = 18
    # GUESS — real-world approximate current conscription duration
    # (Army ~18 months post-2020s reforms), statutory not constitutional.
    NATIONAL_SERVICE_DURATION_MONTHS: int = 18
    # CONFIDENT direction — no Section-382-style "military rights override"
    # exists. Active-duty officers are barred from specific offices
    # (Art. 86(3)/87(4)), which is a different mechanism from a general
    # rights override; set False, direct contrast with Myanmar 2008.
    MILITARY_RIGHTS_OVERRIDE: bool = False
    # GUESS magnitude, CONFIDENT direction — HIGHER than Myanmar 2008's
    # suppressed 0.05, because Korean civil society visibly and effectively
    # mobilises against rights violations (2016-17 candlelight-vigil
    # movement that preceded Park's actual removal; large 2024-12
    # protests after the martial-law declaration). Not independently
    # measured; a directional calibration choice.
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.12
    # GUESS magnitude, CONFIDENT direction — a SPIKE, not Myanmar 2008's
    # "gradual erosion, not spike" framing, because Korea's real 2024-12
    # trust response to the martial-law declaration was immediate and sharp
    # (Yoon's approval collapsed within days), not a slow decay.
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.15

    # EXTRA field, NOT part of the confirmed 86-field engine-read contract.
    # CONFIDENT — Art. 37(2): rights may be restricted by law only for
    # national security/order/public welfare, and "no essential aspect of
    # the freedom or right shall be violated." Research README flags this
    # "essence guarantee" as the single most important nuance lost by
    # flattening Korea to the same booleans as Myanmar 2008 (comparable to
    # German Basic Law Art. 19(2), stronger than Myanmar s.414(b), weaker
    # than MFU's absolute non-suspendability). Included for paper-table
    # completeness and any future engine extension; not currently read.
    RIGHTS_ESSENCE_GUARANTEE: bool = True


# ══════════════════════════════════════════════════════════════════════════════
# NO MERIT-EXAM SYSTEM — electoral politics + civil-service examination
# (Gosiwon) coexist but neither matches MFU's merit-formula governance model
# Maps to: constitution.py / constitution_2008.py -> MeritConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """No constitutional merit-selection formula for elected office. Career
    civil servants ARE selected via a real, rigorous examination system
    (the Gosiwon), but elected officials and political appointees are not —
    neither MFU's merit-formula model nor Myanmar 2008's loyalty-dominance
    model applies cleanly. GUESS overall: Ka-Nova's own modelling proxy,
    same caveat the research package applies to every category with no
    direct Korean constitutional referent."""

    PRODUCTIVITY_WEIGHT: float = 0.20
    # GUESS magnitude, CONFIDENT real-world basis — Korea's civil-service
    # entrance examinations (Gosiwon) are famously rigorous and merit-based;
    # weighted higher than the other three to reflect that real institution,
    # even though it governs the bureaucracy, not elected office.
    EDUCATION_WEIGHT: float = 0.30
    PERFORMANCE_WEIGHT: float = 0.25
    # GUESS — proxy for electoral/party-political selection of officeholders
    # (not military loyalty, as in Myanmar 2008's CIVIC_WEIGHT=0.55).
    CIVIC_WEIGHT: float = 0.25

    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    # CONFIDENT — elections, not exams, determine officeholders.
    MERIT_MIN_PUBLIC_OFFICE: float = 0.0
    # GUESS — real-world statutory fact (Ministry of Personnel Management
    # administers the Gosiwon system), not a constitutional citation.
    EXAM_ADMINISTRATOR: str = "ministry_of_personnel_management_gosiwon_system"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 0
    # GUESS — Korea's civil-service exam results ARE published; no specific
    # day-count found in the research package.
    EXAM_RESULTS_PUBLISH_DAYS: int = 30
    # GUESS enumeration, CONFIDENT basis — Art. 65(2) impeachment grounds
    # ("violation of the Constitution or Act in the performance of official
    # duties") + Public Official Election Act disqualification.
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "violation_of_constitution_or_law_in_office_article_65",
        "election_law_violation_public_official_election_act",
        "final_criminal_conviction",
    )
    # GUESS, CONFIDENT direction — Korean disqualifications are typically
    # conviction-based and can be reversed by presidential pardon (Art. 79),
    # unlike Myanmar 2008's permanent loyalty-based disqualification. Real
    # precedent: Chun Doo-hwan and Roh Tae-woo, convicted 1996, pardoned
    # December 1997.
    DISQUALIFICATION_PERMANENT: bool = False
    # CONFIDENT — no recertification cycle exists; Korean accountability
    # runs through elections/impeachment, not a periodic re-test.
    RECERTIFICATION_INTERVAL: int = 0
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.0
    RECERTIFICATION_VACATE_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# HEAD OF STATE + EXECUTIVE — Art. 66-100 (President), Art. 86-100 (State Council)
# Maps to: constitution.py / constitution_2008.py -> ExecutiveConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Semi-presidential, president-dominant civilian system — NOT MFU's
    ceremonial-President/executive-Chancellor split. President -> executive
    fields; Prime Minister -> CHANCELLOR_* fields (a real office here,
    unlike constitution_2008.py's "none" — see schema-mapping disclosure
    at the top of this file)."""

    # CONFIDENT — Art. 66(1)/(4).
    PRESIDENT_ROLE: str = "head_of_state_and_executive"
    # CONFIDENT — Art. 67(1): "elected by universal, equal, direct and
    # secret ballot."
    PRESIDENT_ELECTION: str = "universal_equal_direct_secret_ballot_article_67"
    # CONFIDENT — Art. 70.
    PRESIDENT_TERM: int = 5
    # CONFIDENT — Art. 70: "shall not be reelected."
    PRESIDENT_MAX_TERMS: int = 1
    PRESIDENT_REELECTION: bool = False
    # CONFIDENT — real executive power, not a tiebreaker-only role.
    PRESIDENT_TIEBREAKER: bool = False
    # CONFIDENT — Art. 66(4).
    PRESIDENT_EXECUTIVE_POWER: bool = True
    # CONFIDENT mapping (research README's own explicit recommendation) —
    # Art. 86(1): PM appointed by the President with National Assembly
    # consent. A real office, unlike Myanmar 2008's "none."
    CHANCELLOR_ROLE: str = "prime_minister_appointed_with_assembly_consent"
    CHANCELLOR_ELECTION: str = "president_nominates_assembly_consents_article_86"
    # GUESS — the Constitution does not fix a PM term length; the PM serves
    # at the President's pleasure (removable per Art. 63). Set equal to the
    # presidential term as a schema-completeness proxy only, not a cited
    # figure.
    CHANCELLOR_TERM: int = 5
    # GUESS — no term-limit provision exists for the PM; effectively
    # unlimited.
    CHANCELLOR_MAX_TERMS: int = 99
    # GUESS — no cooling-off provision found in the research package.
    CHANCELLOR_COOLING_OFF: int = 0
    PRESIDENT_ELECTION_YEAR: int = 1
    CHANCELLOR_ELECTION_YEAR: int = 0
    # GUESS magnitude within a CONFIDENT bound — Art. 88(2): the State
    # Council "shall be composed of... a minimum of fifteen and a maximum
    # of thirty" members. 19 approximates Korea's real current ministry
    # count (Government Organization Act, statutory), not independently
    # re-verified against the research package.
    MINISTER_COUNT: int = 19
    # CONFIDENT — political appointment, not merit-exam-gated.
    MINISTER_MERIT_MIN: float = 0.0
    # CONFIDENT — Art. 94: "The members of the State Council shall be
    # appointed by the President on the recommendation of the Prime
    # Minister."
    MINISTER_CONFIRMATION: str = "president_appointment_pm_recommendation_article_94"
    # GUESS — real-world statutory ministry names (Government Organization
    # Act), not constitutionally enumerated (Art. 94-96 only establishes the
    # State Council's existence/structure generally). Ministry of Unification
    # included deliberately — it is a real, distinctively-Korean ministry
    # tied directly to Art. 4/69's peaceful-unification mandate.
    MINISTRIES: Tuple[str, ...] = (
        "ministry_of_economy_and_finance",
        "ministry_of_foreign_affairs",
        "ministry_of_national_defense",
        "ministry_of_the_interior_and_safety",
        "ministry_of_justice",
        "ministry_of_education",
        "ministry_of_unification",
        "ministry_of_science_and_ict",
    )
    # CONFIDENT — Art. 63: the unicameral National Assembly may pass a
    # removal recommendation; one chamber only.
    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 1
    # CONFIDENT — Art. 63 says "recommendation," not a binding removal; the
    # President retains discretion whether to actually act on it — a real
    # and important structural nuance, contrast Art. 65 impeachment (binding
    # once the Constitutional Court rules).
    CHANCELLOR_DISMISSAL_VETO: bool = True
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = True
    # CONFIDENT — unicameral, Art. 65(2).
    PRESIDENT_REMOVAL_CHAMBERS: int = 1
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = False
    # CONFIDENT — mapping Analysis->Constitutional Court (research's own
    # recommendation): the Court's ruling IS required to actually remove a
    # president after impeachment (Art. 65(1)/(4), 111(1).2) — exactly what
    # happened to Park (2017) and Yoon (2025).
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = True
    # CONFIDENT — Art. 65(2): proposal requires a majority of total members.
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.50
    # CONFIDENT — Art. 65(2): passage requires two-thirds or more of total
    # members. Field name reused as the schema's only second threshold slot
    # (the pass/final threshold, distinct from the propose threshold above)
    # — a repurposing, not a literal "trust" concept; documented here.
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.667
    # CONFIDENT — Art. 71: on vacancy/incapacity the Prime Minister (or
    # State Council members, in statutory order of priority) acts.
    CHANCELLOR_INTERIM: str = "prime_minister_then_statutory_order_article_71"


# ══════════════════════════════════════════════════════════════════════════════
# LEGISLATURE — Art. 40-65 (unicameral National Assembly)
# + CONSTITUTIONAL COURT mapped onto ANALYSIS_* (Art. 111-113)
# Maps to: constitution.py / constitution_2008.py -> ChamberConfig
# KEY DIFFERENCE FROM BOTH EXISTING SCENARIOS: zero reserved military seats,
# unicameral (no second chamber, no ethnic council).
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Art. 41-65 — unicameral National Assembly. No second chamber, no
    ethnic-seat allocation (ethnic channel inert — no real referent), and
    the single cleanest structural contrast with every other scenario:
    zero reserved military seats (vs. Myanmar 2008's 25%, Thailand 2017's
    appointed senate, Chile 1980's institutional senators)."""

    # CONFIDENT — Art. 41(1)/(3): mixed district + proportional
    # representation, directly elected.
    CONGRESS_ELECTION: str = "direct_election_district_and_proportional_article_41"
    # CONFIDENT direction, GUESS exact decimal — Art. 49: ordinary decisions
    # by majority of those present, with a majority-of-total-members quorum
    # requirement (simple-majority proxy).
    CONGRESS_THRESHOLD: float = 0.51
    # CONFIDENT — Art. 42.
    CONGRESS_TERM: int = 4
    CONGRESS_REELECTION: bool = True
    # CONFIDENT — unicameral; zero reserved military seats in the one
    # chamber (research README's explicit recommendation). Both MFU-schema
    # seat-count fields collapse to the same unicameral total.
    MILITARY_RESERVED_SEATS_PYITHU: int = 0
    MILITARY_RESERVED_SEATS_AMYOTHA: int = 0
    MILITARY_SEAT_PERCENTAGE: float = 0.0
    MILITARY_SEATS_APPOINTED_BY: str = "not_applicable_no_reserved_seats"
    # CONFIDENT — no constitutionally recognised ethnic-seat allocation;
    # ethnic channel is inert for this scenario (research §1 note).
    ETHNIC_SEATS: int = 0
    # GUESS/CONFIDENT-direction nullification idiom (mirrors
    # constitution_2008.py's own approach to absent mechanisms) — set
    # unreachable rather than fabricating a real threshold.
    ETHNIC_THRESHOLD: float = 1.0
    ETHNIC_TERM: int = 0
    # CONFIDENT — Art. 113(1): decisions on unconstitutionality,
    # impeachment, party dissolution, and competence disputes require six
    # of nine Constitutional Court justices concurring.
    ANALYSIS_THRESHOLD: float = 0.667
    # GUESS — Art. 113 sets no fixed adjudication deadline. 120 is a
    # directional average of the two real historical rulings: Park
    # Geun-hye's impeachment trial took 91 days (2016-12-09 to
    # 2017-03-10); Yoon Suk Yeol's took ~111 days (2024-12-14 to
    # 2025-04-04). Not a cited constitutional figure.
    ANALYSIS_VETO_TIME_LIMIT: int = 120
    # CONFIDENT — Constitutional Court justices are nominated (3 by the
    # Assembly, 3 by the Chief Justice, 3 by the President, Art. 111(3)),
    # not merit-exam-selected.
    ANALYSIS_MERIT_MIN: float = 0.0
    # CONFIDENT — Art. 112(1): six-year terms.
    ANALYSIS_TERM: int = 6
    # CONFIDENT — no military bloc exists in the Assembly at all.
    MILITARY_BLOC_VOTE_DISCIPLINE: float = 0.0
    # CONFIDENT — ordinary majority suffices; there is no military bloc to
    # overcome (contrast Myanmar 2008's 0.667).
    CIVILIAN_EFFECTIVE_MAJORITY_NEEDED: float = 0.50
    ETHNIC_MAX_TERMS: int = 0
    ETHNIC_PRESIDENTIAL_MIN_TERMS: int = 99


# ══════════════════════════════════════════════════════════════════════════════
# JUDICIARY — Art. 101-113 (Supreme Court + Constitutional Court)
# Maps to: constitution.py / constitution_2008.py -> JudiciaryConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Two separate apex bodies, kept distinct per the research package's
    explicit instruction not to collapse them: the Supreme Court (ordinary
    appellate apex, Art. 101-108) and the Constitutional Court (Art.
    111-113, the body performing the MFU Analysis Council's role here —
    JUDGE_COUNT below is set to the Constitutional Court's 9, since that is
    the body the engine's live code paths actually exercise)."""

    # CONFIDENT — Art. 103 (judicial independence), Art. 106 (judges
    # removable only by impeachment or criminal penalty).
    COURT_INDEPENDENCE: bool = True
    # GUESS magnitude, CONFIDENT real-world basis — Art. 102(2) delegates
    # the exact Supreme Court bench size to statute; the real figure under
    # the Court Organization Act is 14 (Chief Justice + 13 Justices).
    COURT_JUDGES_COUNT: int = 14
    # CONFIDENT — Art. 105(2): Supreme Court Justices serve six-year,
    # reappointable terms (the Chief Justice's own six-year term is
    # non-reappointable per Art. 105(1), a real and distinct nuance).
    COURT_TERM_YEARS: int = 6
    # GUESS — simple majority of the 14-member Supreme Court en banc (no
    # fixed constitutional supermajority found for ordinary rulings).
    RULING_THRESHOLD: int = 8
    # CONFIDENT — Art. 110(4): courts-martial appeals go to the Supreme
    # Court except for specified capital crimes under extraordinary martial
    # law. Direct contrast with Myanmar 2008 s.293(b)/343(b), where the
    # Commander-in-Chief's military-justice ruling is final and conclusive.
    MILITARY_JUSTICE_FINAL: bool = False
    CIVILIAN_COURT_OVERRIDE_MILITARY: bool = True
    # CONFIDENT — Art. 111(2): nine adjudicators.
    CONSTITUTIONAL_TRIBUNAL_SIZE: int = 9
    # CONFIDENT — Art. 112(1).
    TRIBUNAL_TERM_YEARS: int = 6
    # GUESS magnitude, CONFIDENT direction — Korea's judiciary has twice
    # actually removed a sitting president via adjudication (Park 2017,
    # Yoon 2025); direct contrast with Myanmar 2008's 0.20
    # "military appointees dominate" framing.
    COURT_CORRUPTION_RESISTANCE: float = 0.80
    # CONFIDENT mapping (schema-disclosure: repurposed, not a literal
    # "Total Ruin" concept) — the Constitutional Court's 6-of-9 removal
    # threshold (Art. 113(1)) is the real structural analogue to MFU's
    # Total Ruin mechanism, and unlike Myanmar 2008 (where it is
    # constitutionally absent, 0.0), it genuinely exists and has been used
    # twice. Both real historical rulings (Park 8-0; Yoon reported
    # unanimous) in fact EXCEEDED this formal threshold — worth a paper
    # sentence.
    TOTAL_RUIN_THRESHOLD: float = 0.667
    # CONFIDENT — matches research's explicit recommendation: JUDGE_COUNT is
    # read by the live engine code for the body performing this role; set
    # to the Constitutional Court's real size (9), not the Supreme Court's.
    JUDGE_COUNT: int = 9
    # CONFIDENT — Art. 112(1).
    JUDGE_TERM: int = 6
    # CONFIDENT — Art. 112(1): "may be appointed for a renewable term" —
    # effectively unlimited reappointment.
    JUDGE_MAX_TERMS: int = 99
    # GUESS, CONFIDENT direction — follows from COURT_INDEPENDENCE=True
    # above; not independently cited for a specific budget-protection
    # clause in the research package.
    BUDGET_FIXED: bool = True


# ══════════════════════════════════════════════════════════════════════════════
# NO MYANMAR-STYLE IIG — Art. 97-100 Board of Audit and Inspection (BAI)
# Maps to: constitution.py / constitution_2008.py -> IIGConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """Board of Audit and Inspection (Art. 97-100) — the constitutionally
    grounded audit/integrity body. No Myanmar-style IIG or MFU-style
    academy-trained anti-corruption agency exists. Korea's REAL
    anti-corruption trajectory is time-varying (V-Dem political corruption
    0.458 in 1988 -> 0.113 in 2019, driven by a 2001-2021 institutional
    build-out: KICAC 2002, ACRC 2008, Kim Young-ran Act 2016, CIO 2021) —
    this schema is static per scenario, so INITIAL/MAX below bracket the
    real range but CANNOT reproduce the real improvement curve (research
    README flag F3). Flagged here explicitly for the data analyst at
    backtest time, not something this file alone can fix."""

    # GUESS — blended estimate: the BAI Chairman is a political appointee
    # (not merit-exam-gated), but rank-and-file auditing staff ARE
    # civil-service-exam-selected (Gosiwon system). Not a single clean
    # figure.
    ENTRY_MERIT: float = 0.50
    # CONFIDENT — no dedicated "academy" exists; BAI staff come through
    # general civil-service training, not a bespoke academy.
    ACADEMY_MONTHS: int = 0
    # GUESS magnitude, CONFIDENT direction — real, active anti-corruption
    # institutions investigate at a much lower threshold than Myanmar
    # 2008's regime-protective 0.90.
    INVESTIGATION_TRIGGER: float = 0.35
    # GUESS, CONFIDENT direction — a real, functioning institution from day
    # one (BAI dates to 1963), far above Myanmar 2008's near-zero 0.05
    # floor.
    EFFECTIVENESS_FLOOR: float = 0.30
    # CONFIDENT — Art. 97-100: BAI Chairman appointed by the President with
    # Assembly consent; BAI reports annually to the President AND the
    # National Assembly.
    REPORTS_TO: str = "president_with_national_assembly_consent_article_97"
    # GUESS — no explicit constitutional bar on former BAI officials later
    # serving in the Assembly, unlike MFU's permanent Article 7.9 ban.
    CHAMBER_ELIGIBLE: bool = True
    # CONFIDENT — research's explicit recommendation; direct opposite of
    # Myanmar 2008.
    ANTI_CORRUPTION_OBJECTIVE: bool = True
    REGIME_PROTECTION_OBJECTIVE: bool = False
    # GUESS, CONFIDENT direction — year-zero (1988) effectiveness should be
    # low-to-moderate, NOT the eventual 2020s level; the real
    # institutional build-out (see class docstring) happened mostly
    # 2001-2021, after this simulation's year zero.
    INITIAL_EFFECTIVENESS: float = 0.30
    # GUESS, directionally informed by V-Dem's real ~75% relative
    # corruption-index improvement (0.458 -> 0.113); see class docstring's
    # static-schema caveat (flag F3) — the simulation will NOT reproduce
    # the real S-shaped curve this single ceiling implies.
    MAX_EFFECTIVENESS: float = 0.80
    ENTRY_MERIT_MIN: float = 0.50
    # GUESS — Gosiwon civil-service exams are typically taken by candidates
    # in their mid-20s; not a constitutional figure.
    ENTRY_MIN_AGE: int = 25
    ACADEMY_DURATION_MONTHS: int = 0
    # CONFIDENT — Art. 98: BAI Chairman serves a four-year term.
    DIRECTOR_TERM: int = 4
    # CONFIDENT direction, with a real cap the schema has no separate slot
    # for: Art. 98 permits exactly ONE reappointment (not the unlimited
    # renewability this single boolean implies) — flagged explicitly since
    # the boolean alone overstates the real permissiveness.
    DIRECTOR_RENEWABLE: bool = True
    # GUESS — no seniority-gated "Partnership Council" equivalent exists;
    # same inert idiom as constitution_2008.py.
    PARTNER_ELIGIBILITY_YEARS: int = 0
    # GUESS, consistent with the lower, real institutional engagement
    # implied by INVESTIGATION_TRIGGER above (both well below Myanmar
    # 2008's collapsed single 0.90 threshold).
    OPEN_INVESTIGATION_THRESHOLD: float = 0.30
    # GUESS — a genuine two-stage process exists in practice (BAI/ACRC
    # referrals to prosecutors), unlike Myanmar 2008's collapsed
    # single-threshold chain-of-command process.
    PROCEED_PROSECUTION_THRESHOLD: float = 0.45
    # GUESS, CONFIDENT direction — the BAI operates as a real collegial
    # board (Chairman + 5-10 other members, Art. 98), unlike MFU's
    # MFU-specific Partnership Council or Myanmar 2008's "1.0 = sole
    # chain-of-command authority" idiom; a majority-of-board proxy is used
    # instead since Korea genuinely has a multi-member deciding body. Exact
    # BAI Act quorum rule not independently verified.
    PARTNERSHIP_COUNCIL_QUORUM: float = 0.50
    CHAMBER_ELIGIBLE_POST_SERVICE: bool = True
    # GUESS — plausible real-world reintegration paths; not specifically
    # researched.
    PERMITTED_POST_SERVICE: Tuple[str, ...] = (
        "private_sector",
        "academia",
        "elected_office",
        "civil_service",
    )
    # GUESS — BAI's real staff count is in the low thousands; order-of-
    # magnitude plausible figure, not independently verified against a
    # primary source in the research package.
    MAX_AGENTS: int = 1000
    # GUESS — real BAI structure per the Board of Audit and Inspection Act
    # (Audit Bureau + Inspection Bureau), reasonably grounded but not a
    # verbatim statutory division list.
    FUNCTIONAL_DIVISIONS: Tuple[str, ...] = (
        "audit_division",
        "inspection_division",
        "public_corporation_audit_division",
    )
    MANDATE_DIVISIONS: Tuple[str, ...] = (
        "government_accounts_audit",
        "public_officials_conduct_inspection",
        "performance_audit",
    )
    OPERATIONAL_DIVISIONS: Tuple[str, ...] = (
        "central_government_audit_division",
        "local_government_audit_division",
        "public_enterprise_audit_division",
    )


# ══════════════════════════════════════════════════════════════════════════════
# UNITARY STATE STRUCTURE — Art. 117-118 (local autonomy, no federal design)
# Maps to: constitution.py / constitution_2008.py -> FederalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Unitary, not federal. Art. 117-118: local governments handle local
    welfare, manage property, may legislate local-autonomy rules within
    statutory limits; organisation/powers/elections determined by statute.
    No constitutional revenue-sharing formula exists — the MFU 35/35/30
    split has NO Korean counterpart (research README's explicit caution).
    RESOURCE_* fields below are Ka-Nova modelling proxies for a unitary
    state's high central fiscal share, NOT a sourced constitutional split."""

    # CORRECTED 2026-10-20, same fix and same reasoning as
    # FoundationalConfig.STATE_COUNT above: 14 is the real year-zero (1988)
    # count, not the present-day 17 (see research README §6.2).
    STATE_COUNT: int = 14
    # CONFIDENT — no constitutionally recognised multi-ethnic structure;
    # ethnic channel is inert for this scenario.
    ETHNIC_GROUPS: int = 1
    # GUESS, explicit modelling proxy (research README's explicit
    # instruction: "recommend encoding a high central share with an
    # explicit comment this is a modelling proxy for a unitary state, not a
    # constitutional number"). ETHNIC_DIRECT_SHARE kept near-zero only for
    # schema arithmetic sanity — there is no real ethnic-direct-transfer
    # concept at all.
    RESOURCE_STATE_SHARE: float = 0.15
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.80
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.05
    # GUESS — real-world plausible OECD-range market-income Gini
    # (~0.31-0.39 historically), not independently verified against a
    # specific KOSIS/World Bank citation in the research package (which
    # explicitly flagged this field needs "the exact year" cited — not yet
    # done here). Contrast directly with Myanmar 2008's 0.65 "inequality
    # tolerated."
    GINI_THRESHOLD: float = 0.35
    # GUESS, CONFIDENT real-world basis — the Seoul Capital Area's real,
    # well-documented economic dominance (reported at roughly half of
    # national GDP), lower than Myanmar 2008's 0.80 Yangon/Mandalay
    # dominance estimate but still a real regional-concentration dynamic.
    STATE_GDP_CAP: float = 0.55
    # CONFIDENT — Art. 86(3)/87(4) bar active-duty military officers from
    # the Prime Minister's office and the State Council entirely; no
    # military presence in regional/local executive structures either.
    MILITARY_IN_REGIONAL_EXECUTIVE: bool = False
    # GUESS magnitude, CONFIDENT direction — Art. 119(2)'s anti-monopoly/
    # economic-democratisation clause is actually enforced via the Fair
    # Trade Commission and the Monopoly Regulation Act, unlike Myanmar
    # 2008's unenforced Section 36(b) ("on paper" framing). Matches MFU's
    # own enforced 0.30 cap by coincidence of magnitude, not derivation.
    SECTOR_MONOPOLY_CAP: float = 0.30
    # GUESS magnitudes, CONFIDENT direction — Korea has no literal
    # Article-VIII-style "virtuous cycle" clause, but unlike Myanmar 2008
    # (deliberately nullified via TRIGGER_YEARS=99/corruption=0.0/
    # multiplier=1.0), Korea's real post-1987 institutional trajectory (see
    # V-Dem judicial/legislative-constraints consolidation, research §2.3)
    # supports a genuine, if unwritten, accountability-reinforcement
    # dynamic. Made REACHABLE here, unlike Myanmar 2008's deliberate
    # nullification — a Ka-Nova calibration choice, not a literal
    # constitutional clause.
    TRUST_ACCELERATION_TRIGGER_CORRUPTION: float = 0.30
    TRUST_ACCELERATION_TRIGGER_YEARS: int = 5
    TRUST_ACCELERATION_MULTIPLIER: float = 1.15


# ══════════════════════════════════════════════════════════════════════════════
# ARMED FORCES — Art. 5(2), 39, 74, 86-87
# Maps to: constitution.py / constitution_2008.py -> MilitaryConfig
# THE DEFINING CONTRAST WITH MYANMAR 2008: no legal coup mechanism, no
# self-adjudication, political neutrality constitutionally mandated.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Art. 5(2): "The Armed Forces shall be charged with the sacred
    mission of national security and the defense of the land and their
    political neutrality shall be maintained." No coup mechanism, no
    reserved seats, no self-adjudication, no transitional immunity — the
    structural opposite of Myanmar 2008's Chapter VII. See the module
    docstring's "corrected framing" note: this is encoded as low-but-
    nonzero risk, not an absolute-zero floor, per research README flag F1
    (the 2024-12-03 martial-law episode)."""

    # CONFIDENT — research's explicit recommendation.
    COUP_LEGAL_MECHANISM: bool = False
    # CONFIDENT direction — set unreachable (1.0) given COUP_LEGAL_MECHANISM
    # above. Also structurally near-meaningless here: this field (and
    # COUP_TRIGGER_TRUST below) is read only inside
    # engine/elite_agents_v3.py's military-chain prompt builder, which this
    # civilian-chain scenario never calls — both fields are schema-complete
    # but inert for SK specifically, documented for transparency.
    COUP_TRIGGER_CORRUPTION: float = 1.0
    COUP_TRIGGER_TRUST: float = 0.0
    # CONFIDENT — Art. 74(1): the President is directly Commander-in-Chief;
    # no separate NDSC-style appointment-and-approval process exists the
    # way Myanmar 2008's Section 342 requires.
    COMMANDER_IN_CHIEF_APPOINTMENT: str = "president_is_commander_in_chief_directly_article_74"
    # CONFIDENT — research's explicit recommendation; contrast Myanmar 2008
    # s.293(b)/343(b).
    MILITARY_SELF_ADJUDICATION: bool = False
    # CONFIDENT — Art. 74(2): organisation/formation of the Armed Forces by
    # statute under a unified presidential chain of command.
    SINGLE_CHAIN_OF_COMMAND: bool = True
    # CONFIDENT — Art. 5(2) explicit political-neutrality clause, direct
    # opposite of Myanmar 2008 s.6(f).
    MILITARY_POLITICAL_ROLE: bool = False
    PARLIAMENTARY_SEAT_PERCENTAGE: float = 0.0
    PARLIAMENTARY_SEAT_APPOINTMENT: str = "not_applicable_no_reserved_seats"
    # GUESS magnitude, CONFIDENT direction — year-zero (1988) loyalty to the
    # NEW democratic constitutional order was not yet fully consolidated;
    # the military had stepped back from direct rule only recently (the
    # 1979-80 Chun coup was 7-8 years prior). Deliberately LOWER than MFU's
    # own 0.85 "high initial loyalty to regime" framing, which assumes
    # embrace of a brand-new idealised constitution rather than a still-
    # fragile real transition away from prior military rule.
    LOYALTY_INITIAL: float = 0.60
    # CONFIDENT — inert; the "loyalty to the regime" mechanic does not
    # apply the same way once MILITARY_POLITICAL_ROLE=False (the military
    # has no political role to be loyal/disloyal within).
    LOYALTY_CORRUPTION_DRAG: float = 0.0
    # GUESS magnitude, CONFIDENT direction — near-zero but NOT fabricated
    # as impossible (contrast Myanmar 2008's literal 0.0, which means "the
    # military IS the regime, no risk TO it" — a different and inapplicable
    # framing here). This instead models the real, low, but nonzero
    # probability of a coup AGAINST the civilian government, consistent
    # with the required "no zero coups" framing (research README flag F1).
    COUP_PROBABILITY_MULTIPLIER: float = 0.02
    # CONFIDENT — Art. 77 martial law is real and was actually invoked
    # domestically on 2024-12-03.
    DOMESTIC_FORCE_AUTHORIZED: bool = True
    DOMESTIC_FORCE_TRIGGER: str = "presidential_martial_law_declaration_article_77"
    # CONFIDENT direction — unreachable, mirrors constitution_2008.py's own
    # reasoning for these two fields (modelling whether the military turns
    # against its OWN leadership) even more strongly here: with
    # MILITARY_POLITICAL_ROLE=False and COUP_LEGAL_MECHANISM=False, this
    # specific trigger has no real referent at all.
    COUP_TRIGGER_LOYALTY: float = 0.0
    COUP_TRIGGER_APPROVAL: float = 0.0
    # GUESS — neutral citizen-side sorting criterion, not itself
    # constitution-dependent (same framing constitution_2008.py applies to
    # its own equivalent field).
    NS_CIVILIAN_TRACK_THRESHOLD: float = 0.60
    # GUESS, CONFIDENT direction — Korea's conscription is real, mandatory,
    # AND broadly legitimate/accepted (near-universal male conscription,
    # not the coercive post-2021 framing Myanmar 2008 documents). Set
    # between Myanmar 2008's coerced 0.05 and MFU's voluntary high-merit
    # 0.15.
    NS_LOYALTY_BOOST: float = 0.08
    # CONFIDENT — no ethnic-exposure dynamic applies; channel is inert.
    NS_ETHNIC_EXPOSURE_BOOST: float = 0.0
    NS_CIVIC_CONTRIBUTION_BOOST: float = 0.05


# ══════════════════════════════════════════════════════════════════════════════
# ECONOMY — Chapter IX, Art. 119-127
# Maps to: constitution.py / constitution_2008.py -> EconomicConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Chapter IX — Economy (Art. 119-127). Market economy with a real,
    actively-enforced anti-monopoly/"economic democratisation" mandate
    (Art. 119(2)), NOT Myanmar 2008's unenforced-on-paper equivalent."""

    # CONFIDENT — Art. 119(1): market economy respecting individual freedom
    # and creativity; Art. 119(2): the state may regulate to ensure
    # balanced growth, income distribution, prevent market domination, and
    # "democratise the economy."
    ECONOMIC_SYSTEM: str = "market_economy_with_economic_democratization_article_119"
    # GUESS — simplified real-world-informed proxy of Korea's progressive
    # marginal income-tax brackets; statutory (tax Acts), not constitutional.
    TAX_BRACKETS: Tuple[float, ...] = (0.06, 0.15, 0.24, 0.35, 0.42)
    # GUESS — ordinary criminal/tax law applies; no "High Treason" framing
    # as in MFU.
    BLACK_MONEY_PENALTY: str = "criminal_prosecution_under_tax_and_criminal_law"
    # CONFIDENT — Art. 126 (nationalisation only under narrow exceptions,
    # see NATIONALIZATION_BANNED below) and Art. 23/126 (private property
    # protected); direct contrast with Myanmar 2008 s.37(a)'s blanket Union
    # ownership.
    STATE_OWNS_RESOURCES: bool = False
    PRIVATE_PROPERTY_PROTECTED: bool = True
    # CONFIDENT — Art. 119(2), AND genuinely enforced via the Fair Trade
    # Commission/Monopoly Regulation Act — contrast Myanmar 2008's
    # "on paper, unenforced" framing.
    ANTI_MONOPOLY: bool = True
    # GUESS, CONFIDENT real-world basis — Korea has a real, well-documented
    # history of chaebol-political entanglement (e.g., the Choi Soon-sil/
    # Samsung scandal that directly triggered Park Geun-hye's 2016-17
    # impeachment). Set True (not crony-free) with a smaller CRONY_CAPITAL_
    # SHARE than Myanmar 2008, an honest-but-smaller-effect choice rather
    # than a naive "no cronyism" claim.
    CRONYISM_ENABLED: bool = True
    # CONFIDENT — Art. 126: nationalisation/transfer-to-public-ownership
    # banned EXCEPT "to meet urgent necessities of national defense or the
    # national economy" by law — a conditional exception, NOT Myanmar
    # 2008's absolute Section 36(d) ban. Set False to reflect the real,
    # narrower Korean rule (the exception exists; the ban is not absolute).
    NATIONALIZATION_BANNED: bool = False
    # GUESS magnitude, CONFIDENT direction — lower than Myanmar 2008's
    # 0.03, directionally grounded in V-Dem's real corruption decline.
    CORRUPTION_GDP_DRAG: float = 0.01
    # GUESS magnitude, CONFIDENT real-world basis — smaller than Myanmar
    # 2008's 0.40, grounded directionally in the well-documented but
    # real chaebol-political connection (2016-17 scandal); exact magnitude
    # not independently sourced.
    CRONY_CAPITAL_SHARE: float = 0.15
    # GUESS — real-world informed (broadcasting ownership caps, defense
    # procurement restrictions); not independently verified against a
    # specific statute in the research package.
    STRATEGIC_SECTORS: Tuple[str, ...] = (
        "defense",
        "telecommunications",
        "broadcasting_media",
        "banking_financial_services",
    )
    # GUESS — real-world informed (Korea's globally competitive, open
    # export sectors).
    OPEN_SECTORS: Tuple[str, ...] = (
        "manufacturing",
        "retail",
        "technology_and_semiconductors",
        "automotive",
        "shipbuilding",
    )
    # GUESS — real-world plausible figure for restricted-sector foreign
    # ownership caps (e.g., broadcasting); not independently verified.
    FOREIGN_CAP_STRATEGIC: float = 0.49
    # CONFIDENT — Korea's open sectors (manufacturing, technology) have no
    # foreign-ownership cap; a well-documented, very open OECD economy for
    # these sectors.
    FOREIGN_CAP_OPEN: float = 1.00


# ══════════════════════════════════════════════════════════════════════════════
# EDUCATION / SCIENCE — Art. 31, 127
# Maps to: constitution.py / constitution_2008.py -> ScienceConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Art. 31 (education), Art. 127 (science/technology development).
    Korea is a real, well-documented global R&D leader (one of the
    world's highest R&D-to-GDP ratios) with constitutionally protected
    university autonomy — direct contrast with Myanmar 2008's nationalist-
    framed, politically-controlled education system."""

    # CONFIDENT — Art. 31(3): free education is mandated only at the
    # compulsory level, not tertiary/PhD level.
    PHD_TUITION_FREE: bool = False
    # GUESS — no constitutional royalty scheme exists; not a cited figure.
    RESEARCHER_ROYALTY: float = 0.0
    # GUESS magnitude, CONFIDENT direction — real, well-documented R&D
    # intensity (one of the highest R&D-to-GDP ratios globally), far above
    # Myanmar 2008's 0.005 "brain drain high" framing.
    KNOWLEDGE_CAPITAL_GROWTH: float = 0.04
    # CONFIDENT — Art. 31(4) explicitly mandates the political impartiality
    # and autonomy of education and universities — the OPPOSITE of
    # Myanmar 2008 s.28(d)'s nationalist framing.
    EDUCATION_NATIONALIST_FRAMING: bool = False
    # GUESS magnitude, CONFIDENT direction — Korea is a real net talent
    # magnet/globally competitive economy, much lower brain drain than
    # Myanmar 2008's 0.15.
    BRAIN_DRAIN_RATE_BASE: float = 0.03
    # GUESS magnitude, CONFIDENT direction — Art. 31(4) directly cited;
    # contrast Myanmar 2008's 0.20 politically-controlled framing.
    ACADEMIC_FREEDOM: float = 0.85
    RESEARCHER_ROYALTY_RATE: float = 0.0
    # GUESS, CONFIDENT direction — Korea's real strong STEM-PhD-to-economy
    # pipeline; below MFU's own self-designed aspirational 0.25, well above
    # Myanmar 2008's 0.05.
    PHD_KNOWLEDGE_CAPITAL_BOOST: float = 0.20


# ══════════════════════════════════════════════════════════════════════════════
# AMENDMENT — Art. 128-130
# Maps to: constitution.py / constitution_2008.py -> AmendmentConfig
# KEY: a SINGLE uniform procedure for every provision — no differentiated
# entrenchment tiers the way Myanmar 2008 (or MFU) has.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Art. 128-130. Unlike Myanmar 2008's two-tier system (entrenched
    chapters at 75%+referendum vs. standard articles at 75% only), EVERY
    Korean constitutional amendment requires the SAME procedure: 2/3
    Assembly vote + mandatory referendum (50% turnout floor AND 50%
    majority). STANDARD_AMENDMENT_THRESHOLD and ENTRENCHED_AMENDMENT_
    THRESHOLD are therefore set to the same real figure, not two different
    tiers. Observed record: zero successful amendments in 38 years — this
    uniform, doubly-binding procedure is empirically extremely binding."""

    # CONFIDENT — Art. 128(1): proposal by a majority of total Assembly
    # members OR by the President.
    AMENDMENT_INITIATION_THRESHOLD: float = 0.50
    # CONFIDENT — Art. 130(1): National Assembly must decide within 60
    # days, requiring two-thirds of total members.
    ENTRENCHED_AMENDMENT_THRESHOLD: float = 0.667
    # CONFIDENT — Art. 130(2): mandatory national referendum within 30
    # days.
    ENTRENCHED_REQUIRES_REFERENDUM: bool = True
    # CONFIDENT — see class docstring: Korea has no non-referendum
    # "standard" tier at all; every amendment requires the same 2/3 +
    # referendum procedure.
    STANDARD_AMENDMENT_THRESHOLD: float = 0.667
    # CONFIDENT — no military bloc exists to exercise any such veto.
    MILITARY_VETO_ON_AMENDMENTS: bool = False
    # CONFIDENT — see class docstring: no differentiated entrenchment
    # tiers exist; every provision is subject to the identical procedure,
    # contrast directly with both MFU's ENTRENCHED_CLAUSES concept and
    # Myanmar 2008's chapter-specific entrenchment list.
    ENTRENCHED_CHAPTERS: Tuple[str, ...] = ("all_provisions_uniform_procedure",)
    # CONFIDENT — no mandatory periodic constitutional review cycle exists
    # in the 1987 text.
    REVIEW_INTERVAL: int = 0
    # CONFIDENT — kept identical to MFU/Myanmar 2008's value: no real
    # Korean civic-lottery/Citizens-Assembly mechanism exists at all, so
    # there is no principled different number to use (same precedent both
    # existing files already set).
    CITIZENS_ASSEMBLY_SIZE: int = 320

    # EXTRA field, NOT part of the confirmed 86-field engine-read contract.
    # CONFIDENT — research README §1 AmendmentConfig: "Observed record:
    # zero successful amendments in 38 years." Included for paper-table
    # completeness; documents a real, citeable empirical fact about this
    # amendment procedure's bindingness, distinct from (and arguably more
    # interesting than) the formal thresholds above.
    AMENDMENT_RECORD_SINCE_1988: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# TRANSITIONAL PROVISIONS — Addenda to the 1987 Constitution
# Maps to: constitution.py / constitution_2008.py -> TransitionConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """The 1987 Addenda provide only for the first presidential election
    and continuity of existing officials. NO amnesty clause, NO immunity
    clause. Historically the opposite happened: Chun Doo-hwan and Roh
    Tae-woo were PROSECUTED AND CONVICTED in 1996 for the 1979
    insurrection/1980 Gwangju events (later pardoned December 1997). This
    is a genuine, documented structural contrast with Myanmar 2008 s.445
    (research README's explicit instruction)."""

    # CONFIDENT — immediate effect 25 February 1988; no phased transition
    # articles beyond the Addenda's first-election provisions.
    TRANSITION_PERIOD_YEARS: int = 0
    # CONFIDENT — directly per research; no blanket amnesty clause exists.
    AMNESTY_GRANTED: bool = False
    # GUESS, standard-continuity inference — not explicitly named in the
    # research package, but a reasonable assumption absent any contrary
    # provision.
    PRIOR_LAWS_VALID: bool = True
    # CONFIDENT — directly per research; contrast Myanmar 2008 s.445.
    PRIOR_ACTIONS_IMMUNE: bool = False
    # GUESS — standard continuity assumption, not explicitly researched.
    CIVIL_SERVANTS_RETAIN_POSTS: bool = True
    # CONFIDENT — no special pension scheme exists for this purpose.
    TATMADAW_PENSION: float = 0.0
    # CONFIDENT — direct contrast with Myanmar 2008's True; matches
    # research's explicit instruction.
    TATMADAW_IMMUNITY: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# SAFEGUARDS — Art. 91 (NSC), 111-113 (Constitutional Court), 37(2)
# Maps to: constitution.py / constitution_2008.py -> SafeguardConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """Korea's real safeguards are genuinely different from both MFU's
    bespoke named mechanisms AND Myanmar 2008's "no safeguards, military
    control IS the safeguard" framing — neither "all MFU safeguards" nor
    "all absent" is accurate; each field below is evaluated on its own
    real-world merits rather than defaulted to either existing file's
    pattern."""

    CHANCELLOR_COOLING_OFF_ENFORCED: bool = False
    # CONFIDENT — no constitutional merit-exam system governs elected
    # office at all (see MeritConfig).
    MERIT_EXAM_INDEPENDENCE: bool = False
    ETHNIC_COUNCIL_YOUTH_MANDATE: bool = False
    # GUESS, CONFIDENT nuance — Art. 98 permits exactly one BAI Chairman
    # reappointment (neither MFU's strict single-term rule nor Myanmar
    # 2008's unlimited serve-at-pleasure); closest boolean mapping is
    # False (not strictly single-term), with the real one-reappointment cap
    # documented in IIGConfig.DIRECTOR_RENEWABLE's own comment.
    IIG_SINGLE_TERM: bool = False
    # GUESS, CONFIDENT real-world basis — Constitutional Court rulings are
    # genuinely public and high-profile (the Park and Yoon removal rulings
    # were nationally broadcast live), a real and well-documented fact.
    ANALYSIS_TRANSPARENCY: bool = True
    # CONFIDENT — matches RightsConfig.RIGHTS_SUSPENDABLE=True; no right is
    # literally absolute (see RIGHTS_ESSENCE_GUARANTEE for the real,
    # different safeguard Korea has instead).
    RIGHTS_ABSOLUTE: bool = False
    GENERATIONAL_ASSEMBLY_REVIEW: bool = False
    MILITARY_SEAT_RESERVATION: bool = False
    # CONFIDENT — no military veto power exists; President-as-CinC is a
    # civilian constitutional office, not a military veto mechanism.
    COMMANDER_IN_CHIEF_VETO: bool = False
    # CONFIDENT — Art. 91: a National Security Council IS real and
    # constitutionally established, "to advise the President in regard to
    # the establishment of major policies relating to foreign, military and
    # domestic policies prior to their final decision." Key difference from
    # Myanmar's NDSC: Korea's NSC is purely ADVISORY to a civilian
    # President, not a body with independent veto/appointment power over
    # the Commander-in-Chief.
    NDSC_OVERSIGHT: bool = True
    # GUESS — Constitutional Court proceedings are genuinely public; no
    # specific day-count cited in the research package.
    ANALYSIS_PUBLISH_BEFORE_VETO_DAYS: int = 14


# ══════════════════════════════════════════════════════════════════════════════
# NO CRYPTOGRAPHIC JUSTICE — but a REAL "total removal from office" pathway
# exists (Art. 65, 111, 113 impeachment-to-Constitutional-Court-removal)
# Maps to: constitution.py / constitution_2008.py -> CryptoJusticeConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """No blockchain/ZKP/shame-register mechanism exists constitutionally.
    BUT unlike Myanmar 2008 (where a "Total Ruin"-equivalent mechanism is
    constitutionally absent), Korea's impeachment-to-Constitutional-Court-
    removal pathway is REAL and has been used twice (Park 2017, Yoon 2025)
    — TOTAL_RUIN_MECHANISM below is mapped onto that real pathway, not a
    literal cryptographic-justice system (schema-mapping disclosure)."""

    BLOCKCHAIN_ENABLED: bool = False
    ZKP_ENABLED: bool = False
    MULTI_PARTY_SIGNATURES: bool = False
    # CONFIDENT mapping — see class docstring: the real impeachment-removal
    # pathway exists and is operative, unlike Myanmar 2008's constitutional
    # absence of any equivalent mechanism.
    TOTAL_RUIN_MECHANISM: bool = True
    # CONFIDENT — three real, well-documented steps: Assembly impeachment
    # vote (Art. 65(2)) -> automatic suspension of presidential duties
    # (Art. 65(3)) -> Constitutional Court adjudication (Art. 111/113).
    TOTAL_RUIN_STEPS: int = 3
    # CONFIDENT — Art. 113(1): six of nine Constitutional Court justices
    # must concur, matching real history (Park 2017, Yoon 2025).
    COURT_SUPERMAJORITY_FOR_TOTAL_RUIN: int = 6
    # CONFIDENT — no public shame-register mechanism exists
    # constitutionally; real investigative journalism/media plays a
    # similar informal role, but that is a real functional analogue
    # existing OUTSIDE the constitutional text, not something to fabricate
    # a number for.
    SHAME_REGISTER_CORRUPTION_REDUCTION: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# EMERGENCY POWERS — Art. 76-77. THE SINGLE MOST IMPORTANT SOUTH KOREA
# PARAMETER per the research package: a binding legislative kill-switch.
# Maps to: constitution.py / constitution_2008.py -> EmergencyConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Art. 76: President may issue emergency orders having the force of
    law, but must obtain National Assembly approval or the orders lose
    effect. Art. 77: President may proclaim martial law; Art. 77(5):
    "When the National Assembly requests the lifting of martial law by a
    majority of the total members, the President shall comply." No
    presidential veto, no judicial gatekeeping, no quorum escape hatch.
    This is exactly what happened on 2024-12-04: a 190-0 Assembly vote
    forced the lifting within hours. THE structural feature that
    distinguishes this scenario from Myanmar 2008/Thailand/Pakistan/Chile —
    see research README flag F2 on its current engine-wiring limitation."""

    # CONFIDENT — Art. 76 (internal turmoil, external threat, natural
    # calamity, financial-economic crisis) + Art. 77 (military necessity,
    # public safety and order).
    TRIGGER_SCENARIOS: Tuple[str, ...] = (
        "internal_turmoil_external_threat_or_crisis_article_76",
        "military_necessity_or_public_safety_martial_law_article_77",
    )
    # GUESS — Art. 76 does not specify a fixed duration (orders simply lose
    # effect without Assembly approval, "without delay"); not a cited
    # figure, a modelling placeholder only.
    EMERGENCY_MAX_DAYS: int = 60
    # GUESS — no explicit extension mechanism analogous to Myanmar 2008's
    # two 6-month extensions is cited in the research package.
    EMERGENCY_EXTENSIONS: int = 0
    EMERGENCY_EXTENSION_MONTHS: int = 0
    # CONFIDENT — Art. 77(3).
    RIGHTS_UNTOUCHED: bool = False
    # CONFIDENT — research's explicit recommendation; THE key structural
    # contrast with Myanmar 2008's Section 417-419 total transfer.
    TOTAL_POWER_TRANSFER_POSSIBLE: bool = False
    POWER_TRANSFER_TRIGGER: str = "not_applicable_no_total_transfer_mechanism"
    # CONFIDENT — no such transfer exists; the President already holds
    # executive power directly (Art. 66) but does not ACQUIRE legislative
    # or judicial power during an emergency the way Myanmar 2008's Section
    # 419 grants the Commander-in-Chief.
    COMMANDER_IN_CHIEF_LEGISLATIVE: bool = False
    COMMANDER_IN_CHIEF_EXECUTIVE: bool = False
    COMMANDER_IN_CHIEF_JUDICIAL: bool = False
    # CONFIDENT — direct contrast with Myanmar 2008; Art. 77(5) literally
    # requires the Assembly to be ABLE to convene and vote to lift martial
    # law, so it structurally CANNOT be suspended — proven by the actual
    # 190-0 vote on 2024-12-04.
    LEGISLATURE_SUSPENDED_DURING_EMERGENCY: bool = False
    # GUESS magnitude, CONFIDENT direction — genuine emergencies do NOT
    # mechanically escalate toward coup/collapse in Korea's real structure,
    # contrast Myanmar 2008's 1.0 "full probability activation."
    EMERGENCY_COUP_PROBABILITY_MULTIPLIER: float = 0.05

    # EXTRA fields, NOT part of the confirmed 86-field engine-read contract.
    # model_phase3.py's emergency-powers mechanics are not currently wired
    # to EmergencyConfig at all beyond TRIGGER_SCENARIOS (confirmed by
    # direct grep, 2026-10-20) — these two fields document South Korea's
    # single most important real structural feature (research README flag
    # F2: "needs a decision: extend the schema, or accept that the SK/C
    # contrast is carried only by coup-probability parameters") for
    # paper-table completeness and any future engine work. They are
    # currently inert; wiring them into model_phase3.py/feedback/loops.py
    # is a real engine change, out of this config file's scope.
    # CONFIDENT — Art. 77(5): majority of total Assembly members.
    EMERGENCY_LEGISLATIVE_LIFT_THRESHOLD: float = 0.50
    # CONFIDENT — Art. 77(5): "the President shall comply" — zero executive
    # discretion, unlike Myanmar 2008 where no such override exists at all.
    EMERGENCY_LIFT_BINDING_ON_EXECUTIVE: bool = True


# ══════════════════════════════════════════════════════════════════════════════
# RULES OF ENGAGEMENT — Art. 5(1), 77
# Maps to: constitution.py / constitution_2008.py -> ROEConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """Art. 5(1): international peace, repudiates aggressive war. Korea's
    real external security posture is treaty-alliance-based (1953 Mutual
    Defense Treaty with the United States, US Forces Korea stationed under
    SOFA) — encoded honestly here rather than reusing Myanmar 2008's
    "non-aligned" framing, which would be factually wrong for Korea."""

    # CONFIDENT — Art. 5(1): "The Republic of Korea shall endeavor to
    # maintain international peace and... repudiates all aggressive wars."
    FOREIGN_POLICY: str = "international_peace_and_cooperation_article_5"
    NO_AGGRESSION: bool = True
    # GUESS/CONFIDENT real-world fact (NOT covered by the research
    # package's article citations directly) — Korea hosts foreign (US)
    # troops under the 1953 Mutual Defense Treaty and SOFA; copying Myanmar
    # 2008's True here would be factually wrong.
    NO_FOREIGN_TROOPS: bool = False
    # CONFIDENT — Art. 77.
    DOMESTIC_MILITARY_USE: str = "presidential_martial_law_declaration_article_77"
    # GUESS magnitude, CONFIDENT direction — Art. 77's "military necessity"
    # or "public safety and order" bar is a real constitutional threshold,
    # not the broad, low-bar discretion Myanmar 2008's 0.05 encodes.
    DOMESTIC_FORCE_THRESHOLD: float = 0.60
    # GUESS/CONFIDENT real-world fact — Korea's external security posture
    # is alliance-based, not non-aligned; a genuine structural fact worth
    # encoding honestly rather than reusing Myanmar's framing.
    EXTERNAL_ROE: str = "defensive_mutual_defense_treaty_with_united_states"
    # GUESS, CONFIDENT direction — matches Art. 5(1)'s anti-aggression
    # framing.
    EXTERNAL_FULL_FORCE: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# NO PSYCHOLOGICAL-HEALTH MANDATE — no Korean constitutional referent
# Maps to: constitution.py / constitution_2008.py -> PsychConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """No constitutional psychological-health mandate exists (same
    structural absence as Myanmar 2008, for an entirely different real-
    world reason: Korea is a mature democracy with no equivalent recent
    national conflict/ethnic-suppression trauma history at this scale).
    This section's trauma-baseline values are Ka-Nova's own modelling
    choice, NOT independently researched — flagged explicitly rather than
    silently copying either existing file's figures."""

    BIANNUAL_SCREENING: bool = False
    ANTI_BIAS_REVIEW: bool = False
    TRAUMA_CARE_MANDATED: bool = False
    # GUESS — deliberately much lower than Myanmar 2008's conflict-driven
    # 0.45; NOT independently researched, and NOT a claim that Korea has
    # zero societal trauma, only that it is not driven by the same-scale
    # war/ethnic-conflict history Myanmar 2008's framing assumes.
    POPULATION_TRAUMA_BASE: float = 0.15
    TRAUMA_ACCUMULATION_RATE: float = 0.005
    # CONFIDENT — inert; no ethnic-minority structure exists.
    ETHNIC_TRAUMA_MULTIPLIER: float = 1.00
    # GUESS — same "never triggers within the simulation horizon" idiom as
    # constitution_2008.py, consistent with BIANNUAL_SCREENING=False above.
    SCREENING_INTERVAL_MONTHS: int = 9999
    SEVERE_PROBATION_MONTHS: int = 9999
    OUTCOME_STABLE_THRESHOLD: float = 0.40
    OUTCOME_SEVERE_THRESHOLD: float = 0.70
    # GUESS, deliberate no-op — same idiom as constitution_2008.py: no
    # formal psychological-health mandate exists to formally "stop."
    STOP_CONSEQUENCE: str = "no_formal_consequence_mechanism_exists"
    # CONFIDENT — trauma origin categories describe citizen lived
    # experience, not a constitution-specific design choice; reused
    # unchanged from the existing files' category list.
    TRAUMA_CATEGORIES: Tuple[str, ...] = (
        "warfare_conflict",
        "family_domestic_abuse",
        "educational_authoritarian",
        "environmental_displacement",
        "self_identity_ethnic_suppression",
    )
    # GUESS — kept at the MFU/Myanmar-2008-shared midpoint; not
    # independently researched for Korea specifically.
    TRAUMA_DISTORTION_RANGE: Tuple[float, float] = (0.10, 0.30)


# ══════════════════════════════════════════════════════════════════════════════
# NORTH STAR — Art. 4 (peaceful unification), Art. 69 (presidential oath)
# Maps to: constitution.py / constitution_2008.py -> NorthStarConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """Art. 4 and Art. 69 (the presidential oath's "pursue peaceful
    unification of the homeland") are the only constitutionally stated
    national objectives — research's explicit note that PROGRESS_METRIC
    below is a modelling choice, not a constitutional one."""

    # CONFIDENT — Art. 4, Art. 69.
    OBJECTIVES: Tuple[str, ...] = ("peaceful_unification_article_4_and_69",)
    # CONFIDENT — opposite of Myanmar 2008.
    MILITARY_POLITICAL_ROLE_PERPETUATED: bool = False
    # GUESS — modelling choice, per research's explicit note.
    PROGRESS_METRIC: str = "democratic_consolidation_and_peaceful_unification_index"
    # GUESS, informed directly by Korea's real, already-observed V-Dem
    # ceiling (polyarchy ~0.80+, liberal democracy ~0.74 in recent years,
    # research §2.3), unlike Myanmar 2008's literal 0.0 "regime survival is
    # the goal" framing.
    TARGET_YEAR_50_PROGRESS: float = 0.75
    # GUESS, CONFIDENT direction — Korea's real, strong R&D/PhD pipeline;
    # opposite of Myanmar 2008's False.
    PHD_COMPOUNDING_ENABLED: bool = True
    KNOWLEDGE_CAPITAL_TARGET: float = 0.70


# ══════════════════════════════════════════════════════════════════════════════
# TATMADAW TRANSITION — required for chain_type: "civilian" (engine reads
# this section literally at model_phase3.py:521; the name is fixed/
# Myanmar-specific in the engine, not something being encoded about
# Myanmar — see task brief). Mapped onto Korea's REAL 1987-88 transition:
# former generals (Chun Doo-hwan, Roh Tae-woo) moving from military rule
# into the new constitutional civilian order, later prosecuted (not
# amnestied) for their prior conduct.
# Maps to: constitution.py -> TatmadawTransitionConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TatmadawTransitionConfig:
    """Korea's real historical analogue to this section is genuine: Roh
    Tae-woo, a former general, won the first direct presidential election
    under the new 1987 Constitution (Dec 1987) and served the single full
    5-year term the new constitution allows, then returned fully to
    civilian life. Unlike MFU's Article 19 (an invented mechanism for an
    idealised constitution), this reflects a REAL, documented transition.
    BLANKET_IMMUNITY is correctly False (matching research's explicit
    instruction) because Chun and Roh were later prosecuted and convicted
    in 1996 — though subsequently pardoned by presidential grant in
    December 1997, a real and important nuance: the prosecution happened
    (no constitutional immunity was ever granted), but a later political
    pardon followed. ENGINE-REQUIRED FIELD: TRUST_GAIN_PER_CLEAN_YEAR
    (model_phase3.py crashes loudly with AttributeError if this section or
    this field is missing, by design)."""

    # GUESS — loosely modelled on Roh Tae-woo's single 5-year presidential
    # term (1988-1993) as the real historical analogue of a former
    # general's "transition service" under the new constitution; not a
    # literally codified constitutional requirement (no such requirement
    # exists in the 1987 text).
    SENIOR_GENERAL_SERVICE_YEARS: int = 5
    # CONFIDENT — Art. 5(2): the military has no constitutional political
    # role to transition INTO; this field models the absence of such a
    # role, not a transition pathway.
    SENIOR_GENERAL_ROLE: str = "no_constitutional_political_role_article_5_2"
    # CONFIDENT — Art. 5(2), Art. 86(3), Art. 87(4).
    CIVILIAN_SUPREMACY: bool = True
    # CONFIDENT — Art. 70.
    PRESIDENTIAL_TERM_YEARS: int = 5
    # GUESS, inert idiom — no scheduled "active quarter" concept exists for
    # a constitutionally politically-neutral military (Art. 5(2)); set to
    # model the mechanism's absence, not fabricate a schedule.
    ACTIVE_QUARTER: int = 0
    ACTIVE_YEARS_PER_TERM: Tuple[int, int] = (0, 0)
    ELECTIONS_SERVED: int = 0
    # CONFIDENT — directly per research; matches research's explicit
    # instruction (no amnesty clause, no immunity clause).
    BLANKET_IMMUNITY: bool = False
    # CONFIDENT — real historical precedent: Chun Doo-hwan and Roh Tae-woo
    # were prosecuted and convicted in 1996 under ordinary criminal law for
    # the 1979 insurrection / 1980 Gwangju events.
    WAR_CRIMES_PROVEN_TRIGGER: str = "prosecution_under_ordinary_criminal_law_1996_precedent"
    # GUESS, CONFIDENT direction — no constitutional immunity exists even
    # for unproven allegations; ordinary judicial process applies.
    WAR_CRIMES_UNPROVEN: str = "no_constitutional_immunity_case_by_case_judicial_process"
    # CONFIDENT — real historical precedent: the ordinary Supreme Court,
    # not a bespoke tribunal, convicted Chun and Roh in 1996.
    PROSECUTION_BODY: str = "ordinary_courts_supreme_court_1996_precedent"
    # GUESS — standard Korean criminal-law evidentiary standard; reasonable
    # real-world assumption, not independently cited in the research
    # package.
    EVIDENCE_STANDARD: str = "beyond_reasonable_doubt"
    # CONFIDENT — real precedent: Roh Tae-woo, a former general, held
    # civilian constitutional office (the presidency) under the new order.
    CIVILIAN_ROLE_ELIGIBLE: bool = True
    # CONFIDENT — no merit-exam gate exists for elected civilian office
    # (see MeritConfig); electoral/party politics governs instead.
    CIVILIAN_ROLE_REQUIRES_MERIT: bool = False
    # GUESS — standard, no special multiplier documented.
    PENSION_MULTIPLIER: float = 1.0
    PENSION_BASIS: str = "standard_civil_and_military_pension_law"
    # GUESS, CONFIDENT direction — no special privileges documented;
    # consistent with BLANKET_IMMUNITY=False and civilian-supremacy
    # framing throughout this file.
    SPECIAL_PRIVILEGES: bool = False
    # GUESS magnitude, CONFIDENT direction — real empirical record (Powell-
    # Thyne: zero coded coup events after 1961/1987; the smooth 1988-93
    # Roh Tae-woo transition) supports a LOWER early-year risk than MFU's
    # own 0.15 self-assessment of its own idealised constitution, while
    # kept deliberately nonzero per the required "no zero coups" framing
    # (research README flag F1; the 2024-12-03 martial-law episode).
    COUP_RISK_EARLY_YEARS: float = 0.05
    # GUESS — slower decay needed since risk starts already low relative
    # to MFU's own calibration.
    COUP_RISK_DECAY_RATE: float = 0.005
    # GUESS, within the research package's own recommended 0.00-0.02
    # year-zero coup-risk band (§2.6).
    COUP_RISK_FLOOR: float = 0.01
    # GUESS — repurposed as a real, citeable institutional-build-out
    # milestone: 2002 marks the establishment of KICAC (Korea Independent
    # Commission Against Corruption), 14 years after this file's 1988
    # year-zero (research README §1 IIGConfig section).
    TRANSITION_EMBED_YEAR: int = 14
    # ENGINE-REQUIRED FIELD. GUESS magnitude slightly above MFU's own 0.01,
    # CONFIDENT direction — grounded in V-Dem's real, steep institutional-
    # constraint consolidation during Korea's first post-transition decade
    # (legislative constraints 0.073 in 1987 -> 0.719 by 1993; judicial
    # constraints 0.500 -> 0.835 over the same window, research §2.3
    # table). model_phase3.py reads this field literally at
    # `_civilian_chain_rules()`; a missing section/field crashes the
    # engine loudly by design (not optional).
    TRUST_GAIN_PER_CLEAN_YEAR: float = 0.012
    # GUESS magnitude (kept identical to MFU's own figure — no Korea-
    # specific number is researched), CONFIDENT direction — the real
    # 2024-12 martial-law episode's sharp, documented trust/approval
    # collapse supports a comparably large single-shock magnitude.
    TRUST_LOSS_IF_COUP_ATTEMPTED: float = 0.25
    # CONFIDENT — inert; no ethnic-minority structure exists, channel
    # neutral per research's explicit recommendation.
    ETHNIC_TRUST_MULTIPLIER: float = 1.00
    # CONFIDENT — Oct 28 1987 referendum (94.46% approval); in force
    # 25 Feb 1988.
    TRANSITION_TRIGGERED_BY: str = "1987_constitutional_referendum_sixth_republic"
    TRANSITION_YEAR_ZERO: int = 0
    # CONFIDENT — ties directly to Korea's single non-renewable 5-year
    # presidential term (Art. 70); arguably an even cleaner real match than
    # MFU's own framing, since Korea's president serves exactly one term.
    REVIEW_INTERVAL_YEARS: int = 5


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS — Scenario SK calibration
# Maps to: constitution.py / constitution_2008.py -> SimulationConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Scenario SK simulation parameters"""

    SCENARIO: str = "SK"
    SCENARIO_NAME: str = "South_Korea_1987_Democratization_Constitution"
    # CONFIDENT — research README §0's explicit recommended label.
    CONSTITUTIONAL_FRAMEWORK: str = "1987_republic_of_korea_constitution_sixth_republic"
    # CONFIDENT — V-Dem v16 political corruption index, South Korea, 1988
    # (research README §2.3/§2.6 table).
    YEAR_ZERO_CORRUPTION: float = 0.458
    # GUESS — NOT a survey-sourced figure. The research package explicitly
    # states (§2.6, limitation L2): "needs a real survey number... do not
    # guess" and flags WVS W2 (1990-94) Korea E069_11 as the earliest
    # usable value, NOT YET EXTRACTED from primary microdata. This value is
    # a structural proxy derived from V-Dem's own 1988 civil-liberties/
    # polyarchy jump (0.616, research §2.3), scaled to sit in the engine's
    # expected trust_index range — it is NOT a survey percentage and must
    # not be cited as one. Flag to senior-data-analyst / senior-researcher
    # before this number is treated as sourced in any manuscript table.
    YEAR_ZERO_TRUST: float = 0.45
    # GUESS — real-world plausible Korean income Gini circa 1988-1990
    # (commonly cited range ~0.34-0.39 in Korean income-distribution
    # literature); NOT independently verified against a specific KOSIS/
    # World Bank citation in the research package, which explicitly asked
    # for "the exact year" to be cited — not yet done here, flagged.
    YEAR_ZERO_GINI: float = 0.39
    # GUESS — real-world plausible late-1980s Korean employment rate;
    # not independently sourced in the research package.
    YEAR_ZERO_EMPLOYMENT: float = 0.68
    # CONFIDENT — direct consequence of "no constitutionally recognised
    # ethnic-group structure" (research §1 FoundationalConfig note); the
    # ethnic channel is inert for this scenario.
    YEAR_ZERO_ETHNIC_TENSION: float = 0.0
    # CONFIDENT — research README §2.6's explicit recommended range
    # (0.00-0.02); the upper bound is used deliberately to avoid the
    # withdrawn "zero coups" framing (flag F1) while remaining consistent
    # with Powell-Thyne's real zero-coded-events-since-1961 record.
    YEAR_ZERO_COUP_RISK: float = 0.02
    # GUESS — rescaled from the real WGI 1996 Political Stability point
    # estimate (0.57, research §2.6; WGI's raw scale is approximately
    # -2.5..+2.5) via a simple linear (x + 2.5) / 5.0 transform to sit in
    # the engine's expected [0,1] range: (0.57 + 2.5) / 5.0 = 0.614,
    # rounded. This is a 1996 observation applied to this file's 1988
    # year-zero slot — an 8-year gap the research package explicitly flags
    # as unavoidable given real data availability (WGI does not cover
    # 1988).
    YEAR_ZERO_STABILITY: float = 0.61
    # CONFIDENT — direct opposite of Myanmar 2008; matches this entire
    # file's framing throughout.
    MILITARY_CONTROLS_LEGISLATURE: bool = False
    MILITARY_CONTROLS_EXECUTIVE: bool = False
    MILITARY_CONTROLS_JUDICIARY: bool = False
    # CONFIDENT — Korea's rights are meaningfully enforceable in ordinary
    # times via an independent judiciary/Constitutional Court; a genuine,
    # major, real contrast with Myanmar 2008's "exist on paper, not in
    # practice."
    RIGHTS_ENFORCEABLE: bool = True

    # CONFIDENT — locked Monte Carlo design (same population size, same
    # 50-year horizon for every scenario); NOT a constitutional parameter,
    # deliberately NOT varied from MFU/Myanmar 2008's values, same
    # precedent both existing files set.
    CITIZEN_AGENTS: int = 11_000
    # CONFIDENT — same reasoning; model_phase3.py reads this value from
    # MFU's own CONSTITUTION_MFU singleton directly regardless of active
    # scenario (same caveat constitution_2008.py's own comment carries),
    # included here only for field-contract completeness.
    TIME_STEPS: int = 50
    # CORRECTED 2026-10-20 per research README §6.2 (same correction as
    # FoundationalConfig.STATE_COUNT / FederalConfig.STATE_COUNT above):
    # this previously listed Korea's PRESENT-DAY 17 first-level divisions.
    # Daejeon (elevated 1 Jan 1989), Ulsan (15 Jul 1997) and Sejong
    # (2 Jul 2012) did not exist as separate first-level units at
    # simulation year zero (Feb 1988) — Daejeon/Sejong were part of
    # Chungcheongnam-do, Ulsan was part of Gyeongsangnam-do. CONFIDENT
    # these 14 are the real year-zero first-level administrative division
    # names (Seoul Special City; Busan/Daegu/Incheon/Gwangju directly-
    # governed cities; 9 provinces), independently cross-checked against
    # the 13th presidential election's (16 Dec 1987) province-level
    # results table, which has exactly these same 14 rows (README §6.3).
    # Order here is PARALLEL to STATE_POPULATION_WEIGHTS immediately below
    # (same order, same length, required by the field contract) — NOT the
    # same order as the old 17-item list, do not assume positional
    # continuity with any stale downstream reference.
    #
    # CURRENTLY INERT AT RUNTIME for the reason already documented in this
    # file's top-of-module "KNOWN ENGINE WIRING GAP" disclaimer: as of
    # 2026-10-20 this field only takes mechanical effect once
    # model_phase3.py's own per-scenario state-list fix and
    # agents/citizen.py's _assign_state()/_assign_ethnicity() (which now
    # read constitution.simulation.SIMULATION_STATES/
    # STATE_POPULATION_WEIGHTS/STATE_ETHNIC_WEIGHTS when present, per the
    # 2026-10-20 field contract in config/constitution.py's SimulationConfig
    # comment) actually land for this scenario. Filled with real, correct
    # data now so no further edit to this file is needed once that wiring
    # is confirmed live.
    SIMULATION_STATES: Tuple[str, ...] = (
        "seoul", "gyeonggi", "busan", "gyeongnam",
        "chungnam", "gyeongbuk", "jeonnam", "daegu",
        "jeonbuk", "incheon", "gangwon", "chungbuk",
        "gwangju", "jeju",
    )
    # STATE_POPULATION_WEIGHTS — per-country geography field contract (see
    # config/constitution.py's SimulationConfig comment for the full
    # schema). CONFIDENT, sourced: Statistics Korea 1990 Population and
    # Housing Census per-division figures as tabulated by citypopulation.de
    # (accessed 2026-10-20), reconstructed onto the 14 year-zero (1988)
    # units per research README §6.2 — Daejeon (1,049,578) and the Sejong
    # area (90,502) folded back into Chungcheongnam-do; Ulsan (805,355)
    # folded back into Gyeongsangnam-do. This is arithmetic on published
    # census figures, not an estimate. GUESS-tagged limitation (README L1):
    # 1990 is 2 years after year zero; the nearer 1985 census total is
    # sourced (40,466,577) but a complete 14-division 1985 table could not
    # be retrieved for this package, so 1990 shares are used as the best
    # available proxy (README notes the 1985-vs-1990 share drift is at
    # most ~1-2 percentage points, e.g. Seoul 23.8% in 1985 vs 24.45% here).
    # Same order as SIMULATION_STATES above. Sums to 1.0002, not exactly
    # 1.0, due to published-percentage rounding in the source table, not a
    # transcription error.
    STATE_POPULATION_WEIGHTS: Tuple[float, ...] = (
        0.2445, 0.1394, 0.0888, 0.0833,
        0.0706, 0.0629, 0.0578, 0.0544,
        0.0477, 0.0443, 0.0364, 0.0320,
        0.0262, 0.0119,
    )
    # STATE_ETHNIC_WEIGHTS / STATE_ETHNIC_WEIGHTS_DEFAULT — per-country
    # geography field contract. CONFIDENT: every weight tuple below is
    # exactly 1 element long because FederalConfig.ETHNIC_GROUPS = 1 for
    # this scenario (no constitutionally recognised multi-ethnic
    # structure — Korea is among the most ethnically homogeneous states in
    # the world, research README §6.3's explicit instruction is NOT to
    # fabricate an 8-slot Myanmar-style array here). With exactly one
    # group, every state's weight tuple is mathematically forced to (1.0,)
    # — this is a formality, not a modelling choice with real content.
    #
    # DELIBERATE NON-USE of the Yeongnam/Honam regional-bloc data: the
    # research README (§6.3) documents a real, heavily-studied, non-ethnic
    # political cleavage — Yeongnam (Gyeongsang) vs. Honam (Jeolla)
    # regionalism — anchored on real 1987 13th-presidential-election
    # province vote shares (e.g. Gwangju 94.41% Kim Dae-jung vs. Daegu
    # 70.70% Roh Tae-woo), and recommends a 5-slot
    # [capital, yeongnam, honam, chungcheong, gangwon_jeju] array as
    # Korea's real substitute for an ethnic composition array. That
    # recommendation is NOT encoded into STATE_ETHNIC_WEIGHTS here,
    # deliberately: this field's length is contractually tied to
    # ETHNIC_GROUPS (1 for Korea), and engine/cves.py's
    # _get_ethnic_group_count() plus agents/citizen.py's
    # _assign_ethnicity() both validate weight-tuple length against that
    # same count — a 5-element array would not fit this axis and, per the
    # README's own caveat, SHOULD NOT be wired through the constitutional-
    # allocation-shaped ethnic channel anyway, since Korea's regional
    # cleavage has no constitutional status (no reserved seats, no
    # resource transfers) unlike Myanmar's ethnic structure. If a future
    # task wants Yeongnam/Honam regionalism to drive social/trust/
    # grievance dynamics, it needs a NEW, separate field (outside this
    # ETHNIC_GROUPS-sized contract, out of scope for this encoding task,
    # which owns only this file) — not a repurposing of this one. Flagging
    # this explicitly rather than silently discarding real, sourced data.
    STATE_ETHNIC_WEIGHTS: Dict[str, Tuple[float, ...]] = field(default_factory=lambda: {
        "seoul":     (1.0,),
        "gyeonggi":  (1.0,),
        "busan":     (1.0,),
        "gyeongnam": (1.0,),
        "chungnam":  (1.0,),
        "gyeongbuk": (1.0,),
        "jeonnam":   (1.0,),
        "daegu":     (1.0,),
        "jeonbuk":   (1.0,),
        "incheon":   (1.0,),
        "gangwon":   (1.0,),
        "chungbuk":  (1.0,),
        "gwangju":   (1.0,),
        "jeju":      (1.0,),
    })
    STATE_ETHNIC_WEIGHTS_DEFAULT: Tuple[float, ...] = (1.0,)
    # DELIBERATELY UNCHANGED from MFU/Myanmar 2008, not a guess by omission
    # — same precedent and same open-research-question flag both existing
    # files already carry: whether population archetype composition should
    # differ by constitution is a real, separate research question, not
    # resolved here, and changing it would be a new modelling decision with
    # large, hard-to-isolate effect-size consequences well beyond this
    # encoding task. (Also currently inert for the same reason as
    # SIMULATION_STATES above — agents/citizen.py reads ARCHETYPES via the
    # same unconditional bare-CONSTITUTION import.)
    ARCHETYPES: Dict = field(default_factory=lambda: {
        "civic_champion": 0.15,
        "pragmatic_survivor": 0.30,
        "ethnic_loyalist": 0.20,
        "ambitious_meritocrat": 0.15,
        "disillusioned_youth": 0.10,
        "rural_traditionalist": 0.07,
        "trauma_carrier": 0.03,
    })
    # CONFIDENT — kept identical to MFU/Myanmar 2008 for the same reason as
    # AmendmentConfig.CITIZENS_ASSEMBLY_SIZE above: no real civic-lottery
    # mechanism exists under the 1987 Constitution either.
    CITIZENS_ASSEMBLY_SIZE: int = 320


# ══════════════════════════════════════════════════════════════════════════════
# ELITE AGENT LAYER — country-accurate role titles and system prompts
# Read by engine/elite_agents_v3.py (AGENT_DISPLAY_NAMES_BY_SCENARIO /
# SCENARIO_PROMPTS) via getattr(constitution_instance, "ELITE_ROLE_TITLES"/
# "ELITE_SYSTEM_PROMPTS", None). Keys MUST match CHAIN_ORDER_CIVILIAN's
# 7 role-function ids exactly (senior_general, finance_minister,
# central_bank_governor, iig_director, chief_justice, president, chancellor)
# — these are fixed structural chain-position ids baked into the engine,
# not something this file can rename; only the TITLE/PROMPT content per
# position is country-specific.
#
# Mapping chosen (research README §3's own recommended 7 roles, assigned to
# the 7 fixed structural slots; schema-mapping disclosure, consistent with
# this file's overall convention):
#   senior_general        -> Chairman of the Joint Chiefs of Staff (slot 7
#                             in research's own list; placed in chain
#                             position 1 deliberately, so the FIRST voice in
#                             the chain is the military one, exactly as in
#                             Myanmar 2008/MFU's chain structure, but with
#                             completely different real content: Korea's
#                             military has no constitutional political role
#                             at all and cannot legally trigger a coup).
#   finance_minister       -> Deputy Prime Minister for Economic Affairs and
#                             Minister of Economy and Finance. GUESS: a
#                             real, well-documented statutory cabinet post
#                             (Government Organization Act), NOT one of the
#                             research package's own enumerated 7 titles —
#                             added because the structural chain requires an
#                             economic-policy voice and the research
#                             package's 7 roles did not include one.
#   central_bank_governor  -> Governor of the Bank of Korea. GUESS, same
#                             reasoning: real, well-documented (Bank of
#                             Korea Act, independence reinforced 1997-98),
#                             statutory not constitutional, not one of the
#                             research package's own enumerated 7.
#   iig_director           -> Chairman, Board of Audit and Inspection
#                             (research README §3 slot 6, the
#                             constitutionally-grounded choice over the
#                             statutory ACRC alternative also offered).
#   chief_justice          -> President of the Constitutional Court
#                             (research README §3 slot 5).
#   president              -> President of the Republic of Korea (research
#                             README §3 slot 1).
#   chancellor             -> Prime Minister (research README §3 slot 2).
# NOT used in this 7-slot mapping (available per research's own "optional
# 8th role" suggestion if the chain is ever widened): Speaker of the
# National Assembly, Leader of the Opposition.
# ══════════════════════════════════════════════════════════════════════════════

ELITE_ROLE_TITLES: Dict[str, str] = {
    "senior_general":        "Chairman of the Joint Chiefs of Staff",
    "finance_minister":      "Deputy Prime Minister for Economic Affairs and Minister of Economy and Finance",
    "central_bank_governor": "Governor of the Bank of Korea",
    "iig_director":          "Chairman, Board of Audit and Inspection",
    "chief_justice":         "President of the Constitutional Court",
    "president":             "President of the Republic of Korea",
    "chancellor":             "Prime Minister",
}


ELITE_SYSTEM_PROMPTS: Dict[str, str] = {
    "senior_general": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Chairman of the Joint Chiefs of Staff of the Republic of Korea Armed Forces, under the 1987 Constitution.
Constitutional position: Art. 5(2) mandates that the Armed Forces' "political neutrality shall be maintained." Art. 74(1) makes the President, not you, Commander-in-Chief. Art. 86(3)/87(4) bar active-duty officers from the Prime Minister's office or the State Council entirely.
There is NO constitutional coup mechanism (COUP_LEGAL_MECHANISM=False). You have no independent political standing and no legal pathway to act against the civilian government. Korea's last successful military coup was in 1961, before this constitution existed; since 1987 every constitutional crisis (including a 2024 martial-law declaration by a sitting President, which the National Assembly lifted within hours under Art. 77(5)) has been resolved through civilian constitutional mechanisms, not the military acting on its own authority.

Your role is strictly professional and apolitical: assess the State Briefing for genuine external/defense threats, not domestic political conditions. You may flag military-readiness concerns in your reasoning, but coup_signal must reflect your honest constitutional assessment, under this constitution the correct assessment is almost always that no military political action is constitutionally available to you, regardless of domestic conditions.

Groups: this constitution encodes ETHNIC_GROUPS=1 (a single neutral placeholder index, not a real ethnic taxonomy, Korea has no constitutionally recognised multi-ethnic structure). Your ethnic_weights list must have exactly one element, set it to approximately 1.0; do not treat it as a substantive allocation decision.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with exactly:
<DECISION>
{"budget_weight": 0.50, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Professional defense-readiness assessment; no constitutional basis for political action under Article 5(2)"}
</DECISION>""",

    "finance_minister": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Deputy Prime Minister for Economic Affairs and Minister of Economy and Finance of the Republic of Korea.
Mandate (Art. 119(1)/(2)): Korea runs a market economy respecting individual freedom and creativity, but the State may regulate to ensure balanced growth, maintain income distribution, prevent market domination and abuse of economic power, and "democratise the economy." Budget bills require National Assembly passage (Art. 54); the Assembly may not increase expenditure or create new budget items without government consent (Art. 57).
You have seen the Joint Chiefs of Staff Chairman's assessment above. There is no federal/ethnic resource-transfer structure here (Korea is unitary, not federal) — your budget_weight should reflect your assessment of fiscal expansion/redistribution support for the National Assembly's budget process, not an ethnic-transfer allocation.

Groups: this constitution encodes ETHNIC_GROUPS=1, ethnic_weights must be a single-element list set to approximately 1.0, it has no real referent for Korea.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{"budget_weight": 0.60, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Economic democratisation and balanced-growth assessment under Article 119(2)"}
</DECISION>""",

    "central_bank_governor": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Governor of the Bank of Korea.
Mandate: price stability and financial-system stability, with statutory independence from political direction (Bank of Korea Act, substantially strengthened by the 1997-98 independence reform). This is a real, well-documented statutory institution, not a literal constitutional office — the 1987 Constitution's Art. 119 market-economy framework is the broader constitutional backdrop for your mandate.
You have reviewed the Joint Chiefs of Staff Chairman's and the Deputy Prime Minister for Economic Affairs' assessments. Set budget_weight reflecting your independent monetary-stability judgement, not political alignment with the executive's fiscal posture.

Groups: this constitution encodes ETHNIC_GROUPS=1, ethnic_weights must be a single-element list set to approximately 1.0, it has no real referent for Korea.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{"budget_weight": 0.55, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Independent monetary-stability assessment"}
</DECISION>""",

    "iig_director": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Chairman of the Board of Audit and Inspection (BAI) of the Republic of Korea.
Constitutional mandate (Art. 97-100): BAI is established under the President's direct jurisdiction to audit government accounts and inspect the performance of government agencies and public officials. You are appointed by the President with National Assembly consent for a four-year term (one reappointment permitted), and report annually to both the President and the National Assembly.
Korea's real anti-corruption record has improved substantially since this constitution took effect (V-Dem political corruption index: 0.458 in 1988, declining to roughly 0.113 by the late 2010s), driven in large part by institutions established AFTER you in time (KICAC 2002, ACRC 2008, the Improper Solicitation and Graft Act 2016, the Corruption Investigation Office 2021) — treat your own investigative posture as genuinely improving over the simulation's timeline, not static.
You have seen all three prior assessments. Set budget_weight to reflect the resourcing you believe anti-corruption/audit enforcement requires given current conditions.

Groups: this constitution encodes ETHNIC_GROUPS=1, ethnic_weights must be a single-element list set to approximately 1.0, it has no real referent for Korea.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{"budget_weight": 0.55, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Audit and anti-corruption enforcement assessment under Article 97-100"}
</DECISION>""",

    "chief_justice": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Constitutional Court of the Republic of Korea.
Constitutional mandate (Art. 111-113): the Court adjudicates unconstitutionality, impeachment, political-party dissolution, and competence disputes. Decisions on these matters require six of nine justices concurring (Art. 113(1)). You are appointed by the President with National Assembly consent (Art. 111(4)); the Court's nine justices serve six-year, reappointable terms (Art. 112(1)).
This Court has twice actually removed a sitting President from office by adjudicating an impeachment the National Assembly passed: Park Geun-hye (impeached December 2016, removed by unanimous ruling March 2017) and Yoon Suk Yeol (impeached December 2024 after declaring martial law, removed by the Court April 2025). Rights under this constitution may be restricted by law only within the limits of Art. 37(2)'s "essence guarantee" — no essential aspect of a right may be violated even when restricted.
If the Joint Chiefs of Staff Chairman or any prior assessment signals coup conditions or a constitutional crisis, you must reason from the Court's real adjudicative authority, not from any assumption that military/executive consolidation is constitutionally available — it is not.

Groups: this constitution encodes ETHNIC_GROUPS=1, ethnic_weights must be a single-element list set to approximately 1.0, it has no real referent for Korea.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{"budget_weight": 0.50, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Constitutional review assessment under Article 111-113"}
</DECISION>""",

    "president": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Republic of Korea.
Constitutional position (Art. 66, 67, 70, 74): elected by direct popular vote for a single, non-renewable five-year term; head of state, head of the executive branch, and Commander-in-Chief of the Armed Forces. Art. 76 lets you issue emergency orders with the force of law, but they lose effect without National Assembly approval. Art. 77 lets you proclaim martial law — but Art. 77(5) is absolute: "When the National Assembly requests the lifting of martial law by a majority of the total members, the President shall comply." You have no veto over that request.
You have reviewed all five prior advisors' assessments, including the Joint Chiefs of Staff Chairman's. There is no constitutional path to total power transfer available to you or to the military under any condition in this constitution (contrast other 2026-encoded scenarios, where such a mechanism exists) — your authority, however real, is bounded by the National Assembly and the Constitutional Court at every turn.
Primary focus: public trust and the constitutionally mandated pursuit of peaceful unification (Art. 4, Art. 69's presidential oath). Your budget_weight should reflect your endorsement of policy that builds durable public trust, consistent with Art. 119(2)'s balanced-growth/income-distribution mandate.

Groups: this constitution encodes ETHNIC_GROUPS=1, ethnic_weights must be a single-element list set to approximately 1.0, it has no real referent for Korea.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{"budget_weight": 0.60, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Trust-building and balanced-growth priority under Article 119(2) and Article 69"}
</DECISION>""",

    "chancellor": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Prime Minister of the Republic of Korea.
Constitutional position (Art. 86): appointed by the President with National Assembly consent; you assist the President and direct the Executive Ministries under the President's command (Art. 86(2)). Art. 86(3)/87(4) bar active-duty military officers from your office or from State Council membership — you are, by constitutional design, a civilian check embedded inside the executive branch itself. Art. 71: if the presidency becomes vacant or the President is incapacitated, you act in the President's stead in the statutory order of priority. The National Assembly may pass a non-binding recommendation for your removal (Art. 63); the President is not constitutionally bound to act on it, unlike a presidential impeachment, which is binding once the Constitutional Court rules.
You have reviewed all six prior advisors' assessments, including any coup signal from the Joint Chiefs of Staff Chairman and the constitutional reasoning from the Constitutional Court President. No coup or total-power-transfer mechanism is constitutionally available under this instrument. Set your budget_weight to reflect your coordination of Executive Ministry budget requests toward the balanced-growth, income-distribution, and peaceful-unification mandates running throughout this constitution.

Groups: this constitution encodes ETHNIC_GROUPS=1, ethnic_weights must be a single-element list set to approximately 1.0, it has no real referent for Korea.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{"budget_weight": 0.65, "ethnic_weights": [1.0], "coup_signal": false, "reason": "Executive coordination under civilian-supremacy safeguards, Article 86-87"}
</DECISION>""",
}


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# Must mirror MFUConstitution / Myanmar2008Constitution class structure exactly
# ══════════════════════════════════════════════════════════════════════════════

class SouthKorea1987Constitution:
    """
    Master South Korea 1987 Democratization Constitution object for Ka-Nova
    Scenario SK (chain_type: "civilian").

    Usage (via config/scenario_registry.py, NOT a direct import switch):
        from config.scenario_registry import get_scenario
        entry = get_scenario("SK")
        constitution = entry.constitution   # this singleton

    Attribute names mirror MFUConstitution / Myanmar2008Constitution exactly
    so model_phase3.py's self.CONSTITUTION dispatch can use any of them
    interchangeably. ELITE_ROLE_TITLES / ELITE_SYSTEM_PROMPTS are additional
    instance attributes read by engine/elite_agents_v3.py if present.
    """

    def __init__(self):
        self.foundational = FoundationalConfig()
        self.rights = RightsConfig()
        self.merit = MeritConfig()
        self.executive = ExecutiveConfig()
        self.chambers = ChamberConfig()
        self.judiciary = JudiciaryConfig()
        self.iig = IIGConfig()
        self.federal = FederalConfig()
        self.military = MilitaryConfig()
        self.economic = EconomicConfig()
        self.science = ScienceConfig()
        self.amendment = AmendmentConfig()
        self.transition = TransitionConfig()
        self.safeguards = SafeguardConfig()
        self.crypto_justice = CryptoJusticeConfig()
        self.emergency = EmergencyConfig()
        self.roe = ROEConfig()
        self.psychology = PsychConfig()
        # Required for chain_type: "civilian" — model_phase3.py:521 reads
        # this section literally and crashes loudly (AttributeError) if
        # missing. See TatmadawTransitionConfig's own docstring for the
        # real South Korea mapping.
        self.tatmadaw_transition = TatmadawTransitionConfig()
        self.north_star = NorthStarConfig()
        self.simulation = SimulationConfig()

        # Optional engine/elite_agents_v3.py hooks — see that module's
        # AGENT_DISPLAY_NAMES_BY_SCENARIO / SCENARIO_PROMPTS construction,
        # which does getattr(entry.constitution, "ELITE_ROLE_TITLES"/
        # "ELITE_SYSTEM_PROMPTS", None) on this singleton instance.
        self.ELITE_ROLE_TITLES = ELITE_ROLE_TITLES
        self.ELITE_SYSTEM_PROMPTS = ELITE_SYSTEM_PROMPTS

    def validate(self) -> bool:
        """Validate critical South Korea 1987 constitution constraints.
        NOTE: these assertions are SK-specific and deliberately differ from
        Myanmar2008Constitution.validate()'s checks (e.g. military seat
        percentage and total-power-transfer are the OPPOSITE boolean/value
        here — copying the 2008 file's literal assertions would be wrong
        for this file)."""
        checks = [
            # Rights ARE suspendable under martial law (Art. 77(3)), same
            # direction as Myanmar 2008, unlike MFU.
            self.rights.RIGHTS_SUSPENDABLE is True,
            # Zero reserved military seats — the defining structural
            # contrast with every other encoded scenario.
            self.chambers.MILITARY_SEAT_PERCENTAGE == 0.0,
            # No constitutional mechanism exists for total power transfer
            # to the military/executive — the defining emergency-powers
            # contrast with Myanmar 2008.
            self.emergency.TOTAL_POWER_TRANSFER_POSSIBLE is False,
            # No legal coup mechanism exists.
            self.military.COUP_LEGAL_MECHANISM is False,
            # Merit weights must still sum to 1.0 even though no
            # constitutional merit-formula exists (Ka-Nova modelling proxy).
            self.merit.weights_valid,
            # Civilian chain requirement: the engine-required field must be
            # present and numeric.
            isinstance(self.tatmadaw_transition.TRUST_GAIN_PER_CLEAN_YEAR, float),
        ]
        return all(checks)


# Singleton — import this everywhere (registry key: config.constitution_southkorea:CONSTITUTION_SOUTHKOREA)
CONSTITUTION_SOUTHKOREA = SouthKorea1987Constitution()


if __name__ == "__main__":
    c = CONSTITUTION_SOUTHKOREA
    print("constitution_southkorea.py loaded successfully")
    print(f"   Scenario:                {c.simulation.SCENARIO} — {c.simulation.SCENARIO_NAME}")
    print(f"   Rights suspendable:      {c.rights.RIGHTS_SUSPENDABLE} (martial law only, Art. 77(3); essence-guaranteed, Art. 37(2))")
    print(f"   Military seat %:         {c.chambers.MILITARY_SEAT_PERCENTAGE:.0%}")
    print(f"   Total power transfer:    {c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE}")
    print(f"   Coup constitutional:     {c.military.COUP_LEGAL_MECHANISM}")
    print(f"   Legislative lift (Art 77(5)):  threshold={c.emergency.EMERGENCY_LEGISLATIVE_LIFT_THRESHOLD}, binding={c.emergency.EMERGENCY_LIFT_BINDING_ON_EXECUTIVE}")
    print(f"   BAI (IIG) effectiveness: {c.iig.INITIAL_EFFECTIVENESS} -> {c.iig.MAX_EFFECTIVENESS} (static schema; real trajectory is time-varying, see flag F3)")
    print(f"   Amendment threshold:     {c.amendment.STANDARD_AMENDMENT_THRESHOLD:.0%} (uniform procedure, zero successful amendments since 1988)")
    print(f"   Year-Zero corruption:    {c.simulation.YEAR_ZERO_CORRUPTION} (V-Dem 1988, CONFIDENT)")
    print(f"   tatmadaw_transition.TRUST_GAIN_PER_CLEAN_YEAR: {c.tatmadaw_transition.TRUST_GAIN_PER_CLEAN_YEAR} (engine-required field, present)")
    print(f"   ELITE_ROLE_TITLES keys:  {sorted(c.ELITE_ROLE_TITLES.keys())}")
    print(f"   ELITE_SYSTEM_PROMPTS keys match ELITE_ROLE_TITLES: {sorted(c.ELITE_SYSTEM_PROMPTS.keys()) == sorted(c.ELITE_ROLE_TITLES.keys())}")
    print(f"   Validation:              {'PASS' if c.validate() else 'FAIL'}")
    print()

    # Count how many ??? remain (same convention as constitution_2008.py)
    import inspect
    source = inspect.getsource(SouthKorea1987Constitution)
    count = source.count("???")
    if count > 0:
        print(f"   WARNING: {count} ??? placeholders still need filling")
    else:
        print("   All placeholders filled — ready for integration")
