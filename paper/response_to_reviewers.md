# Response to Reviewers

> **Conversion note (delete before upload).** This file is the content source for the
> IEEE Access "Response to Reviewers" template
> (`IEEE-Access-Response-to-Reviewers-template-6.26.23.docx`). The header block, the
> covering paragraph and the three-part per-concern structure below reproduce that
> template exactly; the template ships with three concerns per reviewer and the pattern
> is extended to eight and four. Upload under **Author's Response Files**.
>
> Markers used in this draft:
> `[PENDING CAMPAIGN: ...]` a quantity the paid campaign has not yet produced.
> `[PENDING DELIVERABLE: ...]` an artifact that does not yet exist.
> `[PENDING DECISION: ...]` a call reserved for K.H. or the corresponding author.
> No marker is a placeholder for prose; every response below is written in full.

---

Original Manuscript ID: Access-2026-37966

Original Article Title: "A Hybrid Generative Agent-Based Model with Runtime
Constitutional Validation for Comparative Governance Simulation"

To: IEEE Access Editor

Re: Response to reviewers

Dear Editor,

Thank you for allowing a resubmission of our manuscript, with an opportunity to address
the reviewers' comments.

We are uploading (a) our point-by-point response to the comments (below) (response to
reviewers, under "Author's Response Files"), (b) an updated manuscript with yellow
highlighting indicating changes (as "Highlighted PDF"), and (c) a clean updated
manuscript without highlights ("Main Manuscript").

Best regards,

Kaung Htet et al.

---

## Preamble: what changed between the two versions, stated first

Every quantitative value in this manuscript has changed, and the reviewers will see that
immediately. We state the reason before the point-by-point response, because it is an
audit result rather than an accident, and because a reader who reconstructs it unaided
would reasonably reach a worse conclusion than the one the evidence supports.

Between the initial submission and this version we subjected our own instrument to an
adversarial audit, conducted against our own published claims rather than against our
intentions. The audit found **ten defects in the simulation and measurement pipeline**.
Two of them are present in the dataset underlying the submitted manuscript's own
enforcement table: the structured elite decision was never written to the decision log,
so every enforcement count in the submitted paper had to be recovered by regular
expression over free-text reasoning; and the decision parser silently substituted a
role default whenever it could not read the model's output through one specific
delimiter, a substitution that was schema-valid and that the validator therefore
recorded as a pass. The measured substitution rate on the published campaign is 10.3
percent of all Scenario A decisions and 30.0 percent of decisions by the single role
with explicit latitude to signal a coup. A code comment asserting that the coup signal
was never injected by the implementation was therefore false for thousands of published
decisions.

A third item is a retraction of our own correction. Our first reconciliation of the
submitted manuscript's enforcement table concluded that the unreconciled 394-signal gap
was a counting artifact that shrank to 16 signals under a stricter count, implying an
interception rate of 99.62 percent. **That correction was wrong and is withdrawn in
full.** Its "strict" pattern required a particular literal delimiter, and the rows
lacking that delimiter are precisely the rows on which the parser also failed, so the
strict count was a count of what a broken parser accepted and it made the instrument's
own defect invisible by excluding every decision the defect destroyed. Re-derived with a
working parser, **the originally published figures were correct**: 4,570 emitted coup
signals under Scenario A, reproducing four of the five published per-role figures to the
unit, and 6,009 under Scenario C. The honest headline is therefore **4,176 interceptions
against 4,570 model-decided signals, an interception rate of 91.4 percent**, and the
394-signal gap is real: it is the number of coup signals our own instrument deleted
before its own enforcement layer could evaluate them. We also withdraw the mechanism we
had proposed for that residual, which inspection of the call order shows to be
impossible. The submitted manuscript's statement that interception was complete with
zero uncorrected signals is withdrawn and is not replaced by a second completeness
claim.

We report the retraction rather than overwriting it, because the retraction is itself
part of the finding. An instrument that silently deleted a measurable fraction of the
behaviour it exists to measure, discovered by auditing its own counts, and then
discovered a second time when the first audit was itself mistaken, is a more useful
contribution to the validation literature than a clean number would have been. Section
VI (Instrument Validation) reports all ten defects in a table, each with how it was
found and the specific reviewer-facing quantity it would have corrupted, and Section
VII-A reports the reconciliation and the retraction.

Four further consequences follow, and all four narrow the paper.

1. **No standardised effect size appears anywhere in the resubmission.** The submitted
   manuscript reported four and described them as very large. Each of the four is now
   accounted for by a modelling constant that we name, three of them by our own global
   sensitivity analysis and the fourth by reading our own source. This is a direct answer
   in the negative to Reviewer 1's second concern.
