# IoTox private terminal client v1

Status: implemented behind explicit controller activation, fault-hardened in rev0020, message-bound
in rev0026, bounded-multiplexed in rev0027, route-loss qualified in rev0045, exact-session reconnect
automated by ADR 0289, and production-CLI reconnect qualified on direct UDP and forced TCP by ADR
0300 and across two sequential losses by ADR 0316

## Purpose and boundary

The terminal client is the private same-user byte-stream entrance to Ratox v1. It is not a second
network protocol and it does not grant terminal authority. Tox carries Ratox frames; the confirmed
IoTox transcript and authority proof bind a stable remote principal; the remote signed ledger decides
`interactive.terminal`; the remote profile registry selects fixed local execution policy.

Controller activation is explicit:

```sh
iotox run \
  --enable-ratox-terminal-client \
  --state /absolute/private/device.toxsave \
  --runtime /absolute/private/runtime
```

The default configuration creates no `terminal.sock` and advertises no Ratox feature. Client-only
activation requires neither a local terminal profile store nor a PTY helper because it creates no
local process.

## Commands

Open a new session to one exact Tox public key:

```sh
iotox --runtime "$RUNTIME" terminal "$PEER_PUBLIC_KEY_HEX"
```

Keep that same invocation attached across authoritative route loss:

```sh
iotox --runtime "$RUNTIME" terminal "$PEER_PUBLIC_KEY_HEX" --reconnect
```

This is no longer only a local state-machine claim. The Sandwurm `ratox-cli-reconnect` scenario
executes that exact command under a pseudo-terminal, installs 100% loss on both guest TAPs, requires
one unchanged CLI PID/start time and retained remote PTY, then proves exact generation/sequence
continuation after a higher authenticated epoch on direct UDP and forced TCP. See ADR 0300 and
`evidence/2026-09-02-sandwurm-ratox-cli-reconnect.md`. ADR 0316's additive
`ratox-cli-reconnect-repeated` scenario then proves the same process and shell cross two sequential
losses on both carriers with generations 1-to-2-to-3. Long-soak and overlay-route qualification
remain separate.

Resume one exact retained detached session, optionally restating the peer key:

```sh
iotox --runtime "$RUNTIME" terminal-resume "$SESSION_ID_HEX" ["$PEER_PUBLIC_KEY_HEX"]
```

ADR 0292 also permits any `PEER_PUBLIC_KEY_HEX` position above to use the shared `PEER` selector:
explicit `key:HEX`, `friend:N`, or `alias:NAME`, plus unambiguous bare key/number/alias forms. Alias
resolution crosses the same-user control socket before terminal attachment and changes no terminal
or Ratox framing. An alias grants no authority and a retained alias whose key is not a current friend
fails live attachment.

Public keys are exactly 32 bytes encoded as 64 hexadecimal characters. Session IDs are exactly 16
bytes encoded as 32 hexadecimal characters. `--timeout-ms` is bounded to 1..60000 and applies to
local connection and packet I/O deadlines.

The client prints the accepted session ID after OPENED so an operator can retain it for an explicit
resume. Session IDs are routing metadata, not authority or secrets.

## Terminal interaction

After the Agent returns OPENED, an interactive stdin is placed in raw mode and restored on every
ordinary exit path. Window dimensions are sent initially and after `SIGWINCH`. Output is written to
stdout before a cumulative OUTPUT_ACK is sent.

At the beginning of an input line:

```text
~.  request remote close
~d  detach and leave the remote process resumable
~~  send one literal ~
~?  show local escape help
```

EOF on stdin requests DETACH. SIGINT or SIGTERM also attempts a bounded detach before returning the
signal-derived process status. Escape recognition is local and never enters the remote byte stream
unless `~~` is used.

## Local socket contract

