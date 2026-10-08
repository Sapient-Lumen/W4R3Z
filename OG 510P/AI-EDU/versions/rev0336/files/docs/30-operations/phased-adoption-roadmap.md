# Phased adoption roadmap

## rev0228 maintenance lane: contract canonical surface metadata

Before a canonical row in `SURFACES.json` is used for first-read navigation, release audit, registry lookup, or priority curation, check whether it should be governed by `CUBE_SURFACE_CONTRACTS.json`. Contracted rows must keep expected type, lifecycle, owner, authority, portability, evidence markers, and forbidden tags stable. This is maintenance discipline, not evidence. It keeps the cube navigable while `FT-0181` waits for real `SRC2+` pilot evidence.

Key surfaces: [`../00-meta/surface-contracts-and-metadata-drift-audit.md`](../00-meta/surface-contracts-and-metadata-drift-audit.md), [`../00-meta/cube-refactor-audit-rev0228.md`](../00-meta/cube-refactor-audit-rev0228.md), and [`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md).

## rev0227 maintenance lane: register schemas before trusting JSON

Before a new schema, JSON example, root structured control, or structured-artifact validator can support a release claim, it must be registered in `CUBE_SCHEMA_REGISTRY.json` and pass `check_schema_registry.py`. This is maintenance discipline, not evidence. It keeps examples and control records auditable while `FT-0181` waits for real `SRC2+` pilot evidence.

Key surfaces: [`../00-meta/schema-registry-and-json-plane-refactor.md`](../00-meta/schema-registry-and-json-plane-refactor.md), [`../00-meta/cube-refactor-audit-rev0227.md`](../00-meta/cube-refactor-audit-rev0227.md), and [`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md).

## rev0226 maintenance lane: register tools before trusting them

Before a new validator, generator, or utility script can support a release claim, it must be registered in `CUBE_TOOLCHAIN_REGISTRY.json` and pass `check_toolchain_registry.py`. This is maintenance discipline, not evidence. It keeps release controls auditable while `FT-0181` waits for real `SRC2+` pilot evidence.

Key surfaces: [`../00-meta/toolchain-registry-and-lint-plane-refactor.md`](../00-meta/toolchain-registry-and-lint-plane-refactor.md), [`../00-meta/cube-refactor-audit-rev0226.md`](../00-meta/cube-refactor-audit-rev0226.md), and [`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md).

## rev0224 maintenance lane: navigate before adding

Before any new pilot, branch, or release-control surface, use the re-entry navigation map and surface map to check whether the cube already has a governing path. This maintenance lane is especially important while `FT-0181` waits on real `SRC2+` pilot evidence: pre-import controls are saturated, so navigation refactor is allowed but new gates require a named uncovered risk.

Key surfaces: [`../00-meta/reentry-navigation-map.md`](../00-meta/reentry-navigation-map.md), [`../00-meta/cube-refactor-audit-rev0224.md`](../00-meta/cube-refactor-audit-rev0224.md), and [`control-saturation-and-no-new-control-rule.md`](control-saturation-and-no-new-control-rule.md).

## rev0223 maintenance-mode gate

Before adding another release-control artifact around `FT-0181`, pass the control-saturation admission test. If no material uncovered risk is named, keep the archive in maintenance mode, refresh stale evidence and release records, request real `SRC2+` pilot data, and keep public claims within the claim lexicon.

Use [`control-saturation-and-no-new-control-rule.md`](control-saturation-and-no-new-control-rule.md), [`release-candidate-maintenance-mode-and-stale-gate-policy.md`](release-candidate-maintenance-mode-and-stale-gate-policy.md), [`real-evidence-chain-of-custody-and-redaction-workbench.md`](real-evidence-chain-of-custody-and-redaction-workbench.md), and [`public-claim-lexicon-and-forbidden-phrases.md`](public-claim-lexicon-and-forbidden-phrases.md).


## rev0220 maintenance gate

Before any pilot moves from example-backed readiness to real-evidence import, pass the release audit,
synthetic-example declaration, policy-exception, and assurance-case checks. These are preconditions for
trustworthy handoff, not substitutes for `SRC2+` source data.

## rev0219 maintenance gate

Before a program treats a pilot as recurring infrastructure, it should now produce an operator
handoff, a lifecycle decision, and, where real pilot records are imported, closeout-board minutes.
This is not extra paperwork for its own sake. It protects the archive from three late-stage errors:
claims staying public after evidence expiry, real-import gates closing through status drift, and
conflicted reviewers turning implementation convenience into learning evidence.

Use [`operator-handoff-and-maintainer-runbook.md`](operator-handoff-and-maintainer-runbook.md),
[`service-lifecycle-deprecation-and-archive-exit-rules.md`](service-lifecycle-deprecation-and-archive-exit-rules.md),
[`../20-governance/evaluator-independence-and-evidence-contamination-controls.md`](../20-governance/evaluator-independence-and-evidence-contamination-controls.md),
and [`real-import-closeout-board-and-decision-minutes.md`](real-import-closeout-board-and-decision-minutes.md)
before claiming a field import changed the archive's evidence status.


The archive's rollout rule is simple: **sequence matters**. Deploying AI before literacy, proof,
fallback, and governance produces cheating panic, brittle policy, hidden labor, and weak learning
evidence.



## Rev0215 publication, adapter, and import posture

Before any recurring service publishes a learner, family, teacher, partner, vendor, or public-route
notice, render the service record through a redaction profile and apply every triggered sector
adapter. Before any real pilot export enters the archive, stage it through the import workflow and
mark the source truth class. A valid service record is no longer enough if the audience, sector, and
source provenance are unclear.

Core surfaces:
[`public-summary-redaction-profiles.md`](public-summary-redaction-profiles.md),
[`sector-adapters-for-service-record-schema.md`](sector-adapters-for-service-record-schema.md),
[`real-pilot-record-import-and-normalization-workflow.md`](real-pilot-record-import-and-normalization-workflow.md),
and [`machine-readable-service-record-schema-and-validator.md`](machine-readable-service-record-schema-and-validator.md).

## Rev0213 operating posture

Before adding another exception branch, classify the proposed change in
[`../00-meta/datacube-schema.md`](../00-meta/datacube-schema.md) and
[`../00-meta/surface-map-overview.md`](../00-meta/surface-map-overview.md). If the case is another
recurrence of a watched / repaired / dewatched pattern, use
[`../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md)
instead of minting a new ordinary shell.

