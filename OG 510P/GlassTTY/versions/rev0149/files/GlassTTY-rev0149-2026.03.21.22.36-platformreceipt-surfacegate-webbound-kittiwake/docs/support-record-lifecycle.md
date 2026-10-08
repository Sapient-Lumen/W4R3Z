# Support record lifecycle

Support records are living operational documents. They should change as evidence and implementation change.

## Record states

- `seeded` — template-backed initial record with known unknowns
- `backfilled-from-evidence` — record now cites real artifacts gathered earlier
- `current` — record has been reviewed against recent evidence and current intended scope
- `stale` — record exists but no longer reflects trustworthy current evidence

## Typical lifecycle

1. Seed the record when a surface becomes official.
2. Backfill the record from existing evidence.
3. Update the record after new workflow proof or drift findings.
4. Promote or demote workflow tiers when gates are met or broken.
5. Mark the record stale if evidence age or drift makes current claims unreliable.

## Update triggers

Update a support record when any of the following happens:
- a workflow reaches a higher tier
- a workflow regresses
- a drift incident changes expected behavior
- a browser lane changes meaningfully
- a route/editor/frame model changes
- new evidence replaces older baseline assumptions

## Minimum expectations for an update

A meaningful update should include:
- date of review
- what changed
- evidence refs
- affected workflows
- tier impact
- next action

## What not to do

- do not quietly change support tiers with no evidence refs
- do not let a record remain “current” after obvious drift with no note
- do not treat seeded records as support proof
- do not collapse lane-specific truth into one vague whole-surface claim
