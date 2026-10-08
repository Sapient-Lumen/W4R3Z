# AnonSync revision notes — rev0889

## Revision theme

Rev0889 closes both sides of the receiver transport boundary. Before the first
application byte, the selected service must prove live channel binding and
receiver effect authority. After that gate, one move-only session owns exactly
one request/receipt conversation. Outside the session, one exact Linux listener
capability now owns atomic accept, bounded mutual-TLS handshake, verified-SPKI
membership resolution, accepted socket/`SSL` lifetime, the receiver session,
and subordinate terminal shutdown.

The revision also refactors process-inheritance and absolute-deadline polling
into shared socket capability leaves, corrects two subtle failure-classification
and moved-from fail-stop defects, and performs a deep audit of permanent
receiver staging pressure.

## Parent

The exact parent handoff is:

`AnonSync-rev0888-2026.07.23.03.26-prefixwant-wholerecord-ticketfrontier-cleanevidence.zip`

The parent archive digest and exact parent-relative delta are recorded in
`REVISION_EVIDENCE/rev0889/LINEAGE.json` and `LINEAGE.md`.

## Production C++ changes

### Pre-byte receiver authority

Extended:

- `src/sync_replica_file_delivery_service.hpp`
- `src/sync_replica_file_delivery_service.cpp`
- `src/sync_replica_file_tls_exchange.hpp`
- `src/sync_replica_file_tls_exchange.cpp`

`SyncReplicaFileDeliveryService::preflight_inbound_channel_or_throw()` now
revalidates the opaque live delivery channel and proves that the selected
service owns receiver file-effect authority. The TLS exchange performs this
gate after preparing diagnostics but before reserving the TLS reader or
consuming an application byte. `receive_request_or_throw()` repeats the same
preflight at the complete-frame durable frontier; early admission cannot survive
arbitrary network delay, channel mutation, or process/thread change as durable
authority.

Every borrowed one-conversation exchange terminalizes the local authenticated
capability on success, timeout, peer close, preflight failure, or exception. A
complete local receipt remains exactly that: it does not prove peer receipt or
sender settlement.

### Exclusive receiver session

Added `SyncReplicaFileTlsReceiverSession`, a non-default-constructible,
noncopyable, move-only owner for:

- one borrowed delivery service whose lifetime must outlive the session;
- one authenticated channel;
- one absolute request cutpoint;
- one absolute receipt cutpoint; and
- one stable diagnostic label.

Construction preflights before moving the caller's channel. Custom move
operations explicitly disengage the source `std::optional`; standard optional
move alone would leave `has_value()` true around a moved-from channel. One
`run_or_throw()` consumes the lifecycle. Success, timeout, peer close, exception,
explicit discard, destruction, or move-assignment over an active target leaves
no reusable local application capability.

### Accepted TLS receiver owner

Added:

- `src/sync_replica_file_tls_server.hpp`
- `src/sync_replica_file_tls_server.cpp`

The move-only, non-owning listener capability binds:

- one exact Linux `SOCK_STREAM` lifetime;
- `O_NONBLOCK` readiness policy;
- `FD_CLOEXEC` process-inheritance policy;
- `SO_ACCEPTCONN` listening state; and
- the creating process and exact thread incarnation.

The one-shot accepted-session owner:

1. re-proves the listener and one absolute accept cutpoint;
2. calls `accept4(SOCK_NONBLOCK | SOCK_CLOEXEC)`;
3. scope-owns and closes the accepted descriptor exactly once;
4. creates and scope-owns one server `SSL` object;
5. drives a bounded nonblocking TLS 1.3 mutual-authentication handshake;
6. derives the verified peer SubjectPublicKeyInfo SHA-256;
7. requires an explicit SPKI-to-`SyncReplicaActor` membership mapping;
8. constructs the authenticated channel;
9. transfers it into one `SyncReplicaFileTlsReceiverSession`;
10. preserves the exact receiver result; and
11. only after `ReceiptSent`, attempts bounded one-shot TLS shutdown.

Accept timeout, silent ClientHello, plaintext on the TLS port, handshake
rejection, and a certificate-valid but membership-unmapped peer all terminate
before the durable file service. Shutdown state is subordinate diagnostic
information and cannot downgrade a complete local receipt or claim that the
peer applied it.

The caller retains the listening descriptor and must serialize close, `dup2`,
flag, and listen-state mutation. The caller also keeps the configured `SSL_CTX`
and membership backing state alive and mutation-stable during the synchronous
call.

### Shared exact socket policy and poll

Added:

- `src/sync_stream_socket_deadline_poll.hpp`
- `src/sync_stream_socket_deadline_poll.cpp`

Extended:

- `src/sync_socket_readiness_identity.hpp`
- `src/sync_socket_readiness_identity.cpp`

