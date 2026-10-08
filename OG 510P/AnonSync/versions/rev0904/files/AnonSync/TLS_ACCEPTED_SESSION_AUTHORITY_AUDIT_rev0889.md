# Accepted TLS session authority audit — rev0889

## Mission connection

AnonSync is not trying to prove that bytes crossed a socket. It is trying to
ensure that only exact authorized evidence can reach durable causal and visible
effect authority, and that every ambiguous frontier remains explicit after
failure or retry.

Before rev0889, the strongest receiver path began with a caller-supplied,
already-handshaken `SSL*`. The authenticated channel, bounded record reader,
idempotent SQLite receiver, atomic file publisher, receipt continuation, and
sender settlement rules were implemented and tested, but the path into that
correctness island was missing from production C++:

- no owner proved the listening socket;
- no owner atomically accepted a nonblocking, non-inheritable child;
- no owner bounded a slow or malformed TLS handshake;
- no owner mapped a verified certificate key to an authorized actor epoch; and
- no owner defined whether terminal TLS shutdown could alter application
  settlement.

That missing seam mattered more than another isolated protocol helper. A daemon
cannot safely delegate these decisions to unspecified glue without recreating
exactly the authority confusion the inner model is designed to prevent.

Rev0889 adds one narrow, synchronous, one-shot receiver session owner. It is not
a daemon and does not claim to be one. It is the first production-source
composition from a live Linux listening socket through mutual TLS, membership,
durable receiver effect, exact receipt, and terminal transport cleanup.

## Owned authority chain

`serve_one_sync_replica_file_delivery_tls_session_or_throw()` owns this chain:

1. a move-only, non-owning capability for one exact listening socket lifetime;
2. one bounded `accept4()` attempt loop under an absolute steady-clock cutpoint;
3. one scope-owned accepted descriptor created with `SOCK_NONBLOCK |
   SOCK_CLOEXEC`;
4. one scope-owned OpenSSL `SSL` object bound to that child descriptor;
5. one bounded nonblocking server handshake;
6. one verified peer SubjectPublicKeyInfo digest;
7. one caller-owned membership decision mapping that digest to an exact
   `SyncReplicaActor` epoch;
8. one authenticated TLS channel capability;
9. one complete bounded file-delivery conversation using the existing receiver
   exchange owner;
10. an optional one-shot `close_notify` attempt after a complete local receipt;
   and
11. unconditional destruction of the `SSL` object followed by one close of the
   accepted descriptor.

The listening descriptor remains caller-owned. The capability explicitly
requires the caller to serialize `close`, `dup2`, `fcntl`, and listen-state
mutation while it is active. Descriptor ownership and descriptor authority are
not conflated.

## Listener capability

The listener capability is minted only after proving:

- `SOCK_STREAM` semantics;
- the exact Linux descriptor lifetime tuple already used by the TLS transport
  anchor, including a nonzero `SO_COOKIE`;
- `O_NONBLOCK` as mutable readiness policy;
- `FD_CLOEXEC` as separate process-inheritance policy;
- `SO_ACCEPTCONN == 1` between exact lifetime reproofs; and
- the current process and thread incarnation.

The capability is move-only. A moved-from instance is inactive. Rev0889 checks
that inactive state before the process-incarnation fail-stop guard: ordinary
local use-after-move throws, while an active capability inherited across `fork`
still retains its socket proof and fail-stops at the process boundary. Every
accept attempt re-attests process, thread, socket lifetime, nonblocking policy,
close-on-exec policy, and accepting state before spending the listener.

This does not make raw descriptor mutation impossible. The kernel API exposes
an integer descriptor and the caller still owns it. The capability catches
observable contradiction and fails closed; external serialization remains part
of the contract. Compiled tests mutate both `FD_CLOEXEC` and `O_NONBLOCK` after
minting and prove that the next session use rejects them before `accept4` or any
durable callback.

