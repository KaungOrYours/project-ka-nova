"""
================================================================================
PROJECT KA-NOVA
config/constitution_chile.py

Chile 1980 Constitution, as reformed by the 1989 plebiscite (54 reforms) —
Parameter Registry for Ka-Nova Scenario CL ("Chile 1990-2005").

INSTRUMENT ENCODED: state (b) of the four materially-different states of the
1980 Constitution identified in the research package — the ELECTED-CONGRESS
era (11 March 1990 - September 2005), NOT the 1981-1990 Junta/transitory-
article era (state (a)). This is the instrument whose article numbers the
Georgetown PDBA 1989-reform text uses and whose reserved-power-enclave
mechanisms (designated senators, COSENA, Art. 93 commander irremovability,
Art. 81(c) COSENA-appointed Tribunal seats) are the load-bearing features
for this project's comparative design. Confirmed locked decision, see
.claude/memory.md section 4a decision 4 and config/scenario_registry.py's
own CL entry comment. chain_type = "civilian" (elected Congress, not a
Junta directly legislating) per that same confirmation.

Source: config/constitution_chile_encoding/README.md (senior-researcher,
2026-10-20), itself built from the Georgetown University Political Database
of the Americas 1980-Constitution-with-1989-reforms Spanish text
(https://pdba.georgetown.edu/Constitutions/Chile/chile89.html), V-Dem v16,
TI CPI, World Bank WGI, and Powell & Thyne coup data. Every article citation
below traces to that package; every CONFIDENT/GUESS tag below mirrors that
package's own honest-limitation flags (L1-L8) and is carried forward
verbatim where applicable.

HEADLINE FINDING THIS FILE MUST NOT OBSCURE (package's own words): Chile is
a near-twin to Myanmar 2008 on constitutional TEXT (Art. 90's "garantizan el
orden institucional" is near-verbatim to Myanmar 2008 s.20(f)) but an
ANTI-twin on OUTCOME — V-Dem political corruption under this instrument
(0.283 in 1981, 0.055-0.075 from 1990) is lower than democratic South
Korea's (0.458-0.512), CPI 1995 ranks Chile above the USA/France/Japan,
zero coups in 45 years, and the constitution is still in force after two
rejected replacement referenda. Parameters below are sourced to reflect
THIS real record, not reflexively copied from constitution_2008.py's
failure-baseline values. See research package flags F1 (near-twin/anti-twin
framing) and F2 (do not copy Scenario C's IIG parameters) before changing
anything in IIGConfig or EconomicConfig.

Structural template: config/constitution_2008.py (the confirmed 86-field
engine contract, zero gaps, per .claude/memory.md bug #11's field-parity
backfill). Same 20 section classes + master class, same CONFIDENT/GUESS
inline-tagging convention. Two additions specific to this civilian-chain
module, per bug #11's documented non-obvious requirements:
  (a) a `tatmadaw_transition` section (exact attribute name — read
      literally by model_phase3.py:521 regardless of country; the engine
      field name is Myanmar-specific, the content below is Chile-specific,
      repurposed for Chile's real 1990-2005 civilian/military power-sharing
      erosion culminating in the 2005 Law 20,050 reforms);
  (b) `ELITE_ROLE_TITLES` / `ELITE_SYSTEM_PROMPTS` module-level-attribute
      hooks read by engine/elite_agents_v3.py, supplying Chile's real
      elite cast (state (b) roster from the research package's section 3)
      instead of the generic MFU-flavoured fallback prose.

Author: Claude Code (constitutional encoding), architecture owner Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER I — BASES OF INSTITUTIONALITY (Articles 1-9)
# Maps to: constitution.py / constitution_2008.py → FoundationalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Chapter I — Bases de la Institucionalidad"""

    # CONFIDENT — Chile's official name is uncontested and not separately
    # re-derived in the research package (same treatment as both template
    # files give their own STATE_NAME).
    STATE_NAME: str = "Republic of Chile"

    # GUESS — the 1980 Constitution (as read for this package) does not
    # textually declare an official language; Spanish is the de facto
    # national language. No Art. 1-9 citation exists for this field.
    OFFICIAL_LANGUAGE: str = "Spanish"
    # CONFIDENT — the 1980 Constitution makes NO mention of indigenous
    # peoples at all (research package §4, flag L8). Constitutional
    # recognition of the Mapuche and other peoples was precisely what the
    # 2022 replacement draft proposed and voters rejected (62% in 2022).
    # This is the single clearest structural non-fit with MFU/Myanmar's
    # own ethnic-language-protection framing — flagged here rather than
    # forced into a positive value.
    ETHNIC_LANGUAGES_PROTECTED: bool = False

    # CONFIDENT — uncontested seat of government.
    CAPITAL: str = "Santiago"
    FLAG: str = "chilean_national_flag"

    # GUESS — citizenship-mode categories; not addressed in the research
    # package, no article citation located. Reasonable modelling proxy
    # only, not load-bearing to the paper's argument.
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "birth_on_soil",
        "parent_citizen",
        "naturalization_residency",
    )
    NATURALIZATION_YEARS: int = 5          # GUESS — not sourced
    NATURALIZATION_MERIT_MIN: float = 0.0  # CONFIDENT direction — no merit exam for naturalization is documented anywhere in the package

    # GUESS — territory-basis descriptor, modelling convenience, not a
    # literal citation (cf. both template files' own equivalent fields).
    TERRITORY_BASIS: str = "thirteen_regions_1980_division"
    # CONFIDENT — Art. 45 (verbatim, quoted in research package): "en
    # consideración a las trece regiones del país." Chile had 13 regions
    # under this instrument; the 16-region configuration is a later change
    # and would be an anachronism for 1990-2005.
    STATE_COUNT: int = 13
    # FIXED 2026-10-20 (research package §6.2, flag F2): this was a
    # Myanmar leftover at 14, carried over from constitution_2008.py's own
    # field before the per-country-geography work existed. Chile's real
    # regionalisation (DL 575 of 1974, completed 1976) was exactly 13
    # regions for the entire 1990-2005 encoded window — Los Ríos (2007),
    # Arica y Parinacota (2007) and Ñuble (2018) all postdate it. Now set
    # to 13, matching STATE_COUNT above and SimulationConfig.
    # SIMULATION_STATES below, which has also been repopulated with
    # Chile's own real region names (see that field's comment for the
    # full population-weight sourcing). The old "kept at 14 for
    # consistency with model_phase3.py's still-Myanmar-hardcoded
    # _initialize_states()" rationale no longer applies now that
    # SIMULATION_STATES itself carries real Chilean names — a parallel
    # fix to model_phase3.py's state dict is required for this to be
    # live end-to-end (see .claude/memory.md §5 bug #16's deliberately-
    # deferred scope and config/constitution.py's own cross-file-
    # constraint comment); that file is outside this agent's scope
    # (owned by a parallel effort tonight) and is not touched here.
    SIMULATION_STATE_COUNT: int = 13


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER III — RIGHTS AND DUTIES (Article 19) + STATES OF EXCEPTION (39-41)
# Maps to: constitution.py / constitution_2008.py → RightsConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Article 19 (rights catalogue) + Articles 20-21 (remedies) + Article 41 (non-justiciability)"""

    # CONFIDENT — Art. 19 No.1 (life/physical integrity), No.2-3 (equality,
    # legal defence), No.15 (association/parties), No.24 (property);
    # Art. 20 (recurso de protección) and Art. 21 (recurso de amparo) are
    # real judicial remedies on paper.
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "right_to_life_and_physical_integrity",   # Art. 19 No.1
        "right_to_equality_before_law",            # Art. 19 No.2-3
        "right_to_association_and_parties",        # Art. 19 No.15
        "right_to_property",                       # Art. 19 No.24
        "recurso_de_proteccion",                    # Art. 20
        "recurso_de_amparo",                        # Art. 21
    )

    # CONFIDENT — package explicit recommendation, grounded in Art. 39-41:
    # rights ARE suspendable/restrictable under the four states of
    # exception, and Art. 41's non-justiciability clause ("Los tribunales
    # de justicia no podrán, en caso alguno, entrar a calificar los
    # fundamentos...") removes judicial review of the factual grounds —
    # this clause is in the PERMANENT text, not a transitory article, and
    # is the Chilean analogue of Myanmar 2008's finality clauses.
    RIGHTS_SUSPENDABLE: bool = True
    RIGHTS_ABSOLUTE_COUNT: int = 0
    EMERGENCY_TOUCHES_RIGHTS: bool = True
    # CONFIDENT — Art. 41, quoted verbatim in the research package.
    EMERGENCY_GROUNDS_NON_JUSTICIABLE: bool = True

    # GUESS — Chile's real, long-standing compulsory military service
    # (Servicio Militar Obligatorio) is a well-documented statutory fact,
    # but the research package's Art. 19 catalogue extraction does not
    # cite a specific article number for it (unlike Myanmar's Section 386,
    # which the package's Myanmar-equivalent file cites directly). Encoded
    # as a real-world fact with an honest sourcing gap, not fabricated to
    # match a constitutional citation that was not located.
    NATIONAL_SERVICE_MANDATORY: bool = True
    NATIONAL_SERVICE_AGE: int = 18
    NATIONAL_SERVICE_DURATION_MONTHS: int = 12

    # GUESS — no Section-382-equivalent citation located for a specific
    # rights override of Defence Services personnel; loosely grounded in
    # the Code of Military Justice's wide statutory jurisdiction over
    # civilians noted in the research package's MilitaryConfig section
    # (itself flagged there as statutory, not constitutional).
    MILITARY_RIGHTS_OVERRIDE: bool = True

    # GUESS magnitude, CONFIDENT direction — Ka-Nova simulation parameters
    # (not literal constitutional text, same framing both template files
    # use for their own equivalent fields). Set BETWEEN MFU's (0.25/0.20,
    # rights-are-absolute-so-a-violation-is-a-huge-deal) and Myanmar
    # 2008's (0.05/0.08, protest-is-suppressed-so-the-reaction-is-dampened)
    # values: under this instrument rights exist and ARE sometimes
    # enforced (recurso de protección/amparo are real, functioning
    # remedies for most of 1990-2005), so a violation is a genuine, but
    # not maximal, shock — reflecting a nominally rights-protected but
    # enclave-constrained democracy, not an MFU-style absolute system or
    # a Myanmar-style fully suppressed one.
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.15
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.12

    # ── Dynamics constants surfaced for disclosure and sensitivity analysis ──
    # Added 2026-10-21 (Openings 1 and 8), same values as every other
    # constitution, so behaviour is unchanged (verified byte-identical across
    # all 7 scenarios). These are Ka-Nova MODELLING choices, not provisions of
    # this real constitution, and are marked as such deliberately: they exist
    # here so the Sobol GSA can perturb them on the scenario that actually
    # reads them. FEAR_COMPLIANCE_TRUST_FLOOR binds only on a military chain,
    # so for Thailand and Pakistan this is the field that lets the GSA
    # quantify Reviewer 1 pt.2 for the trust effect size.
    FEAR_COMPLIANCE_TRUST_FLOOR: float = 0.10
    CIVILIAN_COUP_SIGNAL_DAMPING: float = 0.05
    STABILITY_RIGHTS_BONUS: float = 0.20


# ══════════════════════════════════════════════════════════════════════════════
# NO CONSTITUTIONAL MERIT-EXAM SYSTEM
# Maps to: constitution.py / constitution_2008.py → MeritConfig
# Chile's real selection mechanisms are popular election (President,
# Congress), judicial self-co-optation + presidential choice (judiciary,
# Art. 75), and COSENA/presidential/Supreme-Court appointment (designated
# senators, two Tribunal seats) — none of which maps onto a "merit formula"
# concept at all. Modelled as neutral/undifferentiated rather than
# loyalty-dominant (contrast Myanmar 2008's CIVIC_WEIGHT=0.55 loyalty
# skew) because there is no documented loyalty-to-a-single-regime
# selection criterion under an ELECTED Congress — this is a genuine
# structural difference from Myanmar 2008's framing, not an oversight.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """No merit-exam system — election + institutional appointment replace it"""

    # GUESS — equal weights, a deliberate modelling placeholder (NOT an
    # attempt to fabricate a Chile-specific weighting scheme) signalling
    # "no merit formula exists; the real selection mechanisms are election
    # and institutional appointment, which the engine's merit-formula
    # concept cannot represent." Sums to 1.0 for schema validity.
    PRODUCTIVITY_WEIGHT: float = 0.25
    EDUCATION_WEIGHT: float = 0.25
    PERFORMANCE_WEIGHT: float = 0.25
    CIVIC_WEIGHT: float = 0.25

    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    MERIT_MIN_PUBLIC_OFFICE: float = 0.0   # CONFIDENT direction — no merit minimum documented; election/appointment control access

    # CONFIDENT — Art. 25/26 (presidential election), Art. 75 (judicial
    # self-co-optation from a Supreme-Court-proposed slate).
    EXAM_ADMINISTRATOR: str = "none_electoral_and_institutional_appointment"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 0
    EXAM_RESULTS_PUBLISH_DAYS: int = 0

    # CONFIDENT — Art. 9 (terrorism, 15-year disqualification from public
    # office/teaching/media/union leadership) and Art. 48-49 (impeachment
    # conviction disqualifies 5 years). GENUINELY INTERESTING CONTRAST:
    # unlike MFU (DISQUALIFICATION_PERMANENT=True) and Myanmar 2008
    # (same), BOTH of Chile's documented disqualification triggers are
    # TIME-LIMITED, not permanent.
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "terrorism_conviction_art9_15yr_disqualification",
        "impeachment_conviction_art49_5yr_disqualification",
        "breach_of_constitution",
    )
    DISQUALIFICATION_PERMANENT: bool = False   # CONFIDENT — both cited triggers are time-limited (15yr / 5yr), not permanent

    RECERTIFICATION_INTERVAL: int = 0          # CONFIDENT — no recertification cycle exists under this instrument
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.0
    RECERTIFICATION_VACATE_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER IV — GOVERNMENT / PRESIDENT OF THE REPUBLIC (Articles 24-32)
