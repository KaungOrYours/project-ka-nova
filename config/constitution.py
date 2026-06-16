"""
================================================================================
PROJECT KA-NOVA
config/constitution.py

The Meritocratic Federal Union — Constitutional Parameter Registry
Ka-Nova Simulation Engine v1.0

Every parameter in this file is directly derived from a constitutional clause.
This file is the single source of truth for all simulation rules.
Article references are provided for every parameter.

Author: Kaung Htet
License: MIT
================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# PART I — FOUNDATIONAL DECLARATIONS (Article 1)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Article 1 — Foundational Declarations"""

    # 1.1 — Official name
    STATE_NAME: str = "Federal Union of Myanmar"

    # 1.2 — Official language
    OFFICIAL_LANGUAGE: str = "English"
    ETHNIC_LANGUAGES_PROTECTED: bool = True

    # 1.3 — Capital
    CAPITAL: str = "Naypyidaw"

    # 1.4 — National symbols
    FLAG: str = "1948_six_star_independence_flag"

    # 1.6 — Citizenship modes
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "birth_on_soil",
        "parent_citizen",
        "naturalization_10yr_merit_exam"
    )
    NATURALIZATION_YEARS: int = 10
    NATURALIZATION_MERIT_MIN: float = 0.65

    # 1.7 — Territory
    TERRITORY_BASIS: str = "negotiated_ethnic_homeland_maps"
    STATE_COUNT: int = 14
    SIMULATION_STATE_COUNT: int = 14  # Phase 2 full expansion


# ══════════════════════════════════════════════════════════════════════════════
# PART II — RIGHTS AND FREEDOMS (Article 2)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Article 2 — Rights and Freedoms"""

    # 2.1 — Six absolute rights
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "right_to_life",
        "right_to_expression",
        "right_to_assembly",
        "right_to_fair_trial",
        "right_to_education",
        "right_to_healthcare"
    )

    # 2.4 — ALL rights are absolute — none suspendable
    RIGHTS_SUSPENDABLE: bool = False  # hardcoded — never changes
    RIGHTS_ABSOLUTE_COUNT: int = 6

    # 2.5 — Emergency powers do NOT touch rights
    EMERGENCY_TOUCHES_RIGHTS: bool = False  # hardcoded

    # 2.6 — National Service duty
    NATIONAL_SERVICE_MANDATORY: bool = True
    NATIONAL_SERVICE_AGE: int = 18
    NATIONAL_SERVICE_DURATION_MONTHS: int = 18

    # 2.7 — Non-citizen rights
    IMMIGRANT_RIGHTS: Tuple[str, ...] = ("work_rights", "physical_safety")
    IMMIGRANT_VOTING_RIGHTS: bool = False
    IMMIGRANT_PUBLIC_OFFICE: bool = False

    # Ka-Nova: rights violation triggers grievance spike
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.25
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.20


# ══════════════════════════════════════════════════════════════════════════════
# PART III — MERIT SYSTEM (Article 3)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """Article 3 — The Merit System"""

    # 3.2 — Merit formula weights (must sum to 1.0)
    PRODUCTIVITY_WEIGHT: float = 0.35
    EDUCATION_WEIGHT: float = 0.25
    PERFORMANCE_WEIGHT: float = 0.20
    CIVIC_WEIGHT: float = 0.20

    # Validation
    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    # 3.2a — Minimum merit for any public office
    MERIT_MIN_PUBLIC_OFFICE: float = 0.60

    # 3.3 — Examination administration
    EXAM_ADMINISTRATOR: str = "analysis_council_rotating_panel"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 1  # no examiner serves twice in a row
    EXAM_RESULTS_PUBLISH_DAYS: int = 30

    # 3.5 — Permanent disqualification triggers
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "corruption_conviction",
        "two_consecutive_failed_reviews",
        "criminal_conviction_over_1yr"
    )
    DISQUALIFICATION_PERMANENT: bool = True  # no appeal

    # 3.6 — Recertification cycle
    RECERTIFICATION_INTERVAL: int = 4  # years — aligned with elections
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.60
    RECERTIFICATION_VACATE_DAYS: int = 90  # days to leave office if failed

    # Ka-Nova: merit score formula
    # M = (P * 0.35) + (E * 0.25) + (PR * 0.20) + (C * 0.20)
    # All components: 0.0 to 1.0
    # Final score: 0.0 to 1.0


# ══════════════════════════════════════════════════════════════════════════════
# PART IV — EXECUTIVE BRANCH (Article 4)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Article 4 — Executive Branch"""

    # 4.1-4.3 — President
    PRESIDENT_ROLE: str = "ceremonial_head_of_state"
    PRESIDENT_ELECTION: str = "direct_popular_vote"
    PRESIDENT_TERM: int = 5  # years
    PRESIDENT_MAX_TERMS: int = 1  # single term only
    PRESIDENT_REELECTION: bool = False

    # President reserve power — tiebreaker only
    PRESIDENT_TIEBREAKER: bool = True
    PRESIDENT_EXECUTIVE_POWER: bool = False

    # 4.4-4.6 — Chancellor
    CHANCELLOR_ROLE: str = "executive_head_of_government"
    CHANCELLOR_ELECTION: str = "joint_three_chamber_vote"
    CHANCELLOR_TERM: int = 5  # years
    CHANCELLOR_MAX_TERMS: int = 1  # single term only
    CHANCELLOR_COOLING_OFF: int = 5  # years — cannot have served in chambers

    # Term stagger — President elected Year 1, Chancellor Year 3
    PRESIDENT_ELECTION_YEAR: int = 1
    CHANCELLOR_ELECTION_YEAR: int = 3

    # 4.7-4.8 — Cabinet
    MINISTER_COUNT: int = 8  # one per constitutional pillar
    MINISTER_MERIT_MIN: float = 0.65
    MINISTER_CONFIRMATION: str = "simple_majority_all_three_chambers"

    MINISTRIES: Tuple[str, ...] = (
        "ministry_of_justice",
        "ministry_of_federal_affairs",
        "ministry_of_finance_economic_competition",
        "ministry_of_natural_resources",
        "ministry_of_ethnic_affairs_culture",
        "ministry_of_national_service_defence",
        "ministry_of_education_merit_development",
        "ministry_of_science_technology_engineering"
    )

    # 4.9 — Chancellor dismissal
    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 2  # of 3
    CHANCELLOR_DISMISSAL_VETO: bool = False  # no veto on dismissal votes
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = True

    # 4.3 — President removal
    PRESIDENT_REMOVAL_CHAMBERS: int = 2
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = True
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = True
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.25  # below = removable
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.20

    # 4.10 — Succession
    CHANCELLOR_INTERIM: str = "highest_merit_analysis_council_member"


