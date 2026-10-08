# Trajectory map

## rev0227 movement: schema registry and JSON-plane refactor

The archive now treats the JSON/schema plane as a governed cube surface. rev0227 adds `CUBE_SCHEMA_REGISTRY.json`, a schema-registry schema, registry coverage lint, and a row-local diagnostic fix in the toolchain checker. This keeps schemas, examples, root structured controls, validators, and doc surfaces aligned without importing real pilot evidence or changing the `FT-0181` closure rule.

Key surfaces: [`schema-registry-and-json-plane-refactor.md`](schema-registry-and-json-plane-refactor.md), [`cube-refactor-audit-rev0227.md`](cube-refactor-audit-rev0227.md), and [`../../CUBE_SCHEMA_REGISTRY.json`](../../CUBE_SCHEMA_REGISTRY.json).

## rev0226 movement: toolchain registry and lint-plane refactor

The archive now treats the lint/toolchain plane as a governed cube surface. rev0226 adds `CUBE_TOOLCHAIN_REGISTRY.json`, a toolchain-registry schema, registry coverage lint, and a runner that reads the registry instead of carrying a hardcoded validator list. This keeps future validators, generators, and utility scripts discoverable without adding real pilot evidence or changing the `FT-0181` closure rule.

Key surfaces: [`toolchain-registry-and-lint-plane-refactor.md`](toolchain-registry-and-lint-plane-refactor.md), [`cube-refactor-audit-rev0226.md`](cube-refactor-audit-rev0226.md), and [`../../CUBE_TOOLCHAIN_REGISTRY.json`](../../CUBE_TOOLCHAIN_REGISTRY.json).

## rev0225 movement: branch-family refactor without path churn

The archive now treats the branch-history tail as an indexed family archive instead of a first-read governance spine. rev0225 adds a generated branch-family index, a human refactor map, branch-family lint, and surface-map tagging for `branch_archive` rows. It does not move historical files and does not add a new `FT-0181` control.

Key surfaces: [`branch-family-index-and-refactor-map.md`](branch-family-index-and-refactor-map.md), [`cube-refactor-audit-rev0225.md`](cube-refactor-audit-rev0225.md), and [`../../BRANCH_FAMILY_INDEX.json`](../../BRANCH_FAMILY_INDEX.json).


## rev0228 movement: surface metadata contracts

The archive now treats canonical surface metadata as a governed control plane. `SURFACES.json` remains comprehensive and generated, but priority rows can be contract-backed in `CUBE_SURFACE_CONTRACTS.json` so registry, audit, re-entry, and release-control surfaces do not drift into misleading lifecycle, tag, owner, authority, or evidence classifications. This is a navigation/refactor improvement only; it does not close `FT-0181`.

Key surfaces: [`surface-contracts-and-metadata-drift-audit.md`](surface-contracts-and-metadata-drift-audit.md) and [`cube-refactor-audit-rev0228.md`](cube-refactor-audit-rev0228.md).

## rev0224 movement: re-entry refactor after control saturation

The archive now treats navigation itself as a maintenance surface. rev0224 does not add a new `FT-0181` control and does not close the real-import gate. It centralizes re-entry in the navigation map, records the refactor audit, shortens the context-pack startup path, and adds lint so long duplicated control lists do not regrow.

Key surfaces: [`reentry-navigation-map.md`](reentry-navigation-map.md) and [`cube-refactor-audit-rev0224.md`](cube-refactor-audit-rev0224.md).

## rev0223 movement: maintenance mode and control saturation

The archive now recognizes that `FT-0181` has enough pre-import control machinery. rev0223 adds a no-new-control rule, a maintenance-mode stale-gate policy, a real-evidence custody workbench, and a public-claim lexicon. The next meaningful progress should be real `SRC2+` pilot evidence or a named uncovered risk, not another ordinary release-control shell.

