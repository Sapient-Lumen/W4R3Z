# Bounded local IPC admission — rev0027

**Reviewed:** 2026-08-18  
**Applied revision:** rev0027  
**Version:** 0.27.0  
**Decision:** ADR 0077  
**Scope:** owner-private Linux `AF_UNIX/SOCK_SEQPACKET` control and terminal admission

## Question

After rev0026 made every local record message-bound and process-evidenced, could a process that was
already allowed to reach the daemon user's private runtime directory still delay unrelated local
work merely by connecting and remaining silent?

Yes. The security checks were correct, but two scheduling shapes remained availability-sensitive:

```text
control:  accept A -> wait A's complete-record lease -> accept B
terminal: active stream -> listener readable -> accept contenders -> wait shared grace
```

The first shape imposed head-of-line blocking up to the complete-request lease. The second bounded
its total wait to one shared 20 ms grace, but still inserted that wait into the active controller
loop. Neither issue required a protocol change; both were local readiness/admission problems.

## Linux interface findings

### Record boundaries permit descriptor multiplexing

Linux `unix(7)` documents `SOCK_SEQPACKET` as connection-oriented, preserving message boundaries and
message order. IoTox already constrains each control exchange and each terminal packet to one bounded
record. Therefore a readable accepted descriptor can be consumed once with `recvmsg(MSG_DONTWAIT)`;
there is no partial application frame that requires a per-client reassembly state machine.

### Readiness is the nonblocking boundary

Linux `poll(2)` defines readiness as an operation that will not block. A timeout of zero returns
immediately, and a negative timeout waits indefinitely. That permits one worker to poll listener,
wake event, active client, owner pidfd, and bounded pending descriptors together, while independent
monotonic deadlines determine finite waits.

### Accepted sockets can be born hardened

Linux `accept(2)`/`accept4(2)` exposes `SOCK_NONBLOCK` and `SOCK_CLOEXEC` flags on the accepted socket.
IoTox uses both atomically. Admission errors and contender rejections use immediate nonblocking send
attempts; a peer that will not read does not receive a worker-time lease.

### Queue readiness is not application fairness

The kernel pending connection queue and `poll()` readiness report available work; they do not choose
IoTox's per-process quotas, request budgets, or active-controller priority. Those policies must be
explicit in the application and must remain bounded even when the listener stays continuously
readable.

## Applied control-server construction

rev0027 replaces the one-client control worker with a bounded pending set:

```text
listener + wake + pending[0..N) -> one poll set
```

Each admitted client records:

```text
nonblocking accepted descriptor
connection-time PID/UID/GID
steady-clock complete-record deadline
```

The loop order is:

1. drain a stop wake event;
2. handle at most `maximum_requests_per_cycle` readable pending clients;
3. remove dead clients;
4. expire nonready clients whose independent deadlines elapsed;
5. accept at most `maximum_accepts_per_interval` new clients when the admission interval refills.

A ready record skipped only because the per-cycle budget was reached is not expired in that cycle.
The next poll observes it immediately, preserving ready-before-expiry behavior.

Admission is refused when either bound is full:

```text
maximum_pending_clients
maximum_pending_clients_per_process
```

The rejection path never waits. If a complete authenticated request is already queued, it is decoded
only far enough to recover request ID and operation for the error response. It never reaches the
control handler.

### What changed

Before:

```text
silent A reserves the only worker until A's lease ends
```

After:

```text
silent A occupies one bounded pending slot
ready B is handled as soon as poll reports B readable
```

### What did not change

- Each connection still carries one request and one response.
- Record credentials, optional record pidfd, connection credential agreement, and descriptor-
  injection rejection remain mandatory.
- Handler execution remains synchronous. A defective or intentionally blocking handler can delay
  later work and is outside the untrusted-client scheduling claim.

## Applied terminal-server construction

rev0027 replaces the synchronous contender grace function with a persistent bounded contender set
inside the active-client poll loop. Each contender records a nonblocking descriptor, connection-time
credentials, and its own first-record deadline.

