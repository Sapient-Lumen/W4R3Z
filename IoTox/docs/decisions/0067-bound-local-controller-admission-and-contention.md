# ADR 0067: Bound local controller admission and preserve typed contention

Status: accepted
Date: 2026-08-17

## Context

ADR 0066 established one owner-private `SOCK_SEQPACKET` terminal controller stream. The first
implementation accepted one client and then waited for its first packet without a separate admission
lease. A same-user process that connected and remained silent could therefore reserve the only local
controller slot indefinitely. This is not a cross-user authority bypass, because the parent directory,
socket mode, and `SO_PEERCRED` checks still apply, but it is an avoidable local availability failure.

The initial contention rejection also accepted a losing connection, sent a generic busy error, and
closed it immediately. A real competing `iotox terminal` process could still be in its first `OPEN`
send. Depending on scheduling, the client observed the close as `EPIPE` instead of receiving the
canonical `resource_exhausted` result. When the denial used a placeholder stream ID, the client could
also describe a legitimate pre-admission error as stream-ID corruption.

Primary platform references rechecked for this decision:

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/poll.2.html
https://man7.org/linux/man-pages/man2/accept.2.html
```

Linux `SOCK_SEQPACKET` preserves record boundaries and order. `poll` supplies a finite readiness wait,
but its millisecond timeout can be rounded and overrun slightly, so the implementation uses a
steady-clock deadline rather than treating one poll return as elapsed-time truth. Accepted sockets
remain nonblocking and close-on-exec. These sources define platform behavior; they do not audit or
approve IoTox.

## Decision

### Finite first-OPEN lease

Every accepted primary controller connection receives a finite first-`OPEN` lease. The configuration
must be between 1 ms and 60 seconds; the product default is 5 seconds. Until `OPEN` commits, each
server poll is bounded by the smaller of the ordinary service interval and the remaining steady-clock
lease.

If the deadline expires before the first complete canonical packet, the server sends a typed
`timeout` error and closes the connection. No stream is published, no packet handler is called, and no
disconnect callback is emitted for state that never existed. The next same-user connection can then
compete for admission immediately.

### Consume-and-deny contention

While one controller is active, the listener remains observable so contenders receive an explicit
outcome instead of sitting in the listen queue. Rejection is deliberately bounded:

- process at most four queued contenders in one active-client cycle;
- give the whole accepted batch one shared 20 ms window to present first records;
- decode that record only to retain its nonzero stream ID for the response;
- never dispatch the contender packet to the Agent/controller handler; and
- send typed `resource_exhausted` metadata, then close the contender.

A malformed or silent contender still receives a connection-scoped denial after the grace period.
The bounded batch and grace prevent an unbounded accept loop, although a same-user process can still
consume a limited amount of active-stream service time by repeatedly connecting.

The active descriptor has precedence over the listener when it reports terminal state. The server
processes readable active data first when present, then releases an active descriptor that reports
hangup, error, or invalidity before it denies queued contenders. A replacement that was already
queued when the former controller died is therefore eligible for admission instead of receiving a
busy result on behalf of a dead controller.

### Pre-OPEN error scope

Before `OPENED`, an `ERROR` may describe connection admission rather than an admitted stream. The CLI
therefore accepts a canonical server `ERROR` before applying the requested stream-ID equality check.
Every success or progress packet (`OUTPUT_GAP`, `OPENED`, `PONG`, and later stream traffic) remains
bound to the exact random stream ID. This exception does not relax post-admission stream fencing.

### Bounded two-phase DETACH

A successful local `DETACH` no longer implies that the server can close the descriptor immediately.
The Agent may stage final `OUTPUT` followed by `DETACHED`; the CLI must render those bytes before it
sends the cumulative `OUTPUT_ACK`. Closing after the send path completed but before that ACK was read
created an intermittent loss of controller replay truth at the real process boundary.

After `DETACH` commits, the server therefore enters an ACK-only drain bounded to 1 ms..5 s, with a
250 ms default. It continues draining terminal results and accepts only exact-stream `OUTPUT_ACK`
records. Any other packet is a protocol error rejected before handler dispatch. Packet-send waits
consume the same absolute deadline instead of retaining an independent 100 ms budget. The listener is
omitted from the poll set during this short phase, so successors remain in the kernel listen backlog
instead of causing a readable-listener busy loop or receiving a denial for a stream that is already
detaching. Client close or the deadline releases the slot, preserving a finite same-UID availability
bound.

### Process-level fault gate

Add a CTest that starts the real local server and spawns the installed `iotox` executable. It proves:

- one controller wins and a simultaneous controller exits with the typed busy reason;
- the losing `OPEN` is not dispatched to the Agent handler;
- abrupt winner death releases the local attachment;
- a queued replacement is admitted when active death and listener readiness occur in one poll cycle;
- `terminal-resume` renders retained and final detach output before cumulative acknowledgement;
- the server commits that final ACK during the bounded two-phase detach drain; and
- non-ACK traffic after DETACH is rejected before the Agent handler; and
- a restarted empty server returns explicit `not_found` semantics instead of implying PTY survival.

This is a local controller-process gate. It does not substitute for a two-Agent Tox route, real PTY
supervision across daemon restart, authority-revocation timing, or durable replay storage.

## Consequences

A silent same-user client no longer reserves the sole controller slot indefinitely. A legitimate
loser receives a stable typed result across the actual CLI/process boundary, and the implementation
makes “read for admission identity” distinct from “dispatch as an operation.” Local controller death
and replacement semantics now have executable process evidence. Final detach output is not declared
acknowledged merely because the local server finished sending it; the client's cumulative ACK must
cross back through the same handler before close or the finite drain deadline.

One rejection batch has a shared 20 ms receive window plus at most four independent 20 ms error-send
deadlines before the worker returns to the active controller, with ordinary scheduler overhead. That
is an explicit bounded same-user denial-of-service tradeoff, not a fairness guarantee under a
malicious local account. The post-DETACH ACK-only hold is independently bounded to 5 seconds and
defaults to 250 ms. Host compromise, same-UID malice, multiple simultaneous admitted controllers,
persistent controller replay, and remote R6 fault qualification remain outside this
decision.

## Rejected alternatives

- **Wait indefinitely for the first packet.** This lets a silent same-user process hold the sole slot.
- **Close every contender immediately.** The real client can lose the typed denial to a send/close
  race and report only `EPIPE`.
- **Dispatch the contender's `OPEN` before denying it.** Admission parsing must not create controller
  state or Agent effects.
- **Require the placeholder denial stream ID to match.** Before admission, the server may not have
  received the client's random ID; the error is connection-scoped.
- **Add an unbounded accept-and-drain loop.** A connection flood must not monopolize the active
  controller worker.
