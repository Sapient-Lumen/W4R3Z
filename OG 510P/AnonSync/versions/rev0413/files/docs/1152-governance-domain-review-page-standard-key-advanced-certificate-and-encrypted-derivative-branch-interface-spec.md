# Governance-domain review page: Standard key domain, Advanced certificate domain, and encrypted-derivative branch interface spec

## Purpose

This page exists for the moment an operator is choosing among Standard, Advanced, and encrypted-derivative subjects.
It answers one ordinary question:

> what governance system is each option actually built on, what kind of peer identity does it understand, and what later operations does that architecture make possible or impossible?

## When this page must appear

Trigger this page for:

- creation of a new sync subject
- branching a subject into an encrypted copy
- any design review that compares Standard and Advanced as if they were interchangeable
- any workflow that promises later permission mutation or identity-aware delegation

## Fixed page order

1. governance intent header
2. architecture comparison card
3. peer-identity visibility card
4. operator consequences card
5. next-safe branch rail

### 1) Governance intent header

Show:

- requested architecture family
- comparison cohort (`standard vs advanced`, `advanced vs encrypted derivative`, `all three`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Architecture comparison card

Render rows for:

- primitive (`random key`, `digital certificate / PKI`, `encrypted receive/store key`, `unknown`)
- permission model (`reissue by new key`, `owner-governed mutable permissions`, `hardwired RO+encrypted`, `unknown`)
- owner semantics (`none`, `present`, `not meaningful`, `unknown`)
- in-family security posture (`key bearer`, `certificate-bearing peer`, `untrusted backup peer`, `unknown`)

### 3) Peer-identity visibility card

Show the reviewed distinction between:

- device-level peer visibility only
- user-level grouping by certificate
- linked-device owner/default visibility
- encrypted derivative that seeds but does not meaningfully author or reveal cleartext

### 4) Operator consequences card

Possible warnings:

- `Standard shares delegation power through possession of a key, not Owner status`
- `Advanced enables owner-only sharing and on-the-fly permission changes`
- `Encrypted derivative is not a normal readable participant`
- `Config-mode authorship is standard-only`
- `True RO on linked devices may require leaving the linked lane and creating a Standard-key exception`

### 5) Next-safe branch rail

Offer:

- `Open authority and re-share review`
- `Open architecture migration watch`
- `Emit subject architecture lineage receipt`

## Rules

### Rule 1 — the page must compare governance, not marketing tiers

`Free / Pro / Trial` may appear, but it cannot replace the governance comparison.

### Rule 2 — encrypted derivative must stay visibly non-equivalent

It must not be presented as merely `Advanced with more privacy`.

### Rule 3 — peer visibility and delegation have to stay distinct

The fact that Advanced can see users via certificate does not by itself describe who can delegate or mutate permissions.
