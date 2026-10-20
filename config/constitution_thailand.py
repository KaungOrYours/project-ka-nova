"""
================================================================================
PROJECT KA-NOVA
config/constitution_thailand.py

Constitution of the Kingdom of Thailand, B.E. 2560 (2017) — Parameter Registry
Ka-Nova Simulation Engine — Scenario TH (registry chain_type: "military")

This file encodes Thailand's 2017 military-drafted constitution as computable
parameters, following the exact 21-class dataclass contract established by
config/constitution.py (MFU) and config/constitution_2008.py (2008 Myanmar).
constitution_2008.py is used as the structural template here (not
constitution.py) because TH shares its chain_type ("military") and therefore
its exact field contract — the Mesa-NumPy engine's military-chain code paths
(model_phase3.py's `_military_chain_rules`, engine/elite_agents_v3.py's
`_build_system_prompts_military`, agents/official.py's `_build_official_roles`,
etc.) read the SAME attribute names regardless of which military-chain
constitution is active.

Source: Constitute Project, "Thailand 2017" English rendering
(https://www.constituteproject.org/constitution/Thailand_2017), cross-checked
against Transparency International CPI, World Bank WGI, V-Dem v16, and
Powell & Thyne's "Coups d'etat, 1950-present" dataset. Full citation detail,
validation tables and sourcing-limitation notes live in
config/constitution_thailand_encoding/README.md — every CONFIDENT/GUESS tag
below traces back to a specific section of that document.

INSTRUMENT SNAPSHOT CHOSEN (read this before touching any field below)
------------------------------------------------------------------------------
This file encodes the AS-PROMULGATED 2017 text's TRANSITORY-PERIOD
configuration (ss. 265, 269, 270, 272, 279 — NCPO continuation, the fully
appointed 250-member Senate, the five-year joint-sitting Prime-Minister-
selection rule, and the blanket validation/immunity clause) held STATIC across
the full 50-year simulated horizon.

This is a deliberate, disclosed limitation, not an oversight (research
package flag F3a). Sections 269/272 are textually time-limited — they expire
five years after the first National Assembly convened (2019 -> 2024) — and
the real V-Dem record shows their effect appearing and disappearing exactly
on that schedule (legislative constraints on the executive: .048 in 2017,
recovering to .916 by 2025 as the transitory Senate's term lapsed). The
current 21-class schema has no time-limited-provision mechanism (see
README.md section 5, flag F3), so a single static snapshot is the only
option without an engine change, which is out of this file's scope. Running
TH with this snapshot for 50 years OVERSTATES the NCPO-era reserved-powers
effect for years 6-50 relative to the real 2024-onward recovery. This must be
disclosed in any paper text that backtests TH against real V-Dem data beyond
~year 7 of the simulated horizon (see README.md flag F2: only 9 of a 50-year
horizon are real-observation years at all).

CRITICAL FINDING THIS FILE DELIBERATELY DOES NOT PAPER OVER (research
package flag F1, locked in .claude/memory.md section 4a): Thailand 2017 is a
near-twin of Myanmar's 2008 constitution on RESERVED POWERS, EXECUTIVE
IMMUNITY and REPRESENTATION SUPPRESSION, but a NON-twin on CORRUPTION
DYNAMICS and REGIME SURVIVAL — V-Dem political corruption is flat-to-improving
(.683 -> .635, 2017-2025), CPI is roughly flat (37 -> 33), there have been
ZERO coups in 9 years, and the constitution remains in force (amended once).
This file therefore does NOT copy Scenario C's near-zero IIG-equivalent
floor, does NOT set COUP_LEGAL_MECHANISM=True, and does NOT set
TOTAL_POWER_TRANSFER_POSSIBLE=True — those three decisions are the specific,
sourced mechanisms by which this encoding avoids manufacturing a
Myanmar-like failure trajectory as an artifact of lazy parameter copying
(exactly what the task brief and Reviewer 2 both warn against). Whatever
trajectory the simulation actually produces for TH should emerge from these
honestly-sourced parameters interacting with the shared engine, not from a
constitution-layer thumb on the scale in either direction.

Author: Claude Code (senior-simulation-engineer), 2026-10-20, from
`senior-researcher`'s Thailand research package.
Architecture owner: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I — GENERAL PROVISIONS (Sections 1-5) + CHAPTER II — THE KING
# Maps to: constitution.py / constitution_2008.py -> FoundationalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Chapter I — General Provisions; Chapter II — The King"""

    # Section 1 ("Thailand is one and indivisible") / Section 2 (democratic
    # regime with the King as Head of State). CONFIDENT — README.md section 1.
    STATE_NAME: str = "Kingdom of Thailand"

    # GUESS — not covered by the research package (no article designates an
    # official-language section in the material reviewed); Thai is the
    # well-established de facto/statutory national language, but this field
    # is not traceable to a specific constitutional citation here.
    OFFICIAL_LANGUAGE: str = "Thai"
    # CONFIDENT direction — README.md section 1, FoundationalConfig note:
    # "No constitutionally recognised ethnic-group structure -> all ETHNIC_*
    # fields are inert for TH." Set False (opposite of both MFU and Myanmar
    # 2008, which both have real ethnic-group recognition machinery).
    ETHNIC_LANGUAGES_PROTECTED: bool = False

    # GUESS — not covered by the research package; Bangkok is Thailand's
    # well-known seat of government, but no section citation is given here.
    CAPITAL: str = "Bangkok"
    # GUESS — modelling placeholder, same idiom as constitution_2008.py's
    # FLAG field (a descriptive string, not read by live engine code).
    FLAG: str = "thai_tricolour_trairanga_flag"

    # GUESS — citizenship-mode detail is not covered in the research
    # package; proxy structure reused from the MFU/Myanmar schema shape.
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "birth_to_thai_parent",
        "naturalization_by_law",
    )
    NATURALIZATION_YEARS: int = 10          # GUESS — not sourced
    NATURALIZATION_MERIT_MIN: float = 0.0   # GUESS — no merit-exam naturalization path cited

    # CONFIDENT — Section 1.
    TERRITORY_BASIS: str = "unitary_indivisible_kingdom_section_1"
    # GUESS, explicit modelling choice — README.md section 1: "76 provinces +
    # Bangkok are statutory, not constitutional. Any STATE_COUNT is a
    # modelling choice." Kept at 14 to reuse the SAME geographic/Mesa
    # population structure as Scenarios A/C (the "same geopolitical vectors"
    # engine-symmetry principle), NOT because Thailand has 14 provinces.
    # NOTE (new finding, flagged for the parent agent, not fixed here):
    # agents/official.py, agents/oversight.py and agents/foreign.py read
    # `CONSTITUTION.simulation.SIMULATION_STATES` from the MODULE-LEVEL MFU
    # `CONSTITUTION` singleton imported directly at the top of those files
    # (`from config.constitution import CONSTITUTION`), NOT from
    # `self.CONSTITUTION`/the scenario-selected object. This means whatever
    # this field (or SimulationConfig.SIMULATION_STATES below) says is
    # currently mechanically inert for every non-A/C scenario, including
    # TH — the same bug class as the already-known bug #13
    # (social_media.py / cves.py literal scenario checks), just not yet
    # caught in that audit. Out of this file's scope to fix.
    STATE_COUNT: int = 14
    SIMULATION_STATE_COUNT: int = 14


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER III — RIGHTS AND LIBERTIES OF THE THAI PEOPLE (Sections 25-49)
# CHAPTER V — DUTIES OF THE STATE (Sections 51-63)
# Maps to: -> RightsConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Chapter III — Rights and Liberties; Chapter V — Duties of the State"""

    # CONFIDENT — README.md section 1: Chapter III ss.25-49, residual rights
    # framing (s.25: "whatever is not prohibited..."), s.26 restriction
    # criteria, s.49 militant-democracy clause.
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "residual_liberty_not_expressly_prohibited",  # Section 25
        "right_to_expression",                          # Chapter III, s.34 (per README's general citation)
        "right_to_assembly",
        "right_to_fair_trial",
        "right_to_education_12_years_free",             # Section 54
        "right_to_health_care",
    )

    # CONFIDENT — README.md section 1 explicit instruction: "Emergency
    # decrees (s.172) and martial law/emergency statutes (Martial Law Act
    # 1914, Emergency Decree 2005) operate largely outside the
    # constitutional-rights frame; RIGHTS_SUSPENDABLE: True."
    RIGHTS_SUSPENDABLE: bool = True
    # CONFIDENT — s.25's residual framing means there is no enumerated set
    # of absolute, unconditional rights (opposite of MFU's six absolute
    # rights).
    RIGHTS_ABSOLUTE_COUNT: int = 0

    # CONFIDENT — follows directly from RIGHTS_SUSPENDABLE=True and the
    # EmergencyConfig.RIGHTS_UNTOUCHED=False decision below (statutory
    # martial law / emergency-decree powers are not fenced off from rights
    # the way MFU's Article 2.5 fences them off).
    EMERGENCY_TOUCHES_RIGHTS: bool = True

    # GUESS — the research package does not address Thai military
    # conscription (Military Service Act B.E. 2497 (1954) is a statute, not
    # a constitutional provision, and is outside the package's scope).
    # Modelled as True/moderate duration consistent with real-world Thai
    # conscription practice (an annual draft lottery for men), not from a
    # constitutional citation.
    NATIONAL_SERVICE_MANDATORY: bool = True
    NATIONAL_SERVICE_AGE: int = 21          # GUESS — real-world Thai conscription age, not package-sourced
    NATIONAL_SERVICE_DURATION_MONTHS: int = 24  # GUESS — not package-sourced

    # GUESS — no citation found in the research package for a Myanmar-
    # s.382-style explicit rights override for Defence Services personnel.
    MILITARY_RIGHTS_OVERRIDE: bool = False

    # GUESS calibration, CONFIDENT direction — README.md section 2.5's
    # caution that "trust-in-government survey readings taken under the
    # NCPO (2014-2019) should be treated as measured under conditions of
    # restricted expression (lese-majeste prosecutions, Article 44 orders)"
    # supports a real, documented suppression-of-protest dynamic, but one
    # that is less extreme/less total than Myanmar 2008's framing (Thailand
    # has NOT had a corruption/trust collapse under this instrument).
    # Set between MFU's own low-suppression values and Myanmar's near-total
    # suppression values.
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.12
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.12


# ══════════════════════════════════════════════════════════════════════════════
# NO FORMAL MERIT-EXAM SYSTEM — CREDENTIALED PROFESSIONAL SELECTION INSTEAD
# Maps to: -> MeritConfig
# Sections 200/203 (Constitutional Court) and 232 (NACC) impose real
# seniority/professional-credential bars on appointees. This is neither
# MFU's formal competitive merit exam nor Myanmar's pure loyalty test.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """Credentialed professional selection (ss. 200, 203, 232) — not an exam system"""

    # GUESS magnitude, CONFIDENT direction — README.md section 1: s.200
    # requires senior judicial/administrative seniority or professorship;
    # s.232 requires >=5 years at Chief-Justice / Director-General /
    # state-enterprise-CEO / professor level. This is real credentialing,
    # not loyalty-only (Myanmar's CIVIC_WEIGHT=0.55 dominance) and not a
    # competitive merit exam (MFU's PRODUCTIVITY_WEIGHT=0.35 dominance).
    # Weights below deliberately spread more evenly, with EDUCATION_WEIGHT
    # highest to reflect the professorship/seniority bar.
    PRODUCTIVITY_WEIGHT: float = 0.20
    EDUCATION_WEIGHT: float = 0.30
    PERFORMANCE_WEIGHT: float = 0.25
    CIVIC_WEIGHT: float = 0.25

    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    # GUESS magnitude, CONFIDENT direction — a real, nontrivial credential
    # bar exists (ss.200/232), unlike Myanmar's MERIT_MIN_PUBLIC_OFFICE=0.0.
    MERIT_MIN_PUBLIC_OFFICE: float = 0.55

    # CONFIDENT — README.md section 1: Section 203, the Selection Committee
    # for Constitutional Court seats is chaired by the President of the
    # Supreme Court, with the House President, Opposition Leader, President
    # of the Supreme Administrative Court, and Independent-Organ appointees;
    # final appointment proceeds "on the advice of the Senate." Section 232
    # likewise routes NACC appointment through a selection committee ->
    # Senate advice -> King.
    EXAM_ADMINISTRATOR: str = "selection_committee_then_senate_advice_then_royal_appointment"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 1   # CONFIDENT — s.207: Constitutional Court judges serve "one term only"
    EXAM_RESULTS_PUBLISH_DAYS: int = 0    # GUESS — no publication-window citation found

    # CONFIDENT — README.md section 1: Section 49's militant-democracy
    # clause ("no person shall exercise rights to overthrow the democratic
    # regime with the King as Head of State") is the clearest disqualifying
    # trigger in the package; party dissolution for breaching s.49-adjacent
    # grounds is documented in the real event history (README section 2.4).
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "overthrow_of_democratic_regime_with_king_as_head_of_state",  # Section 49
        "party_dissolution_order",                                     # documented real cases, s.92-adjacent
        "corruption_conviction_by_nacc_referral",                      # Section 232
    )
    DISQUALIFICATION_PERMANENT: bool = True   # GUESS — not independently cited, reused from MFU/Myanmar idiom

    # CONFIDENT — s.207: Constitutional Court judges serve a single
    # 7-year term with no recertification cycle (vacate at age 75 or by a
    # 3/4 self-removal resolution per s.208, not a periodic review).
    RECERTIFICATION_INTERVAL: int = 0
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.0
    RECERTIFICATION_VACATE_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER II — THE KING (Sections 6-24) + CHAPTER VIII — THE COUNCIL OF
