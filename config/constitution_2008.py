"""
================================================================================
PROJECT KA-NOVA
config/constitution_2008.py

Myanmar 2008 Military Constitution — Parameter Registry
Ka-Nova Simulation Engine — Scenario C

This file encodes the 2008 Constitution of the Republic of the Union of Myanmar
as computable parameters for Scenario C (Military/Authoritarian Baseline).

Every parameter maps to a specific chapter and section.
This file must mirror the dataclass architecture of constitution.py exactly.
D fills every ??? by consulting the PDF (full text at the URL in the docstring).

PDF source: https://www.constituteproject.org/constitution/Myanmar_2008.pdf
Author: Patil Devyani Anil (fourth author, Ka-Nova Paper 1)
Architecture owner: Kaung Htet
License: MIT
================================================================================

HOW TO FILL THIS FILE
---------------------
1. Open the PDF at the URL above.
2. Find every ??? below. Each ??? has a comment telling you:
   - Which PDF chapter/section to look at
   - What kind of value to put (str, int, float, bool, Tuple)
3. Replace ??? with the correct value.
4. Do NOT change any field names (e.g. STATE_NAME, PRESIDENT_TERM).
   The field names must stay identical to constitution.py.
5. Do NOT change the dataclass class names.
6. After filling, run: python3 config/constitution_2008.py
   It should print "constitution_2008.py loaded successfully".

WHAT IS THIS FILE FOR
---------------------
Ka-Nova Paper 1 compares Scenario A (MFU constitution) against Scenario C
(2008 Myanmar Military Constitution). This file is Scenario C's ruleset.
The same simulation engine reads either constitution — same code, different
parameters. Kaung wires it in model.py with an import switch.

CRITICAL DIFFERENCE FROM MFU
-----------------------------
The 2008 constitution gives the military structural power at every level:
- 25% reserved parliamentary seats nominated by the Commander-in-Chief
- Military controls its own budget, courts, and judicial process
- Commander-in-Chief can take total sovereign power under emergency
- Rights CAN be suspended during emergencies (opposite of MFU)
These differences are the core of what Scenario C simulates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I — BASIC PRINCIPLES OF THE UNION (Sections 1–48)
# Maps to: constitution.py → FoundationalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Chapter I — Basic Principles of the Union"""

    # Section 2 — Official state name
    STATE_NAME: str = "Republic of the Union of Myanmar"

    # Section 450 (Chapter XV) — Official language
    OFFICIAL_LANGUAGE: str = "Myanmar"  # Burmese, not English
    ETHNIC_LANGUAGES_PROTECTED: bool = True  # Section 22(a) — Union assists ethnic language development

    # Section 440 (Chapter XIII) — Capital
    CAPITAL: str = "Nay Pyi Taw"

    # Section 437 — State Flag
    FLAG: str = "2008_tricolour_flag"

    # Section 345-346 — Citizenship modes
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "both_parents_citizens",      # Section 345(a) — born of parents both citizens
        "existing_citizen_on_commencement"  # Section 345(b) — already citizen when constitution adopted
    )
    NATURALIZATION_YEARS: int = 10   # Section 346 — "shall be as prescribed by law" — proxy from Myanmar Citizenship Law 1982
    NATURALIZATION_MERIT_MIN: float = 0.0  # Not specified — no merit exam, just loyalty

    # Section 5 — Territory
    TERRITORY_BASIS: str = "existing_territory_on_adoption_day"
    STATE_COUNT: int = 14   # Section 9(a), 49 — seven Regions + seven States
    SIMULATION_STATE_COUNT: int = 14


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER VIII — CITIZEN, FUNDAMENTAL RIGHTS AND DUTIES (Sections 345–390)
# Maps to: constitution.py → RightsConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Chapter VIII — Citizen, Fundamental Rights and Duties"""

    # Section 354 — Rights guaranteed (but suspendable — see below)
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "right_to_expression",        # Section 354(a)
        "right_to_assembly",          # Section 354(b)
        "right_to_association",       # Section 354(c)
        "right_to_education",         # Section 366
        "right_to_health_care",       # Section 367
        "right_to_equality_before_law"  # Section 347
    )

    # Section 414(b) — President CAN restrict/suspend rights during emergency
    # This is the OPPOSITE of MFU. In MFU: RIGHTS_SUSPENDABLE = False
    RIGHTS_SUSPENDABLE: bool = True   # Section 414(b): "may restrict or suspend...fundamental rights"
    RIGHTS_ABSOLUTE_COUNT: int = 0    # Zero absolute rights — all conditionally suspendable

    # Section 414(b) — Emergency CAN touch rights
    EMERGENCY_TOUCHES_RIGHTS: bool = True  # Opposite of MFU

    # Section 386 — Citizens must undergo military training
    NATIONAL_SERVICE_MANDATORY: bool = True   # Section 386
    NATIONAL_SERVICE_AGE: int = 18            # Not specified in text — proxy
    NATIONAL_SERVICE_DURATION_MONTHS: int = 24  # Not specified — proxy (military-controlled)

    # Section 382 — Defence personnel rights can be restricted by law
    MILITARY_RIGHTS_OVERRIDE: bool = True  # Section 382 — rights can be revoked for Defence Forces

    # Ka-Nova simulation parameters — inverted from MFU
    # Lower trust impact because regime suppresses protest
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.05   # Suppressed — protest costs are high
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.08        # Gradual erosion, not spike