## Atomic accepted-child policy

Linux does not require an accepted socket to inherit `O_NONBLOCK` from its
listener. Setting flags later with `fcntl` would create a window in which
another thread or an `exec` could observe the child with the wrong policy.
Rev0889 therefore uses:

```text
accept4(listener, nullptr, nullptr, SOCK_NONBLOCK | SOCK_CLOEXEC)
```

The accepted descriptor immediately enters one move-only RAII owner. Before it
can reach OpenSSL, the code independently observes its exact stream-socket
lifetime and re-proves both `O_NONBLOCK` and `FD_CLOEXEC`.

Linux can surface pending network errors directly from `accept4`. The retry
classifier preserves one absolute cutpoint across `EINTR`, empty-queue
`EAGAIN`/`EWOULDBLOCK`, `ECONNABORTED`, `EPROTO`, and the documented TCP/IP
network-error set. Resource exhaustion and structural listener errors remain
local exceptions rather than being spun indefinitely.

The child owner performs one `close` call and never retries after `EINTR`.
Retrying `close` on Linux can target an unrelated descriptor if the number has
already been reused. The local owner relinquishes the number before making that
single diagnostic-ignored close call.

## Shared absolute-deadline poll refactor

Rev0889 extracts `poll_sync_stream_socket_until_or_throw()` as a protocol-neutral
leaf shared by accept, handshake, and shutdown.

The poll owner:

- retains one exact `SyncSocketLifetimeIdentity`;
- requires `O_NONBLOCK` before each wait;
- derives each finite millisecond timeout from the original absolute
  `steady_clock` deadline;
- ceiling-rounds positive sub-millisecond remainders and clamps at `INT_MAX`;
- retries `EINTR` and portable `EAGAIN` without resetting the deadline;
- rechecks the absolute cutpoint after wakeup;
- re-proves exact socket lifetime and nonblocking policy before returning; and
- reports only advisory `Ready` or `DeadlineExpired`.

`POLLERR`, `POLLHUP`, and `POLLNVAL` are wakeups, not protocol outcomes. The
caller must issue the exact next `accept4` or OpenSSL operation and classify its
result. This prevents readiness vocabulary from silently becoming delivery,
peer-close, or settlement authority.

`FD_CLOEXEC` checking was likewise moved into the generic socket capability
leaf. It remains distinct from lifetime identity and from I/O readiness.

## Handshake cutpoint and OpenSSL retry contract

The accepted child is nonblocking before `SSL_accept`. Every handshake attempt:

1. re-proves the exact socket and nonblocking policy;
2. checks the absolute handshake cutpoint;
3. clears the current thread's OpenSSL error queue;
4. calls `SSL_accept` once;
5. on non-success, calls `SSL_get_error` immediately on the same thread with no
   intervening OpenSSL operation;
6. retries only `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` after the shared
   bounded poll; and
7. classifies all other OpenSSL outcomes as handshake rejection.

A connected peer that sends no `ClientHello` therefore consumes at most the
handshake budget for this one-shot owner. Plaintext on the TLS port is a typed
handshake rejection. Neither path can invoke the durable file service.

This owner does not yet impose a global concurrent-handshake limit, a per-source
rate, a certificate-chain byte budget beyond OpenSSL/context policy, or a fair
accept scheduler. Those belong to the future daemon and overload owner.

## Certificate validity is not membership

A completed mutual-TLS handshake proves only the configured certificate and TLS
profile. It does not authorize an AnonSync actor.

After handshake completion, the server derives the verified peer certificate's
lowercase SHA-256 SubjectPublicKeyInfo digest. The caller-supplied membership
resolver must map that exact digest to one `SyncReplicaActor {device_id, epoch}`.
Returning `nullopt` closes the session before the durable receiver callback.
The same observed digest is then used as the exact pin when constructing the
existing authenticated channel capability.