`require_sync_stream_socket_close_on_exec_or_throw()` uses the same
lifetime–policy–lifetime sandwich as the existing `O_NONBLOCK` proof.
`FD_CLOEXEC` remains mutable process-inheritance policy, not kernel socket
identity.

`poll_sync_stream_socket_until_or_throw()` retains one exact socket lifetime and
one absolute monotonic cutpoint across `EINTR` and portable `EAGAIN`, ceiling-
rounds finite millisecond timeouts, re-proves lifetime/readiness policy after
wakeup, and reports only advisory `Ready` or `DeadlineExpired`. Protocol
progress, peer close, and errors remain owned by the subsequent exact kernel or
OpenSSL operation.

### Device-isolated capacity, exact migration, and copy-frontier refactor

Extended:

- `src/sync_replica_file_effect_sqlite_owner.hpp`
- `src/sync_replica_file_effect_sqlite_owner.cpp`
- `src/sync_replica_file_delivery_service.hpp`
- `src/sync_replica_file_delivery_service.cpp`

The file-effect database advances from exact schema v2 to exact schema v3. The
new durable policy fields bound effect count and retained payload bytes per
`device_id` across every retained actor epoch. Folder limits retain deterministic
precedence and remain the final aggregate safety boundary. Exact duplicates are
resolved before quota checks, so an ambiguous-response retry can reconcile even
when current policy is saturated. Existing rows that predate a stricter device
policy remain canonical and only block future unique admission.

Every owner load derives sorted actor-epoch and device usage from the complete
retained row closure. Schema v3 persists only compact witnesses (`device_count`
and `device_usage_digest`) and binds them, the two device limits, the legacy
policy, state totals, and effect-set digest into a new cutpoint. A cached counter
never becomes admission authority. The device aggregation deliberately does not
claim human, account, tenant, or membership-principal semantics.

An exact v2 database is migrated under one `BEGIN IMMEDIATE` transaction. The
owner re-attests every v2 policy field and retained row before DDL, preserves all
legacy policy regardless of conflicting caller defaults, imports only the two
new device-limit fields, replaces only the metadata table, verifies exact v3
schema, reloads, and compares retained rows/generation/policy before commit. A
compiled authorizer fault injected after `DROP`/`CREATE` proves failed metadata
insertion rolls the schema back to exact v2; a subsequent retry succeeds.
Tampered v2 and v3 digests fail closed.

`stage_with_diagnostics_or_throw()` now identifies the first violated folder or
device count/byte constraint and returns exact subtraction-safe budgets, current
actor/device usage, and the inspected generation/cutpoint. The file service keeps
that detail receiver-local. The peer still receives only the bounded generic
`EffectCapacityBlocked` disposition, causal evidence is not admitted, and sender-
local policy owns exact retry release.

The review also found redundant full-object copying. New rows are now encoded
directly into one `StoredEffect` and moved into the sorted closure; derived
usage/digest objects move into the loaded state. Constructor, stage,
materialization, and attestation use an `AuthorityOnly` projection and no longer
construct a complete public effect-record vector that no caller observes. Only
`snapshot_or_throw()` materializes `PublicSnapshot`, moving validated records
into the returned view. The service likewise moves its decoded payload-bearing
request after durable stage.

This refactor does not change the owner's role as an O(history) correctness
oracle: it still loads and hashes every retained payload and validates every
canonical operation on each public operation. It also does not provide total
disk charging, a stable membership principal, protected reserve, fair
scheduling, pre-transfer reservations, or reclamation. Those findings are in
`FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md`,
`FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md`, and
`RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md`.

### Corrections found during review

Two non-obvious defects were corrected before sealing:

- The accepted-session profile step initially caught every `std::exception` and
  could classify local allocation/resource failure as hostile peer behavior. It
  now catches only profile-validation `std::runtime_error`; other local failures
  propagate distinctly.
- Listener use initially checked the process fail-stop guard before checking
  whether the move-only wrapper was inactive. Harmless use-after-move could
  therefore terminate the process. Activity is now checked first. An active
  capability inherited across a process boundary still reaches the fail-stop
  guard, while a moved-from local wrapper throws `logic_error`.

## Runtime coverage

Extended:

- `tests/sync_socket_readiness_identity_test.cpp`
- `tests/sync_replica_tls_transport_test.cpp`

New compiled coverage includes:

- pre-byte sender-only service rejection with queued TLS ciphertext, unchanged
  `FIONREAD`, unchanged SQLite snapshot, no response, and poisoned borrowed
  channel;
- receiver-session construction, move-only single ownership, exact-once run,
  post-success inactivity, and second-run rejection;