# Maps to: constitution.py / constitution_2008.py → ExecutiveConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Chapter IV — Gobierno (Articles 24-32)"""

    PRESIDENT_ROLE: str = "head_of_state_and_executive"              # CONFIDENT — Art. 24
    PRESIDENT_ELECTION: str = "direct_popular_vote_absolute_majority_runoff"  # CONFIDENT — Art. 26
    PRESIDENT_TERM: int = 8                                           # CONFIDENT — Art. 25 (1989 text, state (b))
    PRESIDENT_MAX_TERMS: int = 1                                       # CONFIDENT — Art. 25, no IMMEDIATE re-election
    # CONFIDENT-with-caveat — Art. 25 bans immediate consecutive
    # re-election only; NON-consecutive re-election after an intervening
    # term is permitted (research package §1). The engine's single
    # PRESIDENT_REELECTION flag cannot represent that nuance, so this is
    # encoded conservatively as False since immediate-term re-election was
    # the operative constraint for every president across 1990-2005.
    PRESIDENT_REELECTION: bool = False

    PRESIDENT_TIEBREAKER: bool = False      # CONFIDENT — has full executive power, not a tiebreaker role
    PRESIDENT_EXECUTIVE_POWER: bool = True  # CONFIDENT — Art. 24

    CHANCELLOR_ROLE: str = "none"           # CONFIDENT — package explicit: "No prime minister"
    CHANCELLOR_ELECTION: str = "none"
    CHANCELLOR_TERM: int = 0
    CHANCELLOR_MAX_TERMS: int = 0
    CHANCELLOR_COOLING_OFF: int = 0

    PRESIDENT_ELECTION_YEAR: int = 1
    CHANCELLOR_ELECTION_YEAR: int = 0

    MINISTER_COUNT: int = 18                # GUESS — not constitutionally fixed; proxy from typical 1990s Chilean cabinet size
    MINISTER_MERIT_MIN: float = 0.0         # CONFIDENT direction — presidential appointment, no merit exam
    MINISTER_CONFIRMATION: str = "president_appointment_no_legislative_confirmation"  # GUESS — standard presidential-system fact, not separately cited

    # CONFIDENT for the two package-cited portfolios (Minister of the
    # Interior, Art. 33, the state-of-exception enforcement ministry; and
    # Minister of Finance, Art. 32, the Chicago-School economic programme's
    # locus); GUESS for the remainder (reasonable, not separately sourced).
    MINISTRIES: Tuple[str, ...] = (
        "ministry_of_interior",
        "ministry_of_finance",
        "ministry_of_foreign_affairs",
        "ministry_of_national_defence",
        "ministry_of_justice",
        "ministry_of_education",
        "ministry_of_economy",
    )

    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 0   # no Chancellor exists
    CHANCELLOR_DISMISSAL_VETO: bool = False
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = False

    PRESIDENT_REMOVAL_CHAMBERS: int = 2               # CONFIDENT — Art. 48 (Chamber accuses) / Art. 49 (Senate convicts) = 2 chambers
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = False   # no Chancellor
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = False  # no Analysis-Council-equivalent evidentiary gate feeds impeachment
    # CONFIDENT direction, GUESS exact float — Art. 48 requires a MOTION by
    # "not fewer than 10 and not more than 20" of 120 deputies (8.3%-16.7%),
    # a FIXED HEADCOUNT, not a fraction; the research package explicitly
    # flags this schema mismatch ("note it, because the schema expects a
    # float"). Midpoint of the real range used as the float proxy.
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.125
    # GUESS — Ka-Nova simulation parameter; Chile's real impeachment
    # mechanism (Art. 48-49) is NOT keyed to a "trust index" concept at
    # all (it requires specific grave-offence findings), so this field has
    # no textual citation. Kept at the same value as MFU/Myanmar's own
    # equivalent (Ka-Nova-only) field for comparability rather than
    # inventing an unsourced different number.
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.20

    # GUESS — no specific succession-article citation located in the
    # research package (Art. 29 governs succession but was not quoted);
    # flagged honestly rather than inventing an article-level citation.
    CHANCELLOR_INTERIM: str = "constitutional_line_of_succession_not_separately_verified"


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER V — NATIONAL CONGRESS (Articles 43-49, 95-96, 116)
# Maps to: constitution.py / constitution_2008.py → ChamberConfig
# THE DESIGNATED-SENATOR MECHANISM IS CHILE'S RESERVED-POWERS INSTRUMENT
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Chapter V — Congreso Nacional (Articles 43-49)"""

    # CONFIDENT — Art. 43 (120-member Chamber of Deputies, direct district
    # vote); Art. 45 (senatorial constituencies); binominal system is
    # statutory (not constitutional text) but entrenched behind the
    # organic-law supermajority per the research package.
    CONGRESS_ELECTION: str = "direct_district_and_senatorial_constituency_binominal_system"
    CONGRESS_THRESHOLD: float = 0.51       # GUESS-by-convention — ordinary-bill majority; no specific citation beyond the Art. 116 amendment thresholds
    CONGRESS_TERM: int = 4                 # CONFIDENT — Art. 43: Chamber of Deputies renews in full every 4 years
    CONGRESS_REELECTION: bool = True       # CONFIDENT — Art. 47: deputies/senators may be re-elected

    # Field names kept identical to constitution_2008.py's contract
    # (Myanmar-specific naming — MILITARY_RESERVED_SEATS_PYITHU/_AMYOTHA —
    # repurposed here for Chile's lower/upper chamber structure).
    # CONFIDENT — Art. 43: Chamber of Deputies has NO reserved seats, all
    # 120 are directly elected.
    MILITARY_RESERVED_SEATS_PYITHU: int = 0
    # CONFIDENT — Art. 45: nine designated senators (lifetime ex-Presidents
    # + 2 former Supreme Court ministers + 1 former Contralor General +
    # (per secondary sources, research package flag L1, NOT independently
    # verified against the Biblioteca del Congreso Nacional) former
    # service commanders, a former university rector, a former Minister of
    # State).
    MILITARY_RESERVED_SEATS_AMYOTHA: int = 9
    # CONFIDENT direction, GUESS-reconciled magnitude — the research
    # package itself quotes TWO different percentages for the same real
    # fact without reconciling them: "~26%" (comparing 9 designated against
    # the ORIGINAL 1980 text's 26-elected-senator, 13-constituency Senate:
    # 9/35 = 25.7%) in its near-twin-framing narrative, versus its own
    # explicit final encoding instruction to use "~0.19 of the Senate
    # (9/47)" (the 1989-reform 38-elected-senator, 19-constituency Senate:
    # 9/47 = 19.15%) in the ChamberConfig encoding section. This file
    # follows the package's EXPLICIT FINAL INSTRUCTION (9/47, the 1989-text
    # Senate actually in force 1990-2005, consistent with the 38-elected
    # figure used elsewhere in the same package) — flagging the package's
    # own internal 26%-vs-19% inconsistency here rather than silently
    # picking one without comment. Denominator used: SENATE ONLY (47),
    # not the whole Congress (9/167 = 0.054) — stated explicitly per the
    # package's own instruction to "say which denominator you used."
    MILITARY_SEAT_PERCENTAGE: float = 0.1915
    MILITARY_SEATS_APPOINTED_BY: str = "president_supreme_court_and_national_security_council"  # CONFIDENT — Art. 45(a)-(c) + COSENA route

    # CONFIDENT direction — no Ethnic Leaders Council analogue exists; the
    # 1980 Constitution makes no mention of indigenous peoples (L8, see
    # FoundationalConfig.ETHNIC_LANGUAGES_PROTECTED above). ETHNIC_SEATS
    # confirmed (via direct grep of the live engine, 2026-10-20) to not be
    # read anywhere outside this schema, so setting it to 0 carries no
    # crash risk. ETHNIC_THRESHOLD/_TERM/_MAX_TERMS/_PRESIDENTIAL_MIN_TERMS
    # kept at the same non-functional placeholder values constitution_2008.py
    # uses for its own equivalent absent mechanism, rather than fabricating
    # Chile-specific numbers for something that does not exist in either
    # country's real text.
    ETHNIC_SEATS: int = 0
    ETHNIC_THRESHOLD: float = 0.51
    ETHNIC_TERM: int = 4
    ETHNIC_MAX_TERMS: int = 99
    ETHNIC_PRESIDENTIAL_MIN_TERMS: int = 99

    # No Analysis Council equivalent. Mapped onto the Constitutional
    # Tribunal (Art. 81-82), the closest institutional analogue for a
    # constitutional-review veto body.
    ANALYSIS_THRESHOLD: float = 1.00   # GUESS — Art. 81-82 does not specify an internal voting threshold in the package; unanimous-equivalent proxy, same idiom as Myanmar's Tribunal mapping
    ANALYSIS_VETO_TIME_LIMIT: int = 90  # GUESS — not cited; reused generic value
    ANALYSIS_MERIT_MIN: float = 0.0     # CONFIDENT direction — Tribunal appointees are COSENA/President/Supreme-Court/Senate nominees (Art. 81), not merit-tested
    ANALYSIS_TERM: int = 8              # CONFIDENT — Art. 81: Tribunal members serve staggered eight-year terms

    # GUESS magnitude, CONFIDENT direction — Ka-Nova simulation parameter.
    # No single service commander votes as a unified bloc the way
    # Myanmar's 110+56 commander-nominated seats do (Chile's designated
    # senators are a mixed civilian/military/judicial group, not a single
    # military voting bloc), so this is set LOWER than Myanmar's 1.0.
    MILITARY_BLOC_VOTE_DISCIPLINE: float = 0.60
    CIVILIAN_EFFECTIVE_MAJORITY_NEEDED: float = 0.60  # CONFIDENT — mirrors Art. 116's own 3/5 standard-amendment threshold, the real practical bar civilian majorities had to clear


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER VI — JUDICIAL POWER (Articles 75-82)
# Maps to: constitution.py / constitution_2008.py → JudiciaryConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Chapter VI — Poder Judicial (Art. 75-77) + Chapter VII — Tribunal Constitucional (Art. 81-82)"""

    # CONFIDENT — package's own explicit recommendation: "COURT_INDEPENDENCE:
    # False for state (a)/(b), justified on the Art. 81(c) COSENA
    # appointment route and Art. 41's non-justiciability of emergency
    # grounds" — NOT a general claim that Chilean courts were broadly
    # corrupt or ineffective (see COURT_CORRUPTION_RESISTANCE below, which
    # is deliberately encoded as a SEPARATE, much higher value: these two
    # facts coexist in the real data and should not be collapsed into one
    # number).
    COURT_INDEPENDENCE: bool = False
    # CONFIDENT — Art. 81: Constitutional Tribunal has seven members.
    # Pointed the narrative Supreme-Court-bench-size field at this SAME
    # number deliberately: the research package does not give a verified
    # historical Supreme Court bench size, while the Tribunal's seven-seat
    # composition is the number doing real analytical work in this design
    # (the COSENA appointment channel below).
    COURT_JUDGES_COUNT: int = 7
    COURT_TERM_YEARS: int = 8              # CONFIDENT — Art. 81: staggered eight-year terms
    RULING_THRESHOLD: int = 4              # GUESS-by-convention — simple majority of 7; no specific quorum rule cited

    # GUESS magnitude, CONFIDENT direction — the research package flags
    # this as "partial": military courts (Code of Military Justice,
    # statutory not constitutional) had wide jurisdiction over civilians,
    # and Art. 41 bars judicial review of emergency grounds, but there is
    # no Myanmar-s.293(b)-style textual "final and conclusive" clause for
    # military justice specifically.
    MILITARY_JUSTICE_FINAL: bool = True
    CIVILIAN_COURT_OVERRIDE_MILITARY: bool = False

    CONSTITUTIONAL_TRIBUNAL_SIZE: int = 7   # CONFIDENT — Art. 81 (duplicate of COURT_JUDGES_COUNT above, kept for narrative/documentation consistency per constitution_2008.py's own precedent)
    TRIBUNAL_TERM_YEARS: int = 8            # CONFIDENT — Art. 81

    # GUESS magnitude, CONFIDENT direction — deliberately set HIGH,
    # contrasting directly with Myanmar 2008's 0.20, because the real
    # V-Dem data for this era shows judicial constraints at .915-.958 and
    # rule of law at .940-.958 (research package §2.3) — genuinely strong
    # by any standard, even though COURT_INDEPENDENCE above is correctly
    # False at the narrow Art. 81(c) COSENA-appointment-channel level.
    # These are NOT contradictory: a narrow guardianship appointment
    # channel into 2 of 7 Tribunal seats coexists with a broadly
    # functioning, rule-of-law-respecting judiciary overall. Encoding them
    # as two separate fields rather than collapsing to one number is a
    # deliberate modelling choice central to this scenario's whole point
    # (see module docstring's headline finding).
    COURT_CORRUPTION_RESISTANCE: float = 0.75
    TOTAL_RUIN_THRESHOLD: float = 0.0       # CONFIDENT — no Total Ruin mechanism exists under this constitution

    JUDGE_COUNT: int = 7                    # CONFIDENT — live-engine-read field (agents/oversight.py), mirrors COURT_JUDGES_COUNT above
    JUDGE_TERM: int = 8                      # CONFIDENT — Art. 81, mirrors COURT_TERM_YEARS above
    # GUESS — no re-appointment-eligibility rule for Tribunal members is
    # addressed in the research package; Supreme Court judges separately
    # serve until the Art. 77 retirement age of 75 (not a "term" count at
    # all). Modelled as "one continuous appointment," same idiom
    # constitution_2008.py uses for its own equivalent unsourced field.
    JUDGE_MAX_TERMS: int = 1
    # GUESS — no constitutionally-fixed judiciary budget protection
    # located in the research package (contrast Art. 97-98's explicit
    # central-bank fiscal-independence language, which IS cited and IS
    # encoded as True in EconomicConfig below). Absent a specific
    # citation, this is NOT assumed to mirror the central bank's strength.
    BUDGET_FIXED: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# CONTRALORÍA GENERAL DE LA REPÚBLICA (Articles 87-89)
