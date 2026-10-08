# Validation Harness, Invariant Checks, and Machine-Readable Governance

## Why this file exists

`160-operational-registers-watch-queues-and-continuity-memory-governance.md` prevents accepted duties from dissolving into forgotten prose. It asks where a release packet, source-watch duty, review expiry, public-use limit, correction notice, derivative-maintenance obligation, fork declaration, withdrawal rule, or successor-memory field is recorded, what wakes it up, who is notified, what closes it, and what a successor inherits.

That is necessary, but it leaves a further failure mode. A register can exist and still be unreliable. Its fields can be incomplete. Its status vocabulary can drift. A YAML file can use one class while the prose uses another. A release note can claim validation even though no expected invariant was checked. A validation script can test only file presence while its summary sounds like conceptual review. A dashboard can be current in shape but stale in substance. A machine-readable register can become a new prestige object: tidy enough to cite, but not strong enough to warrant the authority being claimed for it.

The danger is **unchecked formalization**: once duties become tables, schemas, scripts, checklists, or dashboards, their neatness can be mistaken for truth, review, public infrastructure, or operational warranty.

This file adds a validation layer after continuity memory: **validation harnesses, invariant checks, schema discipline, local machine-readable records, validation transcripts, exception handling, and automation-boundary governance**. Its job is not to turn metaphysics into software compliance. Its job is to make formal artifacts honest about what they check, what they do not check, what failed, what was waived, what requires human review, and what claims the validation permits.

## Compressed default

The archive should now say:

> **Do not call a packet, register, release, derivative, or lineage claim validation-checked until the schema, required fields, allowed values, invariants, inputs, check mode, result, failure severity, exceptions, remediation, human-review boundary, and permitted claim language have been stated.**

In shorter form:

> **Validation is a smoke alarm, not a judge.**

And more carefully:

> **Every machine-readable or checklist-backed archive claim should state what artifact was checked, what schema or checklist governed it, which invariants were expected, which checks passed, which failed, which were not run, which exceptions were granted, what evidence supports closure, what remains open debt, what human review is still required, and what stronger claims remain forbidden.**

## Place in the control sequence

The applied governance chain now runs:

1. route the case with `144`,
2. attack the route with `145`,
3. ledger reusable hard cases with `146`,
4. propagate accepted changes with `147`,
5. audit terminology with `148`,
6. assign commitment status with `149`,
7. write an auditable dossier with `150`,
8. govern reuse, transfer, appeal, and supersession with `151`,
9. govern transmission and compression with `152`,
10. audit reception and correction pressure with `153`,
11. gate the release and ledger maintenance with `154`,
12. record lineage, compatibility, forks, and migrations with `155`,
13. record provenance, custody, build evidence, and reproducibility with `156`,
14. classify review authority, certification status, and permitted claim language with `157`,
15. assign public reliance, citation, dispute, withdrawal, and retraction rules with `158`,
16. assign stewardship obligations, delegated authority, and accountability rules with `159`,
17. register operational memory, watch queues, notice paths, closure conditions, and successor-memory fields with `160`,
18. and validate the resulting package, packets, registers, schemas, and declared exceptions with this file before claiming that the archive is machine-checkable, validation-backed, dashboard-ready, or operationally monitored.

`160` asks: **where is the duty remembered?**  
`161` asks: **can the memory be checked without inflating the check into authority?**

## Validation statuses

Use these statuses when a package, release note, register, packet, derivative artifact, fork, source-watch table, teaching registry, review ledger, public notice, or generated output claims to be checked.

### V0 — no validation claim

The artifact is prose-only, scratch, private, or historical. It may be useful, but no validation claim travels with it.

### V1 — manual checklist only

A human checked a visible checklist. The result may support local confidence, but it is not machine-readable and should not be described as automated validation.

### V2 — schema declared, not executed

A schema, template, or required-field list exists, but no check has been run. This supports preparation, not validation.

### V3 — field-completeness checked

Required fields are present and non-empty. This does not show that the values are correct, current, or conceptually sound.

### V4 — invariant-consistency checked

The artifact has been checked against declared local invariants: version alignment, file-number continuity, manifest coverage, status-class vocabulary, packet chain, citation form, or register-required fields.

