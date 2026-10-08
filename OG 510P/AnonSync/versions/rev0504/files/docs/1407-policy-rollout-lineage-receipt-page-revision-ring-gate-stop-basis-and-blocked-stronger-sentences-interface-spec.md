# Policy-rollout lineage receipt page: revision, ring, gate, stop basis, and blocked stronger sentences interface spec

## Purpose

This receipt is the exportable proof for a rollout judgment.
It exists so the operator can answer later:

> why did the product move only this far, what exactly blocked broader promotion, and what kind of rollback posture existed at that moment?

## Receipt contents

The receipt must preserve:

- `policy_rollout_id`
- policy family id
- predecessor revision
- successor revision
- issuance time
- current rollout state
- per-ring subject counts
- readiness-gate verdicts
- armed stop conditions
- rollback class
- strongest safe sentence
- blocked stronger sentence
- recommended remediations
- evidence freshness

## Human-readable summary

Example summary:

- `Successor revision is active in canary and pilot rings only. Broad promotion remains blocked by one mixed-major linked family, one Business-held v2 lane, and one restart-bound service cohort. Current rollback posture is restart-bound revert for pilot and holdback for broad.`

## Hard rules

- the receipt must always separate publication from actual promotion state
- per-ring counts must be named explicitly
- governing blockers and armed stop conditions must be listed individually
- rollback class must survive export intact
- the blocked stronger sentence must remain visible even when the rollout is frozen
