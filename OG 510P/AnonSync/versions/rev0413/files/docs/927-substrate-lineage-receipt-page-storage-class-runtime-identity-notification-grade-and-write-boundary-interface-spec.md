# Substrate lineage receipt page: storage class, runtime identity, notification grade, and write boundary interface spec

## Purpose

After any topology approval, runtime migration, write-lane retirement, or boundary warning acceptance, the operator needs a durable receipt that answers later:

> what substrate contract did we approve, which runtime identity and authoritative path were in force, what detection grade did we accept, and what stronger claim stayed forbidden?

## Receipt structure

### Header

Show:

- receipt id
- emitted time
- subject / scope
- action family (`topology-adopted`, `runtime-migrated`, `lane-retired`, `boundary-accepted`, `topology-blocked`)

### Contract summary

Render:

- storage class
- runtime identity
- authoritative access path
- notification grade
- contention grade
- write-path boundary verdict

### Before / after section

Show:

- prior substrate class
- new substrate class
- prior runtime identity
- new runtime identity
- prior write-lane set
- new write-lane set

### Risk and claim section

Show:

- strongest safe sentence after action
- stronger rejected sentence
- accepted degradation, if any
- blocked topology classes, if any

### Evidence section

Show:

- witness basis for path namespace
- witness basis for notification grade
- witness basis for contention state
- freshness window

### Follow-on section

Show:

- next watch pages to monitor
- invalidators for this receipt
- superseding receipts, if later emitted

## Rules

### Rule 1 — receipts preserve the contract, not just the path string

The receipt must capture storage class, identity, and boundary meaning.

### Rule 2 — degraded claims stay visible later

If the operator accepted rescan-backed or mixed-access-degraded posture, that weakened sentence must survive in the receipt.

### Rule 3 — runtime migration must preserve state-world truth

If switching service identity created a new storage/state world, the receipt must say so.

### Rule 4 — forbidden stronger claim remains durable

The receipt must preserve what the product still refused to promise.

## Acceptance criteria

A later operator can:

- tell what substrate contract was approved
- tell who the runtime actor was
- tell which path namespace was authoritative
- tell how strong change detection was
- tell what write boundary was accepted or blocked
- tell what stronger claim remained forbidden
