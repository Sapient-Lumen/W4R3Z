# ADR 0040 — key succession is co-signed and fork-aware

## Decision

Prototype key succession records require signatures from both the old and new keys and must be tracked with rollback and same-sequence fork memory.

## Rationale

Mutable-control-plane keys need rotation. A unilateral pointer is too easy to replay or fork without local evidence handling.

## Status

Toy-tested in `succession.py`.
