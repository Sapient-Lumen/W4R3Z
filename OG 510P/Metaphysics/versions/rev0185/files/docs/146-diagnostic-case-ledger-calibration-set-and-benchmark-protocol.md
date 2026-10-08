# Diagnostic Case Ledger, Calibration Set, and Benchmark Protocol

## Why this file exists

The archive now has two strong control layers: `144-operator-family-map-and-triage-grid.md` routes difficult cases, and `145-adversarial-stress-tests-and-revision-protocol.md` attacks the preferred routing. That is necessary but not sufficient. A case can be routed and stress-tested well once, then later be remembered only as a slogan: "that was a valving case," "that was only artifact," "that was a continuity case," or "that candidate was demoted." The reasons for the verdict then become invisible.

This file adds a third control layer: a **diagnostic case ledger** and **calibration protocol**. Its job is to preserve not only the answer but the tested path by which the archive earned the answer. The archive should be able to rerun hard cases, compare new cases against old ones, and notice when a future revision silently changes the standard of classification.

The danger addressed here is not ordinary error alone. It is **case drift**: the tendency of a growing archive to remember examples as trophies rather than as tests.

## Compressed default

The archive should now say explicitly:

> **No reusable metaphysical classification should be stabilized unless the archive can state the case record that would reproduce, defeat, or revise it.**

In compressed form:

> **Route the case, attack the route, then record the discriminating result.**

And more carefully:

> **A mature operator archive should maintain calibration cases: positives that the operator should catch, negatives that neighboring operators should catch instead, hard positives where the right basis appears under misleading vocabulary, hard negatives where the right vocabulary appears without the basis, boundary cases that should remain unsettled, and regression cases that future revisions must not accidentally reverse.**

## Place in the control sequence

The intended order for hard cases is now:

1. **Target isolation** — state what the case is about before choosing an operator.
2. **Family routing** — use `144` to locate the likely family and nearest rival files.
3. **Adversarial stress** — use `145` to vary word, basis, grain, proxy, failure mode, and continuity consequence.
4. **Ledger recording** — use this file to record the result when the case is reusable, difficult, precedent-setting, or diagnostic for a family.
5. **Revision action** — amend a rule, consolidate a family, demote a proposal, add an operator, or leave the archive unchanged.
6. **Propagation audit** — use `147-revision-dependency-graph-update-propagation-and-drift-control.md` to update, explicitly decline, or ledger downstream consequences before packaging.
7. **Terminology audit** — use `148-terminology-register-synonym-control-and-crosswalk-protocol.md` to record which words the case licenses, blocks, aliases, quarantines, or deprecates.
8. **Commitment-status assignment** — use `149-claim-status-register-maturity-levels-and-commitment-governance.md` to state whether the ledgered result is doctrine, default, diagnostic, local, rival, provisional, quarantined, source-dependent, deprecated, or open debt.
9. **Application dossiering** — use `150-application-dossier-decision-record-and-verdict-report-protocol.md` when the ledgered result will travel as a verdict.
10. **Precedent-reuse governance** — use `151-precedent-reuse-appeal-transfer-and-review-governance.md` when the ledgered or dossiered result will be reused, taught, transferred, appealed, superseded, or marked do-not-reuse.
11. **Transmission governance** — use `152-transmission-excerpt-compression-and-pedagogical-governance.md` when a ledgered, calibrated, or regression case will be summarized, excerpted, taught, diagrammed, or exported.

This file therefore does not replace `144` or `145`, and it is now complemented by `147`, `148`, and `149`. It turns routed and stress-tested results into reusable calibration material; `147` then asks where accepted calibration results must propagate, `148` asks which terms those results license, block, alias, quarantine, or deprecate, `149` asks what commitment status the ledgered result should have, `150` records how the result should travel, and `151` governs whether later uses preserve or appeal that result.

## What counts as a ledger case

A ledger case is not merely an example. It is a **case with discriminating work to do**.

A case is ledger-worthy when at least one of the following holds:

- it is a **nearest-neighbor case** between two or more files,
- it is a **hard positive** where the basis is present but the ordinary vocabulary is misleading,
- it is a **hard negative** where the vocabulary is present but the basis is absent,
- it is a **regression case** that a future revision might accidentally reverse,
- it is a **promotion case** used to justify a new operator,
- it is a **demotion case** used to keep a proposed distinction out of the archive,
- it is a **scope case** that narrows a file's proper domain,
- it is an **artifact case** where the evidence could be proxy-only,
- or it is a **mixed-family case** whose verdict depends on ordered rather than flat use of several files.

Ordinary illustrations may remain inside local operator files. Ledger cases are reserved for examples that calibrate the archive.

## Case record schema

Every substantial ledger entry should use the following fields. A quick entry may use a compressed subset, but promotion, demotion, family consolidation, and synthesis-level revisions should use the full form.