Key surfaces: [`../30-operations/control-saturation-and-no-new-control-rule.md`](../30-operations/control-saturation-and-no-new-control-rule.md), [`../30-operations/release-candidate-maintenance-mode-and-stale-gate-policy.md`](../30-operations/release-candidate-maintenance-mode-and-stale-gate-policy.md), [`../30-operations/real-evidence-chain-of-custody-and-redaction-workbench.md`](../30-operations/real-evidence-chain-of-custody-and-redaction-workbench.md), and [`../30-operations/public-claim-lexicon-and-forbidden-phrases.md`](../30-operations/public-claim-lexicon-and-forbidden-phrases.md).


## rev0220 movement: audit-backed ready-but-not-closed release

rev0220 adds release reproducibility, synthetic-example labeling, explicit no-waiver control, and an
assurance case. The archive is now safer to hand off because future maintainers can distinguish
repository consistency from real pilot evidence.

## rev0219 movement: handoff-safe release candidate

The archive now treats late-stage maintenance as a governed operation. `FT-0181` still depends on
external real pilot records, but the surrounding controls now include operator handoff, lifecycle
deprecation rules, evaluator-independence controls, and closeout-board minutes. This keeps the
release candidate usable while making it harder for a future maintainer to convert examples, vendor
claims, convenience, or schema validity into evidence.

Key surfaces: [`../30-operations/operator-handoff-and-maintainer-runbook.md`](../30-operations/operator-handoff-and-maintainer-runbook.md),
[`../30-operations/service-lifecycle-deprecation-and-archive-exit-rules.md`](../30-operations/service-lifecycle-deprecation-and-archive-exit-rules.md),
[`../20-governance/evaluator-independence-and-evidence-contamination-controls.md`](../20-governance/evaluator-independence-and-evidence-contamination-controls.md),
and [`../30-operations/real-import-closeout-board-and-decision-minutes.md`](../30-operations/real-import-closeout-board-and-decision-minutes.md).


This map names the current direction of the archive. Detailed branch history lives in the individual
surfaces and ledgers; this page is a re-entry surface, not a second canon.

## T0. Make the archive queryable and compressive

rev0213 turns the datacube map into an operational compression tool: every Markdown surface is
represented in `SURFACES.json`, priority rows are linted for curated classification, and repeated
starter-profile questions now close through applied table rows rather than new branch shells.

Related: [`datacube-schema.md`](datacube-schema.md),
[`surface-map-overview.md`](surface-map-overview.md),
[`../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md),
[`../20-governance/profile-hardening-template-for-starter-defaults.md`](../20-governance/profile-hardening-template-for-starter-defaults.md),
[`../20-governance/profile-hardening-application-rows.md`](../20-governance/profile-hardening-application-rows.md).

Linked open questions: `OQ-0094`, `OQ-0097`, `OQ-0098`.

## T1. Preserve the teacher as the accountable instructional adult

The archive treats AI as teacher co-intelligence, not teacher replacement. Teacher-facing systems
may compress drafting, planning, analysis, and feedback preparation, but grades, consequence-bearing
interventions, official communications, and care/escalation remain human-owned.

Related: [`../10-core/reference-model.md`](../10-core/reference-model.md),
[`../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md),
[`../30-operations/teacher-capability-bands-and-service-readiness.md`](../30-operations/teacher-capability-bands-and-service-readiness.md),
[`../30-operations/human-coverage-bands-and-no-orphan-handoffs.md`](../30-operations/human-coverage-bands-and-no-orphan-handoffs.md).

Linked open questions: `OQ-0002`, `OQ-0009`, `OQ-0012`.

## T2. Shift from assignment completion to proof of learning

The archive's strongest pedagogical claim is that AI policy should move from artifact policing
toward proof architecture. The live question is not merely “was AI used?” but “what construct had to
be demonstrated, under what conditions, with what proof, and what role did AI play?”

Related:
[`../40-assessment/authentic-assessment-and-proof-of-learning.md`](../40-assessment/authentic-assessment-and-proof-of-learning.md),
[`../40-assessment/proof-of-learning-bundles.md`](../40-assessment/proof-of-learning-bundles.md),
[`../40-assessment/subject-family-proof-intensity-defaults.md`](../40-assessment/subject-family-proof-intensity-defaults.md),
[`../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md`](../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md).

