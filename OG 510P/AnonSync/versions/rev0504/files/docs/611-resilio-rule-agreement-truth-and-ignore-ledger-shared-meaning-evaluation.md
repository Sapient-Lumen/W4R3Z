# Resilio rule-agreement truth and ignore-ledger shared-meaning evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- the current IgnoreList article still says excluded files are not indexed and are not counted in the Size column
- the same article still says having the same IgnoreList on all peers is `advisable, but not compulsory`
- the same article still says IgnoreList is case sensitive
- the same article still says path delimiters differ by operating system
- the same article still says ignore rules do not work for files already synced
- the same article still says structural information is still passed until disconnect
- the current troubleshooting page still says the Ignore list `must be the same on all peers` so they all agree on what shall be skipped
- the current v3 line still appears active through `3.1.2.1076`

That is useful candor.
Resilio is not pretending ignore rules are simple.
The problem is that the operator still has to reconstruct **what kind of agreement is actually being claimed**.

## What still should not be cloned

The ordinary operator question is simple:

> if this material is ignored here, what exactly is still true everywhere else?

Current official docs still leave that answer spread across IgnoreList mechanics and troubleshooting guidance.
That means one local rule can quietly mix several different truths:

- local indexing exclusion
- local size/accounting exclusion
- future-only omission
- already-synced residue still present
- structural carryover until disconnect
- peer-meaning divergence

Those are all real and useful distinctions.
They just should not remain implicit.

The current clone-veto sentence for this seam is therefore:

> borrow Resilio's candor that ignore rules have real indexing, accounting, and retroactivity semantics; refuse any interface contract where the operator still has to infer whether rule drift is harmless local variance or unsafe shared-meaning disagreement.

## Why this matters for AnonSync

AnonSync should borrow four habits directly:

- say whether a rule is local only or expected to match across peers
- say what accounting and visibility consequences follow locally
- say whether the rule is future-only or leaves already-synced residue in scope
- say what stronger sentence the rule does **not** earn

But AnonSync should refuse four weaker habits:

- treating local exclusion as proof of shared agreement
- hiding rule drift until bytes or counts diverge
- letting retroactivity remain folklore
- making operators reconcile conflicting advice phrases on their own

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `612` — Rule agreement
- `613` — Drift-class review
- `614` — Rule retroactivity
- `615` — Rule agreement receipt

These pages keep the Resilio candor and reject the under-owned shared-meaning contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that IgnoreList changes indexing, counting, and future intake semantics; refuse any interface contract where `ignored here` can sound like `ignored everywhere` without ledger-equivalence proof and residue disclosure.