# ══════════════════════════════════════════════════════════════════════════════
# PART V — THREE VETO CHAMBERS (Article 5)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Article 5 — The Three Veto Chambers"""

    # 5.1-5.2 — Congress
    CONGRESS_ELECTION: str = "bottom_up_district_to_federal"
    CONGRESS_THRESHOLD: float = 0.51  # simple majority
    CONGRESS_TERM: int = 4  # years — aligned with merit cycle
    CONGRESS_REELECTION: bool = True

    # 5.3-5.4 — Ethnic Leaders Council
    ETHNIC_SEATS: int = 8  # one per major ethnic group
    ETHNIC_THRESHOLD: float = 0.51  # simple majority
    ETHNIC_TERM: int = 5  # years
    ETHNIC_MAX_TERMS: int = 2  # maximum 10 years total service
    ETHNIC_NO_BLOODLINE: bool = True  # no two members share bloodline
    ETHNIC_YOUTH_MIN: bool = True  # at least one member aged ≤ 40
    ETHNIC_YOUTH_AGE_MAX: int = 40

    # Ethnic leader presidential pathway
    ETHNIC_PRESIDENTIAL_ELIGIBLE: bool = True  # after min 1 term
    ETHNIC_PRESIDENTIAL_MIN_TERMS: int = 1
    ETHNIC_RETURN_COOLING_OFF: int = 2  # years if election lost

    # 5.5-5.6 — Analysis Council
    ANALYSIS_THRESHOLD: float = 0.75  # 75% qualified supermajority (v7) — highest standard
    ANALYSIS_MERIT_MIN: float = 0.80
    ANALYSIS_TERM: int = 6  # years rotating
    ANALYSIS_VETO_TIME_LIMIT: int = 90  # days — must decide or escalate
    ANALYSIS_METHODOLOGY_PUBLISH_DAYS: int = 14  # before any veto

    # 5.7 — Three-chamber veto process
    # Policy passes ONLY if all three thresholds met simultaneously
    POLICY_REQUIRES_ALL_THREE: bool = True

    # Policy classification — what needs full veto vs chancellor alone
    POLICY_TYPES: Dict[str, str] = field(default_factory=lambda: {
        "constitutional_amendment": "full_three_chamber_plus_referendum",
        "major_legislation": "full_three_chamber_unanimous",
        "national_budget": "congress_plus_ethnic_analysis_audits",
        "emergency_measures": "chancellor_plus_two_chambers_ratify",
        "administrative_orders": "chancellor_alone",
        "state_intervention": "ethnic_council_prerequisite_then_three",
        "domestic_military": "congress_approval",
        "external_military": "chancellor_alone_report_6hrs"
    })

    # 5.8 — Deadlock resolution
    DEADLOCK_TIEBREAKER: str = "president_casts_deciding_vote"
    DEADLOCK_MANIPULATION_THRESHOLD: int = 3  # per session triggers review
    DEADLOCK_MANIPULATION_CONSEQUENCE: str = "permanent_merit_disqualification"


# ══════════════════════════════════════════════════════════════════════════════
# PART VI — CONSTITUTIONAL COURT (Article 6)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Article 6 — The Constitutional Court"""

    # 6.1-6.2 — Composition
    JUDGE_COUNT: int = 11  # odd number prevents ties
    JUDGE_ELECTION: str = "direct_popular_vote"
    JUDGE_TERM: int = 10  # years — longest single service in system
    JUDGE_MAX_TERMS: int = 1  # single term only
    JUDGE_REELECTION: bool = False

    # 6.6 — Ruling threshold
    RULING_THRESHOLD: int = 6  # of 11 — simple majority
    DISSENTING_OPINIONS_PUBLISHED: bool = True

    # 6.7 — Judicial removal — hardest in system
    JUDGE_REMOVAL_CHAMBERS: int = 2  # any two of three
    JUDGE_REMOVAL_PRESIDENT_SIGN: bool = True
    JUDGE_REMOVAL_CHANCELLOR_SIGN: bool = True
    # Four approvals required — most difficult removal in constitution

    # Court jurisdiction
    JURISDICTION: Tuple[str, ...] = (
        "constitutional_review",
        "iig_oversight",
        "rights_protection",
        "electoral_certification",
        "citizen_appeals",
        "deadlock_resolution",
        "emergency_power_certification",
        "security_designation_review"
    )

    # Budget — constitutionally fixed
    BUDGET_FIXED: bool = True
    BUDGET_POLITICAL_INTERFERENCE: bool = False

    # Federal Arbitration Court (Article 6.8)
    ARBITRATION_JURISDICTION: Tuple[str, ...] = (
        "interstate_disputes",
        "investor_state_disputes",
        "cross_border_commercial"
    )
    ARBITRATION_COMPOSITION: str = "mixed_elected_merit"
    ARBITRATION_APPEALS_TO: str = "constitutional_court"


# ══════════════════════════════════════════════════════════════════════════════
# PART VII — INDEPENDENT INTELLIGENCE GROUP (Article 7)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """Article 7 — The Independent Intelligence Group"""

    # 7.0 — IIG Academy
    ACADEMY_REQUIRED: bool = True  # only pathway into IIG
    ACADEMY_DURATION_MONTHS: int = 27
    NS_REQUIRED: bool = True  # must complete national service first
    NS_DISCHARGE_REQUIRED: str = "honorable"

    # Academy admission requirements (ALL must be met)
    ENTRY_MERIT_MIN: float = 0.85
    ENTRY_CIVIL_SERVICE_PERCENTILE: float = 0.99  # top 1%
    ENTRY_PSYCH_TEST: bool = True  # court-administered
    ENTRY_BACKGROUND_CHECK: bool = True
    ENTRY_MIN_AGE: int = 22  # earliest possible after NS + Academy

    # Academy training structure
    ACADEMY_FOUNDATION_MONTHS: int = 6    # constitutional law, ethics
    ACADEMY_TECHNICAL_MONTHS: int = 12   # forensic, cyber, investigation
    ACADEMY_FIELD_MONTHS: int = 6        # supervised real investigations
    ACADEMY_ASSESSMENT_MONTHS: int = 3   # final evaluation

    # 7.1 — Mandate — three mortal sins
    MANDATE: Tuple[str, ...] = (
        "systemic_corruption",      # bribery, embezzlement, abuse
        "resource_sabotage",        # illegal sale, concealment, misreporting
        "merit_subversion"          # rigged appointments, nepotism
    )

    # 7.2 — Independence
    REPORTS_TO: str = "constitutional_court_only"
    POLITICAL_CONTROL: bool = False  # belongs to people via court
    CHAMBER_INTERFERENCE: bool = False

    # 7.3 — Director
    DIRECTOR_APPOINTMENT: str = "constitutional_court_from_senior_iig"
    DIRECTOR_TERM: int = 6  # years — outlasts Chancellor and President
    DIRECTOR_RENEWABLE: bool = False  # single term only

    # 7.4 — Investigation trigger
    INVESTIGATION_TRIGGER: float = 0.45  # corruption score threshold (lowered from 0.70 — most officials never reached 0.70)
    INVESTIGATION_TRIGGER_TYPE: str = "automatic"  # no discretion

    # 7.5 — Data custody
    DATA_CUSTODY: str = "constitutional_court"  # NOT IIG
    IIG_ACCESS_RIGHTS: bool = True
    IIG_PERMANENT_CUSTODY: bool = False  # access only, not ownership

    # 7.6 — Prosecution
    PROSECUTION_BODY: str = "constitutional_court_prosecutors"
    IIG_PROSECUTES: bool = False  # fact-finding only

    # 7.7 — IIG oversight
    IIG_AUDITED_BY: str = "analysis_council"
    AUDIT_SCOPE: Tuple[str, ...] = ("processes", "finances")
    PERSONNEL_VETTED_BY: str = "constitutional_court"

    # 7.8 — Budget
    BUDGET_PROPOSED_BY: str = "analysis_council"
    BUDGET_APPROVED_BY: str = "congress"
    BUDGET_CONGRESS_CAN_MODIFY: bool = False  # approve or reject only
    BUDGET_REJECTION_FALLBACK: str = "previous_year_budget_continues"

    # 7.9 — Post-service restrictions
    CHAMBER_ELIGIBLE_POST_SERVICE: bool = False  # PERMANENT
    PERMITTED_POST_SERVICE: Tuple[str, ...] = (
        "armed_forces",
        "police_service",
        "state_administration",
        "federal_ministries_non_legislative",
        "academic_institutions"
    )

    # IIG Partnership Model (Article 7.10)
    STRUCTURE: str = "partnership_model"
    PARTNER_ELIGIBILITY_YEARS: int = 5
    OPEN_INVESTIGATION_THRESHOLD: float = 0.35   # lowered from 0.51 — evidence-weighted approval
    PROCEED_PROSECUTION_THRESHOLD: float = 0.67  # 2/3 majority
    PARTNERSHIP_COUNCIL_QUORUM: float = 0.60

    # Nine divisions
    FUNCTIONAL_DIVISIONS: Tuple[str, ...] = (
        "forensic_accounting",
        "cybersecurity",
        "field_investigation"
    )
    MANDATE_DIVISIONS: Tuple[str, ...] = (
        "corruption_division",
        "resource_sabotage_division",
        "merit_subversion_division"
    )
    OPERATIONAL_DIVISIONS: Tuple[str, ...] = (
        "intelligence_division",
        "investigation_division",
        "prosecution_preparation_division"
    )

    # Maximum size
    MAX_AGENTS: int = 600  # small, elite, accountable


