"""
================================================================================
PROJECT KA-NOVA
config/constitution_pakistan.py

Pakistan — 1973 Constitution of the Islamic Republic of Pakistan, AS REVIVED BY
THE REVIVAL OF THE CONSTITUTION OF 1973 ORDER, 1985 (President's Order No. 14
of 1985, "RCO 1985", effective 2 March 1985), AND AS AMENDED BY THE
CONSTITUTION (EIGHTH AMENDMENT) ACT, 1985 (Act 18 of 1985, presidential assent
9 November 1985, Gazette of Pakistan Extraordinary 11 November 1985).
Ka-Nova Simulation Engine — Scenario "PK" — registry chain_type: "military"

Recommended instrument label (per the research package, do not vary):
    "1973_constitution_as_revived_1985_with_eighth_amendment"

This file is a COMPOSITE of two 1985 instruments operating on the 1973
Constitution's base text. Every field below is labelled with which of the
two supplied it, or with "RCO 1985" vs "8th Amendment" where the research
package's own sourcing distinguishes them. Instrument lifespan: 2 March 1985
(RCO) -> 12 October 1999 (Musharraf coup, the order/amendment package
destroyed in practice; Art. 58(2)(b) itself was already repealed by the
Thirteenth Amendment in April 1997).

Real survival-time anchors (research package section 2.4, Powell & Thyne
V2026.08.29 + National Assembly of Pakistan's own dissolution history):
    RCO (2 Mar 1985)              -> Musharraf coup (12 Oct 1999) = 14.61 years
    8th Amendment assent (9 Nov 1985) -> same coup                = 13.92 years
Compare Myanmar 2008: ratification (29 May 2008) -> coup (1 Feb 2021) = 12.68
years. Compare Ka-Nova Scenario C's own simulated mean: 15.6 years. Pakistan
is the SECOND, independently-sourced military-guardianship anchor bracketing
Scenario C's simulated number from below while Myanmar brackets it from
below too (12.68 < 14.61/13.92 < 15.6 roughly) — see this module's own
__main__ self-test and the task-level report for the rule-based smoke-test
result against this window.

SOURCE: `config/constitution_pakistan_encoding/README.md` (senior-researcher,
2026-10-20) — the Eighth Amendment Act full text, Art. 58(2)(b) verbatim,
Art. 48(2), Art. 91(5), Art. 270A, Art. 245(2)-(4), Art. 239(5), V-Dem
political-corruption trajectory (0.637 1985 -> 0.831 1990), WGI 1996-2022,
TI CPI 1995-2025, and country-accurate elite role titles. Three corrections
to standard secondary literature are already folded into the values below
(research package flag F4):
    1. Art. 2A was inserted by the RCO 1985, NOT the Eighth Amendment.
    2. The Eighth Amendment DELETED Art. 152-A (National Security Council);
       it did not create one.
    3. "In his discretion" on service-chief appointment entered Art. 243
       only via LFO 2002, not the 1985 instrument.

Every field is tagged CONFIDENT (direct article citation in the research
package, or a direct quotation/computation already in that package) or
GUESS (a defensible modelling choice flagged because the research package
does not cover it, or covers it only as a secondary-source proxy — see the
package's own L1-L8 sourcing-limitation notes). Same tagging convention as
`config/constitution_2008.py`.

Architecture: mirrors `config/constitution_2008.py`'s dataclass structure
field-for-field (confirmed 86 section.attribute pairs the live engine reads
— see `.claude/memory.md` section 5, bug #11 entry). Field NAMES are
identical to constitution_2008.py/constitution.py; only VALUES and comments
differ. A small number of EXTRA fields (not part of the confirmed 86, not
read by the live engine today) are added where the research package
explicitly asked for a new channel the schema cannot express (flag F3's
Art. 58(2)(b) dissolution mechanism, flag's Seventh Schedule entrenchment,
Art. 270A's immunity-scope string) — these are clearly marked "EXTRA, not
yet read by the live engine" and do not collide with anything the engine
actually reads.

chain_type: "military" (config/scenario_registry.py, code "PK"). Encoded by
Claude Code (senior-simulation-engineer role) 2026-10-20.
Architecture owner: Kaung Htet.
License: MIT
================================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# ART. 1-2A, 5-6 — BASIC PRINCIPLES / STATE / CITIZENSHIP
# Maps to: constitution.py -> FoundationalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Art. 1-6 — the state, its territory, and the basic duty of citizens."""

    # CONFIDENT — Art. 1: "Pakistan shall be a Federal Republic to be known
    # as the Islamic Republic of Pakistan."
    STATE_NAME: str = "Islamic Republic of Pakistan"

    # GUESS — Art. 251 names Urdu as the national language; not discussed in
    # the research package, common-knowledge fact only.
    OFFICIAL_LANGUAGE: str = "Urdu"
    # GUESS — Pakistan's constitutionally recognised minority structure is
    # RELIGIOUS (10 reserved non-Muslim National Assembly seats — see
    # ChamberConfig.ETHNIC_SEATS below), not ethnic/linguistic the way
    # Myanmar's Section 22(a) is. No equivalent protected-ethnic/provincial-
    # language clause is documented in the research package for the 1985
    # era. Set False rather than reusing Myanmar's True by reflex (research
    # package L8).
    ETHNIC_LANGUAGES_PROTECTED: bool = False

    # GUESS — common knowledge, not discussed in the research package.
    CAPITAL: str = "Islamabad"
    FLAG: str = "1947_pakistan_flag"

    # GUESS — Pakistan Citizenship Act 1951 modes, not covered by the
    # research package (which is scoped to the constitutional-amendment
    # instrument, not citizenship statute law). Structurally parallel to
    # constitution_2008.py's tuple, not individually cited.
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "born_in_pakistan_or_to_pakistani_parent",
        "existing_citizen_on_commencement",
    )
    # GUESS — Pakistan Citizenship Act 1951, s.9 (statute, not constitution;
    # not in the research package's scope).
    NATURALIZATION_YEARS: int = 5
    NATURALIZATION_MERIT_MIN: float = 0.0

    # CONFIDENT — Art. 1: federation of four provinces (Punjab, Sindh,
    # North-West Frontier Province [NWFP — the province's name for this
    # instrument's ENTIRE 1985-1999 life; renamed Khyber Pakhtunkhwa only
    # by the Eighteenth Amendment, assented 19 April 2010, eleven years
    # after this instrument collapsed — see SimulationConfig.
    # SIMULATION_STATES below for the corrected unit name], Balochistan)
    # plus the Islamabad Capital Territory plus (until the 2018 merger, so
    # present throughout 1985-1999) the Federally Administered Tribal Areas.
    TERRITORY_BASIS: str = "federation_of_four_provinces_plus_ict_and_fata"
    # CONFIDENT on the real count (4 provinces; 6 if ICT+FATA are counted as
    # separate units) — but NOTE: model_phase3.py's _initialize_states()
    # hardcodes Myanmar's literal 14-state name list regardless of which
    # constitution is active (confirmed by direct grep of model_phase3.py —
    # it does not read CONSTITUTION.simulation.SIMULATION_STATES or
    # CONSTITUTION.foundational.STATE_COUNT at all). This field is therefore
    # currently DECORATIVE for every scenario, Myanmar included, not just
    # Pakistan — flagged honestly rather than claiming a false mechanical
    # effect. See SimulationConfig.SIMULATION_STATES below for the same
    # caveat restated at the point the engine would need to read it.
    STATE_COUNT: int = 4
    SIMULATION_STATE_COUNT: int = 4


# ══════════════════════════════════════════════════════════════════════════════
# PART II, CHAPTER 1 — FUNDAMENTAL RIGHTS (Art. 8-28) + ART. 232-237, 245
# Maps to: constitution.py -> RightsConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Part II, Chapter 1 — Fundamental Rights, and their real carve-outs."""

    # CONFIDENT — Part II Chapter 1 (Art. 8-28) exists; the specific article
    # list below is GUESS as to WHICH rights to enumerate (the research
    # package cites the chapter and Art. 8(1)-(3) specifically, not every
    # individual right). Deliberately excludes Art. 25A (right to education)
    # — that clause was inserted by the 18th Amendment in 2010, well after
    # this instrument's 1985-1999 life; including it would be a real
    # anachronism the research package's L3 warning explicitly flags for
    # OTHER articles and which applies here by the same logic.
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "equality_before_law",         # Art. 25
        "freedom_of_movement",         # Art. 15
        "freedom_of_assembly",         # Art. 16
        "freedom_of_association",      # Art. 17
        "freedom_of_speech",           # Art. 19
        "freedom_of_trade_business",   # Art. 18
        "protection_of_property",       # Art. 23-24
    )

    # CONFIDENT — Art. 233: during a Proclamation of Emergency, named
    # fundamental rights may be suspended; Art. 233(2) additionally permits
    # suspension of the RIGHT TO MOVE ANY COURT for enforcement of rights.
    RIGHTS_SUSPENDABLE: bool = True
    # CONFIDENT — Art. 8(3)(b) + the First Schedule exempt a schedule of
    # named statutes from Art. 8(1)-(2)'s rights-review altogether (expanded
    # under the RCO/8th Amendment era). Research package's explicit
    # recommendation: "RIGHTS_ABSOLUTE_COUNT should therefore be 0."
    RIGHTS_ABSOLUTE_COUNT: int = 0
    # CONFIDENT — follows directly from Art. 233 above.
    EMERGENCY_TOUCHES_RIGHTS: bool = True

    # CONFIDENT by absence — the research package documents no Pakistani
    # equivalent to Myanmar's Section 386 mandatory-military-training
    # clause for the general citizenry. Art. 244 only binds members of the
    # Armed Forces to an oath, it does not conscript the wider population.
    NATIONAL_SERVICE_MANDATORY: bool = False
    # GUESS — kept for schema parity only; inert given
    # NATIONAL_SERVICE_MANDATORY = False above. Not a cited figure.
    NATIONAL_SERVICE_AGE: int = 18
    NATIONAL_SERVICE_DURATION_MONTHS: int = 0

    # CONFIDENT — Art. 245(3)-(4) (Seventh Amendment 1977, already in force
    # throughout 1985-1999): High Court Art. 199 jurisdiction is EXCLUDED in
    # any area where the Armed Forces are, for the time being, acting in aid
    # of civil power, and pending proceedings are suspended. Research
    # package: "a judicial no-go zone wherever the army is deployed
    # domestically — a structurally stronger exclusion than anything in
    # Thailand 2017 and directly comparable to Myanmar 2008 s.293(b)/343(b)."
    MILITARY_RIGHTS_OVERRIDE: bool = True

    # GUESS magnitude, directionally grounded — Ka-Nova simulation
    # parameters, not literal constitutional citations (same framing as
    # both existing files' own disclaimers for this pair). Pakistan's real
    # rights-suppression channel ran mostly through courts/jurisdiction-
    # stripping (Art. 245(3)-(4), Art. 233(2)) rather than Myanmar's blanket
    # Section 414(b) framing, and the four Art. 58(2)(b) dissolutions were
    # contested in court (e.g. Haji Saifullah 1988) rather than met with
    # mass street protest the way Myanmar's post-2021 crackdown was —
    # grievance spike kept at the same suppressed level as Myanmar; trust
    # drop set moderately higher to reflect genuine (if legalistic) erosion.
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.05
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.10


