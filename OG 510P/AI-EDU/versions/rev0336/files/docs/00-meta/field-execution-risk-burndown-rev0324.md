# rev0324 field execution risk burndown

## Highest live risks

| Risk | Current state | rev0324 change | Remaining next action |
|---|---|---|---|
| `FT-0181` owner boundary never crossed | First-contact packet and send pack exist, but no send or route block exists | keep owner field router as the only active owner-contact path | send the bounded request or record the route block |
| Micro-pilot result never gets captured | Packet, readiness, next-action, and owner-review stop exist, but no compact post-review receipt existed | add `make micro-pilot-result` to summarize a real owner-reviewed aggregate packet without upgrading claims | run one owner-approved local micro-cycle, record owner review, then record the result receipt |
| Reviewed packet is overclaimed | A future packet could be treated as evidence because it has owner review | result recorder labels evidence, custody, service-authority, public-claim, and closure effects as none | use result only for local next-cycle decisions |
| Packet changes after owner review | A reviewed packet could be edited before result recording | result recorder compares packet hashes against the owner-review stop record | rerun readiness and owner review if packet changes |
| Governance tail absorbs the next session | Cold doctrine remains retrievable | startup path now points to result receipt after owner review | open branch history only after real field result or validator failure |

## Stop condition for more doctrine

Do not create a new schema, validator, branch family, or registry before one of
these events happens:

- a human sends the bounded `FT-0181` request;
- a route block is recorded;
- a real owner-attested CSV returns;
- a real teacher/tutor micro-cycle produces a completed aggregate packet;
- a human local owner review is recorded;
- a local result receipt is recorded;
- a release check finds a reproducible source-truth defect.

## Boundary

This burndown is not evidence and does not change `FT-0181`, service
authorization, public claims, or learning outcomes.
