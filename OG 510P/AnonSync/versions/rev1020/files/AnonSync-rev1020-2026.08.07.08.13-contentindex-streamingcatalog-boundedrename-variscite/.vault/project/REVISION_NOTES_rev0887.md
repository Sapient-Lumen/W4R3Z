# AnonSync rev0887 revision notes

## Mission

AnonSync is an evidence-authorized convergence system under construction.
Exact validated history and live owned capabilities govern identity, causality,
dispatch, retry, receipt, visible effect, and cleanup. TLS return codes, socket
readiness, descriptor integers, local write completion, summaries, source
audits, and build reports remain subordinate evidence. None may silently mint
peer authority, receiver effect, sender settlement, or anonymity.

Rev0887 closes two adjacent transport-composition gaps and corrects one stale
test abstraction:

1. the authenticated TLS capability now binds the exact OpenSSL record-I/O
   policy observed at authentication and re-proves it at ordinary authority,
   fresh operation, pending WANT retry, and readiness-target frontiers;
2. one production receiver exchange now owns complete bounded request,
   durable idempotent file/evidence decision, live receipt-frontier
   re-attestation, and exact bounded receipt emission under two independent
   absolute deadlines; and
3. the shared TLS test driver now accepts both raw and file-dispatch write
   continuations through one stable lvalue template instead of a stale concrete
   type.

## Record-I/O policy authority

The rev0886 channel bound peer SPKI, exporter, exact BIO objects, Linux socket
lifetimes, and strict nonblocking readiness. It did not freeze mutable
per-`SSL*` record semantics.

A caller retaining the raw OpenSSL handle could change options, modes,
read-ahead, quiet shutdown, verification mode, or shutdown bits after
authentication while continuing to borrow the old peer/exporter capability.
The sharpest example was `SSL_OP_IGNORE_UNEXPECTED_EOF`, which could recast an
abrupt socket closure as clean TLS shutdown and weaken AnonSync's explicit
close-versus-truncation frontier.

Rev0887 extracts `sync_replica_tls_io_policy` as one narrow authority leaf. It
normalizes safe context defaults, captures the complete live policy value,
requires exact equality on reproof, and poisons the channel after any observed
contradiction. A pending WANT retry deliberately re-proves transport and policy
without inserting unrelated OpenSSL calls between the exact I/O result and its
`SSL_get_error` classification.

Exact equality also documents the residual limit: observable reproof cannot
detect a transient mutate-and-restore race without exclusive ownership of the
raw `SSL*`. The public contract does not claim otherwise.

See `TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md` for the full failure
matrix, primary OpenSSL references, rejected alternatives, and nonclaims.

## Receiver exchange authority

### Missing production seam

Before this revision, the sender had a guarded first-prefix owner, while the
receiver path existed only as manual test/caller choreography:

1. read one TLS record;
2. call `SyncReplicaFileDeliveryService::receive_request_or_throw`;
3. write its receipt; and
4. let the sender read and apply that receipt.

That ordering is load-bearing. A caller could otherwise invoke durable logic on
partial bytes, reuse a channel after an abandoned application conversation,
renew one relative timeout across request and response, or treat local TLS
write completion as peer receipt.

### New C++ leaf

Rev0887 adds:

- `src/sync_replica_file_tls_exchange.hpp`;
- `src/sync_replica_file_tls_exchange.cpp`; and
- `anonsync_sync_replica_file_tls_exchange`.

`receive_one_sync_replica_file_delivery_over_tls_or_throw` owns exactly one
strict-nonblocking receiver conversation:

> complete bounded authenticated request → durable idempotent effect/evidence
> decision → live channel re-attestation → exact authenticated receipt

The exchange consumes the file service's own request and receipt ceilings. Each
fresh OpenSSL operation is bounded by the transport's 64 KiB step. Every pending
WANT is resumed only through the existing poll owner and one absolute
`steady_clock` cutpoint.

### Independent request and receipt deadlines

The request deadline governs willingness to acquire a complete request. Expiry
before completion invokes no durable callback.

The receipt deadline starts as an independently supplied absolute cutpoint. If
it is exhausted after the receiver has durably published or classified the
effect, the exchange returns that exact inbound decision but does not roll it
back, does not emit a fake terminal receipt, and does not settle the sender.
The sender claim remains live until an authenticated terminal receipt, explicit
exact release, or owned-clock expiry permits a fresh attempt.

### Application stream discard

A complete malformed request or a durable effect with an abandoned response can
leave TLS record framing synchronized while application sequencing is not.
Rev0887 therefore adds
`discard_sync_replica_tls_authenticated_channel_noexcept`. It permanently
poisons the local authenticated capability without claiming TLS shutdown,
remote observation, socket closure, or delivery.

