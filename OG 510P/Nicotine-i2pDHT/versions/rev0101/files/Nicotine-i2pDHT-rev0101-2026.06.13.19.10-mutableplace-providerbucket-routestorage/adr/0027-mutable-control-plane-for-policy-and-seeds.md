# ADR 0027 — Mutable control plane for policy and seed records

## Decision

Treat seed lists, policy capsules, contact-card feeds, and bridge service catalogs as signed mutable records or pointers to signed immutable records.

## Rationale

The DHT already needs BEP44/IPNS-like mutable heads.
Using the same primitive for policy and entrances keeps the protocol algebra small.

## Consequences

- Mutable records remain central.
- Garden nodes can mirror policy/seed heads without authoring them.
- Stale policy and rollback detection become test obligations.
