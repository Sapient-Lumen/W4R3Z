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
- a compact basis witness naming the expected head, observed basis, basis state, and repair posture when current-head grounding mattered,
- whether packaging occurred,
- and a compact receipt-freshness witness naming whether the receipt's terse current-revision identity keys still match the packaged bundle, manifest timestamp, and current comparison rows they are supposed to summarize.

## What this buys

- claim-level auditability without replaying the whole session,
- clearer honesty about whether the revision was grounded on the head or basis it claims to extend,
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

A newer extension is that the receipt should stay a **decision/admission object**, not the whole execution or citation story: the materialized bundle belongs to the release manifest, the frozen public relation belongs to the durable status ledger, and the receipt should only carry the smallest admission-level trace that says why the transition counted.

A fresh extension is that the receipt should also carry one compact **scope witness** whenever the revision is supposed to stay about one exact request, target lineage, or judged object: the active request, the exact target, the nearby ambient surfaces kept out, the current scope state, and the fail-closed repair posture belong in the receipt-level admission trace rather than in flattering session memory.

A newer extension is that the receipt should also carry one compact **authorship witness** whenever collaborative authority could otherwise blur: the initiating lane, draft-authorship posture, approval lane, execution lane, review or compensating-control lane, autonomy posture, lane-collapse state, and fail-closed repair belong in the receipt-level admission trace when proposal, approval, execution, and review are not all the same thing.

A fresh extension is that the receipt should also carry one compact **receipt-freshness witness** whenever terse current-revision identity keys such as `summary_highlight`, `codename`, `created_at`, or current comparison ids could otherwise lag the actual packaged bundle: the current bundle filename, manifest timestamp token, receipt timestamp token, bundle-stem suffix relation, current comparison ids, freshness state, and fail-closed repair belong in the receipt-level admission trace rather than inside maintainers' memory.
