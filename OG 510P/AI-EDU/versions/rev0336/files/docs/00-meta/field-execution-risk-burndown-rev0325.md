# rev0325 field execution risk burndown

## Highest live risks

| Risk | Current state | rev0325 change | Remaining next action |
|---|---|---|---|
| `FT-0181` owner boundary never crossed | Send pack exists but no send or route block exists | field handoff bundle puts the send-now brief, owner email, reply template, and router command in one scratch handoff | send the bounded request or record the route block |
| Micro-pilot never runs | Packet, readiness, owner-review, and result recorders exist, but no real aggregate cycle occurred | same field bundle creates the equality-one-step packet, readiness card, and next-action brief together | complete owner plan, run one local aggregate cycle, then run readiness |
| Operator opens doctrine instead of acting | Current action is spread across many surfaces | root path now points to one `make field-handoff-bundle` step before human action | use bundle output; do not add policy until a real event or validator defect exists |
| Scratch artifacts are mistaken for evidence | Bundle creates actionable local files | bundle manifest and docs mark every output as scratch/local non-evidence | keep generated files out of release packaging and public claims |
| Human review/result boundary skipped | Result recorder exists but requires real owner review | bundle next-action surface keeps owner review and result receipt sequential | record review only after human review; record result only after hash-matched review |

## Stop condition for more doctrine

Do not create a new policy branch, schema, validator, or registry until one of these happens:

- human send/adaptation of the bounded `FT-0181` request;
- route-block record;
- returned owner-attested CSV/source packet;
- real completed teacher/tutor aggregate packet;
- real human owner-review stop;
- legitimate local result receipt;
- reproducible validator/source-truth defect.

## Boundary

This burndown is not evidence and does not change `FT-0181`, service authority, public claims, custody, or learning outcomes.
