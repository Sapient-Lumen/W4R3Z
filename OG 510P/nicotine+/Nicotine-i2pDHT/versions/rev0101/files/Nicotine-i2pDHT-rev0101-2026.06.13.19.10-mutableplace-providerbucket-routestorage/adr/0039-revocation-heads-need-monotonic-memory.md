# ADR 0039 — revocation heads need monotonic memory

## Decision

Clients and gardens should keep local monotonic memory for revocation heads and preserve the union of verified revoked grant hashes they have observed.

## Rationale

A valid old revocation head can omit a later revocation. Stale replay must not make a locally known revoked grant become usable again.

## Status

Toy-tested in `revocation_pressure.py`.
