# Architecture Decisions

- [0001: Keep the product core direct](0001-product-core.md) (superseded)
- [0002: Make the bond the product core](0002-bond-is-product-core.md)
- [0003: Race real-time data; do not guess terminal output](0003-race-realtime-do-not-guess-terminal-output.md)
- [0004: Expose an SSH-compatible remote-shell contract](0004-ssh-compatible-remote-shell.md)
- [0005: Add a public local transport socket with named peer services](0005-public-local-transport-socket.md)

Decision records explain why a boundary exists; they do not track current implementation
status. Use the [specification ledger](../../specs/spec_ledger.json) for authoritative
claim status and exit conditions, [AnonSSH architecture](../context/architecture.md) for
component ownership, [bond protocol](../context/bond-protocol.md) for wire/runtime
semantics, [provider API](../context/provider-api.md) for the reusable integration
boundary, [application interfaces](../context/application-interfaces.md) for shipped and
designed consumer surfaces, [evidence guide](../context/evidence.md) for campaign
interpretation, and
[I2P identity compatibility](../context/i2p-identity.md) for stable derivation details.