Linked open questions: `OQ-0003`, `OQ-0005`, `OQ-0061`.

## T3. Govern AI services as action-taking workflows

A recurring AI service is not just a model or a chatbot. It has data flows, retrieval sources,
memory, tool permissions, authority ceilings, monitoring, fallback, and rollback. rev0210 adds the
service bill of materials, decision-record template, and security/red-team posture needed to review
those workflows before scale.

Related:
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md),
[`../30-operations/ai-service-intake-and-decision-record-template.md`](../30-operations/ai-service-intake-and-decision-record-template.md),
[`../20-governance/ai-action-authority-register-and-delegation-ceilings.md`](../20-governance/ai-action-authority-register-and-delegation-ceilings.md),
[`../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md`](../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md).

Linked open questions: `OQ-0097`, `OQ-0098`.

## T4. Keep personalization useful without turning it into learner surveillance

Persistent memory, learner models, support records, observability, and retention can help
instruction and accessibility, but they can also become hidden profiling. The archive favors narrow
memory states, protected routes, contestability, minimization, and role-specific visibility.

Related:
[`../20-governance/persistent-memory-personalization-and-learner-model-boundaries.md`](../20-governance/persistent-memory-personalization-and-learner-model-boundaries.md),
[`../20-governance/minimum-observability-and-retention-without-surveillance.md`](../20-governance/minimum-observability-and-retention-without-surveillance.md),
[`../20-governance/sector-and-function-profile-splits-for-memory-defaults.md`](../20-governance/sector-and-function-profile-splits-for-memory-defaults.md),
[`../20-governance/sector-and-function-profile-splits-for-observability-defaults.md`](../20-governance/sector-and-function-profile-splits-for-observability-defaults.md).

Linked open questions: `OQ-0002`, `OQ-0023`, `OQ-0031`.

## T5. Treat youth-facing companions as safeguarding systems

Student companions can support practice and persistence, but persistent relationship-like systems
create dependency, boundary, disclosure, and escalation risks. They need age posture,
emotional-safety boundaries, crisis routing, adult visibility where appropriate, and limits on
private simulated intimacy.

Related:
[`../20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md`](../20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md),
[`../20-governance/student-facing-function-deployment-defaults-and-handoff-triggers.md`](../20-governance/student-facing-function-deployment-defaults-and-handoff-triggers.md).

Linked open questions: `OQ-0096`.

## T6. Stop serial repair from becoming permanent public stigma

The hot-exam branch taught the archive a general rule: after repeated watch / repair / dewatch
cycles, do not keep publishing new ordinary shells unless the next event contains a genuinely new
material pattern. Use compression, local handling, redesign, retirement, or residue.

Related:
[`../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md).

Linked open questions: `OQ-0061`, `OQ-0097`.

## T7. Keep public access and lifelong routes in scope

AI education is not only a school or degree issue. The archive keeps a public access mesh for adult
learning, workforce transition, civic first contact, recognition, handoff, and no-fault continuity
when systems change underneath learners.

Related:
[`../30-operations/lifelong-public-ai-learning-stack.md`](../30-operations/lifelong-public-ai-learning-stack.md),
[`../30-operations/minimum-public-entitlement-and-handoff-standard.md`](../30-operations/minimum-public-entitlement-and-handoff-standard.md),
[`../30-operations/portable-public-learning-packet-and-recognition-profile.md`](../30-operations/portable-public-learning-packet-and-recognition-profile.md),
[`../30-operations/in-flight-teach-out-and-substitute-equivalent-rules.md`](../30-operations/in-flight-teach-out-and-substitute-equivalent-rules.md).

Linked open questions: `OQ-0045`, `OQ-0058`.

## T8. Separate claim strength from deployment enthusiasm

rev0213 extends the evidence-grade ladder into a claim-family matrix, six filled pilot examples,
synthetic service-record backtests, and field-trim rules. The next arc should test those tools
against real pilot evidence rather than adding broad theory. Each AI service now needs an exact
claim family, evidence grade, action ceiling, security posture, construct fit, fallback, stop rule,
renewal cadence, and public claim limit.

Key surfaces:
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md),
[`../30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md),
[`../30-operations/ai-pilot-packet-and-filled-examples.md`](../30-operations/ai-pilot-packet-and-filled-examples.md),
[`../30-operations/service-record-backtest-results-and-field-trim.md`](../30-operations/service-record-backtest-results-and-field-trim.md),
[`../40-assessment/construct-map-and-ai-use-disclosure-matrix.md`](../40-assessment/construct-map-and-ai-use-disclosure-matrix.md),
and [`../40-assessment/construct-family-crosswalk-for-proof-profiles.md`](../40-assessment/construct-family-crosswalk-for-proof-profiles.md).

