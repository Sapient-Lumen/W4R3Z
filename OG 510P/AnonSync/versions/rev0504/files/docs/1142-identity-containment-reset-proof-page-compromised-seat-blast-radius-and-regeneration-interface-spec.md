# Identity containment reset proof page: compromised-seat blast radius and regeneration interface spec

## Purpose

This page exists where one linked seat is lost, stolen, misnamed, or otherwise no longer trusted.
It answers one ordinary question:

> is hide or unlink enough, or is the honest containment move a full identity reset with storage cleanup, relicensing, relinking, and resharing?

## When this page must appear

Trigger this page for:

- stolen or compromised linked devices
- identity-regeneration workflows
- business-license ownership disputes across identities
- any case where the operator is tempted to treat `hide offline device` as containment

## Fixed page order

1. containment-proof header
2. blast-radius and action-class card
3. regeneration sequence card
4. entitlement and survivor card
5. receipt/export rail

### 1) Containment-proof header

Show:

- compromised / untrusted seat
- current graph scope
- containment verdict (`hide only`, `local unlink only`, `identity reset required`, `license-owner override needed`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### 2) Blast-radius and action-class card

Render rows for:

- hide-offline effect (`visibility only`)
- unlink effect (`this seat leaves graph; remote seats unchanged`)
- remote-unlink availability (`not supported`, `unknown`)
- whether compromise still threatens other linked seats if disk/runtime are accessible

### 3) Regeneration sequence card

Show the reviewed ladder:

1. back up needed data
2. remove shares from Sync as appropriate
3. unlink trusted seats from the compromised identity
4. stop Sync and clear synced data from storage where required
5. reinstall / remove settings where required
6. generate a new identity
7. relink trusted devices
8. reshare subjects
9. reapply or reclaim license ownership if needed

### 4) Entitlement and survivor card

Show:

- business-license owner class
- ownership-steal / reclaim risk
- whether filesystem bytes survive despite graph reset
- whether graph trust is restored only after relink and reshare, not merely after uninstall

### 5) Receipt/export rail

Offer:

- `Emit identity lineage receipt`
- `Open identity-graph adoption contract sheet`
- `Open certificate takeover review`

## Rules

### Rule 1 — hide may not masquerade as containment

If a cleared offline device can simply reappear later, the page must say so.

### Rule 2 — regeneration must stay visibly stronger than unlink

A new certificate / identity is a graph reset, not a cosmetic refresh.

### Rule 3 — entitlement recovery must stay explicit

License-owner theft, override, reclaim, or reapply steps may not hide inside generic cleanup language.
