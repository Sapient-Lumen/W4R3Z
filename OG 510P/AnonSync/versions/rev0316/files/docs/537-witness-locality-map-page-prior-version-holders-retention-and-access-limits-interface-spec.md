# Witness locality map page: prior-version holders, retention, and access limits interface spec

## Purpose

This page answers one ordinary operator question:

> where do the recoverable prior bytes actually live right now, and which seats can honestly be used to inspect, export, or replay them?

The page exists because `there is an older version somewhere` is not one fact.
It decomposes into at least:

- which seat holds the prior bytes
- whether the bytes are still within retention
- whether that seat can expose them through the current surface
- whether the current seat can perform replay itself or only nominate another host

## Core decision

Every history-bearing product with distributed recovery witnesses must own one first-class **Witness locality map** page.
That page is the semantic home of:

- prior-version holder enumeration
- per-seat retention and access posture
- recovery-host suitability
- authorship gap visibility
- honest next recovery lane

The operator must not have to infer recovery locus from hidden directories, platform folklore, or stale assumptions that the mutating seat kept its own old version.

## Primary page layout

The page always renders the same regions in the same order:

1. subject strip
2. current-seat answer card
3. witness-seat table
4. access and retention card
5. authorship-gap card
6. recovery-host recommendation card
7. recent recovery-locus receipts
8. expert details drawer

### 1) Subject strip

Show:

- subject path / object label
- current live status (`present`, `missing`, `newer-than-desired`, `conflicted`, `deleted-live`)
- acting seat
- strongest honest witness summary (`remote-witnessed`, `local-witnessed`, `multi-seat-witnessed`, `history-only`, `no-known-bytes`)
- safest next action

The strip should answer `what subject am I trying to recover and is there any known prior witness at all?`

### 2) Current-seat answer card

Show:

- whether this seat holds a recoverable prior version now
- if not, why not (`initiator-did-not-keep-old-version`, `retention-expired`, `access-surface-missing`, `history-only`, `unknown`)
- whether this seat can still inspect metadata, nominate another recovery host, or perform only export-free coordination
- whether local trash / recycle-bin recovery is a separate better path

This card should answer `can I solve this from the seat I am already on?`

### 3) Witness-seat table

Each row represents one seat that might hold the prior bytes.
Show columns for:

- seat label
- witness class (`prior-version`, `deleted-copy`, `rename-continuity`, `conflict-copy`, `unknown`)
- byte posture (`plaintext`, `ciphertext-only`, `history-only`, `unconfirmed`)
- retention horizon
- last witness time
- platform reach (`desktop-ui`, `webui`, `android-filesystem`, `ios-no-archive-access`, `offline-seat`, `connector-only`)
- recovery suitability (`inspect`, `export`, `live-replay`, `not-suitable`)

This table should answer `which seats actually hold the useful bytes and what can they honestly do with them?`

### 4) Access and retention card

Show:

- default and custom retention where known
- whether candidate size exceeds local versioning ceiling
- whether the witness is reachable through the current channel or only a different one
- whether the bytes are at risk of near-term expiry or inaccessible mobile storage
- whether Archive is currently serving continuity for rename/move behavior as well as recovery

This card should answer `are these bytes still meaningfully available or just theoretically present?`

### 5) Authorship-gap card

Show:

- whether the witness source already knows who changed the file
- whether the operator must join to History for authorship or chronology attribution
- completeness of the join (`complete`, `partial`, `archive-only`, `history-only`, `unknown`)
- one next honest verb (`open authorship bridge`, `continue with bytes only`, `export witness without actor claim`)

This card should answer `what evidence do I still lack even if the bytes exist?`

### 6) Recovery-host recommendation card

Show only the strongest honest next host choice such as:

1. `Recover from this desktop now`
2. `Nominate remote desktop as recovery host`
3. `Use WebUI to export only`
4. `Switch to desktop surface for live replay`
5. `Open History join before actor claim`
6. `Cancel because no recovery witness remains`

This card should answer `where should the recovery actually happen?`

## Non-negotiable rules

### Rule 1 — witness locality must be visible before restore verbs

The product may not show a confident `Restore` action before it shows where the candidate bytes actually live.

### Rule 2 — current seat insufficiency must be explicit

If the acting seat cannot perform replay because it lacks bytes or lacks archive access, the page must say so directly.

### Rule 3 — access surface is part of recovery truth

`Witness exists` and `witness is reachable through this surface` are different facts and must stay separate.

### Rule 4 — authorship gaps may not be hidden by archive confidence

Byte evidence must not be used to imply actor attribution the archive source does not contain.

## Honest outputs

The page may conclude:

- `A prior version exists, but only on a remote desktop seat; this seat can nominate that host and inspect metadata, not replay.`
- `The current seat has no prior-version witness because it authored the change; another linked seat retains the old version for 11 more days.`
- `Prior bytes exist on Android storage, but the current channel cannot safely replay them; export or desktop-hosted recovery is the honest lane.`
- `History proves a likely actor, but no recoverable bytes remain anywhere.`