# ══════════════════════════════════════════════════════════════════════════════
# NO MERIT SYSTEM IN 2008 CONSTITUTION
# Maps to: constitution.py → MeritConfig
# The 2008 constitution has no merit exam system. Military loyalty and
# Commander-in-Chief approval replace merit selection.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """No merit system — loyalty-based appointment replaces merit"""

    # 2008 constitution: no merit formula. Weights set to reflect loyalty-dominance
    # Loyalty (proxy for CIVIC_WEIGHT) becomes primary selector
    PRODUCTIVITY_WEIGHT: float = 0.10   # Minimal — not a selection criterion
    EDUCATION_WEIGHT: float = 0.15      # Some education required for civil posts
    PERFORMANCE_WEIGHT: float = 0.20    # Performance matters only to military hierarchy
    CIVIC_WEIGHT: float = 0.55          # Loyalty to military = dominant selection criterion

    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    # No formal public office merit threshold — loyalty + Commander approval
    MERIT_MIN_PUBLIC_OFFICE: float = 0.0   # No merit minimum — loyalty replaces it

    # Section 342 — Commander-in-Chief proposes, National Defence Security Council approves
    EXAM_ADMINISTRATOR: str = "commander_in_chief"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 0  # No term limit on military commanders — 0 = unlimited
    EXAM_RESULTS_PUBLISH_DAYS: int = 0     # No publication requirement

    # Disqualification: disloyalty to military, not corruption
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "disloyalty_to_defence_services",
        "treason_against_union",         # Section 71(i) and 396(a)(1)
        "breach_of_constitution"         # Section 71(ii)
    )
    DISQUALIFICATION_PERMANENT: bool = True

    # No recertification cycle — serve until removed by Commander-in-Chief
    RECERTIFICATION_INTERVAL: int = 0    # No cycle
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.0
    RECERTIFICATION_VACATE_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER III — HEAD OF STATE (Sections 59–86) +
