# Runtime stop proof page: runtime witness, drain verdict, and no-further-publication proof interface spec

## Purpose

After a stop request, the operator needs one ordinary proof surface that answers later:

> is the runtime actually gone, did drain finish, what evidence supports that answer, and what exact no-further-publication sentence is the product still allowed to say?

This page exists so `I think it stopped` does not remain tray-memory or platform folklore.

## Proof structure

### Header

Show:

- subject / seat / node name
- proof id
- targeted runtime class
- current proof verdict (`running`, `draining`, `stopped-unproven`, `stopped-proven`, `restart-suspected`, `unknown`)
- strongest safe sentence
- stronger rejected sentence

### Runtime witness section

Render:

- last confirmed projection state
- last confirmed runtime state
- process / service witness basis
- background / mobile witness basis
- evidence freshness window

### Drain verdict section

Show:

- active transfers now
- queued publication now
- last outbound activity time
- drain verdict (`quiet-confirmed`, `quiet-unconfirmed`, `residual-work-present`, `proof-stale`)

### Restart boundary section

Show:

- startup posture
- service persistence posture
- external relaunch suspicion
- any restart observed after stop request
- whether the proof has been invalidated

### Claim section

Show:

- strongest safe sentence now
- stronger rejected sentence now
- what missing witness blocks the stronger claim

### Follow-on section

Show:

- next proof refresh point
- invalidators
- superseding proof or receipt

## Rules

### Rule 1 — proof distinguishes stop request from stop witness

The page must separate requested action from observed runtime state.

### Rule 2 — quiet proof is freshness-bound

A stale proof cannot keep the strongest sentence.

### Rule 3 — restart suspicion invalidates stronger claims fast

Any sign of relaunch must weaken the sentence until re-proven.

### Rule 4 — missing witness stays explicit

The page must say what evidence is absent.

## Acceptance criteria

A later operator can:

- tell whether the runtime was actually proven stopped
- tell whether drain finished
- tell whether restart invalidated the proof
- tell what sentence the product was still allowed to say
- tell what evidence was missing or stale
