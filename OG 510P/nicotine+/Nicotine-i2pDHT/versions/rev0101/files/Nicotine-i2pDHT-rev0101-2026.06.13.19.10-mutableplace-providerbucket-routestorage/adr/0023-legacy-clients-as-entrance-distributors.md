# ADR 0023 — Legacy clients as entrance distributors

## Decision

Treat willing clients on a populated legacy network as distributors of signed I2P/DHT contact cards.

## Rationale

A central network that still works can help seed its successor without becoming that successor's authority.
Contact cards are small, signed, expiring, and easy to exchange through many social/client paths.

## Consequences

- Hybrid mode gains real purpose: reduce central reliance while central access still exists.
- Metadata modes must be explicit.
- Contact-card validation and cache diversity become core DHT design surfaces.
