# Offline roster visibility review page: hide, clear, reappear, and observation ceiling interface spec

This page exists so `offline`, `hidden`, and `gone` stop pretending to mean the same thing.
The operator often wants a cleaner roster, but that is not the same as unlinking a seat or proving it no longer matters.

## Operator question

> did we actually sever this relationship, or did we only suppress its record from view until it shows up again?

## When this page must appear

Render whenever the product is about to:

- hide or clear an offline peer or device record
- infer that a silent seat is irrelevant now
- promise that the roster is clean after uninstall or unlink
- down-rank an old peer observation
- merge multiple stale records into one visible summary

## Fixed page order

1. **Current record verdict**
2. **Observation basis**
3. **Reappearance triggers**
4. **Roster-trust ceiling**
5. **Blocked stronger sentence**

## 1) Current record verdict

Show one verdict:

- `offline record remains visible`
- `offline record hidden from ordinary view`
- `record removed from this roster scope`
- `record lineage unresolved`
- `record may still persist on remote rosters`

The operator must be able to answer: **what happened to the record, not just the device?**

## 2) Observation basis

Possible observation classes include:

- last successful online witness
- roster-only stale record
- uninstall cleanup declaration
- self-unlink witness
- remote revocation witness
- no recent corroboration

Each row must show freshness, scope, and whether it supports only decluttering or an actual trust change.

## 3) Reappearance triggers

Show possible return paths such as:

- same device comes online again
- same identity resumes announcements
- stale record imported from another linked seat
- manual reconnect or relink
- unresolved duplicate-seat / successor-seat ambiguity

Each trigger row must show whether it needs new approval, old standing approval, or unknown approval basis.

## 4) Roster-trust ceiling

Publish separate ceilings for:

- visual absence
- identity severance
- byte irrelevance
- permission irrelevance
- historical evidence retention

Examples:

- a hidden record may still have standing approval history
- a removed linked-family record may still correspond to a remote peer with local bytes
- a roster that looks clean may still be missing cross-seat corroboration

## 5) Blocked stronger sentence

Allowed examples:

- `This offline record was hidden from view only.`
- `No recent witness proves the device still participates.`
- `The record can reappear if the same device resumes announcements.`

Blocked examples:

- `The device no longer exists.`
- `This relationship is fully severed everywhere.`
- `The absence of a row proves the absence of a peer.`

## Main actions

Examples:

- `Hide clutter only`
- `Escalate to unlink / revoke review`
- `Compare remote rosters`
- `Export roster-visibility receipt`