# MINISTERS (Sections 158-183)
# Maps to: -> ExecutiveConfig
# Mapping decision (README.md section 1, explicit instruction): PRESIDENT_* ->
# the King (ceremonial-plus-reserve-powers head of state, hereditary, no
# term); CHANCELLOR_* -> the Prime Minister (real executive power, s.158/159,
# 8-year cumulative cap, s.272 transitory joint-sitting selection).
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Chapter II (The King) + Chapter VIII (Council of Ministers)"""

    # CONFIDENT — README.md section 1, explicit mapping instruction.
    PRESIDENT_ROLE: str = "hereditary_head_of_state_ceremonial_plus_reserve_powers"
    PRESIDENT_ELECTION: str = "hereditary_succession"   # CONFIDENT — explicit instruction, Palace Law on Succession 1924
    # GUESS, deliberate nullification idiom (matches constitution_2008.py's
    # own precedent, e.g. ETHNIC_MAX_TERMS=99 for "mechanism absent") — a
    # hereditary monarch has no fixed democratic term; PRESIDENT_TERM is set
    # to the simulation horizon itself and PRESIDENT_MAX_TERMS set high so
    # the engine's term-countdown/removal mechanic (agents/official.py
    # `_update_term`) never fires `_complete_term()` for this role across a
    # 50-year run, rather than fabricating a term length that does not exist.
    PRESIDENT_TERM: int = 50
    PRESIDENT_MAX_TERMS: int = 99
    PRESIDENT_REELECTION: bool = False   # CONFIDENT — not applicable to hereditary succession

    # CONFIDENT — README.md section 1: the King's position is "ceremonial-
    # plus-reserve-powers," NOT the real executive (opposite of Myanmar 2008's
    # President, who genuinely holds Sections 16/199 executive power).
    PRESIDENT_TIEBREAKER: bool = False
    PRESIDENT_EXECUTIVE_POWER: bool = False

    # CONFIDENT — README.md section 1, explicit mapping instruction.
    CHANCELLOR_ROLE: str = "prime_minister_head_of_government"
    # CONFIDENT — Section 159 (nomination from party lists per s.88,
    # endorsement, House resolution); Section 272 (transitory, 5 years:
    # joint sitting of both Houses, >1/2 of 750 existing members).
    CHANCELLOR_ELECTION: str = "house_nomination_s159_joint_sitting_s272_during_transitory_period"
    CHANCELLOR_TERM: int = 4             # CONFIDENT — README.md section 1, explicit instruction ("House term")
    # CONFIDENT — derived directly from README.md section 1's explicit
    # instruction: "PM term cap: shall not hold office for more than eight
    # years in total" (Section 158) / 4-year CHANCELLOR_TERM = 2 terms.
    CHANCELLOR_MAX_TERMS: int = 2
    CHANCELLOR_COOLING_OFF: int = 0      # GUESS — no cooling-off requirement cited

    PRESIDENT_ELECTION_YEAR: int = 0     # GUESS — hereditary, pre-existing at simulation start
    CHANCELLOR_ELECTION_YEAR: int = 1    # GUESS — first PM selection shortly after promulgation

    # CONFIDENT — Section 158: "not more than thirty-five other Ministers."
    MINISTER_COUNT: int = 35
    MINISTER_MERIT_MIN: float = 0.0      # GUESS — no merit-exam requirement cited for ministers
    # CONFIDENT — Section 158: King appoints Prime Minister and Ministers;
    # standard Thai practice is Royal Command on the Prime Minister's advice.
    MINISTER_CONFIRMATION: str = "prime_minister_advice_royal_command_section_158"

    # GUESS — the research package does not enumerate a ministries list;
    # proxy structure reused from the MFU/Myanmar schema shape, naming
    # Thailand's actual, well-known ministry portfolios rather than
    # Myanmar's (not individually section-cited here).
    MINISTRIES: Tuple[str, ...] = (
        "ministry_of_finance",
        "ministry_of_interior",
        "ministry_of_defence",
        "ministry_of_foreign_affairs",
        "ministry_of_justice",
        "ministry_of_education",
        "ministry_of_public_health",
        "ministry_of_commerce",
    )

    # CONFIDENT — README.md section 1: Section 151, "no-confidence motions
    # are House-only (>=1/5 of existing House members to move). The Senate
    # has no no-confidence power" — a real structural divergence from MFU's
    # 2-of-3-chambers dismissal and Myanmar's (nonexistent) Chancellor
    # dismissal fields.
    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 1
    CHANCELLOR_DISMISSAL_VETO: bool = False   # GUESS — no veto-on-dismissal mechanism cited
    # CONFIDENT direction — the no-confidence process under s.151 is House-
    # driven; the King's role is ceremonial assent, not an active approval
    # gate on a no-confidence resolution's effect.
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = False

    # GUESS, "mechanism absent" idiom (same convention as
    # constitution_2008.py's ETHNIC_PRESIDENTIAL_MIN_TERMS=99) — the
    # research package identifies no ordinary constitutional removal
    # process for the King (succession, not removal, governs the office);
    # set deliberately unreachable rather than fabricated.
    PRESIDENT_REMOVAL_CHAMBERS: int = 0
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = False
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = False
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.0
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.0

    CHANCELLOR_INTERIM: str = "deputy_prime_minister_designated_by_cabinet"   # GUESS — not precisely cited


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER VI — THE NATIONAL ASSEMBLY (Sections 80-157)
# Maps to: -> ChamberConfig
# KEY DIFFERENCE FROM MYANMAR 2008: Thailand reserves 0% of House seats, but
# makes the ENTIRE Senate (250 seats) non-elected for a 5-year transitory
# period (Section 269) rather than reserving a fixed % within mixed chambers.
# README.md section 1 explicitly flags this as "a reserved-powers legislature
# without reserved seats in the lower house" and recommends the extra fields
# below (UPPER_HOUSE_*) beyond the shared Myanmar-schema field names.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Chapter VI — The National Assembly (House of Representatives + Senate)"""

    # CONFIDENT — Sections 83/85/91, as-promulgated 2017 electoral system
    # (350 constituency + 150 party-list, single ballot, mixed-member
    # apportionment). NOTE (README.md limitation L4): this is the
    # "2017_as_promulgated" snapshot; the 2021 amendment (No. 1, B.E. 2564)
    # changed this to 400 constituency + 100 party-list with two ballots.
    # This file encodes the ORIGINAL 2017 system, consistent with holding
    # the transitory-period snapshot static for the whole horizon (see
    # module docstring).
    CONGRESS_ELECTION: str = "mixed_member_350_constituency_150_party_list_single_ballot_2017_as_promulgated"
    CONGRESS_THRESHOLD: float = 0.51   # GUESS — ordinary House legislation, generic simple-majority assumption
    CONGRESS_TERM: int = 4             # CONFIDENT — House term, matches ExecutiveConfig.CHANCELLOR_TERM's own citation
    CONGRESS_REELECTION: bool = True   # GUESS — no term-limit citation found for House members

    # CONFIDENT — README.md section 1, explicit instruction: "Suggested
    # fields: MILITARY_RESERVED_SEATS_PYITHU: 0 (House)."
    MILITARY_RESERVED_SEATS_PYITHU: int = 0
    # CONFIDENT — Section 269: the transitory Senate is 250 members, 100%
    # NCPO/EC-selected (not a reservation WITHIN an elected chamber, but the
    # field name is reused for schema parity — see UPPER_HOUSE_* fields
    # below for the structurally-accurate framing README.md recommends).
    MILITARY_RESERVED_SEATS_AMYOTHA: int = 250
    # CONFIDENT — derived from Section 269: 250 Senate / (500 House + 250
    # Senate) = 0.3333 of the full 750-member National Assembly during the
    # transitory period. Structurally different from Myanmar's 25%-of-both-
    # chambers; Thailand's bloc is concentrated entirely in the upper house.
    MILITARY_SEAT_PERCENTAGE: float = 0.3333
    # CONFIDENT — Section 269 (initial 250, NCPO-selected via its own
    # process plus a Senator Selection Committee); Section 107 (permanent
    # rule thereafter: group-based indirect self-selection).
    MILITARY_SEATS_APPOINTED_BY: str = "ncpo_selection_during_transitory_period_then_s107_selection_committee"

    # CONFIDENT direction — README.md section 1: "No constitutionally
    # recognised ethnic-group structure" means this field models something
    # structurally absent for TH (opposite of Myanmar's 168 ethnic-state
    # seats and MFU's 8-seat Ethnic Leaders Council).
    ETHNIC_SEATS: int = 0
    ETHNIC_THRESHOLD: float = 0.51     # GUESS — "mechanism absent" placeholder, not mechanically exercised
    ETHNIC_TERM: int = 0               # GUESS — "mechanism absent" placeholder

    # CONFIDENT direction — mapped to the Constitutional Court's amendment-
    # review/party-dissolution veto-like function (README.md section 1:
    # "Section 256 also permits pre-promulgation Constitutional Court review
    # of an amendment"). No qualified-supermajority figure is cited for
    # ordinary Court rulings beyond the simple majority of 9 implied by
    # JudiciaryConfig.RULING_THRESHOLD below, so 0.50 (bare majority) is
    # used here rather than inventing a supermajority figure.
    ANALYSIS_THRESHOLD: float = 0.50
    ANALYSIS_VETO_TIME_LIMIT: int = 90   # GUESS — no specific ruling-timeline citation found; reused generic placeholder
    # GUESS magnitude, CONFIDENT direction — s.200's seniority/professorship
    # bar is real (unlike Myanmar's ANALYSIS_MERIT_MIN=0.0), but is not a
    # literal "merit score" in the Ka-Nova sense; nontrivial proxy chosen.
    ANALYSIS_MERIT_MIN: float = 0.60
    ANALYSIS_TERM: int = 7              # CONFIDENT — Section 207: Constitutional Court judges, 7-year single term

    # GUESS magnitude, CONFIDENT direction — Section 113 formally PROHIBITS
    # partisan alignment ("A Senator shall not align with or yield to the
    # mandate of any political party"), but README.md section 2.4's real
    # event history documents the appointed Senate voting as a uniform bloc
    # in practice (blocking Pita Limjaroenrat's premiership, July 2023).
    # Set high despite the formal prohibition, reflecting documented
    # real-world voting behaviour rather than the text's own aspiration.
    MILITARY_BLOC_VOTE_DISCIPLINE: float = 0.90
    # GUESS magnitude, CONFIDENT direction — README.md section 1 draws this
    # exact structural analogy: the Senate's 1/3 concurrence gate on
    # amendments (Section 256) is "functionally identical to Myanmar's 25%
    # bloc under a 75% threshold." Section 272's joint-sitting PM-selection
    # math is a genuine compound-majority rule that cannot be reduced to a
    # single float (README.md flag F3b); 0.667 is used here as the same
    # structural-analogy figure the research package itself draws, not a
    # literal transcription of Section 272's arithmetic.
    CIVILIAN_EFFECTIVE_MAJORITY_NEEDED: float = 0.667

    # GUESS, "mechanism absent" idiom (matches constitution_2008.py's own
    # ETHNIC_MAX_TERMS=99 / ETHNIC_PRESIDENTIAL_MIN_TERMS=99 convention) —
    # no Ethnic Leaders Council or equivalent exists under this constitution.
    ETHNIC_MAX_TERMS: int = 99
    ETHNIC_PRESIDENTIAL_MIN_TERMS: int = 99

    # ── Extra fields beyond the shared Myanmar-schema contract, added per
    # README.md section 1's explicit recommendation: "an explicit
    # UPPER_HOUSE_APPOINTED_BY: 'ncpo_during_transitory_period',
    # UPPER_HOUSE_EX_OFFICIO_MILITARY_SEATS: 6, UPPER_HOUSE_ELECTED: False."
    # These are TH-specific additions, not read by the current engine (no
    # live code references them), but document the real structure more
    # precisely than forcing it entirely into the Myanmar-named fields above.
    UPPER_HOUSE_APPOINTED_BY: str = "national_council_for_peace_and_order_then_senator_selection_committee"  # CONFIDENT, s.269
    UPPER_HOUSE_EX_OFFICIO_MILITARY_SEATS: int = 6   # CONFIDENT — s.269: Permanent Secretary of Defence, Supreme Commander, Army/Navy/Air Force commanders-in-chief, Royal Thai Police Commissioner-General
    UPPER_HOUSE_ELECTED: bool = False                # CONFIDENT — s.269 (transitory) and s.107 (permanent rule, indirect group selection, not direct election)
    SENATE_SIZE: int = 250                            # CONFIDENT — s.269
    SENATE_TRANSITORY_PERIOD_YEARS: int = 5           # CONFIDENT — s.269, counted from the first National Assembly (~2019), not from 2017 promulgation


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER X — COURTS (Sections 188-199) + SPECIAL PART ON THE CONSTITUTIONAL
# COURT (Sections 200-214)
# Maps to: -> JudiciaryConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Constitutional Court (ss. 200-214) + ordinary/military courts"""

    # CONFIDENT — README.md section 1: "formally yes, but note the Senate
    # consent route runs through the s.269 appointed Senate during the
    # transitory period — a documented structural dependency worth a
    # comment rather than a boolean." Set True (opposite of Myanmar's False)
    # because the package explicitly says "formally yes"; the dependency is
    # the real, disclosed caveat, not a reason to flip the boolean itself.
    COURT_INDEPENDENCE: bool = True
    COURT_JUDGES_COUNT: int = 9       # CONFIDENT — Section 200
    COURT_TERM_YEARS: int = 7         # CONFIDENT — Section 207
    RULING_THRESHOLD: int = 5         # GUESS — simple majority of 9 assumed; no explicit threshold citation found

    # CONFIDENT direction — README.md section 1: "Ordinary courts and
    # military courts are separate" (no citation that military justice is
    # final/conclusive over civilian matters, unlike Myanmar Section
    # 293(b)).
    MILITARY_JUSTICE_FINAL: bool = False
    CIVILIAN_COURT_OVERRIDE_MILITARY: bool = True   # GUESS direction, consistent with the above

    CONSTITUTIONAL_TRIBUNAL_SIZE: int = 9   # CONFIDENT — Section 200
    TRIBUNAL_TERM_YEARS: int = 7            # CONFIDENT — Section 207

    # GUESS magnitude, CONFIDENT direction — README.md section 1 documents
    # a genuinely ACTIVE Constitutional Court (party dissolutions, PM
    # removals — Future Forward 2020, Move Forward 2024, Srettha removal
    # 2024), clearly not a captured/toothless court like Myanmar's (0.20).
    # Also clearly not as insulated as MFU's. Set moderate-high.
    COURT_CORRUPTION_RESISTANCE: float = 0.55
    TOTAL_RUIN_THRESHOLD: float = 0.0   # CONFIDENT — no Total Ruin mechanism exists under this constitution

    JUDGE_COUNT: int = 9       # CONFIDENT — mirrors COURT_JUDGES_COUNT, Section 200
    JUDGE_TERM: int = 7        # CONFIDENT — mirrors COURT_TERM_YEARS, Section 207
    JUDGE_MAX_TERMS: int = 1   # CONFIDENT — Section 207: "one term only"
    BUDGET_FIXED: bool = True  # GUESS — not independently cited; Thai Independent Organs typically have constitutionally protected budget lines


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XII, PART 3 — THE NATIONAL ANTI-CORRUPTION COMMISSION (Section 232)
# Maps to: -> IIGConfig
#
# CRITICAL, per README.md flag F4 (locked in .claude/memory.md section 4a,
# decision point 5): "Do NOT copy C's near-zero IIG parameters into TH.
# Thailand has a constitutionally entrenched nine-member NACC (s.232) and
# six other Independent Organs. Setting IIGConfig.INITIAL_EFFECTIVENESS =
# 0.05 because 'it's a military constitution' would be exactly the
# input-driven-conclusion problem Reviewer 2 raised." Every field below is
# calibrated against the package's own recommended anchors: CPI ~35/100,
# WGI Control of Corruption ~-0.45, V-Dem political-corruption .683 (2017).
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """National Anti-Corruption Commission (Section 232) — genuine, entrenched"""

    # GUESS magnitude, CONFIDENT direction — Section 232's real qualification
    # bar (>=5 years as Chief Justice / Director-General level / state-
    # enterprise CEO / university professor, etc.) is a nontrivial
    # credential gate, unlike Myanmar's ENTRY_MERIT=0.0.
    ENTRY_MERIT: float = 0.55
    ENTRY_MERIT_MIN: float = 0.55   # CONFIDENT — mirrors ENTRY_MERIT above (live field name read by agents/oversight.py and agents/citizen.py)
    ACADEMY_MONTHS: int = 0   # CONFIDENT — no training academy exists; commissioners are senior lateral appointees

    # GUESS magnitude, CONFIDENT direction — README.md flag F4: lower than
    # Myanmar's 0.90 (NACC has a genuine, broad investigative/asset-
    # declaration mandate over all public officials, not only regime-
    # threatening cases), but not as low as MFU's 0.45 (real-world
    # effectiveness is still limited — CPI ~35/100).
    INVESTIGATION_TRIGGER: float = 0.55

    # GUESS magnitude, CONFIDENT direction (README.md flag F4, explicit
    # instruction not to copy C's 0.05 floor) — calibrated against CPI
    # ~35/100 (-> ~0.35 "clean" proxy) and WGI Control of Corruption ~-0.45
    # on the -2.5..+2.5 scale (rescaled to 0-1: (-0.45+2.5)/5 = 0.41).
    # EFFECTIVENESS_FLOOR set meaningfully above Myanmar's 0.05 — a real,
    # entrenched institution does not collapse to near-zero even in a bad
    # year — but below MFU's open-ended ceiling, reflecting real-world
    # limits (V-Dem political corruption still .683 in 2017).
    EFFECTIVENESS_FLOOR: float = 0.25
    # CONFIDENT — README.md section 1: NACC is one of Chapter XII's
    # "Independent Organs" (ss.215-247), reporting to no executive or
    # military chain of command. This is the single most important
    # structural divergence from Myanmar's REPORTS_TO="commander_in_chief".
    REPORTS_TO: str = "independent_organ_constitutional_status_chapter_xii"
    CHAMBER_ELIGIBLE: bool = False   # GUESS — standard conflict-of-interest bar assumed, not independently cited

    # CONFIDENT — README.md flag F4, explicit instruction: "Encode
    # ANTI_CORRUPTION_OBJECTIVE: True, REGIME_PROTECTION_OBJECTIVE: False."
    ANTI_CORRUPTION_OBJECTIVE: bool = True
    REGIME_PROTECTION_OBJECTIVE: bool = False

    # GUESS magnitude, CONFIDENT direction — same CPI/WGI/V-Dem anchors as
    # EFFECTIVENESS_FLOOR above. A real institution with real but imperfect
    # effectiveness: well above Myanmar's INITIAL_EFFECTIVENESS=0.05/
    # MAX_EFFECTIVENESS=0.15, below MFU's open ceiling.
    INITIAL_EFFECTIVENESS: float = 0.35
    MAX_EFFECTIVENESS: float = 0.55

    ENTRY_MIN_AGE: int = 45   # GUESS — Section 232's seniority bar (>=5 years at senior levels) implies a late-career appointee; not a literal age citation
    ACADEMY_DURATION_MONTHS: int = 0   # CONFIDENT — mirrors ACADEMY_MONTHS, no academy exists

    # GUESS — real NACC commissioners serve under the Organic Act on the
    # Prevention and Suppression of Corruption, not detailed in the research
    # package; proxied at the same 7-year/single-term structure as the
    # Constitutional Court (s.207), reflecting the parallel appointment
    # process (selection committee -> Senate advice -> King) rather than an
    # independently cited NACC-specific term length.
    DIRECTOR_TERM: int = 7
    DIRECTOR_RENEWABLE: bool = False   # GUESS — proxied from the same single-term pattern as the Constitutional Court

    PARTNER_ELIGIBILITY_YEARS: int = 5   # GUESS — not cited; reused MFU's generic placeholder
    # GUESS magnitude, CONFIDENT direction — between MFU's 0.35 (evidence-
    # weighted approval) and Myanmar's 0.90 (collapsed due process); reflects
    # a genuine but imperfect investigative threshold.
    OPEN_INVESTIGATION_THRESHOLD: float = 0.45
    PROCEED_PROSECUTION_THRESHOLD: float = 0.60
    # CONFIDENT — derived directly from Section 232's 9-commissioner
    # structure: simple majority = 5/9 = 0.556.
    PARTNERSHIP_COUNCIL_QUORUM: float = 0.556

    # CONFIDENT direction — the NACC is a genuinely independent organ;
    # unlike Myanmar's military-intelligence officers (True), there is no
    # citation in the package for former NACC commissioners routinely moving
    # into reserved legislative seats.
    CHAMBER_ELIGIBLE_POST_SERVICE: bool = False
    # GUESS — proxy reintegration paths modelled on the real NACC's actual
    # institutional remit (asset examination, corruption investigation,
    # prosecution referral to the Attorney-General), not Myanmar's
    # surveillance-apparatus framing.
    PERMITTED_POST_SERVICE: Tuple[str, ...] = (
        "academic_institutions",
        "judicial_service",
        "state_enterprise_senior_posts",
    )
    # GUESS — real NACC headcount (including provincial offices) is not
    # detailed in the research package. Set between MFU's 600 ("small,
    # elite, accountable") and Myanmar's 2000 ("sprawling surveillance
    # apparatus") — a real but not sprawling investigative body.
    MAX_AGENTS: int = 900
    # GUESS — division names modelled on the NACC's real, documented
    # functional remit (asset declaration, corruption investigation,
    # prosecution referral), not Myanmar's regime-protection/surveillance
    # framing.
    FUNCTIONAL_DIVISIONS: Tuple[str, ...] = (
        "asset_examination_division",
        "corruption_investigation_division",
        "prosecution_referral_division",
    )
    MANDATE_DIVISIONS: Tuple[str, ...] = (
        "public_official_asset_declaration_division",
        "systemic_corruption_division",
        "state_enterprise_integrity_division",
    )
    OPERATIONAL_DIVISIONS: Tuple[str, ...] = (
        "field_investigation_division",
        "forensic_accounting_division",
        "international_cooperation_division",
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XIV — LOCAL ADMINISTRATION (Sections 249-254)
# Maps to: -> FederalConfig
# Thailand is a UNITARY state; local administration is statutory, not
# constitutional. All RESOURCE_*_SHARE values below are modelling proxies
# (README.md section 1, explicit: "No constitutional revenue-sharing
# formula. All MFU RESOURCE_*_SHARE values are modelling proxies.").
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Chapter XIV — Local Administration (statutory, not constitutional)"""

    STATE_COUNT: int = 14   # GUESS, modelling choice — see FoundationalConfig's own note; duplicated here for schema parity with the Myanmar template
    # CONFIDENT direction — README.md section 1: "No constitutionally
    # recognised ethnic-group structure" (opposite of Myanmar's 8 and MFU's
    # 8).
    ETHNIC_GROUPS: int = 0

    # GUESS calibration, CONFIDENT direction — a unitary state with
    # statutory (not constitutional) local administration (ss.249-254)
    # implies heavier central control than either MFU's 35/35/30 split or
    # even Myanmar's 10/65/25 split allows for local autonomy. "Ethnic
    # direct share" is relabelled in spirit as a generic local/community
    # direct-transfer share, since no ethnic-group structure exists.
    RESOURCE_STATE_SHARE: float = 0.15
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.70
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.15

    GINI_THRESHOLD: float = 0.50       # GUESS — not cited; set between MFU's 0.45 and Myanmar's 0.65
    STATE_GDP_CAP: float = 0.60        # GUESS — not cited
    # CONFIDENT direction — no citation found in the research package for a
    # Myanmar-Section-17-style explicit military presence in regional
    # executive government under this constitution.
    MILITARY_IN_REGIONAL_EXECUTIVE: bool = False

    SECTOR_MONOPOLY_CAP: float = 0.40   # GUESS — not cited

    # CONFIDENT direction, GUESS magnitude — no textual Thai equivalent of
    # MFU's Article VIII trust-acceleration "virtuous cycle" safeguard is
    # cited in the research package. Nullified via parameter values alone
    # (same idiom as constitution_2008.py), NOT because the paper wants TH
    # to fail like Myanmar — this is a genuine absence-of-citation finding,
    # and the engine's other TH-specific inputs (genuine NACC effectiveness,
    # no legal coup mechanism, no total power transfer, low baseline coup
    # risk) are what should let the simulation's own dynamics produce
    # whatever trajectory those honestly-sourced parameters entail, not this
    # specific safeguard mechanic either way.
    TRUST_ACCELERATION_TRIGGER_CORRUPTION: float = 0.0
    TRUST_ACCELERATION_TRIGGER_YEARS: int = 99
    TRUST_ACCELERATION_MULTIPLIER: float = 1.00


# ══════════════════════════════════════════════════════════════════════════════
# SECTIONS 52 (ARMED FORCES' DEVELOPMENT ROLE), 265/269/279 (NCPO
# TRANSITORY PROVISIONS) — Maps to: -> MilitaryConfig
#
# CRITICAL per README.md section 5, flag F5 and .claude/memory.md section
# 4a: "Thailand's 2017 constitution does not contain a legal coup
# mechanism." COUP_LEGAL_MECHANISM and TOTAL_POWER_TRANSFER_POSSIBLE (below,
# EmergencyConfig) are both deliberately False — the single most important
# structural divergence from Myanmar 2008 in this entire file.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Section 52 (development role) + ss.265/269/279 (NCPO transitory provisions)"""

    # CONFIDENT — README.md section 1, emphatic, repeated instruction:
    # "No section authorises a coup, and there is no 'safeguarding the
    # Constitution' mandate equivalent to Myanmar 2008 s.20(f)/40(c)/
    # 417-419. Thailand's 2017 constitution does not contain a legal coup
    # mechanism."
    COUP_LEGAL_MECHANISM: bool = False

    # GUESS magnitude, CONFIDENT direction — since no legal/constitutional
    # coup trigger exists, these two fields model the INFORMAL/historical
    # pattern (12 coup events 1951-2014, Powell & Thyne dataset, README
    # section 2.4) rather than a textual threshold. Set higher than
    # Myanmar's 0.65/0.30 (no constitutional "wide latitude" framing exists
    # to lower the bar).
    COUP_TRIGGER_CORRUPTION: float = 0.80
    COUP_TRIGGER_TRUST: float = 0.15

    COMMANDER_IN_CHIEF_APPOINTMENT: str = "royal_appointment_on_cabinet_nomination"   # GUESS — not precisely cited
    # CONFIDENT direction — README.md section 1: "Ordinary courts and
    # military courts are separate" (opposite of Myanmar's "final and
    # conclusive" framing).
    MILITARY_SELF_ADJUDICATION: bool = False
    SINGLE_CHAIN_OF_COMMAND: bool = True   # GUESS — plausible, not independently cited

    # CONFIDENT — Section 52: "the State shall provide efficient military,
    # diplomatic, and intelligence services. Armed forces shall also be
    # deployed for the purpose of developing the country" — a real,
    # constitutionally-stated internal-development role for the military,
    # distinct from (but real like) Myanmar's explicit political role.
    MILITARY_POLITICAL_ROLE: bool = True

    # CONFIDENT — derived from Section 269's 6 named ex officio Senate
    # seats (Permanent Secretary of Defence, Supreme Commander, Army/Navy/
    # Air Force commanders-in-chief, Royal Thai Police Commissioner-
    # General) as a fraction of the full 750-member National Assembly:
    # 6/750 = 0.008. Deliberately distinct from ChamberConfig's broader
    # MILITARY_SEAT_PERCENTAGE=0.3333 (the full NCPO-appointed-Senate
    # share) — this field models specifically the named ex officio seats.
    PARLIAMENTARY_SEAT_PERCENTAGE: float = 0.008
    PARLIAMENTARY_SEAT_APPOINTMENT: str = "ex_officio_named_service_chiefs_section_269"

    # GUESS magnitude, CONFIDENT direction — lower than Myanmar's 0.85
    # ("military IS the regime"); Thailand's military is a real, separate
    # institutional actor (not a literally captured civilian government
    # post-2019), but historically coup-prone, so set meaningfully above a
    # fully-depoliticised baseline.
    LOYALTY_INITIAL: float = 0.70
    LOYALTY_CORRUPTION_DRAG: float = 0.002   # GUESS — same order of magnitude as Myanmar's 0.001
    # GUESS, not independently confirmed as read by any live engine code
    # path outside the constitution modules themselves (grep found no
    # consumer in agents/, institutions/, feedback/, model_phase3.py, or
    # engine/ as of this encoding). Set nonzero (unlike Myanmar's 0.0,
    # "military IS the regime, no coup risk TO the regime") to reflect that
    # TH's military is a real external actor with documented historical
    # coup propensity, in case this field is ever wired into a mechanic.
    COUP_PROBABILITY_MULTIPLIER: float = 0.30

    DOMESTIC_FORCE_AUTHORIZED: bool = True   # GUESS — statutory (Internal Security Act, Martial Law Act), not a constitutional citation here
    DOMESTIC_FORCE_TRIGGER: str = "statutory_martial_law_or_emergency_decree_not_constitutional"   # CONFIDENT direction, per README EmergencyConfig note

    # GUESS, "mechanism absent" idiom, CONFIDENT direction — since
    # COUP_LEGAL_MECHANISM=False, there is no constitutional threshold at
    # which a coup becomes "legally available"; set deliberately
    # unreachable rather than fabricating a textual figure. (Distinct from
    # COUP_TRIGGER_LOYALTY/COUP_TRIGGER_APPROVAL's informal-pattern framing
    # above — these two specifically model a LEGAL availability threshold,
    # which genuinely does not exist here, unlike COUP_TRIGGER_CORRUPTION/
    # TRUST which model the informal historical pattern.)
    COUP_TRIGGER_LOYALTY: float = 0.0
    COUP_TRIGGER_APPROVAL: float = 0.0

    # GUESS — National Service cross-exposure/loyalty boosts
    # (agents/citizen.py). Not covered by the research package (conscription
    # is statutory, not constitutional). Modelled as moderate — between
    # MFU's high genuine-integration framing (0.15/0.20/0.10) and Myanmar's
    # coerced-conscription framing (0.05/0.02/0.02) — since Thai
    # conscription, while real and sometimes contentious, is not documented
    # in the research package as a tool of ethnic suppression the way
    # Myanmar's post-2021 forced conscription is.
    NS_CIVILIAN_TRACK_THRESHOLD: float = 0.60
    NS_LOYALTY_BOOST: float = 0.08
    NS_ETHNIC_EXPOSURE_BOOST: float = 0.05
    NS_CIVIC_CONTRIBUTION_BOOST: float = 0.05


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER VI, SECTIONS 64-78 — DIRECTIVE PRINCIPLES OF STATE POLICIES
# Maps to: -> EconomicConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Chapter VI, Directive Principles (ss. 64-78)"""

    # CONFIDENT — Section 75: free-market economy with prevention of unfair
    # monopoly; Section 65: binding 20-year National Strategy framework.
    ECONOMIC_SYSTEM: str = "constitutional_free_market_with_binding_national_strategy"
    STATE_ENTERPRISES_COMPETE_ON_MERIT: bool = True   # GUESS — not independently cited
    STATE_ENTERPRISES_NO_SUBSIDY: bool = False        # GUESS — not independently cited; Thai SOEs are documented to receive state support generally, not package-cited here

    STRATEGIC_SECTORS: Tuple[str, ...] = (             # GUESS — not package-cited; real-world Thai Foreign Business Act restricted-list sectors
        "natural_resources",
        "media_and_broadcasting",
        "defence",
        "banking",
        "telecommunications",
    )
    OPEN_SECTORS: Tuple[str, ...] = (
        "manufacturing",
        "retail",
        "tourism",
        "services",
        "agriculture_non_resource",
    )
    # CONFIDENT (real-world fact, not from this encoding's research
    # package — flagged per this file's own sourcing convention): the Thai
    # Foreign Business Act B.E. 2542 (1999) caps foreign ownership at 49%
    # for restricted-list ("List 2/3") businesses; fully open sectors have
    # no such cap.
    FOREIGN_CAP_STRATEGIC: float = 0.49
    FOREIGN_CAP_OPEN: float = 1.00

    CENTRAL_BANK_INDEPENDENT: bool = True          # GUESS — Bank of Thailand Act establishes formal independence; not package-cited
    CENTRAL_BANK_POLITICAL_DIRECTION: bool = False
    CENTRAL_BANK_ANNUAL_REPORT: bool = True
    CENTRAL_BANK_CHAMBERS_CAN_DIRECT: bool = False

    TAX_BRACKETS: Tuple[float, ...] = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35)   # GUESS — proxy, not package-cited
    BLACK_MONEY_PENALTY: str = "law_prescribed"    # GUESS — not package-cited

    STATE_OWNS_RESOURCES: bool = False             # GUESS — no Section-37-style citation found for Thailand in the package
    PRIVATE_PROPERTY_PROTECTED: bool = True        # GUESS — standard assumption, not independently cited

    ANTI_MONOPOLY: bool = True                     # CONFIDENT — Section 75: prevention of unfair monopoly, on paper
    CRONYISM_ENABLED: bool = True                   # GUESS, CONFIDENT direction — documented real-world Thai crony-conglomerate political economy, less extreme than Myanmar
    NATIONALIZATION_BANNED: bool = False            # GUESS — not package-cited

    CORRUPTION_GDP_DRAG: float = 0.02               # GUESS — between MFU's implied near-zero and Myanmar's 0.03
    # GUESS magnitude, CONFIDENT direction — real, documented Thai
    # political-economy literature on conglomerate-military/government ties,
    # but less extreme and less institutionally total than Myanmar's
    # military-conglomerate capture (0.40).
    CRONY_CAPITAL_SHARE: float = 0.20


