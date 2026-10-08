# Project map

GlassTTY now has six documentation layers.

## 1. Top-level canon
These files answer what the project is, what is true now, and what should happen next.

- `README.md`
- `STATUS.md`
- `ROADMAP.md`
- `TASKS.md`
- `TASK_QUEUE.md`
- `PROJECT_MAP.md`
- `REVISION-RECEIPT.json`
- `SUPPORT-BUNDLE-CONTRACT.json`
- `SUPPORT-PUBLIC-SURFACE.json`
- `SUPPORT-SOURCE-LOCK.json`
- `SUPPORT-SOURCE-BASELINE.json`
- `AGENTS.md`
- `DECISIONS.md`

## 2. Canonical design docs
These files define the intended shape of the system.

- `docs/repo-canon.md`
- `docs/design-principles.md`
- `docs/canon-keys.md`
- `docs/architecture.md`
- `docs/workflow-model.md`
- `docs/workflow-catalog.md`
- `docs/workflow-acceptance-checklists.md`
- `docs/state-api.md`
- `docs/state-contracts.md`
- `docs/operational-truth-splits.md`
- `docs/browser-history-witness.md`
- `docs/transient-cues-and-durable-outcomes.md`
- `docs/control-plane-report.md`
- `docs/install-receipt.md`
- `docs/support-surface-snapshot.md`
- `docs/opening-contract.md`
- `docs/truth-surface-register.md`
- `docs/truth-surface-warnings.md`
- `docs/refresh-truth-surfaces.md`
- `docs/revision-receipt.md`
- `docs/validation-artifact-inventory.md`
- `docs/support-bundle-manifest.md`
- `docs/support-bundle-queue.md`
- `docs/published-support-surface.md`
- `docs/support-bundle-transition.md`
- `docs/approved-source-hierarchy.md`
- `docs/support-source-baseline.md`
- `docs/release-manifest.md`
- `docs/operator-startup.md`
- `docs/action-model.md`
- `docs/adapter-model.md`
- `docs/support-truth.md`
- `docs/support-record-template.md`
- `docs/support-record-lifecycle.md`
- `docs/support-matrix.md`
- `docs/drift-program.md`
- `docs/drift-triage-playbook.md`
- `docs/evidence-and-ledgers.md`
- `docs/evidence-ledger-schema.md`
- `docs/feature-traceability.md`
- `docs/agent-policy-model.md`
- `docs/autonomy-ladder.md`
- `docs/implementation-program.md`
- `docs/implementation-epics.md`
- `docs/repo-transition-plan.md`
- `docs/release-gates.md`
- `docs/surface-rollout-plan.md`
- `docs/second-adapter-decision-frame.md`
- `docs/surfaces/*.md`
- `docs/support-records/*.md`

## 3. Operational and implementation docs
These explain current tooling and mechanics.

- `docs/doctor.md`
- `docs/testing.md`
- `docs/fixture-lab.md`
- `docs/native-messaging.md`
- `docs/protocol-v0.md`
- `docs/archive-maintenance.md`
- `docs/archive-memory.md`
- `docs/llm-ops.md`
- `docs/current-capability-map.md`
- `scripts/control-plane-report.py`
- `scripts/install-receipt.py`
- `scripts/support-surface-snapshot.py`
- `scripts/check-support-record-contract.py`
- `scripts/check-opening-contract.py`
- `scripts/truth-surface-register.py`
- `scripts/truth-surface-warnings.py`
- `scripts/validation-artifact-inventory.py`
- `scripts/support-bundle-queue.py`
- `scripts/check-support-bundle-contract.py`
- `scripts/published-support-surface.py`
- `scripts/support-publish-gate.py`
- `scripts/support-source-baseline.py`
- `scripts/support-bundle-transition.py`
- `scripts/release_manifest.py`
- `scripts/check-revision-receipt.py`
- `scripts/refresh-truth-surfaces.py`
- `playwright/README.md`
- `extension/README.md`
- `daemon/README.md`
- `adapters/claude/README.md`

## 4. Templates and operating aids
These reduce ambiguity when creating records and artifacts.

- `docs/support-record-template.md`
- `docs/templates/support-bundle-manifest-template.md`
- `docs/templates/release-gate-checklist.md`
- `docs/templates/workflow-proof-template.md`
- `docs/templates/drift-incident-template.md`
- `docs/templates/support-record-update-template.md`
- `docs/templates/adapter-bringup-checklist.md`

## 5. Living support truth
These files are meant to be updated as evidence changes.

- `docs/support-records/*.md`
- `docs/support-bundles/*/*.json`
- `docs/support-matrix.md`
- `SUPPORT-PUBLIC-SURFACE.json`
- `SUPPORT-SOURCE-LOCK.json`
- `SUPPORT-SOURCE-BASELINE.json`
- release-gate artifacts and published support bundles

## 6. Historical memory
These are useful evidence and history, but they are no longer the place where the project’s main direction should live.

- `docs/handoff-rev*.md`
- `docs/research-notes-*.md`
- `.llm/*`
- older validation/capture artifacts

## Working rule

If a future implementer needs to understand current direction, they should not have to read old handoffs first. Historical docs remain valuable, but the canon should stand on its own.