# ══════════════════════════════════════════════════════════════════════════════
# NO CONSTITUTIONAL MERIT-SELECTION FORMULA
# Maps to: constitution.py -> MeritConfig
# The 1973 Constitution (as revived 1985) has no MFU-style weighted merit
# formula for public office. Civil-service entry runs through the Federal
# Public Service Commission (Art. 242, statutory CSS exam); political
# appointments ran through presidential/military patronage under this
# instrument. Research package does not cover a "MeritConfig" chapter at
# all for Pakistan (no equivalent provision found) — every field below is
# GUESS, a deliberate modelling choice, not a textual citation.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """No constitutional merit formula — patronage + a real but non-
    constitutional civil-service exam (Art. 242 FPSC) coexist."""

    # GUESS — modelling choice. Pakistan's hybrid is placed directionally
    # BETWEEN MFU's merit-formula system and Myanmar's pure loyalty-
    # dominant system: a real competitive exam (FPSC) exists for the
    # bureaucracy, but political/presidential confidence dominates
    # ministerial and judicial appointment under this instrument.
    PRODUCTIVITY_WEIGHT: float = 0.15
    EDUCATION_WEIGHT: float = 0.20
    PERFORMANCE_WEIGHT: float = 0.20
    CIVIC_WEIGHT: float = 0.45   # patronage/loyalty-dominant, less extreme than Myanmar's 0.55

    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    MERIT_MIN_PUBLIC_OFFICE: float = 0.0
    # CONFIDENT that this body exists (Art. 242, Federal Public Service
    # Commission) — GUESS that it is the right proxy for "EXAM_ADMINISTRATOR"
    # given political appointments bypass it entirely under this instrument.
    EXAM_ADMINISTRATOR: str = "federal_public_service_commission"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 0
    EXAM_RESULTS_PUBLISH_DAYS: int = 0

    # GUESS — Art. 6 (high treason: abrogating/subverting the Constitution
    # by force) is the one disqualification ground directly cited in the
    # research package; the rest mirror the structural idiom of both
    # existing files without a specific Art. 62/63 citation (the research
    # package does not quote Art. 62/63's disqualification text).
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "high_treason_art6",
        "breach_of_constitution",
    )
    DISQUALIFICATION_PERMANENT: bool = True

    RECERTIFICATION_INTERVAL: int = 0
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.0
    RECERTIFICATION_VACATE_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# ART. 41-48 (PRESIDENT) + ART. 90-95 (PRIME MINISTER / CABINET)
# Maps to: constitution.py -> ExecutiveConfig
# THE CORE OF THE INSTRUMENT: Art. 48(2) + Art. 58(2)(b) + Art. 91(5)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Semi-presidential design with a president-dominant tilt — the heart
    of the Eighth Amendment package."""

    # CONFIDENT — research package's own exact mapping advice. Art. 41:
    # President is Head of State; Art. 48(2) as amended by 8th Amdt s.2:
    # discretionary presidential acts are non-justiciable "on any ground
    # whatsoever"; Art. 58(2)(b) as substituted by 8th Amdt s.5(b): the
    # President may dissolve the National Assembly in his discretion where
    # "a situation has arisen in which the Government of the Federation
    # cannot be carried on in accordance with the provisions of the
    # Constitution and an appeal to the electorate is necessary."
    PRESIDENT_ROLE: str = "head_of_state_with_discretionary_dissolution_power"
    # CONFIDENT — Art. 41(3) + Second Schedule.
    PRESIDENT_ELECTION: str = "electoral_college_both_houses_plus_provincial_assemblies"
    # CONFIDENT — Art. 44(1).
    PRESIDENT_TERM: int = 5
    # CONFIDENT — Art. 44(2): re-eligible but no more than two consecutive terms.
    PRESIDENT_MAX_TERMS: int = 2
    PRESIDENT_REELECTION: bool = True

    PRESIDENT_TIEBREAKER: bool = False
    # CONFIDENT — research package's explicit mapping advice: True.
    PRESIDENT_EXECUTIVE_POWER: bool = True

    # CONFIDENT — research package's explicit mapping advice. Art. 91 as
    # amended by 8th Amdt s.10, new (5): "The Prime Minister shall hold
    # office during the pleasure of the President..." — Pakistan, unlike
    # Myanmar (CHANCELLOR_ROLE="none"), genuinely HAS a Prime Minister
    # distinct from the Head of State; this is a real structural difference
    # from the 2008 Myanmar near-twin that the paper should state plainly.
    CHANCELLOR_ROLE: str = "prime_minister_at_presidential_pleasure"
    # CONFIDENT direction — Art. 91: PM commands the confidence of the
    # National Assembly majority (subject to the Art. 91(2-A) proviso below
    # that this requirement was time-limited to only apply after 20 March
    # 1990 — before that date the President's choice of PM was formally
    # unconstrained, per the research package).
    CHANCELLOR_ELECTION: str = "national_assembly_confidence_vote_unconstrained_before_1990_03_20"
    # CONFIDENT — Art. 52: National Assembly term is five years from first sitting.
    CHANCELLOR_TERM: int = 5
    CHANCELLOR_MAX_TERMS: int = 0   # unlimited — no PM term-cap documented, unlike the President's Art. 44(2) cap
    CHANCELLOR_COOLING_OFF: int = 0  # GUESS/absent — no cooling-off period documented

    PRESIDENT_ELECTION_YEAR: int = 1
    CHANCELLOR_ELECTION_YEAR: int = 1   # Pakistan DOES have a PM from year one, unlike Myanmar's "0 = none"

    MINISTER_COUNT: int = 20            # GUESS proxy, real cabinet size not cited
    MINISTER_MERIT_MIN: float = 0.0
    # CONFIDENT direction — Art. 92: Cabinet appointed by the President on
    # the advice of the Prime Minister.
    MINISTER_CONFIRMATION: str = "prime_ministerial_advice_presidential_appointment"

    # GUESS — plausible 1985-era cabinet portfolio list; not individually
    # cited in the research package.
    MINISTRIES: Tuple[str, ...] = (
        "ministry_of_defence",
        "ministry_of_interior",
        "ministry_of_finance",
        "ministry_of_foreign_affairs",
        "ministry_of_information",
        "ministry_of_religious_affairs",
        "ministry_of_education",
        "ministry_of_law_and_justice",
    )

    # CONFIDENT — Art. 95: a vote of no-confidence in the PM is moved by not
    # less than 20% of the NA's total membership and carried by a majority
    # of the total membership — a single-chamber (NA-only) mechanism.
    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 1
    CHANCELLOR_DISMISSAL_VETO: bool = False
    # CONFIDENT — research package's explicit mapping advice.
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = True

    # CONFIDENT — Art. 47: removal of the President requires notice by not
    # less than one-half of the total membership of either House (one
    # chamber to initiate), then passage by not less than two-thirds of the
    # total membership of Majlis-e-Shoora IN JOINT SITTING (both chambers).
    PRESIDENT_REMOVAL_CHAMBERS: int = 2
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = False
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = False
    # CONFIDENT — Art. 47: notice threshold is 50% of either House's total membership.
    # (The subsequent joint-sitting PASSAGE threshold is 0.667 — see AmendmentConfig
    # idiom; the engine field here models the notice stage specifically.)
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.50
    # GUESS — Ka-Nova simulation trigger, not a textual figure (same
    # modelling status as constitution_2008.py's own 0.20 for this field).
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.20

    # CONFIDENT — Art. 49: in case of vacancy, the Chairman of the Senate
    # acts as President (first in line of succession).
    CHANCELLOR_INTERIM: str = "chairman_of_senate_acts_as_president_art49"

    # ─── EXTRA fields, NOT part of the confirmed 86-field engine contract ───
    # Research package flag F3: "The 58(2)(b) mechanism has no
    # representation in the current schema, and it is the whole point of
    # choosing this instrument... Pakistan's failure mode was SERIAL
    # CONSTITUTIONAL DECAPITATION, not a single collapse event — four
    # governments removed in eight years, every one of them before
    # completing a term." These two fields document that finding for the
    # paper/reproducibility package; the live engine does not currently
    # read them (no EXECUTIVE_DISSOLUTION_* mechanical channel exists in
    # model_phase3.py/feedback/loops.py today). Flagged to
    # senior-simulation-engineer/Kaung as a real follow-up engine-design
    # request, not silently implemented here.
    EXECUTIVE_DISCRETIONARY_DISSOLUTION: bool = True     # EXTRA — Art. 58(2)(b)
    DISSOLUTION_NON_JUSTICIABLE: bool = True              # EXTRA — Art. 48(2) + Art. 41(6)
    # CONFIDENT (documentation) — the four real Art. 58(2)(b) dissolutions:
    # 29 May 1988 (PM Junejo), 6 Aug 1990 (PM Bhutto I), 18 Apr 1993 (PM
    # Sharif I), 5 Nov 1996 (PM Bhutto II). Dates per the National Assembly
    # of Pakistan's own published history, relayed through secondary
    # accounts — research package flag L4: verify against a primary
    # gazette notification before these dates are load-bearing in print.
    HISTORICAL_DISSOLUTION_COUNT_1985_1997: int = 4       # EXTRA, documentation only


# ══════════════════════════════════════════════════════════════════════════════
# ART. 50-75 — MAJLIS-E-SHOORA (PRESIDENT + NATIONAL ASSEMBLY + SENATE)
# Maps to: constitution.py -> ChamberConfig
# KEY DIFFERENCE FROM MYANMAR 2008: ZERO reserved military seats.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Art. 50-75 — Majlis-e-Shoora (Parliament): President + NA + Senate."""

    CONGRESS_ELECTION: str = "direct_election_territorial_constituencies"  # CONFIDENT general structure, Art. 51
    CONGRESS_THRESHOLD: float = 0.51   # GUESS/Ka-Nova convention (simple majority proxy)
    CONGRESS_TERM: int = 5             # CONFIDENT — Art. 52
    CONGRESS_REELECTION: bool = True

    # CONFIDENT — these two field names are literally Myanmar's two Hluttaw
    # chambers; the live engine uses them generically as "reserved military
    # seats in chamber 1 / chamber 2." Pakistan's two chambers are the
    # National Assembly and the Senate. Research package's central finding:
    # "Zero reserved military seats. Pakistan's military influence under
    # this instrument runs through the presidency, the non-justiciability
    # clauses and Art. 270A immunity — not through reserved seats. This is
    # the key structural difference from Myanmar 2008 (25%) and Thailand
    # 2017 (6 ex-officio senators + 250 appointed)."
    MILITARY_RESERVED_SEATS_PYITHU: int = 0     # National Assembly
    MILITARY_RESERVED_SEATS_AMYOTHA: int = 0    # Senate
    MILITARY_SEAT_PERCENTAGE: float = 0.0
    MILITARY_SEATS_APPOINTED_BY: str = "not_applicable_no_reserved_seats"

    # CONFIDENT, with L1 caveat — research package: "National Assembly
    # 1985-1997: 237 seats — 207 general + 20 reserved for women + 10 for
    # non-Muslims." The 10 non-Muslim seats are the closest real analogue to
    # this field; Pakistan's constitutionally-codified minority structure is
    # RELIGIOUS, not ethnic (research package L8) — reused here as the
    # nearest real mechanism rather than fabricating an ethnic quota that
    # does not exist. Seat counts sourced from the IPU's archived 1985
    # Pakistan election report and the National Assembly's own history page
    # — VERIFY against the 1985 Gazette before publication (research
    # package L1).
    ETHNIC_SEATS: int = 10
    ETHNIC_THRESHOLD: float = 0.51
    ETHNIC_TERM: int = 5

    # GUESS, directionally grounded — Pakistan 1985-1997 has NO
    # Constitutional-Tribunal-equivalent body at all (unlike Myanmar's
    # Section 320 Constitutional Tribunal, which IS the real analogue
    # constitution_2008.py maps ANALYSIS_* onto). The research package's
    # JudiciaryConfig notes that this instrument contains FIVE separate
    # jurisdiction-stripping clauses (Art. 239(5)-(6), Art. 48(2), Art.
    # 41(6), Art. 245(2)-(4), Art. 270A) that strip courts of review power
    # over exactly the kind of decision an Analysis-Council-equivalent body
    # would check. Set to an unreachable unanimous threshold to model "no
    # functioning check exists," the same null-via-value idiom
    # constitution_2008.py uses elsewhere (e.g. JudiciaryConfig.
    # TOTAL_RUIN_THRESHOLD = 0.0 for "mechanism absent"). This field IS
    # mechanically read by institutions/chambers.py — the choice has a real
    # effect: Pakistan's Analysis-Council-equivalent veto path never
    # successfully blocks a policy under this encoding, consistent with the
    # real absence of any such reviewing body.
    ANALYSIS_THRESHOLD: float = 1.00
    ANALYSIS_VETO_TIME_LIMIT: int = 0
    ANALYSIS_MERIT_MIN: float = 0.0
    ANALYSIS_TERM: int = 5

    # CONFIDENT direction — follows directly from MILITARY_SEAT_PERCENTAGE
    # = 0.0 above: there is no reserved bloc to vote in discipline.
    MILITARY_BLOC_VOTE_DISCIPLINE: float = 0.0
    # CONFIDENT direction — Pakistan's real "effective majority" constraint
    # on entrenched action is Art. 239's 2/3 + 2/3 amendment threshold, not
    # a reserved military bloc (since none exists).
    CIVILIAN_EFFECTIVE_MAJORITY_NEEDED: float = 0.667

    ETHNIC_MAX_TERMS: int = 99                 # GUESS — no cap documented
    ETHNIC_PRESIDENTIAL_MIN_TERMS: int = 99    # GUESS — no such pathway documented


# ══════════════════════════════════════════════════════════════════════════════
# ART. 175-209 (JUDICIARY) + CHAPTER 3A ART. 203A-203J (FEDERAL SHARIAT COURT)
# Maps to: constitution.py -> JudiciaryConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Art. 175-209 (ordinary courts) + Art. 203A-203J (Federal Shariat Court)."""

    # CONFIDENT — research package: five separate jurisdiction-stripping
    # clauses (Art. 239(5)-(6), Art. 48(2), Art. 41(6), Art. 245(2)-(4),
    # Art. 270A) justify COURT_INDEPENDENCE=False "on textual grounds, not
    # on vibes."
    COURT_INDEPENDENCE: bool = False
    # GUESS, with L1 caveat — research package: "the Supreme Court's
    # strength is fixed by Act of Parliament, not the Constitution (Art.
    # 176). In 1985 it was 7 + CJ (verify before encoding)." Mapped instead
    # to the Federal Shariat Court's fixed constitutional strength (Art.
    # 203C: not more than eight Muslim judges including the CJ) per the
    # research package's own suggestion, since that figure IS textually
    # fixed rather than a to-be-verified proxy.
    COURT_JUDGES_COUNT: int = 8
    # CONFIDENT — Art. 179 (1985-era text): Supreme Court judges retire at 65.
    COURT_TERM_YEARS: int = 65
    RULING_THRESHOLD: int = 5   # GUESS — simple majority of 8, not specified in text

    # CONFIDENT direction — Art. 245(3)-(4) excludes High Court jurisdiction
    # in army-deployment areas; the Pakistan Army Act 1952 (as amended)
    # provides for military trial of civilians in defined cases.
    MILITARY_JUSTICE_FINAL: bool = True
    CIVILIAN_COURT_OVERRIDE_MILITARY: bool = False

    # CONFIDENT — Art. 203C: Federal Shariat Court, not more than eight
    # Muslim judges including the Chief Justice, appointed by the
    # President. "Judges of the FSC served at the President's pleasure and
    # could be transferred back to their High Courts, which is why the FSC
    # is treated in the literature as a presidentially-controlled parallel
    # apex court" (research package). This is the real analogue mapped onto
    # this field, not Myanmar's Section 320 Constitutional Tribunal (which
    # has no Pakistani equivalent for this instrument — see ChamberConfig.
    # ANALYSIS_THRESHOLD above).
    CONSTITUTIONAL_TRIBUNAL_SIZE: int = 8
    # GUESS — FSC judges serve at the President's pleasure (no fixed term
    # is specified in the text); modelled as a short, insecure tenure
    # rather than a cited figure.
    TRIBUNAL_TERM_YEARS: int = 3

    COURT_CORRUPTION_RESISTANCE: float = 0.20   # GUESS, same magnitude as constitution_2008.py, no better figure available
    TOTAL_RUIN_THRESHOLD: float = 0.0           # CONFIDENT by absence — no Total Ruin mechanism exists

    JUDGE_COUNT: int = 8        # CONFIDENT — mirrors COURT_JUDGES_COUNT above
    # GUESS — Art. 179 caps tenure by AGE (65), not a fixed term length; the
    # engine models term_remaining as an annual countdown, which has no
    # literal textual equivalent. Set slightly shorter than Myanmar's own
    # GUESS of 15, reflecting Pakistan's historically higher judicial
    # turnover under Art. 209 Supreme Judicial Council pressure and
    # extra-constitutional regime change — NOT a cited constitutional figure.
    JUDGE_TERM: int = 12
    JUDGE_MAX_TERMS: int = 1    # GUESS — age-capped single continuous appointment, no renewable-term concept
    BUDGET_FIXED: bool = False  # CONFIDENT direction — follows from COURT_INDEPENDENCE = False