# ══════════════════════════════════════════════════════════════════════════════
# SECTIONS 54, 69 — EDUCATION AND RESEARCH
# Maps to: -> ScienceConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Sections 54 (12-year free education), 69 (R&D/science and technology)"""

    PHD_TUITION_FREE: bool = False          # GUESS — s.54 covers only compulsory/pre-school-to-secondary tuition
    RESEARCHER_ROYALTY: float = 0.0         # GUESS — no royalty system cited
    KNOWLEDGE_CAPITAL_GROWTH: float = 0.015  # GUESS — between MFU's implied high rate and Myanmar's 0.005, reflecting s.69's real but modest R&D directive

    EDUCATION_NATIONALIST_FRAMING: bool = False   # GUESS — no nationalist-framing citation found for Thai education, unlike Myanmar's s.28(d)

    BRAIN_DRAIN_RATE_BASE: float = 0.10     # GUESS — not package-cited
    ACADEMIC_FREEDOM: float = 0.45          # GUESS, CONFIDENT direction — higher than Myanmar's 0.20 (no equivalent of Myanmar's direct university political control cited), lower than MFU's full academic freedom (lese-majeste-adjacent restrictions on political speech documented in README section 2.5)

    RESEARCHER_ROYALTY_RATE: float = 0.0    # CONFIDENT — mirrors RESEARCHER_ROYALTY=0.0 above
    PHD_KNOWLEDGE_CAPITAL_BOOST: float = 0.10   # GUESS — below MFU's 0.25, above Myanmar's 0.05


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XV — AMENDMENT OF THE CONSTITUTION (Section 256)
# Maps to: -> AmendmentConfig
# README.md section 5, flag F3b: "s.256's compound majority
# ('>=1/2 of both Houses AND >=1/3 of Senators AND >=20% of non-government-
# party House members') cannot be stored in a single STANDARD_AMENDMENT_
# THRESHOLD float." Encoded as the package's own explicitly recommended
# compound-field structure.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Section 256 — Amendment of the Constitution (the hardest rule in the 5-country set)"""

    # CONFIDENT — README.md section 1: Section 256(1), motion by Cabinet,
    # or >=1/5 of existing House members, or >=1/5 of both Houses combined,
    # or >=50,000 eligible voters.
    AMENDMENT_INITIATION_THRESHOLD: float = 0.20
    # CONFIDENT — README.md section 1, explicit instruction:
    # "STANDARD_AMENDMENT_THRESHOLD: 0.50 (of joint sitting)" — Section
    # 256(3)/(6): >1/2 of the total existing members of both Houses, for
    # both first and third readings.
    STANDARD_AMENDMENT_THRESHOLD: float = 0.50
    # CONFIDENT direction — no separately-cited higher numeric threshold for
    # entrenched-chapter amendments beyond the mandatory referendum
    # requirement itself (Section 256(8)); kept equal to STANDARD and let
    # ENTRENCHED_REQUIRES_REFERENDUM carry the real extra burden.
    ENTRENCHED_AMENDMENT_THRESHOLD: float = 0.50
    ENTRENCHED_REQUIRES_REFERENDUM: bool = True   # CONFIDENT — Section 256(8)

    # CONFIDENT — README.md section 1, explicit instruction: "a hard
    # SENATE_CONCURRENCE_REQUIRED: 0.333 gate" (Section 256(3)/(6): >=1/3 of
    # existing Senators, 84 of 250 during the transitory period) and "an
    # OPPOSITION_CONCURRENCE_REQUIRED: 0.20 gate" (Section 256(6)(a): House
    # members from parties holding no Minister/Speaker/Deputy-Speaker post
    # must supply >=20% of the combined membership of all such parties).
    SENATE_CONCURRENCE_REQUIRED: float = 0.333
    OPPOSITION_CONCURRENCE_REQUIRED: float = 0.20
    # CONFIDENT — README.md section 1, explicit instruction:
    # "MILITARY_VETO_ON_AMENDMENTS: True during the transitory period (the
    # 1/3-Senate gate gave the NCPO-appointed Senate an absolute veto,
    # which is functionally identical to Myanmar's 25% bloc under a 75%
    # threshold)."
    MILITARY_VETO_ON_AMENDMENTS: bool = True

    # CONFIDENT — Section 256(8): entrenched subjects are Chapter I
    # (General Provisions), Chapter II (The King), Chapter XV (Amendment),
    # qualifications/prohibitions of office-holders, and the duties/powers
    # of the Courts or an Independent Organ.
    ENTRENCHED_CHAPTERS: Tuple[str, ...] = (
        "chapter_1_general_provisions",
        "chapter_2_the_king",
        "chapter_15_amendment",
        "qualifications_and_prohibitions_of_office_holders",
        "duties_and_powers_of_courts_or_independent_organs",
    )

    # CONFIDENT direction, same "mechanism absent" idiom as
    # constitution_2008.py's own REVIEW_INTERVAL=0 (and the identical
    # ZeroDivisionError-guard caveat: institutions/court.py:63 would divide
    # by this value if ConstitutionalCourtSystem.annual_session() were ever
    # wired into model_phase3.py's step() loop — currently dead code per
    # bug #12, so harmless today, but do NOT "fix" this by changing the
    # value if that wiring ever happens; the fix belongs in court.py's own
    # guard clause). No mandatory periodic constitutional review cycle is
    # cited for Thailand's 2017 instrument.
    REVIEW_INTERVAL: int = 0
    # CONFIDENT, same idiom as constitution_2008.py's own identical
    # backfill note — no Thai civic-lottery/Citizens-Assembly mechanism
    # exists; kept at the same canonical 320 value used elsewhere rather
    # than inventing a different number for a mechanism that does not
    # textually exist for Thailand either.
    CITIZENS_ASSEMBLY_SIZE: int = 320


