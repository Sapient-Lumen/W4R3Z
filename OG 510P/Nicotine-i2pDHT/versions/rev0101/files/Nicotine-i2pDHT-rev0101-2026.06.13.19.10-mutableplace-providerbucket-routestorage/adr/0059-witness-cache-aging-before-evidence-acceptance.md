# ADR 0059 — Witness cache aging before evidence acceptance

## Decision

Witness receipts must be cached with local aging, duplicate collapse, family caps, and contradiction quarantine before they influence later DHT decisions.

## Reason

A signed receipt is not timeless truth.  Old evidence can become stale; duplicate gossip can inflate apparent support; one garden family can create a monoculture; and a witness that contradicts itself must be quarantined locally.

## Consequence

`witnesscache.py` is now part of the risk-first surface.  It preserves evidence, but it does not create quorum or global reputation.