# ══════════════════════════════════════════════════════════════════════════════
# PART VIII — FEDERAL STRUCTURE (Article 8)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Article 8 — Federal Structure"""

    # 8.2 — Federal powers
    FEDERAL_POWERS: Tuple[str, ...] = (
        "national_defence",
        "foreign_policy",
        "national_currency",
        "constitutional_law",
        "iig",
        "constitutional_court",
        "federal_universities",
        "federal_research_institutes"
    )

    # 8.3 — State powers
    STATE_POWERS: Tuple[str, ...] = (
        "primary_secondary_education",
        "local_healthcare",
        "local_infrastructure",
        "agriculture_land_use",
        "local_taxation",
        "cultural_affairs",
        "ethnic_language_preservation",
        "local_police"
    )

    # 8.5 — Resource management
    RESOURCE_STATE_MANAGES: bool = True
    RESOURCE_REPORTS_TO_FEDERAL: bool = True
    RESOURCE_IIG_OVERSIGHT: bool = True

    # 8.6 — Revenue split (must sum to 1.0)
    RESOURCE_STATE_SHARE: float = 0.35
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.35
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.30

    # 8.7 — State competition
    STATE_RANKING_PUBLISHED: bool = True
    STATE_RANKING_INTERVAL: int = 1  # years

    # 8.9 — Federal intervention
    INTERVENTION_PREREQUISITE: str = "ethnic_council_majority_first"
    INTERVENTION_ETHNIC_THRESHOLD: float = 0.51
    INTERVENTION_THEN_THREE_CHAMBERS: bool = True

    # Economic Check & Balance (Article 10.8)
    STATE_GDP_CAP: float = 0.40      # triggers if exceeded
    SECTOR_MONOPOLY_CAP: float = 0.30
    # v7 — Trust acceleration trigger (Article VIII)
    TRUST_ACCELERATION_MULTIPLIER: float = 1.50
    TRUST_ACCELERATION_TRIGGER_CORRUPTION: float = 0.20
    TRUST_ACCELERATION_TRIGGER_YEARS: int = 5
    GINI_THRESHOLD: float = 0.45
    ECB_ENFORCERS: Tuple[str, ...] = (
        "analysis_council",    # diagnoses
        "arbitration_court",   # structural remedy
        "iig"                  # corruption investigation
    )
    ECB_SIMULTANEOUS: bool = True  # all three act at same time


# ══════════════════════════════════════════════════════════════════════════════
# PART IX — MILITARY AND SECURITY (Article 9)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Article 9 — Military and Security"""

    # 9.1 — Civilian command
    CIVILIAN_COMMAND: bool = True  # always
    EXTERNAL_COMMAND: str = "chancellor"
    DOMESTIC_COMMAND_REQUIRES: str = "congress_approval"

    # 9.2 — Military oath
    OATH_LOYALTY_TO: str = "constitution_not_person"
    OATH_CIVILIAN_PROTECTION: bool = True
    DUTY_TO_REFUSE_ILLEGAL: bool = True
    FOLLOWING_ORDERS_DEFENSE: bool = False  # never valid

    # 9.4 — Coup definition
    COUP_TRIGGER_LOYALTY: float = 0.30  # below = coup risk
    COUP_TRIGGER_APPROVAL: float = 0.20  # below = coup risk
    COUP_HIGHEST_TREASON: bool = True
    COUP_AMNESTY: bool = False
    COUP_MILITARY_TRIBUNAL: bool = False  # constitutional court only

    # 9.5 — National Service
    NS_MANDATORY: bool = True
    NS_AGE: int = 18
    NS_DURATION_MONTHS: int = 18
    NS_CIVILIAN_TRACK_THRESHOLD: float = 0.65  # merit above = civilian
    NS_MILITARY_TRACK_THRESHOLD: float = 0.65  # merit below = military
    NS_EQUAL_HONOR: bool = True  # both tracks equal status

    # Ka-Nova: NS effects on agent attributes
    NS_LOYALTY_BOOST: float = 0.15
    NS_ETHNIC_EXPOSURE_BOOST: float = 0.20
    NS_CIVIC_CONTRIBUTION_BOOST: float = 0.10

    # 9.6 — Police
    POLICE_LEVEL: str = "state"
    POLICE_OVERSIGHT: str = "state_legislature"
    POLICE_CORRUPTION_INVESTIGATOR: str = "iig"

    # 9.7 — Intelligence
    SOLE_INTELLIGENCE_BODY: str = "iig"
    PARALLEL_MILITARY_INTEL: bool = False  # prohibited

    # Transition — no amnesty
    MILITARY_AMNESTY: bool = False
    PROSECUTION_ORDER: str = "severity_descending"
    COOPERATION_CREDIT: bool = True  # mitigating factor only


