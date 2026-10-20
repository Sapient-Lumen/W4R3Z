# ADR 0066: Separate the private terminal controller stream from local control

Status: accepted
Date: 2026-08-17

## Context

R4 made an authenticated, capability-gated Ratox PTY reachable from the Agent, but it left no
operator-facing byte stream. Reusing the request/response `control.sock` would conflate two different
contracts: finite administrative operations and a long-lived, binary, backpressured terminal stream.
A terminal client also has to survive local process replacement without giving a new process implicit
access to a stale remote attachment, retain unacknowledged input and output across a Tox route loss,
and bind every resumed attachment to the same authenticated peer principal.

The local transport must preserve packet boundaries and order, authenticate the same local user, avoid
replacing an active listener, refuse public or foreign-owned path components, and remove only the exact
socket inode it created. Terminal bytes must not enter the ordinary local control journal or Ratox
metadata journal.

Primary platform references rechecked for this decision:

```text
https://man7.org/linux/man-pages/man7/unix.7.html
https://man7.org/linux/man-pages/man2/accept.2.html
https://man7.org/linux/man-pages/man3/termios.3.html
https://man7.org/linux/man-pages/man2/ioctl_tty.2.html
```

## Decision

Add an explicitly enabled controller plane composed of a pure `RatoxClient`, a private local terminal
protocol, a same-user Unix `SOCK_SEQPACKET` server at `<runtime>/terminal.sock`, and two one-binary
commands:

```text
iotox terminal PEER_PUBLIC_KEY_HEX
iotox terminal-resume SESSION_ID_HEX [PEER_PUBLIC_KEY_HEX]
```

### Independent construction gate

`--enable-ratox-terminal-client` is distinct from the host-side
`--enable-ratox-terminal`. Client-only activation does not require a local profile store or
PTY helper. Either role may negotiate feature bit 23 because both speak Ratox v1; only the host role
can resolve local profiles or create processes. The terminal socket is absent by default and startup
fails closed if its private path cannot be created safely.

### Pure controller state

`RatoxClient` owns no toxcore, socket, authority ledger, wall clock, or terminal descriptor. It owns:

- one exact friend/online-epoch/authenticated-principal route while attached;
- one durable peer/principal/session identity while safely detached;
- an attachment nonce plus incarnation and generation fences;
- bounded unacknowledged input and retained output replay windows;
- exact outbound packets retained until transport acceptance;
- cumulative output acknowledgement and coalesced latest resize;
- ordered OPEN, RESUME, DETACH, CLOSE, route-loss, gap, exit, and failure events; and
- bounded event and packet memory with explicit failure on exhaustion.

A new OPEN resets prior controller state only after the Agent resolves a current confirmed,
feature-negotiated, authenticated route. RESUME may not change peer or principal. Stale online epochs,
wrong correlations, conflicting duplicate bytes, destructive gaps, nonadvancing generations, and
message-ID exhaustion fail closed.

### Private local protocol

Local terminal protocol v1 uses one 32-byte canonical header and at most 16 KiB of payload per
packet. The first packet must be OPEN, a connection has one nonzero stream ID, and OPEN cannot repeat.
Client packets are OPEN, INPUT, RESIZE, DETACH, CLOSE, OUTPUT_ACK, and PING. Server packets are
OPENED, OUTPUT, OUTPUT_GAP, EXIT_STATUS, DETACHED, CLOSED, ERROR, and PONG. Structured payloads are
fixed-width and canonical; reserved bytes, impossible dimensions, unknown types/status values,
trailing bytes, sequence overflow, and malformed directionality are rejected.

The local server admits one live attachment at a time. It uses pathname `AF_UNIX` `SOCK_SEQPACKET`,
owner-only parent and socket permissions, `SO_PEERCRED`, close-on-exec/nonblocking descriptors, and a
wake `eventfd`. It probes but never steals an active socket, reclaims only an unchanged stale socket
owned by the daemon user, and unlinks only the exact device/inode it bound. A second client is rejected
rather than replacing the active stream.

### One-binary terminal behavior

The client enters raw mode only after OPENED, restores terminal attributes and signal handlers through
scoped cleanup, propagates `SIGWINCH` dimensions, writes output exactly before acknowledging it, and
sends cumulative sequence positions. At beginning of line it recognizes SSH-style local escapes:
`~.` closes, `~d` detaches, `~~` sends a literal tilde, and `~?` displays local help. End of stdin
detaches rather than silently killing the remote process.

### Agent join

The Agent resolves the public key to a current friend, then requires an application-ready transcript,
bilateral Ratox negotiation, matching authority online epoch, and a nonzero authenticated remote
principal before OPEN or RESUME. Controller responses are accepted only on that same route. Local
packets, remote responses, authority-head mutation, and transport admission are serialized through
the existing Ratox effect boundary. The local delivery queue is finite and preserves OPENED, gap,
output, completion, and error order.

## Consequences

IoTox now has a real same-user operator stream from one installed executable to the R4 Ratox host
boundary. Disconnecting the local terminal detaches the remote session when it is safe to do so;
route loss preserves only state that can be resumed on a fresh authenticated epoch for the same
principal. Local packet boundaries and peer credentials are platform-enforced on the supported Linux
path, while protocol checks remain explicit in product code.

This does not establish daemon-restart PTY recovery, cross-daemon controller-state persistence,
multiple simultaneous local terminals, two-physical-host qualification, production-default
advertisement, or a complete namespace/cgroup/seccomp/LSM sandbox. Those remain R6 through R8 gates.

## Rejected alternatives

- **Tunnel terminal bytes through `control.sock`.** Finite administrative RPC and a persistent binary
  stream have different lifetime, framing, backpressure, and privacy contracts.
- **Permit any same-machine user and rely only on socket mode bits.** The server also verifies peer
  credentials and a private owned parent directory.
- **Unlink the socket pathname unconditionally on start or stop.** That can steal an active daemon or
  delete a replacement listener created after this instance lost ownership.
- **Infer a detached session from only a peer key.** RESUME names the exact 16-byte session and may not
  change its authenticated principal.
- **Acknowledge output before writing it locally.** That can lose bytes if stdout fails after the ACK.
- **Treat route loss as session exit.** The protocol has explicit detach/resume semantics; safe replay
  state is preserved while attachment authority is fenced.
