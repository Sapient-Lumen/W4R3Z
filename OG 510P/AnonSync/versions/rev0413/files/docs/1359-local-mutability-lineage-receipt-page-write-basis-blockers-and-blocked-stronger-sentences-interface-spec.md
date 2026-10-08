# Local-mutability lineage receipt page — write basis, blockers, and blocked stronger sentences

## Purpose

This receipt gives one durable line-item answer to:

> why could or couldn't this runtime mutate bytes here, through what lane, under what actor, and what stronger write sentence did the product refuse to make?

## Receipt fields

### Identity block

- subject path / handle
- runtime world
- active actor / principal
- requested verb

### Mutability basis block

- write grant class
- host write lane
- current mutability class
- strongest proof rung reached

### Blocker block

- strongest current blocker
- retry / escalation rung
- continuity consequence
- whether current surface can fix it

### Strong-sentence block

- strongest allowed sentence
- blocked stronger sentence
- exact reason blocked

## Copy rules

- Prefer `blocked by lock`, `blocked by provider grant`, `blocked by principal`, `blocked by host lane`, or `blocked by filesystem health` over generic `cannot sync`.
- Prefer `same path but new world` over `same folder` when service/principal changed.
- Prefer `technically writable but unsafe mixed lane` over `healthy` when SMB / direct-local conflict remains.

## Example final sentence pattern

> `Bytes are not currently writable here by this runtime because <barrier>; stronger sentence <writeable-now / same-world continuity / safe-lane> was blocked by <missing proof>.`