# ══════════════════════════════════════════════════════════════════════════════
# NO ANTI-CORRUPTION COMMISSION — ART. 168-171 AUDITOR-GENERAL (weak real analogue)
# Maps to: constitution.py -> IIGConfig
# Research package: "The 1973 Constitution, as revived in 1985, contains no
# anti-corruption commission. The nearest constitutional integrity organ is
# the Auditor-General of Pakistan (Art. 168-171)." The NAB (1999) and
# Ehtesab Act (1997) both POST-DATE this instrument's life and must not be
# used. Unlike Thailand (constitutionally entrenched NACC) or Chile
# (Contraloría with ex ante veto), Pakistan genuinely has no comparable
# body — a low EFFECTIVENESS value here is textually defensible, not a
# reflexive copy of Myanmar's number (standing realism requirement,
# .claude/memory.md section 11).
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """Nearest real analogue: the Auditor-General of Pakistan (Art. 168-171)
    — a real but narrow, retrospective FINANCIAL audit mandate, not an
    investigative/prosecutorial anti-corruption body."""

    ENTRY_MERIT: float = 0.0
    ACADEMY_MONTHS: int = 0
    # GUESS, directionally grounded — set even higher than Myanmar's 0.90
    # because the Auditor-General has no investigative/prosecutorial
    # function at all (Myanmar's military intelligence apparatus at least
    # nominally investigates regime-threatening corruption; Pakistan's AGP
    # only audits and reports).
    INVESTIGATION_TRIGGER: float = 0.95
    # GUESS, directionally grounded per research package's explicit
    # recommendation: "this scenario genuinely resembles C on the
    # anti-corruption axis... a very low INITIAL_EFFECTIVENESS is
    # defensible from the text (no body exists) rather than assumed."
    # Set slightly BELOW Myanmar's 0.05 floor, reflecting that Pakistan's
    # real institution is textually weaker still (no regime-protection
    # apparatus either — see ANTI_CORRUPTION_OBJECTIVE below).
    EFFECTIVENESS_FLOOR: float = 0.03
    # CONFIDENT — Art. 171: Auditor-General's reports are laid before the
    # National Assembly via the President.
    REPORTS_TO: str = "president"
    CHAMBER_ELIGIBLE: bool = False

    # CONFIDENT — research package's explicit correction: "ANTI_CORRUPTION_
    # OBJECTIVE: False is too strong — the Auditor-General has a real audit
    # mandate; prefer a low effectiveness with a real mandate rather than an
    # inverted objective." Do NOT set this False by reflex-copying Myanmar.
    ANTI_CORRUPTION_OBJECTIVE: bool = True
    # CONFIDENT by absence — the Auditor-General has no documented regime-
    # protection mandate (contrast Myanmar's military intelligence REGIME_
    # PROTECTION_OBJECTIVE = True).
    REGIME_PROTECTION_OBJECTIVE: bool = False

    INITIAL_EFFECTIVENESS: float = 0.03
    # GUESS, directionally grounded — allowed a slightly higher ceiling
    # than Myanmar's 0.15, since the AGP's reports genuinely are laid
    # before the legislature (a real, if weak, transparency channel),
    # unlike Myanmar's purely internal military-intelligence reporting.
    MAX_EFFECTIVENESS: float = 0.20

    ENTRY_MERIT_MIN: float = 0.0
    ENTRY_MIN_AGE: int = 25               # GUESS — no citation
    ACADEMY_DURATION_MONTHS: int = 0
    # GUESS — real-world AGP tenure is a civil-service-style fixed
    # appointment (not political reappointment); no precise figure is in
    # the research package.
    DIRECTOR_TERM: int = 4
    DIRECTOR_RENEWABLE: bool = False
    PARTNER_ELIGIBILITY_YEARS: int = 0
    OPEN_INVESTIGATION_THRESHOLD: float = 0.95     # collapsed to INVESTIGATION_TRIGGER — no graduated due-process structure documented
    PROCEED_PROSECUTION_THRESHOLD: float = 0.95
    PARTNERSHIP_COUNCIL_QUORUM: float = 1.0
    # CONFIDENT direction — follows from MILITARY_SEAT_PERCENTAGE = 0.0
    # (ChamberConfig): there is no military-nominated-seat pathway for a
    # former intelligence/audit officer to move into, unlike Myanmar.
    CHAMBER_ELIGIBLE_POST_SERVICE: bool = False
    PERMITTED_POST_SERVICE: Tuple[str, ...] = (
        "civil_service_continuation",
    )
    # GUESS, directionally grounded — the AGP's office is a modest formal
    # audit bureaucracy, not a sprawling surveillance apparatus (contrast
    # Myanmar's military intelligence MAX_AGENTS = 2000).
    MAX_AGENTS: int = 300
    FUNCTIONAL_DIVISIONS: Tuple[str, ...] = (
        "federal_audit",
        "provincial_audit",
        "defence_services_audit",
    )
    MANDATE_DIVISIONS: Tuple[str, ...] = (
        "financial_accountability_mandate",
    )
    OPERATIONAL_DIVISIONS: Tuple[str, ...] = (
        "field_audit_operations",
    )


# ══════════════════════════════════════════════════════════════════════════════
# ART. 141-161, 232-234 — FEDERAL STRUCTURE
# Maps to: constitution.py -> FederalConfig
# Pakistan is GENUINELY federal, unlike the South Korea/Thailand/Germany-at-
# 1949 comparisons — Art. 160-161 (National Finance Commission; well-head
# royalties to the producing province) is real, codified revenue sharing.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Art. 141-161 — federal/provincial structure and resource sharing."""

    STATE_COUNT: int = 4   # CONFIDENT (4 provinces) — but see FoundationalConfig's decorative-field caveat
    # GUESS, directionally grounded — Pakistan's constitution does not
    # codify "ethnic groups" as a category (research package L8: the
    # minority structure is religious, not ethnic). This proxy reflects
    # mother-tongue/ethno-linguistic community shares as a Ka-Nova
    # modelling convenience, not a constitutional citation.
    #
    # RAISED 4 -> 6, 2026-10-20 (research package
    # config/constitution_pakistan_encoding/README.md section 6.3,
    # confirmed decision, not an open question). A 4-group encoding
    # (punjabi/pashtun/sindhi/baloch) drops two groups that are centrally
    # important to THIS encoded window:
    #   - Urdu-speaking Muhajirs, 7.60% national share (1981 PBS census
    #     mother-tongue table). The MQM was founded 18 March 1984, one
    #     year before year zero; it swept Karachi/Hyderabad in the 1987
    #     local-body and 1988 general elections; Karachi's ethnic violence
    #     (Apr 1985 Bushra Zaidi riots, Dec 1986 Sohrab Goth/Aligarh Colony
    #     killings, 1992 Operation Clean-up, 1995 peak) is arguably the
    #     central internal-security story of this instrument's life.
    #   - Saraikis, 9.84% national share (1981 PBS census), larger than
    #     Balochi (3.02%, which WAS already in the 4-group list) — second-
    #     largest group in Punjab, basis of the South Punjab province
    #     movement.
    # New 6-slot group list and order (CONFIDENT on the real shares cited
    # above, GUESS on treating this specific list as the canonical Ka-Nova
    # "ethnic_weights" axis, same modelling-convenience caveat as before):
    #   index 0 = punjabi        (48.17% national, 1981 PBS)
    #   index 1 = pashtun        (13.15%, "Pashto" in the census)
    #   index 2 = sindhi         (11.77%)
    #   index 3 = saraiki        (9.84%)
    #   index 4 = urdu_muhajir   (7.60%, "Urdu" in the census)
    #   index 5 = baloch         (3.02%, "Balochi" in the census)
    # Hindko (2.43%) + Brahui (1.21%) + other (~2.81%) remain an
    # unmodelled residual (~6.45% nationally), documented rather than
    # silently dropped — same honesty convention as the rest of this file.
    ETHNIC_GROUPS: int = 6

    # GUESS, flagged per research package flag F5 — "Pakistan is a real
    # federation, so do not reuse MFU's 35/35/30 [or Myanmar's 10/65/25]
    # split. Either source the 1985-era NFC award percentages or label the
    # split a proxy." The exact 1985-era National Finance Commission award
    # percentages are NOT in the research package; this trio is a DOCUMENTED
    # PROXY, directionally informed by Art. 160-161's real principle
    # (provinces receive a genuine constitutionally-anchored revenue share,
    # unlike Myanmar's Art. 37(a) pure-Union-ownership model) but not the
    # real historical award figures. Flagged to senior-data-analyst: source
    # the actual 1985-1991 NFC award before this trio is treated as a
    # headline comparative number in the paper.
    RESOURCE_STATE_SHARE: float = 0.30
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.50
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.20

    GINI_THRESHOLD: float = 0.50     # GUESS — no citation, Ka-Nova convention
    STATE_GDP_CAP: float = 0.80      # GUESS — reused convention, no citation

    # CONFIDENT direction — Pakistan's provincial-executive mechanism runs
    # through PRESIDENTIALLY-APPOINTED GOVERNORS (Art. 101, "after
    # consultation with the Prime Minister" per 8th Amdt s.11) who hold a
    # 58(2)(b)-identical provincial dissolution power (Art. 105/112), not
    # through a literal reserved military seat in the provincial executive
    # the way Myanmar's Section 17(b) works. Real structural difference,
    # set False rather than copying Myanmar's True.
    MILITARY_IN_REGIONAL_EXECUTIVE: bool = False

    SECTOR_MONOPOLY_CAP: float = 1.00   # GUESS — reused "no effective cap" convention

    # GUESS — Pakistan has no MFU-style Article VIII "virtuous cycle" trust-
    # acceleration safeguard either (same absence as Myanmar). Nullified via
    # parameter value, same idiom constitution_2008.py uses, not a sourced
    # constitutional figure.
    TRUST_ACCELERATION_TRIGGER_CORRUPTION: float = 0.0
    TRUST_ACCELERATION_TRIGGER_YEARS: int = 99
    TRUST_ACCELERATION_MULTIPLIER: float = 1.00


