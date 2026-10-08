# Residual claim matrix page — local, linked, external, and history proof interface spec

## Purpose

The archive already had residual-authority, retained-byte, and severance-scope doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> what exact residue classes still exist after the action, and which claims do those classes support or contradict?

## Core decision

Every serious action claim must be backed by one first-class **Residual claim matrix** page.
That page is the semantic home of:

- residue classes
- claim support and contradiction
- return triggers
- history / archive survival
- external-retainer uncertainty
- strongest next action

The product must not bury these limits in expandable troubleshooting text.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. action-and-claim strip
2. residue matrix
3. return-and-reappearance card
4. claim contradiction card
5. escalation ladder
6. recent claim receipts
7. expert details drawer

### 1) Action-and-claim strip

Show:

- action object
- executed action class
- approved safe statement
- strongest next-safe action
- whether the page is previewing residue or reviewing already-applied residue

The strip should answer `what action and claim am I checking?`

### 2) Residue matrix

Rows should cover at least these planes:

- local materialized bytes
- local placeholders / stubs / metadata residue
- linked-cohort presence
- external known retainers
- external possible retainers
- history / archive survival
- approval / artifact residue
- row reappearance potential

Columns should cover:

- state now
- proof strength
- claim supported
- claim contradicted
- next way to reduce this residue

### 3) Return-and-reappearance card

Show:

- whether a hidden row may return
- whether a disconnected seat can reconnect
- whether a linked cohort can rematerialize the subject
- whether an offline retainer can later replay state
- whether return is impossible, unlikely, unresolved, or expected

This card should answer `what can still come back later?`

### 4) Claim contradiction card

Show the strongest contradiction sentences, for example:

- `Data no longer exists` contradicted by `Archive retains candidates for 30 days.`
- `Seat cannot return` contradicted by `Row is hidden, not retired.`
- `Access is gone everywhere` contradicted by `External retainer remains out of linked-cohort scope.`

This card should answer `why can’t I say the stronger thing?`

### 5) Escalation ladder

Offer a reduction ladder such as:

1. keep current statement
2. add caveat
3. notify affected audience of residual scope
4. perform stronger local cleanup
5. revoke additional artifact families
6. rotate identity / authority epoch

### 6) Recent claim receipts

Show recent receipts with:

- action object
- safe statement
- strongest contradiction
- largest remaining residue plane
- next action taken

### 7) Expert details drawer

Hide peer IDs, archive record references, retention policy internals, and low-level state witnesses behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. residue plane
2. state phrase
3. claim effect phrase
4. reduction path

Example:

```text
External retainer plane · possible non-linked holder remains · contradicts “gone everywhere” · Stronger scope requires new containment review
```

## Mandatory fields

- `action_ref`
- `executed_action_class`
- `approved_statement`
- `residue_planes[]`
- `proof_strength_by_plane{}`
- `supported_claims[]`
- `contradicted_claims[]`
- `return_trigger_summaries[]`
- `largest_remaining_residue_plane`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- see all major residue classes at once
- tell which claims are supported versus contradicted by each residue plane
- predict which rows or bytes may return later
- move directly into stronger cleanup or escalation without reopening the whole action review
