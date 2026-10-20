# Ratox local controller fault-gate source review — rev0020

Date: 2026-08-17 America/New_York

## Question

How should the private single-controller socket bound an incomplete first handshake and reject a
concurrent real CLI without losing typed protocol truth to a send/close race?

## Sources rechecked

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/poll.2.html
https://man7.org/linux/man-pages/man2/accept.2.html
```

The Linux Unix-domain socket documentation defines pathname-socket permissions, ordered record
semantics for `SOCK_SEQPACKET`, peer credentials, and `EPIPE` after the remote endpoint closes. The
`poll` documentation defines readiness and finite millisecond waits, while warning that timeouts are
rounded to clock granularity and can overrun because of scheduling. The `accept` documentation
supports nonblocking accepted-descriptor handling and requires ordinary transient/error treatment
rather than assuming every readiness indication produces a durable client. These are operating-system
semantics, not an IoTox security review.

## Failure found at the process boundary

The in-process socket test originally connected a second client and immediately waited for a busy
response. The real CLI behaves differently: it first sends its canonical `OPEN`. The server could
accept the contender, send `resource_exhausted`, and close quickly enough that the contender's send
observed `Broken pipe`. The typed error existed in the server path but was not reliably observable by
the product client. A generic denial stream ID also caused a valid pre-admission result to look like
stream corruption.

This distinction matters because `SOCK_SEQPACKET` preserves complete records but does not turn an
application close race into a request/reply transaction. The service must define which side consumes
the first record and when it closes.

## Second failure found under repetition

The first separate-process gate passed ordinary CTest and sanitizer runs, then failed once at
iteration 122 of a repeated real-CLI loop. The replacement rendered output staged immediately before
`DETACHED` and sent its cumulative `OUTPUT_ACK`, but the server had already completed outbound drain
and closed without consuming that final record. This was not an assertion timing defect: the local
protocol lacked a close acknowledgement phase.

A naive fix that continued polling the listener while refusing new admission would also be wrong. A
queued connection leaves the listener readable; polling it without accepting would spin, while
accepting and denying would classify a successor against a stream that had already requested detach.

## Applied construction

rev0020 adds a finite steady-clock lease for the first packet. A silent accepted connection receives a
typed timeout, publishes no stream, triggers no disconnect callback, and releases the slot. The lease
is configurable only within 1 ms..60 s and defaults to 5 s.

During an active attachment, the server processes no more than four contenders per cycle. The whole
batch shares one 20 ms first-record window; the server decodes only enough to retain the contender's stream ID, never invokes
the Agent handler for that record, sends the canonical busy result, and closes. A silent or malformed
contender receives a connection-scoped error using the safe fallback ID.

The poll loop gives the active descriptor's terminal state precedence over listener contention. If
active HUP/error and a queued replacement become visible together, any readable active record is
processed first and the dead attachment is released before the listener is classified. This avoids
denying a legitimate replacement for a controller that has already disappeared.

The CLI accepts a canonical `ERROR` before `OPENED` as a connection-admission result. It continues to
require exact stream-ID equality for every success/progress packet and for all admitted stream
traffic.

A committed `DETACH` now starts a bounded ACK-only phase. The server continues sending final staged
results, accepts only cumulative `OUTPUT_ACK`, and closes on client EOF or a configurable 1 ms..5 s
deadline (250 ms default). Every packet-send wait consumes that same absolute deadline. During that
phase the listener is absent from the poll set, leaving queued successors in the kernel backlog until
the former stream is actually released. Any other post-detach packet is rejected before dispatch.

## Evidence added

Unit coverage proves silent-client expiry, successor admission, exact typed busy metadata and stream
ID, configuration bounds, no publication/disconnect for an uncommitted `OPEN`, and exactly one
dispatched `OPEN` under contention. A deterministic blocked-handler test also queues a successor,
closes the active controller, and proves that combined active-HUP/listener readiness admits the
successor rather than returning a stale busy result.

A separate-process CTest spawns the real one-binary client. It proves one winner, an explicit loser,
abrupt winner death, replacement resume with output-before-ACK, exact cumulative acknowledgement,
clean detach, and explicit `not_found` after an empty server restart. The first run of this gate found
the `EPIPE` race; the consume-and-deny handshake is the resulting fix. Repeated execution then found
the detach-ACK race at iteration 122. After adding the bounded two-phase drain and backlog ordering,
the same real-CLI gate completed 1,000 consecutive debug runs without failure. Unit coverage stages
final output before `DETACHED`, verifies render-before-ACK ordering, commits the exact cumulative ACK,
checks invalid drain limits, and rejects non-ACK traffic after detach.

## Boundary retained

The evidence is local to one Linux host and one test server. It does not prove a complete remote
Ratox service across two Agents, toxcore reconnect, revocation races, storage exhaustion, supervised
PTY survival, or persistent controller replay. Same-UID hostile connection flooding and deliberate
use of the bounded post-DETACH hold remain local availability concerns rather than solved
host-compromise problems.