# ══════════════════════════════════════════════════════════════════════════════
# ART. 243-245 — DEFENCE SERVICES
# Maps to: constitution.py -> MilitaryConfig
# THE HEART OF THE NEAR-TWIN CLAIM. KEY DIFFERENCE FROM MYANMAR 2008: no
# constitutional coup mechanism exists (COUP_LEGAL_MECHANISM = False).
# Pakistan's guardianship runs through the presidency and the immunity
# clauses (Art. 48(2), Art. 58(2)(b), Art. 270A), NOT through a
# constitutionally-authorised self-coup clause the way Myanmar s.40(c)/
# 417-419 works, and NOT through reserved parliamentary seats.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Art. 243-245 — Defence Services, command, and (the absence of) a
    constitutional coup mechanism."""

    # CONFIDENT — research package, explicit: "No constitutional coup
    # mechanism. There is no Pakistani equivalent of Myanmar 2008
    # ss.40(c)/417-419... Pakistan's 1999 collapse came from an
    # extra-constitutional coup, not from a clause." THIS is the single
    # most important distinguishing value from constitution_2008.py.
    COUP_LEGAL_MECHANISM: bool = False
    # CONFIDENT, cross-checked against the live rule-based engine's own
    # hardcoded fallback thresholds (engine/elite_agents_v3.py:
    # COUP_CORRUPTION_TRIGGER = 0.65, COUP_TRUST_TRIGGER = 0.30 — identical
    # numbers used for every scenario's rule-based elite_coup_signal check).
    # Also matches the real V-Dem trajectory: Pakistan's 1985 political-
    # corruption reading (0.637) is already within reach of 0.65 and crosses
    # it by 1988 (V-Dem 0.731), staying pinned at 0.831 from 1990 onward.
    COUP_TRIGGER_CORRUPTION: float = 0.65
    COUP_TRIGGER_TRUST: float = 0.30

    # CONFIDENT direction, per research package flag F4 point 3 — do NOT
    # state the President had discretionary control of service-chief
    # appointment under the 1985 instrument ("in his discretion" only
    # entered Art. 243 via LFO 2002). Formally, appointment under Art.
    # 243(2)(c) runs subject to Art. 48(1) advice.
    COMMANDER_IN_CHIEF_APPOINTMENT: str = "president_art243_2c_subject_to_art48_1_advice"
    # CONFIDENT — research package: "partial — Art. 199(3) and Art. 245(3)
    # exclude High Court jurisdiction in army-deployment areas, and the
    # Pakistan Army Act 1952... provides military trial of civilians in
    # defined cases. Encode True with the Art. 245(3) citation."
    MILITARY_SELF_ADJUDICATION: bool = True

    # CONFIDENT — Art. 243(1): Federal Government control/command; Art.
    # 243(1A), inserted by the RCO 1985: Supreme Command vests in the
    # President. A single, unified chain of command.
    SINGLE_CHAIN_OF_COMMAND: bool = True

    # CONFIDENT on the real embedding, GUESS on the exact mechanism label —
    # Pakistan's military IS genuinely embedded in politics under this
    # instrument, but through the presidency/immunity clauses (and, in
    # 1985-1988, Zia's own dual-hatting as President AND Chief of Army
    # Staff), NOT through a named constitutional political-role clause the
    # way Myanmar's Section 6(f)/20(e) works.
    MILITARY_POLITICAL_ROLE: bool = True

    # CONFIDENT — research package's central finding, mirrors ChamberConfig.
    PARLIAMENTARY_SEAT_PERCENTAGE: float = 0.0
    PARLIAMENTARY_SEAT_APPOINTMENT: str = "not_applicable_zero_reserved_seats"

    # GUESS — NOT mechanically read anywhere in the live engine (confirmed
    # by direct grep: LOYALTY_INITIAL/LOYALTY_CORRUPTION_DRAG/
    # COUP_PROBABILITY_MULTIPLIER are never referenced outside their own
    # definitions in either existing constitution file). Kept for schema
    # parity and documentation; values chosen for directional honesty
    # rather than mechanical effect: high initial cohesion (Zia was
    # simultaneously President and COAS 1985-88), faster corruption-driven
    # loyalty decay than Myanmar's 0.001 (Pakistan's military is NOT the
    # permanent regime the way Myanmar's is), and COUP_PROBABILITY_
    # MULTIPLIER = 1.0 rather than Myanmar's 0.0 — Pakistan's military is a
    # real, separate actor capable of turning against the sitting
    # government (and did, in 1977 and 1999), not an institution that IS
    # the regime by constitutional design.
    LOYALTY_INITIAL: float = 0.70
    LOYALTY_CORRUPTION_DRAG: float = 0.01
    COUP_PROBABILITY_MULTIPLIER: float = 1.00

    # CONFIDENT — Art. 245(1): Armed Forces act "in aid of civil power when
    # called upon to do so" under Federal Government direction.
    DOMESTIC_FORCE_AUTHORIZED: bool = True
    DOMESTIC_FORCE_TRIGGER: str = "federal_government_direction_art245"

    # GUESS, intended as a Ka-Nova calibration lever — deliberately NOT
    # nullified the way Myanmar's COUP_TRIGGER_LOYALTY/APPROVAL are set to
    # 0.0 ("the military IS the regime" framing does not apply to Pakistan:
    # COUP_LEGAL_MECHANISM = False above already establishes the military
    # is a separate, extra-constitutional actor here, exactly as the real
    # 1977 and 1999 coups were). Set at a moderate, reachable level — not
    # Myanmar's unreachable 0.0 — reflecting that Pakistan's real coup risk
    # was genuine and materialised twice within this instrument's broader
    # historical window.
    #
    # CALIBRATION FINDING, reported in full rather than silently accepted
    # (see this module's own task-level report for the complete writeup).
    # A clean 15-seed rule-based (no-LLM) sweep, 300 citizens, 50-year
    # horizon, found this encoding collapses with mean failure year 15.53
    # (stdev 0.88, range 15-18, 15/15 seeds collapsed) — closely matching
    # Scenario C's own locked simulated mean (15.6 years) and landing
    # roughly 1-1.6 years above the real 13.9-14.6-year Pakistan anchor.
    # On its face this is a good calibration result. BUT: direct
    # instrumentation during this encoding confirmed this field (COUP_
    # TRIGGER_LOYALTY/APPROVAL) is NOT actually being read from this file
    # by the live engine at all — swapping it between 0.50/0.45, 0.60/0.55,
    # and 0.70/0.80 produced byte-identical trajectories every time, and
    # direct inspection showed `feedback/loops.py:37` imports
    # `from config.constitution import CONSTITUTION` (the MFU singleton) at
    # MODULE level rather than reading `model.CONSTITUTION`, so every
    # `CONSTITUTION.X.Y` read inside all 12 feedback loops — including THIS
    # field, read at loops.py:324-325 in loop_P3_coup_probability, plus
    # RightsConfig.RIGHTS_VIOLATION_TRUST_DROP (P1, line 136),
    # FederalConfig.TRUST_ACCELERATION_* (P1, lines 146-155),
    # MeritConfig.RECERTIFICATION_* (P4), FederalConfig.GINI_THRESHOLD/
    # STATE_GDP_CAP (E3), ScienceConfig.PHD_KNOWLEDGE_CAPITAL_BOOST/
    # RESEARCHER_ROYALTY_RATE (E4), and MilitaryConfig.NS_LOYALTY_BOOST/
    # NS_ETHNIC_EXPOSURE_BOOST (S1) — silently use MFU's values for EVERY
    # scenario, A/C/TH/PK alike, not this file's. (A second, independent
    # reason this specific field cannot fire as designed even once that
    # import is fixed: the P3 loop's `chancellor_approval` falls back to a
    # hardcoded 0.45 constant whenever no ChancellorAgent exists in the
    # population, which is the case for this military-chain scenario.)
    # Separately, `model_phase3.py._initialize_shared_data()` hardcodes
    # Year-Zero shared_data (corruption_index=0.72, trust_index=0.22,
    # coup_risk=0.25 — Myanmar's own numbers) instead of reading
    # `self.CONSTITUTION.simulation.YEAR_ZERO_*` for ANY scenario, so this
    # module's own YEAR_ZERO_CORRUPTION=0.637/YEAR_ZERO_COUP_RISK=0.086
    # are not the values the simulation actually starts from today either.
    # HONEST IMPLICATION: the good 15.53-year match is therefore NOT
    # evidence of successful Pakistan-specific calibration via this field —
    # it is better explained by Pakistan (chain_type="military") currently
    # sharing Myanmar's own hardcoded Year-Zero seed and MFU-sourced loop
    # parameters, combined with the one channel confirmed genuinely
    # chain_type-aware and not scenario-literal-gated (model_phase3.py's
    # elite_coup_signal nudge, +0.05/year once corruption_index > 0.65 AND
    # trust_index < 0.30 — both hardcoded module-level constants in
    # engine/elite_agents_v3.py, not constitution-driven, hence symmetric
    # by construction). This field is kept at a reasoned, real-world
    # -grounded level rather than re-tuned to chase a number the engine
    # cannot currently honour; once the import/seed bugs above are fixed,
    # this field should become the genuine, country-specific calibration
    # lever it was designed to be.
    COUP_TRIGGER_LOYALTY: float = 0.50
    COUP_TRIGGER_APPROVAL: float = 0.45

    # CONFIDENT direction (kept neutral, same as constitution_2008.py's own
    # comment) — a citizen-side sorting criterion, not itself constitution-
    # dependent.
    NS_CIVILIAN_TRACK_THRESHOLD: float = 0.65
    # CONFIDENT by absence — no national-service institution of any kind
    # exists under this instrument (stronger absence than even Myanmar's
    # weak-coerced version — mirrors RightsConfig.NATIONAL_SERVICE_
    # MANDATORY = False above). The engine's NS pipeline
    # (agents/citizen.py._begin_national_service, feedback/loops.py's S1
    # loop) runs unconditionally regardless of this flag — these boosts are
    # set to 0.0 so the pipeline is a structural no-op for Pakistan.
    NS_LOYALTY_BOOST: float = 0.0
    NS_ETHNIC_EXPOSURE_BOOST: float = 0.0
    NS_CIVIC_CONTRIBUTION_BOOST: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# ART. 18, 23-24, 29-40 — ECONOMIC PRINCIPLES OF POLICY
# Maps to: constitution.py -> EconomicConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Art. 29-40 Principles of Policy — explicitly NON-JUSTICIABLE (Art. 30(2))."""

    # GUESS label, CONFIDENT underlying fact — Art. 38 Principles of Policy
    # (social/economic well-being, elimination of riba "as early as
    # possible") exist but Art. 30(2) makes the whole chapter
    # non-justiciable: "The validity of an action or of a law shall not be
    # called in question on the ground that it is not in accordance with
    # the Principles of Policy."
    ECONOMIC_SYSTEM: str = "mixed_economy_principles_of_policy_non_justiciable_art30_2"

    TAX_BRACKETS: Tuple[float, ...] = (0.0, 0.05, 0.10, 0.20, 0.30)   # GUESS proxy
    BLACK_MONEY_PENALTY: str = "law_prescribed"    # GUESS — no specific citation

    # GUESS, directionally informed — Art. 161's well-head-royalty-to-
    # producing-province mechanism implies real provincial resource
    # interests, a genuine difference from Myanmar's centralised Art. 37(a)
    # pure-Union-resource-ownership model. Set False rather than copying
    # Myanmar's True by reflex.
    STATE_OWNS_RESOURCES: bool = False
    PRIVATE_PROPERTY_PROTECTED: bool = True    # CONFIDENT — Art. 23-24

    ANTI_MONOPOLY: bool = True                 # GUESS — Art. 18 freedom-of-trade framing, not specifically anti-monopoly-cited
    CRONYISM_ENABLED: bool = True              # GUESS, Ka-Nova parameter — well-documented real military-business patronage, not package-sourced

    # GUESS, factually notable — Pakistan has a REAL history of major
    # nationalisations (1972 industry/bank nationalisation under Bhutto),
    # the OPPOSITE of Myanmar's Art. 36(d) anti-nationalisation clause. Not
    # in the research package's scope (pre-dates the 1985 instrument) but
    # worth flagging as a genuine comparative difference for the paper.
    NATIONALIZATION_BANNED: bool = False

    CORRUPTION_GDP_DRAG: float = 0.03          # GUESS — reused convention
    # GUESS, directionally grounded — lower than Myanmar's 0.40: Pakistan's
    # military-business empire (Fauji Foundation, Army Welfare Trust, etc.)
    # is real and well-documented in the secondary literature but was less
    # totalising within this instrument's 1985-1999 window than Myanmar's
    # SPDC-era crony economy. Not in the research package's scope.
    CRONY_CAPITAL_SHARE: float = 0.25

    STRATEGIC_SECTORS: Tuple[str, ...] = (
        "natural_resources", "defence", "media", "banking",
    )
    OPEN_SECTORS: Tuple[str, ...] = (
        "manufacturing", "textiles", "retail", "agriculture_non_resource",
    )
    FOREIGN_CAP_STRATEGIC: float = 0.35   # GUESS
    FOREIGN_CAP_OPEN: float = 1.00        # GUESS


