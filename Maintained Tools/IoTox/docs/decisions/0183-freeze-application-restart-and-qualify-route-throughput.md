# ADR 0183: Freeze application restart and qualify multi-route throughput

Status: accepted over direct UDP and forced TCP, 2026-08-26.

## Context

ADR 0182 proved large work could begin with one ready bulk route and remain on it when a second route
joined. Gate 4 still lacked a larger-object fixed/adaptive comparison. The new ABBA fixture also
needed a clean Agent replacement between phases so policy state, route load, and object state could
not leak across measurements.

The first forced-TCP attempt exposed a protocol boundary rather than a scheduler defect. After a
same-savedata Agent replacement, the local TCP relay retained six established relay sockets and did
not emit a fresh Tox offline/online epoch to the stable peer. The replacement Agent correctly
generated a different canonical HELLO nonce; the stable peer correctly froze that changed HELLO
inside what it still understood as one transport epoch. Primary authority recovered slowly in some
phases, while exactly one auxiliary route remained unready and the third restart reached the
180-second bound. A fast process restart therefore could not be inferred from Tox connection state.

## Decision

Freeze `application-epoch-restart-v1` as feature bit 27 and the ordered nonce generation defined in
`protocol-application-epoch-restart-v1.md`. Its first eight bytes are a device-signed durable process
incarnation, its next four are a nonzero process-local connection epoch, and its last four retain
entropy. Only a strictly greater generation negotiated by local, incumbent, and candidate HELLOs can
advance an application epoch within a continuous Tox transport epoch. A stale generation is ignored
without poisoning current state; different bytes at the same generation retain the original
fail-closed conflict. The new epoch retires every application authority and work binding before the
exact local HELLO is resent and the normal confirmation and authority gates run again.

Add `sync-tree-route-throughput`. Each of four phases starts a fresh subscriber Agent and waits at
least 5,000 ms with it stopped. The ABBA order is `fixed-a,adaptive-a,adaptive-b,fixed-b`. Every phase
starts two independent signed tree pulls, each carrying one 16,777,216-byte payload and producing a
16,777,283-byte artifact. Fixed must select `00`; adaptive must select `01`. Acceptance requires four
selections per policy, eight explicit activations, zero reassignments, peak signed work four, final
work zero, four process-incarnation-fenced resource intervals, and 40 protected Ratox samples after
convergence. A 180-second route-readiness deadline remains hard.

The two bulk identities share the same shaped 4 Mbit/s client TAP. This measures whether logical
route placement can avoid one busy Tox/file-manager path on this topology; it deliberately does not
model two independent physical links.

## Consequences

- Clean Agent replacement no longer depends on c-toxcore exposing a matching transport callback.
- Application authorization and work are never inherited merely because Tox stayed connected.
- Fixed and adaptive policy now have one counterbalanced larger-object observation on both supported
  native carrier classes.
- Adaptive gains aggregate throughput in both cells, but the result does not freeze a performance
  promise. Forced TCP also shows materially worse adaptive completion skew than fixed placement.
- The scenario establishes useful concurrency behind one shared host bottleneck, not bandwidth
  bonding, physical striping, relay independence, or proportional scaling.
- Repeated randomized distributions, cold physical route absence, startup concurrent with a fault,
  more than two bulk routes, independent bottlenecks, and production QoS policy remain open.

## Qualification

Binary `e23b5ca2fe020e476c4a49f10f188d3d73638b4fb9d2230e267f7c58a4a5ff2d`
passes strict raw and compact verification in both two-Sandwurm-guest cells.

- Direct UDP `pair.pw3ogf7q`: fixed 179,940 ms / 372,952 artifact B/s; adaptive 154,060 ms /
  435,603 artifact B/s; speedup 1,167,986 ppm (16.80%); fixed skew 720/570 ms, adaptive skew
  3,160/2,570 ms; protected Ratox p50/p95/max 12.256/17.740/21.810 ms.
- Forced TCP `pair.7zsdwj15`: fixed 168,410 ms / 398,486 artifact B/s; adaptive 158,040 ms /
  424,633 artifact B/s; speedup 1,065,616 ppm (6.56%); fixed skew 10,250/2,490 ms, adaptive skew
  19,020/14,650 ms; protected Ratox p50/p95/max 88.640/128.307/131.101 ms.

Each compact proof allocates 270,336 bytes and excludes guest disks, private identities, bootstrap
secrets, payload content, and mutable runtime state. Exact receipt, manifest, resource, and rejected
run evidence lives in `evidence/2026-08-26-sandwurm-sync-route-throughput.md`.
