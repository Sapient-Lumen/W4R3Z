# TLS record-I/O policy authority audit — rev0887

## Finding

AnonSync's authenticated TLS channel bound the peer certificate key, exact actor
epoch, TLS 1.3 profile, ALPN, exporter binding, retained read/write BIO objects,
directional Linux socket lifetimes, process incarnation, thread incarnation,
and one exclusive record continuation. Those proofs still did not bind several
application-mutable properties stored directly on the live `SSL*`.

That omission was material. A caller retaining the raw OpenSSL handle could
change option, mode, read-ahead, quiet-shutdown, peer-verification, or shutdown
state after authentication without changing the peer certificate, exporter,
BIO pointers, descriptor numbers, or socket cookies. The old capability could
therefore authorize later record progress under semantics different from the
ones reviewed at authentication.

The most dangerous case was `SSL_OP_IGNORE_UNEXPECTED_EOF`. OpenSSL documents
that this option treats an unexpected transport EOF as though the peer sent a
TLS `close_notify`. AnonSync's framed reader deliberately distinguishes clean
pre-frame peer closure from truncation. Enabling that option after
authentication could launder an abrupt socket close into the reader's clean
`PeerClosed` terminal state.

Other mutable switches crossed different authority boundaries:

- `SSL_set_shutdown` can mark sent or received shutdown state without the
  corresponding protocol exchange;
- quiet shutdown allows closure without transmitting or requiring
  `close_notify`;
- clearing `SSL_MODE_AUTO_RETRY` can expose WANT-readiness while OpenSSL still
  has processable protocol data, changing what the event loop's socket target
  means;
- `SSL_MODE_ASYNC` introduces asynchronous-engine readiness that the current
  socket-only continuation owner does not represent;
- read-ahead expands hidden OpenSSL progress beyond one bounded application read
  frontier; and
- changing `SSL_VERIFY_PEER` after authentication contradicts the membership
  capability even when the already-completed certificate result remains cached.

This was not a cryptographic break. It was an authority-composition error: one
capability proved identity and transport while silently borrowing mutable I/O
semantics from an unbound live object.

## Authority invariant

Rev0887 establishes the following invariant:

> An authenticated TLS channel owns one exact, safe record-I/O policy together
> with its peer, exporter, BIO, and socket-lifetime evidence. The policy binds
> the complete OpenSSL option mask, mode mask, read-ahead setting,
> quiet-shutdown setting, peer-verification mode, and zero shutdown state.
> Every ordinary authority use, fresh record step, pending WANT retry, and
> readiness-target disclosure must observe exact equality before progressing.
> Any contradiction poisons the byte stream. Abrupt transport EOF must remain
> distinguishable from authenticated `close_notify`.

Exact equality is deliberate. An option or mode that appears independently
benign is still a different post-authentication execution contract. Future code
must explicitly mint a new capability rather than deciding ad hoc that a
mutation is harmless.

## Primary OpenSSL constraints

The implementation and failure model were checked against the OpenSSL 3.5
manuals on 2026-07-22 America/New_York:

- The options manual defines `SSL_OP_IGNORE_UNEXPECTED_EOF` and warns that it
  makes unexpected EOF appear as clean shutdown. It is appropriate only when an
  application protocol independently detects truncation. AnonSync's strict TLS
  frame reader must preserve its own close/truncation frontier:
  <https://docs.openssl.org/3.5/man3/SSL_CTX_set_options/>
- The mode manual defines `SSL_MODE_AUTO_RETRY` and `SSL_MODE_ASYNC`. With
  automatic retry disabled, a read can return WANT even when the transport BIO
  is not the complete readiness authority; asynchronous mode adds a distinct
  wait mechanism:
  <https://docs.openssl.org/3.5/man3/SSL_CTX_set_mode/>
- `SSL_set_shutdown` directly changes the sent/received shutdown bitmask. The
  manual states that setting a bit can avoid sending the corresponding close
  alert:
  <https://docs.openssl.org/3.5/man3/SSL_set_shutdown/>
