# ADR 0037 — witness receipts are evidence, not quorum

## Decision

A valid witness receipt is not automatically useful quorum evidence. Receipt batches must be checked for expiry, signature validity, path/garden family diversity, and contradictions.

## Rationale

Garden nodes can give memory, but a single garden family can also flood the system with signed evidence. The protocol should preserve receipts while refusing to confuse volume with independence.

## Status

Toy-tested in `witnesspoison.py`.
