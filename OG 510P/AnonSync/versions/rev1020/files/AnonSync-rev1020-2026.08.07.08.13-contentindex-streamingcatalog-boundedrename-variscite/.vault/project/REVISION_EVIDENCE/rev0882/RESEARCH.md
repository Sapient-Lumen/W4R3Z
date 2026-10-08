# rev0882 primary-source research, inference, and speculation

Research was checked online on 2026-07-22. The implementation record uses
primary OpenSSL, SQLite, Linux/POSIX, and IETF sources.

## OpenSSL application-write semantics

- `SSL_write_ex()`:
  https://docs.openssl.org/3.5/man3/SSL_write/
  OpenSSL documents that success writes the requested application data to the
  SSL connection, while a nonblocking operation may return WANT_READ or
  WANT_WRITE. It also warns that data may have been partially processed and a
  retry must use the same arguments. This supports a move-only immutable
  continuation; it does not support reconstructing different bytes or treating
  WANT as no progress.
- SSL modes:
  https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/
  Partial-write and moving-buffer modes affect retry contracts. Rev0882 does
  not enable partial-write or moving-buffer behavior and never resumes WANT;
  the channel is poisoned instead.
- Descriptor/BIO setup:
  https://docs.openssl.org/3.5/man3/SSL_set_fd/
  OpenSSL associates socket BIOs with descriptors and inherits descriptor
  blocking behavior. The implementation still observes the live BIO method,
  descriptor, kernel socket type, and `O_NONBLOCK` rather than trusting setup
  history.

Applied inference: successful acceptance of the complete eight-byte prefix by
OpenSSL is a local stream cutpoint. It is not evidence that ciphertext reached
the peer kernel, that the peer TLS stack authenticated a complete record, or
that the receiver application admitted, persisted, or effected the request.
Therefore TLS write completion cannot settle the outbox.

## Linux/POSIX descriptor observation

- `fcntl(2)`:
  https://man7.org/linux/man-pages/man2/fcntl.2.html
  `F_GETFL` exposes file status flags, including `O_NONBLOCK`.
- `getsockopt(2)` / `SO_TYPE`:
  https://man7.org/linux/man-pages/man2/getsockopt.2.html
  A successful `SO_TYPE` observation identifies the kernel descriptor as a
  socket and reports its type.

Applied inference: descriptor visibility plus `O_NONBLOCK` is not enough for a
critical-section readiness proof because non-socket descriptors can carry that
flag. Requiring direct socket BIO methods and `SO_TYPE` narrows the accepted
composition to a topology the code can actually observe. It intentionally
rejects filtered/custom BIOs even when an underlying descriptor might exist.

## SQLite writer semantics

- Transactions:
  https://www.sqlite.org/lang_transaction.html
  `BEGIN IMMEDIATE` begins a write transaction immediately and can fail when
  another writer is active.
- Isolation:
  https://www.sqlite.org/isolation.html
  SQLite serializes writers and isolates separate connections.

Applied inference: the dispatch guard can prevent another connection from
committing a competing release, renewal, settlement, or claim replacement while
the exact claim/channel proof and fixed-size prefix operation run. SQLite does
not become atomic with OpenSSL, TCP, a receiver database, or a filesystem.
Holding the writer across a payload-sized operation would increase lock duration
without creating distributed atomicity.

## TLS record/application acknowledgement distinction

- TLS 1.3, RFC 8446:
  https://www.rfc-editor.org/rfc/rfc8446.html
  TLS authenticates and protects records between endpoints. Application state,
  provisioning, admission, and acknowledgement remain protocol concerns above
  the record layer.
- Channel bindings for TLS 1.3, RFC 9266:
  https://www.rfc-editor.org/rfc/rfc9266.html
  The `tls-exporter` binding can bind higher-layer evidence to the exact TLS
  session; it does not prove receiver application progress.

Applied inference: AnonSync should continue to bind peer actor, operation,
attempt, and receipt semantics above TLS. The exporter prevents a frame prepared
for one authenticated session from being silently treated as authority on
another, but only explicit receiver evidence can retire sender intent.

## Speculation and next experiments

A resumable sender should retain one immutable OpenSSL write operation under an
event-loop capability rather than poison on every WANT. The continuation would
need exact buffer identity, offset/progress owned by the same SSL/process/thread
capability, a monotonic transfer-age policy, and explicit cancellation. It must
never retain a SQLite writer while waiting for readiness.

There are two plausible durable designs:

1. Keep durable state at claim granularity and use receiver idempotency plus
   exact terminal receipts. Heartbeat the live attempt while one event-loop
   continuation owns it. This is smaller, but restart after partial transfer
   remains ambiguous and may duplicate bandwidth.
2. Add an explicit durable in-flight state binding claim ID, canonical frame
   digest, payload identity, transfer generation, and settlement frontier. This
   makes restart ambiguity inspectable, but body offsets are connection-local
   and cannot be resumed on a fresh TLS stream without a higher-level chunk
   protocol. Persisting raw socket/TLS progress would be false authority.

The likely useful hybrid is durable chunk identity and receiver chunk
idempotency, not durable TCP offsets. A fresh authenticated channel can resume
missing immutable chunks while the canonical operation and terminal effect
receipt remain unchanged.

Receiver composition should come before that expansion. A real loop can reveal
whether body backpressure, lease crossing, and duplicate transfer are frequent
enough to justify durable in-flight state. Crash injection should be exhaustive
at each evidence/effect frontier, and the full-history owner should remain a
differential oracle for every indexed optimization.

The privacy name remains ahead of implementation. TLS and pinned device keys
provide channel confidentiality/authentication, not anonymity, unlinkability,
endpoint hiding, or traffic-analysis resistance. Those properties require an
explicit adversary model, discovery/relay metadata analysis, padding or batching
policy, and key/membership lifecycle; they must not be inferred from encrypted
payloads.