- Quiet shutdown marks both directions shut down without exchanging
  `close_notify`, and the manual explicitly notes that this violates the TLS
  standard:
  <https://docs.openssl.org/3.5/man3/SSL_CTX_set_quiet_shutdown/>
- `SSL_read_ex` documents the relationship among processed protocol records,
  application data, AUTO_RETRY, and WANT results:
  <https://docs.openssl.org/3.5/man3/SSL_read/>
- `SSL_get_error` must classify the immediately preceding I/O result in the same
  thread. Rev0887 does not place a policy getter between `SSL_read_ex` or
  `SSL_write_ex` and `SSL_get_error`:
  <https://docs.openssl.org/3.5/man3/SSL_get_error/>

These manuals constrain the design. They do not prove the C++ implementation,
thread safety, absence of memory corruption, end-to-end delivery, or anonymity.

## C++ implementation and refactor

### Separate policy authority leaf

The first implementation placed policy capture and reproof helpers inside
`sync_replica_tls_transport.cpp`, which was already responsible for handshake
profile, certificate/SPKI checks, exporter derivation, BIO/socket anchoring,
record framing, continuation ownership, poisoning, and compatibility wrappers.
Leaving another authority family there would make future review increasingly
lexical and rebuild-heavy.

Rev0887 extracts the policy into:

- `src/sync_replica_tls_io_policy.hpp`; and
- `src/sync_replica_tls_io_policy.cpp`.

CMake builds these files as the narrow
`anonsync_sync_replica_tls_io_policy` library. The transport adapter consumes
that leaf privately. A separate executable tests the leaf without requiring the
large delivery-service and SQLite dependency chain. This is semantic
modularity: the target owns one invariant and one OpenSSL surface, rather than
being a link-time partition with mixed authority.

### Context normalization

`configure_sync_replica_tls_io_policy_or_throw` normalizes context defaults for
subsequently created SSL objects:

- clear `SSL_OP_IGNORE_UNEXPECTED_EOF`;
- set `SSL_MODE_AUTO_RETRY`;
- clear `SSL_MODE_ASYNC`;
- disable read-ahead; and
- disable quiet shutdown.

It reads the context values back and rejects a profile it cannot establish.
Peer verification remains configured by the transport's client/server profile,
because server and client verification flags differ.

Context normalization is not treated as final authority. OpenSSL permits
per-SSL overrides after `SSL_new`, so authentication captures and validates the
actual live object.

### Exact authentication-time policy

`SyncReplicaTlsIoPolicy` is a small value containing:

1. the complete option mask;
2. the complete mode mask;
3. read-ahead;
4. quiet shutdown;
5. verification mode; and
6. shutdown state.

Capture requires strict unexpected-EOF behavior, AUTO_RETRY, no asynchronous
engine mode, no read-ahead, no quiet shutdown, peer verification enabled, and a
zero shutdown state. Authentication captures the policy beside the retained
transport anchor before SPKI/exporter derivation, then re-proves both after
those derivations and before publishing the shared authenticated state. The
state constructor repeats the proof before taking its retained `SSL*`
reference.

### Live authority and retry frontiers

Ordinary delivery-service authority and fresh record I/O now reprove in this
order:

1. exact BIO and socket-lifetime anchor;
2. exact record-I/O policy; and
3. peer SPKI, TLS profile, and exporter binding.

A pending WANT retry deliberately does not invoke unrelated certificate or
exporter operations before retrying the exact OpenSSL call. It nevertheless
reproves the exact BIO/socket anchor, current nonblocking policy where required,
and the exact record-I/O policy. Readiness-target disclosure performs the same
transport and record-policy checks before returning an advisory descriptor and
direction.

Policy failure poisons the shared TLS state. The caller cannot remove the
mutation and reuse the old capability after the contradiction has been
observed.