`<runtime>/terminal.sock` is a Linux pathname Unix-domain `SOCK_SEQPACKET` socket. The runtime parent
must be a real directory owned by the effective user with no group/other permissions. The socket is
owner-only. Connection-time `SO_PEERCRED` is followed by mandatory per-record `SCM_CREDENTIALS` on
both requests and responses; supported kernels also require the sender's `SCM_PIDFD`. Exact peer
identity must match on every record. Malformed, duplicate, truncated, or unexpected ancillary data
fails closed, and any received descriptors are closed before rejection. The server accepts one
live local stream. The first complete `OPEN` must arrive within the configured 1 ms..60 s lease
(default 5 s), so a silent same-user client cannot reserve the slot indefinitely.

Startup behavior is fail closed:

- a non-socket path is never replaced;
- a socket owned by another user is never removed;
- a reachable listener is never stolen;
- a stale owned socket is removed only after an unchanged device/inode recheck; and
- shutdown unlinks only the exact socket device/inode this server bound.

Both endpoints use close-on-exec and nonblocking descriptors. `SOCK_SEQPACKET` preserves message
boundaries and order; product framing still validates every byte.

The first valid request binds the slot to the sending process. The server retains a pidfd delivered by
the kernel or opened against that exact PID, polls it beside socket readiness, and releases the slot
when the process exits even if a forked or descriptor-recipient process still holds the socket. The
accepted connection is also pinned with `SO_PEERPIDFD` before the first request when the running kernel
supports it, closing the silent pre-`OPEN` interval without reopening a numeric PID. Unsupported
kernels retain the finite first-OPEN lease. The client applies the same record-identity check to
server responses, so accepted-server descriptor inheritance does not transfer server identity.

While one stream is active, the server polls the active controller, owner pidfd, listener, wake
descriptor, and a bounded contender set together. Each contender has an independent 20 ms first-
record lease by default. Global and per-process pending quotas, finite accept refills, and finite
ready-record work per cycle bound listener pressure. Active input/output and active descriptor death
are handled before contender work, so a silent contender does not insert its lease into active-stream
latency and a same-cycle successor is not denied for a controller that has already exited. The server
may decode a complete already-queued contender record only to retain its stream ID for a typed
`resource_exhausted` response; it never dispatches the losing packet. Rejections are nonblocking best
effort. These limits do not make a hostile same-UID account or unlimited multi-process coalition
harmless.

Successful `DETACH` uses a separate bounded close phase. The server drains final `OUTPUT` followed by
`DETACHED`, then accepts only exact-stream cumulative `OUTPUT_ACK` records until client close or a
configurable 1 ms..5 s deadline (250 ms default). Packet-send waits consume that same absolute
deadline. The listener is omitted from polling during the phase, leaving successors in the kernel
backlog rather than spinning on readability or receiving a denial for a stream that is already
closing. Any other post-detach packet is rejected before the Agent handler sees it.

## Canonical local protocol

Every packet has a 32-byte header:

```text
offset  size  field
0       4     magic "ITTS"
4       1     major = 1
5       1     minor = 0
6       1     packet type
7       1     flags = 0
8       8     nonzero stream ID, big endian
16      8     sequence or cumulative acknowledgement, big endian
24      2     typed IoTox status, big endian
26      2     payload length, big endian
28      4     reserved = 0
```

Payloads are at most 16,384 bytes. Sequence-bearing packets are INPUT, OUTPUT, and OUTPUT_ACK. The
first packet must be OPEN; later packets must use the same stream ID and may not repeat OPEN.

OPEN has a fixed 56-byte payload: peer public key, session ID, columns, rows, mode, and three reserved
zero bytes. `new_session` requires a nonzero peer and zero session ID. `resume_only` requires a
nonzero session ID and may omit the peer only when the Agent still retains that exact peer/principal
binding.

OPENED reports the accepted session ID, incarnation, generation, next input sequence, and next output
sequence. OUTPUT_GAP reports the first retained remote output byte and the produced-next position.
EXIT_STATUS is an exact eight-byte exited/signaled/unknown record. ERROR contains bounded metadata
bytes and a non-success typed status; the CLI renders those bytes through a printable-ASCII sanitizer.
Before OPENED, ERROR may be connection-scoped because admission can fail before the server learns or
commits the requested stream ID. Every success/progress packet and every admitted-stream packet still
requires the exact nonzero stream ID. ERROR never contains terminal bytes or local process policy.

