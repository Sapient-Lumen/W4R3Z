# Process-pinned local IPC lifetimes — rev0027

**Research date:** 2026-08-18
**Applied revision:** rev0027
**Version:** 0.27.0
**Scope:** Linux connection-process identity, pidfd readiness, inherited Unix-domain descriptors, and
bounded IoTox control/terminal lifetime behavior

## Question

Can IoTox close the interval between connection-time credentials and the first authenticated record,
and can a client distinguish a live server from an accepted socket deliberately retained after server
exit, without replacing the rev0026 message-bound identity contract or making Linux 6.5 mandatory?

## Kernel findings

### `SO_PEERPIDFD` identifies the connected peer with a process handle

Linux's UAPI socket header assigns `SO_PASSPIDFD` and `SO_PEERPIDFD` as adjacent socket options. The
Linux networking maintainer's 2023 review records both `SCM_PIDFD` and `SO_PEERPIDFD` as Linux 6.5
additions for Unix-socket credential passing using pidfds instead of integer PIDs.

For IoTox this distinction matters: `SO_PEERCRED` supplies a numeric PID, UID, and GID captured for the
connection, while `SO_PEERPIDFD` supplies a descriptor referring to the associated process. Retaining
that descriptor avoids reconstructing process identity through a numeric PID that may later be reused.

### pidfds are readiness objects

The `pidfd_open(2)` manual documents that a pidfd can be monitored with `poll(2)`, `select(2)`, or
`epoll(7)`. Process termination makes it readable; reaping can produce hangup. A pidfd is therefore a
lifetime signal that can share one bounded readiness loop with a Unix socket and wake descriptor.

### readiness ordering must preserve queued records

`poll(2)` reports all conditions observed in a poll cycle. A Unix socket may report `POLLIN` together
with hangup, and a pidfd may become readable in the same cycle. A complete `SOCK_SEQPACKET` record sent
immediately before process exit remains a complete ordered record. IoTox therefore gives socket
readability precedence over peer-exit removal for the one-shot administrative request/response paths,
then authenticates the record normally. Terminal commands retain the rev0026 rule that the bound
controller process must still be live immediately before dispatch.

### compatibility remains explicit

Build headers may not define `SO_PEERPIDFD`, and a running kernel may reject the option even when the
constant is available. `ENOPROTOOPT`, `EINVAL`, and equivalent unsupported-option results are treated
as an empty optional capability. `ENODATA` (no attached peer process) and `ESRCH` (peer no longer
available) fail as unavailable identity. Other errors, malformed descriptor lengths, or negative
descriptors are not silently ignored.

## Applied control-server design

Each accepted control connection now carries:

```text
accepted nonblocking seqpacket socket
+ exact connection PID/UID/GID tuple
+ optional SO_PEERPIDFD handle
+ independent absolute request deadline
+ removal state
```

The worker's bounded poll vector contains listener, wake event, every client socket, and every present
peer pidfd. Socket and pidfd indices are retained separately so optional support does not make the
mapping ambiguous. Existing maximum-pending, per-process, accept-refill, and requests-per-cycle bounds
continue to cap memory, descriptors, and work.

A readable request is consumed before a simultaneous pidfd exit. A pidfd exit without readable data
removes the pending client immediately. This closes the case where a child connects, passes the socket
to a parent, and exits while the parent tries to preserve the lease.

Per-process admission accounting now compares the complete connection credential tuple rather than a
PID alone. This does not create cryptographic principals, but avoids grouping unlike credentials
solely by one integer field.

## Applied control-client design

After the client verifies owner-private pathname state, connects, obtains server credentials, pins the
server connection process when supported, and rechecks the exact socket inode, it sends the request and
waits on:

```text
control response socket
+ optional server connection pidfd
+ one absolute response deadline
```

A readable response wins over simultaneous server exit. Server exit without a readable response
returns `unavailable`; socket closure without a response also returns `unavailable`; deadline expiry
returns `timeout`. The received response still must carry exact per-record credentials and optional
sender pidfd matching the connection-time server credentials.

The adversarial oracle starts a server in a child process, arranges for a different process to retain
the accepted server endpoint, and then exits the server process. The client must fail promptly rather
than consume its 2.5-second timeout.

## Applied terminal design

The terminal server obtains a connection pidfd at initial accept and installs it as the owner-liveness
poll entry before the first record. This closes the pre-`OPEN` interval: if the exact connector exits
while a second process retains the connected socket, the active slot is released immediately rather
than waiting for the complete open lease.

The first authenticated record still performs the rev0026 sender binding. Its delivered `SCM_PIDFD`,
or the checked `pidfd_open` fallback when sender pidfd delivery is unavailable, remains the post-OPEN
controller lifetime handle. Subsequent records must match connection and bound sender credentials.
The connection pidfd therefore strengthens, rather than replaces, message-bound authority.

The adversarial oracle forks a connector, passes its still-silent terminal descriptor to the parent,
waits until the server has admitted it, and exits the connector. The server must release the slot well
before the two-second open lease and admit a normal successor without dispatching the silent socket.

## Resource envelope

With defaults on a supporting kernel:

```text
control server: at most 32 client sockets + 32 peer pidfds + listener + wake
control client: one socket + one transient server pidfd
terminal server: one active socket + one active connection/sender pidfd
terminal contenders: unchanged; at most 16 sockets, no added connection pidfds
```

All descriptors are close-on-exec and RAII-owned. Poll storage is reserved from validated bounds before
the service loop. Unsupported kernels retain the smaller descriptor envelope and the finite lease
fallback.

## What the construction proves

The implemented and directly exercised claims are:

- exact connection-process exit can release a retained silent control descriptor;
- exact server-process exit can terminate a retained control response wait;
- exact connection-process exit can release a retained silent pre-`OPEN` terminal descriptor;
- queued complete administrative request/response records retain precedence over simultaneous exit
  readiness while terminal dispatch still requires a live controller;
- all three paths remain bounded by existing leases and work quotas; and
- no protocol wire format or remote authority meaning changes.

## What it does not prove

This work does not make a Unix socket a cryptographic identity, prevent a same-UID process from opening
its own new connection, isolate local traffic by namespace/cgroup, preempt blocking callbacks, or
qualify every supported production kernel. Runtime absence of `SO_PEERPIDFD` is an explicitly weaker
but still bounded compatibility path.

## Primary sources rechecked online

- Linux UAPI socket constants:
  https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/socket.h
- Linux generic socket implementation of `SO_PEERPIDFD`:
  https://github.com/torvalds/linux/blob/master/net/core/sock.c
- Linux networking 2023 summary:
  https://people.kernel.org/kuba/netdev-in-2023
- `pidfd_open(2)`:
  https://man7.org/linux/man-pages/man2/pidfd_open.2.html
- `poll(2)`:
  https://man7.org/linux/man-pages/man2/poll.2.html

The sources establish interface semantics. IoTox scheduling, error precedence, and resource bounds are
project decisions backed by source review and executable tests, not claims made by those sources.
