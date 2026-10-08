# Research notes — 2026-06-03 — rev0028

Research pressure this turn pointed toward three useful cautions:

- libp2p peer/address-store thinking treats peer records and address books as local memory that can be persisted, but address claims still need validation and freshness.
- IBLT/set-reconciliation work is relevant for future anti-entropy, but rev0028 stays at generated fuzz and journal replay rather than adding a half-baked reconciliation protocol.
- SAM v3.3 primary/subsession support is attractive later, but i2pd/SAM feature differences mean the Python prototype should keep streaming-first assumptions shadowed until real routers are testable.

These notes are design pressure, not protocol authority.
