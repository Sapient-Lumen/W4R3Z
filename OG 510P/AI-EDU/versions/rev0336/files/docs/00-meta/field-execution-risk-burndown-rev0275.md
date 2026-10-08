# Field execution risk burndown rev0275

## Burned down in this pass

| Risk | Rev0275 correction |
|---|---|
| Seed-to-review prose gap | Valid workbench seeds now route to `make owner-workbench-review ...` rather than an unstructured manual note. |
| False post-seed acceptance | `workbench-review.json` is forced to `REVIEWED_NOT_ACCEPTED`, `NOT_ACCEPTED`, and `not_evidence`. |
| Weak proceed routing | `PROCEED-DECISION-BOARD` requires `SRC2` or stronger, at least two reviewer roles, at least one surviving field, at least one decision-changing field, no pending re-ask count, and no raw/protected/security/public-claim-upgrade flags. |
| Re-ask improvisation | `REASK-OWNER` reviews can source one bounded `REASK_AWAITING_REPLY` contact-status clock. |
| Raw answer leakage | The review record stores counts, hashes, route labels, and flags only. |
| Release-path leakage | Review outputs are blocked from docs/examples/tools/templates/schemas and other nonscratch archive paths. |

## Still open

`FT-0181` is still externally blocked until a real owner path is executed. The next meaningful non-local event is a sent/adapted owner request followed by either a returned owner CSV or a bounded no-owner-packet outcome.

## Next likely risk

After a valid `PROCEED-DECISION-BOARD` review, the next risk is decision-board overreach: mapping a reviewed local packet into custody, acceptance, public summary, or live-window plans before the decision board records exactly what changed and what remains blocked.