| Field | Required question |
| --- | --- |
| **Case ID** | What stable identifier will let future revisions find this case? |
| **Case status** | Probe, accepted calibration case, negative control, boundary case, regression case, retired case, or superseded case? |
| **Target** | What exactly is under discussion: object, process, relation, role, status, fact, representation, path, flow, interface, capacity, or mixed target? |
| **Ordinary description** | What vocabulary tempts the archive: same, real, part, contains, supports, guides, controls, stores, represents, fails, replaces, opens, closes, or similar? |
| **Primary family** | Which family in `144` bears the main explanatory burden? |
| **Secondary families** | Which neighboring families create plausible but non-primary diagnoses? |
| **Nearest rival files** | Which three existing files have the best claim to handle the case? |
| **Basis** | What actually does the work: material continuity, organization, role, record, boundary, route, aperture, load path, access channel, control architecture, or mixed basis? |
| **Grain** | At what level does the verdict hold: token, type, stage, event, process, system, role, lineage, population, institution, model, regime, or mixed grain? |
| **Positive control** | What nearby case should clearly receive the preferred verdict? |
| **Negative control** | What nearby case should clearly not receive the preferred verdict? |
| **Hard positive** | Where does the basis appear even though the vocabulary is weak or absent? |
| **Hard negative** | Where does the vocabulary appear even though the basis is missing? |
| **Hostile variants** | What happens under same-word/changed-basis, same-basis/changed-word, wrong-grain, proxy-artifact, fission, and failure-mode variation? |
| **Artifact risks** | Which readout, label, model boundary, file name, administrative status, appearance, or route marker could mislead? |
| **Defeaters** | What would force reclassification, demotion, or quarantine? |
| **Continuity consequence** | What remains the same, what changes, and what sort of sameness is not licensed? |
| **Decision** | Existing-file verdict, paired-file verdict, narrowed scope, amended rule, family consolidation, demotion, quarantine, promotion, or unsettled? |
| **Update footprint** | Which control files, local files, source notes, index entries, or manifest entries must change? |
| **Regression instruction** | What must future revisions avoid accidentally reversing? |
| **Open debt** | What still needs a better example, source anchor, distinction, or counterexample? |

The point of the schema is not bureaucracy. It prevents the archive from accepting a classification without saying how the result could be reproduced or defeated.

## Control types

### 1. Positive controls

A positive control is a case the target operator should plainly catch. If a proposed diagnosis cannot handle its own positive controls, the file is underpowered.

Example pattern: a valve that changes aperture and thereby regulates flow rate is a positive control for valving rather than mere guidance.

### 2. Negative controls

A negative control is a nearby case the target operator should not catch. If a proposed diagnosis absorbs its negative controls, the file is too loose.

Example pattern: a fixed pipe that only constrains path is a negative control for valving and a better case for guidance or channeling.

### 3. Hard positives

A hard positive lacks the ordinary label but preserves the basis. The archive should still classify it correctly.

Example pattern: an automated dosage system might not be called a valve in ordinary language, but if the explanatory burden is variable admission through a regulated aperture or equivalent metering architecture, it belongs near valving.

### 4. Hard negatives

A hard negative has the ordinary label but lacks the basis. The archive should resist the word.

Example pattern: a "support" contact that carries no load is not support in the relevant metaphysical sense, even if it is described as support in an interface diagram.

### 5. Boundary cases

A boundary case is not a failure. It is a case where the archive should deliberately withhold promotion or compression until better basis, grain, or artifact-risk evidence appears.

Boundary cases are useful because they prevent the archive from forcing every example into a settled verdict.

### 6. Regression cases

A regression case is a case already used to stabilize a distinction. Future revisions should not reverse it accidentally when adding a nearby operator.

Example pattern: once the archive distinguishes sealing from valving, later additions about filtering, gating, or shielding should not collapse sealing into every case of reduced passage.

## Decision grammar

A ledger case should end in one of the following verdicts:

1. **Existing-file verdict.** One current file handles the case without amendment.
2. **Paired-file verdict.** The case requires two files in ordered relation, such as guidance plus valving, or substitution plus role continuity.
3. **Narrowed-scope verdict.** A file still works, but only under stricter basis or grain conditions.
4. **Method-rule amendment.** The archive needs a new compression or selection rule rather than a new first-order operator.
5. **Family-map amendment.** The routing map needs repair because the family relation was misdescribed.
6. **Frontier-test amendment.** The case belongs in `04` as an unresolved discriminating test.
7. **Demotion.** The proposed distinction belongs as a paragraph, example, warning, or contrast class rather than as a file.
8. **Quarantine.** The archive lacks enough basis, grain, or artifact-risk evidence to stabilize the case.
9. **Consolidation.** Several adjacent files need a higher-level grammar or shared decision tree.
10. **Promotion.** A genuinely new operator is warranted because triage, stress testing, and calibration all show a stable compression gap.

Promotion is therefore only one possible success condition. Often the stronger result is demotion, narrowing, or consolidation.

## Calibration families and benchmark prompts

The following prompts are not final verdicts. They are benchmark designs: each should generate at least one positive control, one negative control, one hard positive, one hard negative, and one boundary case when used seriously.

### 1. Status and category benchmarks

Use these to test whether the archive can distinguish target, representation, status, and category.

