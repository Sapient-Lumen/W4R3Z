# Revision receipts and audit objects

## Working claim

DelayBasin may need a compact **revision receipt** for each revision:
a machine-readable audit object that says what kind of transition just happened,
what status changed,
which external pressure mattered,
and which deterministic checks passed.

This is not meant to replace prose.
It exists because changelogs are good for humans but weak as admissibility objects.
A receipt is the smallest object that says:
**this revision counted, here is why, and here is what changed status.**

## Why this pressure appears now

DelayBasin already preserves:
- certified move classes,
- promotion contracts,
- decay-watch entries,
- recovery kernel,
- bounded handoff state.

What it still lacked was a compact object binding these together **per revision**.
Without that, progress can remain rhetorically described but not serialized as an auditable transition.

## Minimal revision receipt

A minimal DelayBasin revision receipt should preserve:
- revision id,
- prior revision id,
- instantiated certified move classes,
- canon-level ids added or status-shifted,
- quarantined ids added,
- refs materially used,
- deterministic checks passed,
- compact touched-surface list,
- whether packaging occurred.

## What this buys

- claim-level auditability without replaying the whole session,
- clearer distinction between *a revision happened* and *a legitimate transition occurred*,
- better handoff integrity across cold reopen,
- a path toward replay/fork analysis without inflating the archive into a full event log.

## What it does not buy

- theorem-level proof that the revision was good,
- immunity to bad judgment,
- a substitute for reading the actual docs,
- a license to generate empty ceremony.

## Design discipline

Revision receipts should stay small.
If a receipt becomes a second changelog, it has failed.
If a receipt omits the status-changing core, it has also failed.

The right target is a compact **audit object**, not a narrative mirror.
