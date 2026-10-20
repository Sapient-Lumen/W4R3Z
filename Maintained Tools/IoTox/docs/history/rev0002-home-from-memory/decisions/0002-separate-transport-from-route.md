# ADR 0002: Separate application transport from network route

**Status:** accepted for rev0001

## Context

The desired family includes Tox natively, Tox over I2P, and Tox over Tor. Separate future ideas include IoTox communicating directly over I2P or Tor without Tox.

## Decision

Represent the application peer transport and its route as separate types. Tox has native, I2P-reserved, and Tor-reserved routes. I2P-direct and Tor-direct are separate reserved transport kinds.

## Consequences

- Configuration is unambiguous.
- Route fallback can be explicit and fail closed.
- Direct overlay work cannot accidentally inherit Tox semantics.
- Multi-route identity and privacy policy remain visible architecture decisions.
