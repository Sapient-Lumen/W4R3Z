# 0001 — Bundled runtime product posture

- status: accepted
- date: 2026-03-08

## Context

The project aims for a public-facing product with strong noob ergonomics. Requiring end users to install or manage Tor or I2P runtimes would conflict with that goal.

## Decision

AnonSync will treat bundled runtimes as the canonical product posture.

- I2P is bundled through `i2pd`.
- Java I2P is out of scope.
- Rust code reaches I2P through a SAM seam.
- Tor starts as a bundled stable tor daemon.
- Arti is explicitly deferred to a future migration path.
- The user-facing product should abstract away router and daemon details.

## Consequences

- runtime supervision becomes first-class architecture
- packaging and updates for bundled child processes matter early
- provider boundaries still matter because implementation may change later
- docs should avoid assuming the user ever touches transport internals