Recurring, integrated, learner-facing, record-adjacent, or action-taking services should also
complete the service-BOM and decision-record route in
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md)
and
[`ai-service-intake-and-decision-record-template.md`](ai-service-intake-and-decision-record-template.md).
Tool-enabled services must pass the security / red-team posture in
[`../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md`](../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md).
Claims must be graded through
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md)
and
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md).
Recurring services should move through
[`ai-implementation-review-cycle-and-stop-rules.md`](ai-implementation-review-cycle-and-stop-rules.md),
[`ai-pilot-packet-and-filled-examples.md`](ai-pilot-packet-and-filled-examples.md), and
[`service-record-backtest-results-and-field-trim.md`](service-record-backtest-results-and-field-trim.md),
[`import-readiness-manifest-and-no-real-data-gate.md`](import-readiness-manifest-and-no-real-data-gate.md),
[`pilot-source-data-dictionary-template.md`](pilot-source-data-dictionary-template.md),
[`real-import-acceptance-tests-and-reviewer-calibration.md`](real-import-acceptance-tests-and-reviewer-calibration.md),
[`minimum-real-data-request-packet.md`](minimum-real-data-request-packet.md),
[`import-negative-fixtures-and-failure-mode-catalog.md`](import-negative-fixtures-and-failure-mode-catalog.md),
[`decision-delta-log-template-and-field-pruning-rules.md`](decision-delta-log-template-and-field-pruning-rules.md),
[`release-candidate-state-and-open-item-freeze.md`](release-candidate-state-and-open-item-freeze.md), and
[`public-summary-render-smoke-tests.md`](public-summary-render-smoke-tests.md)
rather than jumping from demo to scale. Repeated starter-profile questions should use
[`../20-governance/profile-hardening-application-rows.md`](../20-governance/profile-hardening-application-rows.md),
and accumulated drift should use
[`../20-governance/micro-change-cluster-reset-and-change-budget-defaults.md`](../20-governance/micro-change-cluster-reset-and-change-budget-defaults.md).

## Phase 0 — Readiness

No broad deployment until the institution can answer these questions:

- What is the use case, actor, stakes level, memory state, proof state, action authority, lifecycle
  stage, and named owner?
- What student work is the construct, and what AI use is allowed, disclosed, or prohibited? Use
  [`../40-assessment/construct-map-and-ai-use-disclosure-matrix.md`](../40-assessment/construct-map-and-ai-use-disclosure-matrix.md)
  before assignment-level language hardens.
- What records are created, retained, shown, challenged, minimized, or deleted?
- What human coverage exists during live service windows, especially for minors, credit,
  professional gatekeeping, benefits-linked public routes, and accommodation routes?
- What happens when the AI is wrong, unavailable, compromised, changed, or unable to finish the
  handoff?
- What evidence grade and claim family would promote, pause, demote, or retire the service?
- If a real pilot record will be imported later, what minimum data request, source dictionary, import
  map, acceptance packet, negative fixture, and redaction route will distinguish evidence from examples?

Core setup surfaces:
[`teacher-capability-bands-and-service-readiness.md`](teacher-capability-bands-and-service-readiness.md),
[`human-coverage-bands-and-no-orphan-handoffs.md`](human-coverage-bands-and-no-orphan-handoffs.md),
[`../20-governance/evidence-and-procurement.md`](../20-governance/evidence-and-procurement.md),
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`../20-governance/pilot-to-scale-evidence-and-rollout-gates.md`](../20-governance/pilot-to-scale-evidence-and-rollout-gates.md),
and
[`../20-governance/failure-escalation-safe-degradation-and-manual-fallback.md`](../20-governance/failure-escalation-safe-degradation-and-manual-fallback.md).

## Phase 1 — Teacher productivity and teacher minimum

Start with staff-facing uses where the upside is visible and the risk can stay bounded:

- planning and materials drafting;
- translation, accessibility drafting, and format adaptation;
- feedback drafting under teacher review;
- administrative compression;
- teacher AI fluency and critique.