The resolver is intentionally not implemented as a global trust-store lookup.
Enrollment, revocation, key rotation, actor-epoch transitions, recovery, and
persistent membership policy are still missing product work. The callback is a
narrow dependency-injection seam that prevents a generic certificate authority
from silently authorizing every valid certificate as a replica. The caller must
keep the configured `SSL_CTX` alive and mutation-stable for the call and must
serialize the resolver's backing membership state; neither dependency is owned
by this one-shot session.

Profile-evidence failures after the cryptographic handshake are mapped to
`HandshakeRejected`. The catch is deliberately limited to `std::runtime_error`.
Local failures such as `std::bad_alloc` propagate; resource exhaustion is not
laundered into hostile-peer evidence.

## Durable receiver frontier

No request byte reaches `SyncReplicaFileDeliveryService` until:

- TCP accept succeeded;
- the child socket policy was proved;
- mutual TLS completed under the exact profile;
- the verified SPKI was observed;
- membership supplied an exact actor epoch; and
- the authenticated channel re-attested the live TLS session, BIOs, socket
  lifetime, peer SPKI, exporter binding, and record-I/O policy.

The existing receiver exchange then owns:

- complete bounded request framing;
- request/channel/folder/actor binding;
- payload staging;
- causal evidence admission;
- exact projection guard;
- atomic file publication or idempotent reconciliation;
- receipt construction; and
- bounded receipt prefix/body transmission.

The new server does not reinterpret those outcomes. It maps the exact receiver
terminal state into `PeerClosed`, `RequestDeadlineExpired`,
`ReceiptDeadlineExpired`, or `ReceiptSent`.

## Shutdown is subordinate, not settlement

`ReceiptSent` means the complete local TLS receipt record was accepted by
OpenSSL under the receiver's deadline. It does not prove that the peer read the
record or durably settled its outbox.

Only after `ReceiptSent` does the server attempt `SSL_shutdown`. The application
protocol is one-shot and admits no further application record, so a successful
first-stage TLS shutdown is sufficient transport hygiene for this owner:

- return `1`: local and peer `close_notify` observed (`Complete`);
- return `0`: local `close_notify` sent, peer response outstanding
  (`CloseNotifySent`); this is explicitly not an error and `SSL_get_error` is
  not called;
- return `< 0` with WANT: bounded poll and exact retry;
- fatal/other result: `Failed`; or
- absolute cutpoint reached: `DeadlineExpired`.

A shutdown reproof, poll, or OpenSSL failure cannot downgrade `ReceiptSent`.
Cleanup disposition is a subordinate diagnostic field. Conversely, the server
never calls `SSL_shutdown` after handshake rejection, request truncation,
receipt deadline, or another nonterminal exchange path because an exact pending
OpenSSL operation or fatal stream may exist.

## Failure matrix

| Frontier | Required behavior |
|---|---|
| Blocking, inheritable, non-stream, non-listening, stale, moved-from, foreign-process, or foreign-thread listener | Reject before `accept4` |
| Accept cutpoint already spent or no queued child before cutpoint | `AcceptDeadlineExpired`; no `SSL`, child, or durable callback |
| Retryable Linux accept/network error | Retain original absolute cutpoint and retry |
| Fatal/resource accept error | Throw as local failure; do not spin or label a peer |
| Accepted child | Atomically nonblocking+CLOEXEC, scope-owned, independently re-proved |
| Peer stalls before handshake completion | `HandshakeDeadlineExpired`; close child; no durable callback |
| Plaintext or fatal TLS handshake | `HandshakeRejected`; no durable callback or `SSL_shutdown` |
| Valid certificate/profile but unmapped SPKI | `PeerUnauthorized`; no durable callback |
| Membership resolver returns invalid actor | Authenticated-channel validation throws local policy error |
| Request cleanly closes before a frame | `PeerClosed`; no fabricated request |
| Request deadline | Preserve receiver exchange diagnostics; no shutdown attempt |
| Durable effect followed by receipt deadline | Preserve durable idempotent effect; report `ReceiptDeadlineExpired`; exact retry reconciles later |
| Complete receipt write | `ReceiptSent`; application terminal result retained |
| Post-receipt shutdown return zero | `CloseNotifySent`; never call `SSL_get_error` for zero |
| Post-receipt shutdown failure/timeout | Keep `ReceiptSent`; record subordinate shutdown state |
| Any scope exit | Free `SSL`, then close accepted descriptor once; listener remains caller-owned |

