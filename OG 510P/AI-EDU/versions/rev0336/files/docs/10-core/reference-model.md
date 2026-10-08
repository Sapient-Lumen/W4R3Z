# Reference model

## rev0228 maintenance overlay: contract canonical surface metadata

The reference model now treats canonical surface metadata as part of the archive substrate. A surface can be present, linked, and readable while still carrying misleading generated metadata. Contract-backed rows in `CUBE_SURFACE_CONTRACTS.json` now bind priority surfaces to expected type, lifecycle, owner, authority, portability, evidence markers, and forbidden tags.

This layer is navigation and audit discipline only. It does not close `FT-0181`, import real pilot records, or prove that any AI service works.

Key surfaces: [`../00-meta/surface-contracts-and-metadata-drift-audit.md`](../00-meta/surface-contracts-and-metadata-drift-audit.md), [`../00-meta/cube-refactor-audit-rev0228.md`](../00-meta/cube-refactor-audit-rev0228.md), and [`../../CUBE_SURFACE_CONTRACTS.json`](../../CUBE_SURFACE_CONTRACTS.json).

## rev0227 maintenance overlay: register schemas before trusting structured artifacts

The reference model now treats structured JSON artifacts as part of the governance substrate. A service record, import fixture, release-control record, or root map is not considered governable merely because it parses as JSON; it must have a registered schema, a linted validator, a prose surface, and a closure boundary in `CUBE_SCHEMA_REGISTRY.json`. This is an integrity rule only. It does not close `FT-0181` or prove any AI service works.

Key surfaces: [`../00-meta/schema-registry-and-json-plane-refactor.md`](../00-meta/schema-registry-and-json-plane-refactor.md), [`../00-meta/cube-refactor-audit-rev0227.md`](../00-meta/cube-refactor-audit-rev0227.md), and [`../../CUBE_SCHEMA_REGISTRY.json`](../../CUBE_SCHEMA_REGISTRY.json).

## Toolchain and audit-plane layer

The reference model now treats the archive's own validators, generators, and utility scripts as governed infrastructure. Rev0226 adds a registry-backed lint plane so release-control claims can depend on an explicit list of tools rather than a hidden hardcoded runner.

This layer does not change service authority, learning evidence, public claims, or `FT-0181`. It only makes the maintenance machinery visible enough that future validators cannot become unregistered controls.

Key surfaces: [`../00-meta/toolchain-registry-and-lint-plane-refactor.md`](../00-meta/toolchain-registry-and-lint-plane-refactor.md), [`../00-meta/cube-refactor-audit-rev0226.md`](../00-meta/cube-refactor-audit-rev0226.md), and [`../../CUBE_TOOLCHAIN_REGISTRY.json`](../../CUBE_TOOLCHAIN_REGISTRY.json).

## Re-entry and maintenance-navigation layer

The reference model now separates control completeness from human re-entry. A release can have valid audit, assurance, saturation, custody, and claim-language controls while still being too hard to navigate. Rev0224 adds a compact navigation layer so maintainers use the existing cube before creating new branch or control surfaces.

This layer does not change authority, evidence grade, service effectiveness, or the `FT-0181` closure rule. It only reduces the risk that a future pass mistakes hidden or duplicated surfaces for missing governance.

Key surfaces: [`../00-meta/reentry-navigation-map.md`](../00-meta/reentry-navigation-map.md) and [`../00-meta/cube-refactor-audit-rev0224.md`](../00-meta/cube-refactor-audit-rev0224.md).

## Maintenance-mode control layer

The reference model now separates three things: real evidence, release consistency, and control-plane saturation. Once a real-import gate has validators, human artifacts, negative fixtures, recovery drills, invariants, dependency graph, audit, closure checklist, saturation review, maintenance state, custody workbench, and public-claim lexicon, the archive should stop adding ordinary pre-import shells unless a material uncovered risk appears.

This layer exists to make waiting honest. It keeps `FT-0181` open, keeps public language bounded, and prepares a custody path for real `SRC2+` evidence without committing raw learner traces, protected facts, or security payloads to public surfaces.

Key surfaces: [`../30-operations/control-saturation-and-no-new-control-rule.md`](../30-operations/control-saturation-and-no-new-control-rule.md), [`../30-operations/release-candidate-maintenance-mode-and-stale-gate-policy.md`](../30-operations/release-candidate-maintenance-mode-and-stale-gate-policy.md), [`../30-operations/real-evidence-chain-of-custody-and-redaction-workbench.md`](../30-operations/real-evidence-chain-of-custody-and-redaction-workbench.md), and [`../30-operations/public-claim-lexicon-and-forbidden-phrases.md`](../30-operations/public-claim-lexicon-and-forbidden-phrases.md).


## Late-stage release and lifecycle layer