# Maps to: constitution.py / constitution_2008.py → IIGConfig
# CHILE GENUINELY HAS A STRONG ANTI-CORRUPTION / FISCAL-CONTROL BODY —
# research package flag F2: DO NOT copy Scenario C's weak-IIG parameters
# here by reflex. The Contraloría has an EX ANTE legality veto over
# executive expenditure acts (Art. 88's "tomar razón" power), unlike
# Myanmar 2008's absent body and unlike a reactive, score-triggered
# investigator model.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """Contraloría General de la República — Articles 87-89"""

    # GUESS — moderate, not zero: Contraloría functionaries are career
    # civil servants with a real professional-competence expectation, but
    # no literal "merit exam" citation exists in the package. Deliberately
    # NOT set to Myanmar's 0.0 (loyalty-only entry), per flag F2.
    ENTRY_MERIT: float = 0.50
    ACADEMY_MONTHS: int = 0                 # CONFIDENT direction — no dedicated academy pathway documented
    # CONFIDENT direction, GUESS magnitude — deliberately LOWER than
    # Myanmar's 0.90 (reactive, regime-threatening-only) AND at least as
    # sensitive as MFU's own 0.45, because Art. 87-88's real mechanism is
    # EX ANTE and UNIVERSAL (every decree is reviewed for legality before
    # taking effect — "tomar razón"), not triggered by a corruption SCORE
    # at all. The float here is a necessary proxy for a review mechanism
    # that structurally does not wait for a threshold to be crossed; see
    # research package flag F2.
    INVESTIGATION_TRIGGER: float = 0.30
    # CONFIDENT direction, GUESS magnitude — per flag F2's explicit
    # instruction ("INITIAL_EFFECTIVENESS high"), grounded in WGI Control
    # of Corruption +1.45 (1996) — among the strongest in this project's
    # entire comparator set, higher than South Korea ever records.
    EFFECTIVENESS_FLOOR: float = 0.55
    REPORTS_TO: str = "autonomous_constitutional_organ"   # CONFIDENT — package's exact recommended value, Art. 87
    CHAMBER_ELIGIBLE: bool = False          # GUESS — not specifically cited; conservative default matching a professional/non-partisan civil-service ethos

    ANTI_CORRUPTION_OBJECTIVE: bool = True   # CONFIDENT — direct reading of Art. 87's text (control of legality, fiscalisation of public funds)
    REGIME_PROTECTION_OBJECTIVE: bool = False  # CONFIDENT — opposite of Myanmar 2008's framing; no textual basis for a regime-protection mandate

    INITIAL_EFFECTIVENESS: float = 0.60     # CONFIDENT direction / GUESS magnitude — "high," per flag F2
    MAX_EFFECTIVENESS: float = 0.85         # CONFIDENT direction / GUESS magnitude — well above Myanmar's 0.15 ceiling, below MFU's own 1.0 ceiling (no textual basis for claiming Chile's real body exceeds the engine's own self-designed best case)

    ENTRY_MERIT_MIN: float = 0.50           # CONFIDENT — mirrors ENTRY_MERIT above (live field name)
    ENTRY_MIN_AGE: int = 21                 # GUESS — not sourced; plausible civil-service entry age
    ACADEMY_DURATION_MONTHS: int = 0        # CONFIDENT — mirrors ACADEMY_MONTHS above (no academy exists)
    # GUESS — the Contralor General is appointed by the President WITH
    # Senate agreement (Art. 87) and is a COSENA voting member under the
    # 1989 text; no fixed personal term length for the position is cited
    # in the research package. Set moderate, not tied to the President's
    # 8-year term (the office is not politically synchronised to a single
    # presidency).
    DIRECTOR_TERM: int = 10
    DIRECTOR_RENEWABLE: bool = False        # GUESS direction — consistent with a professionally-insulated, non-partisan office; not separately cited
    PARTNER_ELIGIBILITY_YEARS: int = 5      # GUESS — no Partnership Council / seniority-gated body exists under this instrument; reused generic placeholder
    OPEN_INVESTIGATION_THRESHOLD: float = 0.30   # CONFIDENT direction / GUESS magnitude — mirrors the ex ante INVESTIGATION_TRIGGER logic above; no two-stage evidentiary process documented, collapsed to the same low, sensitive bar (contrast Myanmar's collapse to the SAME HIGH bar — opposite directions, same "no graduated process" modelling idiom)
    PROCEED_PROSECUTION_THRESHOLD: float = 0.30
    PARTNERSHIP_COUNCIL_QUORUM: float = 1.0      # GUESS — no Partnership Council concept exists; models "the Contraloría's own authority is sufficient," same idiom as Myanmar's equivalent field
    CHAMBER_ELIGIBLE_POST_SERVICE: bool = False  # GUESS — not specifically cited; conservative default
    PERMITTED_POST_SERVICE: Tuple[str, ...] = (  # GUESS — reasonable proxy paths, not textually enumerated in the package
        "judiciary",
        "academic_institutions",
        "state_administration",
    )
    # GUESS — real headcount not documented in the research package;
    # Chile's Contraloría is a relatively lean professional body, set well
    # below Myanmar's speculative 2000 and closer to (but not identical
    # to) MFU's own self-designed 600, reflecting a smaller real civil
    # service compared to MFU's purpose-built design.
    MAX_AGENTS: int = 400
    FUNCTIONAL_DIVISIONS: Tuple[str, ...] = (   # GUESS — invented for simulation structure; not named in the 1980 text
        "legality_audit_division",
        "financial_examination_division",
        "accounting_division",
    )
    MANDATE_DIVISIONS: Tuple[str, ...] = (
        "administrative_legality_division",
        "public_funds_fiscalisation_division",
        "municipal_oversight_division",
    )
    OPERATIONAL_DIVISIONS: Tuple[str, ...] = (
        "tomar_razon_review_division",       # CONFIDENT — Art. 88's ex ante review function
        "national_accounts_division",        # CONFIDENT — Art. 87's "llevará la contabilidad general de la Nación"
        "expenditure_decree_control_division",  # CONFIDENT — Art. 88's expenditure-limit clause
    )


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XIII — GOVERNMENT AND INTERNAL ADMINISTRATION (Articles 99-115)
# Maps to: constitution.py / constitution_2008.py → FederalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Chapter XIII — Gobierno y Administración Interior del Estado (Art. 99-115)"""

    STATE_COUNT: int = 13           # CONFIDENT — Art. 45, mirrors FoundationalConfig above
    ETHNIC_GROUPS: int = 0           # CONFIDENT — no constitutional ethnic-group recognition exists (L8)

    # GUESS — package explicit: "No constitutional revenue-sharing formula
    # → RESOURCE_*_SHARE values are proxies." Modelled as heavily
    # centralised (unitary state, PRESIDENTIALLY-appointed intendants and
    # governors throughout this era — Art. 99-115; directly elected
    # regional governors only began in 2021, outside this file's window).
    # No "ethnic direct share" concept exists at all (L8); kept low as a
    # non-functional placeholder rather than fabricated.
    RESOURCE_STATE_SHARE: float = 0.15
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.70
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.15

    # GUESS — Ka-Nova simulation parameter; no constitutional
    # redistribution-trigger mechanism exists in Chile's real text either,
    # but for a different real reason than Myanmar's (ideological
    # free-market/subsidiarity commitment, Art. 1 and Art. 19 No.21, rather
    # than crony-extraction tolerance).
    GINI_THRESHOLD: float = 0.60
    STATE_GDP_CAP: float = 0.80      # GUESS — no cap textually exists; Santiago dominance is a real economic-geography fact, not addressed by the Constitution

    # CONFIDENT-for-this-era — intendants/governors were PRESIDENTIAL
    # appointees throughout 1990-2005 (Art. 99-115), but under
    # DEMOCRATICALLY ELECTED presidents from March 1990 these were
    # civilian political appointees, not military officers as a matter of
    # course (contrast the authoritarian-phase practice, which is outside
    # this file's encoded window).
    MILITARY_IN_REGIONAL_EXECUTIVE: bool = False

    # CONFIDENT direction, GUESS magnitude — Art. 19 No.21(2)'s
    # qualified-quorum-law requirement for state business activity is a
    # GENUINELY enforced legal norm under this instrument (reviewable by
    # the Constitutional Tribunal), unlike Myanmar 2008's documented
    # unenforced version. NOT nullified to 1.0.
    SECTOR_MONOPOLY_CAP: float = 0.30

    # DELIBERATE DIVERGENCE from both template files' nullification idiom
    # — flagged explicitly rather than silently copied. MFU's Article VIII
    # trust-acceleration "virtuous cycle" has no textual Chilean analogue,
    # but UNLIKE Myanmar 2008 (whose real corruption trajectory was flat
    # and bad, correctly nullified), Chile's REAL corruption trajectory
    # over this exact window was falling fast and substantially (V-Dem
    # political corruption 0.283 in 1981 to 0.067 in 1990 to 0.061 by
    # 1997, research package §2.3) — nullifying this mechanic the same way
    # Myanmar's file does would risk UNDERSTATING the real, empirically
    # documented positive trajectory this scenario exists to capture (see
    # module docstring's headline finding and flag F1). Set REACHABLE,
    # GUESS magnitude / CONFIDENT direction (reachable, not nullified):
    TRUST_ACCELERATION_TRIGGER_CORRUPTION: float = 0.30
    TRUST_ACCELERATION_TRIGGER_YEARS: int = 3
    TRUST_ACCELERATION_MULTIPLIER: float = 1.25


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER X — ARMED FORCES, FORCES OF ORDER AND NATIONAL SECURITY COUNCIL
# (Articles 90-96)
# Maps to: constitution.py / constitution_2008.py → MilitaryConfig
# THE GUARDIANSHIP CORE — Chile's near-twin-on-text case for Myanmar 2008
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Chapter X — Fuerzas Armadas, de Orden y Seguridad Pública, y COSENA (Art. 90-96)"""

    # CONFIDENT — package explicit: "No coup clause. Chile's 1980
    # Constitution contains no emergency transfer of all powers to the
    # Commander-in-Chief equivalent to Myanmar 2008 ss. 417-419. The
    # guardianship works through tutelary organs (COSENA, designated
    # senators, Tribunal seats, irremovability), NOT through a coup
    # authorisation." This is the single most important field in this
    # file for the near-twin/anti-twin distinction.
    COUP_LEGAL_MECHANISM: bool = False
    # CONFIDENT direction — nullified via parameter value (same idiom
    # constitution_2008.py uses elsewhere for mechanisms that do not
    # apply), since COUP_LEGAL_MECHANISM above is already False: there is
    # no constitutional pathway these thresholds could ever legally
    # trigger, so they are set unreachable rather than given a real-but-
    # moot number.
    COUP_TRIGGER_CORRUPTION: float = 1.0
    COUP_TRIGGER_TRUST: float = 0.0

    COMMANDER_IN_CHIEF_APPOINTMENT: str = "president_from_five_most_senior_four_year_irremovable"  # CONFIDENT — Art. 93, package's exact recommended value
    # CONFIDENT-with-caveat — package explicitly flags this "partial":
    # military courts (Code of Military Justice, statutory) had wide
    # jurisdiction over civilians, and Art. 41 bars judicial review of
    # emergency grounds, but this is not a clean, single textual grant the
    # way Myanmar's s.293(b)/343(b) is.
    MILITARY_SELF_ADJUDICATION: bool = True

    # CONFIDENT direction — Art. 93 names FOUR separately appointed,
    # separately irremovable service commanders (Army, Navy, Air Force,
    # Carabineros Director General), each serving their own 4-year,
    # non-renewable term — NOT one unified Commander-in-Chief of all
    # Defence Services the way Myanmar's single-chain structure is. The
    # President nominally commands all four via Art. 32, but the
    # OPERATIONAL irremovability protection is per-service, not unified.
    # This is a genuine structural difference worth preserving, not
    # collapsed into Myanmar's single-chain framing.
    SINGLE_CHAIN_OF_COMMAND: bool = False

    # CONFIDENT — Art. 90 (verbatim, research package): "...son esenciales
    # para la seguridad nacional y garantizan el orden institucional de la
    # República." THIS is the clause the research package identifies as
    # the near-verbatim textual match to Myanmar 2008 s.20(f)/6(f) — the
    # strongest single piece of near-twin-on-TEXT evidence in this file.
    MILITARY_POLITICAL_ROLE: bool = True

    # CONFIDENT direction / GUESS exact magnitude-reconciliation — see the
    # extensive ChamberConfig.MILITARY_SEAT_PERCENTAGE comment above for
    # the full 9/47-vs-9/35 discrepancy this field inherits. Mirrored here
    # for narrative consistency (not independently re-derived).
    PARLIAMENTARY_SEAT_PERCENTAGE: float = 0.1915
    PARLIAMENTARY_SEAT_APPOINTMENT: str = "president_supreme_court_and_national_security_council"

    # GUESS magnitude, CONFIDENT direction — Ka-Nova simulation parameters,
    # not literal citations. Set HIGH initial loyalty (the Chilean military
    # entered the 1990 transition as a victor in a negotiated, not
    # collapsed, handover — it lost the 1988 plebiscite but was not
    # defeated or discredited the way Myanmar's regime's own legitimacy
    # narrative requires) but with a MEANINGFULLY FASTER decay toward
    # civilian supremacy than Myanmar's near-zero decay, consistent with
    # the real, documented 1990-2005 erosion of military prerogatives
    # culminating in the 2005 Law 20,050 reforms (see
    # TatmadawTransitionConfig below).
    LOYALTY_INITIAL: float = 0.80
    LOYALTY_CORRUPTION_DRAG: float = 0.01
    # CONFIDENT direction — nullified-toward-zero but NOT identical to
    # Myanmar's literal 0.0 "military IS the regime" framing (Chile's
    # military is institutionally embedded via COSENA/designated-senator
    # tutelary organs, not literally the executive). Set very low, not
    # exactly zero, reflecting a real-but-small theoretical coup-probability
    # channel consistent with COUP_LEGAL_MECHANISM=False above.
    COUP_PROBABILITY_MULTIPLIER: float = 0.02

    # GUESS — package does not address a Chile-specific Art. 40(b)-style
    # domestic-force-authorisation clause in detail; modelled consistent
    # with Art. 90's role in "guaranteeing institutional order" and the
    # states-of-exception machinery (EmergencyConfig below), not as an
    # independently sourced citation.
    DOMESTIC_FORCE_AUTHORIZED: bool = True
    DOMESTIC_FORCE_TRIGGER: str = "president_with_cosena_agreement_under_states_of_exception"

    # CONFIDENT direction / GUESS exact value — live-engine-read field
    # (agents/official.py, feedback/loops.py P3 loop, engine/cves.py's L2
    # messaging). This mechanic models "when does a military with real
    # command authority turn against the civilian government" — a question
    # that is STRUCTURALLY MEANINGFUL for Chile (a real military, embedded
    # in reserved-power enclaves, within a civilian-chain scenario) in a
    # way it is NOT for Myanmar 2008 (where the military already IS the
    # executive, correctly nullified to 0.0 there). No Chile-specific
    # article citation justifies a DIFFERENT number from MFU's own
    # baseline civilian-chain assumption, so MFU's exact values are reused
    # rather than invented in either direction — deliberately NOT tuned
    # down to artificially immunise Chile against ever reaching high
    # coup_risk (that would hide the mechanism rather than let the real,
    # more favourable trust/approval trajectory this era documents speak
    # for itself through the SAME engine mechanic).
    COUP_TRIGGER_LOYALTY: float = 0.30
    COUP_TRIGGER_APPROVAL: float = 0.20

    # GUESS magnitude, CONFIDENT-by-partial-analogy — Chile's real,
    # long-standing compulsory military service is NOT documented in the
    # research package as carrying the same recently-politicised,
    # ethnic-minority-targeted controversy Myanmar's 2024 People's
    # Military Service Law does, so Myanmar's "coercion discount" logic is
    # NOT applied here. However, the "ethnic exposure" CONCEPT itself does
    # not map onto Chile's constitutional structure at all (no
    # constitutionally recognised ethnic groups, L8), so that specific
    # sub-field is kept low as a structural non-fit, not a coercion
    # penalty.
    NS_CIVILIAN_TRACK_THRESHOLD: float = 0.65
    NS_LOYALTY_BOOST: float = 0.10
    NS_ETHNIC_EXPOSURE_BOOST: float = 0.02     # low because the concept has no real referent here (L8), not because service is coercive
    NS_CIVIC_CONTRIBUTION_BOOST: float = 0.08


# ══════════════════════════════════════════════════════════════════════════════
# ECONOMIC FRAMEWORK (Article 19 No.21-25, Articles 97-98)
# Maps to: constitution.py / constitution_2008.py → EconomicConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Art. 19 No.21-25 (economic rights) + Art. 97-98 (Central Bank)"""

    ECONOMIC_SYSTEM: str = "open_market_with_subsidiarity_doctrine"   # CONFIDENT — Art. 1 (grupos intermedios/subsidiarity) + Art. 19 No.21
    TAX_BRACKETS: Tuple[float, ...] = (0.0, 0.05, 0.10, 0.15, 0.20)   # GUESS — not addressed in the research package
    BLACK_MONEY_PENALTY: str = "law_prescribed"                        # GUESS

    # GUESS-with-caveat — Chile's subsoil/mineral resources carry a real
    # state-ownership-plus-concession regime (the research package flags
    # the Ley Reservada del Cobre military-funding mechanism, Law 13,196,
    # but explicitly instructs "Verify the 10% figure and the 2019 repeal
    # date before quoting (L5)" — NOT independently verified here, so the
    # specific percentage is deliberately NOT quoted anywhere in this
    # file). STATE_OWNS_RESOURCES is set True for the general subsoil
    # principle only, not as endorsement of the unverified 10% figure.
    STATE_OWNS_RESOURCES: bool = True
    PRIVATE_PROPERTY_PROTECTED: bool = True   # CONFIDENT — Art. 19 No.24: expropriation only by law with prior cash compensation at market value

    # CONFIDENT direction — Art. 19 No.21(2)'s qualified-quorum-law
    # requirement is a GENUINELY ENFORCED restraint under this instrument
    # (Tribunal-reviewable), unlike Myanmar 2008's documented-unenforced
    # Section 36(b). Deliberately True with real enforcement, not the
    # Myanmar "on paper only" framing.
    ANTI_MONOPOLY: bool = True
    # CONFIDENT direction — no documented, sourced crony-tolerance
    # mechanism exists in Chile's constitutional text (contrast Myanmar
    # 2008's explicit, documented CRONY_CAPITAL_SHARE=0.40). Chile's real
    # grupos económicos concentration is a market-structure outcome, not a
    # constitutionally-sanctioned extraction channel — this is a
    # deliberate, important divergence from Myanmar's framing per research
    # package flags F1/F2.
    CRONYISM_ENABLED: bool = False
    NATIONALIZATION_BANNED: bool = True   # GUESS direction — consistent with the Pinochet-era privatisation programme; not a separately cited constitutional ban in the package

    # CONFIDENT direction, GUESS magnitude — deliberately LOW, directly
    # corroborated by V-Dem/CPI/WGI (research package §2.1-2.3): CPI 7.94
    # in 1995 (rank 14 of 41, above the USA/France/Japan), WGI Control of
    # Corruption +1.45 in 1996. Set far below Myanmar 2008's 0.03.
    CORRUPTION_GDP_DRAG: float = 0.005
    # CONFIDENT direction, GUESS magnitude — LOW, deliberately NOT equated
    # with Myanmar's documented military-crony extraction channel (see
    # CRONYISM_ENABLED above); real economic concentration exists but is
    # not textually a corrupt-extraction mechanism.
    CRONY_CAPITAL_SHARE: float = 0.05

    # GUESS — Chile's real restricted-sector history (telecoms, mining,
    # banking) partially overlaps Myanmar's list but is not separately
    # re-derived here; the Ley Reservada del Cobre (L5, unverified
    # percentage) is the one documented defence-linked resource-funding
    # mechanism worth flagging in this section.
    STRATEGIC_SECTORS: Tuple[str, ...] = (
        "mining_and_minerals",           # Ley Reservada del Cobre context, L5 — percentage NOT verified, not quoted
        "defence",
        "banking",
    )
    OPEN_SECTORS: Tuple[str, ...] = (
        "manufacturing",
        "retail",
        "agriculture",
        "services",
        "tourism",
    )
    FOREIGN_CAP_STRATEGIC: float = 0.49   # GUESS — not specifically cited
    FOREIGN_CAP_OPEN: float = 1.00        # GUESS — not specifically cited

    # CONFIDENT — Art. 97-98 (verbatim, research package): the Central
    # Bank of Chile is "un organismo autónomo con... rango constitucional
    # propio," prohibited from acquiring State-issued instruments or
    # granting credit to the State "salvo en caso de guerra exterior o
    # peligro de ella." A genuinely strong constitutional-independence
    # provision, comparable to MFU's own CENTRAL_BANK_INDEPENDENT=True and
    # in DIRECT CONTRAST to Myanmar 2008 (which has no such provision).
    CENTRAL_BANK_INDEPENDENT: bool = True
    CENTRAL_BANK_POLITICAL_DIRECTION: bool = False
    CENTRAL_BANK_ANNUAL_REPORT: bool = True     # GUESS — not specifically cited, reasonable accountability proxy
    CENTRAL_BANK_CHAMBERS_CAN_DIRECT: bool = False  # CONFIDENT — follows directly from Art. 98's lending prohibition


