# Identity lineage receipt page: graph direction, certificate survivor, and containment class interface spec

## Purpose

This receipt preserves the identity-graph story after the operator leaves the review flow.
It must answer later:

> which graph action was attempted, whose certificate survived, what arrival and authority posture came with it, what containment class applied, and what stronger claim was explicitly refused?

## Receipt fields

Required fields:

- receipt id
- local seat id / remote seat id / identity ids if available
- action class (`link`, `unlink`, `hide offline`, `identity regenerate`, `license reclaim`, `unknown`)
- adoption direction verdict
- surviving certificate / fingerprint class
- graph replacement verdict
- default arrival mode and authority class
- entitlement coupling verdict
- containment class verdict
- strongest safe sentence
- blocked stronger sentence
- evidence freshness
- operator action taken / declined

## Example safe sentence

- `This action linked the local seat into a broader identity graph whose certificate survived from the remote side; future folder arrivals now follow the reviewed linked-device mode, while compromise containment may still require identity regeneration rather than hide-or-unlink alone.`

## Rules

### Rule 1 — receipts must preserve direction

A later reader must be able to tell who adopted whom.

### Rule 2 — receipts must preserve graph, entitlement, and containment separately

Graph membership, owner/license coupling, and recovery scope are different truths.

### Rule 3 — cleanup actions must not erase the record

Even if the graph is later reset, the receipt keeps the previous blast-radius and blocked-claim boundary visible.
