# Issued access page: live artifact register, supersession, and governance drift interface spec

## Purpose

The archive already has strong share-capability doctrine, shareable-artifact doctrine, and correction-register doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> what access-bearing artifacts and grant epochs are still live for this subject right now, and which of them no longer match my current governance intent?

## Core decision

Every shareable subject must own one first-class **Issued access** page.
That page is the semantic home of:

- live artifact inventory
- carrier-versus-artifact truth
- current grant epoch inventory
- supersession and exhaustion state
- governance drift detection
- recent issuance receipts

The product must not let an operator infer artifact state from a past share dialog alone.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. subject strip
2. current-governance-intent card
3. live-artifact register
4. supersession-and-exhaustion card
5. governance-drift card
6. next-safe-issuance card
7. recent issuance receipts
8. expert details drawer

### 1) Subject strip

Show:

- subject
- current issuing seat
- current subject class
- strongest next-safe action

The strip should answer `what subject's issued access am I reviewing?`

### 2) Current-governance-intent card

Show:

- current desired approval posture
- current desired rights ceiling
- current desired expiry and budget posture
- current desired onward-share ceiling
- whether the page is describing present policy or a proposed new policy under review

This card should answer `what governance story do I currently intend?`

### 3) Live-artifact register

For each still-material artifact family or issuance event, show:

- canonical artifact identity
- delivery carriers currently wrapping it
- rights ceiling it can still create
- approval model
- expiry / use budget posture
- current grant epoch it feeds
- whether it is pending, live, exhausted, revoked, superseded, or historically frozen

This register should answer `what exact access-bearing things are still out there?`

### 4) Supersession-and-exhaustion card

Show:

- artifacts already replaced by successor issuance
- artifacts exhausted by use budget
- artifacts expired but still historically relevant
- artifacts explicitly revoked
- artifacts still technically live even though newer issuance exists

This card should answer `which artifacts are truly dead, and which are merely old?`

### 5) Governance-drift card

Show:

- artifacts whose current ceiling no longer matches current governance intent
- artifacts whose approval or expiry story is now weaker than desired
- artifacts whose live descendants still depend on earlier broader terms
- whether drift is harmless historical residue or active risk

This card should answer `what earlier-issued access is now out of step with my current policy story?`

### 6) Next-safe-issuance card

Show the strongest next-safe action, for example:

- `issue reviewed successor artifact`
- `revoke outdated artifact family`
- `leave historical artifact frozen; no further action`
- `open grant-change page first`
- `open revocation-scope page first`

The page should favor honest lifecycle work over reflexively issuing one more link.

### 7) Recent issuance receipts

Show recent receipts with:

- subject
- artifact identity
- carriers used
- grant epoch affected
- supersession status at the time
- governance drift verdict
- action taken

### 8) Expert details drawer

Hide raw hashes, encoded payloads, ACL serials, and transport wrappers behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. artifact phrase
2. grant-epoch phrase
3. approval / budget phrase
4. drift / supersession phrase
5. strongest next action

Example:

```text
Reviewed claim link (QR + copied text are wrappers)   feeds grant epoch g-204   approval: only new peers; expires in 3 days; 1 use left   live but weaker than current policy; successor issuance recommended   Reissue safely
```

## Acceptance criteria

This spec is satisfied when:

- carrier wrappers and distinct artifact families are visibly different answers
- old but live artifacts and fully dead artifacts are visibly different answers
- governance drift is detected without reopening old share dialogs
- the register states which grant epoch each artifact still feeds
- the product emits receipts for issuance-state changes rather than outsourcing memory to clipboard history and chat scrollback
