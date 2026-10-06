# ADR-0037: Scope anti-rollback to automatic acceptance; allow explicit manual rollback

- Status: accepted
- Date: 2026-02-23

## Context

DeriveBSD promises instant rollback while also seeking anti-rollback defenses.

## Decision

Anti-rollback (monotonic rollback indices) applies to:

- automatic update acceptance
- unattended boot

Manual rollback is permitted only with an explicit, policy-gated override that is evidence-recorded and does not decrement the rollback index.

## Consequences

- Downgrade attacks via the automated path are prevented.
- Operators retain fast recovery capability.
- Update convergence is preserved (post-rollback, updates must advance to a newer version).
