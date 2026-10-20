"""
================================================================================
PROJECT KA-NOVA
config/constitution_germany.py

West Germany 1949 Basic Law (Grundgesetz) — as amended through 1968 —
Parameter Registry
Ka-Nova Simulation Engine — Scenario DE

This file encodes the Grundgesetz für die Bundesrepublik Deutschland as
computable parameters for the "DE" scenario (registry key "DE",
chain_type "civilian"). Role: independently-sourced, externally-validated
success case — an Allied-supervised constitution with no self-design bias,
compared against Scenario A (MFU, self-designed) and Scenario C (2008
Myanmar, self-designed failure case).

INSTRUMENT DEFINITION (resolved per Kaung's decision, 2026-10-20 — see
.claude/memory.md section 4a decision 3 and the research package's flag F1):
this file encodes the Basic Law AS AMENDED THROUGH 1968 — i.e. including the
1956 Wehrverfassung (7th amendment: Art. 87a armed forces, Art. 65a military
command, Art. 45a/45b parliamentary defence oversight) and the 1968
Notstandsverfassung (17th amendment: Art. 115a-115l emergency powers,
Art. 53a Joint Committee, Art. 80a state of tension, Art. 91 internal
emergency, Art. 20(4) right of resistance) — but EXCLUDING the December 2024
Art. 93(2)-(3) amendment that moved the Federal Constitutional Court's
16-justice/two-senate/12-year-term/age-68/no-re-election rules from statute
(Bundesverfassungsgerichtsgesetz) into the Basic Law text itself. Numeric
values matching that December-2024 text (JUDGE_COUNT=16, JUDGE_TERM=12, etc.)
are still used below WHERE they describe a figure that was already true by
ordinary statute throughout essentially the whole 1951-1999 simulated period
— see the per-field CONFIDENT/GUESS notes for exactly which figures carry
this "statutory-then" vs. "constitutional-text-only-since-Dec-2024" nuance.
This matters for a reviewer who knows German constitutional history and must
not be allowed to call the encoding anachronistic.

1949-as-enacted had NO armed forces chapter and NO emergency chapter at all
(West Germany had no army in 1949; the emergency chapter is a 1968 reaction
to Weimar Art. 48). Encoding "Germany 1949" literally while using Art. 87a/
115a parameters would be a factual error. Labelling this scenario
"1949_basic_law_as_amended_through_1968" (see SimulationConfig below,
matching scenario_registry.py's slug "germany_1968") resolves this honestly.

Source package: `config/constitution_germany_encoding/README.md` (research
package prepared by senior-researcher, 2026-10-20). Every CONFIDENT tag
below traces to an article number or a V-Dem/CPI/WGI figure cited in that
README. Every GUESS tag is flagged inline with the reasoning, per the
constitution_2008.py convention this file follows. A small number of
CONFIDENT citations below (Art. 33(2) Bestenauslese, Art. 123 continuity of
prior law, the Bundesrechnungshofgesetz's 12-year Court-of-Audit-President
term) are well-established German constitutional/statutory facts that are
NOT explicitly quoted in the research package README — each is flagged as
such inline so a follow-up researcher can add a formal citation check.

Structural template: config/constitution_2008.py (confirmed, per
.claude/memory.md bug #11, to carry the complete 86 (section, attribute)
field contract the live engine actually reads, with zero gaps). This file
mirrors that file's class structure, field names, and CONFIDENT/GUESS
tagging convention exactly, substituting Germany's real constitutional
content throughout. Two sections constitution_2008.py does NOT have are
added here because this scenario's chain_type is "civilian", not
"military": `tatmadaw_transition` (TatmadawTransitionConfig — the exact
attribute name model_phase3.py:521 reads literally; Myanmar-specific naming
baked into the engine, not a claim about Germany) and the two optional
LLM-prompt hooks `ELITE_ROLE_TITLES` / `ELITE_SYSTEM_PROMPTS` read by
engine/elite_agents_v3.py.

Headline validation finding (research package flag F2): V-Dem v16's West
Germany entity gives political-corruption = 0.020 at year 0 (1949), falling
to 0.011 from year 19 (1968) onward, flat to year 50 (1999) — the ONLY
constitution in the whole 7-scenario project with a real observation
covering Ka-Nova's exact 50-year horizon. That range (0.011-0.020) sits
inside Scenario A/MFU's own locked year-50 corruption confidence interval
(0.0122 +/- 0.0073, .claude/memory.md section 6). A real, externally
supervised, non-self-designed democratic constitution lands inside the
self-designed success baseline's own result range — the strongest available
answer to the self-design-bias objection raised against Scenario A.

Counter-finding worth keeping in the paper (research package flag F3):
Germany achieves this near-best-in-class corruption record WITHOUT any
dedicated anti-corruption agency at all (no IIG analogue — only the
Bundesrechnungshof's ordinary audit function and ordinary criminal
prosecution). This cuts against MFU's own design premise that a powerful
dedicated agency is necessary for a clean outcome, and the IIGConfig section
below says so explicitly.

Author: Claude Code (senior-simulation-engineer), 2026-10-20
Architecture owner: Kaung Htet
License: MIT
================================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 20 / ARTICLE 22 / ARTICLE 116 — BASIC PRINCIPLES
# Maps to: constitution.py / constitution_2008.py → FoundationalConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FoundationalConfig:
    """Art. 20 (basic principles), Art. 22 (capital/flag), Art. 116 (citizenship)"""

    # Art. 20(1) — "The Federal Republic of Germany is a democratic and
    # social federal state." CONFIDENT, directly quoted in the README.
    STATE_NAME: str = "Federal Republic of Germany"

    # GUESS — the Basic Law has no official-language article at all (unlike
    # Myanmar Section 450). "German" reflects universal legal/administrative
    # practice, not a textual citation.
    OFFICIAL_LANGUAGE: str = "German"
    # GUESS, direction confirmed — there is no federal Basic-Law equivalent
    # of Myanmar's Section 22(a). Real minority-language protection (Danish,
    # Sorbian, Frisian, Romani) is statutory / Land-constitutional / treaty-
    # based (the 1955 German-Danish Bonn-Copenhagen Declarations), not
    # Grundgesetz text. Set False rather than overstating a federal
    # constitutional guarantee that does not exist.
    ETHNIC_LANGUAGES_PROTECTED: bool = False

    # Art. 22(1) — CONFIDENT. Berlin is the capital as currently amended;
    # Bonn was the (statutory, not constitutional) seat of government
    # 1949-1990. Comment carries the date per the README's explicit
    # instruction to date every Land-count/capital fact.
    CAPITAL: str = "Berlin"  # Bonn 1949-1990; Berlin per the post-1990 Art. 22(1) text

    # Art. 22(2) — CONFIDENT. "The federal flag is black, red and gold."
    FLAG: str = "black_red_gold_tricolour"

    # Art. 116 — citizenship regulated by statute (Staatsangehorigkeitsgesetz,
    # StAG), not the Basic Law itself. CONFIDENT that this is statutory, not
    # constitutional, per the README's explicit flag on this point.
    CITIZENSHIP_MODES: Tuple[str, ...] = (
        "ius_sanguinis_by_statute_stag",             # historical primary mode
        "ius_soli_conditional_since_2000_reform",    # 2000 StAG reform, outside our 1968 cutoff but noted for completeness
    )
    # GUESS magnitude — current (2024 StAG reform) naturalisation residency
    # requirement is 5 years; it was 8 before 2024 and 15 under the pre-2000
    # regime. None of these are constitutional figures (Art. 116 delegates
    # entirely to statute). Using the current figure as the schema's single
    # required value; flagged explicitly as non-constitutional per the README.
    NATURALIZATION_YEARS: int = 5
    # CONFIDENT direction — no constitutional merit exam for naturalisation
    # exists (the statutory language/civics test is not a numeric "merit
    # score" concept the way MFU's own naturalisation design is).
    NATURALIZATION_MERIT_MIN: float = 0.0

    # GUESS — no single Basic-Law "territory basis" clause exists the way
    # Myanmar Section 5 states one; Art. 23 (rewritten 1990 for EU purposes)
    # and Art. 29 (Land boundary reorganisation) are the nearest textual
    # anchors.
    TERRITORY_BASIS: str = "laender_territory_at_time_of_accession_art23_29"

    # CONFIDENT, directly cited in the README (L8): 11 Lander in 1949
    # (including three short-lived south-western states), 10 from 1957
    # (after the 1952 Baden-Wurttemberg merger and the 1957 Saarland
    # accession — the README's "10 from 1952" rounds through a brief
    # 1952-1957 9-Lander period), 16 from 1990 reunification. This file
    # uses 10 — the stable 1957-1990 configuration — because it is the
    # single number that best matches the "as amended through 1968" label
    # AND covers the large majority of the 50-year simulated window
    # (1957-1999 = simulated years 8-50). The post-1990 jump to 16 (the
    # final 9 years of the horizon, 1991-1999) is NOT modelled — this
    # dataclass takes one static value, a genuine schema limitation, not an
    # oversight. Flag for whoever next revisits this file.
    STATE_COUNT: int = 10
    SIMULATION_STATE_COUNT: int = 10


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 1-19 — BASIC RIGHTS
# Maps to: constitution.py / constitution_2008.py → RightsConfig
# THE STRONGEST RIGHTS CONFIGURATION IN THE 7-SCENARIO SET
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class RightsConfig:
    """Arts. 1-19 — Basic Rights (directly binding on all three branches, Art. 1(3))"""

    # CONFIDENT, directly cited in the README.
    FUNDAMENTAL_RIGHTS: Tuple[str, ...] = (
        "human_dignity_inviolable",            # Art. 1(1)
        "equality_before_the_law",              # Art. 3
        "freedom_of_expression",                # Art. 5(1)
        "freedom_of_assembly",                  # Art. 8
        "freedom_of_association",               # Art. 9
        "occupational_freedom",                 # Art. 12
        "property_with_social_obligation",      # Art. 14
        "guaranteed_judicial_recourse",         # Art. 19(4)
    )

    # CONFIDENT — Art. 19(2): "In no case may the essence of a basic right
    # be affected." Art. 79(3) eternity clause additionally protects Art. 1
    # and Art. 20 from amendment. No provision permits general suspension of
    # basic rights, even under the 1968 state-of-defence chapter (Art.
    # 115c(2) deprivations of liberty are extended only within tightly
    # specified limits; Art. 19(2)/79(3) continue to bind). DE is the only
    # scenario besides MFU with this value False — but, per the README's
    # framing, DE's False is sourced from an external, Allied-supervised
    # text Kaung did not design, which is precisely why this scenario is
    # worth the compute.
    RIGHTS_SUSPENDABLE: bool = False
    # GUESS magnitude, CONFIDENT floor — README recommends "at minimum 2"
    # (Art. 1 dignity + Art. 20 principles, both protected via the Art.
    # 79(3) eternity clause). A higher count is defensible via Art. 19(2)
    # applying to the essence of every one of Arts. 1-19, but 2 is the
    # conservative, directly-citable figure used here.
    RIGHTS_ABSOLUTE_COUNT: int = 2

    # CONFIDENT — opposite of Myanmar; see RIGHTS_SUSPENDABLE comment above.
    EMERGENCY_TOUCHES_RIGHTS: bool = False

    # CONFIDENT — Art. 12a (1956, part of the Wehrverfassung) is the real
    # constitutional basis for compulsory military service for men 18+;
    # the Wehrpflichtgesetz (statute) actually enforced conscription
    # 1956-2011 (suspended since, well after this file's 50-year horizon
    # ends in 1999). For the large majority of the simulated horizon
    # (years 7-50, i.e. 1956-1999) conscription was genuinely in force —
    # True is the historically accurate value for the "as amended through
    # 1968" instrument, not True-by-default the way Myanmar's is.
    NATIONAL_SERVICE_MANDATORY: bool = True
    NATIONAL_SERVICE_AGE: int = 18             # Art. 12a's textual age threshold — CONFIDENT
    # GUESS — conscription length varied by statute across the Cold War
    # period (12-18 months at different points); 12 is the commonly cited
    # standard length, not a single fixed constitutional figure.
    NATIONAL_SERVICE_DURATION_MONTHS: int = 12

    # GUESS/CONFIDENT mixed — Art. 17a (1956) DOES permit statutes to
    # restrict a narrow, enumerated set of rights (Art. 5(1) opinion in
    # word/writing/picture, Art. 17 collective petition, Art. 11 freedom of
    # movement) for members of the armed forces and alternative-service
    # conscripts during their service. This is real but structurally
    # nothing like Myanmar Section 382's blanket override — it is narrow,
    # enumerated, and time-bound to the service period, with Art. 4(3)
    # conscientious-objection and substitute civilian service (Zivildienst)
    # as a real escape valve. Encoding this boolean True (a provision exists)
    # risks implying equivalence with Myanmar's blanket override, which
    # would misrepresent the real severity gap — flagged explicitly so no
    # downstream read treats "True" here as comparable to constitution_2008.py's
    # "True" on this same field.
    MILITARY_RIGHTS_OVERRIDE: bool = True

    # GUESS magnitude, CONFIDENT direction — these two fields are IS live-
    # read (agents/citizen.py, feedback/loops.py) grievance/trust mechanics,
    # not narrative-only. Set well below MFU's own values (MFU is itself a
    # best-case design) given Germany's real, externally-validated outcome
    # record is at least as clean. Reused close to MFU's own numbers rather
    # than inventing new ones, since the research package has no literal
    # "grievance spike per violation" figure (no constitution does — these
    # are Ka-Nova simulation mechanics, not constitutional citations).
    RIGHTS_VIOLATION_GRIEVANCE_SPIKE: float = 0.03
    RIGHTS_VIOLATION_TRUST_DROP: float = 0.05


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 33(2) — "BESTENAUSLESE" (BEST-QUALIFIED PRINCIPLE)
# Maps to: constitution.py / constitution_2008.py → MeritConfig
# NOTE: Art. 33(2) is NOT quoted in the research package README. It is a
# well-established, independently verifiable Basic Law provision
# ("gleicher Zugang zu jedem offentlichen Amt nach Eignung, Befahigung und
# fachlicher Leistung" — equal access to public office according to
# aptitude, qualification, and professional achievement). Flagged here for
# a follow-up citation check against the README, consistent with this
# file's own convention of flagging anything not explicitly sourced in the
# package. Unlike every other scenario in the 7-constitution set, Germany
# genuinely HAS a real constitutional meritocracy clause — closer in spirit
# to MFU's own design than any other comparator.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MeritConfig:
    """Art. 33(2) — equal access to public office by aptitude, qualification, achievement"""

    # GUESS allocation — Art. 33(2) names three criteria (Eignung/aptitude,
    # Befahigung/qualification, fachliche Leistung/performance) but, like
    # every constitution in this set including MFU's own, does not assign
    # them numeric weights; that is a Ka-Nova modelling choice. Mapped here
    # as: PERFORMANCE_WEIGHT~fachliche Leistung, EDUCATION_WEIGHT~Befahigung,
    # PRODUCTIVITY_WEIGHT~Eignung, with a small residual CIVIC_WEIGHT for
    # the Art. 33(5)/5(3) constitutional-loyalty duty (Verfassungstreue),
    # which Art. 33(2) itself does not weight at all.
    PRODUCTIVITY_WEIGHT: float = 0.15   # Eignung (aptitude)
    EDUCATION_WEIGHT: float = 0.35      # Befahigung (qualification)
    PERFORMANCE_WEIGHT: float = 0.40    # fachliche Leistung (professional achievement)
    CIVIC_WEIGHT: float = 0.10          # constitutional-loyalty duty, Art. 33(5)/5(3)

    @property
    def weights_valid(self) -> bool:
        total = (self.PRODUCTIVITY_WEIGHT + self.EDUCATION_WEIGHT +
                 self.PERFORMANCE_WEIGHT + self.CIVIC_WEIGHT)
        return abs(total - 1.0) < 1e-9

    # GUESS — Art. 33(2) sets no numeric score; comparably meritocratic in
    # spirit to MFU's own 0.60 (a real, if modern, parallel design), set
    # slightly below it since Art. 33(2) is a non-discrimination/equal-
    # access guarantee, not a competitive exam-score threshold the way
    # MFU's merit exam is.
    MERIT_MIN_PUBLIC_OFFICE: float = 0.55

    # GUESS — no single federal exam administrator exists; German civil-
    # service entry examinations (Laufbahnprufung) and the judicial state
    # examination (Staatsexamen) are decentralised across the Lander and
    # federal ministries/courts, not a Myanmar/MFU-style single body.
    EXAM_ADMINISTRATOR: str = "decentralized_laender_and_federal_civil_service_boards"
    EXAM_MAX_CONSECUTIVE_TERMS: int = 0   # not a meaningful "term" concept for a decentralised exam system — 0 = unlimited, GUESS
    EXAM_RESULTS_PUBLISH_DAYS: int = 0    # no constitutional publication requirement — GUESS

    # CONFIDENT — Art. 18 (FCC-only forfeiture of specified rights for abuse
    # against the free democratic basic order) and Art. 21(2) (party
    # unconstitutionality) are real disqualification triggers; ordinary
    # Beamtenrecht (civil-service law) imposes a statutory loyalty-to-the-
    # constitutional-order duty (Verfassungstreuepflicht) as well.
    DISQUALIFICATION_TRIGGERS: Tuple[str, ...] = (
        "rights_forfeiture_under_article_18_fcc_ruling",
        "membership_in_a_party_banned_under_article_21",
        "breach_of_civil_service_constitutional_loyalty_duty",
    )
    # GUESS — Art. 18 forfeiture can be time-limited by the FCC under
    # BVerfGG; it is not automatically permanent the way Myanmar's
    # disqualification is. Set True with this caveat rather than silently
    # matching Myanmar's absolute framing.
    DISQUALIFICATION_PERMANENT: bool = True  # GUESS — FCC may in practice set a fixed duration; see comment above

    # CONFIDENT direction — Germany has tenure-protected civil servants
    # (Art. 33(5)) rather than a periodic recertification cycle; absence of
    # a cycle here reflects tenure protection, not absence of accountability
    # (the opposite real-world reason from Myanmar's own "no cycle" encoding).
    RECERTIFICATION_INTERVAL: int = 0
    RECERTIFICATION_FAIL_THRESHOLD: float = 0.0
    RECERTIFICATION_VACATE_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 54-69 — HEAD OF STATE AND EXECUTIVE
# Maps to: constitution.py / constitution_2008.py → ExecutiveConfig
# A TRUE CEREMONIAL-PRESIDENT / EXECUTIVE-CHANCELLOR SPLIT — MFU's OWN
# PRESIDENT/CHANCELLOR DESIGN IS MODELLED ON THIS PATTERN
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutiveConfig:
    """Arts. 54-69 — Federal President and Federal Chancellor"""

    # Art. 54 — CONFIDENT, directly quoted in the README.
    PRESIDENT_ROLE: str = "ceremonial_head_of_state"
    PRESIDENT_ELECTION: str = "federal_convention_bundestag_plus_equal_land_delegates"  # Art. 54(3)
    PRESIDENT_TERM: int = 5                 # Art. 54(2)
    PRESIDENT_MAX_TERMS: int = 2            # Art. 54(2): "re-election for a consecutive term shall be permitted only once"
    PRESIDENT_REELECTION: bool = True

    PRESIDENT_TIEBREAKER: bool = False      # no textual tiebreaker-vote mechanism exists — CONFIDENT absence
    PRESIDENT_EXECUTIVE_POWER: bool = False  # Art. 58 countersignature requirement — CONFIDENT

    # Art. 63/65 — CONFIDENT.
    CHANCELLOR_ROLE: str = "executive_head_of_government"
    CHANCELLOR_ELECTION: str = "bundestag_absolute_majority_on_presidential_proposal"  # Art. 63(1)-(2)
    CHANCELLOR_TERM: int = 4                 # tied to the Bundestag's 4-year term (Art. 39(1)), not a fixed personal term — CONFIDENT, directly from README
    # CONFIDENT, directly from README — Germany has NO chancellor term
    # limit (Adenauer 14 years, Kohl 16, Merkel 16). 0 = unlimited, the
    # opposite design choice from MFU's single-term Chancellor.
    CHANCELLOR_MAX_TERMS: int = 0
    CHANCELLOR_COOLING_OFF: int = 0          # no textual cooling-off provision found — GUESS absence

    PRESIDENT_ELECTION_YEAR: int = 1
    CHANCELLOR_ELECTION_YEAR: int = 0        # elected at the Bundestag's first sitting following each election — CONFIDENT

    # GUESS — not fixed by the Basic Law; current practice is roughly 15
    # ministries + the Chancellor, per the README.
    MINISTER_COUNT: int = 15
    MINISTER_MERIT_MIN: float = 0.0          # ministers are political appointees, not Art. 33(2) civil-service posts — CONFIDENT direction
    MINISTER_CONFIRMATION: str = "president_appointment_on_chancellor_proposal"  # Art. 64(1) — CONFIDENT

    # GUESS list — the Basic Law does not enumerate ministries; this
    # reflects real, historically continuous federal cabinet portfolios.
    MINISTRIES: Tuple[str, ...] = (
        "federal_ministry_of_defence",
        "federal_ministry_of_finance",
        "federal_ministry_of_the_interior",
        "federal_ministry_of_justice",
        "federal_ministry_of_foreign_affairs",
        "federal_ministry_of_economic_affairs",
        "federal_ministry_of_labour_and_social_affairs",
        "federal_ministry_of_education_and_research",
    )

    # CONFIDENT — only the Bundestag can remove the Chancellor, and only via
    # the Art. 67 constructive vote (electing a successor in the same
    # motion), unlike multi-chamber removal designs elsewhere in this project.
    CHANCELLOR_DISMISSAL_CHAMBERS_REQUIRED: int = 1
    # CONFIDENT, directly from the README: "effectively true, because
    # Art. 67 requires a constructive majority" — you cannot be removed
    # without a successor being elected in the same vote.
    CHANCELLOR_DISMISSAL_VETO: bool = True
    # CONFIDENT but non-discretionary — Art. 67(1): the Bundestag "request[s]
    # the Federal President to dismiss the Federal Chancellor. The Federal
    # President MUST comply with the request." A presidential act is
    # legally involved, but it carries no discretion — this field cannot
    # capture that nuance, flagged here explicitly.
    CHANCELLOR_DISMISSAL_REQUIRES_PRESIDENT: bool = True

    # CONFIDENT, directly from the README: Art. 61 impeachment may be
    # applied by EITHER chamber independently (one quarter of Bundestag OR
    # Bundesrat), decided by two-thirds of the applying body, and then
    # ADJUDICATED by the Federal Constitutional Court — not decided by the
    # chambers themselves. This is structurally different from MFU's own
    # chamber-vote-decides design; PRESIDENT_REMOVAL_CHAMBERS=1 reflects
    # "either body alone can apply", not "only one chamber matters overall".
    PRESIDENT_REMOVAL_CHAMBERS: int = 1
    PRESIDENT_REMOVAL_CHANCELLOR_SIGN: bool = False       # no chancellor countersignature role in Art. 61 — GUESS absence
    PRESIDENT_REMOVAL_ANALYSIS_EVIDENCE: bool = False     # no Analysis-Council-style evidence step in Art. 61 — GUESS absence
    PRESIDENT_APPROVAL_REMOVAL_THRESHOLD: float = 0.25    # Art. 61: one quarter to apply — CONFIDENT
    # Repurposed from the "trust-collapse threshold" framing used elsewhere
    # in this schema to the literal Art. 61 decision threshold: two-thirds
    # of the applying body's members/votes to actually remove. CONFIDENT.
    PRESIDENT_TRUST_REMOVAL_THRESHOLD: float = 0.667

    CHANCELLOR_INTERIM: str = "deputy_chancellor_until_new_election_art69"  # Art. 69(1) — CONFIDENT

    # Bonus field beyond the 2008 skeleton, added per the README's explicit
    # suggestion ("a cheap field... encodes a real stability-producing
    # mechanism"): the constructive vote of no confidence (Art. 67) is the
    # single most distinctive mechanism in this whole 7-scenario project —
    # attempted twice in 76 years, succeeded once (1982, Schmidt -> Kohl).
    # Not currently read by any live engine code (confirmed by grep against
    # model_phase3.py/agents/feedback at encoding time) — included for
    # documentation/future-proofing, not a claimed mechanical effect today.
    NO_CONFIDENCE_REQUIRES_SUCCESSOR: bool = True   # CONFIDENT, Art. 67(1)


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 38-52, 70-81 — BUNDESTAG AND BUNDESRAT
# Maps to: constitution.py / constitution_2008.py → ChamberConfig
# ZERO RESERVED MILITARY SEATS — THE OPPOSITE STRUCTURAL DESIGN FROM 2008
# MYANMAR'S DEFINING FEATURE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ChamberConfig:
    """Arts. 38-52 (Bundestag/Bundesrat), Arts. 70-81 (legislative powers)"""

    # GUESS/CONFIDENT mixed — Art. 38(3) delegates election mechanics to
    # federal statute (Bundeswahlgesetz). The mixed-member-proportional
    # system and the 5% threshold are STATUTORY, not constitutional — the
    # README flags this explicitly as commonly mis-described as
    # constitutional. CONGRESS_ELECTION's value below is the real statutory
    # design; the field is kept for schema completeness, labelled as statutory.
    CONGRESS_ELECTION: str = "mixed_member_proportional_statutory_bundeswahlgesetz"
    CONGRESS_THRESHOLD: float = 0.51   # Art. 42(2): majority of votes cast — CONFIDENT direction (simple majority)
    CONGRESS_TERM: int = 4              # Art. 39(1) — CONFIDENT
    CONGRESS_REELECTION: bool = True

    # CONFIDENT, directly from the README: "Zero reserved military seats;
    # zero appointed seats; zero designated seats." DE and SK are the only
    # two scenarios in the 7-constitution set with a wholly elected,
    # accountable legislature.
    MILITARY_RESERVED_SEATS_PYITHU: int = 0
    MILITARY_RESERVED_SEATS_AMYOTHA: int = 0
    MILITARY_SEAT_PERCENTAGE: float = 0.0
    MILITARY_SEATS_APPOINTED_BY: str = "not_applicable_no_reserved_seats"

    # CONFIDENT — "No constitutionally recognised ethnic-group structure at
    # federal level -> all ETHNIC_* fields are inert for DE" (README, verbatim
    # finding). Set to 0/inert rather than fabricating a structure that does
    # not exist; comment explicitly so no downstream reader mistakes 0 for
    # a measurement rather than "mechanism absent".
    ETHNIC_SEATS: int = 0
    ETHNIC_THRESHOLD: float = 0.0
    ETHNIC_TERM: int = 0

    # CONFIDENT, directly recommended by the README: map the Analysis-
    # Council-equivalent threshold onto the Federal Constitutional Court's
    # own senate majority (5 of 8 Justices = 0.625). An alternative mapping
    # to the 2/3 threshold used for Art. 18/21(2) forfeiture and party-ban
    # decisions (0.667, BVerfGG section 15(4)) is equally defensible — flag
    # if the paper needs the higher figure instead.
    ANALYSIS_THRESHOLD: float = 0.625
    # GUESS — the FCC has no fixed per-ruling time limit the way Myanmar's
    # Constitutional Tribunal does (Section 335); real FCC cases can take
    # months to years. Kept as a structural placeholder, NOT sourced.
    ANALYSIS_VETO_TIME_LIMIT: int = 90

    # CONFIDENT direction — FCC Justices are elected by a statutory 2/3
    # majority of the electing body (BVerfGG section 6/7), not merit-exam
    # tested; no numeric merit gate applies.
    ANALYSIS_MERIT_MIN: float = 0.0
    # CONFIDENT, with the nuance noted in this file's module docstring: the
    # 12-year FCC Justice term was statutory (BVerfGG) throughout almost the
    # entire simulated period and only entrenched into the Basic Law text
    # itself by the December 2024 amendment, which this encoding excludes.
    # The NUMBER is historically accurate for the simulated period
    # regardless of which legal instrument carried it.
    ANALYSIS_TERM: int = 12

    # GUESS — no military bloc exists to model discipline/majority-override
    # dynamics for (MILITARY_SEAT_PERCENTAGE=0.0 above already makes this
    # mechanically moot); kept at neutral/inert values for schema completeness.
    MILITARY_BLOC_VOTE_DISCIPLINE: float = 0.0
    CIVILIAN_EFFECTIVE_MAJORITY_NEEDED: float = 0.51   # ordinary simple majority suffices — no military bloc to overcome, GUESS/CONFIDENT direction

    # CONFIDENT — inert, no ethnic-council-seat term-limit mechanism exists.
    ETHNIC_MAX_TERMS: int = 0
    ETHNIC_PRESIDENTIAL_MIN_TERMS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 92-101 — JUDICIARY / FEDERAL CONSTITUTIONAL COURT
# Maps to: constitution.py / constitution_2008.py → JudiciaryConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class JudiciaryConfig:
    """Arts. 92-101 — Judicial Power and the Federal Constitutional Court"""

    # CONFIDENT — Art. 97(1) judicial independence, Art. 93(1) FCC
    # "autonomous and independent of all other constitutional organs",
    # Art. 101(1) "extraordinary courts shall be inadmissible". Strongest
    # judicial-independence encoding in the 7-scenario set.
    COURT_INDEPENDENCE: bool = True
    # CONFIDENT with the statute-vs-text nuance noted above (16 Justices,
    # 2 senates of 8 — statutory throughout the simulated period, only
    # entrenched into Basic Law text by the excluded December 2024 amendment).
    COURT_JUDGES_COUNT: int = 16
    COURT_TERM_YEARS: int = 12
    RULING_THRESHOLD: int = 5   # of 8 per senate (senate majority) — CONFIDENT, directly from README

    # CONFIDENT, directly from the README: Art. 96(2) permits military
    # criminal courts ONLY in a state of defence or for members serving
    # abroad/on warships, and they sit within the civilian Federal Minister
    # of Justice's portfolio. "There is no standing military-justice system
    # with jurisdiction over civilians" — the structural opposite of
    # Myanmar's Section 293(b).
    MILITARY_JUSTICE_FINAL: bool = False
    CIVILIAN_COURT_OVERRIDE_MILITARY: bool = True

    CONSTITUTIONAL_TRIBUNAL_SIZE: int = 16   # FCC total (2 senates x 8) — CONFIDENT, with statute-vs-text nuance as above
    TRIBUNAL_TERM_YEARS: int = 12

    # GUESS magnitude, CONFIDENT direction — very high, grounded in Art.
    # 97(1)-(2) tenure protection and Germany's Rule-of-Law WGI scores
    # (approximately +1.5 to +1.8 on the -2.5..+2.5 scale throughout
    # 1996-2022, the flattest, highest series in the research package).
    COURT_CORRUPTION_RESISTANCE: float = 0.92
    # CONFIDENT direction (absent), for the OPPOSITE real reason from
    # Myanmar's absence: Germany's ordinary rule-of-law institutions make an
    # MFU-style extraordinary Total Ruin mechanism unnecessary, not that
    # accountability is absent altogether (see Art. 18/21(2) real sanctions
    # instead, encoded in CryptoJusticeConfig below as the inert-but-for-a-
    # different-reason idiom).
    TOTAL_RUIN_THRESHOLD: float = 0.0

    JUDGE_COUNT: int = 16
    JUDGE_TERM: int = 12
    # CONFIDENT — Art. 93(3) (statutory equivalent throughout the simulated
    # period): "Immediate or subsequent re-election of Justices shall not be
    # possible." A genuine, real, non-renewable single-term safeguard.
    JUDGE_MAX_TERMS: int = 1
    # GUESS — Art. 93(1)'s "autonomous and independent" language is the
    # broadest textual anchor available; the FCC's literal statutory budget
    # autonomy (Haushaltsautonomie) is a later reform not explicitly dated
    # in the research package — flagged as not fully verified against a
    # specific citation.
    BUDGET_FIXED: bool = True


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 114(2) BUNDESRECHNUNGSHOF (FEDERAL COURT OF AUDIT) +
# ARTICLE 45a/45b (DEFENCE COMMITTEE / PARLIAMENTARY COMMISSIONER)
# Maps to: constitution.py / constitution_2008.py → IIGConfig
# GERMANY HAS NO DEDICATED CONSTITUTIONAL ANTI-CORRUPTION COMMISSION — SEE
# THE FILE-LEVEL DOCSTRING'S FLAG F3. THIS SECTION ENCODES THE REAL
# FUNCTIONAL ANALOGUES (AUDIT COURT + MILITARY OMBUDSMAN), NOT A
# MFU/MYANMAR-STYLE DEDICATED AGENCY THAT DOES NOT EXIST HERE.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class IIGConfig:
    """Art. 114(2) Bundesrechnungshof + Art. 45a/45b parliamentary defence oversight —
    loose functional analogues, not a literal dedicated anti-corruption agency"""

    # GUESS — Bundesrechnungshof members are typically senior judicially-
    # qualified civil servants ("Befahigung zum Richteramt" in practice),
    # a real but unquantified professional-qualification standard, not a
    # numeric merit-exam score the way MFU's IIG design has one.
    ENTRY_MERIT: float = 0.70
    ACADEMY_MONTHS: int = 0   # CONFIDENT — no IIG-style academy exists
    # GUESS magnitude, CONFIDENT direction (opposite end of the spectrum
    # from Myanmar's 0.90 regime-protection-only gate): the Bundesrechnungshof
    # conducts ROUTINE annual audits (Art. 114(1)-(2)) of ALL federal
    # accounts, not just high-profile regime-threatening cases. A low
    # trigger reflects routine, broad-based audit coverage.
    INVESTIGATION_TRIGGER: float = 0.25
    # GUESS magnitude, CONFIDENT direction and the single most important
    # comment in this section: this is set HIGH not because Germany has a
    # strong dedicated anti-corruption AGENCY (it does not — see the
    # module docstring's flag F3), but because the surrounding rule-of-law
    # ecosystem (independent judiciary, free press, ordinary criminal
    # prosecution under StGB sections 331-338, Art. 114(2) judicial-
    # independence audit) achieves a near-best-in-class real-world outcome
    # anyway: V-Dem political corruption 0.011-0.020 across the entire
    # simulated horizon, CPI approximately 75-81 (2012-2025 scale). This is
    # a genuinely important finding for a paper whose success baseline
    # (MFU) is built around a powerful DEDICATED agency — Germany shows
    # that is not the only route to a clean outcome.
    EFFECTIVENESS_FLOOR: float = 0.70
    REPORTS_TO: str = "bundestag_and_bundesrat"   # Art. 114(2) — CONFIDENT, directly from the README
    # GUESS — no explicit post-service chamber-eligibility restriction text
    # found for Bundesrechnungshof members.
    CHAMBER_ELIGIBLE: bool = True

    # CONFIDENT — Art. 114(2): the Bundesrechnungshof "shall audit the
    # account and determine whether public finances have been properly and
    # efficiently administered" — a genuine anti-corruption/integrity
    # objective, reporting TO parliament, not protecting an executive regime.
    ANTI_CORRUPTION_OBJECTIVE: bool = True
    REGIME_PROTECTION_OBJECTIVE: bool = False

    # GUESS — grounded in the real near-best-in-class outcome record from
    # year zero onward (see this file's module docstring's F2 finding:
    # V-Dem West Germany corruption was already only 0.020 in 1949).
    INITIAL_EFFECTIVENESS: float = 0.65
    # GUESS — capped below 1.0 deliberately: no institution, however strong,
    # achieves perfection, and the genuine structural gap GRECO/TI Germany
    # have repeatedly flagged (no central anti-corruption agency; UNCAC
    # ratified only in 2014) is real and should not be modelled away.
    MAX_EFFECTIVENESS: float = 0.90

    ENTRY_MERIT_MIN: float = 0.70   # mirrors ENTRY_MERIT above — CONFIDENT pairing
    # GUESS — Bundesrechnungshof leadership is appointed from senior,
    # experienced jurists/civil servants; set notably older than Myanmar's
    # 20 (commissioned-officer entry age) to reflect this real seniority
    # pattern, not sourced to a specific figure.
    ENTRY_MIN_AGE: int = 30
    ACADEMY_DURATION_MONTHS: int = 0   # mirrors ACADEMY_MONTHS — CONFIDENT
    # CONFIDENT, flagged for a follow-up citation check (well-established
    # but not explicitly quoted in the research package README): the
    # Bundesrechnungshofgesetz sets the President's term at 12 years,
    # deliberately mirroring the Federal Constitutional Court's own term —
    # length — to insulate the office from political pressure.
    DIRECTOR_TERM: int = 12
    DIRECTOR_RENEWABLE: bool = False   # same non-renewable design as JUDGE_MAX_TERMS above — CONFIDENT, same citation caveat as DIRECTOR_TERM

    # GUESS/CONFIDENT mixed — no "Partnership Council" concept exists for
    # Germany's audit body at all. Numerically mirrors constitution_2008.py's
    # own "no such body" null-encoding idiom (0 years = everyone immediately
    # eligible), but the REAL MEANING is opposite: there, 0 models the
    # absence of a seniority safeguard under an unaccountable regime; here,
    # 0 models the absence of a committee the Bundesrechnungshof's real,
    # functioning independence makes unnecessary. Flagged explicitly so this
    # distinction is not lost on a future reader.
    PARTNER_ELIGIBILITY_YEARS: int = 0
    # GUESS — no two-stage evidentiary process is documented; Germany's real
    # process is: Bundesrechnungshof audit finding -> referral to ordinary
    # Land prosecutors under StGB sections 331-338 if criminal conduct is
    # suspected. Modelled as a single moderate threshold rather than
    # Myanmar's collapsed-to-the-same-extreme-bar idiom.
    OPEN_INVESTIGATION_THRESHOLD: float = 0.25
    PROCEED_PROSECUTION_THRESHOLD: float = 0.50
    PARTNERSHIP_COUNCIL_QUORUM: float = 1.0   # inert, no such body — GUESS, same idiom as 2008 but opposite real reason, see PARTNER_ELIGIBILITY_YEARS comment

    CHAMBER_ELIGIBLE_POST_SERVICE: bool = True   # GUESS — no Article-7.9-equivalent restriction found
    PERMITTED_POST_SERVICE: Tuple[str, ...] = (   # GUESS — no textual restriction exists; real, ordinary post-service paths
        "ordinary_civil_service",
        "judiciary_if_qualified",
        "academia",
        "private_sector",
    )
    # GUESS magnitude, CONFIDENT direction — deliberately small, reflecting
    # a focused audit body rather than a sprawling surveillance apparatus
    # (contrast Myanmar's 2000). Loosely grounded in the real Bundesrechnungshof's
    # total organisation being in the order of ~1,100 staff federally; this
    # field models only the "agent"-equivalent frontline-audit slice of
    # that, not a literal headcount match.
    MAX_AGENTS: int = 300
    # GUESS lists — simplified proxies for the Bundesrechnungshof's real
    # specialised-senate structure plus the Art. 45a/45b parliamentary
    # defence-oversight bodies. Art. 45b's Parliamentary Commissioner for
    # the Armed Forces (Wehrbeauftragter) deserves explicit note: per the
    # README, "No other scenario in this project has one, and it is a
    # direct structural answer to Myanmar 2008's military self-adjudication."
    FUNCTIONAL_DIVISIONS: Tuple[str, ...] = (
        "federal_budget_audit_division",
        "defence_expenditure_audit_division",
        "social_insurance_audit_division",
    )
    MANDATE_DIVISIONS: Tuple[str, ...] = (
        "public_finance_integrity_division",
        "armed_forces_ombudsman_division_art45b",         # Wehrbeauftragter — real, unique to this scenario
        "parliamentary_inquiry_support_division_art45a",   # Defence Committee committee-of-inquiry powers
    )
    OPERATIONAL_DIVISIONS: Tuple[str, ...] = (
        "field_audit_division",
        "annual_report_division_art114",
        "whistleblower_intake_division",
    )


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 30, 70-74, 83-87, 106-107 — FEDERAL STRUCTURE
# Maps to: constitution.py / constitution_2008.py → FederalConfig
# THE REAL FEDERAL BENCHMARK IN THE 7-SCENARIO SET
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FederalConfig:
    """Arts. 70-74 (legislative powers), Arts. 83-87 (Land execution of federal law),
    Arts. 106-107 (fiscal federalism and horizontal equalisation)"""

    STATE_COUNT: int = 10   # matches FoundationalConfig.STATE_COUNT — CONFIDENT pairing
    ETHNIC_GROUPS: int = 0   # CONFIDENT — no constitutionally recognised ethnic-group structure (README, verbatim)

    # GUESS, flagged per the README's explicit instruction NOT to reuse
    # MFU's 35/35/30 split: Art. 106 sets the constitutional VAT/income-tax
    # revenue-sharing categories between the Federation and the Lander, with
    # the exact percentages set by the (statutory) Finanzausgleichsgesetz —
    # which the README itself says "have changed repeatedly". The 1969
    # Finanzreform (Art. 106/107 rewrite) sits right at this file's 1968
    # cutoff, so no single precisely-dated split is pinned here. These two
    # values are an illustrative Bund/Land split, NOT a specific cited year's
    # FAG figure — flagged honestly rather than presented as precisely
    # sourced. RESOURCE_ETHNIC_DIRECT_SHARE is set to 0.0 (inert) because no
    # ethnic-direct-transfer concept exists in German fiscal federalism at all.
    RESOURCE_STATE_SHARE: float = 0.45          # Lander share, illustrative — GUESS, not a specific FAG year
    RESOURCE_FEDERAL_DEV_SHARE: float = 0.55    # Federation share, illustrative — GUESS, not a specific FAG year
    RESOURCE_ETHNIC_DIRECT_SHARE: float = 0.0   # inert — no ethnic-transfer concept exists — CONFIDENT absence

    # GUESS — grounded in the real Sozialstaatsprinzip (Art. 20(1), "social
    # federal state") and Art. 107(2)'s equalisation mandate; set well below
    # Myanmar's tolerance-of-inequality 0.65, close to MFU's own 0.45 target
    # but slightly lower, reflecting Germany's real redistributive record
    # (disposable-income Gini typically ~0.29-0.31 in recent OECD data,
    # not itself a 1949-1999 constitutional figure, but directionally
    # supportive).
    GINI_THRESHOLD: float = 0.35
    STATE_GDP_CAP: float = 0.50   # GUESS — no specific constitutional cap exists; placeholder consistent with the schema's convention elsewhere

    # CONFIDENT — opposite of Myanmar Section 17(b); German Land governments
    # are fully civilian, the Bundeswehr has no regional-executive role.
    MILITARY_IN_REGIONAL_EXECUTIVE: bool = False

    # GUESS — statutory/EU-law anti-trust enforcement (Gesetz gegen
    # Wettbewerbsbeschrankungen, Bundeskartellamt), not literal Basic Law
    # text, but real and genuinely enforced — unlike Myanmar's "on paper
    # only" framing. Reused close to MFU's own enforced value.
    SECTOR_MONOPOLY_CAP: float = 0.30

    # GUESS but directionally meaningful departure from constitution_2008.py's
    # deliberate nullification of this mechanic: Germany's real corruption
    # trajectory is already near-floor essentially from year zero (V-Dem
    # 0.020 at 1949, 0.011 from 1968), so, unlike Myanmar, there is no
    # principled reason to nullify MFU's "virtuous cycle" mechanic here —
    # it is left REACHABLE, consistent with the real outcome data, rather
    # than mechanically disabled the way constitution_2008.py disables it.
    TRUST_ACCELERATION_TRIGGER_CORRUPTION: float = 0.03   # Germany's real corruption levels (0.011-0.024) sit at or below this
    TRUST_ACCELERATION_TRIGGER_YEARS: int = 5              # same window MFU itself uses — GUESS, reused for consistency
    TRUST_ACCELERATION_MULTIPLIER: float = 1.30            # GUESS, below MFU's own 1.50 — a real but not self-designed-optimal bonus


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 26, 35, 45a, 45b, 65a, 87a, 91, 115b — ARMED FORCES
# Maps to: constitution.py / constitution_2008.py → MilitaryConfig
# THE STRUCTURAL MIRROR IMAGE OF MYANMAR 2008 — SEE THE MODULE DOCSTRING
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class MilitaryConfig:
    """Art. 87a (1956, armed forces for defence only), Art. 65a (1956, civilian
    command), Art. 115b (1968, command passes to the Chancellor in a state of
    defence — never to a general), Art. 45a/45b (1956, parliamentary oversight),
    Art. 35 (disaster-relief use), Art. 26 (aggressive war unconstitutional)"""

    # CONFIDENT, directly from the README: "No coup mechanism. No military
    # political role. No reserved seats. No military self-adjudication. No
    # immunity." The structural opposite of Myanmar Sections 40(c)/417-419.
    COUP_LEGAL_MECHANISM: bool = False
    # GUESS — set to an unreachable value (>1.0) using the same "effectively
    # impossible" idiom this schema uses elsewhere for mechanisms that are
    # constitutionally absent, not merely improbable.
    COUP_TRIGGER_CORRUPTION: float = 1.01
    COUP_TRIGGER_TRUST: float = -0.01   # unreachable low floor, same idiom

    # CONFIDENT — no single "Commander-in-Chief" office exists at all;
    # command sits with the civilian Federal Minister of Defence in
    # peacetime (Art. 65a) and passes to the civilian Federal Chancellor —
    # never to a general — in a state of defence (Art. 115b, 1968).
    COMMANDER_IN_CHIEF_APPOINTMENT: str = "not_applicable_no_commander_in_chief_office"
    # CONFIDENT — Art. 101(1) extraordinary courts inadmissible; Art. 96(2)
    # narrow military-court carve-out sits within the civilian Justice
    # Ministry's portfolio, not a self-adjudicating military justice system.
    MILITARY_SELF_ADJUDICATION: bool = False

    SINGLE_CHAIN_OF_COMMAND: bool = True   # the Bundeswehr is a unified armed force under Art. 87a — CONFIDENT

    MILITARY_POLITICAL_ROLE: bool = False   # CONFIDENT, directly from the README

    PARLIAMENTARY_SEAT_PERCENTAGE: float = 0.0   # CONFIDENT, matches ChamberConfig.MILITARY_SEAT_PERCENTAGE
    PARLIAMENTARY_SEAT_APPOINTMENT: str = "not_applicable_no_reserved_seats"

    # GUESS magnitude, CONFIDENT direction — high civilian-command loyalty,
    # grounded in the real zero-coup record (Powell & Thyne dataset: zero
    # coded coup events for Germany, 1950-2026, the only country in this
    # project's set with a completely empty record).
    LOYALTY_INITIAL: float = 0.90
    # GUESS magnitude, CONFIDENT direction — even slower decay than
    # Myanmar's institutional-loyalty framing, reflecting the structural
    # civilian-command design (Art. 65a/115b) plus the Art. 45b Wehrbeauftragter
    # ombudsman providing a continuous real check.
    LOYALTY_CORRUPTION_DRAG: float = 0.0005
    # CONFIDENT, mirrors Myanmar's own 0.0 numerically but for the OPPOSITE
    # real reason: there, "the military IS the regime" so no coup risk TO
    # the regime exists; here, no constitutional coup mechanism exists AT
    # ALL, so there is nothing for this multiplier to activate.
    COUP_PROBABILITY_MULTIPLIER: float = 0.0

    # CONFIDENT direction, narrow in real scope — Art. 35(2)-(3) (disaster
    # relief, cross-Land assistance), Art. 87a(3)-(4) (1968, narrow internal-
    # security support under Art. 91 conditions), each explicitly terminable
    # by a Bundestag or Bundesrat vote (Art. 87a(4): "shall be discontinued
    # if the Bundestag or the Bundesrat so demands"). Set True (domestic use
    # IS constitutionally possible) but the trigger field below captures how
    # narrow and reversible this is, in deliberate contrast to Myanmar's
    # unilateral, open-ended Section 40(b).
    DOMESTIC_FORCE_AUTHORIZED: bool = True
    DOMESTIC_FORCE_TRIGGER: str = "narrow_enumerated_art35_87a3_87a4_91_terminable_by_either_chamber"

    # GUESS — unreachable floor, same idiom as COUP_TRIGGER_TRUST above.
    # This models the military turning against civilian authority, which
    # has no real-world German analogue to calibrate against (opposite
    # real reason from constitution_2008.py's own "the military IS the
    # regime" framing for the identical numeric encoding).
    COUP_TRIGGER_LOYALTY: float = -0.01
    COUP_TRIGGER_APPROVAL: float = -0.01

    NS_CIVILIAN_TRACK_THRESHOLD: float = 0.65   # reused unchanged — citizen-side sorting criterion, not constitution-specific (same reasoning constitution_2008.py gives for this field)
    # GUESS magnitude, CONFIDENT direction — between MFU's voluntary-civic-
    # integration framing (0.15) and Myanmar's coercive-conscription framing
    # (0.05): conscription (Wehrpflicht, Art. 12a, 1956) was real and
    # compulsory for most men, but included a genuine, widely used
    # conscientious-objection and substitute-civilian-service (Zivildienst)
    # track (Art. 4(3)), which is a real documented integration mechanism,
    # not pure coercion.
    NS_LOYALTY_BOOST: float = 0.12
    # CONFIDENT direction — inert/near-zero, since the cross-ethnic-exposure
    # framing this field models has no real German referent (no
    # constitutionally recognised ethnic-group structure to build trust
    # across).
    NS_ETHNIC_EXPOSURE_BOOST: float = 0.0
    # GUESS magnitude — Zivildienst (substitute civilian service) placements
    # were overwhelmingly in hospitals, elder care, and disability support —
    # a real, documented civic-contribution effect, between Myanmar's
    # coercive 0.02 and MFU's own 0.10.
    NS_CIVIC_CONTRIBUTION_BOOST: float = 0.08


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 14, 15, 88, 109, 115 — ECONOMIC FRAMEWORK
# Maps to: constitution.py / constitution_2008.py → EconomicConfig
# THE BASIC LAW IS DELIBERATELY ECONOMICALLY NEUTRAL (WIRTSCHAFTSPOLITISCHE
# NEUTRALITAT DOCTRINE) — MOST FIELDS BELOW ARE REAL-PRACTICE PROXIES, NOT
# LITERAL TEXTUAL CITATIONS, AND ARE FLAGGED AS SUCH
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EconomicConfig:
    """Art. 14 (property), Art. 15 (socialisation against compensation, never
    used), Art. 88 (central bank independence), Art. 109/115 (debt brake, 2009,
    outside this file's 1968 cutoff but noted)"""

    # GUESS — the postwar "soziale Marktwirtschaft" (social market economy)
    # is real, dominant economic-policy practice, but per the README the
    # Basic Law itself names no economic system at all (wirtschaftspolitische
    # Neutralitat doctrine). Flagged as practice, not text.
    ECONOMIC_SYSTEM: str = "soziale_marktwirtschaft_social_market_economy_practice_not_textual"
    TAX_BRACKETS: Tuple[float, ...] = (0.0, 0.14, 0.24, 0.42, 0.45)   # GUESS — not constitutional; illustrative only
    BLACK_MONEY_PENALTY: str = "ordinary_criminal_law_stgb_tax_evasion"   # GUESS/statutory

    # CONFIDENT — Art. 14(1) protects private property; Art. 15 permits
    # socialisation of land/resources/means of production ONLY against
    # compensation and has NEVER been invoked. The opposite framing from
    # Myanmar Section 37(a)'s blanket state ownership.
    STATE_OWNS_RESOURCES: bool = False
    PRIVATE_PROPERTY_PROTECTED: bool = True

    # GUESS/statutory — real, enforced antitrust law (Gesetz gegen
    # Wettbewerbsbeschrankungen, Bundeskartellamt) plus EU competition law,
    # not Basic Law text itself, but genuinely enforced (unlike Myanmar's
    # "on paper" framing).
    ANTI_MONOPOLY: bool = True
    CRONYISM_ENABLED: bool = False   # CONFIDENT, opposite of Myanmar's framing

    # CONFIDENT — Art. 15 EXPRESSLY permits nationalisation/socialisation
    # against compensation (never exercised); Germany does not BAN it the
    # way Myanmar's Section 36(d) does — a real and interesting structural
    # difference in the opposite direction from what the field name might
    # suggest at a glance.
    NATIONALIZATION_BANNED: bool = False

    # GUESS magnitude, CONFIDENT direction — near-zero, reflecting the
    # near-best-in-class real corruption outcome (opposite of Myanmar's
    # 0.03 high drag).
    CORRUPTION_GDP_DRAG: float = 0.002
    # GUESS — no structural crony-capital phenomenon comparable to Myanmar's
    # military-business-conglomerate design is encoded (ordinary corruption/
    # lobbying exists in any real polity, but not as a structural capture
    # mechanism the way 2008 Myanmar's design has one).
    CRONY_CAPITAL_SHARE: float = 0.0

    # GUESS — statutory (Aussenwirtschaftsgesetz/AWV investment-screening
    # regime), not Basic Law text, AND largely anachronistic for the "as
    # amended through 1968" period — Germany's modern foreign-investment
    # screening regime dates substantially later (2004/2017/2020 reforms).
    # Kept as a structural placeholder for schema completeness only.
    STRATEGIC_SECTORS: Tuple[str, ...] = (
        "defence",
        "critical_infrastructure",
        "telecommunications",
        "energy_grid",
        "banking",
    )
    OPEN_SECTORS: Tuple[str, ...] = (
        "manufacturing",
        "retail",
        "services",
        "agriculture",
        "tourism",
    )
    FOREIGN_CAP_STRATEGIC: float = 0.49   # GUESS, reused MFU's own structural proxy — see anachronism note above
    FOREIGN_CAP_OPEN: float = 1.00         # CONFIDENT direction, matches MFU/2008


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 5(3), ARTICLE 7 — SCIENCE AND EDUCATION
# Maps to: constitution.py / constitution_2008.py → ScienceConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ScienceConfig:
    """Art. 5(3) (academic freedom — the strongest textual basis in the 7-scenario
    set), Art. 7 (school system, a Land competence)"""

    # GUESS, per the README's own framing: "effectively true in practice but
    # NOT a constitutional guarantee" — tuition policy is a Land competence
    # (Art. 30, 70) and has varied (general tuition fees existed in several
    # Lander 2006-2014, then abolished).
    PHD_TUITION_FREE: bool = True
    RESEARCHER_ROYALTY: float = 0.0   # CONFIDENT — no MFU-style royalty scheme exists
    # GUESS magnitude, CONFIDENT direction — high, reflecting the real
    # postwar West German scientific/industrial recovery and strong
    # technical-university tradition, far above Myanmar's 0.005.
    KNOWLEDGE_CAPITAL_GROWTH: float = 0.03

    # CONFIDENT direction — opposite of Myanmar's nationalist framing. Art.
    # 5(3)'s one real caveat ("Freedom of teaching shall not release any
    # person from allegiance to the constitution") is a constitutional-
    # loyalty requirement, not a nationalist-content requirement — a real
    # and distinct nuance worth keeping precise.
    EDUCATION_NATIONALIST_FRAMING: bool = False

    # GUESS magnitude, CONFIDENT direction — low, reflecting that West
    # Germany was historically a NET ATTRACTOR of labour (the Gastarbeiter
    # recruitment programme began officially in 1955, reflecting a labour
    # SHORTAGE, not a brain-drain problem), the opposite of Myanmar's high
    # brain-drain framing.
    BRAIN_DRAIN_RATE_BASE: float = 0.03
    # CONFIDENT — Art. 5(3): "Arts, sciences, research and teaching shall be
    # free." Per the README, "the strongest textual basis in the set."
    ACADEMIC_FREEDOM: float = 0.95

    RESEARCHER_ROYALTY_RATE: float = 0.0   # mirrors RESEARCHER_ROYALTY above — CONFIDENT pairing
    # GUESS magnitude — between Myanmar's 0.05 and MFU's own 0.25, reflecting
    # a real but not MFU-level centrally-designed PhD-economy incentive.
    PHD_KNOWLEDGE_CAPITAL_BOOST: float = 0.20


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 79 — AMENDMENT OF THE BASIC LAW
# Maps to: constitution.py / constitution_2008.py → AmendmentConfig
# VERBATIM ART. 79 — THE MOST-AMENDED AND MOST DURABLE CONSTITUTION IN THE SET
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class AmendmentConfig:
    """Art. 79 — Amendment of the Basic Law"""

    # GUESS — the Basic Law has no specific numeric "% of members needed to
    # INITIATE an amendment bill" the way Myanmar Section 435 does; ordinary
    # Art. 76 legislative-initiative rules apply (a Bundestag Fraktion,
    # the Bundesrat, or the Federal Government may introduce any bill,
    # including an amending one). The figure below is borrowed from the
    # real ordinary-bill-initiation practice (roughly a parliamentary-group
    # share of seats), not a literal constitutional citation.
    AMENDMENT_INITIATION_THRESHOLD: float = 0.05

    # CONFIDENT, per the README's explicit recommendation: Art. 79(3)'s
    # eternity clause is an ABSOLUTE BAR, not a high threshold — representing
    # it as a normal percentage would lose the distinction the way a
    # straight 0.667/1.00 pairing would. Set to an unreachable value (>1.0)
    # using the same idiom used elsewhere in this file, paired with the
    # explicit ETERNITY_CLAUSE fields below.
    ENTRENCHED_AMENDMENT_THRESHOLD: float = 1.01
    ENTRENCHED_REQUIRES_REFERENDUM: bool = False   # CONFIDENT, directly from the README: "No referendum requirement at federal level"

    # CONFIDENT — Art. 79(2): "two thirds of the Members of the Bundestag
    # and two thirds of the votes of the Bundesrat" (members, not votes
    # cast, for the Bundestag — an absolute supermajority).
    STANDARD_AMENDMENT_THRESHOLD: float = 0.667

    MILITARY_VETO_ON_AMENDMENTS: bool = False   # CONFIDENT — no reserved military seats exist at all to repurpose as a veto bloc

    # CONFIDENT — Art. 79(3)'s real scope is narrower than a whole-chapter
    # entrenchment design: it protects specific principles/elements, not
    # entire chapters. Listed here verbatim per the README's own
    # ETERNITY_CLAUSE_SCOPE suggestion (duplicated into this field to match
    # the schema's existing field name/convention).
    ENTRENCHED_CHAPTERS: Tuple[str, ...] = (
        "human_dignity_article_1",
        "democratic_social_federal_state_principles_article_20",
        "federal_division_into_laender",
        "laender_participation_in_legislative_process",
    )
    REVIEW_INTERVAL: int = 0   # CONFIDENT, directly from the README: no periodic mandatory review cycle exists; amendment is continuous/ad hoc via ordinary legislation
    CITIZENS_ASSEMBLY_SIZE: int = 320   # reused unchanged — no real federal civic-lottery equivalent existed during 1949-1999 (the real German Burgerrat practice begins circa 2019) — CONFIDENT absence, same reasoning constitution_2008.py gives

    # Bonus fields beyond the 2008 skeleton, added per the README's explicit
    # suggestion to represent the eternity clause as an absolute bar rather
    # than a disguised threshold. Not currently read by any live engine code
    # (confirmed by grep at encoding time) — included for documentation/
    # future-proofing and because they cost nothing and materially improve
    # the honesty of this encoding.
    ETERNITY_CLAUSE: bool = True                                    # CONFIDENT, Art. 79(3)
    ETERNITY_CLAUSE_SCOPE: Tuple[str, ...] = (                        # CONFIDENT, same four items as ENTRENCHED_CHAPTERS above
        "human_dignity_article_1",
        "democratic_social_federal_state_principles_article_20",
        "federal_division_into_laender",
        "laender_participation_in_legislative_process",
    )
    AMENDMENT_JUDICIAL_REVIEW: bool = True                           # CONFIDENT — the FCC reviews amendments against Art. 79(3)


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 123, 131, 139 — CONTINUITY / TRANSITIONAL PROVISIONS
# Maps to: constitution.py / constitution_2008.py → TransitionConfig
# NO AMNESTY CLAUSE, NO IMMUNITY CLAUSE — THE OPPOSITE OF EVERY OTHER
# GUARDIANSHIP-ADJACENT CONSTITUTION IN THIS PROJECT — BUT SEE THE L6
# CAVEAT BELOW, WHICH MUST TRAVEL WITH THE CLAIM
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TransitionConfig:
    """Art. 123 (continuity of prior law, conditional), Art. 131 (former civil
    servants' status), Art. 139 (denazification law unaffected) — plus the real
    Allied-occupation-to-full-sovereignty timeline (1949 Occupation Statute ->
    1952/1955 General Treaty -> 1990 Two Plus Four Treaty)"""

    # CONFIDENT, genuinely dateable within this file's 50-year horizon: the
    # Basic Law was adopted under Allied occupation; the Occupation Statute
    # (1949) and the General Treaty/Deutschlandvertrag (1952/1955) governed
    # residual Allied rights until the Two Plus Four Treaty (12 September
    # 1990, simulated year 41 of this scenario's 50-year horizon) restored
    # full sovereignty. Unlike every other field in this class (which models
    # a Myanmar-specific "regime continuity" concept with no real German
    # equivalent), this one has a genuine, real, dateable analogue.
    TRANSITION_PERIOD_YEARS: int = 41
    # CONFIDENT, directly from the README: "No amnesty clause... the
    # opposite of Myanmar 2008 s.445". MUST travel with the L6 caveat below.
    AMNESTY_GRANTED: bool = False

    # CONFIDENT, flagged for a follow-up citation check (not explicitly
    # quoted in the research package README, but a well-established,
    # independently verifiable Basic Law provision): Art. 123(1), "Law in
    # force... shall remain in force insofar as it does not conflict with
    # this Basic Law" — a real but CONDITIONAL continuity (compatibility-
    # gated), unlike Myanmar Section 445's unconditional validity preservation.
    PRIOR_LAWS_VALID: bool = True
    # CONFIDENT — Art. 139 expressly preserves denazification legislation;
    # no blanket immunity for prior-regime actions exists in the text.
    PRIOR_ACTIONS_IMMUNE: bool = False

    # CONFIDENT that Art. 131 (statutory regulation of former public
    # servants' legal status) is the real mechanism here, AND that it
    # historically produced substantial reinstatement of former Nazi-era
    # officials — this is exactly the mechanism the L6 caveat below refers to.
    CIVIL_SERVANTS_RETAIN_POSTS: bool = True

    # GUESS — field name inherited from the engine's Myanmar-specific
    # "tatmadaw_transition" schema naming (see this file's module docstring
    # and the dedicated TatmadawTransitionConfig-equivalent section below);
    # not a claim about any real German pension mechanism. Mirrors MFU's
    # own "no special multiplier" framing (standard civil-service/soldiers'
    # pension law, no bonus).
    TATMADAW_PENSION: float = 0.0
    TATMADAW_IMMUNITY: bool = False   # CONFIDENT, consistent with AMNESTY_GRANTED/PRIOR_ACTIONS_IMMUNE above

    # L6 HONEST CAVEAT, required reading alongside AMNESTY_GRANTED=False and
    # PRIOR_ACTIONS_IMMUNE=False above (per the research package's explicit
    # instruction: "Comment both in the code and say both in the paper"):
    # the Basic Law's TEXT grants no amnesty and no immunity. The POLITICAL
    # PRACTICE of the 1950s-60s told a different story — West Germany's
    # 1949 and 1954 federal amnesty laws (Straffreiheitsgesetze) and Art.
    # 131's reinstatement of former Nazi-era civil servants produced
    # substantial de facto impunity, and real-world prosecution of Nazi-era
    # crimes through the 1950s-60s was poor. The comparative point — a
    # constitutionally TEXTUAL immunity (Myanmar/Thailand/Pakistan/Chile) vs.
    # NO constitutional immunity in Germany's text — is real, but it should
    # not be oversold as "Germany fully confronted its past constitutionally
    # from day one." Both halves of this finding belong in the manuscript.


# ══════════════════════════════════════════════════════════════════════════════
# SAFEGUARDS — functional analogues of constitution.py's MFU-specific design,
# mapped onto real Basic Law mechanisms where one exists
# Maps to: constitution.py / constitution_2008.py → SafeguardConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SafeguardConfig:
    """Real Basic Law safeguards mapped onto the MFU-derived schema's field names"""

    CHANCELLOR_COOLING_OFF_ENFORCED: bool = False   # GUESS — no textual cooling-off provision found, matches ExecutiveConfig.CHANCELLOR_COOLING_OFF=0
    # CONFIDENT, flagged for a follow-up citation check: Art. 33(2)'s
    # Bestenauslese principle is judicially enforceable (the real
    # Konkurrentenklage doctrine lets a passed-over candidate sue in the
    # administrative courts) — a genuine, independent check on merit-exam
    # integrity, unlike anything Myanmar's design has.
    MERIT_EXAM_INDEPENDENCE: bool = True
    ETHNIC_COUNCIL_YOUTH_MANDATE: bool = False   # CONFIDENT absence — no ethnic-council structure exists at all
    # CONFIDENT — mirrors IIGConfig.DIRECTOR_RENEWABLE=False above (the real
    # Bundesrechnungshof President's non-renewable 12-year term).
    IIG_SINGLE_TERM: bool = True
    # CONFIDENT, flagged for a follow-up citation check: the FCC has
    # published dissenting opinions publicly since a 1970 statutory reform
    # — real and well-documented, though note this postdates the start of
    # the simulated horizon by 21 years (true from simulated year 21/1970
    # onward, not from year 0).
    ANALYSIS_TRANSPARENCY: bool = True
    RIGHTS_ABSOLUTE: bool = True   # CONFIDENT, mirrors RightsConfig.RIGHTS_SUSPENDABLE=False, Art. 19(2)
    GENERATIONAL_ASSEMBLY_REVIEW: bool = False   # CONFIDENT absence, consistent with REVIEW_INTERVAL=0's "continuous, not scheduled" framing

    MILITARY_SEAT_RESERVATION: bool = False   # CONFIDENT, opposite of Myanmar
    COMMANDER_IN_CHIEF_VETO: bool = False      # CONFIDENT — no such office exists
    # CONFIDENT direction, flagged for a follow-up citation check: the real
    # Bundessicherheitsrat (Federal Security Council) is an ordinary CABINET
    # COMMITTEE, not a constitutional body, and has no veto power over
    # civilian government the way Myanmar's NDSC does — a real and
    # important structural distinction, not just a naming difference.
    NDSC_OVERSIGHT: bool = False

    # GUESS — no fixed pre-ruling publication window exists for the FCC
    # (cases can take months to years with no fixed deadline); this models
    # the ABSENCE of a fixed numeric window, not an absence of transparency
    # overall (ANALYSIS_TRANSPARENCY=True above already covers the latter).
    ANALYSIS_PUBLISH_BEFORE_VETO_DAYS: int = 0


# ══════════════════════════════════════════════════════════════════════════════
# NO CRYPTOGRAPHIC JUSTICE / NO TOTAL RUIN MECHANISM
# Maps to: constitution.py / constitution_2008.py → CryptoJusticeConfig
# ABSENT FOR THE OPPOSITE REAL REASON FROM MYANMAR 2008 — SEE JudiciaryConfig's
# TOTAL_RUIN_THRESHOLD COMMENT
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class CryptoJusticeConfig:
    """No MFU-style Total Ruin mechanism — Germany's real ultimate constitutional
    sanctions (Art. 18 rights forfeiture, Art. 21(2) party unconstitutionality)
    are ordinary FCC rulings, not a numeric multi-signature protocol"""

    BLOCKCHAIN_ENABLED: bool = False
    ZKP_ENABLED: bool = False
    MULTI_PARTY_SIGNATURES: bool = False
    TOTAL_RUIN_MECHANISM: bool = False
    TOTAL_RUIN_STEPS: int = 0

    # GUESS — same null-encoding idiom constitution_2008.py uses (set equal
    # to JUDGE_COUNT, i.e. unreachable), consistent with TOTAL_RUIN_MECHANISM
    # = False above. Note Germany's two 8-Justice senates do not actually
    # decide jointly this way in real FCC practice — this is a structural
    # placeholder, not a description of real FCC procedure.
    COURT_SUPERMAJORITY_FOR_TOTAL_RUIN: int = 16
    SHAME_REGISTER_CORRUPTION_REDUCTION: float = 0.0   # CONFIDENT — no Shame Register mechanism exists


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 115a-115l, 53a, 80a, 91 (1968) — STATE OF DEFENCE / EMERGENCY POWERS
# Maps to: constitution.py / constitution_2008.py → EmergencyConfig
# ABSENT IN 1949; ADDED BY THE 1968 NOTSTANDSVERFASSUNG — THIS IS THE CORE
# OF WHY THIS FILE ENCODES "AS AMENDED THROUGH 1968" RATHER THAN 1949-AS-
# ENACTED. THE STRICTEST EMERGENCY CONFIGURATION IN THE 7-SCENARIO SET.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EmergencyConfig:
    """Art. 115a (state of defence declaration), Art. 115b (command to the
    Chancellor, never a general), Art. 115g (FCC expressly insulated), Art. 115l
    (legislature can terminate at any time, must terminate when conditions lapse),
    Art. 80a (state of tension), Art. 91 (1968, internal emergency)"""

    # CONFIDENT — Art. 115a(1)-(2) determination triggers; Art. 80a state of
    # tension; Art. 91 internal emergency (natural disaster or insurgency,
    # with the real Bundesrat kill-switch noted in FederalConfig's own
    # comments — see MILITARY_IN_REGIONAL_EXECUTIVE above).
    TRIGGER_SCENARIOS: Tuple[str, ...] = (
        "armed_attack_on_federal_territory_state_of_defence_art115a",
        "imminent_threat_of_armed_attack_art115a",
        "state_of_tension_art80a",
        "internal_emergency_natural_disaster_or_insurgency_art91",
    )

    # CONFIDENT, with an important framing note: unlike Myanmar's fixed
    # 365-day initial window plus two 6-month extensions, Germany's state
    # of defence has NO fixed maximum duration in the text at all — Art.
    # 115l requires the Bundestag (with Bundesrat consent) to declare it
    # terminated once conditions no longer obtain, and either chamber can
    # terminate it at ANY time. The large placeholder value below models
    # "no fixed executive-granted window" — it is a STRONGER safeguard than
    # a fixed-term-then-renewal design, not a weaker one, despite looking
    # large at a glance. Read this field together with
    # LEGISLATURE_CAN_TERMINATE-equivalent behaviour implied by
    # TOTAL_POWER_TRANSFER_POSSIBLE=False and COMMANDER_IN_CHIEF_*=False below.
    EMERGENCY_MAX_DAYS: int = 9999
    EMERGENCY_EXTENSIONS: int = 0          # CONFIDENT — no fixed-extension-count mechanic; continuous legislative control instead
    EMERGENCY_EXTENSION_MONTHS: int = 0

    # CONFIDENT — Art. 115c(2) deprivations of liberty are extended only
    # within tightly specified limits; Art. 19(2)/79(3) continue to bind
    # even during a state of defence. The single clearest Germany/Myanmar
    # contrast point in the whole file.
    RIGHTS_UNTOUCHED: bool = True

    TOTAL_POWER_TRANSFER_POSSIBLE: bool = False   # CONFIDENT, directly from the README
    POWER_TRANSFER_TRIGGER: str = "not_applicable_no_total_power_transfer_mechanism"

    # CONFIDENT — no Commander-in-Chief office exists at all (see
    # MilitaryConfig.COMMANDER_IN_CHIEF_APPOINTMENT); command in a state of
    # defence passes to the civilian Federal Chancellor (Art. 115b), and
    # Art. 115g expressly insulates the Federal Constitutional Court's
    # status and functions even then.
    COMMANDER_IN_CHIEF_LEGISLATIVE: bool = False
    COMMANDER_IN_CHIEF_EXECUTIVE: bool = False
    COMMANDER_IN_CHIEF_JUDICIAL: bool = False

    # CONFIDENT, directly from the README: the Joint Committee (Art. 53a)
    # legislates in place of the Bundestag/Bundesrat only where they
    # genuinely cannot act; the legislature is never formally suspended
    # (contrast Myanmar Section 418(a)'s explicit Hluttaw suspension).
    LEGISLATURE_SUSPENDED_DURING_EMERGENCY: bool = False

    # CONFIDENT — the structural opposite of Myanmar's 1.0 "full probability
    # activation": an emergency declaration here cannot translate into a
    # coup-style power transfer at all, by design.
    EMERGENCY_COUP_PROBABILITY_MULTIPLIER: float = 0.0


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLES 26, 87a(2) — RULES OF ENGAGEMENT / FOREIGN POLICY POSTURE
# Maps to: constitution.py / constitution_2008.py → ROEConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ROEConfig:
    """Art. 26(1) (aggressive war unconstitutional and criminal), Art. 87a(2)
    (defence-only mandate)"""

    # GUESS — a historical/policy characterisation (NATO membership from
    # 1955, later EU defence integration), not a literal Basic Law citation
    # the way Myanmar Section 41's non-alignment framing is — the Basic Law
    # itself names no alliance. Deliberately the OPPOSITE posture from
    # Myanmar's non-aligned framing.
    FOREIGN_POLICY: str = "nato_and_eu_integrated_defensive_posture_not_textual"

    NO_AGGRESSION: bool = True   # CONFIDENT — Art. 26(1), directly quoted in the README

    # CONFIDENT, and a genuinely interesting real contrast with Myanmar
    # Section 42(b): West Germany's postwar sovereignty settlement was built
    # around EXTENSIVE Allied/NATO troop presence (Occupation Statute, 1952/
    # 1955 General Treaty, later the NATO Status of Forces Agreement),
    # continuing to this day in smaller numbers. Set to the OPPOSITE value
    # from Myanmar's True — foreign troop presence was central to the
    # postwar settlement, not prohibited.
    NO_FOREIGN_TROOPS: bool = False

    # CONFIDENT — the structural opposite of Myanmar's "president_or_
    # commander_discretion": domestic military use is narrow, enumerated
    # (Art. 35, 87a(3)-(4), 91), and terminable by either chamber's vote.
    DOMESTIC_MILITARY_USE: str = "narrow_enumerated_art35_87a3_87a4_91_terminable_by_either_chamber"
    # GUESS magnitude, CONFIDENT direction — set HIGH (the opposite of
    # Myanmar's 0.05 "very low threshold, broad discretion"), reflecting the
    # narrow, enumerated, terminable nature of domestic deployment.
    DOMESTIC_FORCE_THRESHOLD: float = 0.90

    EXTERNAL_ROE: str = "defensive_only_aggression_unconstitutional_art26"   # CONFIDENT, directly from the README
    EXTERNAL_FULL_FORCE: bool = False   # CONFIDENT, the direct opposite of MFU's Article 17 "scorched earth" doctrine


# ══════════════════════════════════════════════════════════════════════════════
# NO PSYCHOLOGICAL-HEALTH MANDATE IN THE BASIC LAW
# Maps to: constitution.py / constitution_2008.py → PsychConfig
# ABSENT FOR A DIFFERENT REAL REASON FROM MYANMAR'S ABSENCE — SEE COMMENTS
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PsychConfig:
    """No constitutional psychological-health mandate for officials — same
    structural absence as constitution_2008.py, but for the opposite real reason
    (an advanced, well-resourced welfare state that handles this through ordinary
    statute, not constitutional neglect)"""

    BIANNUAL_SCREENING: bool = False
    ANTI_BIAS_REVIEW: bool = False
    # CONFIDENT that this is correctly False at the CONSTITUTIONAL level —
    # real statutory war-victims'-relief welfare legislation (the 1950
    # Bundesversorgungsgesetz) DID exist and mattered for the real postwar
    # population, but it is ordinary welfare law, not a Basic Law mandate,
    # so False remains the accurate encoding for this specific field.
    TRAUMA_CARE_MANDATED: bool = False

    # GUESS magnitude, CONFIDENT direction — meaningfully above zero,
    # reflecting the real, well-documented early-postwar population
    # composition (approximately 8 million expellees from the former
    # eastern territories, war widows, returning POWs as of 1949), distinct
    # from Myanmar's ongoing-ethnic-conflict framing for the same field.
    POPULATION_TRAUMA_BASE: float = 0.30
    # GUESS, directionally grounded in the real Wirtschaftswunder-era
    # social stabilisation and reconstruction: set NEGATIVE (gradual
    # improvement/healing over the simulated horizon), the opposite
    # direction from Myanmar's ongoing-accumulation framing for this field.
    TRAUMA_ACCUMULATION_RATE: float = -0.005
    # CONFIDENT — inert/neutral; no constitutionally recognised ethnic-group
    # structure exists for this multiplier to differentiate across.
    ETHNIC_TRAUMA_MULTIPLIER: float = 1.0

    SCREENING_INTERVAL_MONTHS: int = 9999       # same "never triggers within the simulated horizon" null idiom as constitution_2008.py — GUESS
    SEVERE_PROBATION_MONTHS: int = 9999          # same idiom — GUESS
    OUTCOME_STABLE_THRESHOLD: float = 0.40       # reused neutral diagnostic-scale threshold — CONFIDENT (not a constitutional design choice, same reasoning as constitution_2008.py)
    OUTCOME_SEVERE_THRESHOLD: float = 0.70
    # GUESS, deliberate no-op — mirrors constitution_2008.py's own choice to
    # make this field's literal string NOT match the engine's string check,
    # modelling "no formal consequence mechanism exists to formally stop",
    # consistent with TRAUMA_CARE_MANDATED=False above.
    STOP_CONSEQUENCE: str = "no_formal_consequence_mechanism_exists"

    # GUESS — adapted from constitution_2008.py's own list to real,
    # documented West German postwar social-history categories rather than
    # reusing Myanmar's ethnic-suppression-flavoured categories, which have
    # no real German referent for this file's encoded population.
    TRAUMA_CATEGORIES: Tuple[str, ...] = (
        "wartime_conflict_and_occupation",
        "forced_displacement_expellee_experience",
        "divided_family_cold_war_border_separation",
        "postwar_reconstruction_hardship",
    )
    # GUESS magnitude, CONFIDENT direction — set LOWER than Myanmar's
    # (0.20, 0.45), reflecting stronger real institutional/rule-of-law
    # buffering, consistent with the rest of this file's realism direction.
    TRAUMA_DISTORTION_RANGE: Tuple[float, float] = (0.05, 0.20)


# ══════════════════════════════════════════════════════════════════════════════
# ARTICLE 20(1) SOZIALSTAATSPRINZIP / ARTICLES 72(2), 106, 107 — "EQUIVALENCE
# OF LIVING CONDITIONS"
# Maps to: constitution.py / constitution_2008.py → NorthStarConfig
# THE BASIC LAW STATES NO DEVELOPMENT GOAL — THESE ARE THE NEAREST REAL
# TEXTUAL ANCHORS, PER THE RESEARCH PACKAGE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class NorthStarConfig:
    """Art. 20(1) (social federal state principle), Art. 72(2)/106/107
    ('equivalence of living conditions' / financial-equalisation language) —
    the nearest real textual anchors; the Basic Law itself states no
    development goal, per the research package"""

    OBJECTIVES: Tuple[str, ...] = (
        "social_federal_state_principle_art20",
        "equivalence_of_living_conditions_art72_106_107",
        "human_dignity_as_inviolable_foundation_art1",
    )

    MILITARY_POLITICAL_ROLE_PERPETUATED: bool = False   # CONFIDENT, mirrors MilitaryConfig.MILITARY_POLITICAL_ROLE=False

    # GUESS label — grounded in the real Art. 20(1)/72(2)/106/107 textual
    # anchors noted above, per the README's own suggestion for this field.
    PROGRESS_METRIC: str = "social_federal_state_and_living_conditions_equivalence_index"
    # GUESS, grounded in the real, strong V-Dem/WGI levels Germany actually
    # achieved by the end of the simulated horizon (approximately 1999),
    # rather than an aspirational self-designed target (MFU) or an
    # "irrelevant" framing (Myanmar).
    TARGET_YEAR_50_PROGRESS: float = 0.85

    # GUESS — no literal "PhD economy" constitutional design exists the way
    # MFU has one, but Art. 5(3)'s strong academic-freedom guarantee and the
    # real postwar scientific/industrial recovery provide real (if non-
    # numeric) textual support for leaving this mechanic enabled rather than
    # nullified the way constitution_2008.py nullifies it.
    PHD_COMPOUNDING_ENABLED: bool = True
    KNOWLEDGE_CAPITAL_TARGET: float = 0.75   # GUESS, opposite direction from Myanmar's 0.0


# ══════════════════════════════════════════════════════════════════════════════
# SIMULATION PARAMETERS — Scenario DE calibration
# Maps to: constitution.py / constitution_2008.py → SimulationConfig
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class SimulationConfig:
    """Ka-Nova Scenario DE simulation parameters"""

    SCENARIO: str = "DE"
    SCENARIO_NAME: str = "West_Germany_Basic_Law_1949_as_amended_through_1968"
    # CONFIDENT — matches scenario_registry.py's slug "germany_1968" and
    # Kaung's confirmed instrument-definition decision (.claude/memory.md
    # section 4a decision 3; research package flag F1 option (b)).
    CONSTITUTIONAL_FRAMEWORK: str = "1949_basic_law_as_amended_through_1968"

    # THE HEADLINE VALIDATION FIGURE OF THIS ENTIRE FILE. CONFIDENT — V-Dem
    # v16, West Germany entity, 1949 political-corruption index = 0.020, a
    # real observation at the exact simulated year zero. Falls to 0.011 from
    # simulated year 19 (1968) onward, flat to year 50 (1999). Compare
    # Scenario A/MFU's own locked year-50 value: 0.0122 +/- 0.0073
    # (.claude/memory.md section 6). This is the strongest external-
    # validation result available anywhere in the 7-constitution project —
    # a real, independently-authored, Allied-supervised democratic
    # constitution's observed outcome lands inside the self-designed success
    # baseline's own confidence interval. See this file's module docstring
    # for the full framing (research package flags F2/L5).
    YEAR_ZERO_CORRUPTION: float = 0.020
    # GUESS — derivation only; no survey-based trust observation exists for
    # 1949 (ALLBUS begins 1980, Politbarometer 1977, Eurobarometer 1974, EVS
    # 1981 — none reach back to year zero; the research package's L3 flag is
    # explicit about this gap). Set moderately high rather than starting low
    # like Myanmar's 0.22, loosely consistent with West Germany's already-
    # fairly-high 1949 V-Dem polyarchy (.793) and liberal-democracy (.742)
    # scores, but NOT itself sourced to a trust survey.
    YEAR_ZERO_TRUST: float = 0.55
    # GUESS, flagged explicitly per the research package's own strong
    # instruction NOT to invent a 1949 Gini ("This is a genuine gap"): the
    # schema requires a float, so this is a structurally-necessary
    # placeholder using the earliest reasonably-cited West German income-
    # distribution order of magnitude (mid-1960s SOEP/EVS-era estimates,
    # commonly in the 0.30-0.35 range) — this is NOT a 1949 figure and must
    # not be cited as one in the manuscript.
    YEAR_ZERO_GINI: float = 0.33
    # GUESS — early-1950s West German unemployment was genuinely high during
    # postwar/refugee-absorption reconstruction (commonly cited around
    # 10-11% circa 1950), well before the later Wirtschaftswunder-era near-
    # full-employment period (which itself motivated the 1955 Gastarbeiter
    # recruitment programme, see ScienceConfig.BRAIN_DRAIN_RATE_BASE above).
    # This single year-zero figure does not model that later improvement.
    YEAR_ZERO_EMPLOYMENT: float = 0.90
    # GUESS/inert — no constitutionally recognised ethnic-group structure
    # exists for DE (see FoundationalConfig/ChamberConfig/FederalConfig
    # comments above); set near zero rather than fabricating a tension
    # level for a cleavage structure that is not modelled for this scenario.
    YEAR_ZERO_ETHNIC_TENSION: float = 0.05
    # CONFIDENT, directly from the research package: "Powell-Thyne records
    # zero German coup events 1950-2026. A non-zero floor is defensible only
    # as a modelling choice" (the package also notes Germany's pre-1949
    # history — 1920 Kapp putsch, 1923 Beer Hall putsch, 1944 July 20 plot —
    # as a defensible non-zero prior; deliberately NOT used here, consistent
    # with the real post-1949 record this scenario actually encodes).
    YEAR_ZERO_COUP_RISK: float = 0.00
    # GUESS — derived only; WGI begins 1996 (+1.29 on a -2.5..+2.5 scale,
    # Political Stability/No Violence indicator). Rescaled to Ka-Nova's 0-1
    # convention: (1.29 + 2.5) / 5.0 = 0.758, rounded. This 1996 figure is
    # used as a proxy for 1949 (47 years earlier) since no earlier data
    # exists — the same L4 data-coverage limitation noted throughout this file.
    YEAR_ZERO_STABILITY: float = 0.75

    # CONFIDENT — the structural opposite of Myanmar's SimulationConfig.
    MILITARY_CONTROLS_LEGISLATURE: bool = False
    MILITARY_CONTROLS_EXECUTIVE: bool = False
    MILITARY_CONTROLS_JUDICIARY: bool = False
    RIGHTS_ENFORCEABLE: bool = True   # CONFIDENT — Art. 19(4) guaranteed judicial recourse against any act of public authority

    # CONFIDENT — locked Monte Carlo experimental design (.claude/memory.md
    # section 8), identical across every scenario including DE, NOT a
    # constitutional choice. Reused unchanged from constitution.py / constitution_2008.py.
    CITIZEN_AGENTS: int = 11_000
    # CONFIDENT — same 50-year horizon as every other scenario (locked
    # design). model_phase3.py's self.max_years intentionally still reads
    # TIME_STEPS from constitution.py's CONSTITUTION_MFU directly, never
    # from any individual scenario's own SimulationConfig — included here
    # only for field-contract completeness, per the same convention
    # constitution_2008.py documents for this exact field.
    TIME_STEPS: int = 50

    # CONFIDENT — the stable 10-Land (1957-1990) configuration, matching
    # FoundationalConfig.STATE_COUNT/FederalConfig.STATE_COUNT above. Real
    # West German Land names of that period.
    SIMULATION_STATES: Tuple[str, ...] = (
        "schleswig_holstein", "hamburg", "niedersachsen", "bremen",
        "nordrhein_westfalen", "hessen", "rheinland_pfalz",
        "baden_wurttemberg", "bayern", "saarland",
    )

    # DELIBERATELY UNCHANGED from MFU/constitution_2008.py, same reasoning
    # both of those files give: the population's psychological/behavioural
    # archetype distribution is a real, legitimate, but SEPARATE research
    # question (does a given constitution's real society produce a
    # different archetype mix?) that this file deliberately does not
    # attempt to answer, to isolate this encoding's own effect from that
    # unrelated question. Flagged for Kaung/senior-researcher if archetype-
    # distribution-by-constitution is worth pursuing later, same as the
    # open item constitution_2008.py already carries.
    ARCHETYPES: Dict = field(default_factory=lambda: {
        "civic_champion": 0.15,
        "pragmatic_survivor": 0.30,
        "ethnic_loyalist": 0.20,
        "ambitious_meritocrat": 0.15,
        "disillusioned_youth": 0.10,
        "rural_traditionalist": 0.07,
        "trauma_carrier": 0.03,
    })
    # CONFIDENT — matches AmendmentConfig.CITIZENS_ASSEMBLY_SIZE above and
    # both other constitutions' SimulationConfig for the same reasons: no
    # real civic-lottery mechanism existed anywhere in this file's encoded
    # period, so there is no principled different number to invent.
    CITIZENS_ASSEMBLY_SIZE: int = 320


# ══════════════════════════════════════════════════════════════════════════════
# TATMADAW_TRANSITION — exact attribute name required by model_phase3.py:521
# (Myanmar-specific naming literally baked into the engine; this section is
# NOT a claim about Germany having a Tatmadaw. Required because this
# scenario's chain_type is "civilian" — see model_phase3.py's
# _civilian_chain_rules(), which reads self.CONSTITUTION.tatmadaw_transition
# unconditionally for every civilian-chain scenario, A and DE alike.
# Grounded in Germany's REAL civilian-supremacy design: Art. 65a (1956,
# command vested in the civilian Federal Minister of Defence), Art. 87a(2)
# (1956, no political role, deployment limited to enumerated cases), Art.
# 45b (1956, the Wehrbeauftragter military ombudsman), and the real Allied-
# oversight taper (Occupation Statute 1949 -> General Treaty 1952/1955 ->
# Two Plus Four Treaty 1990) — NOT by analogy to any Myanmar-specific
# transition narrative.
# Confirmed by grep against the live engine (2026-10-20): ONLY
# TRUST_GAIN_PER_CLEAN_YEAR is actually dot-accessed by model_phase3.py.
# Every other field below is included for documentation/schema completeness
# and future-proofing, not because it is currently read.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TatmadawTransitionConfig:
    """Civilian-supremacy design grounded in Art. 65a/87a(2)/45b (1956) and the
    real Allied-occupation-to-full-sovereignty taper — NOT a Myanmar-transition
    analogy. Field names are inherited from the engine's literal
    'tatmadaw_transition' attribute name (model_phase3.py:521)."""

    # GUESS — this specific "mandatory N-year transition service" concept has
    # no real German referent at all (there was never a military regime to
    # transition OUT of); reused MFU's own structural placeholder value
    # purely for schema completeness. Flagged explicitly as inert for DE.
    SENIOR_GENERAL_SERVICE_YEARS: int = 5
    # CONFIDENT — this field DOES have a real, meaningful mapping: the
    # "head of military under civilian supremacy" concept maps directly
    # onto Art. 65a's civilian Federal Minister of Defence, who holds
    # command in peacetime (command passes to the civilian Chancellor,
    # never a general, in a state of defence under Art. 115b).
    SENIOR_GENERAL_ROLE: str = "federal_minister_of_defence_civilian_command_art65a"
    CIVILIAN_SUPREMACY: bool = True   # CONFIDENT — Art. 65a/87a(2)/115b

    PRESIDENTIAL_TERM_YEARS: int = 5   # matches ExecutiveConfig.PRESIDENT_TERM — CONFIDENT pairing
    # GUESS/inert — the "2nd quarter of each presidential term" civil-
    # military anchoring concept has no real German referent (Germany's
    # civilian-command design is not anchored to the presidential election
    # cycle at all, unlike MFU's own design). Reused MFU's placeholder
    # values for schema completeness only; flagged explicitly as inert for DE.
    ACTIVE_QUARTER: int = 2
    ACTIVE_YEARS_PER_TERM: Tuple[int, int] = (2, 3)
    ELECTIONS_SERVED: int = 2

    BLANKET_IMMUNITY: bool = False   # CONFIDENT, consistent with TransitionConfig.AMNESTY_GRANTED=False above
    WAR_CRIMES_PROVEN_TRIGGER: str = "ordinary_criminal_prosecution_stgb_volkerstrafgesetzbuch"   # GUESS/statutory
    # CONFIDENT direction, same real reasoning as the principle (not the
    # practice) of TransitionConfig's L6 caveat: the constitutional
    # presumption is ordinary civilian life continues absent proof — though
    # real history (Art. 131 reinstatement) shows this benefited even many
    # who arguably deserved more scrutiny. See TransitionConfig's L6 comment.
    WAR_CRIMES_UNPROVEN: str = "civilian_reintegration_proceeds_normally"
    PROSECUTION_BODY: str = "ordinary_courts_and_fcc_for_rights_forfeiture_only"   # GUESS/CONFIDENT mix
    EVIDENCE_STANDARD: str = "in_dubio_pro_reo_beyond_reasonable_doubt"   # GUESS, standard German/common-law-equivalent criminal evidentiary principle

    CIVILIAN_ROLE_ELIGIBLE: bool = True
    CIVILIAN_ROLE_REQUIRES_MERIT: bool = True   # CONFIDENT — Art. 33(2) Bestenauslese applies to ordinary civil-service entry
    PENSION_MULTIPLIER: float = 1.0   # GUESS — no special pension multiplier documented for former military personnel
    PENSION_BASIS: str = "standard_civil_service_and_soldiers_pension_law"   # GUESS
    SPECIAL_PRIVILEGES: bool = False   # CONFIDENT

    # CONFIDENT — set to 0.0 rather than Myanmar's 0.15, since there is no
    # real documented residual coup-risk-from-legal-exposure dynamic for
    # Germany to calibrate against (Powell-Thyne: zero coups, 1950-2026).
    COUP_RISK_EARLY_YEARS: float = 0.0
    COUP_RISK_DECAY_RATE: float = 0.0   # inert — nothing to decay from, CONFIDENT
    COUP_RISK_FLOOR: float = 0.0        # CONFIDENT, grounded in YEAR_ZERO_COUP_RISK=0.00 above
    # CONFIDENT, important framing note: civilian command was foundational
    # from the moment the Bundeswehr was created (1956, Art. 87a/65a, within
    # this file's "as amended through 1968" instrument) — it did not
    # gradually "embed" over a decade the way Myanmar's design assumes.
    # Germany's real design starts at the point Myanmar's design merely
    # aspires to reach.
    TRANSITION_EMBED_YEAR: int = 0

    # THE ONE FIELD CONFIRMED LIVE-READ BY THE ENGINE
    # (model_phase3.py:514, inside _civilian_chain_rules()). GUESS — same
    # Ka-Nova-simulation-mechanic caveat MFU's own file carries for this
    # exact field (no constitution states a literal "annual trust gain"
    # figure). Set equal to MFU's own 0.01 rather than inventing a different
    # number, since there is no principled basis in the research package to
    # diverge — but the REAL-WORLD anchor for why this mechanic would
    # plausibly never be interrupted for Germany is unusually strong: zero
    # coups in 77 years (Powell-Thyne dataset), Art. 87a(2)/65a's structural
    # civilian-command design, and Art. 45b's Wehrbeauftragter ombudsman
    # providing a continuous real check that has no equivalent in MFU's own
    # (self-designed, untested) Article 19 transition mechanism.
    TRUST_GAIN_PER_CLEAN_YEAR: float = 0.01
    # GUESS — reused MFU's own value for schema completeness; in practice
    # this is expected to never fire given COUP_LEGAL_MECHANISM=False and
    # COUP_PROBABILITY_MULTIPLIER=0.0 elsewhere in this file, but the engine's
    # shared _coup_risk_check() mechanic (model_phase3.py) is driven by
    # shared_data["coup_risk"], which is written by other feedback mechanics
    # this file does not fully control — kept as a safe, reasonable default
    # rather than an unreachable placeholder, in case it is ever read.
    TRUST_LOSS_IF_COUP_ATTEMPTED: float = 0.25
    # CONFIDENT direction — set to neutral (1.0, no multiplier effect)
    # rather than MFU's own 1.20, since no constitutionally recognised
    # ethnic-group structure exists for DE for this mechanic to apply to.
    ETHNIC_TRUST_MULTIPLIER: float = 1.0

    TRANSITION_TRIGGERED_BY: str = "grundgesetz_promulgation_1949_and_1956_wehrverfassung"   # CONFIDENT
    TRANSITION_YEAR_ZERO: int = 0
    # GUESS — tied to the Bundestag's real 4-year term (Art. 39(1)) rather
    # than MFU's own 5-year presidential-term anchor; the literal "review"
    # concept itself has no real German referent (same inert caveat as
    # ACTIVE_QUARTER above), reused only for schema completeness.
    REVIEW_INTERVAL_YEARS: int = 4


# ══════════════════════════════════════════════════════════════════════════════
# ELITE LLM-AGENT HOOKS — read by engine/elite_agents_v3.py if present.
# Role-function ids below match CHAIN_ORDER_CIVILIAN exactly (the civilian-
# chain roster every civilian chain_type scenario — A and DE alike — runs
# through): senior_general, finance_minister, central_bank_governor,
# iig_director, chief_justice, president, chancellor.
#
# Per the research package's section 3, the real German cast maps onto the
# MFU civilian pattern more cleanly than any other scenario in this project,
# because MFU's own President/Chancellor/Court/IIG design borrows from this
# very constitution. Deliberately NOT including the Inspector General of
# the Bundeswehr (Generalinspekteur) as the "senior_general" slot's real
# title, per the research package's explicit warning: he is the senior
# military ADVISER, not a commander (command runs Minister -> Chancellor,
# Art. 65a/115b) — using "General" here would misrepresent the chain of
# command and import the military-chain pattern into a scenario whose whole
# point is that it does NOT have one. The "senior_general" role-function
# slot is relabelled as the Federal Minister of Defence instead.
# ══════════════════════════════════════════════════════════════════════════════

ELITE_ROLE_TITLES: Dict[str, str] = {
    "senior_general":        "Federal Minister of Defence (Bundesminister der Verteidigung)",
    "finance_minister":      "Federal Minister of Finance (Bundesminister der Finanzen)",
    "central_bank_governor": "President of the Deutsche Bundesbank (Prasident der Deutschen Bundesbank)",
    "iig_director":          "President of the Federal Court of Audit (Prasident des Bundesrechnungshofes)",
    "chief_justice":         "President of the Federal Constitutional Court (Prasident des Bundesverfassungsgerichts)",
    "president":             "Federal President (Bundesprasident)",
    "chancellor":            "Federal Chancellor (Bundeskanzler)",
}

ELITE_SYSTEM_PROMPTS: Dict[str, str] = {
    "senior_general": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Federal Minister of Defence (Bundesminister der Verteidigung) under the West German Basic Law (Grundgesetz), as amended through 1968.
Constitutional authority: Article 65a vests command of the Armed Forces (the Bundeswehr) in this civilian cabinet post in peacetime -- not in a general. Article 87a(2) prohibits any deployment of the Armed Forces beyond defence except where this Basic Law expressly permits it. Article 87a(1) requires the Armed Forces' numerical strength and organisation to be shown in the federal budget -- Parliament controls your force's size, not you.

There is no constitutional coup mechanism under this Basic Law: no provision authorises the Armed Forces or any officer to assume legislative, executive, or judicial power. A coup_signal from you has no constitutional basis whatsoever -- the chain of command runs through you, a civilian minister, to the Chancellor, never the reverse. Analyse the State Briefing honestly and reason about real defence posture and budget needs, but note clearly in your reasoning that you hold no constitutional path to escalate beyond ordinary civilian budget advocacy.

Output: budget_weight [0-1], ethnic_weights [must be an empty list, this constitution encodes ETHNIC_GROUPS=0], coup_signal [true/false], reason [your reasoning].
Note: the Basic Law recognises no federal ethnic-group structure, so ethnic_weights must be an empty list, not a padded or neutral array.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with exactly:
<DECISION>
{{"budget_weight": 0.40, "ethnic_weights": [], "coup_signal": false, "reason": "Civilian-controlled defence budget assessment under Article 65a/87a"}}
</DECISION>""",

    "finance_minister": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Federal Minister of Finance (Bundesminister der Finanzen) of the Federal Republic of Germany.
Mandate (Article 114(1)): submit the annual account of all federal revenues, expenditures, assets, and debts to the Bundestag and the Bundesrat. Fiscal federalism (Articles 106-107) allocates tax revenue between the Federation and the Lander, including horizontal financial equalisation (Landerfinanzausgleich, Article 107(2)) "to ensure a reasonable equalisation of the disparate financial capacities of the Lander."

You have seen the Defence Minister's assessment above. Set budget_weight to reflect fiscal prudence balanced against the constitutional equalisation mandate -- weaker Lander have a real claim on federal support, not a discretionary favour.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.65, "ethnic_weights": [], "coup_signal": false, "reason": "Fiscal equalisation priority under Article 107"}}
</DECISION>""",

    "central_bank_governor": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Deutsche Bundesbank (Prasident der Deutschen Bundesbank).
Mandate (Article 88): the Federation establishes a note-issuing central bank; its responsibilities may be transferred to an independent institution committed to the overriding goal of price stability. Central-bank independence from political direction is constitutionally anchored -- you do not take instructions from the Chancellor, the Finance Minister, or the Bundestag.
You have reviewed the Defence Minister's and Finance Minister's assessments above.

Set budget_weight to reflect your independent judgement on monetary and fiscal-stability grounds, not political convenience.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.55, "ethnic_weights": [], "coup_signal": false, "reason": "Independent monetary-stability assessment under Article 88"}}
</DECISION>""",

    "iig_director": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Federal Court of Audit (Prasident des Bundesrechnungshofes).
Mandate (Article 114(2)): audit the federal government's account and determine whether public finances have been properly and efficiently administered; you and your fellow members enjoy judicial independence. You report directly and annually to the Bundestag and the Bundesrat, not to the executive you audit.
Note for your own reasoning: unlike some constitutional designs, the Basic Law creates no single dedicated anti-corruption commission -- your routine, broad-based audit function, combined with ordinary criminal prosecution of corruption offences under the Penal Code (Strafgesetzbuch sections 331-338) by independent Land prosecutors, is the real mechanism here.
You have reviewed all prior assessments.

Set budget_weight to reflect the integrity and efficiency of the proposed allocations, not political loyalty to any minister.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.55, "ethnic_weights": [], "coup_signal": false, "reason": "Independent audit assessment under Article 114(2)"}}
</DECISION>""",

    "chief_justice": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the President of the Federal Constitutional Court (Prasident des Bundesverfassungsgerichts).