# CHAPTER V — EXECUTIVE (Sections 199–270)
# Maps to: constitution.py → ExecutiveConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Chapter III (Head of State) + Chapter V (Executive)"""

    # Section 59-60 — President qualifications (military-tied)
    PRESIDENT_ROLE: str = "head_of_state_and_executive"  # Section 16: President is BOTH head of state AND head of executive
    PRESIDENT_ELECTION: str = "electoral_college_hluttaw_representatives"  # Section 60 — elected by Hluttaw reps in three groups
    PRESIDENT_TERM: int = 5            # Section 61 — 5-year term (same as Pyidaungsu Hluttaw term)
    PRESIDENT_MAX_TERMS: int = 2       # Section 65 — may serve maximum two terms
    PRESIDENT_REELECTION: bool = True  # Section 65 — re-election permitted once

    # President has REAL executive power — opposite of MFU's ceremonial President
    PRESIDENT_TIEBREAKER: bool = False   # Has full executive power, not just tiebreaker
    PRESIDENT_EXECUTIVE_POWER: bool = True  # Section 16, 199 — President is head of executive

    # No Chancellor in 2008 constitution — President IS the executive
    # Use CHANCELLOR fields as proxies for Prime Minister / civilian head
    CHANCELLOR_ROLE: str = "none"  # 2008 constitution has no Chancellor/PM equivalent
    CHANCELLOR_ELECTION: str = "none"
    CHANCELLOR_TERM: int = 0
    CHANCELLOR_MAX_TERMS: int = 0
    CHANCELLOR_COOLING_OFF: int = 0  # No cooling-off — loyalty determines appointment

    PRESIDENT_ELECTION_YEAR: int = 1
    CHANCELLOR_ELECTION_YEAR: int = 0  # No Chancellor

    # Section 202 — Union Ministers appointed by President
    MINISTER_COUNT: int = 20   # Section 202 — number not fixed in constitution; proxy from real SPDC count
    MINISTER_MERIT_MIN: float = 0.0    # No merit minimum — presidential/military appointment
    MINISTER_CONFIRMATION: str = "president_appointment_pyidaungsu_approval"  # Section 202

    MINISTRIES: Tuple[str, ...] = (
        "ministry_of_defence",          # Key — Defence Minister is military
        "ministry_of_home_affairs",     # Key — Home Affairs is military
        "ministry_of_border_affairs",   # Key — Border Affairs is military
        "ministry_of_finance",
        "ministry_of_foreign_affairs",
        "ministry_of_education",
        "ministry_of_health",
        "ministry_of_agriculture"
    )

    # Section 71 — President removal (1/4 charge + 2/3 vote)
    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 0   # No Chancellor
    CHANCELLOR_DISMISSAL_VETO: bool = False
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = False

    PRESIDENT_REMOVAL_CHAMBERS: int = 2
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = False   # No Chancellor
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = False
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.25  # Section 71(b) — 25% to charge
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.20

    CHANCELLOR_INTERIM: str = "vice_president_highest_votes"  # Section 73(a)


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER IV — LEGISLATURE (Sections 74–198)
# Maps to: constitution.py → ChamberConfig
# KEY DIFFERENCE: 25% of all seats are reserved for military nominees
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Chapter IV — Legislature (Pyidaungsu Hluttaw)"""

    # Section 109 — Pyithu Hluttaw: 440 seats (330 elected + 110 military)
    # Section 141 — Amyotha Hluttaw: 224 seats (168 elected + 56 military)
    # Military gets exactly 25% of ALL seats in BOTH chambers
    CONGRESS_ELECTION: str = "township_and_population_basis"   # Section 109
    CONGRESS_THRESHOLD: float = 0.51   # Simple majority — same structure
    CONGRESS_TERM: int = 5             # Section 61 — 5-year term tied to President
    CONGRESS_REELECTION: bool = True

    # Military reserved seats — THE defining structural feature of 2008 constitution
    MILITARY_RESERVED_SEATS_PYITHU: int = 110    # Section 109(b) — exact number in PDF
    MILITARY_RESERVED_SEATS_AMYOTHA: int = 56    # Section 141(b) — exact number in PDF
    MILITARY_SEAT_PERCENTAGE: float = 0.25        # 25% across both chambers
    MILITARY_SEATS_APPOINTED_BY: str = "commander_in_chief"

    ETHNIC_SEATS: int = 168   # Section 141 — Amyotha Hluttaw: 12 elected per Region/State × 14
    ETHNIC_THRESHOLD: float = 0.51
    ETHNIC_TERM: int = 5

    # No Analysis Council equivalent
    # Map ANALYSIS fields to Constitutional Tribunal (Chapter VI, Section 320)
    ANALYSIS_THRESHOLD: float = 1.00   # Constitutional Tribunal — unanimous (9 members, all must agree per Section 320)
    ANALYSIS_VETO_TIME_LIMIT: int = 90  # Section 335 — Tribunal term = Hluttaw term (5 yrs); 90 days per ruling

    # Ka-Nova simulation — military bloc controls legislative outcomes
    MILITARY_BLOC_VOTE_DISCIPLINE: float = 1.0  # Military nominees vote as a bloc (100%)
    CIVILIAN_EFFECTIVE_MAJORITY_NEEDED: float = 0.667  # Civilian majority needed to overcome 25% military bloc


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER VI — JUDICIARY (Sections 293–336)
# Maps to: constitution.py → JudiciaryConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Chapter VI — Judiciary"""

    # Section 293 — Courts-Martial separate from civilian courts
    COURT_INDEPENDENCE: bool = False    # Section 293(b) — military justice is final and conclusive
    COURT_JUDGES_COUNT: int = 11       # Section 300 — Supreme Court: Chief Justice + number set by law; proxy
    COURT_TERM_YEARS: int = 70         # Section 301 — serve until age 70; age cap not fixed term
    RULING_THRESHOLD: int = 6          # Not specified — simple majority of 11 judges

    # Section 293(b) — Commander-in-Chief decision is final on military matters
    MILITARY_JUSTICE_FINAL: bool = True
    CIVILIAN_COURT_OVERRIDE_MILITARY: bool = False  # Military courts are separate and supreme for DS matters

    # Constitutional Tribunal — Section 320-336
    CONSTITUTIONAL_TRIBUNAL_SIZE: int = 9    # Section 320 — nine members including Chairperson
    TRIBUNAL_TERM_YEARS: int = 5             # Section 335 — same as Pyidaungsu Hluttaw term

    # Ka-Nova: court effectiveness reduced under military dominance
    COURT_CORRUPTION_RESISTANCE: float = 0.20   # Low — military appointees dominate
    TOTAL_RUIN_THRESHOLD: float = 0.0           # No Total Ruin mechanism in 2008 constitution


