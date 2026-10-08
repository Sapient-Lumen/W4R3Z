# AnonSync rev0895 product-spine and TLS-client authority audit

## Audit question

Can the newer causal replica owners be invoked as one bounded production path without linking the self-test implementation corpus, spending a durable outbox claim before peer authorization, or converting network ambiguity into false retry authority?

## Result

Yes, for one file-delivery conversation under the explicit limits and nonclaims below.

Rev0895 adds a production outbound owner, `send_one_sync_replica_file_delivery_tls_session_or_throw`, and a separate `anonsync_replica` executable. The executable composes the causal SQLite owner, durable payload store, anchored TLS membership, receiver effect owner, and terminal receipt path. A registered process test invokes two independent product processes over real TCP and mutual TLS and proves exact destination bytes and sender terminal settlement.

This is a one-shot product spine, not a daemon or scheduler.

## Sender authority order

The sender preserves this order:

1. Validate all static configuration and absolute deadlines.
2. Validate the immutable payload-store snapshot and folder identity.
3. Perform a complete durable payload preflight.
4. Create and attest a nonblocking, close-on-exec socket.
5. Connect to a numeric IPv4 or unscoped IPv6 endpoint under an absolute deadline.
6. Complete a TLS 1.3 client handshake under an absolute deadline.
7. Derive the peer certificate SPKI and compare the exact expected pin.
8. Bind the expected actor to one authenticated-channel capability.
9. Claim at most one policy-compatible outbox item.
10. Begin dispatch under the SQLite guard and cross the complete TLS record-prefix cutpoint.
11. Finish the request body under the request deadline.
12. Read one complete bounded receipt under the receipt deadline.
13. Apply the receipt against the exact authenticated channel, request, operation, and current claim.
14. Attempt bounded `close_notify` only after an application terminal state where shutdown is useful.
15. Close the descriptor exactly once at owner destruction.

The claim cannot be reached by an unauthenticated peer or a missing local payload. Numeric-only addressing avoids silently granting a process-global resolver control over routing, search domains, blocking, or address churn.

## Ambiguity rules

- Connect deadline before socket creation: zero socket and zero claim authority.
- Connect or handshake failure: zero claim authority.
- SPKI mismatch or channel rejection: zero claim authority.
- No ready delivery after authentication: zero request bytes and no claim.
- Failure before the complete guarded request prefix: dispatch code may exact-release according to its existing pre-frontier contract.
- Timeout after the complete guarded request prefix: claim remains live and ambiguous.
- Peer close or receipt timeout: claim remains live and ambiguous.
- Complete authenticated receipt: exact receipt application decides the durable terminal state.
- TLS shutdown failure cannot roll back or downgrade an already applied receipt.

## Context lifetime

`SyncReplicaFileTlsClientContext` is move-only and retains `SSL_CTX` with OpenSSL reference counting. The caller still owns certificate, private-key, trust-store, ALPN, verification, and other context configuration. Concurrent mutation of the context while derived sessions are live is unsupported.

## Product commands

`anonsync_replica` supplies:

- `certificate-spki`: derive the lowercase SHA-256 SPKI pin from a PEM certificate.
- `membership-publish`: reconcile genesis or current anchored membership, then publish an exact next policy epoch.
- `enqueue-file`: read a bounded regular source file, durably place content in the payload store, and create one causal operation/outbox intent.
- `send-one`: authenticate and attempt one exact outbound delivery.
- `serve-one`: accept, authenticate, receive, publish, receipt, and close one exact inbound delivery.

All database, credential, source, and root paths are absolute. Network endpoints are numeric. JSON is emitted on stdout and diagnostics on stderr.

## Process-only defects found and corrected

### Membership genesis

The first CLI implementation called `current_authority_or_throw()` before any membership generation existed. A fresh deployment could not bootstrap. The command now calls the anchored coordinator's reconciliation path and publishes against the returned exact target, which handles genesis and the intentional two-database crash gap.

### Request-frame ceiling

The first CLI implementation set maximum request size to payload size plus a guessed 1 MiB. The protocol independently permits a larger evidence envelope. Both sender and receiver correctly refused the invalid relationship. The CLI now preserves the reviewed protocol default non-payload headroom:

`default max request frame - default max payload`

and adds that checked headroom to the selected payload ceiling.

### Clock authority

The default Linux clock source correctly reports synchronization as unknown when this container hides `adjtimex` or time-namespace capability evidence. That made the product capable of enqueue but incapable of lease claim. Rev0895 adds a paired, explicit operator-trusted profile for deployments that own clock discipline outside the process. It remains bounded by boot/time-namespace evidence, bracketed clocks, uncertainty limits, drift policy, quarantine, and recovery.

The profile is not selected by fallback and is not an attestation.

### Parent directories

The receiver refuses to manufacture missing destination directories. The process test pre-provisions the parent. This is retained deliberately because hidden directory creation would invent filesystem state without a causal operation or receipt meaning.

## Runtime proof

The focused TLS test covers:

- move-only client context retention;
- real TCP connect and real mutual TLS 1.3;
- expected SPKI and actor authorization;
- durable payload-store publication and snapshot;
- claim only after authentication;
- complete guarded request prefix and body;
- receiver file publication and receipt;
- exact sender settlement and converged evidence/visible-state digests;
- close-notify terminal behavior; and
- expired pre-connect deadline with zero socket/claim progress.

The process test additionally covers fresh database bootstrap, independently invoked CLI commands, separate sender/receiver databases, exact JSON surfaces, and exact binary destination bytes.

## Build/link boundary

`anonsync_replica` links the product replica owners and does not link `anonsync_selftests_lib`. In the observed GCC Debug build:

- `anonsync_core`: approximately 29 MiB;
- `anonsync_replica`: approximately 16 MiB;
- self-test symbol inventory in `anonsync_replica`: empty.

Debug size is compiler/configuration-specific and is not a release-size guarantee. The important property is the product link separation.

## Remaining risks and nonclaims

- One-shot operation only; no persistent listener or scheduler.
- No DNS/discovery, NAT traversal, relay, or endpoint privacy.
- No automatic recovery of durable clock quarantine.
- No directory/tombstone/rename/symlink semantics.
- No chunking or resumable large-file protocol.
- No GC or indexed catalog.
- No cross-database atomic transaction between membership, replica, effect, and payload stores.
- No exactly-once network delivery.
- No anonymity, unlinkability, private-interest overlap, traffic-analysis resistance, or at-rest encryption.
- No claim that TLS shutdown completion is part of application settlement.
- Linux exact socket authority only for the new production client path.