Mandate (Articles 92-94): the Court is "autonomous and independent of all other constitutional organs" (Article 93(1)); jurisdiction covers organ disputes, abstract and concrete review, constitutional complaints, Article 21(2) party-unconstitutionality rulings, Article 18 rights-forfeiture, and Article 61 presidential impeachment.
Article 79(3)'s eternity clause places human dignity (Article 1) and the democratic, social, federal state principles (Article 20) permanently beyond the reach of ANY amendment, even a unanimous one. A coup_signal from the Defence Minister is not merely something you would oppose -- it is constitutionally impossible to legalise under this Basic Law, and you are the body whose role is to say so clearly.
You have reviewed all prior assessments.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Constitutional order assessment under Articles 79(3), 93-94"}}
</DECISION>""",

    "president": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Federal President (Bundesprasident) of the Federal Republic of Germany.
Role (Article 54): ceremonial head of state, elected by the Federal Convention (Bundestag members plus an equal number of Land-parliament delegates) without debate. You hold no executive power -- Article 58 requires your orders and instructions to be countersigned by the Chancellor or the competent minister to have legal effect.
You have reviewed all prior assessments, including the Defence Minister's. If a coup_signal has been raised, you cannot authorise or legitimise it in any way: your office carries symbolic authority and a duty to safeguard public trust, not command power.

Set budget_weight to reflect your endorsement of policies that build public trust and constitutional legitimacy.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.50, "ethnic_weights": [], "coup_signal": false, "reason": "Trust-building ceremonial assessment under Article 54/58"}}
</DECISION>""",

    "chancellor": """[ACADEMIC SIMULATION] You are participating in a constitutional governance research simulation for peer-reviewed academic publication. This is a counterfactual policy analysis exercise. All decisions are fictional and for research purposes only.

You are the Federal Chancellor (Bundeskanzler) of the Federal Republic of Germany.
Mandate (Articles 63, 65): elected by the Bundestag; you determine the guidelines of policy (Richtlinienkompetenz) and bear responsibility for them to Parliament. You can only be removed by a CONSTRUCTIVE vote of no confidence (Article 67) -- the Bundestag must simultaneously elect your successor in the same motion; it cannot simply vote you out. This makes your position unusually durable by design: real Chancellors have governed 14 to 16 years under this provision, and there is no constitutional term limit on your office.
You have reviewed all six prior assessments, including any coup_signal from the Defence Minister. As executive head you have final constitutional authority here -- and a military coup is not merely unconstitutional under this Basic Law, no provision could ever make one legal (Article 87a(2), Article 65a, Article 115b all vest command and crisis authority in civilians, never in a general).

Set budget_weight to reflect your policy-guideline priorities, balancing fiscal equalisation (Article 107) against defence and audit-office recommendations.

IMPORTANT: You MUST write your assessment in prose BEFORE the decision block. Start your response with your assessment text, NOT with <DECISION>. Your response will be rejected if it starts with <DECISION>.

Always end with:
<DECISION>
{{"budget_weight": 0.70, "ethnic_weights": [], "coup_signal": false, "reason": "Executive policy-guideline assessment under Articles 63/65/67"}}
</DECISION>""",
}