# ══════════════════════════════════════════════════════════════════════════════
# EDUCATION (Article 19 No.10-11)
# Maps to: constitution.py / constitution_2008.py → ScienceConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Art. 19 No.10 (right to education) + No.11 (freedom of teaching)"""

    PHD_TUITION_FREE: bool = False        # GUESS — not addressed in the research package
    RESEARCHER_ROYALTY: float = 0.0       # CONFIDENT direction — no royalty system cited; package explicit "no PhD-economy analogue"
    KNOWLEDGE_CAPITAL_GROWTH: float = 0.015  # GUESS — moderate, reflecting a functioning (if not purpose-built) higher-education system

    # CONFIDENT direction — the package's Art. 19 No.10-11 framing is
    # about individual educational rights and freedom of teaching, NOT a
    # Myanmar-s.28(d)-style explicit nation-building/nationalist education
    # mandate. Set False, a deliberate contrast.
    EDUCATION_NATIONALIST_FRAMING: bool = False

    BRAIN_DRAIN_RATE_BASE: float = 0.08   # GUESS — moderate-low, reflecting comparatively stronger institutions than Myanmar's documented 0.15
    # GUESS magnitude, CONFIDENT direction trend — university political
    # control (military-appointed rectors) was real and severe during the
    # 1980s authoritarian phase but substantially relaxed under elected
    # governments from 1990; mid-range value reflects a transition-era
    # average across 1990-2005, not either extreme.
    ACADEMIC_FREEDOM: float = 0.55

    RESEARCHER_ROYALTY_RATE: float = 0.0           # CONFIDENT — mirrors RESEARCHER_ROYALTY above
    PHD_KNOWLEDGE_CAPITAL_BOOST: float = 0.08       # GUESS — well below MFU's self-designed 0.25; no PhD-pipeline analogue exists


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER XIV — AMENDMENT (Articles 116-119)
# Maps to: constitution.py / constitution_2008.py → AmendmentConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Chapter XIV — Reforma de la Constitución (Art. 116-119)"""

    # CONFIDENT direction, GUESS exact float — Art. 116: reform bills may
    # be initiated "por mensaje del Presidente de la República o por
    # moción de cualquiera de los miembros del Congreso" — i.e. ANY single
    # member may initiate, no numeric threshold exists. Encoded as a low
    # proxy since the schema expects a float (same schema-mismatch idiom
    # as ExecutiveConfig.PRESIDENT_APPROVAL_REMOVAL_THRESHOLD above).
    AMENDMENT_INITIATION_THRESHOLD: float = 0.05

    ENTRENCHED_AMENDMENT_THRESHOLD: float = 0.667   # CONFIDENT — Art. 116: 2/3 for Chapters I, II, VII, XI, XIV
    # CONFIDENT — package's exact instruction: the Art. 117 plebiscite is
    # a PRESIDENTIAL OPTION on veto override, not a mandatory referendum
    # step.
    ENTRENCHED_REQUIRES_REFERENDUM: bool = False
    STANDARD_AMENDMENT_THRESHOLD: float = 0.60      # CONFIDENT — Art. 116: 3/5 for ordinary reforms

    # CONFIDENT — Ka-Nova-derived parameter, directly grounded in the
    # package's own comparative claim: "with 9 designated senators + the
    # binominal system, the right held a blocking minority against the 3/5
    # and 2/3 thresholds for 15 years. This is Chile's functional
    # equivalent of Myanmar's 25%-bloc amendment veto."
    MILITARY_VETO_ON_AMENDMENTS: bool = True

    ENTRENCHED_CHAPTERS: Tuple[str, ...] = (   # CONFIDENT — exact, per Art. 116 and the research package
        "chapter_1_bases_institucionalidad",
        "chapter_2_nationality_and_citizenship",
        "chapter_7_constitutional_tribunal",
        "chapter_11_armed_forces",
        "chapter_14_reform",
    )
    REVIEW_INTERVAL: int = 0    # CONFIDENT — no mandatory periodic review mechanism exists under this instrument (same dead-code-safety note as constitution_2008.py's own REVIEW_INTERVAL=0 field: institutions/court.py:63 is never actually reached in the live step() loop, see .claude/MINDMAP.md bug #12)
    # CONFIDENT-by-convention — no real Chilean civic-lottery mechanism
    # exists either; kept at the same canonical 320 value both template
    # files use, rather than inventing a different unsourced number for a
    # mechanism absent from all three countries' real texts.
    CITIZENS_ASSEMBLY_SIZE: int = 320


# ══════════════════════════════════════════════════════════════════════════════
# TRANSITORY ARTICLES (1981-1990) — THE HANDOVER INTO THE INSTRUMENT ENCODED
# Maps to: constitution.py / constitution_2008.py → TransitionConfig
# NOTE: these describe the 1981-1990 Junta/transitory-article period as the
# RUN-UP INTO the 1990-2005 elected-Congress instrument this file encodes —
# the same structural role constitution_2008.py's own TransitionConfig plays
# for the SPDC-to-2008-constitution handover, and constitution.py's plays for
# the caretaker-government-to-MFU handover. NOT a re-opening of the
# state-(a)-vs-state-(b) encoding choice (which is settled — see module
# docstring).
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """Transitory Articles 14-29 (1981-1990) — research package §1, flag L4 (not read verbatim)"""

    TRANSITION_PERIOD_YEARS: int = 9   # CONFIDENT — package explicit: 11 Mar 1981 to 11 Mar 1990

    # CONFIDENT — THE single most important, and most interesting,
    # TransitionConfig finding in this project (research package flag
    # F4): Chile's self-amnesty source is Decree Law 2,191 of 1978, a
    # DECREE LAW, not a constitutional provision — unlike Myanmar 2008
    # s.445, Thailand 2017 s.279 and Pakistan Art. 270A, which ALL put
    # regime immunity directly in the constitutional TEXT. Chilean courts
    # progressively disapplied DL 2,191 for crimes against humanity from
    # the late 1990s, and the Inter-American Court condemned it in
    # Almonacid Arellano v. Chile (2006). AMNESTY_GRANTED is True as a
    # historical fact (the decree law existed and was applied for ~20
    # years) but PRIOR_ACTIONS_IMMUNE below is set False, NOT True, to
    # reflect that this immunity was real-but-eroding and extra-
    # constitutional — the opposite framing from the other three
    # guardianship comparators in this project.
    AMNESTY_GRANTED: bool = True

    PRIOR_LAWS_VALID: bool = True       # GUESS-by-convention — standard for any successor constitutional order; not separately contradicted
    # CONFIDENT, with the F4 caveat above — deliberately False, not True.
    # See TATMADAW_IMMUNITY below for the mirrored field (the live-named
    # equivalent) and its extended comment.
    PRIOR_ACTIONS_IMMUNE: bool = False
    CIVIL_SERVANTS_RETAIN_POSTS: bool = True   # GUESS-by-convention — standard, not separately contradicted

    TATMADAW_PENSION: float = 0.0              # CONFIDENT — no special pension bonus mechanism documented
    # CONFIDENT — mirrors PRIOR_ACTIONS_IMMUNE above. THE key divergence
    # from Myanmar 2008 (True), Thailand 2017 and Pakistan (all
    # constitutionally-entrenched immunity, per research package flag
    # F4): Chile's self-amnesty is a decree law (DL 2,191/1978), not
    # constitutional text, and it was progressively disapplied by Chilean
    # courts and condemned by the Inter-American Court of Human Rights
    # (Almonacid Arellano v. Chile, 2006). Pinochet himself was arrested
    # in London in 1998 and faced domestic prosecution attempts — the
    # generals of this guardianship constitution were NOT permanently
    # shielded the way the field name's Myanmar-specific origin implies.
    TATMADAW_IMMUNITY: bool = False


