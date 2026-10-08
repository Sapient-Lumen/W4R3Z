# Batch 02 deep dive — peer/source binding and transfer provenance

## Executive result

The Batch 02 items are not best handled as separate one-off reports. They cluster into three technical families:

- **PB-01:** peer connection identity/generation binding.
- **TR-01:** transfer lifecycle provenance and state binding.
- **PR-01:** allowed heavy-response/request-generation gating.

The strongest next candidate is **U-123 duplicate transfer token overwrite**, because it now has static source traces plus a minimal cross-lane microprobe. It is still blocked from the strict document until it has an end-to-end peer-flow reproduction and a completed hard public-overlap packet.

## U-123 status

U-123 should move to the next dynamic-repro slot. The local microprobe shows that calling `_activate_transfer()` twice for the same username/token overwrites the first transfer in `active_users[username][token]` in 3.3.10, 3.3.x, and master.

This is a real state invariant, but not yet a finished vulnerability report. The missing proof is that a peer can cause the duplicate-token path in a realistic transfer negotiation and that the result has a meaningful user/security impact rather than only an internal stale timer/state artifact.

## U-176 / U-168 / U-165 / U-171 / U-181 status

These belong together. Direct PeerInit replacement, secondary-connection promotion, indirect bearer-token adoption, server-supplied address use, and pending PeerInit buffering are different faces of one connection-generation problem.

The coherent next proof is not five separate writeups. It is a state-machine test that exercises direct and indirect connection races and then verifies whether a secondary connection can replace/pollute the primary connection context.

## U-217 status

U-217 is partially changed upstream. Master now has `AddAllowedResponse(UserInfoResponse, username)` and closes large unsolicited UserInfoResponse messages when the username is not allowed. That does not automatically prove full socket/address/generation binding, but it means the older “no gate exists” phrasing is not valid for master.

## Strict-document decision

No promotion. The strict document remains empty because every touched item still lacks at least one of these gates:

- end-to-end reproduction;
- final public-overlap proof;
- precise current/future branch behavior;
- coherent fix that does not conflict with related fixes;
- severity boundary tight enough for high-priority/high-quality reporting.
