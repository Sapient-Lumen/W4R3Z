# Scenario stub — local-first sync transport storage split

Decision question:
> How should a team choose a local-first stack without collapsing local storage, sync semantics, and transport into one recommendation?

This scenario exists because local-first systems often combine persistence, replication, and conflict semantics that move at different speeds and carry different review burdens.

## Roles to fill
- local persistence
- sync / replication
- transport
- merge / repair semantics
- review / audit support

## Expected artifacts
- `scope-split.receipt.json`
- `decision-brief.md`
- `starter-set.bundle.json`
- `revisit-trigger.policy.json`
- `manual-review.note.md`

## Guardrail
Do not present transport convenience as proof of merge correctness or offline durability.