- A role remains institutionally valid while its bearer changes.
- A record remains accurate while the target changes later.
- A model variable remains indispensable while the alleged target has no independent basis.
- A legal status persists through administrative transfer but not through the collapse of the rule system that sustains it.
- A fact description remains true while the worldly obtaining is redescribed under a different category.

Calibration danger: treating a status as an object, a record as a truthmaker, or a useful model element as automatically real.

### 2. Unity, identity, and continuity benchmarks

Use these to test whether the archive can distinguish numerical identity, material continuity, formal continuity, organizational continuity, role continuity, and lineage.

- A material basis is gradually replaced while organization continues.
- Organization is copied, producing two successors.
- A role continues through a new bearer.
- A lineage continues through repair but not through independent duplication.
- A coincident material basis supports two differently individuated targets.

Calibration danger: proving continuity at one grain and smuggling it into identity at another.

### 3. Dependence and grounding benchmarks

Use these to test whether the archive can distinguish grounding, realization, constitution, causal support, enabling background, scaffolding, and hosting.

- A phenomenon survives removal of one enabling condition by using a substitute basis.
- The alleged ground remains while the organization that mattered disappears.
- A scaffold is necessary during development but not after stabilization.
- A host carries a guest without constituting it.
- A mechanism realizes a capacity without grounding every truth about the system.

Calibration danger: promoting every important condition into the same dependence relation.

### 4. Truthmaker, absence, and privation benchmarks

Use these to test whether the archive can handle negative truth without ontological inflation.

- An empty seat is empty because no occupant is present within a bounded contrast class.
- A missing payment is a privation only relative to a normative or institutional expectation.
- A hole, gap, blockage, and closure share absence-language but differ in positive basis.
- A prevention event and a mere non-occurrence differ in causal and contrastive structure.
- An unrealized capacity remains real though the manifestation is absent.

Calibration danger: reifying every negative truth or, conversely, erasing every absence with explanatory force.

### 5. Access, evidence, and representation benchmarks

Use these to test whether the archive can separate target, vehicle, readout, representation, operationalization, and artifact.

- A detector produces the same readout under a target and under an artifact.
- A model fits while the mechanism producing the fit changes.
- A proxy tracks a target in one regime and fails outside it.
- A map retains reference while changing scale and idealization.
- A report remains sincere while mislocating its target.

Calibration danger: treating access success as ontology or artifact failure as absence of a target.

### 6. Process, time, and transition benchmarks

Use these to test onset, cessation, recurrence, dormancy, delay, attrition, irreversibility, and critical transition.

- A dormant capacity persists without current manifestation.
- A delayed effect arrives after the initiating process has ended.
- A process stops, restarts, and returns without strict identity of every stage.
- Wear accumulates below the threshold of visible failure.
- A tipping event changes the landscape rather than merely moving within it.

Calibration danger: treating every absence of current activity as nonexistence or every return as simple identity.

### 7. Stock, flow, and availability benchmarks

Use these to test accumulation, depletion, replenishment, turnover, circulation, bottlenecking, rerouting, leakage, release, and retention.

- A stock is depleted while throughput continues.
- A bottleneck limits flow without reducing total stock.
- Leakage resembles release but lacks authorized or organized discharge.
- Turnover preserves system-level continuity while replacing constituents.
- Rerouting preserves delivery while changing path architecture.

Calibration danger: collapsing stock, flow, route, rate, reserve, and availability into one quantity vocabulary.

### 8. Interface, placement, support, and assembly benchmarks

Use these to test hosting, attachment, embedding, enclosure, coating, wrapping, lamination, sealing, joining, articulation, clamping, latching, threading, meshing, gripping, support, and guidance.

- A hosted item changes host without becoming part of the host.
- An embedded item is inserted into a site without being identical to the site.
- A sealed boundary blocks passage without guiding or metering what passes.
- A support relation carries load without attaching or hosting the load.
- A guide constrains path without regulating quantity or rate.

Calibration danger: treating every with/in/on/through relation as one generic interface relation.

### 9. Control, capacity, and response benchmarks

Use these to test gating, feedback, saturation, habituation, filtering, shielding, valving, throttling, metering, and regulation.

- A gate permits or blocks coupling without metering quantity.
- A valve regulates admission rate without merely defining a path.
- A filter selectively attenuates components without closing the boundary.
- Saturation limits additional output without proving disappearance of capacity.
- Negative feedback stabilizes a variable without eliminating the process.

Calibration danger: treating all control, resistance, and selectivity as one openness/closure vocabulary.

### 10. Social, normative, living, agential, and conscious benchmarks

Use these to test the archive's typed handling of domains whose reality depends on organization, role, norm, agency, organismic form, or subjectivity.

- An office persists through change of office-holder.
- A norm remains binding despite local noncompliance.
- An organism persists through cellular turnover but not through every possible functional copy.
- Delegated agency preserves accountability under some institutional structures but not all.
- A report tracks an experience in some cases and a social signal in others.

Calibration danger: flattening normativity into causation, consciousness into report, life into mechanism alone, or institution into mere belief.

