# Reset impact page: reset path, storage rehome, and preservation verdict interface spec

## Purpose

The archive already has strong recovery and storage-root doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if I use this reset / password-recovery / service-world / rehome path, what exactly will survive, what will reset, and what new roster or re-share work am I buying?

## Core decision

Every serious recovery system must own one first-class **Reset impact** page.
That page is the semantic home of:

- chosen reset path
- storage-root effect
- preservation verdict
- new-roster / re-share consequences
- safe alternative paths
- reset receipts

The product must not make the operator learn continuity impact from separate support notes after the fact.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. reset-intent strip
2. preservation verdict card
3. storage-rehome card
4. roster-and-subject consequence card
5. safer-alternative card
6. final apply gate
7. recent reset receipts
8. expert details drawer

### 1) Reset-intent strip

Show:

- current seat
- chosen reset path
- strongest next-safe action
- whether this is credential-only, identity repair, storage rehome, or clean install

The strip should answer `what sort of reset am I considering?`

### 2) Preservation verdict card

Show separately whether the chosen path preserves:

- credentials only
- preferences / policy
- durable identity
- linked relationships
- subject bindings
- local bytes
- remembered approvals
- audit receipts

This card should answer `what survives this path?`

### 3) Storage-rehome card

Show:

- whether the effective storage root changes
- whether the product will open into a new empty world
- whether old folders are expected to disappear from the interface only
- what path or storage root would need to be reused to preserve continuity

This card should answer `am I still in the same storage world?`

### 4) Roster-and-subject consequence card

Show:

- whether duplicate rows may appear
- whether old rows merely go offline
- whether re-share / reconnect work is required
- whether any subjects must be re-added or re-adopted
- whether peers will still see the seat as the same one

This card should answer `what new cleanup or rebind work does this reset create?`

### 5) Safer-alternative card

Offer alternatives such as:

- `Credential reset without identity drift`
- `Reuse existing storage root`
- `Migrate continuity rather than clean install`
- `Repair identity locally before relinking`
- `Abort; consequence too broad`

### 6) Final apply gate

The final gate must require acknowledgement of:

- preservation verdict
- storage-root verdict
- duplicate-row or re-share risk
- the strongest expected follow-up task after apply

### 7) Recent reset receipts

Show recent receipts with:

- reset path
- preservation verdict summary
- storage-root verdict
- duplicate-row / re-share consequence
- final action taken

### 8) Expert details drawer

Hide raw config snippets, platform paths, credential-store internals, and storage-root IDs behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. reset-path phrase
2. preservation phrase
3. storage-root phrase
4. roster consequence phrase
5. strongest next action

Example:

```text
WebUI credential recovery via settings reset · preserves subjects but resets global prefs and may duplicate roster row · stays in same storage root · Use config-based recovery instead unless duplicate residue is acceptable
```

## Mandatory fields

- `reset_operation_ref`
- `reset_path_kind`
- `preservation_verdict_summary`
- `storage_root_verdict`
- `roster_consequence_summary`
- `followup_tasks[]`
- `safer_alternatives[]`
- `apply_gate_requirements[]`
- `strongest_next_action`

## Review guarantees

This page must let the operator:

- predict what will and will not survive a reset before they commit
- distinguish same-storage credential repair from new-storage clean world creation
- anticipate duplicate-row, re-share, and reconnect work
- choose a narrower recovery path when available