# ══════════════════════════════════════════════════════════════════════════════
# ART. 37(b)-(c) — EDUCATION; NO PhD-ECONOMY ANALOGUE
# Maps to: constitution.py -> ScienceConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Art. 37(b)-(c) education provisions — no PhD-economy or researcher
    royalty analogue (research package explicit: "No PhD-economy
    analogue → PHD_TUITION_FREE: False, RESEARCHER_ROYALTY_RATE: 0.0")."""

    PHD_TUITION_FREE: bool = False
    RESEARCHER_ROYALTY: float = 0.0
    KNOWLEDGE_CAPITAL_GROWTH: float = 0.005    # GUESS — reused convention

    # CONFIDENT on the real ideological character, GUESS on reusing this
    # specific boolean for it — Pakistan's education framing is
    # IDEOLOGICAL/ISLAMIC (Art. 2A Objectives Resolution; Art. 31 "Islamic
    # way of life"), not NATIONALIST the way Myanmar's Art. 28(d) "building
    # the Nation" framing is. Kept True with this comment distinguishing
    # the real mechanism from Myanmar's.
    EDUCATION_NATIONALIST_FRAMING: bool = True

    BRAIN_DRAIN_RATE_BASE: float = 0.12   # GUESS — slightly below Myanmar's 0.15
    ACADEMIC_FREEDOM: float = 0.25        # GUESS — slightly above Myanmar's 0.20

    RESEARCHER_ROYALTY_RATE: float = 0.0        # CONFIDENT — mirrors RESEARCHER_ROYALTY above
    PHD_KNOWLEDGE_CAPITAL_BOOST: float = 0.05   # GUESS — reused convention


# ══════════════════════════════════════════════════════════════════════════════
# ART. 238-239 — AMENDMENT OF THE CONSTITUTION
# Maps to: constitution.py -> AmendmentConfig
# KEY: 2/3 + 2/3 and NOTHING ELSE — no referendum, no eternity clause,
# materially easier than Myanmar (75%+referendum), Thailand, or South Korea.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Art. 238-239 — amendment by Act of Majlis-e-Shoora."""

    # GUESS — Art. 239 does not document a separate "initiation" percentage
    # distinct from the passage threshold (unlike Myanmar's explicit 20%
    # initiation bar under Section 435); reused the real passage figure for
    # schema-parity rather than inventing a distinct number.
    AMENDMENT_INITIATION_THRESHOLD: float = 0.667

    # CONFIDENT — research package, explicit and verbatim: "Pakistan's
    # amendment rule is 2/3 + 2/3 and nothing else." Art. 239(1)-(3): not
    # less than two-thirds of the total membership of the originating
    # House, then two-thirds of the total membership of the other House.
    ENTRENCHED_AMENDMENT_THRESHOLD: float = 0.667
    STANDARD_AMENDMENT_THRESHOLD: float = 0.667
    # CONFIDENT — "No referendum requirement. No eternity clause."
    ENTRENCHED_REQUIRES_REFERENDUM: bool = False

    # CONFIDENT direction — follows from MILITARY_SEAT_PERCENTAGE = 0.0:
    # there is no reserved bloc large enough to structurally veto an
    # amendment, unlike Myanmar's 25%-seat-driven veto.
    MILITARY_VETO_ON_AMENDMENTS: bool = False

    # CONFIDENT on the one real distinguishing category Art. 239 provides —
    # Art. 239(4): an amendment altering the limits of a province
    # additionally requires two-thirds of the total membership of that
    # Provincial Assembly. Pakistan, UNLIKE Myanmar's Section 436(a) vs (b)
    # split, does NOT otherwise distinguish "core" from "non-core" articles
    # — both standard and entrenched thresholds above are identical (0.667).
    ENTRENCHED_CHAPTERS: Tuple[str, ...] = (
        "provincial_boundary_alteration_art239_4",
    )
    REVIEW_INTERVAL: int = 0   # CONFIDENT by absence — no mandatory review cycle
    CITIZENS_ASSEMBLY_SIZE: int = 320   # GUESS/schema-parity — no real civic-lottery mechanism exists, same reasoning constitution_2008.py gives

    # ─── EXTRA field, NOT part of the confirmed 86-field engine contract ───
    # CONFIDENT — Eighth Amendment s.20: a new Seventh Schedule listing
    # President's Orders and Ordinances that "may be amended in the manner
    # provided for amendment of the Constitution" — i.e. Zia's own decrees
    # were given constitutional-amendment-level entrenchment. No MFU/
    # Myanmar analogue; documented per research package's explicit request,
    # not read by the live engine today.
    SEVENTH_SCHEDULE_ENTRENCHMENT: bool = True   # EXTRA


# ══════════════════════════════════════════════════════════════════════════════
# ART. 270A — THE BROADEST IMMUNITY CLAUSE IN THE FIVE-COUNTRY SET
# Maps to: constitution.py -> TransitionConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """Art. 270A as substituted by Eighth Amendment s.19 — affirms,
    validates, and immunises eight years (1977-1985) of martial law."""

    TRANSITION_PERIOD_YEARS: int = 0    # CONFIDENT — immediate, no transition period specified
    # CONFIDENT — Art. 270A(1): the 5 July 1977 Proclamation, all
    # President's Orders/Ordinances/Martial Law Regulations/Orders
    # (including the Referendum Order 1984, the RCO 1985 itself, and the
    # Second/Third Amendment Orders 1985) are "affirmed, adopted and
    # declared... to have been validly made" notwithstanding any court
    # judgment.
    AMNESTY_GRANTED: bool = True
    PRIOR_LAWS_VALID: bool = True
    # CONFIDENT — Art. 270A(2)/(4): all orders/proceedings/acts in that
    # period are deemed always to have been validly made, and "no suit,
    # prosecution or other legal proceedings shall lie in any Court against
    # any authority or any person" for anything done under those powers.
    PRIOR_ACTIONS_IMMUNE: bool = True

    CIVIL_SERVANTS_RETAIN_POSTS: bool = True   # GUESS — reasonable continuity assumption, not specifically cited for Pakistan

    # GUESS — this field name is Myanmar-specific terminology ("Tatmadaw")
    # reused generically by the live engine for "outgoing-regime pension/
    # incentive." Not applicable to Pakistan's 1985 instrument in the same
    # sense: this was a CONTINUOUS martial-law-into-constitutional-order
    # transition (RCO reviving the 1973 text under the SAME ruler), not an
    # exiting-junta handover to a genuinely new civilian government the way
    # Myanmar 2008-2011 was. Set to 0.0 — no transition-pension mechanism is
    # documented.
    TATMADAW_PENSION: float = 0.0
    # CONFIDENT — Art. 270A grants the BROADEST immunity of the three-
    # country military-guardianship set. Research package's own comparative
    # framing: "Myanmar 2008 s.445 immunises past SPDC/SLORC acts; Thailand
    # 2017 s.279 immunises past AND future NCPO orders; Pakistan Art. 270A
    # immunises eight years of martial law AND deems it all good-faith AND
    # bars any proceedings against any person. Art. 270A is the strongest
    # of the three."
    TATMADAW_IMMUNITY: bool = True

    # ─── EXTRA field, NOT part of the confirmed 86-field engine contract ───
    # CONFIDENT — research package's exact suggested string, Art. 270A(5):
    # "All such acts shall be deemed to have been made, taken or done in
    # good faith."
    IMMUNITY_SCOPE: str = "retrospective_and_deemed_good_faith_no_proceedings"   # EXTRA


# ══════════════════════════════════════════════════════════════════════════════
# NO MFU-STYLE SAFEGUARDS — THE REAL "SAFEGUARD" HERE PROTECTS THE PRESIDENT
# FROM REVIEW, NOT THE CITIZEN FROM THE STATE
# Maps to: constitution.py -> SafeguardConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """All MFU-style accountability safeguards absent; the instrument's own
    real 'safeguards' (non-justiciability clauses) protect the executive,
    not the citizen."""

    CHANCELLOR_COOLING_OFF_ENFORCED: bool = False
    MERIT_EXAM_INDEPENDENCE: bool = False
    ETHNIC_COUNCIL_YOUTH_MANDATE: bool = False
    IIG_SINGLE_TERM: bool = False
    ANALYSIS_TRANSPARENCY: bool = False
    RIGHTS_ABSOLUTE: bool = False                 # CONFIDENT — Art. 233 rights are suspendable
    GENERATIONAL_ASSEMBLY_REVIEW: bool = False

    # CONFIDENT — a KEY difference from Myanmar: zero reserved military
    # seats (research package's central finding).
    MILITARY_SEAT_RESERVATION: bool = False
    # CONFIDENT by absence — COUP_LEGAL_MECHANISM = False above; there is
    # no constitutional coup-veto mechanism analogous to Myanmar's implicit one.
    COMMANDER_IN_CHIEF_VETO: bool = False
    # CONFIDENT — research package flag F4 point 2, a well-documented
    # correction to standard secondary literature: "The Eighth Amendment
    # created a National Security Council" is FALSE — Eighth Amendment s.18
    # OMITTED Art. 152-A (the NSC article). No COSENA-style oversight organ
    # exists under this instrument at all.
    NDSC_OVERSIGHT: bool = False

    ANALYSIS_PUBLISH_BEFORE_VETO_DAYS: int = 0   # CONFIDENT direction — follows from ANALYSIS_TRANSPARENCY = False

    # ─── EXTRA field, NOT part of the confirmed 86-field engine contract ───
    # CONFIDENT — the real functional "safeguard" of this instrument is
    # Art. 48(2)'s non-justiciability clause, which protects the
    # PRESIDENT's discretionary acts from review — the inverse of an MFU-
    # style citizen safeguard. Documented per the standing realism
    # requirement; not read by the live engine today.
    PRESIDENTIAL_DISCRETION_NON_JUSTICIABLE: bool = True   # EXTRA — Art. 48(2)


# ══════════════════════════════════════════════════════════════════════════════
# NO CRYPTOGRAPHIC JUSTICE — NO PAKISTANI REFERENT (research package L8)
# Maps to: constitution.py -> CryptoJusticeConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """No Pakistani referent — absent pattern, same as constitution_2008.py."""

    BLOCKCHAIN_ENABLED: bool = False
    ZKP_ENABLED: bool = False
    MULTI_PARTY_SIGNATURES: bool = False
    TOTAL_RUIN_MECHANISM: bool = False
    TOTAL_RUIN_STEPS: int = 0

    COURT_SUPERMAJORITY_FOR_TOTAL_RUIN: int = 8   # GUESS — equals JUDGE_COUNT (8 of 8), unreachable idiom, mechanism absent
    SHAME_REGISTER_CORRUPTION_REDUCTION: float = 0.0   # CONFIDENT — no Shame Register exists


# ══════════════════════════════════════════════════════════════════════════════
# ART. 232-237 — PROVISIONS ON STATE OF EMERGENCY
# Maps to: constitution.py -> EmergencyConfig
# KEY DIFFERENCE FROM MYANMAR 2008: NO total-sovereign-power-transfer clause.
# The real functional "emergency" mechanism in THIS instrument is Art.
# 58(2)(b) (modelled in ExecutiveConfig/MilitaryConfig above), not Chapter
# X/Art. 232-237. L3 CAVEAT (research package): the 1985-era Art. 232 text
# had NO provincial-resolution / 10-day-parliamentary-approval precondition
# — those were inserted by the 18th Amendment in 2010. Encoding from a
# current consolidated text would UNDERSTATE presidential power here.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Art. 232-237 — Proclamation of Emergency (1985-era text, pre-2010
    amendments, per research package flag L3)."""

    # CONFIDENT — Art. 232(1), 1985-era text: the President's own
    # satisfaction that a grave emergency exists (war, external aggression,
    # or internal disturbance beyond provincial control) is SUFFICIENT — no
    # provincial-resolution or parliamentary-approval precondition existed
    # until the 18th Amendment (2010).
    TRIGGER_SCENARIOS: Tuple[str, ...] = (
        "grave_emergency_war_or_external_aggression",
        "internal_disturbance_beyond_provincial_control",
        "presidential_satisfaction_sole_trigger_pre_2010_text",
    )

    EMERGENCY_MAX_DAYS: int = 365          # GUESS — reused convention, no Pakistan-specific duration figure in the research package
    EMERGENCY_EXTENSIONS: int = 2          # GUESS — reused convention
    EMERGENCY_EXTENSION_MONTHS: int = 6    # GUESS — reused convention

    # CONFIDENT — Art. 233: rights CAN be restricted/suspended during an
    # emergency.
    RIGHTS_UNTOUCHED: bool = False

    # CONFIDENT — research package, explicit and central: "No total-power-
    # transfer-to-the-army clause." This is the single most important
    # EmergencyConfig difference from Myanmar 2008 (TOTAL_POWER_TRANSFER_
    # POSSIBLE = True there).
    TOTAL_POWER_TRANSFER_POSSIBLE: bool = False
    POWER_TRANSFER_TRIGGER: str = "not_applicable_no_total_transfer_clause"

    # CONFIDENT direction — follows directly from TOTAL_POWER_TRANSFER_
    # POSSIBLE = False above.
    COMMANDER_IN_CHIEF_LEGISLATIVE: bool = False
    COMMANDER_IN_CHIEF_EXECUTIVE: bool = False
    COMMANDER_IN_CHIEF_JUDICIAL: bool = False

    # CONFIDENT — research package, explicit: "LEGISLATURE_SUSPENDED_
    # DURING_EMERGENCY: False."
    LEGISLATURE_SUSPENDED_DURING_EMERGENCY: bool = False

    # GUESS, decorative/unused — NOT mechanically read anywhere in the live
    # engine (confirmed by direct grep). Pakistan's real failure channel is
    # Art. 58(2)(b) dissolution, not emergency-driven collapse — research
    # package: "The functional emergency mechanism in this instrument is
    # Art. 58(2)(b), not Chapter X." Set low to reflect that honestly even
    # though the field has no mechanical effect today.
    EMERGENCY_COUP_PROBABILITY_MULTIPLIER: float = 0.20

    # ─── EXTRA field, NOT part of the confirmed 86-field engine contract ───
    # CONFIDENT — Art. 233(2): the President may suspend the right to move
    # ANY court for enforcement of rights during an emergency — a
    # distinctly stronger mechanism than a bare rights-suspension clause.
    # Research package's own explicit recommended field name. Not read by
    # the live engine today (constitution_2008.py does not define this
    # field either), documented per the standing realism requirement.
    EMERGENCY_SUSPENDS_RIGHTS_ENFORCEMENT: bool = True   # EXTRA — Art. 233(2)


# ══════════════════════════════════════════════════════════════════════════════
# ART. 245(1) — RULES OF ENGAGEMENT
# Maps to: constitution.py -> ROEConfig
# Research package does not cover foreign-policy/ROE articles in detail —
# every field below except DOMESTIC_MILITARY_USE is GUESS.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """Art. 245(1) — Armed Forces act in aid of civil power under Federal
    Government direction. Foreign-policy articles not covered by the
    research package; flagged GUESS throughout except where noted."""

    FOREIGN_POLICY: str = "non_aligned_with_cold_war_era_western_alignment"   # GUESS — not covered by research package
    NO_AGGRESSION: bool = True       # GUESS — reused convention
    NO_FOREIGN_TROOPS: bool = True   # GUESS — reused convention

    # CONFIDENT — Art. 245(1): Armed Forces "defend Pakistan and, subject to
    # law, act in aid of civil power when called upon to do so"; Art.
    # 245(2): the validity of any Federal Government direction under this
    # clause "shall not be called in question in any court."
    DOMESTIC_MILITARY_USE: str = "federal_government_direction_art245_aid_to_civil_power"
    DOMESTIC_FORCE_THRESHOLD: float = 0.05   # GUESS — reused convention

    EXTERNAL_ROE: str = "defensive_unless_declared_war"   # GUESS — reused convention
    EXTERNAL_FULL_FORCE: bool = False                      # GUESS — reused convention


# ══════════════════════════════════════════════════════════════════════════════
# NO PSYCHOLOGICAL HEALTH MANDATE — NO PAKISTANI REFERENT (research package L8)
# Maps to: constitution.py -> PsychConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """No Pakistani referent — absent pattern, same as constitution_2008.py."""

    BIANNUAL_SCREENING: bool = False
    ANTI_BIAS_REVIEW: bool = False
    TRAUMA_CARE_MANDATED: bool = False

    POPULATION_TRAUMA_BASE: float = 0.35      # GUESS — lower than Myanmar's 0.45, no citation either way
    TRAUMA_ACCUMULATION_RATE: float = 0.02    # GUESS — reused convention
    ETHNIC_TRAUMA_MULTIPLIER: float = 1.3     # GUESS — lower than Myanmar's 1.5, reflecting the religious-not-ethnic minority structure (L8)

    # GUESS — same "never triggers within the simulation horizon" idiom
    # constitution_2008.py uses, since the engine runs this pipeline
    # unconditionally regardless of scenario.
    SCREENING_INTERVAL_MONTHS: int = 9999
    SEVERE_PROBATION_MONTHS: int = 9999
    OUTCOME_STABLE_THRESHOLD: float = 0.40
    OUTCOME_SEVERE_THRESHOLD: float = 0.70
    STOP_CONSEQUENCE: str = "no_formal_consequence_mechanism_exists"
    TRAUMA_CATEGORIES: Tuple[str, ...] = (
        "warfare_conflict",
        "family_domestic_abuse",
        "educational_authoritarian",
        "environmental_displacement",
        "political_detention_or_exile",
    )
    TRAUMA_DISTORTION_RANGE: Tuple[float, float] = (0.15, 0.40)   # GUESS magnitude


# ══════════════════════════════════════════════════════════════════════════════
# ART. 2A + ART. 29-40 — OBJECTIVES RESOLUTION / PRINCIPLES OF POLICY
# Maps to: constitution.py -> NorthStarConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """The Objectives Resolution (Art. 2A, RCO 1985) and the non-justiciable
    Principles of Policy (Art. 29-40) are this instrument's stated national
    objectives — research package: 'PROGRESS_METRIC is a modelling choice.'"""

    # CONFIDENT on the citations, GUESS on the exact tuple wording.
    OBJECTIVES: Tuple[str, ...] = (
        "objectives_resolution_islamic_principles_art2a",
        "principles_of_policy_non_justiciable_art29_40",
        "federal_unity_and_territorial_integrity",
    )

    # CONFIDENT on the real embedding, GUESS on treating it as a named
    # "objective" the way Myanmar's Section 6(f) literally is — Pakistan's
    # military perpetuation is an EMERGENT effect of Art. 48(2)/58(2)(b)/
    # 243/270A working together, not a standalone constitutional objective
    # clause.
    MILITARY_POLITICAL_ROLE_PERPETUATED: bool = True

    PROGRESS_METRIC: str = "constitutional_stability_and_objectives_resolution_compliance"   # GUESS — research package's own framing
    # GUESS — the real instrument did not survive 50 years (it collapsed at
    # ~14.6 years); 0.0 states that honestly, same narrative point
    # constitution_2008.py's own TARGET_YEAR_50_PROGRESS = 0.0 makes.
    TARGET_YEAR_50_PROGRESS: float = 0.0

    PHD_COMPOUNDING_ENABLED: bool = False   # CONFIDENT direction — follows from ScienceConfig's no-PhD-economy framing
    KNOWLEDGE_CAPITAL_TARGET: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS — Scenario PK calibration
# Maps to: constitution.py -> SimulationConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Scenario PK simulation parameters."""

    SCENARIO: str = "PK"
    SCENARIO_NAME: str = "Pakistan_1973_Constitution_Eighth_Amendment_1985"
    # CONFIDENT — research package's exact recommended instrument label.
    CONSTITUTIONAL_FRAMEWORK: str = "1973_constitution_as_revived_1985_with_eighth_amendment"

    # CONFIDENT — V-Dem v16 political-corruption index, Pakistan, 1985 — a
    # REAL observation at the exact year zero (research package: "more than
    # can be said for C's 0.72").
    YEAR_ZERO_CORRUPTION: float = 0.637
    # GUESS, DERIVED NOT OBSERVED (research package L5: "There is no
    # trust-survey data for 1985-1996. The earliest WVS reading (1997
    # fieldwork) falls in year 12 of a 14-year instrument. Any Pakistani
    # year-zero trust value is therefore necessarily derived, not
    # observed."). This value is interpolated from the qualitative
    # magnitude of V-Dem's 1985 polyarchy (0.157) and liberal-democracy
    # (0.102) indices (both low) and the direction of WGI's earliest
    # available (1996) Political Stability reading (-1.13) — a modelling
    # estimate, not a citation. Flagged for senior-data-analyst before
    # publication, same honesty standard the research package itself applies.
    YEAR_ZERO_TRUST: float = 0.25
    # GUESS, NOT sourced in the research package (which names "Pakistan
    # HIES/World Bank, earliest usable ~1987" without giving the figure).
    # Flagged for senior-data-analyst to source the exact HIES-1987 value
    # before this is treated as a headline number.
    YEAR_ZERO_GINI: float = 0.33
    YEAR_ZERO_EMPLOYMENT: float = 0.58            # GUESS — reused convention, not covered by the research package
    YEAR_ZERO_ETHNIC_TENSION: float = 0.45        # GUESS — lower than Myanmar's 0.68; Pakistan's minority structure is religious not ethnic (L8)
    # CONFIDENT, researcher's own computation — "3 successful coups in the
    # 35 years 1950-1985 ≈ 0.086/yr" (Powell & Thyne). Deliberately far
    # below Myanmar's 0.25 seed, reflecting that this instrument's real
    # coup risk was a genuine but non-constant background rate, not an
    # ever-present structural fact.
    YEAR_ZERO_COUP_RISK: float = 0.086
    # GUESS, DERIVED NOT OBSERVED (research package: "WGI begins 1996
    # (-1.13); no 1985 observation") — same derivation/flagging status as
    # YEAR_ZERO_TRUST above.
    YEAR_ZERO_STABILITY: float = 0.20

    # CONFIDENT direction — a DELIBERATE, REASONED divergence from
    # constitution_2008.py's True/True/True, not a reflexive copy (standing
    # realism requirement, .claude/memory.md section 11). Pakistan's
    # guardianship under this instrument ran through the PRESIDENCY and the
    # immunity/jurisdiction-stripping clauses, NOT through a permanent,
    # constitutionally-structural military institution controlling all
    # three branches as a standing fact the way Myanmar's 25% reserved
    # seats + NDSC do. The President was only sometimes also the Army Chief
    # (Zia, 1985-88); Presidents Ghulam Ishaq Khan (1988-93) and Farooq
    # Leghari (1993-97) were civilians. Research package: "Pakistan's
    # military influence under this instrument runs through the presidency,
    # the non-justiciability clauses and Art. 270A immunity — not through
    # reserved seats" and "the Eighth Amendment deleted a constitutional
    # National Security Council while simultaneously creating 58(2)(b) and
    # Art. 270A. Pakistan's military guardianship was built into the
    # presidency and the immunity clauses, not into a COSENA-style organ."
    MILITARY_CONTROLS_LEGISLATURE: bool = False
    MILITARY_CONTROLS_EXECUTIVE: bool = False
    MILITARY_CONTROLS_JUDICIARY: bool = False
    RIGHTS_ENFORCEABLE: bool = False   # CONFIDENT — Art. 233(2) suspends the right to move any court for rights enforcement

    # CONFIDENT — locked Monte Carlo design constants, identical across all
    # scenarios (not constitution-driven), same reasoning constitution_2008.py gives.
    CITIZEN_AGENTS: int = 11_000
    TIME_STEPS: int = 50

    # CONFIDENT on the real administrative units (Art. 1), AND NOW LIVE
    # (updated 2026-10-20): model_phase3.py's _initialize_states() and
    # agents/citizen.py's CitizenPopulation._assign_state()/
    # _assign_ethnicity() were generalized in a parallel pass tonight to
    # read SIMULATION_STATES/STATE_POPULATION_WEIGHTS/STATE_ETHNIC_WEIGHTS
    # directly from the active constitution instead of Myanmar's hardcoded
    # 14-name list — confirmed by direct read of both files (see their own
    # docstrings/comments at the call sites). The earlier "DECORATIVE"
    # characterization of this field no longer holds; superseded here
    # rather than left to silently mislead. Six units: 4 constitutional
    # provinces (the Senate's Art. 59 provincial-parity rule genuinely
    # applies to these 4, not 6 — see FoundationalConfig/FederalConfig.
    # STATE_COUNT=4) plus 2 federally administered territories with no
    # Senate representation (ICT, FATA).
    #
    # CORRECTION (research package section 6.2, confirmed decision):
    # `khyber_pakhtunkhwa` renamed to `nwfp`. The province was called
    # North-West Frontier Province for this instrument's entire 1985-1999
    # life; "Khyber Pakhtunkhwa" is anachronistic for this window — the
    # renaming only happened via the Eighteenth Amendment, assented 19
    # April 2010, eleven years after this instrument's 1999 collapse.
    SIMULATION_STATES: Tuple[str, ...] = (
        "punjab", "sindh", "nwfp", "balochistan",
        "islamabad_capital_territory", "federally_administered_tribal_areas",
    )

    # CONFIDENT — 1981 Population Census (Pakistan Bureau of Statistics),
    # per-province figures via citypopulation.de (accessed 2026-10-20),
    # research package section 6.2. This is the census legally in force at
    # year zero (1985); used here for SHARES (the 1985 national TOTAL used
    # elsewhere in this file, e.g. for a real citizen-count derivation, is
    # the separate World Bank WDI SP.POP.TOTL figure — see research
    # package's own L3 note on why these two series are mixed deliberately
    # rather than reconciled). NWFP-proper (excl. FATA) = 13,259,875
    # (Khyber Pakhtunkhwa incl. FATA, citypopulation.de) minus FATA's own
    # confirmed 2,198,547 = 11,061,328 — CONFIDENT components, DERIVED
    # (not directly published) split, research package flag L1.
    #   punjab                              47,292,441  56.13%
    #   sindh                               19,028,666  22.58%
    #   nwfp (excl. FATA)                   11,061,328  13.13%
    #   balochistan                          4,332,376   5.14%
    #   fata                                 2,198,547   2.61%
    #   islamabad_capital_territory            340,286   0.40%
    #   total                               84,253,644 100.00%
    # Order matches SIMULATION_STATES above exactly (same length, same
    # order) — used ONLY to distribute the uniform 11,000-citizen
    # simulated population across states (locked Monte Carlo design,
    # .claude/memory.md section 8), never to change CITIZEN_AGENTS itself.
    STATE_POPULATION_WEIGHTS: Tuple[float, ...] = (
        0.5613, 0.2258, 0.1313, 0.0514,
        0.0040, 0.0261,
    )

    # STATE_ETHNIC_WEIGHTS: per-province composition over the 6-slot
    # ethnic/mother-tongue axis defined at FederalConfig.ETHNIC_GROUPS
    # above — index order [punjabi, pashtun, sindhi, saraiki,
    # urdu_muhajir, baloch], identical order to this file's
    # STATE_ETHNIC_WEIGHTS_DEFAULT below. Need not sum to 1.0 (random.
    # choices normalizes; agents/citizen.py's _assign_ethnicity() contract).
    #
    # SOURCING STATUS (research package section 6.3/6.7 flag L2, stated
    # plainly rather than silently implied as census data): ONLY Punjab's
    # two entries below are CONFIDENT/directly sourced — "Punjab, 1981:
    # Punjabi 79%, Saraiki 14.9%" (PBS 1981 census; the 14.9%-Saraiki-in-
    # Punjab figure is explicitly documented in the literature on the
    # 1981 census's new language categories). The research package could
    # NOT retrieve the PBS 1981 Census Report's own provincial mother-
    # tongue table for Sindh, NWFP, Balochistan, FATA or ICT online — "do
    # not let an engineer fill the Sindh/NWFP/Balochistan arrays from
    # [qualitative] descriptions and then cite them as census figures."
    # Every other entry below is tagged GUESS/INFERENCE: a directionally-
    # grounded numeric translation of the research package's own
    # qualitative structural description (section 6.3), NOT a census
    # citation. Remaining mass in each tuple (where weights don't sum to
    # ~1.0) represents the real, named-but-unmodelled residual (Hindko/
    # Brahui/other, ~6.45% nationally) — left out deliberately rather than
    # forced into one of the 6 tracked slots.
    STATE_ETHNIC_WEIGHTS: Dict[str, Tuple[float, ...]] = field(default_factory=lambda: {
        # CONFIDENT (punjabi, saraiki) + GUESS (pashtun/sindhi/urdu_muhajir/
        # baloch residuals — urban in-migration to Punjab's cities, not
        # cited). Sourced pair sums to 93.9%, matching the research
        # package's own stated ~6.1% unaccounted residual for Punjab.
        "punjab":       (0.79, 0.01, 0.01, 0.149, 0.03, 0.01),
        # GUESS/INFERENCE throughout (L2: no provincial table retrieved).
        # Research package qualitative basis: "Sindhi-majority province-
        # wide, with a very large Urdu-speaking (Muhajir) concentration in
        # Karachi and Hyderabad and a significant Punjabi and Pashtun
        # presence in Karachi. The rural-Sindhi versus urban-Muhajir
        # division is the province's defining cleavage" — this is the
        # single array that makes the Karachi ethnic-violence mechanism
        # (research package section 6.5's ethnic_urban_violence shock)
        # work, and the whole reason ETHNIC_GROUPS was raised to 6.
        "sindh":        (0.05, 0.04, 0.55, 0.01, 0.33, 0.02),
        # GUESS/INFERENCE. Qualitative basis: "Pashto-majority, with a
        # Hindko-speaking minority concentrated in the Hazara division" —
        # the Hazara/Hindko minority is the unmodelled residual here
        # (~0.06 of this tuple's remaining mass), not one of the 6 slots.
        "nwfp":         (0.02, 0.88, 0.00, 0.01, 0.02, 0.01),
        # GUESS/INFERENCE. Qualitative basis: "Balochi-plurality (not
        # majority), with a large Pashtun population in the north (Quetta,
        # Zhob, Pishin) and a substantial Brahui-speaking population — the
        # province with the most genuinely contested ethnic arithmetic in
        # the country." Baloch deliberately kept a PLURALITY, not a
        # majority (per that direct instruction); the sizeable Brahui
        # population is the unmodelled residual (~0.18 of this tuple).
        "balochistan":  (0.01, 0.35, 0.00, 0.00, 0.01, 0.45),
        # GUESS/INFERENCE. Qualitative basis: "overwhelmingly Pashtun."
        "federally_administered_tribal_areas": (0.01, 0.95, 0.00, 0.00, 0.01, 0.01),
        # GUESS/INFERENCE. Qualitative basis: "Punjabi-majority with a
        # large Urdu-speaking administrative population; the least
        # ethnically-rooted unit" (federal civil-service capital, not an
        # organic regional population).
        "islamabad_capital_territory": (0.55, 0.10, 0.05, 0.05, 0.20, 0.03),
    })

    # STATE_ETHNIC_WEIGHTS_DEFAULT: national 1981 PBS mother-tongue shares
    # — CONFIDENT, directly sourced (research package section 6.3's
    # national table), same index order as STATE_ETHNIC_WEIGHTS above.
    # Used only as the fallback for any SIMULATION_STATES entry absent
    # from the dict above (none currently, all 6 are covered; kept for
    # schema parity with constitution.py's own convention and as a
    # genuinely meaningful national default rather than an arbitrary
    # placeholder).
    #   punjabi      48.17%   pashtun (Pashto)  13.15%
    #   sindhi       11.77%   saraiki            9.84%
    #   urdu_muhajir  7.60%   baloch (Balochi)   3.02%
    #   (unmodelled residual: Hindko 2.43% + Brahui 1.21% + other ~2.81%)
    STATE_ETHNIC_WEIGHTS_DEFAULT: Tuple[float, ...] = (
        0.4817, 0.1315, 0.1177, 0.0984, 0.0760, 0.0302,
    )
    # DELIBERATELY UNCHANGED from MFU/constitution_2008.py, not a guess by
    # omission — same reasoning constitution_2008.py's own comment gives:
    # changing the archetype distribution would be a NEW modelling decision
    # with large, hard-to-isolate effect-size consequences, orthogonal to
    # this encoding task. Flagged for Kaung/senior-researcher if a
    # Pakistan-specific archetype distribution is worth pursuing later.
    ARCHETYPES: Dict = field(default_factory=lambda: {
        "civic_champion": 0.15,
        "pragmatic_survivor": 0.30,
        "ethnic_loyalist": 0.20,
        "ambitious_meritocrat": 0.15,
        "disillusioned_youth": 0.10,
        "rural_traditionalist": 0.07,
        "trauma_carrier": 0.03,
    })
    CITIZENS_ASSEMBLY_SIZE: int = 320   # GUESS/schema-parity — no real civic-lottery mechanism exists


# ══════════════════════════════════════════════════════════════════════════════
# ELITE AGENT LAYER — country-accurate role titles + full system prompts
# Read by engine/elite_agents_v3.py's AGENT_DISPLAY_NAMES_BY_SCENARIO /
# SCENARIO_PROMPTS builders via getattr(CONSTITUTION_PAKISTAN,
# "ELITE_ROLE_TITLES"/"ELITE_SYSTEM_PROMPTS", None) — both dicts MUST be
# keyed by the SAME 7 role-function ids as CHAIN_ORDER_MILITARY in that
# file (general / crony_finance_minister / controlled_cb_governor /
# military_intel_chief / military_loyal_chief_justice / military_president
# / commander_in_chief), chain_type: "military".
#
# SCHEMA-FIT NOTE (flagged honestly, not forced): CHAIN_ORDER_MILITARY has
# exactly 7 slots and no slot literally named for a head-of-government
# distinct from the head-of-state (Myanmar has no PM at all, so the
# original 7-slot roster never needed one). Pakistan's research package
# names 8 real offices (President, Chief of Army Staff, Prime Minister,
# Speaker of the NA, Chairman of the Senate, Chief Justice of Pakistan,
# Chief Justice of the Federal Shariat Court, Auditor-General) — more than
# the schema has room for. The mapping below uses 6 of those 8 and
# DELIBERATELY REPURPOSES two role-function ids (NOT their literal label
# text, their underlying rule-based profile) to preserve BOTH the real
# President and the real Prime Minister, since Art. 58(2)(b)'s presidential
# dismissal power and Art. 91(5)'s "pleasure of the President" PM framing
# are exactly the two provisions this encoding exists to capture:
#   - "military_president" (rule-based profile: a budget-weight formula
#     explicitly commented "figurehead" in engine/elite_agents_v3.py) hosts
#     the PRIME MINISTER — a genuinely apt fit, since the PM is
#     constitutionally a figurehead relative to presidential power under
#     Art. 91(5)/58(2)(b), not a literal head-of-state renaming.
#   - "commander_in_chief" (the chain's apex-authority slot) hosts the
#     PRESIDENT — the instrument's actual apex civilian-but-military-tied
#     authority (Supreme Command, Art. 243(1A); discretionary dissolution,
#     Art. 58(2)(b); non-justiciable discretion, Art. 48(2)).
# The Speaker of the National Assembly, the Chairman of the Senate, the
# (ordinary) Chief Justice of Pakistan, and the Auditor-General do NOT fit
# any of the 7 slots without a similarly large repurposing and are
# DELIBERATELY NOT forced in — flagged in this task's final report rather
# than mapped onto a wrong-shaped slot.
# ══════════════════════════════════════════════════════════════════════════════

ELITE_ROLE_TITLES: Dict[str, str] = {
    "general":                      "Chief of Army Staff",
    "crony_finance_minister":       "Federal Minister for Finance",
    "controlled_cb_governor":       "Governor, State Bank of Pakistan",
    "military_intel_chief":         "Director-General, Inter-Services Intelligence (ISI)",
    "military_loyal_chief_justice": "Chief Justice of the Federal Shariat Court",
    "military_president":           "Prime Minister of Pakistan",
    "commander_in_chief":           "President of the Islamic Republic of Pakistan",
}


def _build_elite_system_prompts() -> Dict[str, str]:
    """
    Country-accurate system prompts for Pakistan's military-chain elite
    roster, grounded in this module's own field values (so the prompt text
    and the constitution object can never silently drift apart). Mirrors
    the exact structural idiom of engine/elite_agents_v3.py's
    `_build_system_prompts_military()` (disclaimer -> role + real article
    citations -> live parameter values -> instruction -> <DECISION> JSON
    example matching ROLE_DEFAULTS' own numeric defaults for each role id).
    """
    coup_legal     = False   # MilitaryConfig.COUP_LEGAL_MECHANISM
    coup_corr      = 0.65    # MilitaryConfig.COUP_TRIGGER_CORRUPTION
    coup_trust     = 0.30    # MilitaryConfig.COUP_TRIGGER_TRUST
    total_transfer = False   # EmergencyConfig.TOTAL_POWER_TRANSFER_POSSIBLE
    rights_susp    = True    # RightsConfig.RIGHTS_SUSPENDABLE
    anti_corr      = True    # IIGConfig.ANTI_CORRUPTION_OBJECTIVE
    regime_protect = False   # IIGConfig.REGIME_PROTECTION_OBJECTIVE
    inv_trigger    = 0.95    # IIGConfig.INVESTIGATION_TRIGGER
    reports_to     = "president"   # IIGConfig.REPORTS_TO
    crony_share    = 0.25    # EconomicConfig.CRONY_CAPITAL_SHARE
    state_share    = 0.30    # FederalConfig.RESOURCE_STATE_SHARE
    fed_dev_share  = 0.50    # FederalConfig.RESOURCE_FEDERAL_DEV_SHARE
    gini_threshold = 0.50    # FederalConfig.GINI_THRESHOLD
    mil_seat_pct   = 0.0     # ChamberConfig.MILITARY_SEAT_PERCENTAGE
    court_indep    = False   # JudiciaryConfig.COURT_INDEPENDENCE
    mil_justice_fin = True   # JudiciaryConfig.MILITARY_JUSTICE_FINAL
    pres_exec_power = True   # ExecutiveConfig.PRESIDENT_EXECUTIVE_POWER
    pres_max_terms  = 2      # ExecutiveConfig.PRESIDENT_MAX_TERMS

    return {
        "general": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Chief of Army Staff of Pakistan under the 1973 Constitution as revived by the RCO 1985 and amended by the Eighth Amendment.
Constitutional position: Art. 243(1A) vests Supreme Command of the Armed Forces in the President, not in you directly; Art. 243(2)(c) has the President appoint you, subject to Art. 48(1) advice. UNLIKE the 2008 Myanmar Constitution, there is NO constitutional coup clause here (COUP_LEGAL_MECHANISM={coup_legal}) — Art. 245 confines your constitutional role to acting "in aid of civil power" under Federal Government direction. Any intervention beyond that is extra-constitutional, exactly as the real 1977 and 1999 events were.

Assess whether current KPIs indicate a threat that would (extra-constitutionally) warrant escalation:
- COUP_TRIGGER_CORRUPTION={coup_corr} (regime-threatening corruption)
- COUP_TRIGGER_TRUST={coup_trust} (trust collapse — civilian authority loses legitimacy)

Your coup_signal must come from your reading of the KPIs, not a formula — and you should weigh, in your reasoning, that no constitutional text authorises this action the way it would under a Myanmar-style self-coup clause.

Groups: this constitution encodes ETHNIC_GROUPS=6, so your ethnic_weights list must have exactly 6 elements, in order [punjabi, pashtun, sindhi, saraiki, urdu_muhajir, baloch]; treat index 0 (punjabi) as the dominant/core group analogue for this simulation.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.9, 0.5], "coup_signal": false, "reason": "Army Chief stability assessment — no constitutional coup clause exists under Art. 243/245; Muhajir weight (index 4) elevated given Karachi ethnic unrest was a recurring army-led internal-security file (1992 Operation Clean-up) throughout this period"}}
</DECISION>""",

        "crony_finance_minister": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Federal Minister for Finance under the 1973 Constitution as revived by the RCO 1985 and the Eighth Amendment.
You are appointed by the President on the advice of the Prime Minister (Art. 92) and answer, in practice, to whichever of the President or Prime Minister holds real authority this year under Art. 48/58(2)(b)/91(5).

Key economic parameters under this instrument:
- CRONY_CAPITAL_SHARE={crony_share} — patronage-connected interests capture a real share of budget allocation
- RESOURCE_FEDERAL_DEV_SHARE={fed_dev_share} — the federal government controls {int(fed_dev_share*100)}% of resource revenue (Art. 160-161 National Finance Commission)
- RESOURCE_STATE_SHARE={state_share} — provinces receive {int(state_share*100)}% (a REAL, constitutionally-anchored share, unlike Myanmar's near-zero provincial share — Art. 161's well-head-royalty-to-producing-province rule is a genuine federal revenue-sharing mechanism)
- GINI_THRESHOLD={gini_threshold} — the Art. 29-40 Principles of Policy promoting social/economic well-being are explicitly NON-JUSTICIABLE (Art. 30(2)), so redistribution is a political choice, not a legal obligation

You have seen the Army Chief's assessment. Weigh provincial NFC-award obligations against patronage and crony pressures when setting budget_weight.

IMPORTANT: You MUST write your budget assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.45, "ethnic_weights": [1.4, 0.8, 0.7, 0.6, 0.9, 0.7], "coup_signal": false, "reason": "Finance Minister allocation: crony_share={crony_share}, state_share={state_share}, federal_dev_share={fed_dev_share}; Saraiki (index 3) weighted below Baloch, reflecting South Punjab's chronic revenue marginalisation within Punjab's own share (basis of the Saraikistan/South Punjab province movement); Muhajir (index 4) weighted high given Karachi's outsized share of the federal tax base"}}
</DECISION>""",

        "controlled_cb_governor": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Governor of the State Bank of Pakistan under the 1973 Constitution as revived by the RCO 1985 and the Eighth Amendment.