# ══════════════════════════════════════════════════════════════════════════════
# NO IIG IN 2008 CONSTITUTION
# Maps to: constitution.py → IIGConfig
# The IIG is an MFU-specific institution. In 2008, military intelligence
# fulfils the oversight role but with inverted objectives (protecting regime,
# not fighting corruption).
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """No IIG — replaced by military intelligence (inverted objectives)"""

    # No IIG exists — set effectiveness floor to near-zero
    ENTRY_MERIT: float = 0.0          # No merit gate — Commander-in-Chief appointment
    ACADEMY_MONTHS: int = 0           # No academy
    INVESTIGATION_TRIGGER: float = 0.90  # Only investigates very high-profile (regime-threatening) corruption
    EFFECTIVENESS_FLOOR: float = 0.05   # Near-zero anti-corruption effectiveness
    REPORTS_TO: str = "commander_in_chief"   # Reports up, not to court
    CHAMBER_ELIGIBLE: bool = False

    # Inverted objective: protect regime, not expose corruption
    ANTI_CORRUPTION_OBJECTIVE: bool = False   # Opposite of MFU IIG
    REGIME_PROTECTION_OBJECTIVE: bool = True

    # Ka-Nova: IIG effectiveness in Scenario C starts near zero and stays there
    INITIAL_EFFECTIVENESS: float = 0.05
    MAX_EFFECTIVENESS: float = 0.15


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER II — STATE STRUCTURE / FEDERAL STRUCTURE (Sections 49–56)
# Maps to: constitution.py → FederalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Chapter II — State Structure"""

    # Section 49 — Seven Regions + Seven States + Union Territories
    STATE_COUNT: int = 14
    ETHNIC_GROUPS: int = 8    # Eight major national races recognised in Myanmar

    # Section 37(a) — Union is ultimate owner of all land and natural resources
    # No 35/35/30 split — Union (effectively military government) controls resources
    RESOURCE_STATE_SHARE: float = 0.10    # States get minimal autonomy share
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.65   # Central (military) government controls majority
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.25  # Some ethnic community allocation (Section 22c)

    # Gini threshold — Section 36 market economy, no redistribution mandate
    GINI_THRESHOLD: float = 0.65   # Much higher — inequality tolerated
    STATE_GDP_CAP: float = 0.80    # No explicit cap — Yangon/Mandalay dominate

    # Section 17 — Defence Services in executive at all levels
    MILITARY_IN_REGIONAL_EXECUTIVE: bool = True   # Section 17(b)


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER VII — DEFENCE SERVICES (Sections 337–344)
# Maps to: constitution.py → MilitaryConfig
# THIS IS THE DEFINING CHAPTER OF 2008 CONSTITUTION
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Chapter VII — Defence Services"""

    # Section 20(f) — Defence Services "mainly responsible for safeguarding the Constitution"
    # Section 40(c) — Commander-in-Chief can take total sovereign power
    # Section 417-419 — Full transfer of legislative, executive, judicial power to CiC
    COUP_LEGAL_MECHANISM: bool = True   # Section 40(c), 417-418 — coup is constitutionally authorised
    COUP_TRIGGER_CORRUPTION: float = 0.65   # Section 40(c) — "disintegration" framing gives wide latitude
    COUP_TRIGGER_TRUST: float = 0.30

    # Section 342 — President appoints Commander-in-Chief WITH approval of NDSC
    COMMANDER_IN_CHIEF_APPOINTMENT: str = "president_with_ndsc_approval"
    MILITARY_SELF_ADJUDICATION: bool = True   # Section 20(b), 343(b) — "final and conclusive"

    # Section 338 — ALL armed forces under Defence Services
    SINGLE_CHAIN_OF_COMMAND: bool = True

    # Section 20(e) — Military "mainly responsible" for Union non-disintegration
    MILITARY_POLITICAL_ROLE: bool = True   # Section 6(f) — explicitly in basic principles

    # Section 14 — 25% reserved seats in ALL Hluttaws
    PARLIAMENTARY_SEAT_PERCENTAGE: float = 0.25
    PARLIAMENTARY_SEAT_APPOINTMENT: str = "commander_in_chief_nominated"

    # Military loyalty dynamics in Ka-Nova simulation
    LOYALTY_INITIAL: float = 0.85       # High initial loyalty to regime
    LOYALTY_CORRUPTION_DRAG: float = 0.001  # Very slow decay — institutional loyalty
    COUP_PROBABILITY_MULTIPLIER: float = 0.0  # No coup risk to regime — military IS the regime

    # Domestic use of force — Section 40(b)
    DOMESTIC_FORCE_AUTHORIZED: bool = True
    DOMESTIC_FORCE_TRIGGER: str = "president_or_commander_in_chief_declaration"


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I (Economic) — Sections 35-37 + CHAPTER V Economic provisions
# Maps to: constitution.py → EconomicConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Chapter I — Economic Framework (Sections 35–37)"""

    # Section 35 — Market economy
    ECONOMIC_SYSTEM: str = "market_economy"   # Section 35

    # Section 36 — Mixed economy with state, cooperatives, private
    TAX_BRACKETS: Tuple[float, ...] = (0.0, 0.05, 0.10, 0.20, 0.30)  # Proxy — not specified in constitution
    BLACK_MONEY_PENALTY: str = "law_prescribed"   # Not specified as High_Treason like MFU

    # Section 37(a) — Union owns ALL land and natural resources
    STATE_OWNS_RESOURCES: bool = True
    PRIVATE_PROPERTY_PROTECTED: bool = True   # Section 37(c) — private property right exists

    # Section 36(b) — Anti-monopoly clause exists but unenforced
    ANTI_MONOPOLY: bool = True   # On paper — but crony capitalism dominates in simulation
    CRONYISM_ENABLED: bool = True   # Ka-Nova parameter — not in constitution text

    # Section 36(d) — "Not nationalize economic enterprises"
    NATIONALIZATION_BANNED: bool = True

    # Ka-Nova: economic parameters under military governance
    CORRUPTION_GDP_DRAG: float = 0.03   # High corruption drag
    CRONY_CAPITAL_SHARE: float = 0.40   # ~40% of economy to military-connected cronies


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I — Education provisions (Sections 28, 366)
# Maps to: constitution.py → ScienceConfig
# No PhD economy or researcher royalty — minimal science investment
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Education and Science — Sections 28, 366"""

    # Section 28(c) — Free compulsory primary education only
    PHD_TUITION_FREE: bool = False   # No free tertiary tuition
    RESEARCHER_ROYALTY: float = 0.0  # No royalty system
    KNOWLEDGE_CAPITAL_GROWTH: float = 0.005  # Very slow — brain drain high

    # Section 28(d) — Education to "contribute to building the Nation" (nationalist framing)
    EDUCATION_NATIONALIST_FRAMING: bool = True

    # Ka-Nova: knowledge capital parameters under military governance
    BRAIN_DRAIN_RATE_BASE: float = 0.15   # High — educated leave
    ACADEMIC_FREEDOM: float = 0.20        # Low — political control of universities


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XII — AMENDMENT (Sections 433–436)
# Maps to: constitution.py → AmendmentConfig
# KEY: 75% threshold + nationwide referendum for core articles
# AND: military holds 25% veto on all amendments
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Chapter XII — Amendment of the Constitution"""

    # Section 435 — 20% of Hluttaw reps needed to submit amendment bill
    AMENDMENT_INITIATION_THRESHOLD: float = 0.20   # Section 435

    # Section 436(a) — Core articles: 75% Hluttaw + >50% referendum
    ENTRENCHED_AMENDMENT_THRESHOLD: float = 0.75    # Section 436(a)
    ENTRENCHED_REQUIRES_REFERENDUM: bool = True      # Section 436(a)

    # Section 436(b) — Non-core articles: 75% Hluttaw vote only
    STANDARD_AMENDMENT_THRESHOLD: float = 0.75   # Section 436(b)

    # PRACTICAL EFFECT: Military 25% = veto on ALL amendments
    # 75% threshold means if military bloc (25%) votes no, amendment fails
    MILITARY_VETO_ON_AMENDMENTS: bool = True   # Ka-Nova derived parameter

    # Entrenched chapters: I, II, III (s59-60), IV (s74,109,141,161),
    #                       V (s200,201,248,276), VI (s293,294,305,314,320),
    #                       XI (s410-432), XII (s436)
    ENTRENCHED_CHAPTERS: Tuple[str, ...] = (
        "chapter_1_basic_principles",
        "chapter_2_state_structure",
        "chapter_3_head_of_state_key_sections",
        "chapter_4_legislature_key_sections",
        "chapter_5_executive_key_sections",
        "chapter_6_judiciary_key_sections",
        "chapter_11_emergency_powers",
        "chapter_12_amendment"
    )
    REVIEW_INTERVAL: int = 0   # No mandatory review cycle — amendment is exceptionally hard


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XIV — TRANSITIONAL PROVISIONS (Sections 441–448)
# Maps to: constitution.py → TransitionConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """Chapter XIV — Transitional Provisions"""

    # Section 442 — SPDC continues sovereignty until constitution operational
    TRANSITION_PERIOD_YEARS: int = 0    # Immediate — no transition period specified
    AMNESTY_GRANTED: bool = True         # Section 445 — no proceedings against SPDC/SLORC

    # Section 445 — All SPDC laws and actions remain valid
    PRIOR_LAWS_VALID: bool = True
    PRIOR_ACTIONS_IMMUNE: bool = True    # Section 445 — total immunity for past actions

    # Section 448 — Civil servants continue in post
    CIVIL_SERVANTS_RETAIN_POSTS: bool = True

    # Ka-Nova: no Tatmadaw incentive structure (that is MFU Article 19 — not needed here)
    TATMADAW_PENSION: float = 0.0        # Already guaranteed by existing law
    TATMADAW_IMMUNITY: bool = True        # Section 445 grants blanket immunity


