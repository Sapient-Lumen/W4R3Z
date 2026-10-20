# ADR 0077: Bound and multiplex local seqpacket admission

- Status: accepted and implemented
- Date: 2026-08-18
- Revision: rev0027
- Supersedes: the serial administrative request worker and blocking active-terminal contender grace retained by ADRs 0011, 0067, and 0076
- Extends: ADR 0076 kernel-bound record identity

## Context

IoTox has two owner-private Linux `AF_UNIX/SOCK_SEQPACKET` planes:

1. `control.sock` carries one finite administrative request and response per connection.
2. `terminal.sock` carries one active controller stream and explicitly rejects concurrent attach attempts.

rev0026 bound each record to kernel sender evidence and added a finite request/open lease. That closed
indefinite descriptor retention, but it did not close two availability gaps among processes that can
already reach the daemon user's private socket directory:

- the control worker accepted one client and waited for that client's complete request before
  returning to the listener, so one silent connection serialized every ready request behind its
  lease; and
- the terminal worker accepted a bounded batch of contenders and synchronously waited in a shared
  grace window for their first packets while an established controller stream was active.

Linux `poll(2)` defines readiness as an operation that can proceed without blocking, and a zero
poll timeout is an immediate observation. `accept4(2)` can atomically return nonblocking,
close-on-exec accepted sockets. `SOCK_SEQPACKET` preserves record boundaries, so each ready control
client or contender can be consumed as one complete authenticated record without introducing an
application reassembly queue. These properties permit a single bounded readiness loop without one
thread per peer.

## Decision

### Administrative request lane

The control server SHALL:

- keep a bounded vector of accepted pending clients;
- poll the listener, wake event, and all pending clients together;
- assign each accepted client an independent complete-record deadline;
- process ready records before expiring silent leases;
- cap ready requests handled per poll cycle;
- cap accepts per admission interval;
- cap total pending clients and pending clients sharing one connection-time process ID;
- authenticate the received record against the connection-time credentials before dispatch;
- best-effort decode an already queued overloaded request only to correlate its request ID and
  operation, never to dispatch it; and
- perform admission-error sends on nonblocking accepted descriptors and close immediately if the
  response cannot be queued.

A ready administrative request therefore no longer waits behind an unrelated silent client's
request lease. Handler execution remains synchronous and trusted; this decision does not pretend to
preempt a blocking application handler.

### Active terminal controller lane

The terminal server SHALL continue to admit exactly one controller into the state machine. While
that controller is active, the server SHALL:

- keep only a bounded vector of accepted contenders;
- maintain an independent short first-record deadline for every contender;
- poll active controller, owner pidfd, wake event, listener, and contenders in one loop;
- process active-controller events and outbound drain before contender work;
- release a dead active controller before accepting or rejecting a successor observed in the same
  poll cycle;
- cap contender accepts per admission interval and first-record decodes per cycle;
- cap total contenders and contenders sharing one connection-time process ID;
- decode a contender record only to recover its stream ID for a correlated `resource_exhausted`
  response; and
- never wait for contender input or output inside the active-stream path.

Once DETACH commits, the listener remains out of the poll set until the bounded ACK drain releases
the old stream. Already accepted contenders remain bounded and may receive best-effort nonblocking
busy responses, but they never enter the controller state machine.

### Configuration bounds

All new limits are explicit `ControlServer::Config` or `TerminalServer::Config` fields. Zero,
oversized, internally inconsistent, or nonpositive interval/lease values fail startup before the
socket is published.

Defaults are intentionally finite:

```text
control pending clients                         32
control pending clients per process              4
control accepts per 1 ms interval                 8
control requests per cycle                        8
terminal pending contenders                      16
terminal pending contenders per process           4
terminal accepts per 1 ms interval                 4
terminal contender records per cycle              8
terminal contender first-record lease             20 ms
```

## Consequences

### Positive

- One silent control peer cannot serialize otherwise ready administrative requests behind its lease.
- Same-process connection hoarding is bounded independently from the global descriptor bound.
- Silent or slow terminal contenders do not impose a grace-window pause on the active controller.
- Accept and decode work is bounded per refill/cycle, reducing listener-flood monopolization of the
  single owner thread.
- Existing message-bound credential/pidfd and ancillary-injection checks remain on every consumed
  record.
- No local packet format or Ratox wire version changes.

### Costs and tradeoffs

- The server holds a small bounded set of additional file descriptors and poll entries.
- Admission order is readiness-driven rather than a strict global FIFO once clients are accepted.
- A response to an overloaded peer is best effort; a nonreading peer may be closed without receiving
  the error.
- Per-process quotas use Linux process identity, not a cryptographic principal. Multiple cooperating
  processes under one UID can consume their individual quotas.
- The synchronous control handler and terminal packet/drain callbacks can still delay their own
  worker if application code blocks.

## Rejected alternatives

### One detached thread per client

Rejected because it makes thread count attacker-shaped, complicates stop/join semantics, and is
unnecessary for one-record seqpacket exchanges.

### Preserve serial acceptance and shorten the lease

Rejected because it only reduces, rather than removes, head-of-line blocking and couples legitimate
latency to an unrelated peer's timeout.

### Immediately close every terminal contender without reading

Rejected because an already queued canonical OPEN can be cheaply authenticated and decoded to return
the attempted stream ID. The decode is bounded and never dispatched.

### Promote an already accepted contender when the active controller dies

Rejected for this revision. Admission classification remains stable: a connection accepted while a
controller is live is a contender and is never silently promoted into the privileged state machine.
A successor still queued in the kernel when active death is observed remains eligible for normal
admission.

## Evidence

Owned tests cover:

- a silent control client coexisting with a ready request that completes before the silent lease;
- per-process control pending-client quota and recovery after close;
- a silent terminal contender coexisting with an active PING/PONG that completes before the
  contender lease;
- per-process terminal contender quota;
- correlated concurrent terminal rejection;
- queued successor admission when active death and listener readiness coincide;
- invalid zero and inconsistent configuration limits; and
- all rev0026 credential, pidfd, ancillary-rights, inode-ownership, callback-stop, and process-exit
  cases.

The applied review is `docs/research/bounded-local-ipc-admission-rev0027.md`. Qualification logs are
under `artifacts/rev0027/`.

## Nonclaims

rev0027 does not claim:

- authorization or confidentiality between mutually hostile processes sharing one UID;
- starvation freedom under an unbounded coalition of distinct same-UID processes;
- kernel-level traffic shaping, cgroup resource quotas, or namespace isolation;
- preemption of a blocking application callback;
- promotion fairness for contenders already accepted while a controller is active;
- target-kernel-fleet qualification or independent production security review.

## Primary sources rechecked online

- Linux `unix(7)`: https://man7.org/linux/man-pages/man7/unix.7.html
- Linux `accept(2)`: https://man7.org/linux/man-pages/man2/accept.2.html
- Linux `poll(2)`: https://man7.org/linux/man-pages/man2/poll.2.html
- Linux `socket(7)`: https://man7.org/linux/man-pages/man7/socket.7.html
- Linux `recv(2)`: https://man7.org/linux/man-pages/man2/recv.2.html
- Linux `pidfd_open(2)`: https://man7.org/linux/man-pages/man2/pidfd_open.2.html

These sources define kernel interfaces; they do not audit IoTox or prove the fairness properties of
this implementation.