### V5 — package validation transcript recorded

A release includes a validation transcript naming inputs, checks, results, failures, exceptions, remediation, open debt, and permitted claim language.

### V6 — local machine-readable register included

The archive includes a local YAML, CSV, JSON, or similar register or schema file that can be read independently of the prose. This is still archive-local unless public infrastructure exists.

### V7 — scheduled or automated watch with human review

The register is not only present but tied to a repeatable or scheduled check, with human-review boundaries and escalation rules. This requires actual operational infrastructure, not merely a future promise.

### V8 — independently reproducible validation

An independent party, environment, or rebuild has executed the validation harness and recorded a comparable result. This requires external evidence beyond this package's self-report.

### V9 — failed, unsafe, or validation-laundered artifact

The artifact failed required checks, concealed failures, overclaimed what was checked, mixed incompatible schemas, or used automation language to imply authority the checks do not warrant.

## Invariant families

A validation harness should say which invariant families it checks. Not every release needs every family, but silence should not masquerade as success.

### I1 — version identity invariants

`VERSION`, root folder, package filename, README header, release packet, lineage packet, provenance packet, public-use packet, stewardship packet, continuity packet, and validation transcript should agree or explain the discrepancy.

### I2 — file-continuity invariants

Numbered markdown documents should run continuously from `00` through the declared final file unless a deletion, deprecation, split, or skipped number is explicitly recorded.

### I3 — index and front-door invariants

`README.md`, `ARCHIVE_INDEX.md`, and `docs/00-start-here.md` should list the newly added numbered file and should not leave the principal operating method behind the archive's actual control stack.

### I4 — manifest and package invariants

Every release file except `MANIFEST.sha256` should appear in the manifest with the correct hash. Manifest validation should be run after all edits, not before.

### I5 — packet-chain invariants

A release that claims public-use, stewardship, continuity, validation, review, provenance, or lineage status should contain the corresponding packet or explicitly state that the packet is omitted.

### I6 — status-vocabulary invariants

Classes such as A, L, P, C, U, O, K, V, I, and severity levels should be used in their proper file-specific senses. Reusing a letter-class from another file requires an explicit namespace.

### I7 — source-boundary invariants

If no new external source anchors were added, `05-source-citations.md` should say so. If a claim depends on current law, science, medicine, engineering, policy, institutional practice, repository state, or public infrastructure, a source-watch or source-refresh rule should be recorded.

### I8 — public-claim invariants

No validation result should claim public registry status, independent certification, external peer review, domain authority, public issue-tracker operation, maintained derivative monitoring, or operational warranty unless the evidence exists.

### I9 — exception and waiver invariants

Skipped checks, waived fields, non-fatal failures, known omissions, or open debts should be named. A validation transcript that hides exceptions is worse than no transcript.

### I10 — automation-boundary invariants

A script, schema, lint rule, or dashboard can check structure, fields, hashes, vocabulary, and declared dependencies. It cannot by itself decide metaphysical truth, source accuracy, domain applicability, independent review, or public reliance.

## Validation record schema

A validation record should minimally include:

- **Validation ID**
- **Artifact checked**
- **Version identity**
- **Schema or checklist used**
- **Validation status**
- **Check mode** — manual, scripted, mixed, scheduled, independent, or not run
- **Inputs inspected**
- **Invariant families checked**
- **Checks passed**
- **Checks failed**
- **Checks not run**
- **Failure severity**
- **Exceptions or waivers**
- **Human-review boundary**
- **Remediation action**
- **Closure evidence**
- **Allowed claim language**
- **Forbidden claim language**
- **Next validation trigger**
- **Open validation debt**

This schema may be stored as prose, YAML, JSON, CSV, a database row, a release transcript, or a public dashboard. The storage form does not change the warrant. The warrant comes from what was actually checked and what the result permits.

## Failure severities

Use these severities when a validation check fails.

### S0 — observation only

The check found a fact worth recording but not a defect.

### S1 — local warning

A minor mismatch, unclear label, or non-blocking omission exists. Repair is recommended, but release is not blocked.

### S2 — repair before public summary

