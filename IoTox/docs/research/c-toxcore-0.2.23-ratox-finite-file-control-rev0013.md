# Research note — c-toxcore 0.2.23 and ratox finite-file control, rev0013

- Retrieved: 2026-08-14
- IoTox revision: rev0013
- Method: read pinned public header and implementation plus ratox source
- Evidence class: upstream source contract and implementation reading; no official library executed

## Primary sources

```text
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.c
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/Messenger.c
https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/Messenger.h
https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c
https://github.com/pranomostro/ratox
https://raw.githubusercontent.com/JFreegman/toxic/v0.16.3/src/file_transfers.c
```

The c-toxcore tag is the version pinned by `dependencies.lock`. Ratox master is read as design and
compatibility history, not as a provider contract.

## Public c-toxcore contract

### One Tox instance must be serialized

`tox.h` states that no more than one API function may operate on one `Tox` instance at a time. IoTox
therefore keeps every file send, control, chunk answer, callback, and savedata action on the one
transport owner thread. A filesystem FIFO handler never calls c-toxcore directly.

### File numbers are friend-specific and reusable

`tox_file_send` returns a friend-specific file number. The public header explicitly says that any
pattern in file numbers must not be relied on. Zero-length terminal chunk callbacks release the
number for future reuse.

IoTox therefore keys live transfers by friend number plus the full `uint32_t` file number. It does
not persist the number as globally unique identity and it does not derive business meaning from the
numeric pattern.

### Incoming offers begin paused

The `tox_file_recv_cb` contract says the client should acquire resources and that incoming transfers
start PAUSED. The client accepts with RESUME or rejects with CANCEL. This supports IoTox's ordering:

```text
validate local destination
create private same-directory temporary file
install receiver state
send RESUME
```

Generic `file-control ... resume` is unsafe for a still-pending offer because it has not selected or
secured a destination. The file FIFO therefore requires `file-receive` for first acceptance.

### Pause belongs to both sides

The `Tox_File_Control` documentation says the sending and receiving sides can each pause; if both
pause, both must resume. The error enum distinguishes not-paused, peer-owned pause denial, and
already-paused conditions.

IoTox records `local_paused` and `peer_paused` independently. A local RESUME cannot erase peer-owned
pause evidence.

### File-control callbacks are peer-originated evidence

The public `tox_callback_file_recv_control` contract says the event fires when a control is received
from a friend. A successful local `tox_file_control()` call is not echoed through that callback.
rev0013 corrected the exact ABI mock so local control changes local-owned state directly and only a
peer-originated callback changes peer-owned state.

### Chunk service is exact

For outgoing files, `file_chunk_request` supplies the position and exact requested length. The
client must answer the full requested length. A failed send can cause the same or previous chunk to
be requested again, and that can happen repeatedly. IoTox uses positional reads from a finite regular
file instead of consuming an unrecoverable FIFO stream.

A zero-length request terminates outgoing resources. For incoming data, a zero-length chunk
terminates receiver resources. A known-size incoming transfer is complete only when terminal
position equals the advertised size. IoTox then syncs and publishes its staged file atomically.

### Disconnect is terminal for live transfers

c-toxcore's transfer state belongs to a live friend connection. Current implementation clears file
transfer slots when the friend goes offline. IoTox does not claim transfer durability across
disconnect or daemon restart. A later resumable object protocol would require its own stable identity,
integrity, and checkpoint semantics above file transfer.

## Implementation reading: direction encoding

The public API says file-number patterns are opaque. The pinned `Messenger.c` implementation
currently distinguishes direction as follows:

```text
outgoing slot j -> file number j, below 1 << 16
incoming slot j -> file number (j + 1) << 16, at least 65536
```

Control and seek routines decode the same complete handle. This explains why an incoming offer in
the exact mock uses 65536 and why one local `file-control` grammar can pass the full handle without a
separate direction token.

This is an implementation observation, not an IoTox wire or storage contract. IoTox preserves the
number exactly and must continue to work if a compatible provider changes the pattern.

The implementation also bounds concurrent transfer slots per friend and direction to 256. IoTox's
own defaults are lower (32 active sends, 32 active receives, 256 pending offers) to impose explicit
product backpressure before provider exhaustion.

## Maintained-client reading

Toxic 0.16.3 keeps explicit sender/receiver transfer objects, closes retained local resources, may
send CANCEL, reports provider failure, and clears terminal state. It reinforces direction and cleanup
as client responsibilities. It is a useful maintained implementation reference, not the IoTox
product architecture.

## Ratox reading

Ratox projects per-friend `file_in`, `file_out`, and `file_pending`. It reads bytes from `file_in` as
an outgoing stream, writes incoming bytes to `file_out`, and uses opening/closing behavior as part of
acceptance and cancellation. This is elegant for pipelines, SSH-like tunnels, audio/video-like
streams, and shell composition.

The same design lacks an intrinsic finite local destination, durable admission record, no-clobber
publication boundary, or restart semantics. A named pipe can close mid-stream and cannot answer a
provider seek-back after consumed bytes have disappeared unless the client retains its own chunk
history.

## rev0013 conclusion

The modern ratox successor should preserve **ordinary files and one-write control**, not necessarily
ratox's exact byte-stream contract.

rev0013 therefore makes the peer-local FIFO name one finite local file operation and leaves exact
chunk, pause, completion, and safe publication semantics inside the typed C++ manager. This is a
product decision informed by ratox and the pinned provider; it is not a claim that ratox itself was
wrong for its purpose.

## Unproved questions

The exact ABI mock proves IoTox's consumed calls and callback ordering only. A source-linked or
system-linked official c-toxcore run must still measure:

- real offer and callback ordering across two peers;
- peer pause/resume combinations and provider error values;
- chunk sizes, repeated requests, queue pressure, and completion timing;
- simultaneous incoming/outgoing file-number behavior;
- disconnect cleanup and file-number reuse;
- interoperability with other Tox clients;
- bootstrap, relay, NAT, and public-network behavior.
