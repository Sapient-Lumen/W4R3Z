# PB-01 compatibility coherence refactor — rev0038

## Refactor purpose

Earlier PB-01 notes correctly warned that a naive fix could break direct/indirect connection races. Rev0038 makes that warning executable and separates the actual primary-election invariant from adjacent rows.

## Keep inside PB-01

- **U-168**: username/type-keyed direct `PeerInit` replacement over an established primary.
- **U-176**: secondary post-init promotion over an established primary.
- **U-165 support path**: valid PierceFireWall can create a secondary while a direct primary remains established; the defect is late promotion, not the initial compatibility behavior.

## Keep outside PB-01

- **U-123**: transfer-token active-owner collision and stale cleanup identity. That sink is `active_users[username][token]`, not `PeerInit` username/type primary election.
- **SEARCH-RESP-01 / U-163**: search response source/scope and parse order. That sink is search-token response handling, not connection-primary mutation.
- **U-138 and media-parser backlog**: local metadata parser materialization, not network connection binding.
- **U-171 / address-connect policy**: peer address source and direct-connect policy; relevant context but not the PB-01 sink.
- **U-181 / pending-message buffering**: queue pressure/backpressure; relevant to message migration but not the primary election bug itself.

## Compatibility vocabulary after rev0038

```text
established primary: init.sock points to a PeerConnection in _conns with is_established=True
secondary: a PeerConnection sharing init where conn.sock != init.sock
allowed replacement: previous primary absent, missing, or not established
blocked replacement: previous primary exists and is established
allowed promotion: no established primary remains
blocked promotion: established primary remains alive
```

This vocabulary is narrow enough for a maintainer patch and broad enough to cover P, D, and F post-init promotion without conflating PB-01 with transfer-token or parser-budget findings.
