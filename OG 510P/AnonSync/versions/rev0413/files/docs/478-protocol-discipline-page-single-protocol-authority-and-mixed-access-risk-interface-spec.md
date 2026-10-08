# Protocol discipline page: single-protocol authority and mixed-access risk interface spec

## Purpose

This page answers:

> which protocol or mutation lane is authoritative for this namespace, what mixed-access pattern is currently present or proposed, and what exact corruption or rollback risk comes with violating that discipline?

The page exists because `can access folder` is not the same thing as `may safely co-author it through any path available`.

## Core rule

Every subject whose bytes may be touched through more than one protocol or access lane must compile to one first-class **Protocol discipline** page before the product treats that arrangement as safe.
That page owns:

- authoritative mutation lane
- observed or proposed alternate lanes
- mixed-access risk
- mitigation or block decision
- discipline receipt

## Primary layout

The page always renders the same regions:

1. discipline verdict
2. authoritative-lane card
3. alternate-lane card
4. risk and mitigation card
5. receipt and follow-on links

### 1) Discipline verdict

Show:

- verdict label: `single-lane-safe`, `mixed-read-only`, `mixed-mutation-risk`, `rollback-risk`, `unknown`
- strongest honest one-line summary
- authoritative protocol / lane
- one safest next action

### 2) Authoritative-lane card

Show:

- authoritative protocol (`local fs`, `smb`, `sync service`, `app sandbox`, `unknown`)
- who may mutate through that lane
- who may only observe through that lane
- why that lane is authoritative here

The operator must be able to answer: **which path gets to author truth for this namespace?**

### 3) Alternate-lane card

Show:

- any additional access lane presently detected or intentionally allowed
- whether that lane is read-only observation, ordinary user access, or true mutation
- path overlap with the authoritative lane
- strongest incompatibility signal

The operator must be able to answer: **what other way are these same bytes being touched?**

### 4) Risk and mitigation card

Show:

- risk class (`corruption`, `rollback`, `lock contention`, `freshness skew`, `unknown`)
- strongest evidence behind the risk
- allowed mitigation ladder, such as:
  - keep one protocol authoritative
  - downgrade alternate lane to read-only observation
  - isolate namespaces
  - reject subject admission
- explicit non-effects of the chosen mitigation

The operator must be able to answer: **why is mixed access dangerous here, and what exact change would make it acceptable?**

### 5) Receipt and follow-on links

Link to:

- Network path class
- Detection grade
- Network subject admission

After any accepted action, emit a receipt that preserves:

- authoritative lane reviewed
- alternate lanes present or rejected
- risk class acknowledged
- mitigation chosen or explicit abstention
- residual risk after the decision

## Honest outputs

This page may conclude:

- `single SMB lane authoritative · direct-on-host mutation forbidden`
- `NAS direct access plus Samba access detected · corruption/rollback risk · reject admission`
- `alternate lane read-only only · mixed mutation not allowed`
- `authority lane unknown · cannot claim safe co-authoring`

It may not collapse these into one generic `multiple apps may access files` warning.

## Rules

### Rule 1 — one mutation lane must be first-class

If multiple protocols can change the same namespace, the product must name one as authoritative or block the arrangement.

### Rule 2 — read-only observation and mutation must not blur

A second lane that only observes is a different contract from one that writes.
Do not hide both under `external access`.

### Rule 3 — rollback risk needs product-owned language

If an arrangement can roll back third-party changes or corrupt data, the interface must state that directly rather than burying it in a support article.

### Rule 4 — mitigations need non-effects

If the product recommends isolating writes to one protocol, it must say what remains allowed: e.g. `SMB browsing remains allowed; direct mutation does not`.

## Event language

Use explicit phrases such as:

- `protocol discipline violated; same bytes mutated through direct host path and Samba path`
- `alternate lane downgraded to read-only observation`
- `rollback risk remains because authoritative lane not isolated`
- `subject admission rejected until one mutation lane is chosen`

Avoid vague lines such as:

- `external apps may interfere`
- `compatibility issues possible`
- `unexpected changes detected`

## Non-clone reason

Current official Resilio docs are usefully candid that direct-on-host access mixed with Samba access can damage or roll back files.
But the operator still has to infer the actual discipline contract from cautionary prose.
AnonSync should instead expose one Protocol discipline page where authoritative lane, alternate lanes, risk class, and mitigation stay adjacent.
