# rev0882 implementation and architecture audit

## Heart of the mission

AnonSync is an authority-accounting and convergence system, not a file-copy
wrapper. Exact validated history owns operation identity, causal projection,
outbox attempts, receipt meaning, and visible effects. A clock, queue entry,
encoded frame, TLS session, socket buffer, filesystem pathname, index, or test
report may coordinate or attest work, but it cannot silently mint authority
that the exact evidence and cutpoint do not grant.

Rev0882 applies that rule to the sender's first transport progress. A frame that
was valid when built is historical data after its exact claim or channel changes.
The new composition reacquires and re-proves both immediately before the first
application-record prefix and retains the database writer only through that
fixed-size frontier.

## Corrected severe boundary

Rev0881 made frame construction current under `BEGIN IMMEDIATE`, then returned
an ordinary value. A queue could retain claim A's frame after release, expiry,
settlement, or claim-B replacement. The generic TLS writer did not know the
claim or channel cutpoint that had authorized the bytes. Receiver idempotency
would often preserve correctness, but stale bandwidth, receiver work, confusing
settlement evidence, and an unowned dispatch transition remained possible.

`sync_replica_file_tls_dispatch` now owns that transition. It freezes bounded
input, rebuilds canonical request/frame/digest, acquires the exact claim guard,
re-proves the TLS exporter-bound channel and claim-derived request, then writes
only the full encrypted eight-byte length prefix before committing SQLite. The
potentially large immutable body follows through a move-only continuation after
the writer is gone.

## Audit/refactor finding corrected during implementation

The first continuation draft was not exclusive in the SSL owner. A same-thread
caller could hold an unfinished prefix capability and begin another record or
read before supplying the first body. That would violate stream framing despite
move-only wrapper syntax.

The authenticated TLS state now owns an explicit `record_write_active_`
reservation. Begin sets it; finish clears it; abandonment or any contradiction
poisons the stream. Generic read/write and a second begin reject overlap. The
runtime matrix proves that rejected overlap leaves the original continuation
usable and that completion prevents reuse.

A second overclaim was also removed. `SSL_get_rfd()`/`SSL_get_wfd()` plus
`O_NONBLOCK` do not prove socket backing: a descriptor BIO can expose a pipe or
ordinary file. The strict guarded composition now requires direct
`BIO_TYPE_SOCKET` methods and a successful kernel `SO_TYPE` query before checking
`O_NONBLOCK` in both directions. The negative runtime uses a non-socket
descriptor and proves zero prefix progress.

## Refactor assessment

Three duplicated or diffuse responsibilities are now centralized:

1. generic delivery, file delivery, and TLS dispatch share one exact
   claim-to-request constructor;
2. pre-dispatch exact release and typed dispatch-guard failure handling share
   file-service helpers; and
3. ordinary one-shot TLS writes delegate to the same begin/continuation state
   machine as the guarded composition.

The dependency direction remains narrow. The file service is OpenSSL-neutral;
the TLS transport is SQLite/effect-neutral; the composition target alone links
both. This is preferable to a large service class with hidden cross-layer
state.

## Failure ownership

- Before prefix success: roll back the guard, poison any partially progressed
  stream, exact-release the claim under local positive bounded policy, and
  propagate the original or combined contradiction.
- After prefix success: commit/body exceptions poison the stream but retain the
  exact claim as ambiguous. No immediate retry is manufactured.
- After body success: the claim remains live awaiting a validated receiver
  receipt. TLS completion is never settlement authority.

This split is conservative because OpenSSL documents that WANT results may have
partially processed data. Rev0882 never resumes a WANT operation. Before a
successful prefix return no body has been supplied and the channel is discarded;
a fresh attempt cannot append to that old stream. After prefix return, any body
failure is ambiguous and therefore cannot exact-release automatically.

## Validation hierarchy

Load-bearing fresh evidence is:

- complete GCC Debug all-target compilation with 311 fresh Ninja actions and no
  observed warning/error diagnostic;
- one complete 192/192 registered CTest invocation;
- one complete 61/61 audit-named CTest invocation;
- 5,198/5,198 focused runtime checks in GCC Debug, Clang 17 Release `-Werror`,
  and GCC ASan/UBSan with bundled SQLite instrumented;
- 5,920/5,920 checks across 100 mixed authority executions;
- a separate 100-run, 7,400-check TLS dispatch stress gate; and
- 505/505 selected lexical architecture checks across 17 audits.

The selected source audits prove vocabulary, file inventory, dependency shape,
and expected ordering only. They do not prove OpenSSL progress, SQLite
serialization, exception safety, crash recovery, peer receipt, cryptographic
security, or remote effect semantics.

## Remaining severe gaps

The largest remaining implementation gap is not another local guard. It is an
actual service owner for nonblocking transport liveness and receiver
composition. The present body writer poisons on WANT instead of retaining the
same immutable arguments and resuming under event-loop readiness. A large body
can cross lease expiry because the SQLite writer is intentionally released
before transfer; receiver idempotency protects state, but duplicate bandwidth
and scheduling pressure remain.

There is no durable `dispatch_started`/body-offset state, transfer heartbeat,
cancellation rule, transfer-age policy, chunk/resume protocol, or restart
recovery for an in-flight body. There is also no production receiver loop or
shipped executable using the new causal/file-effect/TLS stack. Assurance around
an isolated library must not be confused with product integration.

The older broad executable path and the newer correctness-oriented owner stack
remain weakly connected. The O(history) SQLite owners should remain oracles for
repair and differential testing, while an indexed production owner is built
separately. Build modularity is also still partly superficial: a focused sender
change compiled 311 actions in the complete gate and more than one hundred in
each focused compiler lane.

## Recommended next slice

Create one small replica-service executable with a nonblocking event loop. It
must own immutable write buffers across WANT states, read exact framed requests,
invoke the existing receiver file-delivery service, and send the exact receipt
on the same authenticated channel. Inject crashes after prefix, arbitrary body
offsets, receiver evidence commit, payload staging, rename, directory fsync,
receipt write, and sender settlement. Define heartbeat/expiry/cancellation only
from observed failure evidence, and migrate the shipped executable before
expanding the isolated feature surface.
