# ADR 0076 — Bind local seqpacket records to kernel sender evidence

- Status: accepted
- Date: 2026-08-18
- Revision: rev0026
- Supersedes: no earlier ADR; strengthens ADRs 0066, 0067, and 0068

## Context

The Ratox administrative `control.sock` and single-controller `terminal.sock` are owner-private
filesystem `AF_UNIX/SOCK_SEQPACKET` endpoints. Before this decision, each server authenticated the
peer once with `SO_PEERCRED` after `accept(2)`. That proves the process credentials captured when the
connection was established, but it does not prove which process sent a later record through the open
file description. A process can inherit or receive a connected descriptor after `fork(2)` or
`SCM_RIGHTS`, while `SO_PEERCRED` continues to describe the original peer.

The same asymmetry existed in the reverse direction: local clients verified the server at connect
time but did not authenticate each response record. Both receive paths also accepted ancillary data
even though neither protocol transfers descriptors or any other control message.

The control server additionally processed one accepted connection synchronously with no complete-
request deadline. A silent same-UID client could reserve that worker indefinitely. Its stale-socket
cleanup and client pathname checks were weaker than the terminal endpoint's exact inode ownership
contract.

Linux exposes the evidence needed to close these gaps:

- `SO_PASSCRED` asks the kernel to attach one `SCM_CREDENTIALS` record containing the sender's PID,
  real UID, and real GID to every subsequently received message;
- Linux 6.5 and suitable build headers optionally expose `SO_PASSPIDFD`/`SCM_PIDFD`, delivering a
  pollable pidfd for the actual sender;
- `MSG_CMSG_CLOEXEC` seals any installed descriptor at receipt; and
- `MSG_CTRUNC` identifies ancillary truncation, which must be treated as loss of security evidence.

## Decision

### Authenticate every record in both directions

Every IoTox local seqpacket listener and every IoTox local seqpacket client enables `SO_PASSCRED`
before records can be queued. When the build headers and running kernel support it, the socket also
enables `SO_PASSPIDFD`; otherwise credentials remain mandatory and `pidfd_open(2)` is the terminal
owner-liveness fallback.

Accepted sockets must prove that the listener options were inherited. This check occurs before any
queued record is consumed because a client may send before the server returns from `accept(2)`.

For each request, terminal record, control response, and terminal response:

1. receive with `recvmsg(2)` and `MSG_CMSG_CLOEXEC` into a fixed ancillary ceiling;
2. require exactly one well-formed `SCM_CREDENTIALS` record;
3. require exactly one `SCM_PIDFD` when pidfd delivery was successfully enabled;
4. compare the record credentials exactly with the connection-time `SO_PEERCRED` tuple; and
5. reject the record without dispatch or decode if any check fails.

The kernel record sender is the identity delivered to local request/terminal handlers. A fork child
or descriptor recipient cannot act as the process that originally connected merely by possessing the
same open socket description.

### Pin the terminal controller process lifetime

The first authenticated terminal record binds the controller PID/UID/GID. The server retains the
kernel-supplied sender pidfd when available, otherwise opens a pidfd for that exact authenticated PID.
The pidfd joins the worker's poll set. Process exit releases the single controller slot even if a
fork child or descriptor recipient continues to hold the socket open.

Every subsequent terminal record must still carry the exact bound credentials. The pidfd is checked
again before dispatch. This is process-lifetime ownership, not merely socket-lifetime ownership.

### Reject all ancillary capabilities

Neither local protocol defines descriptor transfer. Every `SCM_RIGHTS` descriptor is therefore
closed immediately and the complete record is rejected. Unknown control-message levels/types,
duplicate credentials or pidfds, malformed lengths, unexpected credentials on an unauthenticated
receive path, payload truncation, and `MSG_CTRUNC` all fail closed.

The same parser is used by clients, so a compromised or accidentally forked server-side descriptor
cannot inject file descriptors into the CLI. No received descriptor is exposed to protocol decoders
or handlers.

### Bound and own the administrative endpoint

`ControlServer::Config::request_timeout` is a positive complete-record lease capped at 60 seconds. A
silent connection is closed after the lease instead of monopolizing the worker forever, and the wake
descriptor interrupts that wait during shutdown.

The administrative endpoint now also:

- requires an absolute pathname beneath a real owner-private directory;
- rejects group/other-accessible modes;
- probes an existing owned socket and refuses to unlink an active listener;
- rechecks device/inode before removing a stale socket;
- records the device/inode created by `bind(2)` and unlinks only that exact socket at cleanup;
- preserves a replacement socket installed at the same pathname; and
- has clients verify owner-private type/mode and the same device/inode before and after connect.

Server stop is callback-safe, wake/join operations are bounded by explicit ownership, and thread
creation failure performs exact socket cleanup.

## Consequences

- Local authority is bound to the kernel-observed sender of each record, not only to the process that
  established the connection.
- Passing or inheriting a terminal controller socket no longer extends controller ownership beyond
  the authenticated process lifetime.
- Ancillary descriptors are an explicit protocol violation and are closed before rejection.
- Administrative silent-client denial changes from unbounded to a configured finite lease.
- Active and replacement socket inodes are not removed by a competing or stopping server instance.
- Linux 6.5+ can carry pidfds directly. Older supported Linux kernels retain mandatory per-record
  credentials and use `pidfd_open` only for terminal-owner liveness when available.
- The implementation remains Linux-specific; it does not claim portable credential semantics for
  non-Linux Unix-domain sockets.

## Nonclaims

rev0026 does not claim:

- isolation from root, kernel compromise, or an arbitrary process with equivalent daemon authority;
- that same-UID local processes cannot open their own new connection where policy permits it;
- multiplexed/fair service for an unlimited number of administrative clients;
- protection after the daemon intentionally exports a different authority-bearing interface;
- a cryptographic local transport, namespace boundary, or sandbox; or
- completion of independent R8 audit, public-network qualification, or production support.

## Executable evidence

The owned registry must prove:

- fork-inherited request and terminal records are rejected without handler dispatch;
- fork-inherited server responses are rejected by the client;
- request-side and response-side `SCM_RIGHTS` descriptors are closed and their records rejected;
- pidfd-observed controller exit releases a socket still held by another process;
- a silent control client expires and a successor is admitted;
- an active control listener cannot be unlinked by a second instance;
- a replacement control socket inode survives shutdown of the original server;
- unsafe paths, modes, and request leases fail before use; and
- all prior authority, restart, PTY, confinement, cgroup, and R7 evidence remains green.

## References

- `docs/research/message-bound-local-ipc-hardening-rev0026.md`
- Linux `unix(7)`: <https://man7.org/linux/man-pages/man7/unix.7.html>
- Linux `recvmsg(2)`: <https://man7.org/linux/man-pages/man2/recv.2.html>
- Linux `pidfd_open(2)`: <https://man7.org/linux/man-pages/man2/pidfd_open.2.html>
- Linux socket implementation (`SO_PASSPIDFD` state):
  <https://github.com/torvalds/linux/blob/master/include/net/sock.h>
- Linux networking 2023 summary (`SCM_PIDFD` introduction):
  <https://people.kernel.org/kuba/netdev-in-2023>
