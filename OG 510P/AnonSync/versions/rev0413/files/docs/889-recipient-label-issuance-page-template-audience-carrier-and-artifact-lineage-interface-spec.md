# Recipient-label issuance page: template, audience, carrier, and artifact lineage interface spec

## Purpose

This page owns the outward-label question:

> what label will recipients see on the thing I am about to issue, how was that label chosen, and does changing it alter the subject or only this artifact family?

## Core decision

Every outward invite, claimable artifact, QR, browser-open handoff, or comparable recipient-facing artifact that carries a human label must render one first-class **Recipient-label issuance** page before commit.

## Fixed page order

1. canonical subject strip
2. recipient-label proposal
3. carrier and artifact family card
4. older-artifact divergence card
5. issuance receipt promise

### 1) Canonical subject strip

Show:

- canonical subject title
- local alias on issuing seat if relevant
- current default recipient-label template
- strongest safe sentence

### 2) Recipient-label proposal

Show:

- label that the new artifact will carry
- why that label was chosen (`inherit canonical`, `inherit local alias`, `manual custom label`, `template`, `other`)
- whether this is a one-off or future default
- whether the label differs from canonical title

### 3) Carrier and artifact family card

Show:

- carrier (`QR`, `browser link`, `copyable token`, `local handoff`, `other`)
- artifact family
- whether carrier regeneration is required for the new label to really ship
- whether the label is sealed into the artifact or merely shown in the local send surface

### 4) Older-artifact divergence card

Mandatory when earlier artifacts for the same subject still exist.
Show:

- older labels still out in the world
- whether they remain valid
- whether they remain truthful, merely older, or actively misleading
- reissue options

### 5) Issuance receipt promise

The page must promise a receipt that preserves:

- canonical subject title at issuance time
- recipient-facing label actually shipped
- carrier and artifact family
- whether this was a one-off or template mutation
- what older artifacts were left untouched

## Rules

### Rule 1 — recipient label is never assumed canonical

The product must always distinguish `label recipients will see on this artifact` from `canonical subject title`.

### Rule 2 — one-off and default mutations are separate

A one-off issued label must not silently become the new future default.

### Rule 3 — carrier regeneration truth must be explicit

If a new QR or other carrier must be regenerated, the page must say so before issuance.

### Rule 4 — untouched older artifacts stay visible

The operator must see whether previous labels remain live in earlier artifacts.

## Acceptance criteria

A later operator can prove:

- what recipients were meant to see
- what the subject was canonically called at issuance time
- whether the issued label was one-off or template-derived
- which artifact family carried it
- whether older artifacts were intentionally left with older labels