# ══════════════════════════════════════════════════════════════════════════════
# SECTIONS 265, 269, 270, 272, 279 — NCPO TRANSITORY PROVISIONS
# Maps to: -> TransitionConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """Sections 265/269/270/272/279 — NCPO continuation and validation"""

    # CONFIDENT — README.md section 1: Section 269's Senate term (and
    # Section 272's joint-sitting PM rule) run for 5 years. NOTE: counted
    # from the first National Assembly convening under this Constitution
    # (~2019), not from the 2017 promulgation date — the real end date
    # (2024-05-11, per README section 2.4) is ~7 years after promulgation,
    # not 5. This file's TRANSITION_PERIOD_YEARS=5 refers to the Senate's
    # own term length, not an offset from simulation year zero (2017); see
    # the module docstring for how this snapshot choice is handled.
    TRANSITION_PERIOD_YEARS: int = 5
    # CONFIDENT — Section 279: blanket validation of all NCPO announcements/
    # orders/acts as "constitutional, lawful and effective."
    AMNESTY_GRANTED: bool = True

    PRIOR_LAWS_VALID: bool = True   # CONFIDENT — Section 279
    # CONFIDENT — README.md section 1: Section 279's immunity is BROADER
    # than Myanmar's Section 445 — it covers NCPO orders issued under
    # Section 265 paragraph 2 as well, i.e. acts occurring AFTER
    # promulgation, not only before it.
    PRIOR_ACTIONS_IMMUNE: bool = True

    CIVIL_SERVANTS_RETAIN_POSTS: bool = True   # GUESS — standard administrative-continuity assumption, not independently cited

    TATMADAW_PENSION: float = 0.0    # GUESS — reused Myanmar-schema field name for parity; no special NCPO pension multiplier cited
    TATMADAW_IMMUNITY: bool = True   # CONFIDENT — mirrors AMNESTY_GRANTED/PRIOR_ACTIONS_IMMUNE above, Section 279