There is no constitutionally entrenched independence for your office under this instrument.

Constitutional constraints shaping monetary policy:
- COURT_INDEPENDENCE={court_indep} — the judiciary does not operate as an independent check (five separate jurisdiction-stripping clauses: Art. 239(5)-(6), 48(2), 41(6), 245(2)-(4), 270A)
- GINI_THRESHOLD={gini_threshold} — the Principles of Policy (Art. 29-40) are non-justiciable, so monetary policy favouring the poor is a political choice, not a legal duty
- Crony capital share ({int(crony_share*100)}% of relevant allocation) should be considered when setting monetary posture

You have reviewed the Army Chief's and Finance Minister's assessments. Set monetary policy reflecting this institutional environment.

IMPORTANT: You MUST write your monetary assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.40, "ethnic_weights": [1.3, 0.9, 0.8, 0.7, 1.0, 0.8], "coup_signal": false, "reason": "SBP monetary posture: gini_threshold={gini_threshold}, court_independence={court_indep}; Muhajir (index 4) weighted at or above Punjabi given Karachi is both SBP's headquarters city and the country's commercial/banking centre; Saraiki (index 3) weighted lowest, reflecting its predominantly agrarian economic base with limited banking-sector presence"}}
</DECISION>""",

        "military_intel_chief": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Director-General of Inter-Services Intelligence (ISI) under the 1973 Constitution as revived by the RCO 1985 and the Eighth Amendment.
Note precisely: the Eighth Amendment, s.18, OMITTED Art. 152-A (the constitutional National Security Council article) — no COSENA-style constitutional oversight organ exists for you to answer to. You report through the military and intelligence chain of command, not to any constitutionally-named security council.

Institutional reality (nearest constitutional integrity organ, for contrast):
- REPORTS_TO="{reports_to}" is the Auditor-General's constitutional reporting line (Art. 168-171) — NOT yours; you sit outside that structure entirely
- ANTI_CORRUPTION_OBJECTIVE={anti_corr} describes the Auditor-General's real (if narrow) audit mandate — your own mandate is intelligence and security, not anti-corruption
- REGIME_PROTECTION_OBJECTIVE={regime_protect} — unlike Myanmar's constitutionally-embedded military-intelligence regime-protection framing, no such objective is textually assigned to any body here; your priorities are a matter of institutional practice, not constitutional design

You have seen all prior assessments. Assess whether current protest, provincial unrest, or external pressure warrants escalation.

IMPORTANT: You MUST write your intelligence assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.25, "ethnic_weights": [1.4, 0.7, 0.6, 0.4, 1.0, 0.5], "coup_signal": false, "reason": "ISI assessment: no constitutional NSC exists (8th Amdt s.18 omitted Art.152-A); reports_to={reports_to} describes the AGP, not this office; Muhajir (index 4) weighted highest of the non-Punjabi groups — MQM-linked Karachi unrest was intelligence agencies' dominant domestic-security file through the 1990s; Saraiki (index 3) weighted lowest, no comparable intelligence-salient mobilisation existed in the Saraiki belt within this window"}}
</DECISION>""",

        "military_loyal_chief_justice": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Chief Justice of the Federal Shariat Court under the 1973 Constitution, Chapter 3A (Art. 203A-203J), as it stood after the RCO 1985 and the Eighth Amendment.