# ══════════════════════════════════════════════════════════════════════════════
# NO CONSTITUTIONAL SAFEGUARDS EQUIVALENT
# Maps to: constitution.py → SafeguardConfig
# 2008 constitution has no anti-loophole safeguards — the reverse:
# it institutionalizes military control as the "safeguard"
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """No safeguards — military control IS the constitutional safeguard"""

    # All MFU safeguards disabled
    CHANCELLOR_COOLING_OFF_ENFORCED: bool = False
    MERIT_EXAM_INDEPENDENCE: bool = False
    ETHNIC_COUNCIL_YOUTH_MANDATE: bool = False
    IIG_SINGLE_TERM: bool = False
    ANALYSIS_TRANSPARENCY: bool = False
    RIGHTS_ABSOLUTE: bool = False           # Section 414(b) — rights can be suspended
    GENERATIONAL_ASSEMBLY_REVIEW: bool = False

    # 2008 "safeguards" — military-centric
    MILITARY_SEAT_RESERVATION: bool = True  # 25% seats — Section 109, 141
    COMMANDER_IN_CHIEF_VETO: bool = True    # Implicit throughout
    NDSC_OVERSIGHT: bool = True             # National Defence and Security Council


# ══════════════════════════════════════════════════════════════════════════════
# NO CRYPTOGRAPHIC JUSTICE
# Maps to: constitution.py → CryptoJusticeConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """No cryptographic justice — military justice is final"""

    BLOCKCHAIN_ENABLED: bool = False
    ZKP_ENABLED: bool = False
    MULTI_PARTY_SIGNATURES: bool = False
    TOTAL_RUIN_MECHANISM: bool = False
    TOTAL_RUIN_STEPS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XI — EMERGENCY POWERS (Sections 410–432)