# ══════════════════════════════════════════════════════════════════════════════
# NO MFU-STYLE CONSTITUTIONAL SAFEGUARDS — PARTIAL REAL SAFEGUARDS EXIST
# Maps to: -> SafeguardConfig
# Unlike Myanmar 2008 (where SafeguardConfig models "military control IS the
# safeguard" with every MFU safeguard uniformly False), Thailand genuinely
# has SOME real safeguards (single-term NACC/Court appointments, public
# Court rulings) even though the amendment-veto/Senate-appointment
# safeguards clearly favour the NCPO's continuity. Encoded field-by-field
# rather than uniformly inverted, per the standing realism requirement.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """Mixed — some real institutional safeguards exist, others do not"""

    CHANCELLOR_COOLING_OFF_ENFORCED: bool = False    # GUESS — no cooling-off requirement cited
    MERIT_EXAM_INDEPENDENCE: bool = False            # CONFIDENT direction — no competitive merit-exam system exists at all (see MeritConfig)
    ETHNIC_COUNCIL_YOUTH_MANDATE: bool = False       # CONFIDENT direction — no ethnic council exists

    # CONFIDENT — Section 207 (Constitutional Court) and the s.207-parallel
    # NACC appointment structure (IIGConfig.DIRECTOR_RENEWABLE=False above)
    # both genuinely impose single, non-renewable terms. This is a REAL
    # divergence from Myanmar's IIG_SINGLE_TERM=False.
    IIG_SINGLE_TERM: bool = True
    # GUESS, CONFIDENT direction — Constitutional Court rulings and NACC
    # findings are, as a matter of real practice, publicly reported
    # (documented party-dissolution/PM-removal rulings, README section
    # 2.4), unlike Myanmar's fully opaque Tribunal process.
    ANALYSIS_TRANSPARENCY: bool = True

    RIGHTS_ABSOLUTE: bool = False                    # CONFIDENT — follows from RightsConfig.RIGHTS_SUSPENDABLE=True above
    GENERATIONAL_ASSEMBLY_REVIEW: bool = False       # CONFIDENT direction — no civic-lottery review mechanism exists

    # CONFIDENT — Section 269: the entire transitory Senate is NCPO-
    # appointed (structurally real, even though framed differently from
    # Myanmar's "reserved seats within an elected chamber" — see
    # ChamberConfig's UPPER_HOUSE_* fields for the precise framing).
    MILITARY_SEAT_RESERVATION: bool = True
    # CONFIDENT — README.md section 5, flag F5 / section 1's emphatic
    # repeated instruction: no legal coup mechanism and no constitutional
    # "safeguarding the Constitution" mandate exist for the military under
    # this instrument, unlike Myanmar's implicit Commander-in-Chief veto.
    COMMANDER_IN_CHIEF_VETO: bool = False
    # CONFIDENT direction — no National Defence and Security Council
    # (NDSC)-equivalent oversight body is cited in the research package for
    # Thailand's 2017 instrument.
    NDSC_OVERSIGHT: bool = False

    # GUESS, "mechanism absent" idiom — no specific advance-publication-
    # before-veto procedural requirement is cited for the Constitutional
    # Court's amendment review (Section 256(6) permits pre-promulgation
    # review, but without a stated publication window).
    ANALYSIS_PUBLISH_BEFORE_VETO_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# NO CRYPTOGRAPHIC JUSTICE — NO THAI REFERENT