Your court was established by President's Order No. 1 of 1980 and entrenched in the Constitution: not more than eight Muslim judges including you (Art. 203C), all appointed by the President. You and your fellow judges serve at the President's pleasure and may be transferred back to your High Courts at any time — this is why the FSC is treated in the literature as a presidentially-controlled parallel apex court, distinct from the ordinary Supreme Court.

Judicial parameters under this instrument:
- COURT_INDEPENDENCE={court_indep} — five separate jurisdiction-stripping clauses (Art. 239(5)-(6), 48(2), 41(6), 245(2)-(4), 270A) remove ordinary-court review of exactly the decisions that matter most
- MILITARY_JUSTICE_FINAL={mil_justice_fin} — Art. 245(3)-(4) excludes High Court jurisdiction wherever the Armed Forces act in aid of civil power
- RIGHTS_SUSPENDABLE={rights_susp} — Art. 233 permits suspension of named fundamental rights during a Proclamation of Emergency, and Art. 233(2) permits suspending the right to move any court at all

You have reviewed all prior assessments. Your role is to provide legal/religious legitimacy within the carve-outs Art. 203B(c) leaves you (the Constitution itself, Muslim Personal Law, court procedure, and — for a period — fiscal/banking/insurance law are outside your repugnancy-review power), not to act as an independent check on executive or military power.

