# ADR 0064 — Valid signature is not freshness, path, or transport proof

## Decision

A valid signature must remain separate from freshness, path diversity, and transport/session validity.

## Reason

The hardest DHT failures often involve valid cryptographic objects delivered stale, through captured paths, or under wrong transport/session assumptions.

## Consequence

rev0015 keeps four separate surfaces: witness cache aging, lookup transcript pressure, SAM shadow session checks, and garden scheduling.  They can inform each other, but none erases the others.
