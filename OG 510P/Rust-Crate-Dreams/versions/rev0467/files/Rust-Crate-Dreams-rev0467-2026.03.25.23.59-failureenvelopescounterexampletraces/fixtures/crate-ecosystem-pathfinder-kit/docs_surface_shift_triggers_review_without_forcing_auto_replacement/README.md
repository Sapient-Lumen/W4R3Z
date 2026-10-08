# Scenario — `docs_surface_shift_triggers_review_without_forcing_auto_replacement`

A team froze a starter set partly because one candidate had a clearer visible target/support story on docs.rs.
Later, docs.rs default targets or visible docs posture shift.

## What this scenario is for

- `revisit-trigger.policy.json` should be able to classify docs-surface shifts as `review_due` rather than a no-op.
- `freeze-horizon.policy.json` should keep a routine review cadence even if no other trigger fires.
- The watch layer should not force automatic replacement just because visible docs posture moved.

## Why this matters

Visible support story is part of crate choice, but it is not identical to task fit.
A good pathfinder should reopen review without pretending that docs-surface drift by itself settles the replacement decision.