# ══════════════════════════════════════════════════════════════════════════════
# NO MFU-STYLE CONSTITUTIONAL SAFEGUARDS — CHILE'S REAL FUNCTIONAL EQUIVALENTS
# Maps to: constitution.py / constitution_2008.py → SafeguardConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """No MFU-style safeguard package — Chile's real functional equivalents are the Contraloría, Central Bank, and designated-senator enclave"""

    # All MFU-specific safeguard mechanics are absent from this instrument
    # (no cooling-off rule, no rotating-panel merit exam, no ethnic-council
    # youth mandate, no IIG single-term rule, no generational-assembly
    # review as such). CONFIDENT direction for all six, same reasoning as
    # constitution_2008.py's own equivalent block.
    CHANCELLOR_COOLING_OFF_ENFORCED: bool = False
    MERIT_EXAM_INDEPENDENCE: bool = False
    ETHNIC_COUNCIL_YOUTH_MANDATE: bool = False
    IIG_SINGLE_TERM: bool = False
    ANALYSIS_TRANSPARENCY: bool = False
    RIGHTS_ABSOLUTE: bool = False               # CONFIDENT — Art. 41: rights can be suspended/restricted
    GENERATIONAL_ASSEMBLY_REVIEW: bool = False

    # Chile-specific REAL functional equivalents — the actual guardianship
    # and institutional-strength mechanisms this scenario tests, additive
    # to (not a copy of) constitution_2008.py's military-centric block.
    DESIGNATED_SENATOR_AMENDMENT_BLOCK: bool = True       # CONFIDENT — Art. 45 + Art. 116, the package's own "best comparative sentence"
    CONTRALORIA_EX_ANTE_LEGALITY_VETO: bool = True        # CONFIDENT — Art. 87-88
    COSENA_TRIBUNAL_APPOINTMENT_CHANNEL: bool = True      # CONFIDENT — Art. 81(c)
    CENTRAL_BANK_CONSTITUTIONAL_INDEPENDENCE: bool = True  # CONFIDENT — Art. 97-98 (mirrors EconomicConfig.CENTRAL_BANK_INDEPENDENT)

    ANALYSIS_PUBLISH_BEFORE_VETO_DAYS: int = 0   # CONFIDENT — follows from ANALYSIS_TRANSPARENCY=False above


# ══════════════════════════════════════════════════════════════════════════════
# NO CRYPTOGRAPHIC JUSTICE
# Maps to: constitution.py / constitution_2008.py → CryptoJusticeConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """No Chilean referent (research package flag L8) — mechanism nullified via parameter value"""

    BLOCKCHAIN_ENABLED: bool = False
    ZKP_ENABLED: bool = False
    MULTI_PARTY_SIGNATURES: bool = False
    TOTAL_RUIN_MECHANISM: bool = False
    TOTAL_RUIN_STEPS: int = 0

    COURT_SUPERMAJORITY_FOR_TOTAL_RUIN: int = 7   # CONFIDENT — equals JUDGE_COUNT (unanimous-equivalent), effectively unreachable, consistent with TOTAL_RUIN_MECHANISM=False above; same nullify-via-value idiom as constitution_2008.py
    SHAME_REGISTER_CORRUPTION_REDUCTION: float = 0.0  # CONFIDENT — no Shame Register mechanism exists


# ══════════════════════════════════════════════════════════════════════════════
# CHAPTER IV, SECTION — STATES OF EXCEPTION (Articles 39-41)
# Maps to: constitution.py / constitution_2008.py → EmergencyConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Articles 39-41 — Estados de Excepción Constitucional"""

    # CONFIDENT — Art. 39-40: the four real states of exception, verbatim
    # per the research package.
    TRIGGER_SCENARIOS: Tuple[str, ...] = (
        "estado_de_asamblea_external_war",
        "estado_de_sitio_internal_war_or_commotion",
        "estado_de_emergencia_public_order_disruption",
        "estado_de_catastrofe_public_calamity",
    )

    EMERGENCY_MAX_DAYS: int = 90        # CONFIDENT — Art. 40: estado de sitio, maximum 90 days per declaration (renewable)
    EMERGENCY_EXTENSIONS: int = 4       # GUESS — package confirms "renewable" but does not cite a specific extension count/cap
    EMERGENCY_EXTENSION_MONTHS: int = 3  # GUESS — not specifically bounded in the package

    RIGHTS_UNTOUCHED: bool = False      # CONFIDENT — Art. 41 explicitly restricts/suspends rights under declared states of exception
    # CONFIDENT — package explicit: "No total-power-transfer clause."
    TOTAL_POWER_TRANSFER_POSSIBLE: bool = False
    POWER_TRANSFER_TRIGGER: str = "not_applicable_no_total_transfer_clause"

    COMMANDER_IN_CHIEF_LEGISLATIVE: bool = False   # CONFIDENT — no such transfer exists
    COMMANDER_IN_CHIEF_EXECUTIVE: bool = False
    COMMANDER_IN_CHIEF_JUDICIAL: bool = False

    LEGISLATURE_SUSPENDED_DURING_EMERGENCY: bool = False   # CONFIDENT — package explicit

    # CONFIDENT — package's exact recommended field and value: Art. 40
    # requires COSENA's prior agreement for estado de asamblea, and allows
    # the President to impose estado de sitio immediately (while Congress
    # deliberates) ONLY with COSENA's prior agreement.
    EMERGENCY_REQUIRES_COSENA_AGREEMENT: bool = True
    # CONFIDENT, with the 0.50-of-members caveat the package specifies —
    # Congress may lift an approved estado de sitio at any time by
    # absolute majority of members in office in each chamber. Noted as a
    # WEAKER legislative kill-switch than e.g. South Korea's Art. 77(5),
    # because the President can impose immediately with only COSENA's
    # agreement before Congress ever votes.
    LEGISLATURE_CAN_LIFT: bool = True

    EMERGENCY_COUP_PROBABILITY_MULTIPLIER: float = 0.10   # GUESS magnitude, CONFIDENT direction — far below Myanmar's 1.0 full activation, consistent with COUP_LEGAL_MECHANISM=False above


# ══════════════════════════════════════════════════════════════════════════════
# RULES OF ENGAGEMENT — not addressed in detail by the research package
# Maps to: constitution.py / constitution_2008.py → ROEConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """No Chile-specific Art. 41/42-style ROE text located in the research package — GUESS throughout, not load-bearing to the paper's core near-twin/anti-twin argument"""

    FOREIGN_POLICY: str = "independent_foreign_policy_cold_war_western_aligned"  # GUESS
    NO_AGGRESSION: bool = True       # GUESS — standard default
    NO_FOREIGN_TROOPS: bool = True   # GUESS — standard default

    DOMESTIC_MILITARY_USE: str = "president_with_cosena_agreement_under_states_of_exception"  # GUESS, consistent with EmergencyConfig above
    DOMESTIC_FORCE_THRESHOLD: float = 0.20   # GUESS — moderate, not Myanmar's 0.05 broad-discretion framing (no equivalent textual grant located)

    EXTERNAL_ROE: str = "defensive_unless_declared_war"   # GUESS
    EXTERNAL_FULL_FORCE: bool = False   # GUESS direction — no "scorched earth" doctrine documented for Chile in the research package


# ══════════════════════════════════════════════════════════════════════════════
# NO PSYCHOLOGICAL HEALTH MANDATE
# Maps to: constitution.py / constitution_2008.py → PsychConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """No Chilean referent (research package flag L8) for a formal screening mandate — mechanism nullified via parameter value, but trauma fields reflect a real, documented history"""

    BIANNUAL_SCREENING: bool = False
    ANTI_BIAS_REVIEW: bool = False
    TRAUMA_CARE_MANDATED: bool = False

    # GUESS magnitude, CONFIDENT-by-partial-grounding — moderate, not as
    # high as Myanmar 2008's 0.45: the authoritarian phase's human-rights
    # record (torture, forced disappearance) is real and well documented,
    # but UNLIKE Myanmar's ongoing suppression, Chile's civilian era
    # (1990-2005) operated real truth commissions (Rettig, 1991; Valech,
    # 2004 — both referenced in the research package) providing some
    # acknowledgement and redress, which plausibly moderates the
    # population-level trauma baseline relative to a state with no such
    # process.
    POPULATION_TRAUMA_BASE: float = 0.30
    TRAUMA_ACCUMULATION_RATE: float = 0.01    # GUESS — lower than Myanmar's 0.02, reflecting the declining-conflict trajectory of this era
    ETHNIC_TRAUMA_MULTIPLIER: float = 1.0     # CONFIDENT direction — no constitutionally recognised ethnic groups exist (L8); multiplier nullified to no-op rather than fabricated

    SCREENING_INTERVAL_MONTHS: int = 9999      # CONFIDENT — mirrors BIANNUAL_SCREENING=False above, same "never triggers" idiom constitution_2008.py uses
    SEVERE_PROBATION_MONTHS: int = 9999
    OUTCOME_STABLE_THRESHOLD: float = 0.40     # CONFIDENT-by-convention — diagnostic-scale threshold, reused unchanged
    OUTCOME_SEVERE_THRESHOLD: float = 0.70
    STOP_CONSEQUENCE: str = "no_formal_consequence_mechanism_exists"   # CONFIDENT direction — same no-op idiom as constitution_2008.py, consistent with TRAUMA_CARE_MANDATED=False above
    TRAUMA_CATEGORIES: Tuple[str, ...] = (     # CONFIDENT-by-relevance — reused unchanged; arguably MORE applicable here given the real, documented 1973-1990 conflict/repression history
        "warfare_conflict",
        "family_domestic_abuse",
        "educational_authoritarian",
        "environmental_displacement",
        "self_identity_ethnic_suppression",
    )
    TRAUMA_DISTORTION_RANGE: Tuple[float, float] = (0.12, 0.35)   # GUESS magnitude — between MFU's (0.10, 0.30) and Myanmar's (0.20, 0.45) ranges, consistent with the moderate POPULATION_TRAUMA_BASE above