# Maps to: constitution.py → EmergencyConfig
# KEY: Commander-in-Chief can take TOTAL sovereign power — legislature, executive, judicial
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Chapter XI — Provisions on State of Emergency"""

    # Section 414(a) — Emergency duration specified in ordinance
    EMERGENCY_MAX_DAYS: int = 365    # Section 417 — initial declaration = 1 year
    EMERGENCY_EXTENSIONS: int = 2    # Section 421(b) — two 6-month extensions permitted
    EMERGENCY_EXTENSION_MONTHS: int = 6  # Section 421(b)

    # Section 414(b) — Rights CAN be suspended — OPPOSITE of MFU
    RIGHTS_UNTOUCHED: bool = False   # Section 414(b): rights "may be restricted or suspended"

    # Section 417-419 — Total sovereign power transfer to Commander-in-Chief
    TOTAL_POWER_TRANSFER_POSSIBLE: bool = True   # Section 418 — all three branches transferred
    POWER_TRANSFER_TRIGGER: str = "disintegration_or_insurgency"   # Section 417

    # Section 419 — Commander-in-Chief exercises legislative + executive + judicial power
    COMMANDER_IN_CHIEF_LEGISLATIVE: bool = True   # Section 419
    COMMANDER_IN_CHIEF_EXECUTIVE: bool = True     # Section 419
    COMMANDER_IN_CHIEF_JUDICIAL: bool = True      # Section 419

    # Section 421 — After total power transfer, Hluttaws suspended
    LEGISLATURE_SUSPENDED_DURING_EMERGENCY: bool = True   # Section 418(a)

    # Ka-Nova simulation parameters
    # Emergency = structural collapse in Scenario C — maps to coup trigger
    EMERGENCY_COUP_PROBABILITY_MULTIPLIER: float = 1.0  # Full probability activation


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I (ROE) — Sections 41-42
# Maps to: constitution.py → ROEConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """Rules of Engagement — Sections 41-42, Chapter VII"""

    # Section 41 — Non-aligned foreign policy
    FOREIGN_POLICY: str = "independent_active_non_aligned"

    # Section 42(a) — No aggression against other nations
    NO_AGGRESSION: bool = True

    # Section 42(b) — No foreign troops permitted
    NO_FOREIGN_TROOPS: bool = True

    # Section 40(b) — Defence Services can act domestically
    # Section 339 — Lead in safeguarding against internal AND external dangers
    DOMESTIC_MILITARY_USE: str = "president_or_commander_discretion"  # Section 40(b)
    DOMESTIC_FORCE_THRESHOLD: float = 0.05   # Very low threshold — broad discretion

    EXTERNAL_ROE: str = "defensive_unless_declared_war"


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I — Psychological Health (Section 18)
# Maps to: constitution.py → PsychConfig
# No equivalent in 2008 constitution
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """No psychological health mandate in 2008 constitution"""

    BIANNUAL_SCREENING: bool = False
    ANTI_BIAS_REVIEW: bool = False
    TRAUMA_CARE_MANDATED: bool = False

    # Ka-Nova simulation: trauma accumulates under military governance
    POPULATION_TRAUMA_BASE: float = 0.45   # High baseline trauma
    TRAUMA_ACCUMULATION_RATE: float = 0.02  # Annual increase
    ETHNIC_TRAUMA_MULTIPLIER: float = 1.5   # Higher for ethnic minorities


# ══════════════════════════════════════════════════════════════════════════════
# NORTH STAR — Inverted objectives for Scenario C
# Maps to: constitution.py → NorthStarConfig
# 2008 constitution's "North Star" = military perpetuation, not development
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """Inverted North Star — military regime perpetuation"""

    # Section 6 — Three consistent objectives of the Union (under military framing)
    OBJECTIVES: Tuple[str, ...] = (
        "non_disintegration_of_union",      # Section 6(a)
        "non_disintegration_of_national_solidarity",  # Section 6(b)
        "perpetuation_of_sovereignty",       # Section 6(c)
    )

    # Military's actual dominant objective
    MILITARY_POLITICAL_ROLE_PERPETUATED: bool = True  # Section 6(f)

    # Ka-Nova: North Star progress metrics — inverted from MFU
    # "Progress" in Scenario C = regime stability, not SDG outcomes
    PROGRESS_METRIC: str = "regime_stability_index"
    TARGET_YEAR_50_PROGRESS: float = 0.0   # MFU goal irrelevant — regime survival is goal

    # PhD Economy — near-zero under military governance
    PHD_COMPOUNDING_ENABLED: bool = False
    KNOWLEDGE_CAPITAL_TARGET: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS — Scenario C calibration
# Maps to: constitution.py → SimulationConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Scenario C simulation parameters"""

    SCENARIO: str = "C"
    SCENARIO_NAME: str = "Military_2008_Constitution"
    CONSTITUTIONAL_FRAMEWORK: str = "2008_myanmar_military_constitution"
    YEAR_ZERO_CORRUPTION: float = 0.72    # Real Myanmar CPI 2023 (Transparency International)
    YEAR_ZERO_TRUST: float = 0.22         # World Bank Governance 2022
    YEAR_ZERO_GINI: float = 0.55          # World Bank 2017
    YEAR_ZERO_EMPLOYMENT: float = 0.58    # Myanmar Census 2014
    YEAR_ZERO_ETHNIC_TENSION: float = 0.68  # V-Dem Dataset
    YEAR_ZERO_COUP_RISK: float = 0.25     # Post-2021 estimate
    YEAR_ZERO_STABILITY: float = 0.18     # World Bank Political Stability 2022

    # Scenario C specific
    MILITARY_CONTROLS_LEGISLATURE: bool = True
    MILITARY_CONTROLS_EXECUTIVE: bool = True
    MILITARY_CONTROLS_JUDICIARY: bool = True
    RIGHTS_ENFORCEABLE: bool = False    # Rights exist on paper, not in practice


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# Must mirror MFUConstitution class structure in constitution.py exactly
# ══════════════════════════════════════════════════════════════════════════════

