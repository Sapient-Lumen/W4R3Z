# PB-01 compatibility and fix-shape notes — rev0011

## The compatibility trap

PB-01 is not a request to reject every secondary connection. The public protocol and current implementation both need compatibility for direct/indirect connection races. The rev0011 test therefore separates compatibility baselines from the problematic primary-election transitions.

## Preserve

- A first valid direct P/D `PeerInit` should become primary.
- A valid `PierceFireWall` with no direct primary should become primary.
- A valid `PierceFireWall` should be able to win over a direct attempt that has not established yet.
- A valid indirect connection may need to remain open behind an already-established direct primary for compatibility.

## Change

- A later direct `PeerInit` should not steal an established primary solely by claiming the same username and connection type.
- Pending outgoing messages should not migrate to a new connection without an explicit generation/election match.
- A secondary P/D/F connection should not become primary merely because it sends any post-init data.

## Candidate model

Use one vocabulary across P, D, and F:

```text
connection_generation
expected_source/address context where available
connection_origin = direct / indirect / accepted incoming / file-transfer
is_primary_elected
is_failover_candidate
expected_transfer_token/session for F
```

Then change primary assignment and queued-message migration to require an explicit election state. This avoids three incompatible local fixes.