# ══════════════════════════════════════════════════════════════════════════════
# PART X — ECONOMIC FRAMEWORK (Articles 10-10.13)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Articles 10 — Economic Framework"""

    # 10.1 — Economic system
    ECONOMIC_SYSTEM: str = "open_market_with_sectoral_caps"
    STATE_ENTERPRISES_COMPETE_ON_MERIT: bool = True
    STATE_ENTERPRISES_NO_SUBSIDY: bool = True

    # 10.3 — Foreign investment
    STRATEGIC_SECTORS: Tuple[str, ...] = (
        "natural_resources",
        "technology",
        "defence",
        "media",
        "banking"
    )
    OPEN_SECTORS: Tuple[str, ...] = (
        "manufacturing",
        "retail",
        "tourism",
        "services",
        "agriculture_non_resource"
    )
    FOREIGN_CAP_STRATEGIC: float = 0.49  # max 49% foreign ownership
    FOREIGN_CAP_OPEN: float = 1.00       # fully open

    # 10.5 — Central bank
    CENTRAL_BANK_INDEPENDENT: bool = True
    CENTRAL_BANK_POLITICAL_DIRECTION: bool = False
    CENTRAL_BANK_ANNUAL_REPORT: bool = True
    CENTRAL_BANK_CHAMBERS_CAN_DIRECT: bool = False

    # 10.9 — Tax brackets
    # (poverty_line_multiple_min, poverty_line_multiple_max, rate)
    TAX_BRACKETS: Tuple[Tuple, ...] = (
        (0.0, 1.0, 0.00),          # below poverty line — zero tax
        (1.0, 2.0, 0.10),          # bracket 1 — 10%
        (2.0, 5.0, 0.20),          # bracket 2 — 20%
        (5.0, 10.0, 0.30),         # bracket 3 — 30%
        (10.0, 20.0, 0.40),        # bracket 4 — 40%
        (20.0, float('inf'), 0.50) # bracket 5 — 50% maximum
    )

    # 10.10 — Tax exemptions (ONLY these three)
    TAX_EXEMPT_CATEGORIES: Tuple[str, ...] = (
        "under_18",
        "active_enrolled_student",
        "phd_research_grant_stipend"  # grant not salary
    )
    # ALL employees pay tax — no profession exemptions
    PROFESSION_EXEMPTIONS: bool = False
    MILITARY_TAX_EXEMPT: bool = False   # pays full tax
    POLICE_TAX_EXEMPT: bool = False     # pays full tax
    POLITICIANS_TAX_EXEMPT: bool = False # pays full tax
    JUDGES_TAX_EXEMPT: bool = False     # pays full tax

    # 10.11 — Dynamic poverty line
    POVERTY_LINE_FACTORS: Tuple[str, ...] = (
        "state_productivity_index",
        "gdp_growth_rate",
        "employment_vacancy_rate"
    )
    POVERTY_LINE_CALCULATOR: str = "analysis_council_annual"
    POVERTY_LINE_PUBLISHED_BEFORE_TAX_YEAR: bool = True

    # 10.12 — No black money
    ALL_INCOME_MUST_DECLARE: bool = True
    UNDECLARED_INCOME_CRIME: str = "high_treason"
    DECLARED_BLACK_MONEY_ORIGIN_PROSECUTED: bool = True  # separately
    TAX_PAID_DOES_NOT_CLEAR_ORIGIN: bool = True

    # Ka-Nova: tax evasion consequence
    TAX_EVASION_CRIMINAL_RECORD: bool = True
    TAX_EVASION_TOTAL_RUIN: bool = True

    # 10.13 — Age-based minimum wage
    MIN_WAGE_BY_AGE: Dict[str, float] = field(default_factory=lambda: {
        "16_18": 0.60,  # 60% of adult minimum — training wage
        "18_21": 0.80,  # 80% — youth wage
        "21_25": 0.90,  # 90% — entry adult
        "25_plus": 1.00 # 100% — full adult minimum floor
    })
    MIN_WAGE_STATES_BELOW_FEDERAL: bool = False  # never below federal floor
    MIN_WAGE_VIOLATION: str = "iig_investigation_plus_state_merit_review"


# ══════════════════════════════════════════════════════════════════════════════
# PART XI — SCIENCE, TECHNOLOGY & EDUCATION (Article 11)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Article 11 — Science, Technology and Education"""

    # 11.1 — PhD program entitlements
    PHD_TUITION: float = 0.0  # fully funded
    PHD_STIPEND: str = "civil_service_entry_salary"
    PHD_ACCOMMODATION: str = "single_university_dorm_until_completion"
    PHD_ANNUAL_PROGRESS_REVIEW: bool = True
    PHD_DROPOUT_REPAY_AFTER_YEAR: int = 2  # repay if dropout after year 2

    # 11.2 — Research institutes
    STATE_RESEARCH_INSTITUTES: bool = True
    ALONGSIDE_UNIVERSITIES: bool = True

    # 11.3 — IP ownership
    IP_PRIVATE_FUNDED_OWNER: str = "researcher_or_entity"
    IP_STATE_FUNDED_OWNER: str = "federal_union"
    RESEARCHER_ROYALTY_RATE: float = 0.15  # 15% of net licensing revenue
    IP_STATE_SELL_FOREIGN: bool = False    # requires three-chamber approval

    # 11.4 — Tech foreign investment
    TECH_FOREIGN_CAP: float = 0.49  # same as strategic sector rule

    # 11.5 — Academic freedom
    ACADEMIC_FREEDOM: bool = True
    ACADEMIC_EXCEPTION: str = "court_certified_national_security"
    SECURITY_DESIGNATION_RENEWABLE: bool = True
    SECURITY_DESIGNATION_RENEWAL_INTERVAL: int = 1  # year
    SECURITY_DESIGNATION_PERMANENT: bool = False
    RESEARCHER_APPEAL_DAYS: int = 30

    # Ka-Nova: PhD pipeline effect on knowledge capital
    PHD_KNOWLEDGE_CAPITAL_BOOST: float = 0.25  # per graduate
    PHD_PIPELINE_YEARS: int = 4  # average completion time


# ══════════════════════════════════════════════════════════════════════════════
# PART XII — AMENDMENT AND REVIEW (Article 12)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Article 12 — Amendment and Constitutional Review"""

    # 12.1 — Three-tier amendment system
    MINOR_AMENDMENT: str = "three_chamber_supermajority"
    MINOR_CONGRESS_THRESHOLD: float = 0.67
    MINOR_ETHNIC_THRESHOLD: float = 0.67
    MINOR_ANALYSIS_THRESHOLD: float = 1.00

    SIGNIFICANT_AMENDMENT: str = "supermajority_plus_citizens_assembly"
    CORE_AMENDMENT: str = "supermajority_plus_assembly_plus_referendum"
    REFERENDUM_MIN_TURNOUT: float = 0.50  # 50% minimum participation

    # 12.2 — Permanently entrenched
    ENTRENCHED_CLAUSES: Tuple[str, ...] = (
        "ethnic_veto_rights",  # ONLY this is permanent
    )
    ENTRENCHED_CAN_EXPAND: bool = True   # add ethnic groups
    ENTRENCHED_CAN_REDUCE: bool = False  # never

    # 12.3 — Mandatory ten-year review
    REVIEW_INTERVAL: int = 10  # years — mandatory not optional
    CITIZENS_ASSEMBLY_SIZE: int = 320
    CITIZENS_ASSEMBLY_METHOD: str = "civic_lottery"  # not election
    REVIEW_MECHANISM_REMOVABLE: bool = False  # cannot be removed by review