2. **The comparative-outcomes claim is withdrawn, and the title changes.** The paper is
   now a methods and instrument paper with a measured negative result. The submitted
   title, which names comparative governance simulation, no longer describes it.
   [PENDING DECISION: final title. The working title in the manuscript source is
   "Encoding Constitutions as Runtime Constraints in a Generative Agent-Based Model:
   Article-Level Enforcement, a Mechanism Audit, and an Instrument Validation".]
3. **The designed constitution is no longer part of the experimental design.** The
   self-designed Meritocratic Federal Union encoding and the second designed variant have
   been removed from the roster. The differential-constraint result is now demonstrated on
   two real, historically enacted constitutions, so the central claim does not rest on a
   constitution written by one of the authors. The parameter schema into which all
   encodings are written remains that constitution's own vocabulary, which is a
   measurement limitation we quantify in Section V-G rather than assert away.
4. **One of the reviewers' concerns cannot be fully answered**, and we say so in the
   relevant entry rather than at the end. Reviewer 2's first concern asks how the approach
   performs on more similar constitutions. We built that test and the result is negative:
   the model does not separate structurally similar guardianship constitutions. We report
   the measurement, the specific line of code responsible, and why the obvious remedy is
   circular.

Where a quantity in this response depends on the re-run that these fixes made necessary,
it is marked `[PENDING CAMPAIGN]`. No number in this response or in the manuscript is
carried forward from the superseded dataset as if it were current, and no number is
back-filled or estimated.

---

## Reviewer#1, Concern # 1 (please list here):

"Additional scenarios and/or systematic parameter sensitivity analysis are needed to
demonstrate that the reported divergence is not primarily determined by the selected
parameterization."

**Author response:**

We did both of the things this concern offers as alternatives, and the result does not
support the proposition we were asked to demonstrate. We therefore report which parts of
the divergence are parameterisation-driven and which are not, rather than asserting a
negative we cannot evidence.

On additional scenarios: five further constitutions are now encoded at article level from
primary legal texts, giving six live encodings in total (South Korea 1987, Thailand 2017,
Pakistan under the 1973 Constitution as amended by the Eighth Amendment, Chile 1980 as
operative in its elected-Congress period, the German Basic Law, and the 2008 Constitution
of Myanmar). Three of these were selected because they are structurally similar to one
another, which is the discriminating test, and the outcome of that test is reported under
Reviewer 2's first concern.

On systematic sensitivity analysis: four Sobol analyses have been completed, each at 960
model runs over a thirteen-parameter space at full citizen scale, implemented with SALib
following Saltelli et al. The analyses establish that three of the four previously
reported separations are governed by a single modelling constant each. A fourth
separation, corruption, is produced by a structural branch on chain type rather than by
any parameter, and we note explicitly that a sensitivity analysis over parameters cannot
detect it; that one was found by reading the source.

We also disclose the scope limit of the sensitivity analysis rather than presenting it as
broader than it is. The sampling bounds were authored around the designed constitution's
own parameter values. Checked programmatically against every encoding's live
configuration, those bounds fail to bracket the real configuration for a majority of
parameters on several encodings, and a spot check found 61 percent of
non-designed-constitution defaults outside the sampled region. A cross-scenario
sensitivity table under one shared bound set would therefore sample regions that do not
contain the scenarios' actual configurations, and we do not publish one. The scope is now
enforced at run time rather than stated in a documentation note. We additionally report
that at the sample size used, the confidence interval on the dominant index is wide
relative to the estimate, and that negative first-order estimates are estimator noise
reported as not distinguishable from zero.

**Author action:**

We updated the manuscript by adding Section V (Mechanism Audit), which reports with file
and line which published quantities are driven by constitutional content and which by
engine-level constants; by adding Section V-F (Global Sensitivity Analysis and Its Scope)
with the three cautions above stated as numbered items; by adding Table 1 in Section III-B
documenting the six encodings and their year-zero calibration with the instrument and
observation year for each; by adding Section V-C with Table 3, which names the governing
constant for each of the four previously reported separations; and by promoting the
sensitivity scope statement from prose into a run-time guard described in Section V-F.
[PENDING CAMPAIGN: the two remaining sensitivity runs, a restricted-parameter run for
trust on the Myanmar encoding and a `coup_risk` run, both of which are free to execute
and are required before the `coup_risk` disclosure in Section III-B can be quantified.]

---

## Reviewer#1, Concern # 2 (please list here):

"...demonstrate that these results are robust and are not mechanically induced by
thresholds, parameter bounds, or deterministic relationships embedded in the model."

**Author response:**

**We investigated all four separations and the answer is in the negative for all four.**
Each is accounted for by a threshold, a bound or a deterministic relationship embedded in
the model, in the precise terms of this concern. We report no standardised effect size
anywhere in the resubmission.

The four accounts are as follows.

*Public trust.* The reported value under the guardianship encoding is a clamp,
`rights.FEAR_COMPLIANCE_TRUST_FLOOR = 0.10`, applied on the military chain at two
independent sites in the feedback layer, both carrying comments describing it as a
fear-compliance floor. Sobol total-order index 1.00 for that constant on that scenario.
The reported variance across runs is exactly zero, which is a property of a clamp and not
of a trajectory.

*Coup probability.* Constant by construction. Sobol indices are undefined because the
output has zero variance across all 960 samples of the full parameter space. The value is
set by a hardcoded civilian-chain decrement of 0.05 per signal, not by any parameter,
constitutional or otherwise. We report the metric as invariant to the entire
thirteen-parameter space and we report the zero-variance outcome as a finding rather than
as a failed analysis.

*Stability.* Sobol first-order index 0.9908 for `rights.STABILITY_RIGHTS_BONUS = 0.20`,
with all twelve other parameters at total order at or below 0.008.

*Corruption.* This is the one the sensitivity analysis could not have found, and it is the
one that matters most, because corruption carried the submitted manuscript's headline
divergence. State corruption is written at exactly two sites in the repository, both
inside a branch on chain type: the civilian arm reduces corruption in proportion to
anti-corruption effectiveness, and **the military arm reads no constitutional field at
all** and accumulates at a fixed drift. Measured rather than inferred, the three
guardianship encodings' corruption series are parallel straight lines of slope exactly
0.0100 per year, differing only in their year-zero intercept. The submitted manuscript's
own stated mechanism for that divergence, that regime-protective oversight caps
anti-corruption effectiveness so corruption accumulates, is therefore not the implemented
mechanism, because the military branch never reads anti-corruption effectiveness. **We
withdraw that narrative.**

Two reporting consequences follow, and both are now enforced throughout the manuscript.
First, where a separation is complete and produced by a constant, we report it as
complete, name the constant, and treat it as a check that the model behaves as specified
rather than as a discovery. A clamp holding trust at exactly its floor with zero variance
is evidence that the clamp is implemented; it is not evidence about constitutions. Second,
horizon-matched comparison is mandatory. The submitted manuscript compared corruption at
the end of the horizon for a scenario that completes the horizon against a scenario that
terminates in its second decade. We report the comparison at the year nearest the
terminating scenario's mean final year, and we additionally report that the terminating
scenario reaches the variable's upper clip before its own mean termination year, so that
the comparison is compressed from above by a bound rather than by a mechanism.

We note the five relevant coefficients inside the chain-type branch have been promoted
from bare literals to per-constitution fields at identical values, verified byte-identical
across all encodings at matched seeds. That makes the branch named, inspectable,
disclosable and reachable by sensitivity analysis. It is a precondition for honest
reporting and we are explicit that it is not a result and does not make similar
constitutions separate.

**Author action:**

We updated the manuscript by adding Section V-C (Separation by Construction: The Four
Governing Constants) and Table 3, which gives the metric, the governing constant and the
evidence for each of the four; by deleting every standardised effect size and the phrase
describing effect sizes as very large from the abstract, Section III-G (Outcome Metrics)
and the results; by stating in Section III-G that no standardised effect size is reported
anywhere in the paper and why; by adding equation (3) and Section V-A (What the Engine
Branches On), which gives the chain-type corruption update explicitly and names the method
in which it occurs; by withdrawing the regime-protective-oversight mechanism narrative in
Section V-C; and by adding Section V-D (Boundary-Pinned Metrics), which marks the
bound-arrival year on every series that reaches a bound.
[PENDING CAMPAIGN: the horizon-matched corruption comparison at the publication sample
size, with the clip year stated for each series.]

---

## Reviewer#1, Concern # 3 (please list here):

"The scientific role of the LLM component should be clarified. The manuscript reports
statistically indistinguishable aggregate outcomes when the LLM elite layer is replaced by
a deterministic rule-based mechanism. This is an important result, but it also raises the
question of whether the generative component materially contributes to the simulation
outcomes or primarily serves as a decision-provenance and runtime-validation mechanism."

**Author response:**

We read this as a disjunctive question rather than as an endorsement of either horn, and
we are explicit in the manuscript that the reviewer posed the question and did not answer
it. We take the second horn and we evidence it.

First, we accept the premise and we strengthen it. The generative layer does not determine
aggregate outcomes, and the invariance is not a discovery: it is entailed by the coupling
design, and we now derive it in the methodology rather than reporting it in the results.
The layer's total influence on the simulation is three quantities: a single scalar bounded
to [0, 0.15] and consumed as a multiplicative term on a transfer that is itself a fraction
of income; an ethnic-weight vector explicitly normalised to mean one before consumption,
so its mean is destroyed by construction and only relative dispersion survives; and a
boolean that a civilian chain suppresses, with a second lock at the aggregation stage in
addition to the constitutional layer. A bounded scalar, a mean-normalised vector and a
suppressed boolean cannot move aggregate indicators far. Reporting that as a negative
result about generative agents in governance simulation generally would be an over-claim,
and the submitted manuscript came closer to that than it should have. It is a property of
this model's coupling and we credit the derivation to our own audit.

Second, we state what the layer does contribute, in descending order of defensibility.
It is the only substrate that generates the phenomenon the validator governs: a
deterministic rule-based elite does not emit a coup signal under a civilian-supremacy
encoding, so there is no rule-based counterpart to the enforcement record, and the
enforcement record is the object of study. It supplies interpretable decision provenance:
the audit trail records, per decision, the conditions at decision time, the structured
decision itself, the validation outcome at each of the four layers, and, on interception,
the rule cited and the re-prompt that followed. And it is a control condition: because the
rule-based path produces materially identical aggregate outcomes, a difference between
scenarios cannot be attributed to language-model idiosyncrasy, and within the simulation it
must be attributed to the configuration, after which Section V establishes how much of
that configuration is constitutional content and how much is engine constant. A
single-substrate design could not support that inference at all.

Third, we state the cost of this position rather than letting a reviewer state it for us.
If the generative component does not determine outcomes, the sharper follow-up is why it
is a contribution. Our answer is that the enforcement record is the contribution, the
generative layer is its necessary substrate, and a validator with nothing to validate is
not a validator. The elite-to-citizen coupling is weak by construction, so the layer's
influence on indicators is small by design, and strengthening that pathway is the priority
for the next iteration of the engine. That is a disclosed design choice, not a defended
result.

Fourth, and directly relevant here, the audit found that before this revision the prompts
for the five enacted encodings instructed the model that a coup signal had no
constitutional basis and should not be set, while the two original encodings carried no
such instruction. Any earlier statement about what the generative layer contributed under
those five encodings was therefore partly a statement about our own prompts. Those
instructions have been removed, and what those encodings emit under symmetric prompts is
now a measurement rather than an instruction.

**Author action:**

We updated the manuscript by rewriting and expanding the LLM-role subsection, now Section
VIII-A (The Role of the LLM Layer: A Control Condition and a Provenance Mechanism), into
four explicitly labelled parts: accepting and deriving the premise, what the layer does
contribute, the honest cost of the position, and the prompt-symmetry disclosure; by moving
the coupling bound into the methodology as equation (1) in Section III-D with a sentence
stating that it is placed there because it is the reason the invariance holds and that is
better stated in advance than discovered; by adding Section III-D-1 (Prompt Symmetry)
documenting exactly which instructions were removed and which factual constitutional
descriptions were retained; and by stating in Section VIII-A that the reviewer's point is
a question and is not cited as an endorsement of our answer.

---

## Reviewer#1, Concern # 4 (please list here):

"These should be investigated more thoroughly rather than primarily deferred to future
work. In particular, any discrepancy between theoretically expected parameter limits and
simulated outcomes should be explained."

**Author response:**

Both discrepancies of this class that we are aware of have been root-caused to a named
site in the source, fixed, and reported with their mechanism rather than deferred.

The discrepancy the reviewers identified is the anti-corruption body effectiveness
reported under the 2008 Myanmar encoding, which exceeded the near-inert ceiling that
encoding's own parameters imply. The cause is in the institutional sub-model's annual
operations routine, which advanced an effectiveness value on a path that did not consult
the active encoding's own ceiling. It is fixed and the mechanism is stated in the
manuscript with the file and method named.

The audit found a second discrepancy of exactly this class, which the reviewers could not
have seen, and we report it because the method's own logic requires us to. The
civilian-chain effectiveness floor was applied at the end of the state-update method,
after the per-state loop had already consumed the effectiveness value, while the
institutional sub-model overwrites that value earlier in the year with its real computed
figure, which is zero before any investigation resolves. Every encoding except the
designed one carries its own encoded effectiveness floor, which props the value back up;
the designed one carries none. Measured at a fixed seed before the fix, the designed
scenario read an effectiveness of exactly zero for its first five simulated years, applied
no corruption reduction at all, and its corruption index was frozen at 0.8976 for exactly
those five years. The published effectiveness column and the number the corruption
mechanism consumed were different quantities. The fix is a real behavioural change, not a
refactor, and it moves the designed scenario's outcome in its own favour, so we flag that
direction explicitly so a reader can weigh it.

**Author action:**

We updated the manuscript by reporting the anti-corruption effectiveness discrepancy and
its cause in Section V (Mechanism Audit) with the responsible routine named; by adding
Section V-B (The Ordering Defect in the Effectiveness Floor) reporting the second
discrepancy, its measured effect, and the explicit flag that its correction favours the
previously self-designed scenario; and by listing it as defect D8 in Table 2 of Section VI
with how it was found and what it would have corrupted.
[PENDING CAMPAIGN: the recomputed effectiveness and corruption trajectories under the
corrected ordering at the publication sample size. The provisional single-seed figure
measured during the fix is not a publication quantity and is not printed.]

---

## Reviewer#1, Concern # 5 (please list here):

"Historical backtesting, even for a restricted subset of model outputs, would considerably
strengthen the evidence."

**Author response:**

We take the literal wording seriously: a restricted subset of model **outputs**, not a
restricted subset of cases. Our own internal record had drifted into reading it as
licensing the declination of individual countries, and we have corrected that reading. The
concern licenses backtesting fewer metrics; it does not license dropping cases. We
therefore select a narrow output set and report it for **every** enacted encoding,
including where it fails, rather than reporting only the cases that match.

This is answered in part and scoped as a limitation in part, and we distinguish the two.

What we can report: a backtest table covering all five enacted encodings on the selected
output set, with the simulated value, the real-world observation, the source and an
explicit verdict per row including failures. On the provisional free rule-based survey
taken before several of the fixes in Section VI landed, one case matches its real duration
closely, one survives the full horizon as it did historically, one makes a prediction
beyond its real observation window rather than contradicting it, and one over-survives its
real duration substantially. We do not print any of those four statements as results until
the campaign confirms them at the publication sample size, and in particular we no longer
describe any case as the strongest match: the case that previously carried that description
no longer matches.
[PENDING CAMPAIGN: the full backtest table at the publication sample size, and the
per-row verdicts.]

What we scope as a limitation: the collapse mechanism is deliberately symmetric across
encodings, with an identical threshold and an identical success roll. That symmetry
preserves the experimental control and simultaneously limits what the mechanism can
represent, so **no survival prediction is claimed for any polity** and the symmetry is
reported as a scope limit of the mechanism rather than as a result. We also report that
corruption, the output most naturally backtested, is pinned at a boundary for three of the
encodings before the end of the period over which each is observed, so that any figure
plotting corruption across all encodings contains flat segments that carry no information
about the encodings. Every such figure now marks the bound-arrival year.

**Author action:**

We updated the manuscript by adding Section VII-D (Historical Backtesting on a Restricted
Subset of Outputs), which states the restricted-outputs reading explicitly and commits to
reporting the selected output set for all five enacted encodings including failures; by
adding the no-survival-prediction scope limit and the symmetric-collapse-mechanism
disclosure in the same subsection; by adding Section V-D (Boundary-Pinned Metrics); and by
correcting the manuscript and our internal record wherever the "restricted subset" wording
had been paraphrased as a subset of cases.

---

## Reviewer#1, Concern # 6 (please list here):

"Several figures are of insufficient quality for an IEEE journal and some graphical
elements appear highly stylized or synthetic... regenerated directly from the underlying
data/model as publication-quality vector or high-resolution graphics. Fonts, labels,
symbols, line weights, and overall graphical style should also be made consistent."

**Author response:**

We accept this without qualification. The four schematic figures (architecture, annual
sequence, elite chain, validation pipeline) are the likely referents of the comment about
stylized or synthetic graphical elements, and they are being redrawn as vector graphics in
a single consistent style covering fonts, labels, symbols and line weights. Every data
figure is regenerated directly from model output by scripts released with the
reproducibility package, so that the figure and the number in the text come from the same
artifact and a reader can re-run the generation.

**Author action:**

We updated the manuscript by replacing all figures.
[PENDING DELIVERABLE: the figures do not yet exist. Figures 1 to 4 are schematics and
require no campaign data; the data figures require the campaign. This entry must not be
submitted until the replacement figures are in the manuscript, and the "Author action"
sentence above must then be made specific, naming the vector format, the common style
specification and the generating scripts.]

---

## Reviewer#1, Concern # 7 (please list here):

"If generative-AI tools were used to create or substantially modify any figures or
graphical elements, this should be transparently disclosed."

**Author response:**

A dedicated disclosure section has been added. It distinguishes two uses that the submitted
manuscript did not separate. The first is generative AI inside the object of study: the
elite agent layer is a locally hosted Llama 3.2 3B model, and its role, configuration,
prompts and outputs are described in the methodology and the instrument-validation
sections and released in full. The second is generative-AI tooling used in preparing the
manuscript and its artifacts, which is disclosed per artifact class, naming the tool and
the extent of its use, with the authors taking full responsibility for all content.

**Author action:**

We updated the manuscript by adding Section X (Disclosure of Generative-AI Use), which
separates generative AI as the object of study from generative-AI tooling in manuscript
preparation and discloses the latter per artifact class.
[PENDING DECISION: the factual determination required for this section has not been made
by any author. For each of (a) the schematic figures, (b) the data figures, (c) manuscript
prose and (d) source code, the author who produced the artifact must confirm whether a
generative tool was used and to what extent. The reviewer asked about figures explicitly.
Any statement that is not confirmed must be removed rather than softened, and this entry
must not be submitted until the determination exists.]

---

## Reviewer#1, Concern # 8 (please list here):

"...including constitutional encodings, parameter values, random seeds, LLM configuration,
prompts, CVES rules, and statistical procedures."

**Author response:**

Each named item is addressed in a dedicated reproducibility section, including the two
places where the honest answer is a limitation.

*Constitutional encodings.* Released as readable source modules with per-field provenance
comments naming the instrument, the citation, the year and the entity, and with explicit
confidence tags. Between 35 and 50 percent of the implemented fields in each enacted
encoding are self-labelled as estimates, and we publish that ratio rather than suppress
it, because it is evidence for one of the paper's findings.

*Parameter values.* A provenance table covers every year-zero field for every encoding and
flags each field for which no retrievable observation exists. Two disclosures are made
against our own interest. Myanmar's year-zero corruption was corrected from 0.72 to 0.878:
the 0.72 figure was present at the repository's initial commit labelled as a V-Dem
baseline, it is not a V-Dem value for any year, and it is in fact the inverted Transparency
International score of 28 of 100. And the year-zero coup risk of 0.25 is four to five times
Myanmar's historical base rate computed on the same convention used for every other
encoding. We did not quietly change it; we disclose it, publish the historical rate beside
it, and added `coup_risk` as a sampled parameter so that its contribution can be measured
rather than asserted. We also record that governance-index point estimates are re-estimated
at each release of their source, so the package ships the frozen data extract rather than a
download instruction, and that we did not retrofit a coincidental numerical match as a
citation: a brute-force search over roughly two thousand candidate transformations of a
governance panel hits any two-decimal target by chance, and hitting it is not provenance.

*Random seeds.* **We correct the submitted manuscript's statement that all runs are
seeded.** It was true of the simulation and false of the audit trail. The run identifier
was never written to any logged row, so the shipped logs of the original submission carry a
constant run identifier and cannot be partitioned by run. This is defect D1 and it is the
single defect most directly implicated in the reconciliation failure. It is fixed: the
identifier is threaded from the runner to every logged row, verified on all encodings, and
reconciliation on the re-run becomes a join on run, year and agent rather than a regular
expression over prose. We also report that determinism under the language-model path is
bounded rather than guaranteed, and that we deliberately do not enable parallel decoding,
because batched decode changes floating-point reduction order and would put per-seed
reproducibility at risk.

*LLM configuration.* The model, serving stack, context length, per-call parameters and
exact model digest are recorded in the run log of every campaign and reported in the
package.

*Prompts.* All role prompts across all encodings are released verbatim, and the
prompt-symmetry change is published as a diff so that a reader can see exactly which
instructions were removed and verify that every factual constitutional description was
retained.

*CVES rules.* The four layers, the three constitutional rules, the schema, the clamping
ranges and the re-prompt policy are released as source, and the **reachability** of each
rule is documented in the text rather than left to inspection. Of the three constitutional
rules, one is live, one is unreachable because no prompt, schema or parser produces the
field it tests, and one is structurally redundant because an upstream clip makes its
condition unsatisfiable. We label the third as structurally redundant rather than
engineering it to fire.

*Statistical procedures.* Tests, sample sizes and the sensitivity analysis configuration
are stated, with the scope restriction on the sensitivity analysis stated explicitly.

Two open reproducibility items are stated as limitations rather than claimed as resolved.
The container image installs its dependencies from an inline, unpinned list rather than
from the pinned dependency file, so the image's installed versions can drift from the
pinned set. And exact per-row reconciliation of the superseded dataset remains impossible
for the reason above, which is why the reconciliation in Section VII-A is reported as an
account of a superseded dataset rather than as the paper's enforcement record.

**Author action:**

We updated the manuscript by adding Section IX (Reproducibility) organised under the
reviewer's own seven headings plus audit trails and continuous integration; by correcting
the seeding claim in that section and stating both facts; by documenting per-rule
reachability of the constitutional layer in Section III-F; by adding the
calibration-provenance and frozen-data-extract statements; and by listing the container
image's unpinned dependency install as an explicit limitation in Section VIII-C.
[PENDING DELIVERABLE: the supplementary reproducibility package must be uploaded as a .zip
with the resubmission, not after acceptance, per the Resubmission Checklist. It must
contain the encodings, the frozen data extracts, the verbatim prompts and the prompt diff,
the validation rules, the seeds and the statistical procedures.]
[PENDING CAMPAIGN: the model digest, server version, context length and measured per-call
latency of the campaign pod, and the determinism check result from one run identifier
executed twice with the decision logs diffed ignoring timestamps.]

---

## Reviewer#2, Concern # 1 (please list here):

"...the current evaluation is based on only one very extreme constitution pair, so it is
still difficult to know how well the approach would work for more similar constitutions."

**Author response:**

**We cannot fully answer this concern, and we report the measured negative result rather
than a partial defence.** We built the test the concern asks for, and the approach as
implemented does not separate structurally similar constitutions.

Three independently sourced guardianship constitutions were encoded at article level
(Thailand 2017, Pakistan under the Eighth Amendment, and Chile 1980 as operative in its
elected-Congress period), chosen precisely because they are structurally similar to one
another and to the 2008 Myanmar encoding. Inside the engine the guardianship encodings
differ in their year-zero intercepts and in their encoded anti-corruption effectiveness
floors, and **their corruption trajectories are parallel straight lines of identical slope,
exactly 0.0100 per year, differing only in intercept.** The reason is specific and
reportable: the unchecked drift coefficient has no constitutional analogue in any of the
three texts, so it defaults to the same value for all three. We promoted it from a bare
literal to a per-constitution field, which makes the mechanism visible, named, disclosable
and reachable by sensitivity analysis. **It does not make the encodings separate, and we
state that explicitly so the promotion is not mistaken for a fix.**

**There is an obvious remedy and we considered it and rejected it.** One could source a
per-country drift rate from each country's own observed corruption series, for example its
own V-Dem corruption index trajectory. That would make the encodings separate, and it
would do so by fitting the model to the outcome the model then claims to reproduce. It is
circular, and a reviewer with repository access would find it. A closely related variant
was rejected for the same reason after inspection of our own provenance comments: driving
the military arm from each encoding's anti-corruption effectiveness floor looked
principled, but two of the three comparator magnitudes were themselves calibrated against
outcome measures, a control-of-corruption governance index and a corruption perceptions
score, and only one was derived from constitutional text. A non-circular version would
derive drift from encoded constitutional features, which is new modelling research rather
than a revision fix, and we list it as such.

We report the deeper cause as a property of the modelling approach rather than as an
implementation shortcoming, because it is measurable. The parameter schema into which all
encodings are written was derived from a designed constitution. That schema is 1.6 to 1.8
times larger than any real constitution's encoding. The anti-corruption institution makes
the problem concrete: it is the designed constitution's own invention, and the three real
analogues are not the same kind of institution at all. Thailand's National Anti-Corruption
Commission investigates and prosecutes after the fact; Chile's Contraloría exercises an ex
ante veto, preventing the act before it occurs; Pakistan under the encoded instrument has
no such body. **They differ in mechanism, not in magnitude.** Collapsing them into a single
effectiveness scalar discards exactly what distinguishes the constitutions, and the scalar
then has to be filled from outcome data because no textual quantity exists to read. Real
constitutions are partly characterised by the absence of the designed constitution's
inventions.

One genuine positive counter-example survives and we report it as the one place the
encoding work demonstrably functions inside the engine: on the military side, the
anti-corruption effectiveness term tracks Thailand's real encoded floor at roughly nine to
ten times the value produced for Myanmar and Pakistan. The same mechanism behaves correctly
when it is not sitting beside a competing chain-type hardcode.

The honest summary, which is what the manuscript now says, is that the approach
discriminates between structurally opposite constitutions and does not discriminate between
structurally similar ones, that we can name the line of code responsible, and that we can
say what it would take to change that.

**Author action:**

We updated the manuscript by adding Section V-H (The Structurally Similar Constitutions Do
Not Separate), which reports the negative result, the measured parallel-line finding, the
rejected remedy and the reason it is circular, and the one positive counter-example; by
adding Section V-G (Schema Fit, and Why the Comparator Magnitudes Cannot Drive Outcomes),
which reports the schema asymmetry, the estimate-labelled field ratio and the
mechanism-not-magnitude finding for the three real analogues; by listing the
non-separation as the first item in Section VIII-C (Limitations); by adding the
derive-drift-from-encoded-features item to Section XI-A (Future Work) as a prerequisite
rather than an extension; and by stating in Section II-F (Case Selection) that three
encodings were chosen because they are structurally similar and that the result of that
test is negative.

---

## Reviewer#2, Concern # 2 (please list here):

"...many manually chosen constitutional and feedback parameters drive the simulation."

**Author response:**

We agree, and we answered this by measuring it rather than by arguing about it. The result
concedes the concern with numbers.

The three feedback-layer constants that the submitted manuscript treated as fixed
modelling choices were promoted to constitutional fields at identical values and entered
into the global sensitivity analysis with lower bounds reaching zero, so that the analysis
could find them dominant if they were. It did. The fear-compliance trust floor reaches a
total-order index of 1.00 on the guardianship encoding; the stability rights bonus reaches
a first-order index of 0.9908, with the other twelve parameters at total order at or below
0.008; and the civilian-chain coup-signal damping produces an output with zero variance
across the entire parameter space, which makes the indices undefined and the metric
constant by construction. In other words, **the sensitivity analysis establishes that the
manually chosen feedback constants, not the constitutional parameters, govern three of the
four separations the submitted manuscript reported.** We report that as the finding.

Since then the audit extended the same treatment to five further coefficients in the
state-update method that were bare literals inside the chain-type branch, verified
byte-identical across all encodings at matched seeds, and added the year-zero coup risk as
a sampled parameter with bounds reaching below its historical base rate so that the
analysis can answer what the model does at the real rate.

Two caveats accompany this and are stated in the manuscript. The sensitivity analysis is
scoped to the designed constitution's parameter region, for the bracketing reason given
under Reviewer 1's first concern, so it is not a per-country sensitivity result. And the
feedback constants themselves are identical across all encodings, so there is no
per-country sensitivity in them to measure.

**Author action:**

We updated the manuscript by adding Section V-F (Global Sensitivity Analysis and Its
Scope) reporting all four completed analyses, their configuration and their three
cautions; by adding Table 3 in Section V-C, whose evidence column is the sensitivity
result for three of the four separations; by documenting in Section V-A the promotion of
the five state-update coefficients to per-constitution fields and the byte-identical
verification; by documenting the addition of `coup_risk` as a sampled parameter in Section
III-B alongside the disclosure of its value against the historical base rate; and by
stating the two caveats in Section V-F rather than in a footnote.

---

## Reviewer#2, Concern # 3 (please list here):

"...two metrics remain constant, and the reported IIG effectiveness under Scenario C does
not match the expected behavior of its parameter setting. These should be resolved before
publication."

**Author response:**

All three items are resolved, each with a named cause, and we distinguish full resolution
from partial resolution rather than reporting all three as closed.

*The composite progress score.* It was constant because no write path for it existed: it
was a missing feature, not a formula error. A real write path is implemented, and following
the audit the composite is now reported **decomposed term by term for every encoding and
never as a single headline number**, with a regression test asserting that the seven terms
sum to the composite and that each matches an independent recomputation. The decomposition
is also the clearest illustration in the paper of what we mean by a mechanism audit:
measured at full publication scale, three of the seven terms land at an identical maximal
value for every civilian-chain encoding regardless of which real constitution is active,
and those three carry 45 percent of total composite weight. Nearly half of the composite
success score is decided before any constitution is read. We neither re-weight the
composite, because any weights we chose would reintroduce the design-bias problem, nor
retire it, because it is one of the metrics this concern asked us to resolve rather than
remove.

*Ethnic harmony.* The metric is no longer constant, and the cause is named. This is a
**partial** resolution and we label it as such: the ethnicity-to-archetype assignment
matrix is still drawn from one country's census for all encodings, so the metric is live
but not comparable across countries. Consequently **no cross-country claim involving
ethnic harmony is made anywhere in the paper**, and the limitation is stated rather than
the metric quietly used. A separate correctness defect found in the same area is also
fixed and reported: the policy impact dictionary was built with only four of eight ethnic
groups, which made an affirmative vote arithmetically impossible for four of eight council
seats in every scenario and every year. It is now built from the ethnicities actually
seated in the active scenario, and all seats are verified reachable.

*Anti-corruption body effectiveness under the 2008 encoding.* Root-caused to the
institutional sub-model's annual operations routine and fixed, as described under Reviewer
1's fourth concern, together with a second discrepancy of the same class that the audit
found independently.

**Author action:**

We updated the manuscript by implementing and documenting the composite write path and
reporting the composite decomposed in Section V-E (The North-Star Composite, Decomposed)
and in Section III-G, with the three-identical-terms finding and the 45 percent weight
figure; by reporting the ethnic-harmony resolution as partial in Section VIII-C
(Limitations) item 6 and by removing every cross-country ethnic-harmony claim from the
paper; by reporting the council-vote defect and its fix; and by reporting the effectiveness
discrepancy and its cause in Sections V and V-B and as defect D8 in Table 2.
[PENDING CAMPAIGN: the seven-term decomposition table for every encoding at the
publication sample size, and the recomputed effectiveness column.]

---

## Reviewer#2, Concern # 4 (please list here):

"The LLM and rule-based versions produce almost identical overall outcomes... it also
shows that the LLM is currently only weakly connected to the main simulation results. The
role and value of the generative-agent component should therefore be demonstrated more
clearly."

**Author response:**

We accept the observation and we have treated the request literally: the concern asks for
the role to be **demonstrated more clearly**, and we answer it with a demonstration rather
than with an argument. There are three parts, and the second is new evidence produced
specifically for this concern.

First, we accept that the layer is weakly connected to aggregate outcomes, and we go
further than the submitted manuscript by deriving that weakness from the coupling design
rather than reporting it as a finding. The derivation is given under Reviewer 1's third
concern and in Section VIII-A. We state plainly that the coupling is weak by construction
and that strengthening it is the priority for the next iteration of the engine.

Second, the demonstration. The role of the generative layer is that it is the only
substrate that produces the behaviour the runtime validator exists to govern, and that
behaviour is now demonstrated **on two real, historically enacted constitutions, with no
author-designed constitution involved**. On a smoke test of three runs over ten simulated
years with 300 citizens per run, with the language model live:

- Under the **South Korea 1987** encoding, a civilian-supremacy chain, the elite agents
  emitted coup signals and **five were intercepted and annulled by the constitutional
  layer**, producing an enforcement record. [PENDING CAMPAIGN: the emitted count for this
  encoding, which was not separately recovered from the smoke test.]
- Under the **Pakistan 1973 Constitution as amended by the Eighth Amendment** encoding, a
  military chain, the elite agents emitted **28 coup signals and none were intercepted**.
  Every one was permitted, and no violations file was created at all, because that encoding
  reaches no live constitutional rule.

That is the differential-constraint mechanism: the same elite behaviour, generated by the
same model under the same engine, is unlawful under one encoded constitution and lawful
under another, recoverable per decision from a shipped log. A deterministic rule-based
elite does not produce that behaviour at all, so the enforcement record has no rule-based
counterpart. **We report both counts as smoke-test magnitudes and as lower bounds, not as
results.** The sample is three runs over ten years; the run was executed before the final
parser fix, so some decisions were still being replaced by role defaults with the coup
signal forced to false, which can only have suppressed the counts and never inflated them.
[PENDING CAMPAIGN: both counts at the publication sample size and horizon, which replace
the smoke-test magnitudes.]

Third, the ablation. The constitutional layer can be run in enforce, observe and off modes,
and the identical configuration run under enforce against observe gives the measured
contribution of runtime constitutional enforcement to the reported indicators. This is the
only quantity in the revision that bears directly on this concern and is a number rather
than an argument. **We pre-commit to the reporting position before seeing the result, and
record that pre-commitment in the manuscript**, because the plausible outcome is that the
suppression of coup probability under a civilian-supremacy encoding is produced by the
validator rather than by the constitutional provision, which would contradict the submitted
manuscript's own discussion. If that is the result, it is the finding and it will be
reported as such, and the submitted mechanism narrative is withdrawn accordingly. We also
record that the ablation must run on a civilian chain, because on a military chain the
measured difference is structurally zero: that encoding reaches no live rule, which we
confirmed empirically and not only by reading the source.

We also report, rather than omit, the finding that bears against us here. Before this
revision the prompts for the enacted encodings instructed the model not to emit the very
signal the validator exists to intercept, which is both circular and disabling of the
measurement. The instructions were removed after a systematic read of every role prompt by
three distinct defect patterns, and a re-audit by all three patterns found no remaining
instance; we state the patterns searched for and note that the search was not exhaustive
over all possible forms of output-directing language.

**Author action:**

We updated the manuscript by rewriting Section VIII-A as described under Reviewer 1's
third concern; by adding Section VII-B (Differential Constraint) to report the enforcement
record per decision and per role on real enacted encodings; by adding Section VII-G (The
L2 Ablation) containing the pre-committed reporting position in the text, dated before the
run; by adding Section III-D-1 (Prompt Symmetry) with the audit method, the patterns
searched for and the bound of the search; by adding the weak-coupling disclosure and the
elite-to-citizen coupling strengthening item to Section VIII-A and Section XI-A (Future
Work); and by removing the designed constitutions from the experimental roster so that the
differential-constraint demonstration rests on real enacted texts.
[PENDING CAMPAIGN: the enforce-versus-observe indicator difference, which is the direct
numerical answer to this concern.]

---

## Appendix to this response: status of each concern

| # | Concern (short) | Status |
|---|---|---|
| R1.1 | Additional scenarios and/or sensitivity analysis | Answered, with the honest negative component stated |
| R1.2 | Results not mechanically induced | Answered in the negative, all four separations |
| R1.3 | Scientific role of the LLM component | Answered, provenance horn adopted and evidenced |
| R1.4 | Parameter-limit discrepancies explained | Answered |
| R1.5 | Historical backtesting on a restricted subset of outputs | Partially answered; survival prediction scoped as a limitation |
| R1.6 | Figure quality | Pending deliverable, not yet answerable |
| R1.7 | Generative-AI disclosure for figures | Pending factual determination, not yet answerable |
| R1.8 | Reproducibility package | Answered, with two items scoped as limitations |
| R2.1 | More similar constitutions | Cannot be fully answered; reported as a measured negative result |
| R2.2 | Manually chosen constitutional and feedback parameters | Answered |
| R2.3 | Constant metrics and the effectiveness discrepancy | Answered; ethnic harmony partially, labelled as such |
| R2.4 | Role and value of the generative component | Partially answered; the ablation number is pending |
