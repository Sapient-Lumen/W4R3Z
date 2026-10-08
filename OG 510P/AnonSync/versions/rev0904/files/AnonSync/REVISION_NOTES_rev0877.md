# AnonSync rev0877 revision notes

## Live authenticated-channel authority

Rev0877 corrects an authority mismatch in rev0876. The delivery service accepted
`SyncReplicaDeliveryChannelContext`, a public struct containing a peer actor and
channel-binding bytes. Those bytes were useful evidence but were caller
fabricable; they did not prove that the TLS adapter had authenticated a live
peer. The service could therefore be invoked without carrying the transport
capability that justified the durable operation.

The new `SyncReplicaDeliveryChannelAuthority` is privately minted, move-only,
non-copyable, process-bound, thread-lifetime-bound, and optionally backed by a
transport verifier. Every service operation validates this authority before
reading the context or touching `SyncReplicaSqliteOwner`.

The deterministic mint needed by delivery-service tests is isolated in
`tests/sync_replica_delivery_test_channel.*` and linked only into the test target.
This is explicit same-process domain separation, not a hostile-code security
boundary.

## Owned and continuously validated TLS state

`SyncReplicaTlsAuthenticatedChannel` now shares one authenticated TLS state with
its service authority and record I/O. The state:

- retains the `SSL` object with `SSL_up_ref()` and releases it with `SSL_free()`;
- binds the creating process and exact thread lifetime;
- revalidates the TLS profile, peer SPKI, and RFC 9266 exporter before each
  service or record use;
- rejects foreign-thread use before OpenSSL and fork-inherited use through the
  process-capability fail-stop path; and
- permanently poisons itself after a failed live-session check, uncertain I/O,
  partial record frontier, or invalid peer frame.

The caller may release its original OpenSSL reference after authentication.
Concurrent mutation, clearing, or re-handshaking of the same `SSL` object remains
unsupported. Sequential mutation is detected before the next authorized use.

An old authority after `SSL_clear()` and a fresh handshake is rejected before
SQLite mutation. The old stream is then poisoned; a newly authenticated channel
can claim the exact intent that remained durable.

## Preclaim wire-policy fence

The service now calls
`SyncReplicaSqliteOwner::claim_next_outbox_for_delivery_or_throw()`. The owner
shares the existing claim transaction, restores exact state, finds the first
ready intent, resolves its canonical operation, and validates that operation
against the complete delivery model before any lease mutation.

A wire-incompatible first-ready operation therefore retains attempt zero, no
claim ID, no worker, no deadline, and the same cutpoint under a valid clock
observation. Once compatible limits are supplied, the same intent receives
attempt one. This removes claim/encode/expiry churn for locally unsendable work.

The current fail-closed behavior creates intentional head-of-line blocking. A
future typed permanent-rejection/dead-letter state must own policy generation,
reason, operator visibility, and explicit reclassification before the owner can
safely scan past such an intent.

## Audit/refactor work

Three existing source audits had encoded the old implementation shape by looking
inside only `claim_next_outbox_or_throw()`. Both public claim surfaces now
delegate to `claim_next_outbox_impl_or_throw()`, and the audits verify delegation
plus ordering in that shared core. This keeps one load-bearing ordering proof for
entropy, writer authority, full restore, clock observation, lease transition,
and publication.

The first TLS fork test used an ad hoc raw `fork()`. The cube's raw-fork audit
correctly rejected it. The test now uses the shared inherited-process harness,
leaving one raw fork in one owned implementation. Exact process-boundary
inventories were updated to 14 inherited consumer translation units, 25
inherited spawn sites, eight fresh-image campaigns, and 33 combined sites.

A new 18-check `audit_sync_replica_delivery_channel.py` verifies source-shape
hygiene while explicitly disclaiming behavioral authority. Runtime tests remain
the proof for rollback, process/thread fences, retained OpenSSL lifetime, stale
session rejection, and stream poison.

## Validation

The final rev0877 validation records:

- GCC 14.2 Debug complete all-target build and no-work dependency closure;
- 180/180 registered tests in one CTest invocation;
- 55/55 audit-named registered tests;
- 2,896/2,896 focused checks under GCC Debug;
- 2,896/2,896 focused checks under Clang 17 Release with C++ warnings fatal;
- 2,896/2,896 focused checks under GCC ASan/UBSan with leak detection and bundled
  SQLite instrumented;
- owner stress 20/20 and 3,780 checks;
- delivery-service stress 20/20 and 760 checks;
- TLS transport stress 50/50 and 1,250 checks; and
- 100/100 focused clock, lease, owner, and delivery-channel source-audit checks.

Exact logs, projection, lineage, manifest, and package results are recorded in
`RELEASE_GATE.json` and `REVISION_EVIDENCE/rev0877/`.

## Central gap and next step

No production executable calls the new service or authenticated TLS channel. The
path still stops at durable operation evidence rather than payload or visible
filesystem effect. The highest-value next step is one narrow restart-safe
executable that composes bounded payload transfer, content verification, effect
intent, atomic publication, directory durability, an effect-terminal receipt,
and exact sender settlement.

## Deliberate nonclaims

Rev0877 does not claim protection against hostile in-process code, concurrent
`SSL` mutation, nonblocking/event-loop transport, payload transfer,
filesystem-effect completion, independently signed receipts, exactly-once
effects, complete membership/key lifecycle, reconnect policy, complete
retry/dead-letter behavior, anti-entropy/compaction, production-scale performance
from the O(history) owner, anonymity, or use of this path by `anonsync_core`.

See `AUTHENTICATED_CHANNEL_CAPABILITY_AUDIT_rev0877.md` for the full mission
analysis, defect audit, primary-source research, remaining risks, speculation,
and recommended sequence.
