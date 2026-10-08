# PB-01 coherence / cluster refactor — rev0010

## Decision

Treat PB-01 as one report-candidate, not as several independent suggestions.

## Why

U-168 and U-176 share the same higher-order invariant: connection primary election relies on claimed username/type or shared init object state rather than an explicit source/generation model. Fixing them separately risks contradictory advice:

- Rejecting every secondary connection can break legitimate direct/indirect fallback behavior.
- Allowing every direct PeerInit replacement preserves compatibility but keeps the hijack/replacement primitive.
- Binding only F transfer sockets would leave P and D primary-election behavior unchanged.
- Binding only P/D would leave transfer-session F attachment and handoff semantics inconsistent with the rest of the connection model.

## Cluster result

| item | rev0010 decision |
|---|---|
| U-168 | PB-01a, direct replacement behavior, strict/front-lane candidate |
| U-176 | PB-01b, secondary promotion behavior, same strict/front-lane candidate |
| U-165 | supporting PierceFireWall context only |
| U-171 | separate address/server-trust hardening backlog |
| U-181 | separate queue/backpressure backlog |
| U-40 | merged/aliased into U-145 |
| U-145 | canonical address-class validation row |
| U-205 | remains alias of U-145 |

## Fix-shape constraint

Any recommendation should preserve legitimate reconnect and direct/indirect compatibility. The likely shared primitive is an explicit connection generation/election record that ties the expected username, connection type, address/source context when available, pending request token when available, and the permitted handoff/failover state.