An already-expired request budget, malformed complete frame, post-effect
exception, pre-prefix response timeout, or active continuation abandonment
cannot leave the old application stream reusable.

### Exact result classes

`SyncReplicaFileTlsReceiveResult` distinguishes:

- clean `PeerClosed` before a frame;
- `RequestDeadlineExpired` before a complete request;
- `ReceiptDeadlineExpired` after a durable inbound decision but before local
  receipt completion; and
- `ReceiptSent` after OpenSSL locally accepts the complete receipt record.

It retains request and receipt prefix/body cutpoints for diagnostics. Those
numbers are not peer receipt, receiver durability by themselves, sender
settlement, or exactly-once network delivery. The exact durable inbound value is
present only after the receiver service returns. Its move into the result is
statically required to be no-throw.

See `TLS_RECEIVER_EXCHANGE_CUTPOINT_AUDIT_rev0887.md` for the state table,
timeout/exception matrix, online TLS 1.3 replay review, and remaining production
gaps.

## Audit and refactor correction

The recovered pre-seal rev0887 test source contained a helper accepting only
`SyncReplicaTlsRecordWriteContinuation&`, while two call sites passed the newer
`SyncReplicaFileTlsDispatchContinuation`. That was a concrete compile-time
break in the unfinished tree even though both continuations intentionally share
the same bounded progress vocabulary.

The helper is now a template over one stable lvalue continuation. It does not
perfect-forward or move the owner across repeated operations. Existing source
audits were also corrected to look for the current semantic labels and shared
`label + " write poll"` owner rather than obsolete exact string literals.
Those audits remain lexical hygiene, not runtime proof.

## Runtime evidence

The real TLS 1.3 integration executable covers:

- record-I/O policy normalization, live mutation rejection, pending WANT
  mutation, and abrupt socket closure classification;
- exact BIO/socket identity, descriptor ABA, nonblocking policy, process/thread
  affinity, bounded read/write continuations, duplex poll, and sender
  first-prefix dispatch;
- receiver success from complete request through visible file publication and
  terminal receipt settlement;
- zero-prefix receipt expiry after durable publication;
- sender intent remaining live after the ambiguous response;
- owner-clock expiry and a fresh channel/claim retry;
- receiver reconciliation as `AlreadyPublished` with one retained effect and
  unchanged bytes;
- a genuine partial-frame WANT retaining exact prefix/body progress until the
  request deadline with unchanged receiver/effect snapshots;
- already-expired request handling with unchanged receiver/effect snapshots;
  and
- complete malformed-frame rejection with no durable mutation and no reusable
  application stream.

The registered `audit_sync_file_tls_exchange.py` inventory checks source shape,
build wiring, and ordering vocabulary. It explicitly does not prove OpenSSL
retry identity, deadline behavior, SQLite durability, filesystem publication,
crash recovery, peer receipt, package integrity, exactly-once effects, or
anonymity.

## Online protocol review

The TLS profile continues to disable early data and reject resumed sessions.
RFC 8446 section 8 treats 0-RTT application data as replayable and requires the
application to own replay safety. Receiver idempotency is defense in depth, not
permission to enable early data silently.

Primary references reviewed for rev0887 are recorded in the two TLS audit
documents and include OpenSSL 3.5 manuals for options, modes, shutdown,
`SSL_read_ex`, `SSL_write_ex`, `SSL_get_error`, and early data, plus RFC 8446.

## Remaining severe gaps

Rev0887 does **not** provide:

- a production listener, connection acceptor, or long-running replica service;
- membership enrollment, key epochs, rotation, revocation, recovery, or rollback
  protection;
- peer/folder quotas, fairness, bounded staging lifetime, dead-letter ownership,
  or garbage collection;
- a crash-injection matrix across every OpenSSL, SQLite, payload, rename,
  directory-durability, receipt, and settlement frontier;
- indexed production ownership with differential convergence against the
  full-history SQLite oracle;
- causal compaction, tombstone retirement, checkpoint/rejoin authority, or
  offline/revoked replica policy;
- deletion, rename, directory, permission, or conflict-effect protocols;
- traffic-analysis resistance, unlinkability, anonymity, or metadata privacy;
  or
- externally trusted build provenance.

The next useful milestone is a small replica service that owns authenticated
connection acceptance, invokes this exchange once per application
conversation, closes/discards terminal channels, and persists bounded
retry/dead-letter policy. The current full-history owner should remain the
correctness, repair, migration, and differential oracle while a scalable
indexed owner is introduced.