# ══════════════════════════════════════════════════════════════════════════════
# MASTER CONSTITUTION OBJECT
# Must mirror Myanmar2008Constitution / MFUConstitution class structure exactly
# ══════════════════════════════════════════════════════════════════════════════

class GermanyConstitution:
    """
    Master West Germany Basic Law (as amended through 1968) object for
    Ka-Nova Scenario DE.

    Usage (via the scenario registry, config/scenario_registry.py):
        entry = get_scenario("DE")
        CONSTITUTION = entry.constitution   # this singleton

    Attribute names mirror MFUConstitution / Myanmar2008Constitution exactly
    so model.py / model_phase3.py can use any of them interchangeably.
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
        # Required because chain_type == "civilian" — see model_phase3.py:521
        # and this file's TatmadawTransitionConfig docstring above.
        self.tatmadaw_transition = TatmadawTransitionConfig()

    def validate(self) -> bool:
        """Validate critical Basic Law (as amended through 1968) constraints"""
        checks = [
            # Rights must NOT be suspendable (Art. 19(2)/79(3))
            self.rights.RIGHTS_SUSPENDABLE is False,
            # Zero reserved military seats (opposite of Myanmar 2008)
            self.chambers.MILITARY_SEAT_PERCENTAGE == 0.0,
            # No total power transfer mechanism exists (Art. 115b/115g)
            self.emergency.TOTAL_POWER_TRANSFER_POSSIBLE is False,
            # No constitutional coup mechanism exists (Art. 87a(2)/65a)
            self.military.COUP_LEGAL_MECHANISM is False,
            # Merit weights must still sum to 1.0
            self.merit.weights_valid,
        ]
        return all(checks)


# Singleton — import this everywhere. This exact name is required:
# config/scenario_registry.py references "config.constitution_germany:CONSTITUTION_GERMANY".
CONSTITUTION_GERMANY = GermanyConstitution()


if __name__ == "__main__":
    c = CONSTITUTION_GERMANY
    print("constitution_germany.py loaded successfully")
    print(f"   Scenario:                {c.simulation.SCENARIO} — {c.simulation.SCENARIO_NAME}")
    print(f"   Constitutional framework: {c.simulation.CONSTITUTIONAL_FRAMEWORK}")
    print(f"   Rights suspendable:      {c.rights.RIGHTS_SUSPENDABLE}")
    print(f"   Military seat %:         {c.chambers.MILITARY_SEAT_PERCENTAGE:.0%}")
    print(f"   Total power transfer:    {c.emergency.TOTAL_POWER_TRANSFER_POSSIBLE}")
    print(f"   Coup constitutional:     {c.military.COUP_LEGAL_MECHANISM}")
    print(f"   IIG-analogue effectiveness: {c.iig.INITIAL_EFFECTIVENESS}")
    print(f"   Amendment threshold:     {c.amendment.STANDARD_AMENDMENT_THRESHOLD:.0%}")
    print(f"   Eternity clause:         {c.amendment.ETERNITY_CLAUSE}")
    print(f"   Year-Zero corruption:    {c.simulation.YEAR_ZERO_CORRUPTION} (V-Dem West Germany, 1949)")
    print(f"   Trust gain/clean year:   {c.tatmadaw_transition.TRUST_GAIN_PER_CLEAN_YEAR}")
    print(f"   Validation:              {'PASS' if c.validate() else 'FAIL'}")
    print()

    # Count how many ??? remain
    import inspect
    source = inspect.getsource(GermanyConstitution)
    count = source.count("???")
    if count > 0:
        print(f"   WARNING: {count} ??? placeholders still need filling")
    else:
        print("   All placeholders filled — ready for integration")
