# ADR 0012: Bootstrap nodes and TCP relays are configured roads, not authorities

**Status:** accepted and partially implemented in rev0004

## Context

A usable Tox agent needs bootstrap nodes and often TCP relays. Shipping or operating
those endpoints can accidentally be presented as vendor account infrastructure or a
trust root. Tox bootstrap/relay participation provides reachability, not IoTox
ownership.

## Decision

IoTox accepts repeated bootstrap and TCP-relay endpoint configuration in the form:

```text
host:port:64-hex-public-key
[IPv6-address]:port:64-hex-public-key
```

The endpoint parser is strict. Calls and outcomes are inspectable transport events.
Disconnected agents retry bootstrap on a bounded interval.

Endpoint selection, list update, and health policy remain configuration and operations
work. No endpoint can grant roles, recover a RecallRoot, reassign a device, or bypass
the authorization ledger.

## Consequences

Owners and communities can operate infrastructure without becoming sovereign. Public
list provenance, pinning, rotation, health, privacy, and denial-of-service policy remain
open work.

## Revisit when

Real-network evidence shows a different bootstrap cadence or discovery mechanism is
required, or Tox-over-Tor/I2P requires route-specific endpoint records.