## Starter ledger templates

The archive should use concise IDs. A recommended form is:

- `CL-STATUS-001` for status/category cases,
- `CL-ID-001` for identity/continuity cases,
- `CL-DEP-001` for dependence cases,
- `CL-TRUTH-001` for truthmaker/absence cases,
- `CL-ACCESS-001` for evidence/representation cases,
- `CL-PROCESS-001` for process/time cases,
- `CL-FLOW-001` for stock/flow cases,
- `CL-INTERFACE-001` for interface/support cases,
- `CL-CONTROL-001` for capacity/control cases,
- and `CL-DOMAIN-001` for social/normative/living/agential/conscious cases.

A minimal ledger entry can be written as:

```text
Case ID:
Status:
Target:
Ordinary description:
Primary family:
Nearest rival files:
Basis:
Grain:
Positive control:
Negative control:
Hard positive:
Hard negative:
Hostile variants:
Artifact risks:
Defeaters:
Continuity consequence:
Decision:
Regression instruction:
Open debt:
```

A revision does not need to fill a long table for every example. It does need to fill one when a case becomes precedential.


## Starter compact calibration entries

The following entries are deliberately compact. They are not meant to settle all metaphysical disputes. They show the intended grain of ledger use: enough structure to preserve the discriminating work, not so much structure that every example becomes a monograph.

### CL-ID-001: Role continuity without bearer identity

- **Status:** accepted calibration pattern.
- **Target:** continuity of a role through change of bearer.
- **Primary family:** unity, identity, social/status.
- **Nearest rival files:** `29-identity-individuality-and-haecceity.md`, `37-social-ontology-status-functions-and-institutional-reality.md`, `86-succession-inheritance-descent-and-lineage-continuity.md`.
- **Basis:** rule-governed role continuity and institutional recognition, not material or personal identity.
- **Positive control:** an office continues when one office-holder is replaced by another under valid succession rules.
- **Negative control:** the former office-holder does not remain numerically identical to the successor.
- **Hard positive:** the role continues even when ordinary language emphasizes the new person rather than the office.
- **Hard negative:** a ceremonial title used without operative rules does not supply the same continuity basis.
- **Decision:** paired-file verdict: social-status continuity plus succession, not numerical identity.
- **Regression instruction:** do not let role continuity prove bearer identity.

### CL-ID-002: Duplication defeats simple identity transfer

- **Status:** accepted calibration pattern.
- **Target:** copied organization producing two successor candidates.
- **Primary family:** unity, identity, duplication.
- **Nearest rival files:** `12-unity-sortals-and-persistence.md`, `87-duplication-copying-fission-and-branching-continuity.md`, `124-substitution-replacement-stand-ins-and-functional-equivalence.md`.
- **Basis:** copying or branching preserves some structure but not one-one numerical identity when two equally qualified successors exist.
- **Positive control:** two independently running copies inherit a pattern or lineage relation.
- **Negative control:** both copies cannot be the one original in the same numerical-identity sense.
- **Hard positive:** duplication can occur without ordinary "copy" vocabulary if the one-one continuity relation branches.
- **Hard negative:** replacement by one functionally equivalent successor is not yet branching duplication.
- **Decision:** existing-file verdict: duplication/branching continuity blocks simple identity transfer.
- **Regression instruction:** never allow fission to silently duplicate strict identity.

### CL-DEP-001: Scaffold dependence versus constitution

- **Status:** accepted calibration pattern.
- **Target:** a dependent organization enabled by a support structure.
- **Primary family:** dependence, support, scaffolding.
- **Nearest rival files:** `08-dependence-relations-map.md`, `76-scaffolding-support-niche-construction-and-environmental-enablement.md`, `141-support-bearing-suspension-hanging-bracing-and-load-path-carriage.md`.
- **Basis:** enabling or developmental support, not automatic parthood or constitution.
- **Positive control:** a support condition enables formation or maintenance of a target.
- **Negative control:** removal of one scaffold after stabilization need not destroy the target if the relevant organization has become self-maintaining or otherwise supported.
- **Hard positive:** a background niche can scaffold a process even when ordinary language does not call it a part.
- **Hard negative:** a coincident object is not scaffolding merely because it is nearby.
- **Decision:** narrowed-scope verdict: scaffold only where the enabling relation is doing explanatory work.
- **Regression instruction:** do not promote every enabling condition into a constituent.

### CL-TRUTH-001: Bounded absence without negative-entity inflation

- **Status:** accepted calibration pattern.
- **Target:** truth of an absence claim.
- **Primary family:** truthmaker, absence, privation.
- **Nearest rival files:** `13-truthmakers-absences-and-privation.md`, `56-facts-states-of-affairs-and-obtaining.md`, `57-truth-correspondence-and-reality-answerability.md`.
- **Basis:** positive arrangement plus contrast class, not a free-standing negative object.
- **Positive control:** a bounded space with no occupant can make an emptiness claim true.
- **Negative control:** every true negative sentence does not require a distinct negative fact-thing.
- **Hard positive:** absence can be metaphysically relevant even when the positive basis is a norm, role, or expected function.
- **Hard negative:** mere non-salient nonpresence outside a relevant contrast class is not a privation.
- **Decision:** existing-file verdict: restrained truthmaker treatment.
- **Regression instruction:** preserve the difference between absence, privation, omission, prevention, and mere non-occurrence.

