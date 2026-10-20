# ADR 0127: construct the default-off synchronization vertical slice

Status: accepted, 2026-08-21.

## Decision

`state-sync-v1` may be advertised only when `iotox run` explicitly receives
`--enable-sync --sync-policy-root PATH` and strict loading of every owner-only namespace succeeds.
Construction creates both protocol roles: the bounded publisher from ADR 0126 and a one-source
subscriber. The disabled default advertises nothing and a policy path without the enable gate is an
error.

The subscriber requests a signed HEAD, verifies that its writer is the exact currently proven v3
`sync.publish` principal and a configured writer, then requests artifact and manifest with distinct
nonzero FileIds. Paused c-toxcore offers join only by those FileIds; remote filenames never select a
path. Each receive is journaled before resume, its completed staging file is SHA-256 verified and
committed by immutable kind/digest/size identity, and the signed HEAD is accepted only after both
objects commit. Acceptance never activates a revision.

Potentially blocking HEAD/object loads, hashing, verification, and final commit run on one bounded
worker outside the toxcore callback pump. Terminal receive truth uses a separate priority queue sized
from the maximum admitted receive population, so ordinary request pressure cannot discard completion,
cancellation, or failure. Each worker action reacquires the common authority-effect lock and rebuilds
the current session/authority context before any effect. Disconnect, epoch change, proof change, or
revocation therefore fences queued work.

The first local surface is deliberately narrow: `sync-namespaces`, `sync-pull FRIEND NAMESPACE`, and
`sync-status`. Repeating `sync-pull` resends the exact retained unanswered request, relying on the
publisher's epoch replay contract rather than creating another transfer identity.

## Consequences

- The daemon now contains a usable default-off complete-source network slice, not merely codecs and
  transport-neutral services.
- Active attempt recovery runs before networking. Complete staging can commit; incomplete staging is
  discarded and fenced. Live Tox file numbers are never recovered.
- The local status surface exposes bounded content-free publisher, pull, and worker counters. It does
  not expose object contents, remote filenames, private paths, or signing material.
- The deterministic mock-provider E2E gate proves actual Agent control, authority proof, lossless
  frames, paused file offers, file callbacks, two object commits, HEAD-last acceptance, and absence of
  activation.
- Namespace administration, local publication, cancellation, activation commands, durable job retry
  schedules, partial/range reuse, private runtime projection, and genuine two-guest convergence remain
  open. The slice is not yet M5B exit evidence.