## Replay and failure semantics

The controller retains unacknowledged input and output under independent byte bounds. An outbound
Ratox packet remains immutable until c-toxcore accepts it. Cumulative output ACK and latest resize may
coalesce, while input, OPEN/RESUME, detach/close, and completion ordering remain exact.

Local detach completion does not infer acknowledgement from a successful server send. The CLI writes
every final output byte first, sends the cumulative ACK, receives `DETACHED`, and closes; the server's
bounded ACK-only phase commits that final acknowledgement or releases the slot at its explicit
deadline.

Remote duplicate OUTPUT is accepted only when overlapping bytes are identical. A remote gap may
advance beyond bytes already discarded locally, but it may not destroy retained local output.
Route loss while attached transitions to detached state, clears the attachment route, and retains only
state safe for an exact-session resume. Route loss while opening, stale correlations, wrong principal,
conflicting duplicate bytes, sequence overflow, nonadvancing generation, and resource exhaustion fail
closed.

While attached with local input open, the installed client sends local PING once per second. The
Agent forwards it through the exact current Ratox attachment and returns local PONG only after a
correlated remote PONG. Three consecutive unanswered sampling deadlines produce a warning but do not
close the controller, detach or resume the session, relabel the carrier, or advance an epoch. Sampling
continues; a later PONG reports recovery. Explicit detach/input close stops new sampling.

The Ratox client reuses one exact PING identity per attachment to bound the host's never-evicted v1
control replay cost. This proves remote Agent route/replay reachability, not PTY process progress,
output latency, or upstream privacy-route health (ADR 0193).

ADR 0197 qualifies the complete-loss continuation of this rule. A heartbeat timeout remains only a
warning while carrier/session truth is confirmed. Authoritative peer-offline returns typed
`unavailable` to the local controller and leaves the remote PTY detached under its existing bounded
host policy. The operator may invoke `terminal-resume` only after the peer is confirmed and
authority-capable on a higher online epoch; the server must return the exact session ID,
incarnation, next byte positions, and generation plus one. The client never silently opens a new
session or migrates routes to make resume appear successful.

ADR 0289 automates only that already-authorized resume step. After the first OPENED, `--reconnect`
retains the exact session ID/incarnation/generation, treats only authoritative `unavailable` as the
transition into reconnect, and retries one `resume_only` request every 500 ms. The Agent still gates
each attempt on a higher authenticated epoch and stable peer/principal. The CLI accepts OPENED only
when session/incarnation remain exact and generation increases. It never falls back to `new_session`;
`not_found`, changed identity, busy state, and protocol failure terminate visibly. SIGINT/SIGTERM
interrupt the wait. Batch mode and an already explicit `terminal-resume` cannot select reconnect.

## Privacy and nonclaims

Terminal input/output is held only in bounded live memory and transport packets. It is not written to
`status`, `ratox-events`, ordinary control journals, argv logs, or profile records. Error strings passed
through the local protocol are bounded and metadata-only.

rev0020 adds one-host separate-process evidence for typed contention, abrupt local-controller death,
replacement resume, retained and final detach output before ACK, exact cumulative acknowledgement
committed before release, clean detach, and explicit `not_found` after an empty server restart. Unit
coverage additionally proves that non-ACK traffic cannot cross the post-detach dispatch gate. It also
participates in the deterministic R6 controller-replacement gate. rev0026 adds process-bound request/
response and ancillary-injection evidence. rev0027 adds active-stream latency, per-process
contender-quota, and retained pre-`OPEN` descriptor process-exit regressions. It does not claim:

- survival of the remote PTY across Agent restart;
- persistence of controller replay state across Agent restart;
- genuine-route repeated reconnect soak, revocation, storage-failure, or complete toxcore fault qualification;
- more than one local terminal stream per Agent;
- authorization between arbitrary processes sharing the same UID;
- starvation freedom against an unlimited hostile same-UID process coalition;
- preemption of a blocking Agent/controller callback after a packet is admitted;
- complete two-guest Sandwurm or impaired-network qualification;
- a complete process sandbox; or
- production-default terminal enablement.