The package may remain locally usable, but public summaries or derivative artifacts should not rely on the affected claim until repaired.

### S3 — repair before release

The defect should block a clean release: missing version alignment, missing index entry, incomplete packet, unlisted file, or stale source note.

### S4 — release hold

The release should not be treated as current until the defect is resolved or explicitly downgraded to release-with-declared-debt under `154`.

### S5 — quarantine

The affected file, packet, register, derivative, fork, or source-bound use should be quarantined until rerouted, redossiered, source-refreshed, or rebuilt.

### S6 — rollback / withdrawal / retraction trigger

The failure threatens package identity, public-use status, source-bound claim, review warrant, lineage relation, or operational reliance strongly enough to trigger `154`, `155`, `158`, or `160`.

### S7 — unsafe validation claim

The validation claim itself is misleading: automation, schema, or manifest language has been used to imply authority not actually supported. Correct public wording before further reuse.

## What a validation harness may check

A local validation harness may responsibly check:

- whether `VERSION`, package name, root folder, and new file range align,
- whether numbered docs are continuous,
- whether README, archive index, and `00` include the final numbered file,
- whether `MANIFEST.sha256` covers all non-manifest files and hashes match,
- whether required control packets are present for the current release,
- whether a local validation transcript exists when validation is claimed,
- whether local YAML or CSV registers use declared top-level fields,
- whether source-neutral revisions explicitly say no new external anchors were added,
- whether forbidden public-infrastructure claims appear without infrastructure evidence,
- and whether validation failures, skipped checks, and open debts are visible.

A local validation harness should not claim to check:

- whether the metaphysical theory is true,
- whether a source-dependent claim is current without source refresh,
- whether a domain-bound use is legally, medically, clinically, engineering-wise, financially, or policy-wise appropriate,
- whether a review is independent unless independent-review evidence exists,
- whether public reliance is warranted beyond the public-use packet,
- whether a fork is safe merely because it shares filenames,
- or whether a generated summary preserved meaning unless a human or scoped reviewer inspected the output.

## Automation-boundary rules

### Rule 1: No script promotes doctrine

A script can detect missing files, broken hashes, stale version strings, absent packets, malformed records, and forbidden claim phrases. It cannot promote a distinction, defeat a rival, certify a source interpretation, or settle an application dossier.

### Rule 2: Field completeness is not correctness

A filled packet can still be wrong. Completeness checking supports review; it is not review.

### Rule 3: Local machine-readable is not public operational

A YAML file inside a ZIP is discoverable local structure. It is not a public issue tracker, maintained dashboard, derivative registry, source-watch service, or notice system.

### Rule 4: Repeatability needs inputs

A validation result should name the artifact, version, script or checklist, inputs, expected invariants, and output. Otherwise later users cannot distinguish an actual check from a remembered impression.

### Rule 5: Exceptions must be first-class

A skipped check, unimplemented validator, missing source watch, or open infrastructure debt should appear as a named exception, not a silent absence.

### Rule 6: Human review remains scoped

Human review may inspect what the script cannot: conceptual fit, over-compression, source use, terminology laundering, public-use risk, and high-stakes overreach. That review also needs scope and allowed claim language under `157`.

## Local artifacts introduced with this revision

`rev0155` introduces three archive-local validation artifacts:

1. `REGISTERS/README.md` — explains that the included registers are local package records, not public infrastructure.
2. `REGISTERS/schemas/validation-record-v1.yml` — records the local schema fields and allowed validation concepts for this revision.
3. `REGISTERS/rev0155-release-validation.yml` — records the validation transcript for this release.
4. `tools/validate_archive.py` — provides a minimal local validation harness for package identity, numbered-doc continuity, index/front-door inclusion, and manifest integrity.

These artifacts move the archive from V1/V2 prose-check discipline toward V5/V6 local validation. They do not create V7 public scheduled monitoring, V8 independent reproducibility, or any external certification.

## Validation anti-patterns

### Manifest absolutism

A package has a valid manifest, so it is treated as reviewed, source-accurate, current, or philosophically sound. Fix: manifest validation is I4 only.

### YAML prestige

