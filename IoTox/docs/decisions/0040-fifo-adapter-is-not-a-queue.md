# ADR 0040 — The ratox command FIFO is an adapter, not a queue

- Status: accepted
- Revision: rev0011
- Date: 2026-08-14
- Supersedes the unresolved FIFO portion of ADR 0023
- Depends on ADR 0036 and ADR 0039

## Context

Ratox is compelling because a peer becomes a directory and an action becomes an ordinary write.
IoTox needs that property without pretending that bytes buffered by a kernel FIFO are a durable,
identified, authorized command.

A FIFO is a named reference to a kernel pipe. Its bytes are not stored in the filesystem, it is a
byte stream rather than a message queue, and unread bytes disappear when no process retains the
pipe. Multiple writers are protected from interleaving only when each record is emitted in one
write no larger than `PIPE_BUF`. POSIX guarantees at least 512 bytes; Linux currently provides
4096 bytes.

The durable command engine already freezes an outgoing identity and canonical request before the
first toxcore send. A filesystem entrance must use that engine rather than creating a second truth.

## Decision

Every projected Tox peer receives a private FIFO:

```text
/run/iotox/peers/<UPPERCASE-TOX-PUBLIC-KEY>/command
```

The rev0011 contract is deliberately narrow:

```text
record encoding:       printable ASCII followed by LF
maximum record body:   256 bytes
implemented operation: device.describe
recommended emission: one write of at most 257 bytes including LF
reply channel:         none in-band
```

The FIFO monitor is a synchronous framing adapter. It owns no persistent queue, operation policy,
message identity, transport retry, or result state. A complete record is handed to the Agent's
existing command entrance. The operation is admitted only after that path commits its exact signed
durable record. A successful `write(2)` therefore means only that bytes reached the pipe; it does
not mean the command was admitted, sent, received, authorized, executed, or completed.

Ingress evidence is appended to the transient per-peer `command-events` journal. An admitted event
contains the durable sender epoch and message id. The authoritative command record lives in the
signed command store and its `commands/` projection. `device.describe` terminal state is also
projected under the peer's `iotox/description` tree.

The daemon shall:

- create and enforce a daemon-owned mode-`0600` FIFO under a daemon-owned mode-`0700` peer
  directory;
- reject symlinks, regular files, foreign ownership, wrong modes, and inode substitution using
  `lstat`, `open(..., O_NOFOLLOW)`, `fstat`, and device/inode comparison;
- open separate nonblocking read and hold-writer descriptors instead of relying on Linux's
  nonportable `O_RDWR` FIFO behavior;
- bound records before allocation or operation dispatch;
- reject non-printable bytes;
- expire an unterminated or discard-mode fragment after bounded inactivity so one abandoned writer
  cannot silently prefix a later writer;
- periodically discover newly projected peers and withdraw stale descriptors;
- fail closed rather than replacing a hostile path in the monitor;
- stop the FIFO monitor before the structured control server and transport during daemon shutdown.

An empty line is a complete record and is rejected by the operation parser. The monitor may read
several complete lines from one atomic write, but each line becomes a distinct admission attempt.

## Consequences

The ordinary surface now works through the same persistent semantics as the structured CLI. Shell
scripts gain a ratox-like entrance without requiring toxcore linkage or knowledge of the local
control protocol.

The FIFO is intentionally unsuitable as an offline mailbox, durable spool, request/reply protocol,
or proof of completion. Writers that need a correlated synchronous response should use the one
`iotox` executable over the structured local socket. Writers that use the FIFO must inspect
`command-events`, `commands/`, or the CLI afterward.

Backpressure is real. The monitor invokes the durable command path synchronously, so a saturated or
slow command engine slows FIFO draining. This is preferable to silently inventing a second queue,
but per-peer admission scheduling and explicit operator feedback remain future work.

Adding parameters or mutable operations requires a new canonical local record grammar and the
operation's own safety contract. Rev0011 does not make arbitrary shell text executable.