This phase is not a blank cheque for delegation. Publish which services require `TC1`, `TC2`, or
`TC3-TC4`; which require `HC0-HC4`; and which functions may only advise, draft, queue, or require
human sign-off. See
[`teacher-capability-bands-and-service-readiness.md`](teacher-capability-bands-and-service-readiness.md),
[`human-coverage-bands-and-no-orphan-handoffs.md`](human-coverage-bands-and-no-orphan-handoffs.md),
and
[`../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md).

## Phase 2 — Student-facing support under construct control

Student-facing AI should be introduced as learning support, not completion infrastructure. Each use
case must state:

- the cognitive-effort budget (`CE0-CE5`);
- whether the AI gives hints, diagnosis, examples, comparison, or production help;
- what disclosure is required;
- what proof shifts when AI production is allowed;
- where handoff to a teacher, counselor, accommodation route, or human office is required.

Core surfaces:
[`../20-governance/student-facing-function-deployment-defaults-and-handoff-triggers.md`](../20-governance/student-facing-function-deployment-defaults-and-handoff-triggers.md),
[`../20-governance/sector-and-age-profile-splits-for-student-facing-defaults.md`](../20-governance/sector-and-age-profile-splits-for-student-facing-defaults.md),
[`../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md`](../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md),
and
[`../20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md`](../20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md).

## Phase 3 — Assessment redesign and proof of learning

Move from artifact policing to proof architecture. Courses and programs should decide which
combinations of unaided work, checkpoints, process records, oral defense, live transfer, portfolios,
and exam conditions actually prove the construct.

Core surfaces:
[`../40-assessment/construct-map-and-ai-use-disclosure-matrix.md`](../40-assessment/construct-map-and-ai-use-disclosure-matrix.md),
[`../40-assessment/authentic-assessment-and-proof-of-learning.md`](../40-assessment/authentic-assessment-and-proof-of-learning.md),
[`../40-assessment/proof-of-learning-bundles.md`](../40-assessment/proof-of-learning-bundles.md),
[`../40-assessment/subject-family-proof-intensity-defaults.md`](../40-assessment/subject-family-proof-intensity-defaults.md),
and
[`../40-assessment/sector-and-age-profile-splits-for-proof-intensity-defaults.md`](../40-assessment/sector-and-age-profile-splits-for-proof-intensity-defaults.md).

## Phase 4 — Institutional systems and action authority

Institution-facing systems can create hidden harm because they shape records, eligibility, routing,
warnings, and communications. Each system needs a published action-authority ceiling:

- read-only suggestion;
- draft for review;
- queue or recommend;
- reversible low-stakes action;
- record-bearing or consequence-bearing action under special sign-off;
- human-only / prohibited.

Core surfaces:
[`../20-governance/ai-action-authority-register-and-delegation-ceilings.md`](../20-governance/ai-action-authority-register-and-delegation-ceilings.md),
[`../20-governance/sector-and-office-profile-splits-for-institution-facing-defaults.md`](../20-governance/sector-and-office-profile-splits-for-institution-facing-defaults.md),
[`../20-governance/minimum-observability-and-retention-without-surveillance.md`](../20-governance/minimum-observability-and-retention-without-surveillance.md),
and
[`../20-governance/model-and-workflow-change-classification-and-fresh-review-triggers.md`](../20-governance/model-and-workflow-change-classification-and-fresh-review-triggers.md).

## Phase 5 — Scale, evaluation, and retirement

A service should not scale because people like it. It should scale only when there is enough
evidence for the stakes, enough coverage for the service truth, enough security for the workflow,
and enough contestability for affected learners and staff.

Keep a live review date, rollback owner, material-change trigger, and retirement rule. Retire or
demote tools that do not improve learning, increase hidden labor, create dependency without
understanding, weaken accessibility, or require stronger surveillance than the learning value
justifies. Do not treat `SRC0` examples, `SRC1` templates, source dictionaries, or import maps as
real pilot evidence during scale review; require a minimum real-data request packet, acceptance packet,
negative fixture pass, render smoke test, and decision-delta log for `FT-0181` closure.

Core surfaces:
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`ai-implementation-review-cycle-and-stop-rules.md`](ai-implementation-review-cycle-and-stop-rules.md),
[`../20-governance/pilot-to-scale-evidence-and-rollout-gates.md`](../20-governance/pilot-to-scale-evidence-and-rollout-gates.md),
[`../20-governance/sector-and-function-profile-splits-for-rollout-gates.md`](../20-governance/sector-and-function-profile-splits-for-rollout-gates.md),
[`../20-governance/evidence-and-procurement.md`](../20-governance/evidence-and-procurement.md),
[`../20-governance/external-evidence-watchlist-and-source-triage.md`](../20-governance/external-evidence-watchlist-and-source-triage.md), and
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md).

## Cross-cutting public route

The formal school/course rollout is not the whole system. Adult learners, workers, community
learners, older learners, and residents outside enrollment need public entry points, warm transfer,
learner-controlled portability, and recognition-before-duplication rules. Keep public-route claims
narrow: broad enough to avoid needless restart, but not broad enough to expose protected support
records or invent false equivalence.

Core surfaces: [`lifelong-public-ai-learning-stack.md`](lifelong-public-ai-learning-stack.md),
[`minimum-public-entitlement-and-handoff-standard.md`](minimum-public-entitlement-and-handoff-standard.md),
[`portable-public-learning-packet-and-recognition-profile.md`](portable-public-learning-packet-and-recognition-profile.md),
[`standing-equivalency-lists-and-review-governance.md`](standing-equivalency-lists-and-review-governance.md),
and
[`in-flight-teach-out-and-substitute-equivalent-rules.md`](in-flight-teach-out-and-substitute-equivalent-rules.md).

## Compact warning

Do not adopt AI for convenience first and invent learning proof later. That sequence is the main
institutional failure mode.


## Release-candidate hardening gate

Before a real pilot import closes `FT-0181`, run the release-candidate hardening gate:
invariant record, dependency graph, release delta, recovery drills, closure checklist, release
audit, synthetic-example declaration, policy-exception register, assurance case, control
coverage, evidence-refresh calendar, and signoff quorum. Passing this gate means the archive is
ready to evaluate real evidence. It does not mean the evidence exists.



## Rev0225 maintenance insertion: branch-history scan before expansion

During maintenance phases, scan [`../00-meta/branch-family-index-and-refactor-map.md`](../00-meta/branch-family-index-and-refactor-map.md) before adding branch-history surfaces. If the requested case belongs to an existing family, prefer an applied row, compression note, or terminal disposition over another sibling shell.
