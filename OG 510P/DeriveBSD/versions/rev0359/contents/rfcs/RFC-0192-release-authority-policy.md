# RFC-0192: Release authority policy

## Problem

DeriveBSD can verify artifacts, but “who is allowed to publish a release?” often devolves into CI scripts and tribal knowledge.
Emergency halts and key rotations then become unaudited procedures.

## Proposal

Add first-class release authority artifacts:

- `release.authority.policy` (`spec/release.authority.policy.schema.json`)
- `release.publish.receipt` (`spec/release.publish.receipt.schema.json`)
- `release.halt.event` (`spec/release.halt.event.schema.json`)

And extend `release.capsule` bindings with:
- `release_authority_policy_digest`
- `release_publish_receipt_digest`

Authority policy defines:
- signing roles + threshold rules for publish/halt/resume/rotate
- transparency requirements (optional but policy-driven)
- optional “monitor clean” gates

## Why now

Key management and emergency controls are hardest to retrofit.
This keeps release authority reviewable, composable, and attachable to incident evidence from day 0.

## Risks / tradeoffs

- Too much flexibility can recreate TUF complexity; keep a minimal core.
- Threshold publishing requires operational discipline (key custody, signing ceremonies).

See also: `docs/260-release-authority-policy-and-key-management.md`.
