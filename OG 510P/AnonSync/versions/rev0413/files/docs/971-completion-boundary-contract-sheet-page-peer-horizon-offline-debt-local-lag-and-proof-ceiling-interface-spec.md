# Completion boundary contract sheet page — peer horizon, offline debt, local lag, and proof ceiling

## Purpose

Give the operator one canonical answer to:

> complete relative to whom, with what excluded debt, and with what proof ceiling?

This page exists specifically so the product never reduces completion truth to a green glyph, a quiet queue, or a recent transfer timestamp.

## Core objects shown

### 1. Claim sentence

A single human sentence at the top, for example:

- `Complete for all currently connected writable peers; freshness for offline peers unproven.`
- `Locally indexed and transferred to reachable quorum; two intended peers remain outside horizon.`
- `No completion claim available; local detection lag still open.`

### 2. Peer horizon panel

Shows explicit membership buckets:

- connected peers in scope
- known offline peers still in scope
- peers excluded by operator choice
- peers excluded by horizon policy
- expired / hidden / forgotten peers whose previous membership still matters historically
- unknown-source / ghost-risk peers if relevant

Each bucket shows counts and named members.

### 3. Offline debt panel

Lists the debt that prevents stronger claims:

- offline intended peers
- peers with stale last-proof age
- peers whose source eligibility is unknown
- peers hidden from the active horizon by expiry or policy
- peers blocked by route / storage / lock / eligibility gates

### 4. Local lag panel

Shows whether local truth is fully surfaced yet:

- filesystem notifications healthy / degraded / absent
- scheduled rescan cadence
- manual rescan pending
- indexing / hashing / merge debt
- write backlog or locked-file blockage if relevant

### 5. Proof ceiling panel

Enumerates the strongest sentence currently allowed, such as:

- `connected-peer transfer complete`
- `known-peer completion pending offline debt`
- `local scan complete but remote freshness unproven`
- `transfer quiet only — do not infer completion`

Also shows the stronger blocked sentence, for example:

- `all intended peers are complete`
- `globally fresh`
- `no further local work remains`

## Required fields

- subject name and subject identifier
- current completion class
- current freshness class
- peer horizon policy name
- proof timestamp
- proof basis vector
- invalidators since proof
- offline debt count
- local lag count
- stronger rejected sentence

## Interaction rules

- Clicking any count opens the exact member list; no hidden aggregate-only counts.
- A green visual style may appear only after the claim sentence is already specific.
- The page never uses `synced` unqualified.
- Any change in peer-horizon policy or peer membership supersedes the displayed sentence.
- Hidden or expired peers remain inspectable in historical context.

## Empty / degraded states

If the system lacks enough evidence, the page must say so plainly:

- `Cannot prove completion because local scan freshness is stale.`
- `Cannot prove beyond connected peers because intended peer set is unresolved.`
- `Completion blocked by internal work debt.`