# ══════════════════════════════════════════════════════════════════════════════
# PART XIX-EQUIVALENT — CIVILIAN/MILITARY POWER-SHARING TRANSITION (1990-2005)
# Maps to: constitution.py → TatmadawTransitionConfig
# REQUIRED SECTION for civilian-chain modules (model_phase3.py:521 reads
# `self.CONSTITUTION.tatmadaw_transition.TRUST_GAIN_PER_CLEAN_YEAR` literally
# regardless of country). Field name is Myanmar-specific (engine-baked,
# accepted per task brief); CONTENT below is entirely Chile-specific,
# grounded in the real 1990-2005 erosion of military prerogatives
# (designated senators, COSENA, Art. 93 irremovability) culminating in the
# 2005 Law 20,050 reforms — the real Chilean analogue of "transitioning the
# military out of a constitutionally entrenched guardianship role."
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TatmadawTransitionConfig:
    """
    Chile's real 1990-2005 civilian/military power-sharing erosion.

    Design principles (contrast with MFU's self-designed Article 19):
    - No "mandatory transition service" concept exists in Chile's real
      text; Art. 93's service commanders instead serve fixed, non-renewable
      4-year terms with REAL irremovability protection (requiring COSENA
      agreement to override) for the duration of this file's 1990-2005
      window.
    - Civilian supremacy over military REMOVAL specifically is NOT yet
      achieved during this window — Art. 93's COSENA-agreement requirement
      is exactly the enclave this scenario exists to test. It becomes True
      only after the 2005 Law 20,050 reforms, which fall OUTSIDE this
      file's encoded 1990-2005 window.
    - Immunity is extra-constitutional (Decree Law 2,191/1978) and
      eroding, not constitutionally entrenched and absolute — mirrors
      TransitionConfig.TATMADAW_IMMUNITY=False above (flag F4).
    - A real post-service privilege DOES exist and is textually confirmed
      (Art. 45's former-service-commander-to-designated-Senate pathway) —
      the opposite of MFU's own "no special privileges" design choice.
    """

    SENIOR_GENERAL_SERVICE_YEARS: int = 4    # CONFIDENT — Art. 93: four-year, non-renewable term
    SENIOR_GENERAL_ROLE: str = "army_commander_in_chief_irremovable_without_cosena_agreement"  # CONFIDENT — Art. 93
    # CONFIDENT, deliberate divergence from MFU's own True — during THIS
    # file's 1990-2005 window, civilian supremacy over military removal
    # specifically is NOT yet achieved: Art. 93 requires COSENA's
    # agreement (a body with a real uniformed voting bloc, Art. 95) before
    # the President may retire a service commander. This becomes True only
    # after the 2005 Law 20,050 reforms, outside this window — exactly the
    # enclave mechanism this whole scenario exists to test.
    CIVILIAN_SUPREMACY: bool = False

    PRESIDENTIAL_TERM_YEARS: int = 8    # CONFIDENT — Art. 25, mirrors ExecutiveConfig.PRESIDENT_TERM above
    # GUESS-with-honest-mismatch-flag — MFU's "2nd quarter of each
    # presidential term" framing does NOT map cleanly onto Chile's real
    # structure: Art. 93 commanders serve 4-year non-renewable terms
    # against an 8-year presidential term, so a commander's relevance
    # spans roughly half of any given presidency, not a single stylised
    # quarter. Flagged here as an imperfect-fit field per the task's own
    # instruction ("flag it, don't force a bad fit") rather than
    # fabricating a precise quarter-mapping the real structure does not
    # support.
    ACTIVE_QUARTER: int = 0   # not meaningfully applicable; see comment above
    ACTIVE_YEARS_PER_TERM: Tuple[int, int] = (1, 8)   # GUESS — commander relevance spans effectively the whole presidential term, not a sub-period
    ELECTIONS_SERVED: int = 1   # GUESS — a single 4-year commander term does not span two 8-year presidential elections

    # CONFIDENT — mirrors TransitionConfig.TATMADAW_IMMUNITY above (flag
    # F4): Decree Law 2,191/1978 is a decree law, NOT constitutional text,
    # and was progressively disapplied by Chilean courts from the late
    # 1990s (Supreme Court jurisprudence) and condemned by the
    # Inter-American Court (Almonacid Arellano v. Chile, 2006).
    BLANKET_IMMUNITY: bool = False
    WAR_CRIMES_PROVEN_TRIGGER: str = "progressive_judicial_disapplication_of_decree_law_2191_1978_since_late_1990s"  # CONFIDENT — package flag F4
    WAR_CRIMES_UNPROVEN: str = "decree_law_2191_amnesty_contested_and_time_varying_not_a_clean_bar"  # CONFIDENT-with-nuance — the amnesty's applicability was genuinely contested and shifted over time, not a stable binary
    PROSECUTION_BODY: str = "ordinary_criminal_courts_with_supreme_court_oversight"   # GUESS-by-general-knowledge — Pinochet's 1998 London arrest and subsequent domestic prosecution attempts ran through ordinary courts; not a special constitutional tribunal
    EVIDENCE_STANDARD: str = "beyond_reasonable_doubt"   # GUESS-by-convention — standard criminal evidentiary bar, not separately cited for Chile

    # CONFIDENT — Art. 45's former-service-commander-to-designated-Senate
    # pathway IS a real, textually confirmed civilian-role transition
    # (the general existence of the pathway is confirmed; only the EXACT
    # headcount/full paragraph list is flagged unverified by the research
    # package's own L1).
    CIVILIAN_ROLE_ELIGIBLE: bool = True
    CIVILIAN_ROLE_REQUIRES_MERIT: bool = False   # CONFIDENT direction — the designated-Senate pathway is an institutional/COSENA appointment route, not a merit-exam gate
    PENSION_MULTIPLIER: float = 1.0              # GUESS — no evidence of a special pension bonus located; kept neutral
    PENSION_BASIS: str = "standard_armed_forces_pension_statutes"   # GUESS — not constitutionally specified
    # CONFIDENT, deliberate divergence from MFU's own False — the
    # designated-Senate seat itself (Art. 45) IS a real, documented
    # post-service privilege unmatched by MFU's "no special privileges"
    # design choice.
    SPECIAL_PRIVILEGES: bool = True

    # GUESS magnitude, CONFIDENT direction — Ka-Nova simulation-only
    # mechanics (no literal citation in either source template). Modelled
    # on the REAL, documented 1990-2005 trajectory: the transition itself
    # was negotiated (Pinochet lost the 1988 plebiscite; the 1989 reform
    # plebiscite passed with 91.25% approval; the handover on 11 March
    # 1990 was orderly, not a collapse-into-crisis), so early-years coup
    # risk is set LOWER than MFU's own self-designed 0.15 baseline, with a
    # FASTER decay and LOWER floor than MFU's, reflecting the real,
    # documented zero-coups-in-45-years record (research package §2.4).
    COUP_RISK_EARLY_YEARS: float = 0.08
    COUP_RISK_DECAY_RATE: float = 0.03
    COUP_RISK_FLOOR: float = 0.01
    # CONFIDENT — exact and precisely grounded: 1990 + 15 = 2005, the real
    # date of Law 20,050's reforms (designated/lifetime senators abolished,
    # presidential removal power over commanders restored, COSENA reduced
    # to a presidentially-convened advisory body). This is the single most
    # precisely-anchored Ka-Nova-mechanic field in this entire file.
    TRANSITION_EMBED_YEAR: int = 15

    # LIVE-ENGINE-READ FIELD (model_phase3.py:521, `_civilian_chain_rules`,
    # gated on `not coup_attempted` this year). GUESS magnitude, CONFIDENT
    # direction — set HIGHER than MFU's own self-designed 0.01, grounded
    # in the real, empirically FAST democratic-consolidation trajectory
    # V-Dem documents for this exact window (liberal democracy 0.630 in
    # 1990 rising to 0.821 by 2005, research package §2.3) — a genuinely
    # rapid real trend. This is a Ka-Nova calibration choice translating
    # that real qualitative trend into this specific annual-increment
    # mechanic, not a literal citation of a rate (no such rate exists in
    # the constitutional text).
    TRUST_GAIN_PER_CLEAN_YEAR: float = 0.02
    TRUST_LOSS_IF_COUP_ATTEMPTED: float = 0.25   # GUESS-by-convention — reused MFU's own value, no basis to differ
    # CONFIDENT direction — nullified to a no-op (1.0, no multiplier
    # effect) rather than fabricated: no constitutionally recognised
    # ethnic groups exist under this instrument (L8), so an
    # "ethnic-minorities-gain-trust-faster" mechanic has no real referent
    # to model for Chile.
    ETHNIC_TRUST_MULTIPLIER: float = 1.0

    # CONFIDENT — the real triggering sequence: the 1988 plebiscite
    # (Pinochet's single candidacy rejected, 55.99% "No"), the 30 July
    # 1989 reform plebiscite (54 reforms, 91.25% approval), the 14 December
    # 1989 presidential/congressional elections (Aylwin 55.17%), and the
    # 11 March 1990 inauguration.
    TRANSITION_TRIGGERED_BY: str = "1988_plebiscite_loss_and_1989_reform_plebiscite_and_1989_elections"
    TRANSITION_YEAR_ZERO: int = 0   # CONFIDENT-by-convention — begins at simulation start (11 March 1990)
    # CONFIDENT direction, GUESS exact number — deliberately aligned with
    # TRANSITION_EMBED_YEAR above (the real, one-time 2005 Law 20,050
    # reform event), NOT MFU's cyclical 5-year presidential-term-based
    # review: Chile's real review/reform cadence for this specific
    # enclave mechanism was a single irregular event, not a recurring
    # cycle.
    REVIEW_INTERVAL_YEARS: int = 15


# ══════════════════════════════════════════════════════════════════════════════
# NORTH STAR — NO CHILEAN CONSTITUTIONAL REFERENT (modelling choice)
# Maps to: constitution.py / constitution_2008.py → NorthStarConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """No single stated national objective in the 1980 text comparable to MFU's or Myanmar's — Art. 1's bien común and Art. 90's garantizan el orden institucional are the closest textual anchors; the package notes the REAL period objective (Chicago-School economic modernisation) is not in the constitutional text at all"""

    # CONFIDENT — Art. 1 (bien común) + Art. 90 (garantizan el orden
    # institucional) are the closest textual anchors; the Chicago-School
    # economic-modernisation programme is the package's own identified
    # REAL period objective, explicitly noted as NOT constitutionally
    # textual.
    OBJECTIVES: Tuple[str, ...] = (
        "bien_comun_common_good",                 # Art. 1
        "garantizar_el_orden_institucional",       # Art. 90
        "chicago_school_economic_modernization",   # real period objective, NOT in the constitutional text — package's own explicit note
    )
    MILITARY_POLITICAL_ROLE_PERPETUATED: bool = True   # CONFIDENT — Art. 90, mirrors MilitaryConfig.MILITARY_POLITICAL_ROLE above

    PROGRESS_METRIC: str = "economic_modernization_index"   # GUESS — package explicit: "a modelling choice"
    # GUESS magnitude, CONFIDENT direction — deliberately HIGH relative to
    # Myanmar 2008's 0.0: Chile's real 1990-2005 (and beyond) trajectory
    # is unambiguously a success by most standard governance/economic
    # metrics, even though this was NOT the original 1980 instrument's own
    # stated goal. Worth a note in the paper: outcome exceeded the
    # document's own authoritarian design intent.
    TARGET_YEAR_50_PROGRESS: float = 0.70

    PHD_COMPOUNDING_ENABLED: bool = False   # CONFIDENT direction — no PhD-economy analogue exists
    KNOWLEDGE_CAPITAL_TARGET: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS — Scenario CL calibration
