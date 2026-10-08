# Restore, history, archive, and share-safe reintroduction interface spec

## Purpose

The archive already has history entries, restore candidates, rollback receipts, and file-intent reviews.
What it still lacked was one concrete interface contract for the moment an operator needs a real file back:

> when bytes disappeared or a prior version is needed, what page shows candidate versions, who changed what, where those bytes currently live, and whether putting them back is a local restore, a share mutation, or a fork for inspection?

Current Resilio docs make this seam unusually concrete.
Archive versions still live in hidden `.sync/Archive`, only manual restoring is possible, the restoring peer must be running at the right moment or the file may be archived again as older, Archive stores remote-changed prior versions rather than acting as a complete local version ledger, and Archive itself does not tell you which peer made the change — the docs tell you to learn that from History.
That is candid behavior documentation.
It is not a recovery contract AnonSync should clone.

## Core decision

Restore must be a first-class **reintroduction review**, not a file-manager ritual.
One surface must keep candidate bytes, provenance, and blast radius together.

The review must distinguish at least:

1. **Local-only restore** — recover bytes for inspection without changing shared state
2. **Share reintroduction** — restore bytes back into the live subject with explicit mutation scope
3. **Forked comparison restore** — recover into a side path for diff/inspection
4. **Blocked restore** — bytes exist, but the requested reintroduction would be misleading or unsafe without more review

## Why this matters

Current Resilio docs still split restore meaning across too many places:

- hidden service directories for the bytes
- separate History for who changed them
- sync runtime state for whether reintroduction will propagate correctly
- platform-specific visibility limits for Archive access

AnonSync should therefore make restore read like one reviewed change to live or local state, not a successful scavenger hunt.

## The fixed review order

Every restore or reintroduction review should render sections in this order:

1. **Missing or changed path answer**
2. **Candidate bytes and source locations**
3. **Provenance and authorship**
4. **Chosen reintroduction shape**
5. **Freshness and propagation guardrails**
6. **Receipt promise**

## 1) Missing or changed path answer

Show:

- current path or path tombstone
- whether the trigger is deletion, overwrite, conflict adjudication, historical inspection, or accidental cleanup
- current live-subject status for that path
- whether the requested recovery target is local-only or share-visible

The operator should be able to answer:

> what exactly is missing or wrong now, and am I trying to inspect old bytes or publish them back into the live subject?

## 2) Candidate bytes and source locations

List candidate versions with:

- version ID / restore candidate ID
- content timestamp and capture reason
- where the bytes currently live
- whether the copy is plaintext, encrypted-only, placeholder-backed, or remote-only
- retention horizon and deletion risk

The operator should not have to browse hidden folders to know what restore options even exist.

## 3) Provenance and authorship

For each candidate, show:

- actor or seat that last changed the path, when known
- whether the candidate came from local history, remote-preserved archive, rollback bundle, or incident evidence
- whether provenance is complete, partial, or unknown
- what continuity claim is strongest: same live line, side branch, or orphaned recovered bytes

Archive bytes without authorship are still useful, but the surface should say when the authorship answer depends on another evidence source.

## 4) Chosen reintroduction shape

Primary actions should be explicit:

- `Restore locally only`
- `Restore into comparison fork`
- `Restore into live subject`
- `Restore as replacement after review`
- `Export recovered bytes`

The UI should never hide whether the operator is merely recovering a file for themselves or republishing it to peers.

## 5) Freshness and propagation guardrails

Before apply, explain:

- whether the candidate is older than current live state
- whether reintroduction will create a local-only fork, a live overwrite, or a merge review
- whether the system currently has enough source/presence confidence to propagate the result
- whether any settlement or conflict guardrail must be satisfied first

The product should not require the operator to know that `have Sync running now` is part of successful restore semantics.
That guardrail belongs in the product surface.

## 6) Receipt promise

The resulting receipt must prove:

- candidate chosen
- provenance and authorship quality
- reintroduction scope
- whether peers were affected
- resulting live-path status
- any fork, comparison, or preservation path created

A later reader should be able to answer:

> did we inspect old bytes, fork them, or intentionally restore them back into the shared subject?

## What must never happen automatically

The product must never automatically:

- hide restore behind filesystem spelunking
- flatten local-only recovery into live-share mutation
- reintroduce old bytes without saying whether they will propagate
- separate provenance from restore choice so thoroughly that the operator restores blind
- imply that the absence of authorship means the bytes are untrustworthy or vice versa

## Why this is worth the trouble

Restore is where sync products often reveal whether they actually model recovery or merely document it.
AnonSync can do better by giving file recovery one page that keeps bytes, provenance, and share-visible consequence in one reviewed decision.