A field appears in YAML, so it is treated as stronger than the prose. Fix: compare storage form to scope; a machine-readable field may still be wrong, stale, or unsupported.

### Dashboard fiction

A file calls itself a registry, queue, or watch, but no person, trigger, schedule, public notice path, or closure evidence exists. Fix: lower the K/V status and state open debt.

### Hidden exception

A skipped check is omitted from the transcript. Fix: list checks not run, waivers, and open validation debt.

### Script overreach

The validation script reports pass, and the release note says the archive has been certified. Fix: allowed claim language should name only what the script checked.

### Stale schema lock-in

A schema created for one revision blocks a necessary future conceptual correction because old fields are treated as doctrine. Fix: schemas are tools under `147`, not immutable metaphysics.

### Fork validation laundering

A fork passes local file checks and then claims compatibility with the main archive. Fix: file validation does not replace lineage/fork compatibility under `155`.

### Public-infrastructure laundering

A local register inside a ZIP is cited as a public issue tracker, public registry, or maintained notice system. Fix: require actual public infrastructure or state K2/V6 local-only.

## Validation worksheet

Before claiming that a release, packet, register, derivative, fork, or public artifact is validation-backed, answer:

1. What exact artifact was validated?
2. Which version, package, root folder, and file range are claimed?
3. Which schema, checklist, script, or invariant set governed the check?
4. Which invariant families were checked?
5. Which checks passed?
6. Which checks failed?
7. Which checks were not run?
8. Which failures are release-blocking, warning-level, quarantine-level, or rollback-level?
9. Which exceptions or waivers were granted?
10. What evidence closes the check?
11. What still requires human review?
12. What claim language is allowed?
13. What claim language is forbidden?
14. What next trigger should rerun validation?
15. What validation debt remains?

## Future expansion rule

Do not add another validation-governance file merely because more checks can be imagined. Add or revise infrastructure only when the archive needs an actual schema, script, register, public validation transcript, source-watch integration, derivative registry, issue queue, independent rebuild path, or external audit record that cannot be represented by this file.

Likely future work should be practical rather than merely conceptual:

- expand `tools/validate_archive.py` into a full package auditor,
- add JSON Schema or stricter YAML validation for registers,
- add a release-packet extractor,
- add a source-watch register for source-dependent revisions,
- add citation templates that preserve version/status/warning fields,
- add a public errata queue if the archive becomes publicly maintained,
- or add an independent rebuild transcript if external reproducibility is claimed.

## Relationship to workflow governance

`162-release-workflow-runbooks-execution-traces-and-handoff-governance.md` does not replace this validation layer. It places validation inside a release workflow. A validation transcript says what was checked, what failed, what was skipped, what was waived, and what claim language the check permits. A workflow trace says when that validation occurred, what stages came before and after, whether the manifest was regenerated after final edits, whether the ZIP passed fresh-extraction validation, and what handoff limits a successor receives.

A release should not use a workflow trace to inflate validation, and it should not use a validation pass to imply a complete workflow. The safe claim is conjunctive and narrow: **local validation passed inside a recorded local workflow**, not external certification, public CI, independent review, source authority, or proof of metaphysical truth.

## Initial validation packet for this revision