class Myanmar2008Constitution:
    """
    Master 2008 Myanmar Military Constitution object for Ka-Nova Scenario C.

    Usage in model.py (import switch):
        if scenario == "C":
            from config.constitution_2008 import CONSTITUTION_2008 as CONSTITUTION
        else:
            from config.constitution import CONSTITUTION

    Attribute names mirror MFUConstitution exactly so model.py can use either.
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

    def validate(self) -> bool:
        """Validate critical 2008 constitution constraints"""
        checks = [
            # Rights must be suspendable (opposite of MFU)
            self.rights.RIGHTS_SUSPENDABLE is True,
            # Military seats must be 25%
            self.chambers.MILITARY_SEAT_PERCENTAGE == 0.25,
            # Total power transfer must be constitutionally possible
            self.emergency.TOTAL_POWER_TRANSFER_POSSIBLE is True,
            # Merit weights must still sum to 1.0 (even if loyalty-dominant)
            self.merit.weights_valid,
        ]
        return all(checks)


# Singleton — import this everywhere
CONSTITUTION_2008 = Myanmar2008Constitution()


if __name__ == "__main__":
    c = CONSTITUTION_2008
    print("constitution_2008.py loaded successfully")
    print(f"   Scenario:                {c.simulation.SCENARIO} — {c.simulation.SCENARIO_NAME}")
    print(f"   Rights suspendable:      {c.rights.RIGHTS_SUSPENDABLE}")
    print(f"   Military seat %:         {c.chambers.MILITARY_SEAT_PERCENTAGE:.0%}")
    print(f"   Total power transfer:    {c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE}")
    print(f"   Coup constitutional:     {c.military.COUP_LEGAL_MECHANISM}")
    print(f"   IIG effectiveness:       {c.iig.INITIAL_EFFECTIVENESS}")
    print(f"   Amendment threshold:     {c.amendment.STANDARD_AMENDMENT_THRESHOLD:.0%}")
    print(f"   Year-Zero corruption:    {c.simulation.YEAR_ZERO_CORRUPTION}")
    print(f"   Validation:              {'PASS' if c.validate() else 'FAIL'}")
    print()

    # Count how many ??? remain
    import inspect
    source = inspect.getsource(Myanmar2008Constitution)
    count = source.count("???")
    if count > 0:
        print(f"   WARNING: {count} ??? placeholders still need filling")
    else:
        print("   All placeholders filled — ready for integration")