# ══════════════════════════════════════════════════════════════════════════════
# PART XIII — TRANSITIONAL PROVISIONS (Article 13)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """Article 13 — Transitional Provisions"""

    # 13.2 — Caretaker government
    CARETAKER_TYPE: str = "neutral_technocratic"
    CARETAKER_APPOINTED_BY: str = "all_ethnic_groups_unanimous"
    CARETAKER_NO_POLITICAL_PARTY: bool = True
    CARETAKER_MAX_MILITARY_RANK: str = "non_commissioned_officer"
    CARETAKER_MERIT_MIN: float = 0.70
    CARETAKER_MANDATE: Tuple[str, ...] = (
        "security",
        "basic_services",
        "humanitarian_response",
        "institution_construction"
    )
    CARETAKER_PROHIBITED: Tuple[str, ...] = (
        "permanent_policy",
        "international_treaties",
        "constitutional_changes"
    )
    CARETAKER_DISSOLVES: str = "upon_first_presidential_election"

    # 13.3 — Military justice
    MILITARY_AMNESTY: bool = False
    PROSECUTION_ORDER: str = "severity_descending"
    COOPERATION_SENTENCING_CREDIT: bool = True
    COOPERATION_IS_AMNESTY: bool = False

    # 13.4 — Timeline (10-year phased)
    TRANSITION_DURATION: int = 10  # years

    PHASE_1: Dict = field(default_factory=lambda: {
        "years": "0-2",
        "name": "Foundation",
        "milestones": [
            "constitutional_court_established",
            "iig_academy_founded",
            "census_ethnic_mapping",
            "basic_civil_administration"
        ]
    })
    PHASE_2: Dict = field(default_factory=lambda: {
        "years": "2-4",
        "name": "Institution Building",
        "milestones": [
            "first_congressional_elections",
            "ethnic_leaders_council_constituted",
            "analysis_council_appointed",
            "three_chamber_system_begins"
        ]
    })
    PHASE_3: Dict = field(default_factory=lambda: {
        "years": "4-6",
        "name": "Executive Formation",
        "milestones": [
            "first_presidential_election",
            "first_chancellor_election",
            "cabinet_confirmed",
            "iig_first_graduating_class"
        ]
    })
    PHASE_4: Dict = field(default_factory=lambda: {
        "years": "6-8",
        "name": "Consolidation",
        "milestones": [
            "resource_revenue_split_operational",
            "phd_programs_running",
            "central_bank_independent",
            "first_merit_recertification"
        ]
    })
    PHASE_5: Dict = field(default_factory=lambda: {
        "years": "8-10",
        "name": "Full Sovereignty",
        "milestones": [
            "all_mfu_institutions_operational",
            "first_constitutional_review_scheduled",
            "transition_officially_ends"
        ]
    })

    FIRST_ELECTION_BY_YEAR: int = 4


# ══════════════════════════════════════════════════════════════════════════════
# PART XIV — CONSTITUTIONAL SAFEGUARDS (Article 14)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """Article 14 — The Seven Constitutional Safeguards"""

    # S.1 — Chancellor cooling-off
    CHANCELLOR_COOLING_OFF: int = 5  # years

    # S.2 — Merit exam independence
    EXAM_ROTATING_PANEL: bool = True
    EXAM_MAX_CONSECUTIVE: int = 1
    EXAM_RESULTS_PUBLIC: bool = True
    EXAM_PUBLISH_DAYS: int = 30

    # S.3 — Ethnic council generational rule
    ETHNIC_YOUTH_REQUIRED: bool = True
    ETHNIC_YOUTH_MAX_AGE: int = 40
    ETHNIC_SELECTION_AUTONOMOUS: bool = True

    # S.4 — IIG single term + data sovereignty
    IIG_DIRECTOR_SINGLE_TERM: bool = True
    IIG_DATA_HELD_BY_COURT: bool = True
    IIG_WEAPONIZE_DATA: str = "institutional_treason"

    # S.5 — Analysis council transparency
    ANALYSIS_PUBLISH_BEFORE_VETO_DAYS: int = 14
    ANALYSIS_CITIZEN_CHALLENGE: bool = True
    ANALYSIS_CHALLENGE_BODY: str = "constitutional_court"

    # S.6 — Rights absolute — NO suspension ever
    RIGHTS_SUSPENDABLE: bool = False  # absolute — hardcoded
    SUSPENSION_AUTHORITY: str = "none"  # no authority exists

    # S.7 — Generational renewal
    REVIEW_INTERVAL: int = 10
    ASSEMBLY_SIZE: int = 500
    ASSEMBLY_METHOD: str = "civic_lottery"
    REVIEW_ITSELF_REMOVABLE: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# PART XV — CRYPTOGRAPHIC JUSTICE (Article 15)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """Article 15 — Cryptographic Justice Protocol"""

    # Three-layer system
    LAYER_1: str = "blockchain_evidence_ledger"
    LAYER_2: str = "zero_knowledge_proofs"
    LAYER_3: str = "multi_party_digital_signatures"

    # Evidence requirements
    EVIDENCE_MUST_BE_ON_LEDGER: bool = True
    EVIDENCE_OFF_LEDGER_ADMISSIBLE: bool = False

    # Multi-party signatures required for Total Ruin
    SIGNATURES_REQUIRED: int = 4
    SIGNATURE_PARTIES: Tuple[str, ...] = (
        "iig_director",
        "iig_partnership_council_majority",
        "constitutional_court_supermajority",  # 8 of 11
        "analysis_council_financial_verification"
    )
    COURT_SUPERMAJORITY_FOR_TOTAL_RUIN: int = 8  # of 11

    # Total Ruin trigger conditions (ALL must be true)
    TOTAL_RUIN_TRIGGERS: Tuple[str, ...] = (
        "corruption_score_above_0.85",
        "evidence_chain_intact_on_blockchain",
        "zkp_verified",
        "all_four_signatures_obtained",
        "court_supermajority_8_of_11",
        "appeal_window_expired_60_days"
    )

    # Total Ruin — 7 sequential steps
    TOTAL_RUIN_STEPS: Tuple[str, ...] = (
        "freeze_all_personal_assets_24hrs",
        "full_financial_audit_family_3_degrees",
        "complete_asset_seizure_personal_business_trusts",
        "permanent_disqualification_all_public_office",
        "public_record_national_ledger",
        "proceeds_to_federal_development_fund",
        "name_national_shame_register_permanent"
    )

    # National Shame Register
    SHAME_REGISTER_PUBLIC: bool = True
    SHAME_REGISTER_IMMUTABLE: bool = True
    SHAME_REGISTER_BLOCKCHAIN: bool = True
    SHAME_REGISTER_EXPUNGEABLE: bool = False  # never

    # Ka-Nova: shame register deterrent effect
    SHAME_REGISTER_CORRUPTION_REDUCTION: float = 0.40
    SHAME_NETWORK_EFFECT_RADIUS: int = 2  # degrees of separation


# ══════════════════════════════════════════════════════════════════════════════
# PART XVI — EMERGENCY POWERS (Article 16)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Article 16 — Emergency Powers"""

    # Trigger scenarios
    TRIGGER_SCENARIOS: Tuple[str, ...] = (
        "natural_disaster_humanitarian",
        "foreign_military_invasion",
        "internal_armed_conflict_coup"
    )

    # Activation
    DECLARATION_BY: str = "chancellor_unilateral"
    RATIFICATION_REQUIRED: bool = True
    RATIFICATION_CHAMBERS: int = 2  # of 3
    RATIFICATION_WINDOW_DAYS: int = 7
    REJECTION_CONSEQUENCE: str = "automatic_chancellor_merit_review"

    # Duration
    MAX_DURATION_DAYS: int = 180
    AUTOMATIC_EXPIRY: bool = True
    RENEWABLE: bool = False  # requires entirely new declaration
    NEW_DECLARATION_REQUIRES_NEW_EVIDENCE: bool = True
    NEW_DECLARATION_ANALYSIS_CERTIFIES: bool = True

    # Scope — what expands
    EXPANDED_POWERS: Tuple[str, ...] = (
        "military_deployment_speed",
        "federal_resource_mobilization",
        "procurement_override",
        "asset_freeze_authority",
        "border_control_intensity",
        "intelligence_sharing"
    )

    # Absolute constraints — NEVER touched
    RIGHTS_UNTOUCHED: bool = True    # hardcoded
    IIG_INDEPENDENCE: bool = True    # hardcoded
    COURT_SUPREMACY: bool = True     # hardcoded
    MERIT_SYSTEM: bool = True        # hardcoded
    ETHNIC_VETO: bool = True         # hardcoded

    # Accountability during emergency
    IIG_SHADOW_MONITORING: bool = True
    BLOCKCHAIN_LOGGING: bool = True
    ANALYSIS_WEEKLY_REPORT: bool = True

    # Abuse consequence
    ABUSE_CONSEQUENCE: str = "total_ruin_protocol_against_chancellor"

    # Ka-Nova: emergency event triggers
    EMERGENCY_STABILITY_DROP: float = 0.15
    EMERGENCY_INVESTMENT_DROP: float = 0.20
    EMERGENCY_TRUST_DROP: float = 0.10