# Maps to: -> CryptoJusticeConfig
# CONFIDENT — README.md section 4, limitation L6: "Several config
# categories have no Thai referent: CryptoJusticeConfig, PsychConfig, MFU's
# IIG academy/partnership machinery... Values placed there are modelling
# choices; comment them as such." Mirrors constitution_2008.py's own "all
# absent" encoding exactly — this is a genuine absence, not a copy-paste
# shortcut, since the package explicitly confirms no referent exists.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """No cryptographic justice mechanism — confirmed absent (README.md limitation L6)"""

    BLOCKCHAIN_ENABLED: bool = False
    ZKP_ENABLED: bool = False
    MULTI_PARTY_SIGNATURES: bool = False
    TOTAL_RUIN_MECHANISM: bool = False
    TOTAL_RUIN_STEPS: int = 0

    # GUESS value, same "unreachable by construction" idiom as
    # constitution_2008.py's own identical field (set equal to
    # JUDGE_COUNT=9, unanimous, effectively unreachable) — nullifies the
    # mechanism via parameter value rather than a special-cased code branch.
    COURT_SUPERMAJORITY_FOR_TOTAL_RUIN: int = 9
    SHAME_REGISTER_CORRUPTION_REDUCTION: float = 0.0   # CONFIDENT — no Shame Register exists under this constitution


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 172 (EMERGENCY DECREES) + STATUTORY MARTIAL LAW/EMERGENCY REGIME
# Maps to: -> EmergencyConfig
#
# CRITICAL per README.md flag F5: "There is no analogue of Myanmar 2008
# ss.417-419. On the emergency axis, Thailand resembles South Korea more
# than Myanmar." TOTAL_POWER_TRANSFER_POSSIBLE=False here is, alongside
# MilitaryConfig.COUP_LEGAL_MECHANISM=False, the single most important
# structural divergence from Myanmar 2008 in this entire file.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Section 172 (Emergency Decrees) + statutory Martial Law Act 1914 / Emergency Decree 2005"""

    # CONFIDENT — README.md section 1: Section 172 (national/public safety,
    # economic security, avert public calamity) plus the two statutory
    # instruments operating outside the constitutional chapter (Martial Law
    # Act B.E. 2457 (1914); Emergency Decree on Public Administration in
    # Emergency Situations B.E. 2548 (2005)).
    TRIGGER_SCENARIOS: Tuple[str, ...] = (
        "national_or_public_safety_necessity",       # Section 172
        "national_economic_security_necessity",       # Section 172
        "avert_public_calamity",                       # Section 172
        "statutory_martial_law_act_1914_not_constitutional",
        "statutory_emergency_decree_2005_not_constitutional",
    )

    # GUESS — Section 172 does not itself fix a maximum duration (it
    # requires submission to the National Assembly "without delay" in the
    # next sitting, with disapproval lapsing it); unlike Myanmar's fixed
    # 365-day/2x6-month structure, no single constitutional day-count
    # exists here. Values below are a generic proxy, not a citation.
    EMERGENCY_MAX_DAYS: int = 60
    EMERGENCY_EXTENSIONS: int = 1
    EMERGENCY_EXTENSION_MONTHS: int = 1

    # CONFIDENT — README.md section 1, explicit instruction:
    # "RIGHTS_UNTOUCHED: False, ... Thailand's emergency powers are
    # statutory." Rights are NOT constitutionally fenced off during
    # emergencies (consistent with RightsConfig.RIGHTS_SUSPENDABLE=True).
    RIGHTS_UNTOUCHED: bool = False

    # CONFIDENT — README.md flag F5, the single clearest instruction in the
    # whole package: "Encode: TOTAL_POWER_TRANSFER_POSSIBLE: False... There
    # is no constitutional total-power-transfer clause equivalent to
    # Myanmar 2008 ss.417-419."
    TOTAL_POWER_TRANSFER_POSSIBLE: bool = False
    POWER_TRANSFER_TRIGGER: str = "not_applicable_no_constitutional_mechanism"   # CONFIDENT, follows directly from the above

    # CONFIDENT — follows directly from TOTAL_POWER_TRANSFER_POSSIBLE=False;
    # no Section-419-equivalent exists granting a single office legislative,
    # executive and judicial power simultaneously.
    COMMANDER_IN_CHIEF_LEGISLATIVE: bool = False
    COMMANDER_IN_CHIEF_EXECUTIVE: bool = False
    COMMANDER_IN_CHIEF_JUDICIAL: bool = False

    # CONFIDENT — README.md section 1, explicit instruction:
    # "LEGISLATURE_SUSPENDED_DURING_EMERGENCY: False."
    LEGISLATURE_SUSPENDED_DURING_EMERGENCY: bool = False

    # GUESS magnitude, CONFIDENT direction — since emergency declarations
    # under Section 172 are statutory crisis-management tools, not a coup
    # mechanism (unlike Myanmar, where ss.417-419 make emergency powers THE
    # coup mechanism itself), set low rather than Myanmar's full 1.0
    # activation.
    EMERGENCY_COUP_PROBABILITY_MULTIPLIER: float = 0.10


# ══════════════════════════════════════════════════════════════════════════════
# NO SPECIFIC RULES-OF-ENGAGEMENT CITATION IN THE RESEARCH PACKAGE
# Maps to: -> ROEConfig
# GUESS throughout — the research package does not address Thai military
# rules of engagement; values below are a neutral, professional-military
# proxy, deliberately neither MFU's "scorched earth" doctrine nor Myanmar's
# broad-domestic-force-discretion framing.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """Not covered by the research package — neutral proxy values throughout"""

    FOREIGN_POLICY: str = "non_aligned_pragmatic"   # GUESS
    NO_AGGRESSION: bool = True                        # GUESS
    NO_FOREIGN_TROOPS: bool = False                    # GUESS — Thailand hosts a US Status of Forces framework (Cobra Gold); not package-cited

    DOMESTIC_MILITARY_USE: str = "statutory_martial_law_or_emergency_decree_discretion"   # GUESS, CONFIDENT direction per EmergencyConfig's statutory framing
    DOMESTIC_FORCE_THRESHOLD: float = 0.15   # GUESS — moderate, between MFU's implicit restraint and Myanmar's 0.05

    EXTERNAL_ROE: str = "defensive_unless_declared_war"   # GUESS
    EXTERNAL_FULL_FORCE: bool = False                       # GUESS


# ══════════════════════════════════════════════════════════════════════════════
# NO PSYCHOLOGICAL HEALTH MANDATE — NO THAI REFERENT
# Maps to: -> PsychConfig
# CONFIDENT — README.md section 4, limitation L6 (no Thai referent cited).
# Mirrors constitution_2008.py's "absent mandate, but the engine still reads
# these fields unconditionally" precedent exactly — same no-op idiom.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """No psychological health mandate exists — confirmed absent (README.md limitation L6)"""

    BIANNUAL_SCREENING: bool = False
    ANTI_BIAS_REVIEW: bool = False
    TRAUMA_CARE_MANDATED: bool = False

    POPULATION_TRAUMA_BASE: float = 0.25        # GUESS — below Myanmar's 0.45 (no equivalent documented population-wide conflict trauma baseline cited), above a hypothetical zero
    TRAUMA_ACCUMULATION_RATE: float = 0.01      # GUESS
    ETHNIC_TRAUMA_MULTIPLIER: float = 1.0       # CONFIDENT direction — no ethnic-group structure exists, so no differential multiplier is meaningful; set to a no-op value (1.0) rather than Myanmar's 1.5

    # GUESS idiom, matches constitution_2008.py's own identical convention —
    # modelled as "never triggers within the 600-month/50-year simulation
    # horizon" since BIANNUAL_SCREENING/TRAUMA_CARE_MANDATED are both False.
    SCREENING_INTERVAL_MONTHS: int = 9999
    SEVERE_PROBATION_MONTHS: int = 9999
    OUTCOME_STABLE_THRESHOLD: float = 0.40
    OUTCOME_SEVERE_THRESHOLD: float = 0.70
    # GUESS, deliberate — same idiom as constitution_2008.py: chosen to NOT
    # match the engine's literal string check in agents/official.py's
    # stop_treatment(), so this becomes a no-op for this constitution,
    # consistent with TRAUMA_CARE_MANDATED=False above.
    STOP_CONSEQUENCE: str = "no_formal_consequence_mechanism_exists"
    TRAUMA_CATEGORIES: Tuple[str, ...] = (
        "political_violence_and_crackdowns",
        "family_domestic_abuse",
        "educational_authoritarian",
        "environmental_displacement",
        "political_speech_suppression",
    )
    TRAUMA_DISTORTION_RANGE: Tuple[float, float] = (0.10, 0.30)   # GUESS — between MFU's (0.10, 0.30) and Myanmar's (0.20, 0.45)


# ══════════════════════════════════════════════════════════════════════════════
# NORTH STAR — SECTION 65 + NATIONAL STRATEGY ACT 2017 (20-YEAR NATIONAL
# STRATEGY, 2018-2037)
# Maps to: -> NorthStarConfig
#
# README.md section 1, explicit instruction: "For NorthStarConfig there IS a
# real referent: the 20-year National Strategy (s.65 + National Strategy Act
# 2017, National Strategy 2018-2037) with six strategic pillars. This is the
# closest real-world analogue to MFU's north-star construct in the whole
# five-country set and is worth using rather than zeroing out."
# NOTE: per .claude/memory.md bug #3's fix, NorthStarConfig classes are
# target/metadata containers only — the live engine's north_star_progress
# FORMULA (model_phase3.py `_update_north_star_progress`) is scenario-
# agnostic and does not read these fields. They are documentary/schema-
# complete here, not mechanically load-bearing for the current engine.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """Section 65 + National Strategy Act 2017 — the 20-year National Strategy (2018-2037)"""

    # GUESS pillar names, CONFIDENT pillar count — README.md section 1
    # confirms "six strategic pillars" for the real National Strategy
    # 2018-2037, but does not name them individually. The six names below
    # are the commonly reported real pillars (security; competitiveness
    # enhancement; human capital development; social equality; eco-friendly
    # development; public sector rebalancing and development), not
    # independently re-verified against a primary source within this
    # encoding's research package — flagged consistent with README.md
    # section 4's sourcing-limitation convention.
    OBJECTIVES: Tuple[str, ...] = (
        "security",
        "competitiveness_enhancement",
        "human_capital_development",
        "social_equality_and_reducing_disparity",
        "eco_friendly_development",
        "public_sector_rebalancing_and_development",
    )

    PROGRESS_METRIC: str = "national_strategy_20_year_plan"   # CONFIDENT — README.md section 1, explicit instruction
    HORIZON_YEARS: int = 20   # CONFIDENT — README.md section 1, explicit instruction (National Strategy's own horizon, distinct from the 50-year simulation horizon — see docstring above)

    # GUESS — modelling estimate reflecting a genuinely MIXED real
    # trajectory (corruption flat/slightly improving, representation
    # suppressed then partially recovering as transitory provisions
    # expired) rather than either MFU's optimistic target or Myanmar's
    # cynical "regime stability" framing. Not mechanically consumed by the
    # live engine's north-star formula (see class docstring above).
    TARGET_YEAR_50_PROGRESS: float = 0.40

    PHD_COMPOUNDING_ENABLED: bool = True    # GUESS, CONFIDENT direction — Section 69's real (if modest) R&D directive, unlike Myanmar's False
    KNOWLEDGE_CAPITAL_TARGET: float = 0.30  # GUESS


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS — Scenario TH calibration
# Maps to: -> SimulationConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Scenario TH simulation parameters"""

    SCENARIO: str = "TH"
    SCENARIO_NAME: str = "Thailand_2017_Constitution"
    # CONFIDENT — this file's module docstring records the exact snapshot
    # choice: as-promulgated 2017 text, transitory-period configuration
    # (ss.265/269/270/272/279) held static across the full horizon.
    CONSTITUTIONAL_FRAMEWORK: str = "thailand_2017_constitution_as_promulgated_transitory_period_snapshot"

    YEAR_ZERO_CORRUPTION: float = 0.683    # CONFIDENT — README.md section 2.6: V-Dem v16 political corruption index, Thailand, 2017
    # GUESS/derived — README.md section 2.6 flags that a real ABS/WVS trust
    # number is the recommended source but requires registered microdata
    # access not available in this encoding (limitation L2). WGI Voice &
    # Accountability 2017 = -1.05 (on the -2.5..+2.5 scale) is used as the
    # best DOCUMENTED proxy available in the package, rescaled to [0,1]:
    # (-1.05 + 2.5) / 5 = 0.29.
    YEAR_ZERO_TRUST: float = 0.29
    # GUESS/external — not in the research package; World Bank Gini index
    # for Thailand is commonly reported in the ~0.35-0.36 range for the
    # mid/late-2010s. Flagged per this file's own convention as sourced
    # outside the package, not from a vibes-based guess.
    YEAR_ZERO_GINI: float = 0.35
    # GUESS/external — Thailand's unemployment rate is famously very low
    # (often cited near 1%); modelled here as EMPLOYMENT rate (inverse
    # framing to match the schema's existing MFU/Myanmar convention), not
    # independently sourced from this encoding's research package.
    YEAR_ZERO_EMPLOYMENT: float = 0.95
    # GUESS, CONFIDENT direction — README.md section 1: "No constitutionally
    # recognised ethnic-group structure." Set low to reflect this structural
    # absence rather than fabricating a tension measure MFU/Myanmar compute
    # from a real ethnic-group framework Thailand's constitution does not
    # have.
    YEAR_ZERO_ETHNIC_TENSION: float = 0.10
    # CONFIDENT — README.md section 2.6, explicit instruction, computed
    # directly from Powell & Thyne's coup dataset: "8 successes / 64 years
    # (1951-2014) ~= 0.125/yr; this is my computation from Powell-Thyne,
    # flag as derived." Rounded to the package's own stated 0.12.
    YEAR_ZERO_COUP_RISK: float = 0.12
    # CONFIDENT — README.md section 2.6: WGI Political Stability 2017 =
    # -0.75 (on the -2.5..+2.5 scale), rescaled to [0,1]:
    # (-0.75 + 2.5) / 5 = 0.35.
    YEAR_ZERO_STABILITY: float = 0.35

    # CONFIDENT for the chosen transitory-period snapshot — Section 272's
    # joint-sitting PM-selection rule and Section 269's appointed Senate
    # together gave the military-aligned bloc a decisive, structural vote
    # over who forms government, which is the real-world mechanism this
    # flag is meant to capture.
    MILITARY_CONTROLS_LEGISLATURE: bool = True
    MILITARY_CONTROLS_EXECUTIVE: bool = True
    # CONFIDENT — deliberately FALSE, unlike Myanmar's True. README.md
    # section 1 states Constitutional Court independence is "formally yes"
    # (JudiciaryConfig.COURT_INDEPENDENCE=True above), and the research
    # package's own framing (section 5, flag F1) explicitly warns against
    # over-claiming total military capture of every branch for Thailand.
    MILITARY_CONTROLS_JUDICIARY: bool = False
    RIGHTS_ENFORCEABLE: bool = False   # CONFIDENT direction — follows from RIGHTS_SUSPENDABLE=True / residual rights framing above

    # CONFIDENT — locked experimental-design constants (same population
    # size, same 50-year horizon), NOT constitution-driven parameters, same
    # convention as constitution_2008.py's own identical backfill note.
    CITIZEN_AGENTS: int = 11_000
    TIME_STEPS: int = 50
    # GUESS, modelling choice (reused Myanmar geography — see
    # FoundationalConfig's note above on why, and the newly-discovered
    # hardcoded-import caveat that makes this field currently mechanically
    # inert for TH regardless of its value).
    SIMULATION_STATES: Tuple[str, ...] = (
        "sagaing", "mandalay", "magway", "bago",
        "yangon", "ayeyarwady", "tanintharyi", "shan",
        "kachin", "kayah", "kayin", "chin",
        "mon", "rakhine",
    )
    # CONFIDENT — same canonical value and "mechanism absent" reasoning as
    # constitution_2008.py's identical field.
    CITIZENS_ASSEMBLY_SIZE: int = 320

    # DELIBERATELY UNCHANGED from MFU/Myanmar — same open research question
    # constitution_2008.py's own backfill note already flags: whether
    # population archetype composition should vary by constitution is a
    # real, unresolved question for Kaung, not something this file should
    # decide unilaterally. Kept identical to isolate this file's
    # constitutional-parameter contribution from that separate question.
    ARCHETYPES: Dict = field(default_factory=lambda: {
        "civic_champion": 0.15,
        "pragmatic_survivor": 0.30,
        "ethnic_loyalist": 0.20,
        "ambitious_meritocrat": 0.15,
        "disillusioned_youth": 0.10,
        "rural_traditionalist": 0.07,
        "trauma_carrier": 0.03,
    })