### CL-ACCESS-001: Readout stability without target stability

- **Status:** accepted calibration pattern.
- **Target:** access relation between target, instrument, and readout.
- **Primary family:** access, evidence, artifact-risk.
- **Nearest rival files:** `61-measurement-detection-and-operationalization.md`, `65-robustness-triangulation-and-convergent-access.md`, `66-artifact-risk-distortion-and-failure-modes.md`.
- **Basis:** readout-generation architecture, not target ontology by itself.
- **Positive control:** a stable readout across independent methods increases confidence in a target.
- **Negative control:** a stable readout from one faulty channel can be an artifact.
- **Hard positive:** a target may be real even when one operationalization fails.
- **Hard negative:** a measurement category can persist administratively after losing target contact.
- **Decision:** paired-file verdict: measurement plus artifact-risk audit before ontological promotion.
- **Regression instruction:** do not convert proxy stability into target stability without triangulation.

### CL-PROCESS-001: Dormancy versus cessation

- **Status:** accepted calibration pattern.
- **Target:** inactive but continuing capacity or organization.
- **Primary family:** process, time, capacity.
- **Nearest rival files:** `79-dormancy-latency-standby-and-suspended-activity.md`, `84-cessation-deactivation-offlining-and-terminal-ending.md`, `85-reactivation-recurrence-restart-and-return.md`.
- **Basis:** preserved readiness or latent organization, not current manifestation.
- **Positive control:** a dormant capacity remains structured for reactivation.
- **Negative control:** terminal destruction is not dormancy merely because nothing is happening now.
- **Hard positive:** inactivity can be dormancy even when ordinary descriptions call it "off." 
- **Hard negative:** a broken system labeled "standby" is not latent readiness.
- **Decision:** existing-file verdict: dormancy requires preserved reactivation basis.
- **Regression instruction:** do not infer nonexistence from nonmanifestation alone.

### CL-FLOW-001: Leakage versus authorized release

- **Status:** accepted calibration pattern.
- **Target:** movement of stored or contained material out of a boundary.
- **Primary family:** stock/flow, boundary, control.
- **Nearest rival files:** `115-release-discharge-unloading-and-mobilization.md`, `116-leakage-seepage-permeation-and-uncontrolled-escape.md`, `133-sealing-closure-plugging-gasketing-and-caulking.md`.
- **Basis:** organized discharge versus uncontrolled escape through failed or porous boundary.
- **Positive control:** a designed release event restores availability or discharges a held stock.
- **Negative control:** seepage through a failed seal is not authorized release.
- **Hard positive:** controlled unloading can be release even if ordinary language says material "leaked out" casually.
- **Hard negative:** a valve label does not make an uncontrolled escape into regulated release.
- **Decision:** nearest-rival verdict: release and leakage must be separated by control architecture and failure mode.
- **Regression instruction:** do not let outward movement alone settle release, leakage, or depletion.

### CL-INTERFACE-001: Sealing versus valving

- **Status:** accepted regression pattern.
- **Target:** boundary relation governing passage.
- **Primary family:** interface, passage, control.
- **Nearest rival files:** `133-sealing-closure-plugging-gasketing-and-caulking.md`, `142-guiding-channeling-conduiting-ducting-and-rail-guided-passage.md`, `143-valving-throttling-metering-and-aperture-control.md`.
- **Basis:** closure integrity versus regulated admission, rate, or aperture.
- **Positive control:** a gasketed closure blocks unwanted passage by maintaining interface integrity.
- **Negative control:** a variable aperture that meters flow is not merely a seal.
- **Hard positive:** a seal can be real even without explicit "sealed" vocabulary if the work is closure across an interface.
- **Hard negative:** a label saying "sealed valve" may hide the fact that the relevant metaphysical work is metering, not closure.
- **Decision:** paired-rival verdict: sealing and valving are adjacent but not interchangeable.
- **Regression instruction:** later control files must not collapse every passage-reduction case into sealing or every closure case into valving.

### CL-CONTROL-001: Gating versus valving

- **Status:** accepted calibration pattern.
- **Target:** selective permission versus metered regulation.
- **Primary family:** control, coupling, passage.
- **Nearest rival files:** `97-gating-coupling-tuning-and-selective-responsiveness.md`, `122-bottlenecks-congestion-backpressure-and-chokepoints.md`, `143-valving-throttling-metering-and-aperture-control.md`.
- **Basis:** permissive coupling or responsiveness window versus aperture/rate/dose regulation.
- **Positive control:** a gate opens a coupling condition or permission window.
- **Negative control:** a throttling element that continuously meters flow is not just gating.
- **Hard positive:** gating can occur without a physical gate if the basis is selective responsiveness.
- **Hard negative:** an on/off label can hide continuous metering or backpressure control.
- **Decision:** narrowed-scope verdict: gating is not generic control; valving is not generic permission.
- **Regression instruction:** preserve the difference between selection, route permission, quantity regulation, and capacity limit.