## Runtime evidence added in this revision

The compiled Linux/real-TLS matrix now exercises:

1. blocking listener rejection;
2. missing `FD_CLOEXEC` rejection;
3. non-listening stream-socket rejection;
4. move-only listener invalidation;
5. no-peer accept timeout with exact no-mutation snapshots;
6. connected slow-handshake timeout with exact no-mutation snapshots;
7. plaintext-on-TLS handshake rejection with exact no-mutation snapshots;
8. certificate-valid but membership-unmapped rejection;
9. full loopback TCP accept, mutual TLS, SPKI-to-actor resolution, canonical
   operation claim, bounded request, durable evidence/effect publication,
   terminal receipt, sender settlement, replica-digest convergence, one unique
   published effect, and close-notify attempt;
10. generic socket policy distinction between lifetime, `O_NONBLOCK`, and
    `FD_CLOEXEC`;
11. already-expired poll without protocol progress;
12. advisory readability and writability; and
13. peer hangup reported as readiness and classified only by the subsequent
    `recv`.

The final revision evidence records exact compiler, sanitizer, stress, CTest,
and source-audit counts. The lexical audits inventory reviewed shape only; they
are not semantic proof.

## Online protocol review

The implementation was checked against current primary documentation:

- OpenSSL 3.5 `SSL_accept` nonblocking WANT behavior:
  <https://docs.openssl.org/3.5/man3/SSL_accept/>
- OpenSSL 3.5 `SSL_get_error` same-thread, no-intervening-call, empty-error-queue
  contract:
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>
- OpenSSL 3.5 `SSL_shutdown` return-zero and close-notify semantics:
  <https://docs.openssl.org/3.5/man3/SSL_shutdown/>
- Linux `accept4`, atomic child flags, pending network-error retry guidance, and
  noninheritance of `O_NONBLOCK`:
  <https://man7.org/linux/man-pages/man2/accept.2.html>
- Linux/POSIX `poll`, advisory error/hangup bits, timeout rounding, `EINTR`, and
  portable `EAGAIN` guidance:
  <https://man7.org/linux/man-pages/man2/poll.2.html>

These manuals constrain the implementation. They do not prove OpenSSL or kernel
internals, descriptor-mutation serialization, membership correctness, fair
scheduling, durable effects, anonymity, or package provenance.

## Remaining production gaps

Rev0889 is a composition milestone, not a service release. The following remain
missing or deliberately outside this owner:

- a long-running accept loop and daemon lifecycle;
- bounded concurrent-session and handshake ownership;
- per-source and per-member rate limits;
- overload admission, fairness, cancellation, and graceful drain;
- persistent enrollment, membership epochs, revocation, recovery, and key
  rotation;
- certificate-chain/revocation policy owned by an AnonSync configuration model;
- peer-address and transport-metadata privacy;
- structured operational telemetry that cannot leak sensitive path/payload
  material;
- resumption policy (tickets remain disabled);
- a client-side connect/handshake owner with symmetric absolute cutpoints;
- multi-operation sessions or multiplexing;
- end-to-end crash injection around accept, handshake, request, publication,
  receipt, shutdown, and daemon restart; and
- receiver payload fairness and garbage collection, audited separately in
  `RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md`.

The next service milestone should build a small listener scheduler around this
one-shot owner without weakening its cutpoints or letting scheduling summaries
become durable authority.
