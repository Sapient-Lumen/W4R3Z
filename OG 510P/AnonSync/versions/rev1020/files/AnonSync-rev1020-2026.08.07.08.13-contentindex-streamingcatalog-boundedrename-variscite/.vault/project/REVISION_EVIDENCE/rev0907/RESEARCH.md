# AnonSync rev0907 research record

Primary sources reviewed on 2026-07-26:

- TLS 1.3 closure and truncation semantics, RFC 8446:
  https://www.rfc-editor.org/rfc/rfc8446.html
- OpenSSL `SSL_shutdown` state and return semantics:
  https://docs.openssl.org/3.5/man3/SSL_shutdown/
- gRPC deadline model and deadline propagation guidance:
  https://grpc.io/docs/guides/deadlines/
- SQLite busy-timeout accumulated sleeping behavior:
  https://www.sqlite.org/c3ref/busy_timeout.html
- Linux `clock_gettime`, including `CLOCK_MONOTONIC` and `CLOCK_BOOTTIME`:
  https://man7.org/linux/man-pages/man3/clock_gettime.3.html

## Conclusions applied to the implementation

TLS `close_notify` is orderly transport shutdown, not an application queue-empty
statement. Rev0907 therefore combines authenticated transport state with an
exact local zero-application-byte predicate and gives the result only the narrow
name `authenticated_peer_closed_idle`.

A nested stack should propagate one absolute deadline by reducing remaining
budget rather than restarting full relative timeouts at each layer. Rev0907
starts one command deadline before preflight and clamps each admitted session
stage to it. The implementation remains cooperative because outer timeout return
does not asynchronously stop inner filesystem, database, crypto, or kernel work.

SQLite busy handling may sleep repeatedly before returning `SQLITE_BUSY`. This
means a future hardening step must carry the same command budget into busy
handling and payload/dispatch-guard work; merely bounding socket polling is not a
complete command-time proof.

Linux steady clocks commonly exclude suspend while `CLOCK_BOOTTIME` includes it.
Because transport deadlines and durable lease observations use those different
models, suspend can age a claim while the transport budget appears frozen. The
release documents that mismatch instead of treating the derived static minimum
as a real-time completion guarantee.

## Speculation and next architecture

The next useful C++ boundary is a deadline-aware transactional pre-prefix guard
that either preserves the exact fenced claim and emits the prefix, or releases
that same claim before any application byte. Deadline propagation should then
reach SQLite busy policy, payload reproof, and receipt application.

Long static leases are safe against the admitted horizon but slow recovery after
a dead sender. A mature design likely needs renewable, fenced lease heartbeats
whose authority, cadence, cap, and failure semantics are explicit and durably
auditable. Named protocol stages should replace anonymous ordinal stages, and the
process-local supervisor should eventually become a durable typed lifecycle
owner rather than another retry loop.
