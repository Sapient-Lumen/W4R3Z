# RFC-0193: Rollout privacy constraints

## Problem

Cohorts are necessary for staged rollouts, but cohort assignment and hints can become a long-lived identifier if not constrained.

## Proposal

Extend `rollout.policy.cohorting` with an optional `privacy` block that makes privacy constraints reviewable and enforceable:
- `entropy_budget_bits`
- `max_cohorts`
- `min_bucket_size`
- `salt_rotation` (epoch duration and triggers)
- `allow_hw_fingerprint` (explicit opt-in)

Update `docs/258-staged-rollouts-and-cohorts.md` to link to privacy guidance.

## Why now

Once cohort IDs are in telemetry, receipts, and transparency entries, tightening privacy later becomes expensive and politically hard.
Bake constraints in before ecosystem drift.

## Risks / tradeoffs

- Lower cohort entropy can reduce rollout steering granularity.
- Salt rotation can complicate longitudinal analysis; prefer explicit epochs.

See also: `docs/261-rollout-privacy-and-cohort-hygiene.md`.
