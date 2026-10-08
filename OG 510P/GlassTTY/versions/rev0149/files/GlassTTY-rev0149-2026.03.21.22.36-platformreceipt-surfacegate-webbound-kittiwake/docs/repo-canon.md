# Repo canon

This file explains where the living source of truth should live.

## Canonical layers

### Top-level canon
These files tell a future implementer what the project is and what it should do next.
- `README.md`
- `STATUS.md`
- `ROADMAP.md`
- `TASKS.md`
- `TASK_QUEUE.md`
- `PROJECT_MAP.md`
- `AGENTS.md`
- `DECISIONS.md`

### Canonical design docs
These define the intended architecture, doctrine, and vocabulary.
- `docs/repo-canon.md`
- `docs/design-principles.md`
- `docs/canon-keys.md`
- `docs/workflow-model.md`
- `docs/workflow-catalog.md`
- `docs/workflow-acceptance-checklists.md`
- `docs/state-api.md`
- `docs/state-contracts.md`
- `docs/adapter-model.md`
- `docs/support-truth.md`
- `docs/support-record-template.md`
- `docs/support-record-lifecycle.md`
- `docs/drift-program.md`
- `docs/drift-triage-playbook.md`
- `docs/evidence-and-ledgers.md`
- `docs/evidence-ledger-schema.md`
- `docs/evidence-catalog.md`
- `docs/feature-traceability.md`
- `docs/agent-policy-model.md`
- `docs/autonomy-ladder.md`
- `docs/implementation-program.md`
- `docs/implementation-epics.md`
- `docs/repo-transition-plan.md`
- `docs/surface-rollout-plan.md`
- `docs/second-adapter-decision-frame.md`
- `docs/surfaces/*.md`
- `docs/support-records/*.md`

### Operational docs
These describe current tools, scripts, and implementation mechanics.
- `docs/doctor.md`
- `docs/testing.md`
- `docs/fixture-lab.md`
- `docs/llm-ops.md`
- `docs/native-messaging.md`
- `docs/protocol-v0.md`
- README files under `extension/`, `daemon/`, `playwright/`, and `adapters/`

### Templates and operating aids
These reduce ambiguity when recording evidence and support truth.
- `docs/templates/support-bundle-manifest-template.md`
- `docs/templates/release-gate-checklist.md`
- `docs/templates/workflow-proof-template.md`
- `docs/templates/drift-incident-template.md`
- `docs/templates/support-record-update-template.md`
- `docs/templates/adapter-bringup-checklist.md`

### Historical docs
These remain valuable but are not the main source of current strategy.
- `docs/handoff-rev*.md`
- `docs/research-notes-*.md`
- `.llm/*`
- archived validation and capture outputs

## Canon rules

1. Major strategy changes should land in top-level or canonical design docs.
2. New system nouns should be added to `docs/canon-keys.md` before they spread.
3. Support truth should live in support records and support matrix rows, not in freeform claims.
4. Historical handoffs can explain why a change happened, but not be the only place where the change is described.
5. Templates should be preferred when a new record type is introduced.
6. Big feature ideas should be traceable through workflows, state, evidence, navigation truth when relevant, and support truth.
7. Transient cues should not be allowed to masquerade as durable workflow completion.
8. Autonomy changes should identify their ladder level and policy requirements.

## Rule of thumb

If a future implementer must read ten handoff files to understand current direction, the canon is failing.
