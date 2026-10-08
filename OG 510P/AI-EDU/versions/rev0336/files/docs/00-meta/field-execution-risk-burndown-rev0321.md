# rev0321 field execution risk burndown

## Highest live risks

| Risk | Current state | rev0321 change | Remaining next action |
|---|---|---|---|
| `FT-0181` owner boundary never crossed | Prepared first-contact packet exists, but no send or route block exists | keep the send pack as the only active owner-contact surface | send the bounded request or record the route block |
| Micro-pilot never runs | Packet, measure card, and readiness scorer exist, but the passing branch was manual | add `make micro-pilot-dry-run` so the positive path can be rehearsed synthetically | delete the dry run, generate a fresh packet, run one owner-approved cycle, then score the real aggregate packet |
| Synthetic rehearsal mistaken for evidence | Positive smoke now fills plausible aggregate rows | readiness scorer returns `SYNTHETIC_READY_SMOKE_NOT_EVIDENCE` when `DRY-RUN-TRACE.json` is present | keep synthetic packets out of evidence routes and release packaging |
| False learning claim | No local outcome exists | dry-run and readiness statuses both state not-evidence boundaries | keep public language at no-effectiveness-claim |
| Governance tail absorbs the next session | Long meta/governance tails remain retrievable | re-entry points to dry-run then fresh real packet instead of another audit tail | expand through indexes only after a real field result or validator failure |

## Stop condition for more doctrine

No new schema, validator, branch family, or registry should be created before one of these occurs:

- a human owner sends or refuses/blocks the `FT-0181` request;
- a real owner-attested CSV returns and the router emits the next intake command;
- a teacher/tutor owner completes and scores a real micro-pilot aggregate packet;
- a release check finds a reproducible packaging/source-truth defect.

## Claim boundary

This burndown is not evidence and does not change the status of `FT-0181`, service authorization,
public claims, or learning outcomes.
