# AnonSync rev0888 revision notes

## Mission

AnonSync is an evidence-authorized convergence system under construction.
Exact validated history and live owned capabilities govern operation identity,
causality, dispatch, retry, receiver effect, terminal receipt, settlement, and
cleanup. A TLS return code, zero byte count, socket readiness event, summary,
source audit, or build report remains subordinate evidence and cannot silently
mint authority.

Rev0888 closes the receiver's first receipt-prefix backpressure gap and removes
a duplicated transport state machine. One resumable write owner now carries the
exact encrypted record prefix and body from pre-I/O preparation through local
completion. A complete-suite timeout also exposed and corrected a lost-first-
request race in the SQLite connection-authority test harness rather than being
dismissed through a successful rerun.

## Concrete defect

Rev0887 correctly ordered complete request, durable idempotent effect decision,
and terminal receipt. Its receipt body used a typed write continuation, but the
8-byte record prefix was synchronously driven inside the begin factory. A real
nonblocking WANT at that first operation became an exception and stream discard.
The result could not truthfully distinguish:

- deadline before any receipt operation;
- an attempted zero-byte first-prefix WANT;
- partial prefix progress;
- complete prefix with partial body; or
- complete local receipt write.

The path was safe against silent stream reuse, but it was unnecessarily lossy
and duplicated prefix/body OpenSSL control flow.

## Unified prefix/body write authority

`SyncReplicaTlsRecordWriteContinuation` now owns in one heap-stable private
state:

- the exact encoded 8-byte prefix;
- the exact bounded copied frame;
- prefix and body offsets;
- the current operation phase;
- exact pending offset and length;
- pending WANT direction;
- whether any OpenSSL write was attempted; and
- the exclusive authenticated record-write reservation.

`prepare_sync_replica_tls_record_write_or_throw` validates the frame ceiling,
copies the body, constructs all state, validates/reserves the authenticated
stream, and returns before `SSL_write_ex`. This allows event-loop owners to
retain first-prefix WANT as typed state.

Each `advance_or_throw` performs at most one 64 KiB prefix or body operation.
Successful partial writes advance only their phase. WANT retains the same
private pointer and length. Prefix completion returns an explicit `Progress`
frontier without issuing a hidden body operation.

An untouched prepared owner releases its reservation without poisoning because
no TLS operation exists. Once any write is attempted, including a zero-byte
WANT, abandonment poisons the stream because the exact pending OpenSSL operation
cannot be replaced safely.

## Sender compatibility

The existing sender file-dispatch owner still calls the begin factory while its
SQLite outbox guard is live. That factory now delegates to the shared
continuation and drives only until `prefix_complete()`. The dispatch owner then
commits and releases the guard before body backpressure.

A prefix WANT in this guarded API remains a fail-closed exception and exact
pre-prefix claim release. The sender does not hold a database writer or claim
guard across network polling. Supporting sender prefix polling later requires an
explicit durable intermediate state, not a hidden relaxation of this cutpoint.

## Receiver post-effect receipt

The receiver exchange now uses the preparation factory. It owns first-prefix
WANT and body WANT through the same shared poll loop and independent absolute
receipt deadline. Its result records:

- `receipt_write_started`;
- `receipt_prefix_bytes_written`;
- `receipt_prefix_accepted`; and
- `receipt_body_bytes_written`.

Every deadline snapshots the exact local frontier and discards the application
channel. A durable inbound decision is never rolled back. A sender claim is
never settled by local timeout or local write progress.

The new real-TLS case forces:

> durable visible publication → saturated response path → first receipt-prefix
> `WANT_WRITE` with zero accepted prefix/body bytes → deadline

The result retains the durable `Published` decision and attempted-write
cutpoint, the visible file exists exactly once, the sender outbox remains live,
and the old stream is unusable. Exact retry continues to reconcile through the
existing receiver idempotency path.

## Audit and refactor

The retired synchronous prefix helper was removed. Prefix and body now share one
retry implementation, one socket/BIO/policy reproof path, one bounded-step rule,
one readiness owner, one abandonment rule, and one completion path.

`audit_sync_tls_write_continuation.py` and
`audit_sync_file_tls_exchange.py` were revised from their stale body-only and
prefix-synchronous assumptions. They now inventory phase identity, exact private
prefix/body pointers, untouched-versus-attempted cleanup, explicit prefix
progress, receiver diagnostics, deadline discard, and the forced first-prefix
WANT tests. They continue to declare that lexical shape cannot prove OpenSSL
retry semantics, deadlines, SQLite/file durability, peer receipt, exactly-once
effects, package integrity, or anonymity.

The README and release verifier now bind the rev0888 implementation and design
record instead of leaving the handoff at rev0886/rev0887 documentation state.

### Validation synchronization correction

The first complete registered-test invocation timed out in
`anonsync_sqlite_connection_authority_test`, although an immediate isolated run
passed. The `PolicyRetirementMutexProbe` worker initialized its wait predicate
from the current requested ticket. If ticket one was published before worker
startup, the worker waited for a later ticket and lost the only notification.

The worker now compares requested work with an explicit completed-ticket
frontier initialized to zero. A deterministic regression constructs the probe
with ticket one already published before the thread can enter its loop; the old
implementation necessarily blocks on that schedule. The SQLite mutex-capability
source audit now binds the corrected state machine and regression. See
`SQLITE_CONNECTION_AUTHORITY_TEST_SYNCHRONIZATION_AUDIT_rev0888.md`.

## Runtime and validation intent

The focused TLS executable covers preparation with zero I/O, caller mutation,
explicit prefix frontier, genuine first-prefix backpressure, continuation move,
abandonment poison, receiver post-effect prefix timeout, unchanged sender
settlement, and exactly one durable visible effect. It retains the parent matrix
for TLS 1.3 profile, peer pin, exporter, BIO/socket lifetime, descriptor ABA,
record-I/O policy, process/thread affinity, read/write continuation, duplex poll,
sender dispatch, receiver success/idempotency, malformed input, close, and
absolute deadlines.

Release evidence records independent GCC Debug, Clang Release `-Werror`, and
GCC ASan/UBSan runs, repeated real-TLS stress, registered tests, lexical audits,
active source projection, exact parent delta, and package verification. Exact
counts belong to `REVISION_EVIDENCE/rev0888/validation/VALIDATION_SUMMARY.json`
and `RELEASE_GATE.json`, not this narrative.

## Online protocol review

The implementation follows the OpenSSL 3.5 `SSL_write_ex` rule that a WANT retry
uses the same arguments unless moving-write-buffer mode is enabled. It retains a
stable private pointer and exact length regardless. Successful partial writes
are treated as completed bounded operations; a new operation is created only
from the resulting cutpoint.

Primary references:

- <https://docs.openssl.org/3.5/man3/SSL_write/>
- <https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/>

These specifications constrain but do not prove the C++ implementation.

## Remaining severe gaps

Rev0888 does not provide a production listener or replica daemon, membership
and key lifecycle, persistent retry/dead-letter policy, peer/folder resource
quotas, staging expiry/garbage collection, complete crash injection, indexed hot
ownership, causal compaction/rejoin, deletion/rename/conflict protocols,
traffic-analysis resistance, unlinkability, implemented anonymity, or externally
trusted build provenance.

The next useful slice is still a small long-running replica service that owns
authenticated connection acceptance, invokes one bounded receiver conversation,
closes/discards terminal channels, and records typed retry/dead-letter state.
The current full-history SQLite owner should remain the correctness, migration,
repair, and differential oracle while a scalable indexed owner is introduced.