- post-success borrowed-exchange channel terminalization;
- blocking, inheritable, and non-listening listener rejection;
- post-mint `O_NONBLOCK` and `FD_CLOEXEC` mutation rejection before `accept4`;
- moved-from listener rejection before process fail-stop;
- accept timeout with no durable mutation;
- connected silent-peer handshake timeout with no durable mutation;
- plaintext-on-TLS handshake rejection with no durable mutation;
- certificate-valid but membership-unmapped peer rejection;
- full loopback TCP/mutual-TLS/membership/request/publication/receipt/sender-
  settlement/canonical-digest convergence;
- close-notify diagnostic separation;
- independent close-on-exec policy mutation;
- already-expired, readable, writable, and peer-hangup advisory socket polling;
- caller operation, rather than poll, classification of peer EOF;
- exact actor-epoch and multi-epoch device usage derivation;
- byte-for-byte identical usage reconstruction after owner restart;
- deterministic folder-before-device constraint precedence;
- exact duplicate admission while folder or device policy is saturated;
- independently classified folder/device count and retained-byte pressure;
- exact v2 fixture attestation and v2-to-v3 policy migration;
- preservation of legacy policy despite conflicting caller defaults;
- invalid/tampered migration refusal before DDL;
- post-DDL fault injection with transactional schema rollback and clean retry;
- v3 device-usage-digest tamper rejection;
- independent-device admission while another device is saturated;
- capacity diagnostics bound to the exact pre-evidence effect cutpoint; and
- receiver-local device detail with unchanged generic wire disposition, no
  causal admission, and exact sender retry release.

## Audit and refactor work

Added:

- `tools/audit_sync_file_tls_receiver_session.py`
- `tools/audit_sync_file_tls_server.py`
- `TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md`
- `TLS_ACCEPTED_SESSION_AUTHORITY_AUDIT_rev0889.md`
- `RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md`
- `tools/audit_sync_file_effect_capacity_accounting.py`
- `FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md`

Refactored:

- `tools/audit_sync_file_tls_exchange.py` so its lexical inventory follows the
  pre-byte preflight and terminal-discard contract;
- `tools/audit_sync_socket_readiness_identity.py` so it inventories the
  separate close-on-exec policy and shared absolute-deadline poll leaf; and
- CMake and release package policy so the complete inner/outer receiver surface
  is built, tested, audited, and mandatory from rev0889 onward.

The lexical audits explicitly disclaim semantic authority. Compiled tests,
independent compiler and sanitizer lanes, stress, exact lineage, and package
verification remain the load-bearing evidence.

The staging fairness audit identifies a severe remaining liveness defect:
staged and published payloads consume one permanent folder-global count/byte
budget. There is no per-membership-principal reserve or quota, fair scheduler,
expiry, dead-letter owner, causal-stability proof, or garbage collection. An
authorized actor or normal long-lived churn can therefore starve unrelated
peers indefinitely. Rev0889 now completes only the actor/device accounting and
typed local-pressure subset of Phase 1. It does not delete exact payload
evidence merely to make a counter fall; the audits specify safe principal
identity, reservation, lifecycle, compaction, overload, and crash-test work.

## Validation

Final validation results are bound under:

- `REVISION_EVIDENCE/rev0889/validation/VALIDATION_SUMMARY.json`
- `REVISION_EVIDENCE/rev0889/AUDIT.md`
- `RELEASE_GATE.json`

The handoff archive is published only after the final staged directory and the
immutable ZIP independently pass the release package verifier.

## Remaining priority work

The next highest-value storage implementation is a persisted, versioned
membership-principal quota policy with idempotent operation reservations and a
protected reserve for other principals, differentially tested against the
full-history accounting oracle. In parallel, a small long-running service around
the one-shot accepted owner should add bounded concurrent accepts and handshakes,
per-peer/folder admission and receiver capacity, durable membership/key epoch
lifecycle, structured pressure telemetry, graceful drain, and crash injection
at transport, SQLite, payload, publication, receipt, settlement, and close
frontiers.

The current full-history SQLite owners should remain correctness, migration,
repair, and differential oracles while a separate indexed production owner is
developed. Safe payload retirement requires causal stability and explicit
rejoin/compaction policy, not age-only deletion.

## Nonclaims

Rev0889 does not claim a production daemon, internet deployment safety,
certificate enrollment/revocation/rotation/recovery, fair scheduling, staged-
payload garbage collection, client-side bounded connect ownership,
multi-operation sessions, exactly-once network delivery, atomicity across
independent databases, anonymity, unlinkability, traffic-analysis resistance,
formal verification, or externally trusted build provenance.

It proves a narrower executable slice in this cloudtainer: one accepted Linux
listener/child/TLS/member/receiver-session lifecycle can reject static local role
failure before consuming application bytes, keep preauthentication failures out
of durable authority, publish and receipt one canonical file operation, and
separate application terminal state from transport shutdown diagnostics.
