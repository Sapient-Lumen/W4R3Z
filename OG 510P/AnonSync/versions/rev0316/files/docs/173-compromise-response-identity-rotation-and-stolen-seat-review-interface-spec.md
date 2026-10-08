# Compromise response, identity rotation, and stolen-seat review interface spec

## Purpose

The archive already has compromise cases, retirement records, successor replacement, and seat/root attribution.
What it still lacked was one concrete interface contract for the hardest trust break in a sync system:

> when a device is stolen, suspected compromised, or no longer trustworthy, what page tells the operator whether to hide it, quarantine it, revoke it, replace it, rotate identity material around it, or rebuild a wider trust boundary altogether?

Current Resilio docs make this seam sharper than the earlier route or rights seams.
If a device is stolen and its drive was not encrypted, the docs say the thief may be able to view, modify, or remove data on other linked devices.
The documented response is broad: back up data, remove shares, unlink the remaining devices from the current identity, remove synced data from the storage folder, reinstall Sync, regenerate identity, relink devices, and reshare folders.
Those same linking docs also say you cannot remotely unlink other devices.
That is serious and candid support guidance.
It is not the interface contract AnonSync should inherit.

## Core decision

A suspected compromise or stolen seat must open a first-class **compromise response review**.
The product should never treat `this member may be hostile now` as equivalent to `unlink things until the mesh looks clean again`.

The review must distinguish at least these response shapes:

1. **Cosmetic hide only** — remove clutter from views but preserve trust
2. **Operational quarantine** — stop new trust, publication, or approvals from the suspect seat while preserving evidence
3. **Authority revocation** — revoke the seat or member from current subjects without rotating the whole constellation
4. **Successor replacement** — retire one seat and explicitly anoint another as its successor
5. **Identity rotation** — rotate identity-bearing material because the old one may now be exposed
6. **Full continuity rebuild** — preserve bytes and receipts where possible while reissuing trust roots and live artifacts

## Why this matters

Current Resilio docs still reveal four truths AnonSync should not clone:

- a compromised linked device can still threaten other linked devices
- you cannot remotely unlink the suspect device
- the documented remedy is often identity-wide teardown and reissue
- license and share continuity are repaired partly by reinstall, relink, and reshare ritual

AnonSync should therefore make compromise response read like a reviewed trust-boundary decision, not like support-driven reinstallation folklore.

## The fixed review order

Every compromise response review should render sections in this order:

1. **Incident classification and current evidence**
2. **Potential blast radius**
3. **Continuity the operator may still want to preserve**
4. **Admissible response shapes**
5. **Reissue and dependent fallout**
6. **Receipt promise**

## 1) Incident classification and current evidence

Show:

- suspect seat / member label and stable handle
- whether the trigger is stolen device, lost control, malware suspicion, credential leakage, forensic uncertainty, or planned secure retirement
- current last-seen and last-acted facts
- whether disk encryption, screen lock, and local secret protection are known, unknown, or absent
- whether the seat is currently reachable, offline, hidden, quarantined, or still trusted

The operator should be able to answer:

> what exactly happened, how certain are we, and is this a safety incident or just inventory cleanup?

## 2) Potential blast radius

This section should enumerate the authority surface that may have been exposed:

- linked-constellation identity material
- current writable subjects
- approval capability
- onward delegation or share issuance capability
- stored recovery material
- locally materialized plaintext bytes
- route/publication posture that may expose endpoint or membership facts

The page should not flatten all incidents into one red banner.
It should say what the suspect seat could plausibly still do if it comes online.

## 3) Continuity the operator may still want to preserve

Show separately what can survive the response:

- healthy seats that remain trusted
- local bytes that should be retained
- subject handles and receipts that may be preserved through successor review
- offers, grants, or approvals that can be reissued cleanly
- state roots that are evidence-bearing and should be sealed instead of deleted

A compromise response is not only about destruction.
It is also about preserving good continuity while cutting away bad trust.

## 4) Admissible response shapes

Primary actions should be explicit and semantically narrow:

- `Hide from views only`
- `Quarantine suspect seat`
- `Revoke seat from current subjects`
- `Replace with reviewed successor`
- `Rotate constellation identity material`
- `Reissue grants and offers under new authority epoch`
- `Open full rebuild plan`

The product should never imply that `reinstall everything` is the only intelligible operator action when a narrower honest response exists.

## 5) Reissue and dependent fallout

Show fallout on:

- linked-member trust records
- outstanding offers and claim artifacts
- approval memory
- share authority epochs
- same-machine children of the suspect seat
- recovery bundles and encrypted replicas
- diagnostic/evidence bundles created for the incident

For each, say whether it will be:

- preserved
- sealed as evidence
- revoked
- reissued
- translated to a successor
- blocked pending broader rotation

## 6) Receipt promise

The resulting receipt must prove:

- incident class
- suspect seat and chosen response shape
- preserved versus revoked continuity
- whether identity or authority material rotated
- which offers, grants, approvals, and receipts were reissued or sealed
- what successor, if any, replaced the old seat

A later reader should be able to answer:

> did we merely hide a stale laptop, revoke a risky member, or rotate the trust boundary because a stolen seat could still act?

## What must never happen automatically

The product must never automatically:

- treat a compromise incident as mere list hygiene
- delete evidence-bearing local state before the operator chooses a response shape
- keep using exposed approval or issuance material just because the suspect seat is offline
- equate `offline` with `safe now`
- imply that successor replacement is the same as trust rotation

## Why this is worth the trouble

Incident response is where convenience-first sync tools most obviously run out of interface vocabulary.
AnonSync can do better by making stolen-seat and compromise response one reviewed trust workflow whose receipts preserve what is still good while proving what authority was actually cut away.