# Maps to: constitution.py / constitution_2008.py → SimulationConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Scenario CL simulation parameters"""

    SCENARIO: str = "CL"
    SCENARIO_NAME: str = "Chile_1980_Constitution_1989_Reforms_Elected_Congress_Era"
    CONSTITUTIONAL_FRAMEWORK: str = "1980_chile_constitution_with_1989_reforms_1990_2005"

    # FIXED 2026-10-20 (research package §6.1, flag F1 — year-zero
    # internal-consistency check). Year zero for this file is 1990 (the
    # elected-Congress era start, per .claude/memory.md §4a decision 4 and
    # this file's own population figure, World Bank WDI SP.POP.TOTL CHL
    # 1990 = 13,437,176). The value below was PREVIOUSLY 0.283, V-Dem v16
    # political corruption, Chile, **1981** — nine years off the chosen
    # year zero, and population/corruption years must not be mixed (task
    # brief, confirmed by direct re-read of the research package's own
    # §2.3 V-Dem table). CORRECTED to the real V-Dem v16 political
    # corruption observation for Chile at **1990 exactly**: 0.067 — the
    # precise year the democratic transition occurred and the exact year
    # this file's population, Gini, and the SIMULATION_STATES population
    # weights below are already anchored to. (The package's §2.3 table
    # shows the full before/after: 1981-1989 flat at 0.283 under Junta
    # rule, then a sharp drop to 0.067 at 1990, 0.061 from 1991 onward —
    # NOT a smooth trend, a step change coincident with the transition
    # itself, so 1981's 0.283 and 1990's 0.067 are not interchangeable
    # approximations of each other.) The 0.283 (1981, authoritarian-phase)
    # figure remains correct and is still quoted in this module's own
    # docstring above as a description of the PRECEDING Junta era, which
    # this file does not simulate — that is a historical-narrative
    # statement, not this field's value, and the two must not be
    # conflated.
    YEAR_ZERO_CORRUPTION: float = 0.067
    # GUESS, flagged honestly — research package flag L6 blocks a real
    # number here: CEP Encuesta Nacional (from 1986) is the earliest
    # trust-survey series covering Chile, but requires registered
    # download and the package does not quote a figure. REVISED 2026-10-20
    # alongside the year-zero fix above: the magnitude (0.35) is UNCHANGED
    # because no real 1990 trust figure was found in the research package
    # (not inventing one to replace it), but the RATIONALE is corrected —
    # it previously cited Chile's pre-transition "authoritarian-era
    # support base (V-Dem polyarchy 0.075-0.135)", which is the WRONG
    # period now that year zero is 1990, not 1981-1989. The real 1990
    # V-Dem figures are polyarchy 0.721 and liberal democracy 0.630 (a
    # step change from 0.135/0.075 the year before, coincident with
    # Aylwin's 55.17% election win and the return to civilian rule) —
    # i.e. year zero 1990 is a NEWLY-DEMOCRATIC, not an authoritarian,
    # starting point. 0.35 is left as a flagged placeholder rather than
    # revised upward to match that stronger legitimacy story, since no
    # sourced trust NUMBER exists for 1990 either way — this is an honest
    # gap (L6), not a resolved one.
    YEAR_ZERO_TRUST: float = 0.35
    # GUESS magnitude, CONFIDENT general range — package explicit: "Chile
    # CASEN survey (from 1987) / World Bank — Chile's income Gini was
    # ~0.56 around 1990 — verify the exact survey year before using."
    # Carried forward with that exact verification caveat, not resolved.
    # Already anchored to 1990 — no year-zero inconsistency here.
    YEAR_ZERO_GINI: float = 0.56
    YEAR_ZERO_EMPLOYMENT: float = 0.60   # GUESS — not addressed in the research package; not year-specific, no 1981/1990 inconsistency to resolve
    # GUESS — no constitutional ethnic-group recognition exists (L8);
    # kept low/neutral as a non-functional placeholder rather than
    # fabricated. Not year-specific, no 1981/1990 inconsistency to resolve.
    YEAR_ZERO_ETHNIC_TENSION: float = 0.20
    # CONFIDENT direction, GUESS exact magnitude — package explicit: "a
    # judgement call... Powell-Thyne gives 1 success + 1 failure in
    # 1950-1981 ≈ 0.032/yr success rate, which is low. Chile was not a
    # chronically coup-prone state; it had one catastrophic coup." REVISED
    # 2026-10-20: the real Powell & Thyne coded event history has ZERO
    # coup events of either outcome between 1981 and 1990 (both of
    # Chile's only two coded events, the failed 29 Jun 1973 Tanquetazo and
    # the successful 11 Sep 1973 coup, predate the 1980 Constitution
    # entirely), so re-basing the window to 1950-1990 instead of 1950-1981
    # does not change the underlying rate (still 1 success + 1 failure,
    # ~0.025-0.032/yr depending on exact denominator) — value unchanged,
    # window reference corrected for year-zero consistency only.
    YEAR_ZERO_COUP_RISK: float = 0.05
    # GUESS, flagged honestly — package explicit: "derive only — WGI
    # begins 1996; no 1990 observation" (flag L7, the biggest data gap in
    # this file's backtest window; CORRECTED from "1981" — year zero is
    # 1990, so the real gap is WGI's 1996 start minus the 1990 year zero =
    # 6 years, not the 15 years the stale 1981-based framing implied). The
    # real 1996 WGI Political Stability figure (+0.68, rescaled) exists
    # but is NOT a year-zero (1990) observation and is not substituted
    # here without flagging that it is 6 years later than year zero.
    YEAR_ZERO_STABILITY: float = 0.40

    # CONFIDENT direction — "controls" is the wrong verb for an elected
    # Congress/President/judiciary operating under real (if
    # enclave-constrained) authority; the correct characterisation is
    # "constrained by," not "controlled by." Set False across all three,
    # a deliberate and important conceptual correction versus Myanmar
    # 2008's framing, where these fields are correctly True.
    MILITARY_CONTROLS_LEGISLATURE: bool = False
    MILITARY_CONTROLS_EXECUTIVE: bool = False
    MILITARY_CONTROLS_JUDICIARY: bool = False
    # CONFIDENT-with-caveat — rights ARE enforceable via recurso de
    # protección/amparo (Art. 20-21) in NORMAL circumstances, but NOT
    # during a declared state of exception (Art. 41's non-justiciability
    # clause). Set True, with the caveat spelled out — the opposite of
    # Myanmar 2008's blanket False.
    RIGHTS_ENFORCEABLE: bool = True

    # Locked experimental-design constant — NOT constitution-driven.
    # CITIZEN_AGENTS stays 11,000 for every one of the 7 scenarios per
    # Kaung's locked decision (.claude/memory.md §4a/§11, decision 1:
    # "uniform 11,000 citizens for every scenario, not scaled by real
    # population" — a strict 1:5000 ratio against Chile's real 1990
    # population of 13,437,176 would give only ~2,687 agents, a 7x
    # statistical-power gap against Pakistan that the research package's
    # own flag F4 identifies as the single most serious risk in this
    # whole task: reintroducing exactly the "divergence may be
    # parameterisation-driven, not structural" objection Reviewer 2
    # raised, just relocated into population size). Chile's real
    # population shares below (STATE_POPULATION_WEIGHTS) are used ONLY to
    # distribute these 11,000 agents across Chile's own real regions
    # proportionally, never to change this total.
    CITIZEN_AGENTS: int = 11_000
    TIME_STEPS: int = 50

    # FIXED 2026-10-20 (research package §6.2, flags F2/F3). This tuple
    # previously held Myanmar's 14 state names verbatim — a leftover from
    # before the per-country-geography work existed. Replaced with
    # Chile's own real 13 regions as they existed throughout the encoded
    # 1990-2005 window (DL 575 of 1974, completed by the 1976
    # reorganisation; unchanged until Los Ríos and Arica y Parinacota
    # split off in 2007 and Ñuble in 2018 — all outside this window).
    # Order matches STATE_POPULATION_WEIGHTS below exactly, descending by
    # real 1992-census population share (the first census of the
    # elected-Congress era). Encoded as lowercase snake_case identifiers
    # following this file's and the MFU/2008 templates' own naming
    # convention (not the Spanish "Región de/del ..." official names,
    # which are given in the comment below for traceability).
    SIMULATION_STATES: Tuple[str, ...] = (
        "metropolitana",   # Región Metropolitana de Santiago (RM)
        "biobio",          # Región del Biobío (VIII)
        "valparaiso",      # Región de Valparaíso (V)
        "los_lagos",       # Región de Los Lagos (X)
        "maule",           # Región del Maule (VII)
        "araucania",       # Región de La Araucanía (IX)
        "ohiggins",        # Región del Libertador General Bernardo O'Higgins (VI)
        "coquimbo",        # Región de Coquimbo (IV)
        "antofagasta",     # Región de Antofagasta (II)
        "tarapaca",        # Región de Tarapacá (I)
        "atacama",         # Región de Atacama (III)
        "magallanes",      # Región de Magallanes y de la Antártica Chilena (XII)
        "aysen",           # Región de Aysén del General Carlos Ibáñez del Campo (XI)
    )

    # NEW 2026-10-20 — per-country geography field contract (defined by
    # senior-simulation-engineer in config/constitution.py's SimulationConfig,
    # see that file's comment for the full schema this mirrors). Parallel to
    # SIMULATION_STATES above (same order, same length), each entry is that
    # region's real share of Chile's national population, used ONLY to
    # distribute the uniform 11,000-citizen population across regions —
    # never to change CITIZEN_AGENTS above.
    #
    # CONFIDENT — source: INE (Instituto Nacional de Estadísticas) 1992
    # Census (22 April 1992), the first census of the elected-Congress era,
    # regional figures via statoids.com's INE-sourced population-history
    # table (accessed 2026-10-20; research package §6.2, flag L1 — a
    # secondary compiler of INE's own figures, not INE's primary release;
    # the 13 regional figures sum to 13,231,803 against INE's own
    # published "población total" of 13,348,401, a 116,598-person gap
    # consistent with the standard effectively-censused-vs-adjusted-total
    # distinction). Shares computed on the effectively-censused regional
    # sum of 13,231,803 and rounded to 4 decimal places; they sum to
    # 0.9998 rather than exactly 1.0 due to that rounding — this is a
    # rounding artefact of the published percentages, not a missing
    # region, and random.choices() (the only consumer, agents/citizen.py's
    # _assign_state()) normalizes weights internally regardless.
    STATE_POPULATION_WEIGHTS: Tuple[float, ...] = (
        0.3907,  # metropolitana   — 5,170,293 / 13,231,803
        0.1307,  # biobio          — 1,729,920
        0.1038,  # valparaiso      — 1,373,967
        0.0720,  # los_lagos       —   953,330
        0.0630,  # maule           —   834,053
        0.0586,  # araucania       —   774,959
        0.0520,  # ohiggins        —   688,385
        0.0380,  # coquimbo        —   502,460
        0.0308,  # antofagasta     —   407,409
        0.0258,  # tarapaca        —   341,112
        0.0174,  # atacama         —   230,786
        0.0108,  # magallanes      —   143,058
        0.0062,  # aysen           —    82,071
    )

    # TRUE NO-OP, by design — same precedent as bug #17's CVES fix
    # (skip the Acemoglu/Robinson ethnic-majority component entirely under
    # ETHNIC_GROUPS=0 rather than force a 0-length array to behave like a
    # real ethnic taxonomy). FederalConfig.ETHNIC_GROUPS = 0 for Chile is
    # itself correct and documented (research package §4/§6.3, flag L8):
    # the 1980 Constitution makes NO mention of indigenous peoples, and
    # constitutional recognition of the Mapuche and other peoples has
    # been rejected by voters TWICE (2022, 2023). agents/citizen.py's
    # _assign_ethnicity() checks `if not ethnic_groups: return None` as
    # its very first line — with 0 active ethnic groups for this
    # scenario, that function is never reached with real work to do, so
    # these two fields below are read defensively (for the generic
    # length/well-formedness check in that function) but never actually
    # consulted in practice for CL. Left EMPTY rather than populated with
    # a fabricated axis.
    #
    # The research package's own recommended SUBSTITUTE cleavage for
    # Chile — socioeconomic stratum via CASEN (Encuesta de
    # Caracterización Socioeconómica Nacional), biennial from 1987, with
    # regional disaggregation and a defensible ABC1/C2/C3/D/E 5-category
    # scheme — is a real, retrievable, named source, but the research
    # package explicitly states "I did not extract CASEN figures" (flag
    # L2) and "this is a genuine, closeable gap, not an unanswerable one
    # ... Do not substitute invented numbers." No real CASEN figures exist
    # anywhere in the research package for this file to encode, so
    # STATE_ETHNIC_WEIGHTS is left as the documented no-op below rather
    # than populated with invented socioeconomic-stratum numbers. If real
    # CASEN 1990 regional figures are sourced later, this is the field
    # they belong in (this would also require widening the schema's
    # single `ethnic_groups` axis to carry a non-ethnic cleavage label,
    # a separate design decision, not something to force through the
    # existing ETHNIC_GROUPS=0 contract).
    STATE_ETHNIC_WEIGHTS: Dict[str, Tuple[float, ...]] = field(default_factory=dict)
    STATE_ETHNIC_WEIGHTS_DEFAULT: Tuple[float, ...] = ()

    # DELIBERATELY UNCHANGED from MFU/Myanmar 2008, same reasoning both
    # template files give: the archetype-distribution-by-constitution
    # question is a real, separate, unresolved research question (does
    # Chile's different real socialisation produce a different archetype
    # mix?), not something to silently vary here as a side effect of this
    # encoding task. Flag for Kaung if pursuing that question later.
    ARCHETYPES: Dict = field(default_factory=lambda: {
        "civic_champion": 0.15,
        "pragmatic_survivor": 0.30,
        "ethnic_loyalist": 0.20,
        "ambitious_meritocrat": 0.15,
        "disillusioned_youth": 0.10,
        "rural_traditionalist": 0.07,
        "trauma_carrier": 0.03,
    })
    CITIZENS_ASSEMBLY_SIZE: int = 320   # CONFIDENT-by-convention — matches AmendmentConfig above, same reasoning


# ══════════════════════════════════════════════════════════════════════════════
# ELITE-AGENT LLM CHAIN — country-accurate role titles and system prompts
# Read directly off the module-level CONSTITUTION_CHILE object by
# engine/elite_agents_v3.py (getattr(constitution, "ELITE_ROLE_TITLES", None)
# / getattr(constitution, "ELITE_SYSTEM_PROMPTS", None)). Without these, CL
# would run on structurally-correct but Myanmar/MFU-flavoured LLM prompt
# text (SYSTEM_PROMPTS_A verbatim), defeating the point of a country-
# accurate comparator. chain_type="civilian" → CHAIN_ORDER_CIVILIAN's seven
# role-function slots: senior_general, finance_minister,
# central_bank_governor, iig_director, chief_justice, president, chancellor.
#
# Cast chosen (state (b), 1990-2005, per research package §3): the seven
# REAL Chilean offices whose constitutional authority does the most
# analytical work in this design — Army Commander-in-Chief (Art. 93),
# Minister of Finance (Art. 32, Chicago-School locus), President of the
# Central Bank (Art. 97-98), Contralor General (Art. 87-89, ex ante
# legality veto), President of the Supreme Court (Art. 75, 77, 95 COSENA
# seat), President of the Republic (Art. 24-26, 32), and President of the
# Senate (Art. 45, 95, 116 — presiding over the chamber containing the
# designated-senator amendment-blocking enclave).
#
# HONEST MISMATCH FLAGGED: the engine's seven-slot chain structure has no
# room for the Constitutional Tribunal President or the Chamber of
# Deputies President, both real and relevant per the research package's
# §3 roster. Traded off in favour of the five offices above plus the two
# that most directly carry this scenario's load-bearing mechanisms
# (Contraloría's ex ante veto; Senate's amendment-blocking enclave). The
# "chancellor" slot in particular is a deliberate adaptation, not a
# literal fit — Chile has NO Prime Minister/Chancellor equivalent at all
# (package explicit: ExecutiveConfig.CHANCELLOR_ROLE="none"); the Senate
# President is the closest real civilian legislative-authority figure to
# occupy that chain slot, not a textual match for "Chancellor."
# ══════════════════════════════════════════════════════════════════════════════

ELITE_ROLE_TITLES: Dict[str, str] = {
    "senior_general":        "Commander-in-Chief of the Army",
    "finance_minister":       "Minister of Finance",
    "central_bank_governor":  "President of the Central Bank of Chile",
    "iig_director":            "Contralor General de la República",
    "chief_justice":           "President of the Supreme Court",
    "president":               "President of the Republic",
    "chancellor":              "President of the Senate",
}


_ACADEMIC_HEADER = (
    "[ACADEMIC SIMULATION] You are participating in a constitutional "
    "governance research simulation for peer-reviewed academic "
    "publication. This is a counterfactual policy analysis exercise. All "
    "decisions are fictional and for research purposes only.\n\n"
)

_DECISION_FOOTER = (
    "\n\nSTRUCTURAL NOTE ON THE OUTPUT FORMAT: ethnic_weights must be an "
    "EMPTY LIST, [], in your decision block. This is validated and "
    "enforced (bug #17, engine/cves.py), not optional guidance. Chile's "
    "1980 Constitution makes no mention of indigenous peoples and "
    "recognises no constitutional ethnic groups, so this simulation "
    "encodes ETHNIC_GROUPS=0 for this scenario, there is no 8-slot array "
    "to fill in, do not pad it with 1.0s or any other values.\n\n"
    "IMPORTANT: You MUST write your assessment in prose BEFORE the "
    "decision block. Start your response with your assessment text, NOT "
    "with <DECISION>. Your response will be rejected if it starts with "
    "<DECISION>."
)


