# ADR 0297: Add signed tree-v2 namespace health

- Status: accepted and implemented
- Date: 2026-09-02

## Context

The Agent already exposed live job counters, explicit repair, signed workspace and maintenance
state, conflicts, automation retry counters, sparse custody, and exact-probe source evidence. Those
facts were scattered across transient and operator-triggered surfaces. After restart there was no
authenticated, content-free statement of what the last complete namespace inspection proved, and a
sparse node could be mistaken either for corruption or for a complete backup.

## Decision

Add owner-local `sync-health NAMESPACE [cached|refresh]` and local-control v1.54 operation 122.
Refresh performs a read-only tree-v2 inspection under the namespace transaction, derives one closed
green/yellow/red result, and atomically commits a stable-device-signed `health.state`. The fixed
record stores commitments instead of namespace names, paths, principals, or content. It advances a
local sequence, binds the exact namespace policy, and carries only closed flags and bounded counters.
Cached reads verify the signature and namespace binding; policy drift is explicit.

Green requires authenticated policy/membership/frontier/maintenance state, complete selected-object
coverage, a stable workspace at the current merged manifest, a clean worktree, no conflicts, no
automation stall, no store-pressure warning, and no exhausted source set. Sparse intent is orthogonal:
complete selected custody may be green while total custody is partial. Yellow covers actionable but
non-corrupt states. Missing selected bytes, pending exchange, missing required authenticated layers,
or source exhaustion is red. Structural corruption fails the command instead of being reduced to a
color.

The record explicitly says `rollback-witness=0 backup-certified=0`. Its signature is tamper evidence,
not anti-rollback state or remote attestation. The first implementation is deliberately tree-v2-only;
older engines continue to expose their stronger existing repair/status facts and are refused here.
No peer, Ratox, sync-object, or authority framing changes.

## Consequences

Operators now have a fast authenticated cached answer and an explicit expensive refresh. Expected
sparse custody is no longer conflated with missing selected data. Source absence captured from the
last runtime pull becomes durable evidence without claiming current reachability. Policy changes
cannot silently reuse a green result.

The deterministic gates prove green/yellow/red classification, sparse-green semantics, signed reload,
sequence advance, policy staleness, tamper refusal, malformed CLI/local framing, and a live Agent
refresh plus cached read after a forward restore. This is same-host construction evidence, not soak,
independent-media, rollback-witness, legacy-engine parity, or backup qualification.