### CL-DOMAIN-001: Normative persistence despite noncompliance

- **Status:** accepted calibration pattern.
- **Target:** normative status under violation.
- **Primary family:** normative, social, status.
- **Nearest rival files:** `37-social-ontology-status-functions-and-institutional-reality.md`, `44-normativity-reasons-and-deontic-structure.md`, `81-malfunction-pathology-deviance-and-misfire.md`.
- **Basis:** rule, reason, authority, or correctness condition that persists despite some failures of conformity.
- **Positive control:** a requirement remains binding when someone violates it.
- **Negative control:** repeated behavior alone does not generate normativity without the relevant authority, practice, or correctness structure.
- **Hard positive:** normativity can operate without explicit command vocabulary when reasons or standards are active.
- **Hard negative:** prediction or regularity is not obligation merely because it is socially expected.
- **Decision:** paired-file verdict: normativity plus social status where appropriate, not causal regularity alone.
- **Regression instruction:** do not reduce normative reality to compliance rates or psychological pressure.

## Anti-patterns

### 1. Trophy-example use

A case is used only because it sounds vivid. No rival, basis, grain, negative control, or defeater is recorded.

Correction: downgrade the example to illustration until it has a case record.

### 2. Verdict-first ledgering

The case record is written only after the verdict is already fixed, and the controls are chosen to flatter the result.

Correction: write the positive and negative controls before the final verdict.

### 3. Vocabulary capture

The case is classified by the word used in ordinary description rather than by the basis doing the work.

Correction: add hard positives and hard negatives.

### 4. Grain leakage

A case proves continuity at role, type, or system grain and is then used as evidence for token identity.

Correction: write the grain into the decision line.

### 5. Artifact laundering

A readout, record, file name, label, administrative category, or model boundary is treated as if it were the target itself.

Correction: add a proxy-artifact variant and require a target/vehicle distinction.

### 6. Expansion laundering

A new operator is promoted because it has examples, not because the examples defeat existing files under calibration.

Correction: require a negative-control set showing why neighboring files fail.

## Regression protocol for future revisions

Before adding a new first-order operator, future revisions should run the candidate against at least:

- the nearest three files named by `144`,
- two positive controls for the proposed operator,
- two hard negatives from neighboring files,
- one same-word/changed-basis variant,
- one same-basis/changed-word variant,
- one wrong-grain variant,
- one proxy-artifact variant,
- and one regression case from an older file that the new operator must not swallow.

Before consolidating a family, future revisions should run at least one case from each member file and at least two boundary cases where the old files were easy to confuse.

Before demoting a proposed operator, future revisions should record which evidence would have promoted it if found. Demotion without a promotion condition is too easy.

## Relation to sources

This file adds no new external anchor by itself. It is methodological. When a ledger case depends on a historical, scientific, legal, clinical, engineering, or textual example, the local revision should cite the source in `05-source-citations.md` or keep the case generic.

Generic calibration cases are allowed only when they are used to test the archive's internal distinction. Case-specific empirical claims need their own source support.

## Relation to revision-dependency propagation

A ledgered case can itself create archive-wide obligations. If a case becomes a regression test, negative control, demotion precedent, promotion precedent, or family-defining benchmark, `147-revision-dependency-graph-update-propagation-and-drift-control.md` should determine which front-door, synthesis, method, frontier, source, family-map, adversarial, terminology, index, version, manifest, and package files must recognize that status.

The ledger preserves the verdict path; the propagation protocol prevents that preserved verdict from becoming invisible to the rest of the archive.

## Relation to terminology registration

A ledgered case can also create term obligations. If a case shows that the same word changes basis, that different words share a basis, that a metaphor must be quarantined, that an alias is safe only under a condition, or that a source-specific term should not be exported, `148-terminology-register-synonym-control-and-crosswalk-protocol.md` should record the term status.

The ledger preserves the verdict path; the terminology register preserves the vocabulary discipline that made the verdict reproducible.

## Relation to the archive's anti-bloat policy

The anti-bloat policy previously said: route before expanding, then stress-test the route. This file adds: **calibrate before reusing**. `147` adds: **propagate before closing**. `148` adds: **register terms before letting vocabulary carry doctrine**. `149` adds: **assign status before letting a distinction carry commitment**. `150` adds: **write an application dossier before letting a verdict travel**. `151` adds: **govern reuse and appeal before letting a dossier become precedent**.

A distinction is not mature merely because it is stated clearly. It is mature when the archive knows what would count for it, what would count against it, what would look like it without being it, what would be it without looking like it, and what future revision must not forget.

## Default verdict

The default verdict of this file is procedural:

> **Stable ontology requires repeatable diagnosis, not just persuasive analysis.**

The archive should therefore treat ledgered cases as calibration instruments. They are not ornaments. They are the means by which a large metaphysical archive keeps itself answerable to its own distinctions.


