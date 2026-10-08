# Snapshot send, expiry budget, and post-transfer lineage interface spec

## Purpose

The archive already has offer issuance, claim review, portable artifact inspection, and subject workspace grammar.
What it still lacked was one concrete interface contract for the small, convenient transfer that is **not** a live share:

> when the operator wants to send a file or small batch as a snapshot, what page makes clear that this is a one-time content handoff, not an enduring shared subject with future synchronization rights?

Current Resilio docs expose this seam well.
Single-file sharing is described as a one-time one-way transfer; if the shared files change, the transfer is invalidated and a new link must be generated; if the link expires, the files must be added again and a new link generated; there is no option to restrict usage count or ban specific devices from using the link; recipients can share the files further even though they cannot change the link expiration date; same-name collisions add `(1)`; and removing the entry from Sync UI does not necessarily remove the local file from the device.
That is practical.
It is also a perfect example of why AnonSync should give snapshot sends their own subject class.

## Core decision

A snapshot send must be represented as a first-class **snapshot transfer object**, not as a miniature live share.
The surface must say five things explicitly:

1. this transfer has a finite content snapshot
2. future source edits are out of scope unless a new transfer is issued
3. redemption budget and expiry are separate from content identity
4. downstream resharing, if allowed, is a distinct lineage event
5. UI removal and local-file retention are different actions

## The fixed review order

Every snapshot-send surface should render sections in this order:

1. **Transfer class and captured contents**
2. **Redemption budget and expiry**
3. **Receiver landing and collision behavior**
4. **Downstream rights and lineage**
5. **Post-transfer local retention truth**
6. **Receipt promise**

## 1) Transfer class and captured contents

Show:

- artifact label and stable snapshot-send ID
- whether the payload is one file or a bounded batch
- captured filenames, sizes, and snapshot timestamp
- explicit statement that future edits are not included
- whether the sender is issuing a fresh snapshot or reissuing the same captured bytes

The operator should be able to answer:

> am I offering a live subject, or only this captured set of bytes?

## 2) Redemption budget and expiry

This section should show:

- expiry time or `does not expire`
- redemption budget (single redemption, bounded count, or unbounded window)
- recipient scope or lack of recipient pinning
- what happens when budget or expiry is exhausted
- whether reissue preserves or changes the content snapshot

A snapshot-send surface should never make `same bytes, new time budget` look the same as `new bytes, new transfer`.

## 3) Receiver landing and collision behavior

Before a receiver accepts, show:

- default landing path
- whether same-name collisions create duplicates, block, require rename, or require review
- whether receipt of the transfer implies future sync, later fetchability, or only present download
- whether accepted files become normal local files, managed local artifacts, or claimed-but-not-yet-landed entries

A duplicate filename should not silently become the only visible cue that this was a separate snapshot object.

## 4) Downstream rights and lineage

The page must say plainly:

- whether recipients may reshare the received bytes
- whether downstream resharing preserves provenance to the original snapshot-send ID
- whether downstream resharing can widen recipient scope or only create sibling deliveries
- whether later edits by the recipient create a new lineage branch rather than modifying the original snapshot contract

Snapshot convenience should not erase where the bytes came from.

## 5) Post-transfer local retention truth

After completion, the product should keep distinct:

- transfer entry in UI
- local file on disk
- sender-side retained snapshot record
- receiver-side retained provenance record

Good actions include:

- `Remove transfer entry`
- `Delete local file`
- `Forget retained provenance after export`
- `Reissue snapshot`

The product should never rely on menu wording alone to teach whether removing an entry also removes bytes.

## 6) Receipt promise

The resulting receipt must prove:

- snapshot-send ID and payload digest set
- expiry and redemption budget
- landing path and collision resolution
- whether downstream resharing occurred
- whether local bytes were later removed or merely the UI entry was cleared

A later reader should be able to answer:

> was this a live share, a one-time snapshot, a reissue of the same snapshot, or a downstream derivative send?

## What must never happen automatically

The product must never automatically:

- imply future synchronization for a snapshot-send
- collapse expiry renewal into content continuity
- let downstream resharing sever provenance completely
- use filename duplication as the main explanation of collision handling
- equate hiding a transfer entry with deleting the local file

## Why this is worth the trouble

Small transfers are where convenience most easily smuggles in semantic ambiguity.
AnonSync can do better by making snapshot sends fast and friendly while still proving they are bounded content handoffs rather than under-specified mini-shares.
