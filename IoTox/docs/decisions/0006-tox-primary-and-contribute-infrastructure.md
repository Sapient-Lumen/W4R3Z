# ADR 0006: Keep Tox primary and contribute useful infrastructure

**Status:** accepted for rev0002

## Context

Tox provides the peer identity, encrypted sessions, bootstrap discovery, NAT traversal, relays, custom packets, and file transfer that make ratox compelling. IoTox values the fact that Tox is a working community network rather than a vendor-controlled service.

Sentiment does not replace measurement, but abandoning Tox before native integration testing would discard the project's strongest working premise.

## Decision

Keep c-toxcore as IoTox's primary peer transport and make Tox/native the first production target.

Plan for Tox/Tor and Tox/I2P as explicit future routes. Direct Tor and direct I2P transports remain separate, secondary ideas.

IoTox should contribute to the Tox commons through some combination of public bootstrap nodes, TCP relays, owner-operated server tooling, reproducible deployment, test reports, documentation, and upstream fixes. Server participation must not grant IoTox ownership authority or require user accounts.

## Consequences

- The next networking gate remains a pinned real c-toxcore build and controlled two-node native test.
- Route status language distinguishes adapter verification from real network verification.
- Server work is part of product stewardship, not a hidden centralized dependency.
- Tox can still be rejected later if measured reliability, power, security maintenance, licensing, or target-platform behavior fails explicit gates.