## Revision-integration note: ledger cases and commitment status

`149-claim-status-register-maturity-levels-and-commitment-governance.md` adds a status layer to calibration. A ledgered case is not automatically doctrine. It may be a positive control, negative control, hard positive, hard negative, boundary case, regression warning, demotion case, source-bound case, or open debt.

Future ledger entries should include a compact **commitment-status field** when the case will guide later revisions. At minimum, record whether the case creates a calibrated precedent, preserves a live rival, narrows a working default, demotes a candidate, quarantines an analogy, or leaves open debt.


## Revision-integration note: ledger cases and application dossiers

`150-application-dossier-decision-record-and-verdict-report-protocol.md` adds a report layer to calibration. A ledgered case already preserves controls, boundary behavior, regression instructions, and defeaters. The application dossier adds how that case may be communicated and reused: illustration, precedent, calibration, regression warning, source-bound example, live rival, open pressure, or do-not-reuse.

Future ledger entries should therefore include a compact **future-use permission** field when the case will guide later work. This prevents a vivid calibration example from being promoted into unrestricted precedent by repetition alone.


## Revision-integration note: calibration and precedent status

`151-precedent-reuse-appeal-transfer-and-review-governance.md` distinguishes calibration precedent from teaching illustration, controlled precedent, regression warning, source-bound precedent, live-rival precedent, deprecated caution, appeal-pending item, and do-not-reuse item. Future ledger entries should therefore record not only whether a case is positive control, negative control, hard positive, hard negative, boundary case, or regression case, but also how it may be reused and what appeal triggers would suspend that reuse.


## Revision-integration note: calibration cases in transmission

`152-transmission-excerpt-compression-and-pedagogical-governance.md` adds a rule for calibration visibility. A calibration case should not be transmitted as if it were a generic memorable example. Future ledger entries should therefore mark whether the case may appear in C1 orientation, C3 teaching, C5 technical briefs, or C7 archive-grade extraction, and what warning must accompany it: illustration only, calibration control, regression warning, source-bound, appeal pending, or do-not-reuse.

## Revision-integration note: reception cases as calibration instruments

`153-reception-feedback-errata-and-correction-loop-governance.md` identifies repeated misreadings, failed transfers, teaching failures, operational failures, and source-boundary confusions that may deserve ledger status. Future calibration entries should distinguish cases that test the doctrine from cases that test the transmission. A reception failure can be a valuable regression case even when the underlying metaphysical verdict remains unchanged.

## Revision-integration note: calibration debt and release packets

`154-release-gates-maintenance-ledgers-deprecation-and-rollback-governance.md` requires release packets to say whether ledgered hard cases are satisfied, deferred, or release-blocking. A case may be useful enough for release with declared debt, but not if the release hides that the distinction lacks positive controls, negative controls, hard negatives, or regression instructions needed for future reuse.

## Revision-integration note: version lineage and compatibility

Calibration cases now need lineage status when they cross releases: a case may remain a control, become historical caution, require redossiering, or lose precedent force after source, term, status, or method changes.

## Revision-integration note: provenance, custody, and reproducibility

`rev0150` adds `156-provenance-custody-build-evidence-and-reproducibility-governance.md`. Calibration cases now need artifact provenance when they travel across releases, forks, teaching derivatives, source-refresh branches, or recovered copies. A case may remain diagnostically valuable while the artifact that carries it is only historical, teaching-only, partial-custody, or quarantine pending rebuild.


## Revision-integration note: review authority and claim warrant

`rev0151` adds `157-review-authority-audit-certification-and-claim-warrant-governance.md`. Ledger cases and calibration benchmarks should distinguish being recorded from being reviewed. A calibration entry may be useful, but it should not become a controlled reviewed precedent unless its review scope, evidence, and permitted claim language are stated.

## Revision-integration note: public reliance after review

`rev0152` adds `158-public-reliance-citation-dispute-withdrawal-and-retraction-governance.md`. The control stack now distinguishes review warrant from public reliance. A result that is correctly routed, stress-tested, ledgered, propagated, named, status-assigned, dossiered, transmission-safe, reception-audited, release-gated, lineage-governed, provenance-audited, and reviewed still needs public-use status before it may circulate as something others can rely on. Future use should therefore ask whether the item is U0 private scratch, U1 orientation, U2 historical citation, U3 public summary with limits, U4 controlled public citation, U5 teaching/derivative reuse, U6 source-bound use, U7 advisory decision support, U8 release-warranted reliance, or U9 unsafe to cite.

## Revision-integration note: stewardship obligations and accountability

`rev0153` adds `159-stewardship-obligations-delegated-authority-and-accountability-governance.md`. Calibration entries that travel publicly should record stewardship status when responsibility is diagnostic: attribution-only, warning-preservation, update-watch, dispute-routing, correction/migration, domain-responsibility, or entrusted-steward duty.


## Revision-integration note: continuity registers after stewardship