The reference model now includes a small maintainer-facing layer. After service records, redaction
profiles, sector adapters, import readiness, acceptance packets, and negative fixtures are in place,
the archive still requires operator handoff, lifecycle/deprecation decisions, evaluator independence,
and closeout-board minutes before real pilot imports can change evidence posture.

This layer exists to prevent clean-looking operational artifacts from laundering weak evidence or
conflicted claims. It is especially relevant to `FT-0181`, but it also applies to any recurring AI
service whose public summary, authority ceiling, memory state, or evidence grade might drift after
deployment.


The reference model describes the target shape of the AI education ecosystem. It is intentionally
compact: detailed rules live in governance, operations, assessment, and meta surfaces.

## One-sentence model

AI should expand explanation, feedback, access, teacher capacity, institutional learning, and
lifelong opportunity **without** replacing human responsibility, weakening proof of learning, hiding
consequential decisions, or turning support records into surveillance.

## Layer 1. Substrate

Every serious deployment needs governed infrastructure before scale:

- privacy and procurement review;
- identity, access, and role control;
- data-flow and retention rules;
- model / vendor / retrieval transparency;
- security and red-team review;
- rollback, fallback, and incident ownership;
- a publication and adapter rail for audience-specific summaries, sector obligations, and source provenance;
- source dictionaries, minimum request packets, acceptance packets, and negative fixtures before real pilot imports are treated as evidence.