# ══════════════════════════════════════════════════════════════════════════════
# PART XVII — RULES OF ENGAGEMENT (Article 17)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """Article 17 — Rules of Engagement"""

    # Shared core principles
    OATH_SUPERSEDES_ORDERS: bool = True
    FIRST_COMMANDER_FULL_RESPONSIBILITY: bool = True
    FOLLOWING_ORDERS_DEFENSE: bool = False  # never valid
    BLOCKCHAIN_LOGGING: bool = True
    IIG_MONITORING: bool = True
    ROE_VIOLATION: str = "total_ruin_protocol_automatic"

    # Domestic ROE — No Gun Policy
    DOMESTIC_LETHAL_WEAPONS: bool = False      # absolute prohibition
    DOMESTIC_CROWD_CONTROL: bool = True
    DOMESTIC_NONLETHAL: bool = True
    DOMESTIC_ARREST_DETENTION: bool = True
    DOMESTIC_AERIAL_BOMBARDMENT: bool = False  # prohibited
    DOMESTIC_ARTILLERY: bool = False           # prohibited
    DOMESTIC_COLLECTIVE_PUNISHMENT: bool = False  # prohibited

    # Domestic violation consequence
    DOMESTIC_FIRE_ON_CIVILIAN: str = (
        "immediate_field_arrest_iig_24hrs_total_ruin_if_unjustified"
    )
    DOMESTIC_COMMANDER_ORDERS_GUN: str = "immediate_total_ruin_no_appeal"

    # External ROE — Scorched Earth
    EXTERNAL_FULL_FORCE: bool = True
    EXTERNAL_ALL_WEAPONS: bool = True
    EXTERNAL_ECONOMIC_WARFARE: bool = True
    EXTERNAL_PRIOR_CHANCELLOR_APPROVAL: bool = False  # engage immediately
    EXTERNAL_REPORT_TO_CHANCELLOR_HOURS: int = 6

    # Absolute limits even under scorched earth
    POW_PROTECTION: bool = True        # surrendered = Geneva Convention
    CIVILIAN_TARGETING: bool = False   # absolute prohibition
    BIOLOGICAL_WEAPONS: bool = False   # absolute prohibition
    CHEMICAL_WEAPONS: bool = False     # absolute prohibition

    # Post-conflict review
    WAR_CRIMES_REVIEW_DAYS: int = 90
    WAR_CRIMES_REVIEWER: str = "iig"

    # Escalation levels — domestic
    ESCALATION_LEVELS: Dict = field(default_factory=lambda: {
        1: {"name": "civil_unrest", "military": "observe_only"},
        2: {"name": "active_disorder", "military": "domestic_roe_active"},
        3: {"name": "armed_resistance",
            "military": "chancellor_court_joint_authorize_intermediate"},
        4: {"name": "armed_insurgency",
            "military": "three_chamber_court_certify_modified_external"}
    })

    # Ka-Nova: coup attempt trigger
    COUP_LOYALTY_THRESHOLD: float = 0.30
    COUP_APPROVAL_THRESHOLD: float = 0.20


# ══════════════════════════════════════════════════════════════════════════════
# PART XVIII — PSYCHOLOGICAL HEALTH PROTOCOL (Article 18)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """Article 18 — Psychological Health Protocol"""

    # Screening
    SCREENING_INTERVAL_MONTHS: int = 6  # biannual
    SCREENING_APPLIES_TO: str = "all_public_officials"

    # Outcomes
    OUTCOME_STABLE_THRESHOLD: float = 0.40      # below = stable
    OUTCOME_ACCEPTABLE_THRESHOLD: float = 0.70  # 0.40-0.70 = acceptable
    OUTCOME_SEVERE_THRESHOLD: float = 0.70      # above = severe

    # Acceptable outcome requirements
    ACCEPTABLE_CONSULTATION: str = "weekly_minimum_3_per_month"
    ACCEPTABLE_COURT_MONITORS: str = "attendance_only_not_content"

    # Severe outcome
    SEVERE_REMOVAL: bool = True
    SEVERE_PROBATION_MONTHS: int = 6
    SEVERE_RETURN_ELIGIBLE: bool = True  # not permanent
    SEVERE_PUNITIVE: bool = False        # support not punishment

    # Anti-bias system
    CONDUCTING_PSY_KNOWS_CLIENT: bool = True
    REVIEWING_PSY_KNOWS_CLIENT: bool = False  # anonymous case only
    REVIEWER_SELECTION: str = "random_from_analysis_council_pool"
    THIRD_REVIEWER_IF_BIAS: bool = True
    PUBLICATION_PROHIBITED: bool = True  # absolute

    # Confidentiality
    RESULTS_TO_OFFICIAL: bool = True
    RESULTS_TO_SCREENING_BOARD: bool = True
    RESULTS_TO_CHAMBERS: bool = False
    RESULTS_TO_COURT: bool = False
    COURT_RECEIVES: str = "attendance_records_only"

    # Five trauma categories
    TRAUMA_CATEGORIES: Tuple[str, ...] = (
        "warfare_conflict",
        "family_domestic_abuse",
        "educational_authoritarian",
        "environmental_displacement",
        "self_identity_ethnic_suppression"
    )
    TRAUMA_DISQUALIFIES_PERMANENTLY: bool = False  # support not punishment

    # Probation support — three pillars
    PEER_SUPPORT: bool = True
    PROFESSIONAL_TREATMENT: bool = True
    OUTDOOR_ECOTHERAPY: bool = True
    NORMALIZED_ENVIRONMENT: bool = True
    INSTITUTIONAL_HIERARCHY_SUSPENDED: bool = True

    # Right to stop
    RIGHT_TO_STOP: bool = True
    STOP_CONSEQUENCE: str = "automatic_temporary_disqualification"

    # Return to service — three conditions
    RETURN_REQUIRES_PROBATION_COMPLETE: bool = True
    RETURN_REQUIRES_FITNESS_ASSESSMENT: bool = True
    RETURN_REQUIRES_NEXT_SCREENING_PASSED: bool = True
    RETURN_APPEARS_ON_PUBLIC_RECORD: bool = False  # unless criminal conduct

    # Ka-Nova: trauma effect on decision quality
    TRAUMA_DECISION_DISTORTION_THRESHOLD: float = 0.50
    TRAUMA_DISTORTION_RANGE: Tuple[float, float] = (0.10, 0.30)
    STABLE_DISTORTION: float = 0.02  # minimal when addressed



