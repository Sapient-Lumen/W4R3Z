# ADR 0024 — I2P-only mode is default off and readiness-gated

## Decision

Design an I2P-only mode that never silently connects to classic servers, but keep it default off and gated by entrance-cache readiness.

## Rationale

A sovereignty mode that quietly falls back to central login is dishonest.
A default-on mode before the DHT is mature would be hostile to casual users.

## Consequences

- The DHT must support diverse bootstrap portfolios.
- The UI must expose entrance health.
- Power users can override, but defaults remain conservative.