Key surfaces:
[`../20-governance/evidence-and-procurement.md`](../20-governance/evidence-and-procurement.md),
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md),
[`../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md`](../20-governance/ai-service-security-red-team-and-agentic-tool-boundaries.md),
[`../30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md),
[`../30-operations/ai-service-intake-and-decision-record-template.md`](../30-operations/ai-service-intake-and-decision-record-template.md),
[`../30-operations/public-summary-redaction-profiles.md`](../30-operations/public-summary-redaction-profiles.md),
[`../30-operations/sector-adapters-for-service-record-schema.md`](../30-operations/sector-adapters-for-service-record-schema.md),
[`../30-operations/real-pilot-record-import-and-normalization-workflow.md`](../30-operations/real-pilot-record-import-and-normalization-workflow.md),
[`../30-operations/pilot-source-data-dictionary-template.md`](../30-operations/pilot-source-data-dictionary-template.md),
[`../30-operations/real-import-acceptance-tests-and-reviewer-calibration.md`](../30-operations/real-import-acceptance-tests-and-reviewer-calibration.md),
[`../30-operations/minimum-real-data-request-packet.md`](../30-operations/minimum-real-data-request-packet.md),
[`../30-operations/import-negative-fixtures-and-failure-mode-catalog.md`](../30-operations/import-negative-fixtures-and-failure-mode-catalog.md),
[`../30-operations/release-candidate-state-and-open-item-freeze.md`](../30-operations/release-candidate-state-and-open-item-freeze.md),
and [`../20-governance/external-evidence-watchlist-and-source-triage.md`](../20-governance/external-evidence-watchlist-and-source-triage.md).

## Layer 2. Teacher co-intelligence

Teachers remain accountable for instructional purpose, adaptation, judgment, care, and escalation.
AI may help with planning, examples, differentiation, feedback drafts, translation, accessibility
formats, and analysis, but official consequences require human ownership.

Key surfaces:
[`../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md`](../20-governance/teacher-facing-function-delegation-defaults-and-sign-off-triggers.md),
[`../30-operations/teacher-capability-bands-and-service-readiness.md`](../30-operations/teacher-capability-bands-and-service-readiness.md),
and
[`../30-operations/human-coverage-bands-and-no-orphan-handoffs.md`](../30-operations/human-coverage-bands-and-no-orphan-handoffs.md).

## Layer 3. Student companion and support

Student-facing AI should be bounded by construct, age, stakes, memory, and handoff. It may support
practice, hints, revision, explanation, study planning, and reflection. It should not quietly become
an answer engine, counselor, disciplinary witness, or unchallengeable record source.

Key surfaces:
[`../20-governance/student-facing-function-deployment-defaults-and-handoff-triggers.md`](../20-governance/student-facing-function-deployment-defaults-and-handoff-triggers.md),
[`../20-governance/sector-and-age-profile-splits-for-student-facing-defaults.md`](../20-governance/sector-and-age-profile-splits-for-student-facing-defaults.md),
[`../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md`](../20-governance/cognitive-effort-budget-and-construct-preservation-defaults.md),
and
[`../20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md`](../20-governance/ai-companion-dependency-and-youth-safeguarding-defaults.md).

## Layer 4. Proof of learning

The archive treats assessment redesign as central. AI-era assessment should define the construct,
permitted assistance, disclosure rule, proof bundle, sampling ceiling, and challenge path. Some
tasks can permit AI production if proof shifts to oral defense, live transfer, checkpoints, process
evidence, or unaided comparison. Other tasks must remain unaided because the unaided performance is
the construct.

Key surfaces:
[`../40-assessment/construct-map-and-ai-use-disclosure-matrix.md`](../40-assessment/construct-map-and-ai-use-disclosure-matrix.md),
[`../40-assessment/authentic-assessment-and-proof-of-learning.md`](../40-assessment/authentic-assessment-and-proof-of-learning.md),
[`../40-assessment/proof-of-learning-bundles.md`](../40-assessment/proof-of-learning-bundles.md),
[`../40-assessment/subject-family-proof-intensity-defaults.md`](../40-assessment/subject-family-proof-intensity-defaults.md),
and
[`../40-assessment/bundle-intensity-bands-and-sampling-ceilings.md`](../40-assessment/bundle-intensity-bands-and-sampling-ceilings.md).

## Layer 5. AI literacy and curriculum

AI literacy is not just prompting. Learners and staff need a human-centered understanding of model
limits, bias, hallucination, privacy, copyright, labor, security, disclosure, dependence, and when
to refuse automation. AI literacy also belongs in subject practice: writing with AI differs from
using AI in math proof, clinical simulation, laboratory work, language learning, or studio critique.

Key surface: [`minimal-ai-literacy-spine.md`](minimal-ai-literacy-spine.md).

## Layer 6. Institutional governance

Institutions must govern AI as services with authority, memory, evidence, lifecycle, and owners.
This includes action ceilings, observability without surveillance, failure escalation,
model/workflow change review, contestability, and explicit retirement.

Key surfaces:
[`../20-governance/ai-action-authority-register-and-delegation-ceilings.md`](../20-governance/ai-action-authority-register-and-delegation-ceilings.md),
[`../20-governance/minimum-observability-and-retention-without-surveillance.md`](../20-governance/minimum-observability-and-retention-without-surveillance.md),
[`../20-governance/failure-escalation-safe-degradation-and-manual-fallback.md`](../20-governance/failure-escalation-safe-degradation-and-manual-fallback.md),
[`../20-governance/model-and-workflow-change-classification-and-fresh-review-triggers.md`](../20-governance/model-and-workflow-change-classification-and-fresh-review-triggers.md),
[`../20-governance/micro-change-cluster-reset-and-change-budget-defaults.md`](../20-governance/micro-change-cluster-reset-and-change-budget-defaults.md),
and
[`../20-governance/pilot-to-scale-evidence-and-rollout-gates.md`](../20-governance/pilot-to-scale-evidence-and-rollout-gates.md).

## Layer 7. Improvement and research

Deployments should produce evidence about learning, workload, equity, access, accessibility, error
modes, cost, and harms. A tool that is popular but weakens learning proof, increases hidden labor,
or forces stronger surveillance than its benefit justifies should be demoted or retired.

Key surfaces:
[`../20-governance/evidence-and-procurement.md`](../20-governance/evidence-and-procurement.md),
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`../20-governance/pilot-to-scale-evidence-and-rollout-gates.md`](../20-governance/pilot-to-scale-evidence-and-rollout-gates.md),
[`../30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md),
[`../30-operations/ai-pilot-packet-and-filled-examples.md`](../30-operations/ai-pilot-packet-and-filled-examples.md),
[`../30-operations/service-record-backtest-results-and-field-trim.md`](../30-operations/service-record-backtest-results-and-field-trim.md),
and
[`../20-governance/sector-and-function-profile-splits-for-rollout-gates.md`](../20-governance/sector-and-function-profile-splits-for-rollout-gates.md).

## Cross-cutting public access mesh

AI education must extend beyond ordinary course shells. Community colleges, VET and adult-education
providers, public workforce systems, libraries, and civic learning spaces provide first contact,
bridge learning, recognition, navigation, and ongoing access. Portability should be
learner-controlled, narrow, and separated from protected support records.

Key surfaces:
[`../30-operations/lifelong-public-ai-learning-stack.md`](../30-operations/lifelong-public-ai-learning-stack.md),
[`../30-operations/minimum-public-entitlement-and-handoff-standard.md`](../30-operations/minimum-public-entitlement-and-handoff-standard.md),
[`../30-operations/portable-public-learning-packet-and-recognition-profile.md`](../30-operations/portable-public-learning-packet-and-recognition-profile.md),
and
[`../30-operations/standing-equivalency-lists-and-review-governance.md`](../30-operations/standing-equivalency-lists-and-review-governance.md).

## Cross-cutting rails added by recent revisions

- Datacube schema and `SURFACES.json`: make the archive queryable by actor, stakes, function,
  memory, proof, authority, owner, lifecycle, evidence, and portability.
- Action-authority register: asks what the AI can actually cause before treating it as harmless
  support.