## T9. Make drift and no-fault continuity costs operational

The archive now treats small changes and route changes as governance events when they accumulate or
shift cost onto learners. Micro-change clusters get a change budget; protected continuity gets a
transition-cost payer posture. This keeps maintenance and public-route repair from becoming hidden
learner burden.

Key surfaces:
[`../20-governance/micro-change-cluster-reset-and-change-budget-defaults.md`](../20-governance/micro-change-cluster-reset-and-change-budget-defaults.md),
[`../30-operations/documented-reliance-and-burden-thresholds.md`](../30-operations/documented-reliance-and-burden-thresholds.md),
[`../30-operations/no-fault-transition-cost-absorption-and-fee-waiver-rules.md`](../30-operations/no-fault-transition-cost-absorption-and-fee-waiver-rules.md),
and [`../30-operations/transition-cost-allocation-and-substitute-equivalent-coverage.md`](../30-operations/transition-cost-allocation-and-substitute-equivalent-coverage.md).


## T10. Publish by audience, import by provenance

rev0215 and rev0216 added the publication and import-provenance rail. Public summaries now render
through redaction profiles; sector adapters overlay K-12/minors, higher-ed credit, public workforce
recognition, and protected support; and import-readiness manifests keep examples, operator drafts,
and verified records separate.

Key surfaces:
[`../30-operations/public-summary-redaction-profiles.md`](../30-operations/public-summary-redaction-profiles.md),
[`../30-operations/sector-adapters-for-service-record-schema.md`](../30-operations/sector-adapters-for-service-record-schema.md),
[`../30-operations/real-pilot-record-import-and-normalization-workflow.md`](../30-operations/real-pilot-record-import-and-normalization-workflow.md),
[`../30-operations/import-readiness-manifest-and-no-real-data-gate.md`](../30-operations/import-readiness-manifest-and-no-real-data-gate.md),
and [`../30-operations/machine-readable-service-record-schema-and-validator.md`](../30-operations/machine-readable-service-record-schema-and-validator.md).

Linked open questions: `OQ-0103`, `OQ-0104`, `OQ-0105`.

## T11. Accept real imports through calibration, not wishful closure

rev0221 strengthens the last live followthrough item without pretending real pilot data exists. The
archive now requires a source data dictionary, a minimum real-data request packet, an acceptance and
reviewer-calibration packet, negative import fixtures, a release-candidate open-item freeze, a
no-fake-real-import guard, an external-evidence watchlist, a control-coverage matrix, an
evidence-refresh calendar, and a human signoff quorum before the first real import can close
`FT-0181`. The first real record should be a calibration event: it should reveal what fields change
decisions, what public claims must narrow, and what schema burden can be cut.

