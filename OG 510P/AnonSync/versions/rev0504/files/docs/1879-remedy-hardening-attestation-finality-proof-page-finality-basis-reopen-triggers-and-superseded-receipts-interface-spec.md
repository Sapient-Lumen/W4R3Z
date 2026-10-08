# Remedy-hardening-attestation-finality proof page — finality basis, reopen triggers, and superseded receipts

## Purpose

This page is the durable proof that a ruling's closure class was evaluated under explicit finality, reopenability, and supersession rules.
It must let a later verifier see not only that a ruling once existed, but how durable it was, who could rely on it, and whether a later receipt displaced it.

## Sections

### 1) Finality header

Publish:

- case identifier
- source challenge receipt identifier
- adjudicated surviving sentence
- current finality class
- current reliance audience class
- current precedence owner

### 2) Finality basis

List the concrete basis for the current class:

- decisive witness durability grade
- same-world continuity result
- reopen horizon result
- evidence retention result
- support-lane dependency result
- restart or rebuild contamination result
- later contradiction sweep result

### 3) Reopen trigger table

For each possible reopen trigger print:

- trigger name
- current status
- witness that would trip it
- witness that would disarm it
- whether the trigger belongs to this receipt or was inherited from an earlier one

### 4) Supersession and precedence map

The proof must print receipt relationships explicitly:

- predecessor receipt
- successor receipt, if any
- whether this receipt still owns live precedence
- whether this receipt remains historical-only
- whether both receipts remain valid for different worlds or audiences

### 5) Reliance sentence ladder

The proof must print the sentence ladder explicitly:

- adjudicated surviving sentence
- sentence currently speakable outwardly
- strongest blocked permanence sentence
- strongest blocked stronger sentence

Example proof outputs:

- `adjudicated but reopenable; live use allowed for internal investigators only`
- `final on current record; appeal window lapsed and decisive evidence preserved, but broader external reliance still blocked`
- `superseded by successor-world receipt; predecessor receipt remains historical only`
- `non-reopenable at narrowed historical-integrity floor; current-world trust sentence stays blocked`

### 6) Claim ceilings

The page must explicitly forbid false upgrades such as:

- `resolved permanently` when reopen triggers remain armed
- `same receipt still governs` when a successor receipt outranks it
- `same world remained continuous` when ruling depended on rebuild or fresh instance creation
- `all consumers may rely` when the ruling is audience-qualified only
- `final` when the basis is merely absence of visible contradiction
