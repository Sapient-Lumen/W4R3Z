# RFC-0190: Staged rollouts and cohorts

## Problem

Even with A/B recovery, offering a bad update to everyone at once is an avoidable outage.
Most production update systems rely on staged rollouts and cohorts, but these controls are often ad-hoc and hard to audit.

## Proposal

Introduce explicit rollout artifacts:

- `rollout.policy` (`spec/rollout.policy.schema.json`): phases + cohort assignment + guardrails
- `rollout.receipt` (`spec/rollout.receipt.schema.json`): evidence of a specific “offer/hold/block” decision

Rollout decisions should be:

- deterministic where possible (salted hashing)
- steerable only via signed/receipted policy
- attachable to incident bundles and explain output

## Why now

Staged rollouts touch almost every later subsystem (telemetry, incident response, emergency override).
If we don’t standardize them early, they become scripts with no evidence trail.

## Risks / tradeoffs

- Bad cohort design can leak information; prefer hashes and avoid raw IDs.
- Rollout policy becomes a powerful lever; must be governed by trust policy and two-person integrity when required.

See also: `docs/258-staged-rollouts-and-cohorts.md`.