- Cognitive-effort budget: ties permission to the construct and shifts proof when AI production is
  allowed.
- Companion-safeguarding ladder: keeps persistent youth-facing coaches from hiding inside ordinary
  tutoring labels.
- Serial repair compression: prevents recurring hot-exam repair shells from turning into permanent
  public stigma.
- Service BOM and security posture: treats deployed AI as a workflow with data, tools, retrieval,
  authority, threat surfaces, fallback, and rollback.
- Evidence-grade ladder and claim-family matrix: separate learning, performance, workload, access, safety, validity, security, contestability, and compliance claims.
- Implementation review cycle and filled pilot packet: turn intake, sandbox, pilot, scale, renewal, stop rules, examples, and retirement into an operational sequence.
- Construct map and proof crosswalk: link AI permission, disclosure, proof, accessibility, and cognitive effort to the construct being assessed.

Key surfaces: [`../00-meta/datacube-schema.md`](../00-meta/datacube-schema.md),
[`../00-meta/surface-map-overview.md`](../00-meta/surface-map-overview.md),
[`../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md),
[`../20-governance/ai-service-bom-and-procurement-intake.md`](../20-governance/ai-service-bom-and-procurement-intake.md),
[`../20-governance/evidence-grade-and-claim-strength-ladder.md`](../20-governance/evidence-grade-and-claim-strength-ladder.md),
[`../20-governance/claim-family-evidence-matrix.md`](../20-governance/claim-family-evidence-matrix.md),
[`../30-operations/ai-implementation-review-cycle-and-stop-rules.md`](../30-operations/ai-implementation-review-cycle-and-stop-rules.md),
[`../30-operations/ai-pilot-packet-and-filled-examples.md`](../30-operations/ai-pilot-packet-and-filled-examples.md),
[`../40-assessment/construct-map-and-ai-use-disclosure-matrix.md`](../40-assessment/construct-map-and-ai-use-disclosure-matrix.md),
and
[`../40-assessment/construct-family-crosswalk-for-proof-profiles.md`](../40-assessment/construct-family-crosswalk-for-proof-profiles.md).

## Role split

**Teachers** own purpose, review, adaptation, care, escalation, and final educational judgment.

**Students** use AI for practice, exploration, drafting, critique, and reflection while remaining
responsible for learning.

**Institutions** own safe infrastructure, procurement, literacy provision, assessment redesign,
contestability, public routes, and service retirement.

**AI systems** are useful when they extend explanation, feedback, access, personalization, and
teacher capacity; they are unsafe when they replace responsibility, conceal failure, or dilute
evidence of learning.

## Compact thesis

The right institutional shape is not “AI replaces teachers.” It is: every teacher gets serious
co-intelligence, every learner gets bounded support, every institution gets proof and governance
infrastructure, the curriculum teaches judgment, and the public system offers lifelong entry routes
without turning support into surveillance.


## Import-readiness guardrail

The reference model now distinguishes four different things that can otherwise be confused:
realistic examples, operator-drafted templates, real pilot records, and public notices. Realistic
examples can test schema completeness, but they do not prove effectiveness. A real import must pass
the readiness manifest, minimum request packet, source dictionary, acceptance packet, decision-delta
log, service-record validator, sector adapters, redaction profiles, negative fixture checks, and
public-summary render smoke tests before it can change the archive's evidence posture.

This keeps the model implementation-ready without letting implementation theatre become evidence.


## Release assurance layer

Late-stage service governance now has an assurance layer above ordinary lint:

- release audit manifest for selected hashes and generated artifacts;
- synthetic-example declaration so examples stay non-evidence;
- policy-exception record so waivers cannot become hidden policy;
- ready-but-not-closed assurance case so a release can ship without pretending external gates are closed.

This layer governs the archive and service records. It does not replace classroom evidence, protected-route
review, construct validation, or real pilot import.


## Late-stage control plane

rev0222 adds a release-control plane around real pilot import. The control plane includes
invariants, dependency graph, release delta, recovery drills, and an `FT-0181` closure checklist.
These artifacts govern claims about the archive itself: what is lint-clean, what is externally
gated, what must fail, and what evidence is still missing. They do not prove any AI service is
effective, safe, compliant, or ready for promotion.



## Rev0225 branch-history note

Historical branch surfaces remain valid but are no longer treated as first-read architecture. Use [`../00-meta/branch-family-index-and-refactor-map.md`](../00-meta/branch-family-index-and-refactor-map.md) and [`../../BRANCH_FAMILY_INDEX.json`](../../BRANCH_FAMILY_INDEX.json) when a case appears to require another `first-*`, `portable-*`, or `late-relapse-*` governance shell. The reference model should absorb recurring branch logic through compression, profile hardening, service records, or lifecycle rules before creating another sibling branch.