Key surfaces:
[`../30-operations/pilot-source-data-dictionary-template.md`](../30-operations/pilot-source-data-dictionary-template.md),
[`../30-operations/real-import-acceptance-tests-and-reviewer-calibration.md`](../30-operations/real-import-acceptance-tests-and-reviewer-calibration.md),
[`../30-operations/minimum-real-data-request-packet.md`](../30-operations/minimum-real-data-request-packet.md),
[`../30-operations/import-negative-fixtures-and-failure-mode-catalog.md`](../30-operations/import-negative-fixtures-and-failure-mode-catalog.md),
[`../30-operations/decision-delta-log-template-and-field-pruning-rules.md`](../30-operations/decision-delta-log-template-and-field-pruning-rules.md),
[`../30-operations/public-summary-render-smoke-tests.md`](../30-operations/public-summary-render-smoke-tests.md),
[`../30-operations/release-candidate-state-and-open-item-freeze.md`](../30-operations/release-candidate-state-and-open-item-freeze.md),
[`../30-operations/operator-handoff-and-maintainer-runbook.md`](../30-operations/operator-handoff-and-maintainer-runbook.md),
[`../30-operations/service-lifecycle-deprecation-and-archive-exit-rules.md`](../30-operations/service-lifecycle-deprecation-and-archive-exit-rules.md),
[`../20-governance/evaluator-independence-and-evidence-contamination-controls.md`](../20-governance/evaluator-independence-and-evidence-contamination-controls.md),
[`../30-operations/real-import-closeout-board-and-decision-minutes.md`](../30-operations/real-import-closeout-board-and-decision-minutes.md),
[`../30-operations/control-coverage-matrix-and-validator-trace.md`](../30-operations/control-coverage-matrix-and-validator-trace.md),
[`../30-operations/evidence-refresh-calendar-and-staleness-gates.md`](../30-operations/evidence-refresh-calendar-and-staleness-gates.md),
[`../30-operations/human-signoff-quorum-and-conflict-attestation.md`](../30-operations/human-signoff-quorum-and-conflict-attestation.md),
and [`../20-governance/external-evidence-watchlist-and-source-triage.md`](../20-governance/external-evidence-watchlist-and-source-triage.md).

## Immediate priorities

1. Wait for an actual `SRC2+` pilot export or local record set before closing `FT-0181`.
2. Before asking for records, use the minimum real-data request packet and negative fixtures to avoid
   raw exports, protected leakage, hidden authority, unsupported public claims, and decision-neutral
   field creep.
3. When real records arrive, run the readiness manifest, source dictionary, import map,
   service-record validator, acceptance packet, public-summary render smoke test, negative fixture
   checks, lifecycle decision, evaluator-independence check, control-coverage matrix, signoff
   quorum, closeout board, and decision-delta log together.
4. Let the first real import trim or simplify schema fields when they do not change decisions.
5. Use the operator handoff and release-candidate state to ship ready-but-not-closed packages without claiming fake closure.
6. Use lifecycle decisions to demote, deprecate, or archive services whose claims expire or drift.
7. Use the evidence watchlist and refresh calendar to update evidence grades, expiry clocks, public claims, and security
   tests without spawning broad literature branches.
8. Use the control-coverage matrix, signoff quorum, release invariants, dependency graph, recovery drills, and closure checklist to keep release controls from becoming fake evidence.


## T12. Keep the release candidate audit-ready without fake closure

rev0222 turns the late-stage control plane into explicit audit machinery. Release invariants
state the claim boundaries; the dependency graph shows which validators and human artifacts
support each gate; the release-delta manifest separates internal hardening from real evidence;
recovery drills rehearse false-closure and leakage responses; and the `FT-0181` closure checklist
names the missing real evidence rather than letting pre-import controls masquerade as closure.

Key surfaces:
[`../30-operations/release-invariants-and-claim-boundaries.md`](../30-operations/release-invariants-and-claim-boundaries.md),
[`../30-operations/artifact-dependency-graph-and-control-plane.md`](../30-operations/artifact-dependency-graph-and-control-plane.md),
[`../30-operations/version-delta-manifest-and-change-accounting.md`](../30-operations/version-delta-manifest-and-change-accounting.md),
[`../30-operations/recovery-drills-for-false-closure-and-leakage.md`](../30-operations/recovery-drills-for-false-closure-and-leakage.md),
and [`../30-operations/ft0181-closure-evidence-checklist.md`](../30-operations/ft0181-closure-evidence-checklist.md).