`rev0154` adds `160-operational-registers-watch-queues-and-continuity-memory-governance.md`. Future uses of this file should distinguish a duty, status, packet, or verdict that is conceptually stated from one that is operationally registered. When a routed verdict, stress test, ledger case, propagation debt, terminology entry, commitment status, application dossier, precedent packet, transmission packet, reception event, release packet, lineage packet, provenance packet, review packet, public-reliance packet, or stewardship packet creates an ongoing watch, notice, correction, migration, source-refresh, derivative-maintenance, or successor duty, route the operational memory through `160`.

## Revision-integration note: validation harnesses after continuity registers

`rev0155` adds `161-validation-harness-invariant-checks-and-machine-readable-governance.md`. Future uses of this file should distinguish a rule, verdict, packet, register, or duty that is merely stated from one whose fields and invariants have actually been checked. Validation can confirm package identity, file continuity, manifest integrity, packet presence, local schema shape, and declared exceptions; it does not by itself certify metaphysical truth, source currency, public reliance, domain authority, independent review, or operational monitoring.

## Revision integration note: rev0156 workflow governance

`rev0156` adds `162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` and local workflow artifacts after the validation layer. This file should now treat workflow-control claims as downstream of its own verdicts: a routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, and validation-checked item still needs a runbook stage trace before it is described as workflow-controlled, handoff-ready, or repeatably produced. Local workflow records do not create independent review, public CI, public issue tracking, source currency, or philosophical authority.

## Revision integration note: rev0157 automation-boundary governance

`rev0157` adds `163-automation-boundaries-agent-delegation-scheduled-execution-and-tool-permission-governance.md` plus local automation-boundary artifacts after workflow governance. This file should now treat automation, tool assistance, generated drafts, scheduled checks, validators, packaging commands, search tools, and delegated agents as bounded execution aids rather than sources of authority. A routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, and workflow-traced item still needs automation status, tool-permission class, scheduled-execution class, authorized scope, human-review gate, evidence record, allowed claim language, forbidden claim language, and stop triggers before it is described as automated, monitored, source-current, independently re-executed, or tool-certified. Local tool use does not create public CI, source-watch automation, external audit, independent review, domain authority, or philosophical truth.

## Rev0158 integration note: semantic fidelity after automation

`164-semantic-fidelity-generated-output-audit-and-warning-retention-governance.md` adds the next control layer after automation. This file should now be read with the following boundary in mind: an output may be routed, stress-tested, registered, validated, workflow-executed, and automation-bounded while still failing to preserve target, basis, status, warning, non-verdict, source, version, or public-use limits. When a result is summarized, diagrammed, taught, generated, excerpted, migrated, or handed off, route the transfer through `164` before calling it faithful, teaching-safe, derivative-ready, source-preserving, or public-use appropriate.


## Rev0159 integration note: operational reliance after semantic fidelity

`165-operational-reliance-deployment-boundaries-and-action-use-governance.md` adds the next control layer after semantic fidelity. This file should now be read with the following boundary in mind: a result may be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, and semantically faithful while still being unauthorized for action. When archive material is proposed as policy, procedure, classifier, recommendation, decision support, automated trigger, institutional workflow, teaching practice, public guidance, or high-stakes domain advice, route the use through `165` before calling it operationally permitted.

## Rev0160 integration note: incident response after deployment

`166-incident-response-harm-review-near-miss-and-recovery-governance.md` adds the next control layer after deployment-boundary governance. This file should now be read with the following boundary in mind: a result may be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, and deployment-classified while still producing an incident, near miss, warning failure, unauthorized escalation, evidence-loss risk, rollback failure, derivative misuse, public reliance failure, or domain-sensitive recovery debt. When something goes wrong after action-use or attempted action-use, route the event through `166` before calling it ordinary feedback, ordinary errata, closed recovery, harmless misuse, or solved rollback.


## Rev0161 integration note: post-incident learning after incident response

`167-post-incident-learning-root-cause-capa-and-recurrence-risk-governance.md` adds the next control layer after incident response. This file should now be read with the following boundary in mind: an event can be routed, stress-tested, ledgered, propagated, terminology-safe, status-assigned, dossiered, reusable, transmissible, reception-audited, release-gated, lineage-recorded, provenance-audited, review-warranted, public-use-governed, stewarded, continuity-registered, validation-checked, workflow-traced, automation-bounded, semantically faithful, deployment-classified, and incident-recovered while still being unlearned. When a recovered incident, near miss, warning failure, deployment-boundary failure, derivative misuse, validation misclaim, or recovery dispute may recur, route it through `167` before calling the pattern fixed, prevented, verified, or safe to forget.

## Rev0162 integration note

`rev0162` adds `168-longitudinal-monitoring-effectiveness-review-sunset-and-residual-risk-governance.md`. This does not replace this protocol. It adds a later check on whether controls, warnings, review duties, release gates, deployment limits, incident lessons, or post-incident preventive actions remain effective across future releases and uses. Any result produced by this file that is meant to persist, travel, govern derivatives, guide operational use, or close a recurrence risk should now be eligible for a `168` monitoring packet stating monitoring status, effectiveness class, residual-risk trend, review trigger, and sunset/renewal condition.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