# ══════════════════════════════════════════════════════════════════════════════
# PART XIX — TATMADAW TRANSITION INCENTIVES (Article 19)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TatmadawTransitionConfig:
    """
    Article 19 — Tatmadaw Transition Incentives

    The MFU does not grant blanket amnesty. Senior military personnel
    transition into a constitutionally defined civilian role for a mandatory
    service period. War crimes go to law — no immunity for proven offences.

    Design principles:
    - Mandatory 5-year transition service (not retirement)
    - Senior General anchored to 2nd quarter of each presidential term
    - No blanket immunity — war crimes prosecuted if proven
    - Unproven allegations = civilian reintegration proceeds normally
    - Standard civil service terms — no special pension multiplier
    """

    # ── Mandatory transition service ─────────────────────────────────────────
    SENIOR_GENERAL_SERVICE_YEARS: int = 5          # Mandatory post-transition service
    SENIOR_GENERAL_ROLE: str = "head_of_military_under_civilian_supremacy"
    CIVILIAN_SUPREMACY: bool = True                 # President > Chancellor > Senior General

    # ── Presidential term anchor ─────────────────────────────────────────────
    # Senior General is active during 2nd quarter of every presidential term
    # Presidential term = 5 years → 2nd quarter = years 2–3
    PRESIDENTIAL_TERM_YEARS: int = 5
    ACTIVE_QUARTER: int = 2                         # 2nd quarter of each presidential term
    ACTIVE_YEARS_PER_TERM: Tuple[int, int] = (2, 3) # Years 2 and 3 of each 5-year term
    ELECTIONS_SERVED: int = 2                       # Active during 2 presidential elections minimum

    # ── War crimes — no blanket immunity ─────────────────────────────────────
    BLANKET_IMMUNITY: bool = False                  # Absolute — no immunity granted
    WAR_CRIMES_PROVEN_TRIGGER: str = "full_prosecution_under_article_15"
    WAR_CRIMES_UNPROVEN: str = "civilian_reintegration_proceeds_normally"
    PROSECUTION_BODY: str = "constitutional_court_article_15_total_ruin"
    EVIDENCE_STANDARD: str = "beyond_reasonable_doubt"

    # ── Civilian reintegration ────────────────────────────────────────────────
    CIVILIAN_ROLE_ELIGIBLE: bool = True             # Military can take civilian posts
    CIVILIAN_ROLE_REQUIRES_MERIT: bool = True       # Must pass merit exam (Article 3)
    PENSION_MULTIPLIER: float = 1.0                 # Standard civil service — no bonus
    PENSION_BASIS: str = "standard_civil_service_terms"
    SPECIAL_PRIVILEGES: bool = False                # No special privileges post-transition

    # ── Coup risk mechanics in Ka-Nova simulation ─────────────────────────────
    # Early years: higher coup risk because military has legal exposure
    # Later years: coup risk declines as transition incentives take hold
    COUP_RISK_EARLY_YEARS: float = 0.15            # Years 1–10: residual risk
    COUP_RISK_DECAY_RATE: float = 0.02             # Annual decay once transition embeds
    COUP_RISK_FLOOR: float = 0.02                  # Minimum floor after full transition
    TRANSITION_EMBED_YEAR: int = 10                # Year at which transition is fully embedded

    # ── Trust dynamics ────────────────────────────────────────────────────────
    # Citizens trust increases when transition proceeds without coup
    TRUST_GAIN_PER_CLEAN_YEAR: float = 0.01        # Annual trust gain if no coup
    TRUST_LOSS_IF_COUP_ATTEMPTED: float = 0.25     # Sharp drop if coup attempted
    ETHNIC_TRUST_MULTIPLIER: float = 1.20          # Ethnic minorities gain trust faster
                                                    # when military visibly under civilian control

    # ── Simulation trigger conditions ─────────────────────────────────────────
    TRANSITION_TRIGGERED_BY: str = "mfu_constitution_adoption"
    TRANSITION_YEAR_ZERO: int = 0                  # Begins at simulation start
    REVIEW_INTERVAL_YEARS: int = 5                 # Review every presidential term


