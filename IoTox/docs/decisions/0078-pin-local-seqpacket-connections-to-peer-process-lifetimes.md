# ADR 0078: Pin local seqpacket connections to peer process lifetimes

- Status: accepted and implemented
- Date: 2026-08-18
- Revision: rev0027
- Extends: ADR 0076 message-bound sender evidence and ADR 0077 bounded multiplexed admission

## Context

ADRs 0076 and 0077 bind every consumed local `SOCK_SEQPACKET` record to kernel sender credentials,
optionally retain a sender pidfd, and keep silent or competing connections inside finite bounded
leases. Those controls distinguish the process that sends a record from a process that merely owns a
copy of the connected file description.

A remaining pre-record and response-wait gap existed. `SO_PEERCRED` identifies the process that
established a Unix-domain connection, but exposes a numeric PID. If that process exits after passing
or inheriting the connected descriptor, the surviving socket remains open. Before this decision:

- a silent accepted control connection could retain one bounded pending slot until its request lease;
- a silent active terminal connection could retain the sole pre-`OPEN` controller slot until its open
  lease; and
- a control server could exit after arranging for another process to retain the accepted descriptor,
  leaving the client to wait for the complete response timeout.

Opening a pidfd later from the numeric `SO_PEERCRED` PID introduces an avoidable process-exit and PID-
reuse window. Linux 6.5 added `SO_PEERPIDFD`, which returns a pidfd for the process associated with the
connected peer. A pidfd is pollable: process exit makes it readable, and reap produces a hangup event.
This supplies an exact connection-time process handle without reconstructing identity from a reusable
integer PID.

## Decision

### Runtime-probed connection pidfds

Immediately after connection-time credential verification, IoTox SHALL call
`getsockopt(SOL_SOCKET, SO_PEERPIDFD)` on:

1. every admitted administrative control connection;
2. every accepted active terminal-controller connection; and
3. every connected administrative client socket, to pin the responding server.

A successful descriptor SHALL be validated, marked close-on-exec, owned by an RAII wrapper, and
closed on every exit path. `ENODATA` means the socket has no attached peer process identity and
`ESRCH` means the peer exited before identity could be pinned; both fail that admission or request as
unavailable. Malformed lengths or negative descriptors fail closed.

`ENOPROTOOPT`, `EINVAL`, and equivalent unsupported-option errors are a compatibility result, not a
startup failure. Kernels or build headers without `SO_PEERPIDFD` retain mandatory per-record
`SCM_CREDENTIALS`, optional `SCM_PIDFD`, exact connection credentials, and finite leases. The product
must not fabricate a connection pidfd by reopening the numeric PID in this compatibility path.

### Control-server admission lifetime

Every pending control client SHALL retain its connection pidfd when available. The readiness loop
polls each socket and pidfd together under the existing bounded descriptor, accept, and request-work
limits.

- A readable complete request is authenticated and handled before process-exit removal when both
  socket and pidfd become ready in the same poll cycle.
- A process-exit event without a readable request removes the pending client immediately.
- A socket error or hangup without readable data removes it as before.
- The independent request deadline remains authoritative on kernels without connection pidfds and as
  an upper bound on supported kernels.

A descriptor recipient therefore cannot extend the original connector's pending admission lifetime.
Per-process quotas compare the complete connection credential tuple rather than only a numeric PID.

### Control-client server lifetime

After connect-time server credentials and socket-inode continuity are verified, the administrative
client SHALL poll its socket and the server connection pidfd against one absolute response deadline.

- Socket readability wins over simultaneous server-exit readiness, preserving a complete response
  queued immediately before exit.
- Server process exit without a readable response returns `unavailable` immediately.
- Socket close/error without a readable response returns `unavailable`.
- Deadline expiry remains `timeout`.

The eventual response still passes the ADR 0076 per-record credential and optional sender-pidfd check;
a connection pidfd does not replace message-bound identity.

### Terminal pre-OPEN lifetime

The active terminal worker SHALL initialize its owner-liveness poll entry from the accepted
connection pidfd before consuming the first record. If the connection process exits before a valid
`OPEN`, the server releases the active slot promptly even when another process retains the socket.

