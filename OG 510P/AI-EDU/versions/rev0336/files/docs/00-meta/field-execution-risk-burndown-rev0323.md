# rev0323 field execution risk burndown

## Highest live risks

| Risk | Current state | rev0323 change | Remaining next action |
|---|---|---|---|
| `FT-0181` owner boundary never crossed | First-contact packet and send pack exist, but no send or route block exists | keep owner field router as the only active owner-contact path | send the bounded request or record the route block |
| Micro-pilot never reaches human review | Packet, measure card, readiness scorer, dry-run harness, and next-action router exist | add `make micro-pilot-owner-review` for the future non-synthetic ready packet | run one owner-approved local micro-cycle, score the aggregate packet, then record review only after human review |
| Synthetic rehearsal mistaken for review | Dry-run packets can pass readiness as synthetic smoke | owner-review recorder refuses `DRY-RUN-TRACE.json` and any status except `READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE` | delete dry-runs before real owner work |
| Local owner decision drifts from readout | Decision could be copied into one file but not the other | owner-review recorder requires CLI decision, final row 8, and memo decision to match | use one of four bounded decisions only |
| Governance tail absorbs the next session | Cold doctrine remains retrievable | startup path now points to the owner-review stop card and command | open branch history only after real field result or validator failure |

## Stop condition for more doctrine

Do not create a new schema, validator, branch family, or registry before one of these events happens:

- a human sends the bounded `FT-0181` request;
- a route block is recorded;
- a real owner-attested CSV returns;
- a real teacher/tutor micro-cycle produces a completed aggregate packet;
- a human local owner review is recorded with `make micro-pilot-owner-review`;
- a release check finds a reproducible source-truth defect.

## Boundary

This burndown is not evidence and does not change `FT-0181`, service authorization, public claims, or
learning outcomes.