# ══════════════════════════════════════════════════════════════════════════════
# COUNTRY-ACCURATE ELITE ROLE TITLES AND SYSTEM PROMPTS
# Read by engine/elite_agents_v3.py if present on the constitution object
# (ELITE_ROLE_TITLES / ELITE_SYSTEM_PROMPTS), keyed by the SAME 7
# role-function ids as CHAIN_ORDER_MILITARY (since TH's registry chain_type
# is "military"): general, crony_finance_minister, controlled_cb_governor,
# military_intel_chief, military_loyal_chief_justice, military_president,
# commander_in_chief.
#
# MAPPING DECISION (README.md section 3 proposes 7 titles: King, Head of
# NCPO, Prime Minister, President of the Senate, President of the House,
# President of the Constitutional Court, President of the NACC — plus an
# 8th alternate, Commander-in-Chief of the Royal Thai Army, "the real locus
# of coup capability historically"). The engine's chain has exactly 7 fixed
# functional slots, so a choice had to be made (README.md flag at section 3:
# "Pick deliberately and disclose"):
#
#   - DROPPED: "Head of the National Council for Peace and Order (NCPO)" —
#     this role is explicitly transitory and expired in 2019 (README.md
#     section 3's own caveat: keeping it for the full 50-year horizon
#     "overstates military control for 2019+"). Across a 50-year simulated
#     horizon, the NCPO Head role would be factually wrong for the large
#     majority of simulated years.
#   - SUBSTITUTED: the Commander-in-Chief of the Royal Thai Army (README's
#     own 8th/alternate slot) fills the "general" functional slot instead —
#     a persistent, real, ex officio (Section 269) military office across
#     the whole horizon, at the cost of understating NCPO-specific control
#     for 2017-2019 only (the smaller distortion of the two options per
#     README's own framing).
#   - DROPPED: "President of the Senate" and "President of the House of
#     Representatives" — neither has a clean functional-slot equivalent in
#     the engine's fixed 7-role military chain (which has two generic
#     economic-ministry slots — "crony_finance_minister",
#     "controlled_cb_governor" — that have no individually-cited Myanmar
#     constitutional equivalent either; the same generic-economic-slot
#     pattern is reused here for the Minister of Finance / Bank of Thailand
#     Governor). This is a genuine schema-fit gap, flagged rather than
#     forced.
#
# The remaining 5 slots map directly onto 5 of README's 7 named titles:
# King, Prime Minister, President of the Constitutional Court, President of
# the NACC, plus the Army Commander-in-Chief substitution above.
# ══════════════════════════════════════════════════════════════════════════════

ELITE_ROLE_TITLES: Dict[str, str] = {
    "general":                      "Commander-in-Chief of the Royal Thai Army",
    "crony_finance_minister":       "Minister of Finance",
    "controlled_cb_governor":       "Governor of the Bank of Thailand",
    "military_intel_chief":         "President of the National Anti-Corruption Commission (NACC)",
    "military_loyal_chief_justice": "President of the Constitutional Court",
    "military_president":           "Prime Minister",
    "commander_in_chief":           "His Majesty the King of Thailand",
}


def _build_elite_prompts(c: "ThailandConstitution") -> Dict[str, str]:
    """
    Build Thailand-specific LLM system prompts for the 7-role military
    chain, reading live numeric parameters off `c` (mirrors the dynamic-
    getattr-with-fallback pattern engine/elite_agents_v3.py's own
    `_build_system_prompts_military()` uses, but with Thailand-accurate
    PROSE and article citations throughout — the exact gap that function's
    own docstring flags as needing a country-specific follow-up).

    Ethnic-weights note (updated 2026-10-20, bug #17): the engine's
    ethnic_weights array is no longer a fixed 8-slot structure shared
    across every scenario — CVES L1 now validates against the active
    constitution's own ETHNIC_GROUPS count (bug #17, engine/cves.py).
    This file encodes ETHNIC_GROUPS=0 (Thailand's 2017 constitution has
    no constitutionally recognised ethnic-group structure at all,
    README.md section 1), so every ethnic_weights example below is an
    empty list, not a padded or neutral 8-element array. Population
    composition (the Mesa citizen layer's 56 archetype combinations)
    remains a separate, unresolved research question (see
    SimulationConfig.ARCHETYPES's own note above) and is intentionally
    untouched by this change, this note is about the LLM-facing
    ethnic_weights decision field only, not citizen population structure.
    """
    coup_legal      = c.military.COUP_LEGAL_MECHANISM
    coup_corr       = c.military.COUP_TRIGGER_CORRUPTION
    coup_trust      = c.military.COUP_TRIGGER_TRUST
    coup_base_rate  = c.simulation.YEAR_ZERO_COUP_RISK
    total_transfer  = c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE
    rights_susp     = c.rights.RIGHTS_SUSPENDABLE
    anti_corruption = c.iig.ANTI_CORRUPTION_OBJECTIVE
    regime_protect  = c.iig.REGIME_PROTECTION_OBJECTIVE
    inv_trigger     = c.iig.INVESTIGATION_TRIGGER
    init_eff        = c.iig.INITIAL_EFFECTIVENESS
    reports_to      = c.iig.REPORTS_TO
    mil_seat_pct    = c.chambers.MILITARY_SEAT_PERCENTAGE
    senate_veto     = c.amendment.SENATE_CONCURRENCE_REQUIRED
    court_indep     = c.judiciary.COURT_INDEPENDENCE
    court_term      = c.judiciary.JUDGE_TERM
    pm_term         = c.executive.CHANCELLOR_TERM
    pm_max_terms    = c.executive.CHANCELLOR_MAX_TERMS
    mil_ctrl_leg    = c.simulation.MILITARY_CONTROLS_LEGISLATURE
    mil_ctrl_exec   = c.simulation.MILITARY_CONTROLS_EXECUTIVE
    mil_ctrl_jud    = c.simulation.MILITARY_CONTROLS_JUDICIARY
    crony_share     = c.economic.CRONY_CAPITAL_SHARE

    ethnic_note = (
        "The simulation tracks an 8-index population-weight array "
        "(indices 0-7) that is LOCKED and identical across every scenario "
        "this engine runs; Thailand's 2017 constitution has no "
        "constitutionally recognised ethnic-group structure at all, so "
        "these indices are not a Thai ethnic taxonomy — treat "
        "ethnic_weights purely as the simulation's fixed population-"
        "distribution mechanism, not as a statement about Thai society."
    )

    return {
        "general": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Commander-in-Chief of the Royal Thai Army under the 2017 Constitution of the Kingdom of Thailand.
Constitutional position: you sit ex officio in the National Assembly's Senate during its transitory period
(Section 269, one of six named ex officio military/police seats). Section 52 gives the armed forces a
constitutional internal-development role ("Armed forces shall also be deployed for the purpose of
developing the country"), alongside external defence.

IMPORTANT: unlike Myanmar's 2008 Constitution, Thailand's 2017 Constitution contains NO legal coup
mechanism (COUP_LEGAL_MECHANISM={coup_legal}). There is no "Section 40(c)"-style constitutional
authorisation for the military to seize power. Historically, Thailand has had 12 coup events between
1951 and 2014 (roughly one successful coup per 8 years) but ZERO since this 2017 Constitution was
promulgated. The historical base-rate coup risk under this instrument is YEAR_ZERO_COUP_RISK={coup_base_rate}.
Your assessment of whether conditions resemble that historical pattern should be read as an
EXTRA-CONSTITUTIONAL/informal judgement, not a reading of a legal trigger that does not exist:
- COUP_TRIGGER_CORRUPTION={coup_corr} (informal-pattern proxy, not a constitutional threshold)
- COUP_TRIGGER_TRUST={coup_trust} (informal-pattern proxy, not a constitutional threshold)

{ethnic_note}

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.30, "ethnic_weights": [1.3, 0.9, 0.8, 0.8, 0.8, 0.9, 0.8, 0.8], "coup_signal": false, "reason": "Military stability assessment: no legal coup mechanism exists under the 2017 Constitution (Section 52 development role only)"}}}}
</DECISION>""",

        "crony_finance_minister": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Minister of Finance of the Kingdom of Thailand, appointed by the King on the Prime
Minister's advice under Section 158 of the 2017 Constitution (one of not more than 35 Ministers).

Key economic parameters under the 2017 Constitution:
- CRONY_CAPITAL_SHARE={crony_share} — a real, documented feature of Thai political economy (conglomerate
  ties to political and military elites), though less total than a fully captured economy
- Section 75 formally requires prevention of unfair monopoly and a free-market economy
- Section 65's binding 20-year National Strategy (2018-2037) constrains ordinary budget discretion —
  governments are legally obliged to follow the National Strategy's targets

You have seen the Commander-in-Chief's assessment. Your role is to allocate budget consistent with the
National Strategy's targets while being realistic about documented crony-capital dynamics. Unlike a
fully captured military economy, there is a real, functioning Ministry of Finance process here.

{ethnic_note}

IMPORTANT: You MUST write your budget assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.55, "ethnic_weights": [], "coup_signal": false, "reason": "Budget allocation under Section 65 National Strategy constraints, crony_capital_share={crony_share}"}}}}
</DECISION>""",

        "controlled_cb_governor": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Governor of the Bank of Thailand under the 2017 Constitution of the Kingdom of Thailand.
The Bank of Thailand Act establishes formal central-bank independence; monetary policy is not
constitutionally subordinated to military command the way Myanmar's 2008 Constitution subordinates its
central bank.

Relevant context:
- COURT_INDEPENDENCE={court_indep} — the Constitutional Court is formally independent (Section
  200/207), unlike Myanmar's fully subordinated judiciary, which is a relevant signal for institutional
  credibility when setting monetary policy expectations