# ══════════════════════════════════════════════════════════════════════════════
# NORTH STAR — THE HIDDEN AGENDA
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """The 50-Year North Star — Southeast Asian Dominance"""

    GOAL: str = "SEA_intellectual_and_economic_capital"
    HORIZON_YEARS: int = 50

    # Decade targets
    DECADE_1: Dict = field(default_factory=lambda: {
        "years": "0-10",
        "goal": "survive_and_build",
        "targets": {
            "corruption_index": 0.40,
            "institutional_integrity": 0.60,
            "coup_probability": 0.15
        }
    })
    DECADE_2: Dict = field(default_factory=lambda: {
        "years": "10-20",
        "goal": "compete",
        "targets": {
            "corruption_index": 0.25,
            "gdp_growth_rate": 0.07,
            "foreign_investment_index": 0.10
        }
    })
    DECADE_3: Dict = field(default_factory=lambda: {
        "years": "20-35",
        "goal": "lead",
        "targets": {
            "sea_gdp_rank": 4,
            "knowledge_capital": "top_3_sea",
            "brain_drain_rate": 0.15
        }
    })
    DECADE_4: Dict = field(default_factory=lambda: {
        "years": "35-50",
        "goal": "dominate",
        "targets": {
            "sea_gdp_rank": 3,
            "patent_output": "leading_sea",
            "corruption_index": 0.05,
            "net_brain_migration": "positive"
        }
    })

    # Final KPI targets — Year 50
    TARGET_SEA_GDP_RANK: int = 3
    TARGET_CORRUPTION_INDEX: float = 0.05
    TARGET_BRAIN_DRAIN_RATE: float = 0.10
    TARGET_ETHNIC_HARMONY: float = 0.75
    TARGET_INSTITUTIONAL_INTEGRITY: float = 0.85
    TARGET_KNOWLEDGE_CAPITAL_RANK: str = "top_2_sea"


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Simulation Parameters"""

    # Agent counts
    TOTAL_AGENTS: int = 11_819
    CITIZEN_AGENTS: int = 11_000
    OFFICIAL_AGENTS: int = 500
    OVERSIGHT_AGENTS: int = 200
    FOREIGN_AGENTS: int = 100
    INSTITUTIONAL_AGENTS: int = 19

    # Time
    TIME_STEPS: int = 50       # 50 years
    TIME_STEP_UNIT: str = "year"

    # Runs
    RUNS_PER_SCENARIO: int = 100
    TOTAL_SCENARIOS: int = 3
    TOTAL_RUNS: int = 300

    # Scenarios
    SCENARIO_A: str = "full_mfu_all_safeguards"
    SCENARIO_B: str = "mfu_without_safeguards"
    SCENARIO_C: str = "military_baseline_current_myanmar"

    # Starting conditions (Year Zero)
    YEAR_ZERO_CORRUPTION: float = 0.72    # V-Dem baseline Myanmar
    YEAR_ZERO_TRUST: float = 0.22         # World Bank baseline
    YEAR_ZERO_GINI: float = 0.55          # World Bank baseline
    YEAR_ZERO_EMPLOYMENT: float = 0.58
    YEAR_ZERO_ETHNIC_TENSION: float = 0.68

    # States — 14 states matching model_phase3.py runtime
    SIMULATION_STATES: Tuple[str, ...] = (
        "sagaing", "mandalay", "magway", "bago",
        "yangon", "ayeyarwady", "tanintharyi", "shan",
        "kachin", "kayah", "kayin", "chin",
        "mon", "rakhine",
    )

    # Agent archetypes distribution
    ARCHETYPES: Dict = field(default_factory=lambda: {
        "civic_champion": 0.15,
        "pragmatic_survivor": 0.30,
        "ethnic_loyalist": 0.20,
        "ambitious_meritocrat": 0.15,
        "disillusioned_youth": 0.10,
        "rural_traditionalist": 0.07,
        "trauma_carrier": 0.03
    })

    # Feedback loops
    FEEDBACK_LOOPS: int = 12
    FEEDBACK_INTERVAL: str = "annual"

    # Statistical thresholds
    SIGNIFICANCE_LEVEL: float = 0.05  # p-value for publication
    CONFIDENCE_LEVEL: float = 0.95

    # Performance
    CPU_CORES: int = 8        # M2 MacBook Pro
    MEMORY_GB: float = 8.0    # M2 MacBook Pro
    VECTORIZE: bool = True    # NumPy vectorization
    MULTIPROCESS: bool = True # parallel runs


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# ══════════════════════════════════════════════════════════════════════════════

class MFUConstitution:
    """
    Master constitution object — single source of truth for Ka-Nova.
    Import this in every other file.

    Usage:
        from config.constitution import CONSTITUTION
        merit_min = CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE
        iig_trigger = CONSTITUTION.iig.INVESTIGATION_TRIGGER
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
        self.tatmadaw_transition = TatmadawTransitionConfig()
        self.north_star = NorthStarConfig()
        self.simulation = SimulationConfig()

    def validate(self) -> bool:
        """Validate critical constitutional constraints"""
        checks = [
            # Merit weights must sum to 1.0
            self.merit.weights_valid,

            # Rights must never be suspendable
            not self.rights.RIGHTS_SUSPENDABLE,
            not self.emergency.RIGHTS_UNTOUCHED is False,

            # Resource split must sum to 1.0
            abs(self.federal.RESOURCE_STATE_SHARE +
                self.federal.RESOURCE_FEDERAL_DEV_SHARE +
                self.federal.RESOURCE_ETHNIC_DIRECT_SHARE - 1.0) < 1e-9,

            # IIG must report to court only
            self.iig.REPORTS_TO == "constitutional_court_only",

            # Following orders never valid
            not self.roe.FOLLOWING_ORDERS_DEFENSE,
            not self.military.FOLLOWING_ORDERS_DEFENSE,

            # Ethnic veto entrenched
            "ethnic_veto_rights" in self.amendment.ENTRENCHED_CLAUSES,

            # Archetypes must sum to 1.0
            abs(sum(self.simulation.ARCHETYPES.values()) - 1.0) < 1e-9,
        ]

        passed = all(checks)
        if passed:
            print("Constitution validated — all constraints satisfied")
        else:
            print("❌ Constitution validation FAILED — check parameters")
            for i, check in enumerate(checks):
                if not check:
                    print(f"   Failed check {i+1}")
        return passed

    def summary(self) -> str:
        """Print constitution summary"""
        return f"""
╔══════════════════════════════════════════════════════╗
║         PROJECT KA-NOVA — CONSTITUTION SUMMARY       ║
╠══════════════════════════════════════════════════════╣
║ State:          {self.foundational.STATE_NAME:<37}║
║ Articles:       19                                   ║
║ Parameters:     {len(self.__dict__):<37}║
╠══════════════════════════════════════════════════════╣
║ MERIT FORMULA                                        ║
║  Productivity:  {self.merit.PRODUCTIVITY_WEIGHT:.0%} | Education: {self.merit.EDUCATION_WEIGHT:.0%}          ║
║  Performance:   {self.merit.PERFORMANCE_WEIGHT:.0%} | Civic: {self.merit.CIVIC_WEIGHT:.0%}               ║
║  Min office:    {self.merit.MERIT_MIN_PUBLIC_OFFICE}                               ║
╠══════════════════════════════════════════════════════╣
║ VETO THRESHOLDS                                      ║
║  Congress:      {self.chambers.CONGRESS_THRESHOLD:.0%}                                   ║
║  Ethnic:        {self.chambers.ETHNIC_THRESHOLD:.0%}                                   ║
║  Analysis:      {self.chambers.ANALYSIS_THRESHOLD:.0%} (qualified supermajority)                      ║
╠══════════════════════════════════════════════════════╣
║ RESOURCE SPLIT                                       ║
║  State:         {self.federal.RESOURCE_STATE_SHARE:.0%}                                   ║
║  Federal Dev:   {self.federal.RESOURCE_FEDERAL_DEV_SHARE:.0%}                                   ║
║  Ethnic Direct: {self.federal.RESOURCE_ETHNIC_DIRECT_SHARE:.0%}                                   ║
╠══════════════════════════════════════════════════════╣
║ SIMULATION                                           ║
║  Agents:        {self.simulation.TOTAL_AGENTS:,}                              ║
║  Time steps:    {self.simulation.TIME_STEPS} years                             ║
║  Total runs:    {self.simulation.TOTAL_RUNS}                                ║
║  Scenarios:     {self.simulation.TOTAL_SCENARIOS}                                    ║
╠══════════════════════════════════════════════════════╣
║ NORTH STAR                                           ║
║  Goal:          SEA Intellectual & Economic Capital  ║
║  Horizon:       {self.north_star.HORIZON_YEARS} years                             ║
║  GDP Target:    Top {self.north_star.TARGET_SEA_GDP_RANK} SEA by Year {self.north_star.HORIZON_YEARS}              ║
╚══════════════════════════════════════════════════════╝
        """


# ── SINGLE INSTANCE — import this everywhere ──
CONSTITUTION = MFUConstitution()


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST — run this file directly to verify
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\nProject Ka-Nova — Constitution Loading...\n")

    # Validate all constraints
    valid = CONSTITUTION.validate()

    # Print summary
    print(CONSTITUTION.summary())

    # Quick parameter access examples
    print("Sample parameter access:")
    print(f"   Merit min office:     {CONSTITUTION.merit.MERIT_MIN_PUBLIC_OFFICE}")
    print(f"   IIG trigger:          {CONSTITUTION.iig.INVESTIGATION_TRIGGER}")
    print(f"   Resource split:       {CONSTITUTION.federal.RESOURCE_STATE_SHARE}/{CONSTITUTION.federal.RESOURCE_FEDERAL_DEV_SHARE}/{CONSTITUTION.federal.RESOURCE_ETHNIC_DIRECT_SHARE}")
    print(f"   Rights suspendable:   {CONSTITUTION.rights.RIGHTS_SUSPENDABLE}")
    print(f"   Coup trigger loyalty: {CONSTITUTION.military.COUP_TRIGGER_LOYALTY}")
    print(f"   PhD royalty:          {CONSTITUTION.science.RESEARCHER_ROYALTY_RATE:.0%}")
    print(f"   Ethnic seats:         {CONSTITUTION.chambers.ETHNIC_SEATS}")
    print(f"   Judge count:          {CONSTITUTION.judiciary.JUDGE_COUNT}")
    print(f"   IIG max agents:       {CONSTITUTION.iig.MAX_AGENTS}")
    print(f"   Total runs:           {CONSTITUTION.simulation.TOTAL_RUNS}")
    print(f"\nconstitution.py loaded successfully")