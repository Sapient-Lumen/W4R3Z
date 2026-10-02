# Ratox-successor command FIFO v1

## Purpose

This contract defines the first literal writable ratox-style surface in IoTox. It is intentionally
smaller than the structured local protocol and intentionally enters the same durable command
engine.

## Location and lifecycle

For each current Tox friend with public key `K`, the daemon projects:

```text
<RUNTIME>/peers/K/command          FIFO, mode 0600
<RUNTIME>/peers/K/command.help     regular file, mode 0600
<RUNTIME>/peers/K/command-events   regular append journal, mode 0600
```

`K` is exactly 64 uppercase hexadecimal characters. The containing peer directory is daemon-owned
mode `0700`. The FIFO appears and disappears with the peer projection. An open descriptor may
briefly outlive an unlinked projection, but the monitor withdraws it on the next bounded rescan.

## Record grammar

```abnf
record       = command LF
command      = read-operation / profile-status-set / update-stage
read-operation = "device.describe" / "system.summary"
profile-status-set = "profile.status.set" SP status
update-stage = "update.stage" SP head-record
status       = "available" / "away" / "busy"
head-record  = 64HEXDIG
HEXDIG       = DIGIT / %x41-46 / %x61-66
SP           = %x20
LF           = %x0A
```

The maintained revision implements exactly:

```text
device.describe
system.summary
profile.status.set available
profile.status.set away
profile.status.set busy
update.stage HEAD_RECORD_HEX
```

No quoting, escaping, free-form argument tail, shell expansion, NUL, CR, UTF-8, JSON, or binary
framing is accepted. Each mutation has exactly one bounded argument. An empty record is framed
successfully and rejected as an unsupported operation.

A producer should emit the entire operation plus LF in one `write(2)`. The largest supported write
is 257 bytes, which is below the POSIX minimum `PIPE_BUF` of 512 bytes. This preserves record
contiguity among conforming concurrent writers. `printf '%s\n' system.summary > command` is one
canonical shell example.

The monitor tolerates a record split across reads because a FIFO is a byte stream. It cannot observe
writer boundaries. An incomplete record is therefore discarded after two seconds of inactivity so
an abandoned writer cannot silently concatenate with a later writer. Oversized or non-printable
records enter discard mode until LF or timeout.

## Admission semantics

The following statements are deliberately different:

```text
write returned success       bytes entered the kernel pipe
record observed              monitor framed one complete record
record parsed                operation name is registered
record admitted              exact signed durable command was committed
transport queued             toxcore accepted the exact packet locally
remote RECEIVED              peer committed the exact request
terminal result              operation completed or failed terminally
```

`command-events` records the local ingress result. An admitted line carries nonzero
`sender-epoch` and `message-id`; those fields identify the signed durable record. A rejected line
uses `state=not-admitted` and a nonzero error code.

An existing Tox friend does not need to be online for admission. The signed v3 store, not the FIFO,
retains the request until a compatible confirmed and authorized session exists. A normal-priority,
non-expiring FIFO request has the same one-second first-attempt delay as the structured entrance.
Cancellation is deliberately typed and durable-key-bound rather than encoded as a second FIFO
grammar:

```sh
iotox --runtime <RUNTIME> command-cancel K EPOCH MESSAGE
```

It succeeds only before the first committed request attempt.

`command-events` is a transient projection, not the queue and not the audit authority. Inspect the
signed command store through:

```sh
iotox --runtime <RUNTIME> command-store
iotox --runtime <RUNTIME> command-record outgoing K EPOCH MESSAGE
```

For `device.describe`, terminal peer state is also projected under:

```text
<RUNTIME>/peers/K/iotox/description/
```

Every durable terminal result retains exact `result.frame`. Successful registered typed operations
also publish an operation-specific, human-readable `result` beside that frame under `commands/`.

## Security invariants

The daemon never follows the command path as a symlink and never accepts a regular-file
substitution. Discovery verifies type, effective-user ownership, mode, and opened inode. Separate
read-only and hold-writer descriptors avoid Linux-only `O_RDWR` FIFO semantics. The hold writer
prevents repeated EOF churn while external writers come and go; it does not create persistence.

A hostile process with the same Unix account can still write the FIFO and use the structured local
socket. Unix same-user admission is not IoTox remote authority. The daemon applies protocol session,
remote authority, capability, and durable command rules before a remote effect.

## Extension rule

Any later grammar extension must keep bounded canonical arguments, must not parse arbitrary shell
text, and must not bypass the operation registry. ADR 0148 freezes `profile.status.set` and ADR 0186
freezes exact-HEAD `update.stage`; both are non-expiring desired-state operations. Every additional
mutation requires its own effect-specific idempotency, expiry, restart, and cancellation decisions
before advertisement.