The active-loop priority is:

1. stop wake and active owner-pidfd exit;
2. active controller input;
3. active outbound drain;
4. active close decision;
5. bounded ready/expired contender rejection;
6. bounded listener acceptance when the admission interval refills.

This order is security-relevant. When active HUP and listener readability arrive together, IoTox
releases the dead controller before touching the listener. A successor still in the kernel queue is
therefore admitted by the outer worker rather than rejected on behalf of a controller that is
already gone.

Contenders never enter the Agent/controller state machine. A complete authenticated first packet is
decoded only to recover its stream ID, then receives `resource_exhausted`. Silent contenders receive
a generic stream-1 rejection after their independent short lease. All contender responses are
best-effort nonblocking sends.

The following explicit bounds prevent a continuously readable listener or one process from shaping
unbounded worker work:

```text
maximum_pending_contenders
maximum_pending_contenders_per_process
maximum_contender_accepts_per_interval
maximum_contender_records_per_cycle
contender_admission_interval
contender_open_timeout
```

## Adversarial tests added

### Control head-of-line test

A raw same-process control connection remains silent under a 400 ms request lease. A second normal
PING request is issued after the silent peer has been accepted. The PING succeeds within its 200 ms
client deadline, the handler runs once, and the silent peer later receives the timeout response.

### Control per-process bound

With a one-client per-process pending quota, the first silent connection is retained and the second
is rejected as `resource_exhausted`. Closing the first releases the quota; a later valid request is
accepted and dispatched.

### Terminal active-latency test

An established controller opens stream 8501. A second connection remains silent under a 400 ms
contender lease. After the contender has been admitted, the active controller's PING/PONG completes
within 200 ms and before the contender is rejected. The contender never reaches the packet handler.

### Terminal per-process bound

With one pending contender allowed per process, the first silent contender is retained and the
second is immediately rejected with the explicit per-process quota error. The first later receives
the ordinary concurrent-client rejection.

### Retained race tests

The existing queued-successor test deliberately holds the active handler, queues a successor, closes
the active client, and then releases the handler. rev0027 still admits that successor. Existing
fork-inherited sender, pidfd-exit, SCM_RIGHTS injection, detach ACK drain, socket-inode, and callback-
stop tests remain green.

## Resource and complexity bounds

For configured bounds `C`, `T`, and per-cycle budgets `Bc`, `Bt`:

```text
control poll descriptors <= C + 2
terminal active poll descriptors <= T + 4
control accepted descriptors <= C
terminal accepted contender descriptors <= T
per-cycle untrusted record decodes <= Bc + Bt
```

Per-process quota checks are linear in the bounded pending vector. This is intentional: the default
sets are small, no attacker-shaped hash table is introduced, and the maximum configuration is 256.

## Security interpretation

This revision improves availability within the already established owner-private socket boundary. It
is not a new authorization layer. Linux PID/UID/GID evidence distinguishes processes and supports
quotas, but another process with the daemon UID remains within the documented same-UID threat
boundary. A coalition of many processes can still compete across per-process quotas, and root can
bypass filesystem and process assumptions.

The useful claim is narrower:

> Within configured finite bounds, a silent accepted peer no longer forces unrelated ready control
> work to wait for its lease, and a silent terminal contender no longer inserts a blocking grace wait
> into the active controller loop.

## Sources rechecked online

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/accept.2.html
https://man7.org/linux/man-pages/man2/poll.2.html
https://man7.org/linux/man-pages/man7/socket.7.html
https://man7.org/linux/man-pages/man2/recv.2.html
https://man7.org/linux/man-pages/man2/pidfd_open.2.html
https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/core/scm.c
```

The online material defines Linux behavior. It does not establish IoTox correctness, starvation
freedom, production readiness, or target-fleet qualification. Those remain bounded by the executable
evidence and nonclaims in ADR 0077.