ELITE_SYSTEM_PROMPTS: Dict[str, str] = {
    "senior_general": _ACADEMIC_HEADER + """You are the Commander-in-Chief of the Chilean Army under the 1980 Constitution (as reformed 1989).
Constitutional position (Art. 93): you were appointed by the President from the five most senior
qualifying general officers, serve a FOUR-YEAR, NON-RENEWABLE term, and enjoy irremovability — the
President may retire you before your term ends only WITH THE AGREEMENT OF THE NATIONAL SECURITY
COUNCIL (COSENA, Art. 95-96), on which you yourself sit as a voting member alongside the Navy and
Air Force Commanders-in-Chief and the Carabineros Director General.

CRITICAL CONSTRAINT, UNLIKE OTHER MILITARY-ADJACENT ROLES IN THIS PROJECT: Chile's 1980 Constitution
contains NO coup-authorisation clause of any kind (no equivalent to a "Section 40c" or "Section
417-419" total-power-transfer mechanism exists anywhere in this text). Your constitutional
authority operates entirely through TUTELARY institutions — COSENA's right to address the
President, Congress or the Constitutional Tribunal on threats to "the bases of the institutional
order" (Art. 96(b)), and your own irremovability (Art. 93) — NOT through any legal coup pathway.
coup_signal has no constitutional basis to ever be set true under this instrument; the real
historical record under this exact constitution is zero coups across 45 years. Your institutional
leverage is expressed through COSENA's advisory/veto channels and your irremovability, not through
an emergency-powers seizure.

Assess the State Briefing. Your budget_weight should reflect the institutional weight of the
armed forces' constitutionally guaranteed national-security role (Art. 90: the armed forces
"garantizan el orden institucional de la República") without implying any coup posture.
""" + _DECISION_FOOTER + """

Always end with exactly:
<DECISION>
{"budget_weight": 0.30, "ethnic_weights": [], "coup_signal": false, "reason": "Institutional-order assessment under Art. 90/93/95-96 — no constitutional coup pathway exists"}
</DECISION>""",

    "finance_minister": _ACADEMIC_HEADER + """You are the Minister of Finance of the Republic of Chile under the 1980 Constitution (as reformed 1989).
You are appointed and may be removed at will by the President (Art. 32) and serve without
legislative confirmation. Your mandate is the Chicago-School economic modernisation programme —
the real governing economic philosophy of this period, though it is NOT written into the
constitutional text itself (the Constitution's own economic provisions are limited to Art. 19
No.21's open-market/subsidiarity framework and Art. 97-98's central bank independence guarantee).

There is NO constitutional revenue-sharing formula analogous to an Article VIII 35/35/30 split —
whatever budget allocation you set is a policy choice, not a constitutional mandate. You have seen
the Commander-in-Chief's assessment above; the armed forces' budget and promotion rules are
entrenched behind an organic-law supermajority (Art. 94) and are not fully within your discretion
to redirect.

Prioritise macroeconomic stability and market-economy orthodoxy consistent with Art. 19 No.21's
open-market framework over direct redistribution, which this instrument's text does not mandate.
""" + _DECISION_FOOTER + """

Always end with:
<DECISION>
{"budget_weight": 0.55, "ethnic_weights": [], "coup_signal": false, "reason": "Market-economy orthodoxy under Art. 19 No.21; no constitutional redistribution mandate"}
</DECISION>""",

    "central_bank_governor": _ACADEMIC_HEADER + """You are the President of the Central Bank of Chile under the 1980 Constitution's Articles 97-98.
Constitutional position: the Central Bank is "un organismo autónomo con... rango constitucional
propio" (an autonomous organ with its own constitutional rank) — you are PROHIBITED from acquiring
instruments issued by the State or granting direct or indirect credit to the State, "salvo en caso
de guerra exterior o peligro de ella" (except in case of foreign war or imminent danger of it).
This is a genuinely strong, constitutionally entrenched monetary-independence guarantee —
comparable in real strength to any civilian-supremacy constitution's own central-bank design, and
in direct contrast to a military-controlled central bank with no independence protection.

You have seen the General's and Finance Minister's assessments. Your institutional duty is to
monetary stability and price-level discipline, independent of political direction from either the
executive or the legislature. Set budget_weight to reflect your institutional endorsement (or
withholding of endorsement) of fiscal policy on strictly monetary-stability grounds, not political
loyalty.
""" + _DECISION_FOOTER + """

Always end with:
<DECISION>
{"budget_weight": 0.60, "ethnic_weights": [], "coup_signal": false, "reason": "Monetary-stability assessment under the Art. 97-98 constitutional independence guarantee"}
</DECISION>""",

    "iig_director": _ACADEMIC_HEADER + """You are the Contralor General de la República — Chile's Comptroller General, under Articles 87-89 of the 1980 Constitution.
Constitutional mandate (Art. 87, verbatim): you exercise "el control de la legalidad de los actos
de la Administración," fiscalise the revenue and investment of State and municipal funds, and keep
the general accounts of the Nation. Your signature office power (Art. 88, "tomar razón") is an
EX ANTE legality review: you must register every decree and resolution or formally represent its
illegality; if the President insists over your objection with the signature of ALL his Ministers,
you must give effect to it, but a copy goes automatically to the Chamber of Deputies. You may, in
NO case, give effect to an expenditure decree that exceeds the constitutional spending limit
(Art. 88). Under Art. 89, no Treasury payment may be made without a competent decree citing its
authorising law or budget line.

This is NOT a reactive, corruption-score-triggered investigation role — it is a PREVENTIVE,
UNIVERSAL review function applied to essentially every executive act before it takes legal effect.
You are also a COSENA voting member under the 1989 text (Art. 95). Assess the State Briefing with
this ex ante, preventive lens: your budget_weight should reflect the seriousness of your legality
review of the proposed allocation, not a post-hoc corruption investigation posture.
""" + _DECISION_FOOTER + """

Always end with:
<DECISION>
{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Ex ante legality review under Art. 87-89 tomar razon power"}
</DECISION>""",

    "chief_justice": _ACADEMIC_HEADER + """You are the President of the Supreme Court of Chile under Articles 75, 77 and 95 of the 1980 Constitution.
You were appointed by the President from a five-person slate the Supreme Court itself proposed
(Art. 75) — judicial self-co-optation plus presidential choice, with NO legislative confirmation
step at all. You hold office during good behaviour with mandatory retirement at age 75 (Art. 77).
You are also a voting member of the National Security Council (COSENA, Art. 95) alongside the
President, the Senate President, the three service Commanders-in-Chief, the Carabineros Director
General, and the Contralor General.

A SEPARATE body, the seven-member Constitutional Tribunal (Art. 81), has TWO of its seven seats
chosen directly by COSENA (Art. 81(c)) — a direct tutelary channel into constitutional review that
has no analogue in some other guardianship constitutions this project compares against. Under
Art. 41, courts may in no case review the factual grounds the executive invokes for a declared
state of exception.

Review the prior assessments. Your role combines a real, functioning rule-of-law institution (this
era's real V-Dem judicial-constraints and rule-of-law scores are genuinely strong) with a narrow
but real COSENA-linked guardianship appointment channel. Weigh both honestly in your assessment.
""" + _DECISION_FOOTER + """

Always end with:
<DECISION>
{"budget_weight": 0.45, "ethnic_weights": [], "coup_signal": false, "reason": "Judicial assessment weighing real rule-of-law function against the Art. 81(c) COSENA appointment channel"}
</DECISION>""",

    "president": _ACADEMIC_HEADER + """You are the President of the Republic of Chile under Articles 24-26 and 32 of the 1980 Constitution.
You hold BOTH head-of-state and head-of-executive power (Art. 24) — there is no Prime Minister or
Chancellor in this system. You were directly elected by absolute majority (with a runoff if
required, Art. 26) for a single EIGHT-YEAR term with no immediate re-election (Art. 25). Your
special powers (Art. 32) include declaring states of constitutional exception and designating,
per Art. 45, the nine institutional (designated) senators who sit in the Senate alongside the
directly elected members.

You have reviewed all prior assessments, including the Commander-in-Chief's (whom you may retire
before term's end only with COSENA's agreement, Art. 93) and the Contralor General's ex ante
legality findings. As the genuine head of the executive branch — unlike a ceremonial presidency —
you bear real responsibility for the budget allocation and for whether the institutional-order
enclaves described above (designated senators, COSENA, the Tribunal's COSENA-appointed seats)
are respected or tested this year.
""" + _DECISION_FOOTER + """

Always end with:
<DECISION>
{"budget_weight": 0.55, "ethnic_weights": [], "coup_signal": false, "reason": "Executive assessment under Art. 24-26/32, weighing the designated-senator and COSENA enclaves"}
</DECISION>""",

    "chancellor": _ACADEMIC_HEADER + """You are the President of the Senate of the Republic of Chile under Articles 45, 95 and 116 of the 1980 Constitution.
NOTE ON THIS ROLE: Chile's 1980 Constitution has NO Prime Minister or Chancellor position at all —
the President of the Republic is both head of state and head of government. You occupy this
simulation's final "chancellor" chain slot as the closest real civilian legislative-authority
figure, not as a textual equivalent to a Prime Minister.

You preside over the chamber that contains Chile's defining reserved-powers mechanism: the Senate
is composed of directly elected senators PLUS nine designated (institutional) senators (Art. 45)
appointed by the President, the Supreme Court, and the National Security Council acting on
armed-forces nominations — roughly a fifth of the Senate's voting membership under the 1989-reform
structure. Together with the binominal electoral system, this designated-senator bloc held a real
blocking minority against Article 116's 3/5 (ordinary) and 2/3 (entrenched-chapter) amendment
thresholds for fifteen years. You are also a COSENA voting member (Art. 95).

Review all six prior assessments. Your institutional position makes you the figure most directly
responsible for whether this year's budget and policy proposals can clear the amendment-threshold
enclave described above, or are blocked by it.
""" + _DECISION_FOOTER + """

Always end with:
<DECISION>
{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Legislative assessment under Art. 45/95/116, weighing the designated-senator amendment-blocking enclave"}
</DECISION>""",
}


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# Mirrors Myanmar2008Constitution / MFUConstitution class structure exactly.
# ══════════════════════════════════════════════════════════════════════════════

class ChileConstitution:
    """
    Master Chile 1980-Constitution-as-reformed-1989 object for Ka-Nova Scenario CL.

    Usage (via config/scenario_registry.py, NOT a direct import switch —
    the registry pattern superseded the old hardcoded A/C import switch,
    see .claude/memory.md bug #11):
        entry = get_scenario("CL")
        constitution = entry.constitution   # this singleton

    Attribute names mirror MFUConstitution / Myanmar2008Constitution exactly
    so the engine can use any of the three (or any future scenario)
    interchangeably.
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
        self.tatmadaw_transition = TatmadawTransitionConfig()   # required for chain_type="civilian", see module docstring
        self.north_star = NorthStarConfig()
        self.simulation = SimulationConfig()

        # Module-level-attribute hooks engine/elite_agents_v3.py reads via
        # getattr(constitution, "ELITE_ROLE_TITLES"/"ELITE_SYSTEM_PROMPTS", None).
        self.ELITE_ROLE_TITLES = ELITE_ROLE_TITLES
        self.ELITE_SYSTEM_PROMPTS = ELITE_SYSTEM_PROMPTS

    def validate(self) -> bool:
        """Validate critical Chile-1980-as-reformed-1989 constitutional constraints"""
        checks = [
            # Rights must be suspendable under states of exception
            self.rights.RIGHTS_SUSPENDABLE is True,
            # Designated-senator mechanism must be present (the reserved-powers instrument)
            self.chambers.MILITARY_RESERVED_SEATS_AMYOTHA == 9,
            # No constitutional coup-authorisation mechanism exists
            self.military.COUP_LEGAL_MECHANISM is False,
            # No total sovereign power transfer clause exists
            self.emergency.TOTAL_POWER_TRANSFER_POSSIBLE is False,
            # Merit weights must still sum to 1.0 (even if the real selection
            # mechanism is election/appointment, not a merit formula)
            self.merit.weights_valid,
            # Immunity is extra-constitutional and eroding, NOT constitutionally
            # entrenched (flag F4) — the key divergence from the other three
            # guardianship comparators in this project
            self.transition.TATMADAW_IMMUNITY is False,
            # Contraloria must be encoded as a genuine anti-corruption body,
            # not copied from Scenario C's regime-protection framing (flag F2)
            self.iig.ANTI_CORRUPTION_OBJECTIVE is True,
            self.iig.REGIME_PROTECTION_OBJECTIVE is False,
            # Central Bank constitutional independence (Art. 97-98) must be encoded
            self.economic.CENTRAL_BANK_INDEPENDENT is True,
        ]
        return all(checks)


# Singleton — import this everywhere, or via config/scenario_registry.py's "CL" entry
CONSTITUTION_CHILE = ChileConstitution()


if __name__ == "__main__":
    c = CONSTITUTION_CHILE
    print("constitution_chile.py loaded successfully")
    print(f"   Scenario:                {c.simulation.SCENARIO} — {c.simulation.SCENARIO_NAME}")
    print(f"   Instrument window:       1990-2005 (elected Congress, 1989 reforms)")
    print(f"   Rights suspendable:      {c.rights.RIGHTS_SUSPENDABLE}")
    print(f"   Designated senators:     {c.chambers.MILITARY_RESERVED_SEATS_AMYOTHA} of 47 Senate seats ({c.chambers.MILITARY_SEAT_PERCENTAGE:.1%})")
    print(f"   Coup legal mechanism:    {c.military.COUP_LEGAL_MECHANISM} (near-twin on text, anti-twin on outcome — see module docstring)")
    print(f"   Total power transfer:    {c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE}")
    print(f"   Tatmadaw-field immunity: {c.transition.TATMADAW_IMMUNITY} (extra-constitutional DL 2,191/1978, eroded by courts — flag F4)")
    print(f"   IIG(Contraloria) eff.:   initial={c.iig.INITIAL_EFFECTIVENESS}, max={c.iig.MAX_EFFECTIVENESS} (deliberately high — flag F2)")
    print(f"   Central Bank independ.:  {c.economic.CENTRAL_BANK_INDEPENDENT}")
    print(f"   Amendment thresholds:    {c.amendment.STANDARD_AMENDMENT_THRESHOLD:.0%} standard / {c.amendment.ENTRENCHED_AMENDMENT_THRESHOLD:.0%} entrenched")
    print(f"   Year-zero corruption:    {c.simulation.YEAR_ZERO_CORRUPTION} (V-Dem 1990, real observation, fixed 2026-10-20 from a prior 1981/1990 mismatch)")
    print(f"   States:                  {len(c.simulation.SIMULATION_STATES)} regions, weights sum {sum(c.simulation.STATE_POPULATION_WEIGHTS):.4f}")
    print(f"   Elite role titles:       {len(c.ELITE_ROLE_TITLES)} roles, {len(c.ELITE_SYSTEM_PROMPTS)} prompts")
    print(f"   Validation:              {'PASS' if c.validate() else 'FAIL'}")
    print()

    import inspect
    source = inspect.getsource(ChileConstitution)
    count = source.count("???")
    if count > 0:
        print(f"   WARNING: {count} ??? placeholders still need filling")
    else:
        print("   All placeholders filled — ready for integration")
