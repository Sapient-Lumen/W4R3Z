# ADR 0061: Freeze Ratox v1 as a fenced, paced, lossless byte protocol

Status: accepted
Date: 2026-08-15

## Context

The controlled impairment gate showed that reliable custom packets preserve order but can build a
large prefix and reject local admission, while lossy packets cannot carry irreversible input.
Forced TCP also makes both APIs share one ordered head-of-line domain. Ratox therefore needs a
small canonical envelope, cumulative at-most-once byte semantics, complete attachment fencing, and
an explicit congestion response before a PTY exists.

## Decision

Freeze the version-1 envelope and registry in `docs/protocol-ratox-v1.md` and the production codec
in `iotox/protocol/ratox.hpp`.

- Use custom-lossless packet ID `0xA2`, fixed major/minor 1.0, a 124-byte canonical header, and a
  1,200-byte total packet ceiling.
- Carry session, principal, attachment nonce, incarnation, and generation in every frame. OPEN and
  ATTACH have narrowly defined zero fields; accepted traffic never does.
- Use independent cumulative input/output byte sequences, next-expected ACKs, explicit output
  gaps, 64 KiB input replay, and 1 MiB output history.
- Keep v1 as opaque PTY bytes. Do not negotiate terminal emulation, screen deltas, or lossy state.
- Reserve the distinct `interactive.terminal` authority name at bit 7, but do not broaden the
  current authority-ledger v1. A reviewed signed migration is required before OPEN can be enabled.
- OPEN has no remote profile selector; local policy resolves at most one enabled profile for the
  proven principal. It carries no arbitrary command/environment/path.
- Treat SENDQ rejection as unsent congestion evidence. Retained bytes are retried only through the
  qualified pacer; no failed submission advances delivery state.
- Coalesce at a 20 ms base. Rejection doubles the interval to at most 320 ms; eight consecutive
  acceptances halve it toward base, and an empty queue resets it. Even a full frame is paced.
- Reject unknown version/type/flag/reserved/length and impossible attachment or stream state before
  side effects. Future extensions require negotiation and a new minor or major version.

## Consequences

The parser and invariants can now be fuzzed before exposing a shell. At-most-once input does not
depend on transport reconnect behavior, and stale controllers cannot target a replacement PTY.
The 124-byte identity cost leaves 1,076 bytes of terminal data per maximum packet, an intentional
latency and auditability tradeoff.

This decision does not implement or advertise OPEN handling, a PTY, a shell, reconnect service, or
authority-ledger v2. Those remain closed until lifecycle, denial, replay, process, two-host, and
threat-review gates pass.
