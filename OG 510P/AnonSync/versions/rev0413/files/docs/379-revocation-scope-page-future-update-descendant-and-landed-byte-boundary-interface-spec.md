# Revocation scope page: future-update, descendant, and landed-byte boundary interface spec

## Purpose

The archive already has strong revocation, retained-copy, and residual-reliance doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if I revoke or disconnect this access now, what exactly stops, which descendants remain affected, and what bytes remain outside recall?

## Core decision

Every serious revoke or disconnect action must own one first-class **Revocation scope** page.
That page is the semantic home of:

- direct target
- future-update boundary
- descendant and derivative blast radius
- pending-claim boundary
- landed-byte residue
- cleanup and follow-up ladder

The product must not let a destructive-sounding button stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. target strip
2. direct-effect card
3. descendant-blast-radius card
4. pending-claim card
5. landed-byte residue card
6. cleanup-and-followup card
7. recent revocation receipts
8. expert details drawer

### 1) Target strip

Show:

- target member, seat, or artifact
- subject
- current right or artifact ceiling
- strongest next-safe action
- whether the page is previewing a revoke or reviewing one already applied

The strip should answer `what exact access am I about to stop?`

### 2) Direct-effect card

Show one explicit verdict:

- `future updates stop for this direct target`
- `future updates stop only after pending work drains`
- `direct target already frozen; revoke is historical`
- `artifact revoked but current member access remains through another epoch`
- `requested revoke exceeds current operator authority`

Also show:

- whether the direct target loses live access immediately or only after current session boundary
- whether any alternate grants keep the member effectively connected

This card should answer `what immediate direct effect will happen?`

### 3) Descendant-blast-radius card

Show:

- affected local derivatives
- affected inherited seats or linked descendants
- affected onward-granted descendants
- descendants not affected because they sit on parallel grant epochs
- whether a source downgrade cascades automatically or requires separate review

This card should answer `what else loses updates because of this revoke?`

### 4) Pending-claim card

Show:

- pending requests this revoke will cancel
- already-issued artifacts that remain claimable unless separately retired
- approval-memory consequences
- whether the operator must also revoke or supersede artifact families to close the door fully

This card should answer `what access doors remain open after I revoke this target?`

### 5) Landed-byte residue card

Show:

- already-landed bytes that remain on prior recipients
- whether placeholders, metadata-only views, or detached visibility remain
- whether local cleanup, remote courtesy notice, or retained-copy follow-up is available
- what the product can prove versus what it cannot reclaim

This card should answer `what replicated data remains outside the scope of revocation?`

### 6) Cleanup-and-followup card

Show the strongest honest follow-up ladder, for example:

1. revoke future updates
2. retire still-live artifacts
3. open retained-copy follow-up
4. notify downstream stewards if descendants remain
5. record correction / supersession notice if old artifact circulation is expected

This card should answer `what extra work is still needed after revoke?`

### 7) Recent revocation receipts

Show recent receipts with:

- target
- subject
- direct-effect verdict
- descendant-blast-radius verdict
- landed-byte boundary shown
- follow-up actions opened

### 8) Expert details drawer

Hide raw ACL diffs, session IDs, transport cutover details, and artifact fingerprints behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. target phrase
2. direct-effect phrase
3. descendant phrase
4. landed-byte phrase
5. strongest next action

Example:

```text
alex@fedora via epoch g-204   future updates stop for direct target   one local derivative also loses updates; two parallel descendants unaffected   landed bytes remain; retained-copy follow-up available   Revoke with review
```

## Acceptance criteria

This spec is satisfied when:

- future-update stop and byte recall are visibly different answers
- direct target and descendant blast radius are visibly different answers
- alternate grant paths are shown before commit
- pending claims and already-landed bytes are separated cleanly
- the product emits receipts for revocation scope rather than outsourcing memory to terse disconnect logs
