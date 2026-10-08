# Completeness confidence page: index, hash, source, and surface readiness interface spec

## Purpose

The archive already had readiness, transfer lanes, warning tiers, and hash-readiness work.
What it still lacked was one explicit page for this ordinary question:

> is the product's current view of this subject complete, or is it provisional because detection, hashing, scanning, or source availability is still lagging?

Current Resilio docs make this seam concrete.
They still say watcher quality depends on the storage, scheduled rescans run every 600 seconds by default, rescans can be disabled entirely by setting the interval to zero, only mtime/size are checked cheaply before rehashing, and some advanced settings defer or prioritize indexing work.
That is real operator truth.
It still lives mostly in FAQs and power-user tables.

## Core decision

AnonSync should expose a first-class **completeness confidence** object for every subject and every substantial subtree.
The object answers four questions:

1. have names been enumerated?
2. have payload bytes been verified / hashed as needed?
3. are required sources reachable for the missing parts?
4. how current is the surface relative to the local filesystem and the known mesh?

## Fixed review order

Every completeness-confidence page should render sections in this order:

1. **Scope of claim**
2. **Enumeration state**
3. **Verification state**
4. **Source reachability dependence**
5. **Freshness / watcher quality**
6. **Actions to raise confidence**

## 1) Scope of claim

State clearly whether the confidence applies to:

- the full subject
- this subtree only
- this list view only
- this metric only
- this seat only

A product must not overclaim completeness for the whole subject when only the current pane has been checked.

## 2) Enumeration state

Show whether the product currently has:

- no listing yet
- structural listing only
- full local enumeration
- announced remote structure but incomplete local confirmation

This section should say when names or directories are known before payload verification.

## 3) Verification state

Show whether the product has:

- verified payload hashes
- only mtime/size-based suspicion of change
- deferred hashing still pending
- pre-seeded bytes awaiting comparison
- placeholder-only entries not yet materialized

This is the page that should answer whether rename, dedup, conflict, and replay semantics are fully ready to trust yet.

## 4) Source reachability dependence

Say plainly whether higher confidence depends on:

- another peer coming online
- a full-copy witness existing somewhere
- a manual rescan or manual fetch
- waiting for background indexing to finish

Confidence is partly a local question and partly a reachability question.

## 5) Freshness / watcher quality

Show:

- whether filesystem notifications are healthy, degraded, or unavailable
- scheduled rescan cadence
- manual reverify option
- last verified time
- whether the surface may lag due to sleep, throttling, or disabled rescans

This section should make `current enough for browsing` distinct from `current enough for destructive decisions`.

## 6) Actions to raise confidence

Good actions include:

- `rescan now`
- `finish indexing now`
- `verify hashes for this subtree`
- `fetch missing members from source`
- `show confidence blockers`

Each action should say what kind of confidence it improves.

## Confidence classes

Use a small fixed set such as:

- **complete** — enumeration and needed verification are current for this claim scope
- **usable but provisional** — likely correct for browsing, not yet strong enough for destructive decisions without review
- **degraded** — known watcher/rescan/source blockers exist
- **unknown** — the product cannot currently justify a claim

## Receipt

A completeness receipt should prove:

- claim scope
- confidence class
- blockers
- verification state
- source dependencies
- last verified time

## What must never happen automatically

The product must never:

- present a provisional surface as authoritative without a confidence label
- hide watcher/rescan disablement when the operator is about to trust completeness
- imply payload verification from structure alone
- imply local completeness when remote-only members are still required for the claim
- make destructive decisions on a degraded confidence surface without a review step

## Resulting product doctrine

Completeness is not binary.
The interface must say whether it knows the names, the bytes, both, or neither — and how current that knowledge is.