After the first authenticated record, existing ADR 0076 behavior remains in force: the record sender
credentials bind the controller and a delivered sender pidfd, or the existing `pidfd_open` fallback,
fences the post-`OPEN` process lifetime. Every later record must still match both the connection and
bound sender credentials.

Contender connections remain short-lived, globally bounded, per-process bounded, and nondispatched.
This decision does not add one pidfd per terminal contender.

## Consequences

### Positive

- Silent inherited or transferred control sockets no longer consume admission slots after the exact
  connector exits on supported kernels.
- A retained accepted descriptor cannot make a dead control server appear alive until the full client
  timeout.
- A silent inherited terminal socket cannot retain the sole pre-`OPEN` controller slot after its
  connector exits.
- No PID-reuse lookup is introduced for connection identity.
- Complete administrative request and response records already queued before peer exit retain
  deterministic precedence. Terminal commands retain ADR 0076's stronger live-controller-before-
  dispatch rule.
- Older kernels preserve the prior bounded fail-closed construction rather than losing service.

### Costs and tradeoffs

- Supported systems consume one additional pidfd per admitted control connection and one for the
  active terminal connection; administrative clients briefly consume one server pidfd.
- Poll vectors contain additional entries, still bounded by explicit configuration.
- Runtime behavior is stronger on kernels that expose `SO_PEERPIDFD`; the compatibility path relies on
  the existing leases and message-bound sender evidence.
- A same-UID process remains free to establish a new authorized-by-local-policy connection. Process
  lifetime is not application authority.

## Rejected alternatives

### Reopen `SO_PEERCRED.pid` with `pidfd_open`

Rejected for connection identity because the peer can exit and the numeric PID can be reused between
credential retrieval and pidfd acquisition. The existing terminal first-record fallback remains
acceptable because the sender credentials are observed on that exact record and the result is checked
before dispatch.

### Treat peer exit before queued administrative data

Rejected for one-shot administrative request/response paths because `poll(2)` can report socket
readability and pidfd readiness together. A complete control record already queued by the
authenticated peer is valid evidence and must not be discarded merely because the process exited
immediately afterward. Terminal commands remain governed by ADR 0076: the bound controller process
must still be live immediately before dispatch.

### Require Linux 6.5 at startup

Rejected for this revision. The previous construction already has finite leases, exact per-record
credentials, optional sender pidfds, and bounded work. `SO_PEERPIDFD` is a monotonic runtime
hardening layer, not a silent removal of the established compatibility floor.

## Executable evidence

The owned registry must prove on a supporting kernel that:

- four silent control leases expire concurrently rather than serially;
- the true global pending-control ceiling rejects excess admission and recovers;
- a control socket retained by another process is released when its exact connector exits;
- a control client returns promptly when the exact server exits while its accepted socket survives;
- a silent terminal socket retained by another process releases the pre-`OPEN` slot when its exact
  connector exits; and
- each release admits a normal successor without dispatching the silent connection.

Unsupported kernels skip only the connection-pidfd-specific assertions and retain all compatibility,
lease, message-bound credential, and ancillary-rejection tests.

## Nonclaims

rev0027 does not claim:

- authorization, confidentiality, or resource isolation among hostile same-UID processes;
- protection from root, kernel compromise, ptrace-equivalent authority, or a compromised daemon;
- starvation freedom against an unlimited coalition of distinct processes;
- callback preemption after a request is admitted;
- namespace or cgroup traffic accounting for local IPC; or
- target-fleet qualification or independent production security review.

## Primary sources rechecked online

- Linux UAPI socket options (`SO_PASSPIDFD` and `SO_PEERPIDFD`):
  https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/socket.h
- Linux generic socket `SO_PEERPIDFD` implementation and `ENODATA` result:
  https://github.com/torvalds/linux/blob/master/net/core/sock.c
- Linux networking 2023 summary recording the Linux 6.5 introduction:
  https://people.kernel.org/kuba/netdev-in-2023
- `pidfd_open(2)` polling semantics:
  https://man7.org/linux/man-pages/man2/pidfd_open.2.html
- `poll(2)` readiness, timeout, and simultaneous event semantics:
  https://man7.org/linux/man-pages/man2/poll.2.html

These sources define kernel interfaces. They do not audit IoTox or prove the scheduling properties of
this implementation.