## Failure matrix

| Mutation or observation | Required result |
|---|---|
| Context starts with unexpected-EOF ignore enabled | Strict profile clears it |
| Context starts without AUTO_RETRY | Strict profile restores it |
| Context starts with ASYNC, read-ahead, or quiet shutdown | Strict profile removes it |
| Unsafe per-SSL option or mode before authentication | Authentication rejects |
| Nonzero per-SSL shutdown state before authentication | Authentication rejects |
| Any option/mode/read-ahead/quiet/verify/shutdown mutation after authentication | Next authority frontier rejects and poisons |
| Mutation while a WANT retry is pending | No OpenSSL retry; reject and poison |
| Mutation before readiness-target lookup | No descriptor disclosure; reject and poison |
| Abrupt socket close without `close_notify` | TLS error/truncation, never clean `PeerClosed` |
| Unchanged exact policy | Reproof and record progress continue |

## Runtime evidence

The focused leaf test covers context normalization, safe capture, unchanged
reproof, every unsafe capture class, every exact post-capture mutation class,
and null-handle fail-closed behavior.

The real TLS 1.3 integration test additionally covers authentication rejection,
post-authentication poisoning before bytes, pending-WANT target and retry
frontiers, verification-mode mutation, forged shutdown state, and an abrupt
socket close that must not become clean peer closure. The existing matrix still
covers peer pinning, exporter binding, BIO replacement, in-place descriptor
mutation, socket ABA, nonblocking policy, stable WANT arguments, bounded steps,
duplex reservation, process/thread affinity, framing, and file dispatch.

`tools/audit_sync_tls_io_policy.py` is intentionally only a source-shape and
release-inventory audit. It cannot prove OpenSSL behavior, operation ordering at
runtime, race freedom, or delivery semantics.

## Rejected alternatives

### Rely only on context configuration

Rejected. Per-SSL setters remain available after object creation and after
handshake. A context default is not a live capability.

### Check only known-dangerous bits

Rejected for post-authentication use. That would let an unreviewed future option
or apparently benign mode change the execution contract while retaining old
authority. Capture enforces the known safe subset; live reproof requires exact
mask equality.

### Revalidate only before fresh I/O

Rejected. A pending WANT operation is still an owned OpenSSL continuation, and
the event loop can otherwise disclose a stale target or retry under changed
semantics.

### Treat unexpected EOF as clean closure because the frame has a length prefix

Rejected. A length prefix detects incomplete application frames only after the
reader has observed enough framing state. Clean pre-frame closure is a distinct
protocol terminal, so laundering an abrupt close into `PeerClosed` still changes
observable authority and can hide truncation between records.

### Claim exclusive raw-SSL ownership

Rejected as a current claim. The authenticated state retains an OpenSSL
reference but the API still accepts a caller-owned raw `SSL*`, and existing
callers may retain aliases. Rev0887 detects observable mutation and fail-closes;
it cannot detect a mutation that is restored before every observation.

## Remaining gaps and next useful work

Rev0887 does **not** claim:

- exclusive ownership of the raw `SSL*` or its BIOs;
- detection of transient mutate-and-restore activity;
- safe concurrent access by another thread or library component;
- hidden transport identity behind arbitrary custom/filter BIOs;
- a production accept/connect/event-loop owner;
- receiver durable admission, payload publication, terminal effect receipt, or
  sender settlement;
- exactly-once remote effects; or
- anonymity, unlinkability, traffic-analysis resistance, or metadata privacy.

The long-term correction is to stop publishing or retaining a generally mutable
raw SSL alias after authentication. One process/thread-bound connection owner
should create, handshake, authenticate, drive, close, and finally free the
OpenSSL object. The most valuable product slice remains the symmetric receiver
composition: authenticated frame decode, canonical request verification,
durable SQLite admission, bounded payload/effect ownership, atomic visible
publication, authenticated terminal receipt, and exact sender settlement.
