# ADR 0077 — useful refusal is capacity evidence, not replication success

## Decision

A bounded, signed refusal from a sibling or garden is useful evidence but not proof of storage, availability, or truth.

## Consequences

Useful refusal can improve scheduling and backoff choices. It cannot satisfy replication thresholds. Silent failure and useful refusal must remain separate local signals.