**Validation ID:** VP-rev0155-001  
**Artifact checked:** `rev0155`, package `Metaphysics-rev0155-2026.05.18.23.58-validationharness-invariantchecks.zip`; new `161` validation-harness / invariant-check / machine-readable governance layer plus local `REGISTERS/` artifacts and `tools/validate_archive.py`.  
**Version identity:** root folder `metaphysics_rev0155`; `VERSION` states `rev0155`; numbered docs run through `161`.  
**Schema or checklist used:** `REGISTERS/schemas/validation-record-v1.yml` plus local package checks in `tools/validate_archive.py`.  
**Validation status:** V5 package validation transcript recorded plus V6 local machine-readable register included; not V7 public scheduled watch and not V8 independently reproducible validation.  
**Check mode:** mixed manual and local scripted self-check.  
**Inputs inspected:** predecessor `rev0154` package, edited markdown files, new local register files, validation script, archive index, README, `00`, `VERSION`, and regenerated manifest.  
**Invariant families checked:** I1 version identity, I2 file continuity, I3 index/front-door inclusion, I4 manifest and package integrity, I5 packet-chain presence, I7 source-boundary note, I8 public-claim limits, and I10 automation-boundary warning.  
**Checks passed:** version alignment, docs continuity from `00` through `161`, README inclusion, archive-index inclusion, `00` inclusion, local validation transcript inclusion, manifest regeneration, and fresh-extraction validation.  
**Checks failed:** no release-blocking failures after repair.  
**Checks not run:** independent external rebuild, external philosophical review, source-domain review, public issue tracker check, public derivative registry check, scheduled watch automation, and full semantic validation of every first-order operator file.  
**Failure severity:** S0 after repair; inherited stale README revision note from `rev0154` was repaired before packaging.  
**Exceptions or waivers:** no public infrastructure is claimed; no independent review is claimed; the local YAML schema is not a formal external standard.  
**Human-review boundary:** package-structure validation and local schema validation support release hygiene only; conceptual, source-bound, domain-bound, public-use, and high-stakes claims still require the earlier control files and appropriate human review.  
**Remediation action:** added `161`, added local `REGISTERS/` records, added validation script, repaired README revision-note drift, updated front door/synthesis/method/frontier/source/control files, and regenerated manifest.  
**Closure evidence:** package-level manifest validation and clean fresh-extraction check.  
**Allowed claim language:** “manifest-verified,” “fresh-extraction checked,” “local validation transcript included,” “minimal local validation harness included,” and “validation-governance layer added.”  
**Forbidden claim language:** “externally certified,” “independently validated,” “public registry verified,” “automatically philosophically reviewed,” “source-current by automation,” “domain-authorized,” “operationally warranted,” or “public monitoring service active.”  
**Next validation trigger:** future release, new register family, changed schema, source-dependent update, fork import, public-infrastructure claim, independent-review claim, failed manifest, or validation dispute.  
**Open validation debt:** no public repository, public issue tracker, public continuity dashboard, maintained derivative registry, source-watch automation, independent rebuild transcript, external audit record, or full semantic validator is included.

## Closing formulation

A mature archive should not only remember its duties; it should be able to check whether the memory is structurally present, internally consistent, and honestly described. But the check must remain modest. Validation is a way of resisting drift, not a way of outsourcing judgment.

Validation governance is the archive's resistance to false authority by formal neatness.

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

## Rev0162 validation packet note

**Validation update:** `tools/validate_archive.py` now requires `RUNBOOKS/effectiveness-monitoring-review-v1.md`, `REGISTERS/schemas/effectiveness-monitoring-record-v1.yml`, and current-version `REGISTERS/{version}-effectiveness-monitoring.yml` for packages whose numbered docs reach `168+`.  
**Validation boundary:** this only checks expected local artifact presence, front-door/index references, numbered-doc continuity, and manifest integrity. It does not prove effectiveness, active monitoring, source freshness, sunset safety, or domain compliance.

## Revision-integration note: risk portfolio governance

`169-cross-case-risk-portfolio-systemic-exposure-and-prioritization-governance.md` adds a control above single-record review. This file's verdicts, packets, registers, duties, warnings, release gates, review claims, public-use permissions, deployment boundaries, incidents, learning controls, or monitoring items should not be treated as collectively manageable merely because they are locally acceptable one by one. When several such items accumulate, future revisions should use `169` to classify portfolio status, exposure aggregation, correlation/common-cause class, cumulative burden, priority/treatment class, accepted residual risks, blocked or escalated items, allowed wording, forbidden wording, and next review trigger.

## Rev0164 capacity-allocation update

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` adds a layer after portfolio prioritization. Any result from this file that becomes a priority item, release debt, source-refresh need, public-use restriction, derivative duty, deployment-boundary review, incident lesson, monitoring trigger, validation gap, or stewardship obligation should not be described as assigned, scheduled, manageable, monitored, safe to defer, or handled until a capacity packet states CAP/BL/WIP/DEF classes, resource basis, scarce dependency, owner or declined responsibility, next action, WIP limit, stop condition, allowed wording, forbidden wording, and open capacity debt.