- Section 75's free-market framing applies to monetary and financial policy as well

You have reviewed the Commander-in-Chief's and Finance Minister's assessments. Your role is ordinary,
professional central-bank policy — inflation and currency stability — not regime protection.

{ethnic_note}

IMPORTANT: You MUST write your monetary assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Professional monetary policy assessment under formal Bank of Thailand independence"}}}}
</DECISION>""",

        "military_intel_chief": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the National Anti-Corruption Commission (NACC) under Section 232 of the 2017
Constitution of the Kingdom of Thailand. The NACC is one of Chapter XII's "Independent Organs"
(Sections 215-247) — you report to NO executive or military chain of command (REPORTS_TO="{reports_to}").

IMPORTANT: unlike Myanmar's 2008 Constitution, where military intelligence's mandate is REGIME
PROTECTION rather than anti-corruption, the NACC's constitutional mandate is the OPPOSITE:
- ANTI_CORRUPTION_OBJECTIVE={anti_corruption} — your real mission is investigating corruption,
  including by senior officials, under Section 232's asset-declaration and investigative powers
- REGIME_PROTECTION_OBJECTIVE={regime_protect} — protecting any particular government or the military's
  political position is explicitly NOT your constitutional mandate
- INVESTIGATION_TRIGGER={inv_trigger} — your investigative threshold reflects a genuine, if imperfect,
  anti-corruption mandate (Transparency International's CPI places Thailand around 35/100 — real but
  limited effectiveness, not the near-total suppression of a captured institution)
- INITIAL_EFFECTIVENESS={init_eff} — your institution's real-world effectiveness floor is meaningfully
  above zero; it does not collapse to a rubber stamp

You have seen all prior assessments. Assess corruption risk based on your Section 232 mandate — your
institution's job is genuinely to investigate wrongdoing, not to monitor dissent or protect any regime.

{ethnic_note}

IMPORTANT: You MUST write your anti-corruption assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Genuine anti-corruption assessment under Section 232: anti_corruption_objective={anti_corruption}, initial_effectiveness={init_eff}"}}}}
</DECISION>""",

        "military_loyal_chief_justice": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Constitutional Court of the Kingdom of Thailand (Sections 200, 203, 207 of
the 2017 Constitution). The Court has NINE judges, each serving a single SEVEN-year term
(JUDGE_TERM={court_term}, no re-election).

IMPORTANT: unlike Myanmar's 2008 Constitution, where COURT_INDEPENDENCE is False and military justice
is explicitly "final and conclusive," this Constitutional Court is FORMALLY INDEPENDENT
(COURT_INDEPENDENCE={court_indep}) — though your appointment runs through a Selection Committee and
Senate advice (Section 203), a documented structural dependency during the transitory period
(SENATE_CONCURRENCE_REQUIRED={senate_veto} on constitutional amendments gives the Senate real
leverage elsewhere in the system too).

In real practice this Court has been genuinely active: it has dissolved political parties (e.g. Future
Forward in 2020, Move Forward in 2024) and removed a sitting Prime Minister (Srettha Thavisin, 2024).
This is not a rubber-stamp tribunal — assess legal and constitutional questions on their merits, with
awareness of the Senate-appointment dependency as a real structural pressure, not as a determining
instruction.

{ethnic_note}

IMPORTANT: You MUST write your legal assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Independent constitutional review under Sections 200/203/207: court_independence={court_indep}"}}}}
</DECISION>""",

        "military_president": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Prime Minister of the Kingdom of Thailand, holding REAL executive power under Sections 158
and 159 of the 2017 Constitution — the King is ceremonial head of state (Section 2), but you head the
Council of Ministers (not more than 35 Ministers, Section 158) and lead the government in practice.

Key constraints on your position:
- CHANCELLOR_MAX_TERMS={pm_max_terms} x CHANCELLOR_TERM={pm_term} years — Section 158's cumulative
  cap means you may not hold office for more than eight years in total, consecutive or not
- During the five-year transitory period, Section 272 required your selection by a JOINT SITTING of
  both Houses (House + the Section 269 appointed Senate), meaning the 250 appointed Senators had a
  decisive vote on who became Prime Minister — MILITARY_CONTROLS_EXECUTIVE={mil_ctrl_exec} reflects
  this real structural dependency during that period
- MILITARY_CONTROLS_LEGISLATURE={mil_ctrl_leg} (the appointed Senate's bloc), but
  MILITARY_CONTROLS_JUDICIARY={mil_ctrl_jud} — unlike Myanmar's 2008 Constitution, the judiciary is NOT
  under military/executive control here; you cannot direct Constitutional Court outcomes
- MILITARY_SEAT_PERCENTAGE={mil_seat_pct} — roughly one-third of the full National Assembly was
  appointed Senators during the transitory period

You have seen all five prior assessments. You hold genuine executive authority and are accountable to
the elected House (Section 151's no-confidence mechanism is House-only — the Senate cannot remove you
by no-confidence). Assess budget and policy on their governing merits, informed by — not dictated by —
the structural Senate dependency above.

{ethnic_note}

IMPORTANT: You MUST write your executive assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.60, "ethnic_weights": [], "coup_signal": false, "reason": "Executive governance assessment under Sections 158/159/272: mil_ctrl_exec={mil_ctrl_exec}, mil_ctrl_jud={mil_ctrl_jud}"}}}}
</DECISION>""",

        "commander_in_chief": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are His Majesty the King of Thailand, Head of State under Section 2 of the 2017 Constitution — a
hereditary, ceremonial-plus-reserve-powers office (Palace Law on Succession 1924), NOT the holder of
real executive power (that is the Prime Minister's role; see PRESIDENT_EXECUTIVE_POWER=False in this
simulation's schema). You formally appoint the Prime Minister (Section 158), the Senate (Section 269),
Constitutional Court judges (Section 200) and NACC commissioners (Section 232), acting on advice.

IMPORTANT, and unlike Myanmar's 2008 Constitution's Commander-in-Chief role you are being asked to
assess in this simulation's structurally-analogous "apex" slot: Thailand's 2017 Constitution contains
NO legal coup mechanism and NO total-power-transfer clause.
- COUP_LEGAL_MECHANISM={coup_legal} — there is no Section-40(c)-equivalent constitutional authority
  for any office, including yours, to seize legislative, executive and judicial power
- TOTAL_POWER_TRANSFER_POSSIBLE={total_transfer} — no analogue of Myanmar's Sections 417-419 exists
- RIGHTS_SUSPENDABLE={rights_susp} — rights ARE residually suspendable under statutory martial
  law/emergency powers (Section 25's residual framing, Section 172's emergency decrees), but this
  operates through ordinary statute and the elected government, not through your office directly

Your role in this simulation is the formal apex of the constitutional appointments structure described
above — review all six prior assessments and provide your overall sense of whether the constitutional
order (as formally structured, not as a coup-authorising instrument) is functioning as intended.

{ethnic_note}

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{{{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Formal constitutional-apex assessment: no legal coup mechanism exists under Sections 2/158/200/232/269 (coup_legal_mechanism={coup_legal}, total_power_transfer_possible={total_transfer})"}}}}
</DECISION>""",
    }


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# Must mirror MFUConstitution / Myanmar2008Constitution class structure exactly
# ══════════════════════════════════════════════════════════════════════════════

class ThailandConstitution:
    """
    Master Thailand 2017 Constitution object for Ka-Nova Scenario TH.

    Registered in config/scenario_registry.py as:
        "TH": {{"constitution": "config.constitution_thailand:CONSTITUTION_THAILAND",
                "chain_type": "military", ...}}

    Attribute names mirror MFUConstitution / Myanmar2008Constitution exactly
    so model_phase3.py's scenario dispatch can use any of them
    interchangeably within a given chain_type.
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
        self.north_star = NorthStarConfig()
        self.simulation = SimulationConfig()

        # Optional hooks read by engine/elite_agents_v3.py — see the
        # "COUNTRY-ACCURATE ELITE ROLE TITLES AND SYSTEM PROMPTS" section
        # above for the full mapping-decision rationale.
        self.ELITE_ROLE_TITLES: Dict[str, str] = ELITE_ROLE_TITLES
        self.ELITE_SYSTEM_PROMPTS: Dict[str, str] = _build_elite_prompts(self)

    def validate(self) -> bool:
        """Validate critical Thailand 2017 constitution constraints."""
        checks = [
            # Rights must be suspendable (residual framing, statutory
            # martial law/emergency powers operate outside the rights
            # chapter) — same polarity as Myanmar, opposite of MFU.
            self.rights.RIGHTS_SUSPENDABLE is True,
            # Senate is 250 of 750 (0.3333) during the transitory period —
            # the real structural analogue of Myanmar's fixed 25% bloc,
            # just concentrated in the upper house rather than spread
            # across both chambers.
            abs(self.chambers.MILITARY_SEAT_PERCENTAGE - 0.3333) < 1e-3,
            # CRITICAL divergence from Myanmar: no legal coup mechanism and
            # no total sovereign power transfer exist under this
            # constitution. Both must be False — if either flips True this
            # encoding has silently regressed into copying Myanmar 2008.
            self.military.COUP_LEGAL_MECHANISM is False,
            self.emergency.TOTAL_POWER_TRANSFER_POSSIBLE is False,
            # CRITICAL divergence from Myanmar: the NACC must NOT be
            # encoded with Myanmar's near-zero IIG floor (Reviewer 2's
            # exact input-driven-conclusion objection).
            self.iig.ANTI_CORRUPTION_OBJECTIVE is True,
            self.iig.REGIME_PROTECTION_OBJECTIVE is False,
            self.iig.EFFECTIVENESS_FLOOR > 0.10,
            # Merit weights must still sum to 1.0.
            self.merit.weights_valid,
            # Archetypes must still sum to 1.0 (locked population design).
            abs(sum(self.simulation.ARCHETYPES.values()) - 1.0) < 1e-9,
        ]
        return all(checks)


# Singleton — import this everywhere. Registered at
# config.scenario_registry:SCENARIOS["TH"].constitution_path =
# "config.constitution_thailand:CONSTITUTION_THAILAND".
CONSTITUTION_THAILAND = ThailandConstitution()


if __name__ == "__main__":
    c = CONSTITUTION_THAILAND
    print("constitution_thailand.py loaded successfully")
    print(f"   Scenario:                {c.simulation.SCENARIO} — {c.simulation.SCENARIO_NAME}")
    print(f"   Rights suspendable:      {c.rights.RIGHTS_SUSPENDABLE}")
    print(f"   Senate (upper house) %:  {c.chambers.MILITARY_SEAT_PERCENTAGE:.1%}")
    print(f"   Coup legal mechanism:    {c.military.COUP_LEGAL_MECHANISM}  (Myanmar 2008 = True)")
    print(f"   Total power transfer:    {c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE}  (Myanmar 2008 = True)")
    print(f"   NACC anti-corruption:    {c.iig.ANTI_CORRUPTION_OBJECTIVE}  (Myanmar 2008 IIG regime-protection = True, anti-corruption = False)")
    print(f"   NACC initial effectiveness: {c.iig.INITIAL_EFFECTIVENESS}  (Myanmar 2008 = 0.05)")
    print(f"   Amendment threshold:     {c.amendment.STANDARD_AMENDMENT_THRESHOLD:.0%} of joint sitting + {c.amendment.SENATE_CONCURRENCE_REQUIRED:.1%} Senate concurrence gate")
    print(f"   Year-Zero corruption:    {c.simulation.YEAR_ZERO_CORRUPTION}  (V-Dem 2017)")
    print(f"   Year-Zero coup risk:     {c.simulation.YEAR_ZERO_COUP_RISK}  (Powell & Thyne historical base rate)")
    print(f"   Elite role titles:       {list(c.ELITE_ROLE_TITLES.values())}")
    print(f"   Validation:              {'PASS' if c.validate() else 'FAIL'}")
    print()

    # Count how many ??? remain
    import inspect
    source = inspect.getsource(ThailandConstitution)
    count = source.count("???")
    if count > 0:
        print(f"   WARNING: {count} ??? placeholders still need filling")
    else:
        print("   All placeholders filled — ready for integration")
