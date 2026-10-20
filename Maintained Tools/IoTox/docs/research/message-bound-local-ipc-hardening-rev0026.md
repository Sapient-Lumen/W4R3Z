# Message-bound local IPC hardening — rev0026

**Research date:** 2026-08-18 America/New_York
**Applied revision:** rev0026
**Decision:** ADR 0076

## Question

Can IoTox make its local Ratox control and terminal streams resistant to descriptor handoff,
fork-inherited authority, ancillary descriptor injection, silent administrative clients, and socket
pathname replacement without changing the wire encodings or pretending that same-UID IPC is a
complete hostile-user boundary?

## Primary-source findings

### `SO_PEERCRED` is connection-time evidence

Linux `unix(7)` states that `SO_PEERCRED` returns credentials in effect at connect, listen, or
socketpair creation time. That is useful for authenticating an endpoint, but it is intentionally not
an assertion about the process that sends every later record. A connected file descriptor can be
inherited across `fork(2)` or transferred with `SCM_RIGHTS` while the stored peer tuple remains
unchanged.

### `SO_PASSCRED` is message-time evidence

Enabling `SO_PASSCRED` causes the kernel to include `SCM_CREDENTIALS` for the sending process in each
subsequently received message. The default record contains the sender PID, real UID, and real GID;
explicitly supplied credentials are kernel-validated. Comparing that record with `SO_PEERCRED`
therefore detects a later sender that possesses the connection but is not the process that opened it.

The option is enabled before bind/listen on server sockets and before connect on clients. Accepted
sockets verify inheritance before consuming data because a seqpacket can already be queued when
`accept(2)` returns.

### `SCM_PIDFD` can carry a non-reusable sender handle

Linux 6.5 added `SO_PASSPIDFD`/`SCM_PIDFD`. When both the userspace headers and running kernel support
it, each record carries a close-on-exec pidfd for the sender. IoTox treats successful option enablement
as a requirement for every subsequent record on that socket. Unsupported-option errors fall back to
mandatory credentials rather than failing supported older kernels.

For the long-lived terminal controller, the first record's pidfd is retained and polled. On kernels
without pidfd delivery, `pidfd_open(2)` is attempted for the already authenticated PID. A readable
pidfd means the process has exited; the slot is released even if another process holds the socket.
This avoids PID-reuse ambiguity and does not depend on receiving EOF from every duplicated descriptor.

### Ancillary truncation destroys the proof

`recvmsg(2)` reports `MSG_CTRUNC` when control data is discarded. A parser cannot safely accept the
payload after losing unknown credentials, pidfds, or rights, so IoTox rejects the record. The parser
also rejects payload truncation, malformed lengths, duplicate identity records, unknown ancillary
types, and mismatches between configured requirements and actual records.

`MSG_CMSG_CLOEXEC` prevents a received descriptor from crossing a later exec. `SCM_RIGHTS` is not a
feature of either IoTox local protocol, so all delivered rights are closed immediately and the record
is rejected. Excess rights discarded by the kernel are never exposed to IoTox code.

## Constructed boundary

One internal `seqpacket_security` module now owns:

- close-on-exec descriptor RAII;
- `SO_PASSCRED` and optional `SO_PASSPIDFD` enablement;
- inherited-option verification;
- connection-time peer credential acquisition;
- one fixed-ceiling `recvmsg` parser;
- unconditional `SCM_RIGHTS` closure;
- exact PID/UID/GID comparison;
- `pidfd_open` fallback; and
- nonblocking pidfd exit inspection.

Both `control.sock` and `terminal.sock` consume that module in both directions. Protocol decoders see
only a bounded payload after the entire ancillary contract has passed.

### Terminal ownership

```text
connect-time SO_PEERCRED
  + first-record SCM_CREDENTIALS exact match
  + optional first-record SCM_PIDFD (or pidfd_open fallback)
  -> bind controller process
  -> require exact credentials on every later record
  -> poll controller pidfd beside socket and wake event
  -> release slot on process exit, protocol violation, disconnect, or stop
```

Contender stream-ID peeks are authenticated too. A rejected contender cannot smuggle a descriptor or
cause a packet to be dispatched while the active controller owns the slot.

### Administrative control ownership

Each control connection has one complete-record lease. The worker polls the client and stop event;
timeout produces a typed error and closes the connection. Requests are authenticated at record time,
and responses are authenticated by the client at record time.

The filesystem endpoint now uses the same exact-identity discipline as the terminal endpoint:
owner-private real parent, active listener probe, stale-inode recheck, exact bound-inode cleanup, and
pre/post-connect inode comparison. Shutdown cannot unlink a replacement pathname.

## Executable abuse cases

The direct owned registry grows from 303 to 313 checks. New cases cover:

1. a child sending a control request through its parent's connected descriptor;
2. a child sending a terminal record through its parent's active controller descriptor;
3. a child sending a forged control response through an inherited server descriptor;
4. `SCM_RIGHTS` injection into a control request;
5. `SCM_RIGHTS` injection into a terminal record;
6. `SCM_RIGHTS` injection into a terminal response;
7. controller-process exit while a passed socket remains open elsewhere;
8. a silent administrative connection followed by a legitimate successor;
9. a second server attempting to replace an active control socket; and
10. preservation of a different socket inode installed before original-server shutdown.

Each rights test closes the sender's original write descriptor and observes EOF only after the IoTox
receiver has closed the injected copy. Handler counters prove rejected records are never dispatched.

## Resource and compatibility bounds

- payload ceilings remain the protocol constants plus one truncation-detection byte;
- ancillary storage is fixed at 4096 bytes per receive;
- every received descriptor is RAII-owned or synchronously closed;
- the administrative request lease is positive and at most 60 seconds;
- listener backlogs retain existing finite caps;
- pidfd delivery is runtime-probed and optional, while `SO_PASSCRED` is mandatory; and
- no on-wire protocol version or field changes.

## Nonclaims

This construction does not make a same-UID process a cryptographically isolated principal. A process
allowed by policy may still open a new connection and be authenticated as itself. Root, kernel
compromise, ptrace-equivalent authority, deliberate daemon descriptor export, and arbitrary mutation
by an equivalent owner remain outside the claimed boundary.

The single control worker is now finitely leased but is not a general multi-client fairness scheduler.
R7 physical-host evidence, independent security review, and operational R8 qualification remain open.

## Sources rechecked online

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/recv.2.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://github.com/torvalds/linux/blob/master/include/net/sock.h
https://people.kernel.org/kuba/netdev-in-2023
```

These sources define Linux interfaces and do not audit IoTox. The executable evidence supports only
the bounded behavior described above.
