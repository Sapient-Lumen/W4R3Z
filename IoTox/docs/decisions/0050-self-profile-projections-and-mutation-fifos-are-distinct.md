# ADR 0050 — self-profile projections and mutation FIFOs are distinct

Status: accepted  
Date: 2026-08-14

## Decision

The ordinary self-profile surface uses separate read projections and mutation FIFOs:

```text
self/name                 provider-confirmed bytes
self/status-message       provider-confirmed bytes
self/status               provider-confirmed available|away|busy text
self/name-set             private byte-line FIFO, 0..128 data bytes
self/status-message-set   private byte-line FIFO, 0..1007 data bytes
self/status-set           private printable FIFO, available|away|busy
```

One complete record, including its LF delimiter, must fit one `write(2)` within the FIFO's actual
`PIPE_BUF`. LF is framing and is not profile data. A lone LF clears name or status message.

The FIFO adapter translates into the same local control operations used by the one-binary CLI. Only
the serialized toxcore owner mutates the provider. Success is followed by savedata persistence,
provider readback, and atomic projection. Presentation fields never grant IoTox identity, ownership,
friendship, or capability authority.

## Rationale

A filesystem inode cannot honestly remain both a stable readable current-value file and a monitored
FIFO. Separate names preserve ordinary shell use while making direction and completion boundaries
explicit. The `-set` suffix also prevents a successful kernel write from being mistaken for the
new provider-confirmed value; readers observe the unsuffixed projection.

The existing hardened FIFO service supplies no-follow, owner, mode, opened-inode, record-bound,
partial-record expiry, rescan, and replacement checks. Profile mutation therefore gains no private
parser, queue, or provider path.

## Consequences

- Empty presentation values are representable without magic tokens.
- Newlines cannot be stored through the ordinary façade; binary values containing LF use the typed
  `profile-*-stdin`/local protocol entrance.
- Successful FIFO processing is persisted because the existing transport mutation seam saves state.
- Runtime projections can be safely replaced atomically without replacing ingress FIFOs.