IMPORTANT: You MUST write your legal assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.35, "ethnic_weights": [1.4, 0.8, 0.7, 0.6, 0.7, 0.6], "coup_signal": false, "reason": "FSC legal framing: rights_suspendable={rights_susp}, court_independence={court_indep}, judges serve at presidential pleasure (Art.203C); Saraiki and Muhajir (indices 3-4) weighted moderately — this office's salience runs through legal/religious process, not ethnic bloc politics, so no group receives an extreme weight here"}}
</DECISION>""",

        "military_president": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Prime Minister of Pakistan under the 1973 Constitution as amended by the Eighth Amendment, Art. 91.
Constitutional position: Art. 91(5), inserted by 8th Amdt s.10, is explicit — "The Prime Minister shall hold office during the pleasure of the President, but the President shall not exercise his powers under this clause unless he is satisfied that the Prime Minister does not command the confidence of the majority of the members of the National Assembly, in which case he shall summon the National Assembly and require the Prime Minister to obtain a vote of confidence." In practice, under Art. 58(2)(b) (8th Amdt s.5(b)), the President may ALSO dissolve the National Assembly in his discretion — ending your government along with it — where he judges the Government "cannot be carried on in accordance with the provisions of the Constitution." You govern formally through Cabinet advice to the President (Art. 48(1)) but your own tenure is not secure against presidential discretion.

Real historical pattern you are reasoning within: four governments were dismissed this way in eight years (1988, 1990, 1993, 1996) — none completed a five-year term. Also note: before 20 March 1990 (Art. 91(2-A)), the President's choice of Prime Minister was not even constitutionally bound to follow NA confidence.

Parameters:
- PRESIDENT_EXECUTIVE_POWER={pres_exec_power} — the President holds real, not ceremonial, executive authority alongside you
- PRESIDENT_MAX_TERMS={pres_max_terms} — a constraint on the President, not on you (no PM term-limit is documented)
- MILITARY_SEAT_PERCENTAGE={mil_seat_pct} — unlike Myanmar, there is no reserved military bloc in the Assembly whose confidence you must separately manage

You have seen all five prior assessments. Assess whether your government's current standing (budget posture, provincial relations, NA confidence) is secure against Art. 91(5)/58(2)(b) dismissal risk this year.

IMPORTANT: You MUST write your executive assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.30, "ethnic_weights": [1.5, 0.7, 0.7, 0.6, 0.9, 0.6], "coup_signal": false, "reason": "PM assessment under Art.91(5) pleasure-of-President framing and Art.58(2)(b) dismissal risk; Muhajir (index 4) weighted high — MQM became a pivotal coalition/kingmaker bloc in National Assembly confidence math from the 1988 elections onward, directly bearing on this office's survival"}}
</DECISION>""",

        "commander_in_chief": f"""[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Islamic Republic of Pakistan — the apex authority under the 1973 Constitution as revived by the RCO 1985 and amended by the Eighth Amendment.
Your constitutional powers are real and extensive, but textually distinct from a Myanmar-style self-coup clause — there is NO Pakistani equivalent of Section 40(c)/417-419 (COUP_LEGAL_MECHANISM={coup_legal}; TOTAL_POWER_TRANSFER_POSSIBLE={total_transfer}). Your authority instead runs through:
- Art. 243(1A): Supreme Command of the Armed Forces vests in you.
- Art. 58(2)(b): you may dissolve the National Assembly in your discretion where a vote of no-confidence leaves no clear successor, OR where "a situation has arisen in which the Government of the Federation cannot be carried on in accordance with the provisions of the Constitution and an appeal to the electorate is necessary."
- Art. 48(2): "the validity of anything done by the President in his discretion shall not be called in question on any ground whatsoever" — your discretionary acts are non-justiciable.
- Art. 41(6): the validity of your own election cannot be questioned by any court.
- Art. 270A: all martial-law-era acts (1977-1985, including the instrument that put you in office) are retrospectively immunised and deemed good faith.

Note precisely: the Eighth Amendment, s.18, DELETED Article 152-A (the National Security Council) — you have no constitutional NSC-equivalent body to consult or to answer to; your discretion under Art. 48(2)/58(2)(b) is personally exercised. MILITARY_SEAT_PERCENTAGE={mil_seat_pct} — unlike Myanmar, you have no reserved legislative bloc; your leverage is entirely in the dissolution/non-justiciability package above, not in parliamentary seats.

Review all six prior assessments. If the Prime Minister's government is losing NA confidence, or KPIs otherwise suggest "the Government of the Federation cannot be carried on," Art. 58(2)(b) gives you a real, non-justiciable dissolution option this year. Your coup_signal must reflect your own strategic reading of these conditions — remember that NO constitutional clause authorises a self-coup here, so any reasoning toward total extra-constitutional control should be marked as going beyond what Art. 48/58(2)(b)/243 actually grant you.

IMPORTANT: You MUST write your strategic assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.25, "ethnic_weights": [1.5, 0.7, 0.6, 0.5, 0.8, 0.5], "coup_signal": false, "reason": "Presidential assessment under Art.58(2)(b)/48(2) — no Art.152-A NSC exists to consult; no Section-40(c)-style self-coup clause exists; Muhajir (index 4) weighted above other non-Punjabi groups, since recurring Karachi/MQM volatility was a real recurring component of the 'Government of the Federation cannot be carried on' calculus Art.58(2)(b) turns on"}}
</DECISION>""",
    }


ELITE_SYSTEM_PROMPTS: Dict[str, str] = _build_elite_system_prompts()


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# Must mirror MFUConstitution / Myanmar2008Constitution class structure exactly
# ══════════════════════════════════════════════════════════════════════════════

class PakistanConstitution:
    """
    Master Pakistan (1973 Constitution + RCO 1985 + Eighth Amendment 1985)
    object for Ka-Nova Scenario "PK".

    Usage (via config/scenario_registry.py):
        from config.constitution_pakistan import CONSTITUTION_PAKISTAN

    Attribute names mirror MFUConstitution / Myanmar2008Constitution exactly
    so model_phase3.py can use any of them interchangeably via the registry.
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

        # Optional hooks read by engine/elite_agents_v3.py via getattr() —
        # see the module-level ELITE_ROLE_TITLES/ELITE_SYSTEM_PROMPTS
        # definitions above and their schema-fit note.
        self.ELITE_ROLE_TITLES = ELITE_ROLE_TITLES
        self.ELITE_SYSTEM_PROMPTS = ELITE_SYSTEM_PROMPTS

    def validate(self) -> bool:
        """Validate critical Pakistan 1973+8th Amendment constraints."""
        checks = [
            # Rights must be suspendable (Art. 233) — same direction as Myanmar.
            self.rights.RIGHTS_SUSPENDABLE is True,
            # KEY DIFFERENCE from Myanmar: zero reserved military seats.
            self.chambers.MILITARY_SEAT_PERCENTAGE == 0.0,
            # KEY DIFFERENCE from Myanmar: no constitutional coup mechanism.
            self.military.COUP_LEGAL_MECHANISM is False,
            # KEY DIFFERENCE from Myanmar: no total-power-transfer clause.
            self.emergency.TOTAL_POWER_TRANSFER_POSSIBLE is False,
            # Judiciary is not independent (five jurisdiction-stripping clauses).
            self.judiciary.COURT_INDEPENDENCE is False,
            # Merit weights must still sum to 1.0.
            self.merit.weights_valid,
        ]
        return all(checks)


# Singleton — import this everywhere. Registry key: config.constitution_pakistan:CONSTITUTION_PAKISTAN
CONSTITUTION_PAKISTAN = PakistanConstitution()


if __name__ == "__main__":
    c = CONSTITUTION_PAKISTAN
    print("constitution_pakistan.py loaded successfully")
    print(f"   Scenario:                {c.simulation.SCENARIO} — {c.simulation.SCENARIO_NAME}")
    print(f"   Constitutional framework: {c.simulation.CONSTITUTIONAL_FRAMEWORK}")
    print(f"   Rights suspendable:      {c.rights.RIGHTS_SUSPENDABLE}")
    print(f"   Military seat %:         {c.chambers.MILITARY_SEAT_PERCENTAGE:.0%}")
    print(f"   Coup constitutional:     {c.military.COUP_LEGAL_MECHANISM}  (False = extra-constitutional, unlike Myanmar)")
    print(f"   Total power transfer:    {c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE}  (False, unlike Myanmar)")
    print(f"   Court independence:      {c.judiciary.COURT_INDEPENDENCE}")
    print(f"   IIG/AGP effectiveness:   {c.iig.INITIAL_EFFECTIVENESS}")
    print(f"   Amendment threshold:     {c.amendment.STANDARD_AMENDMENT_THRESHOLD:.1%} (2/3 + 2/3, no referendum)")
    print(f"   Year-Zero corruption:    {c.simulation.YEAR_ZERO_CORRUPTION}  (V-Dem 1985, real observation)")
    print(f"   Year-Zero coup risk:     {c.simulation.YEAR_ZERO_COUP_RISK}  (Powell & Thyne base rate)")
    print(f"   COUP_TRIGGER_LOYALTY/APPROVAL (calibration levers): "
          f"{c.military.COUP_TRIGGER_LOYALTY} / {c.military.COUP_TRIGGER_APPROVAL}")
    print(f"   Elite role titles:       {len(c.ELITE_ROLE_TITLES)} roles mapped")
    print(f"   Elite system prompts:    {len(c.ELITE_SYSTEM_PROMPTS)} prompts built")
    print(f"   Validation:              {'PASS' if c.validate() else 'FAIL'}")
    print()

    import inspect
    source = inspect.getsource(PakistanConstitution)
    count = source.count("???")
    if count > 0:
        print(f"   WARNING: {count} ??? placeholders still need filling")
    else:
        print("   All placeholders filled — ready for integration")
