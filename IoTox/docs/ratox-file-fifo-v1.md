# IoTox ratox-successor finite-file façade v1

**Revision:** rev0013  
**Codename:** Ordinary Cargo  
**Status:** implemented against the owned C++20 manager and exact toxcore ABI mock; genuine c-toxcore network validation remains pending

## 1. Purpose

This document freezes the first ordinary filesystem entrance for Tox finite-file transfer.
It preserves ratox's central delight—name a peer, write an ordinary thing, observe ordinary
files—without claiming that a FIFO is a file stream, a durable queue, a completion receipt, or
authority to execute received content.

The v1 surface is intentionally path-based:

```text
peers/<TOX_PUBLIC_KEY>/file-send
peers/<TOX_PUBLIC_KEY>/file-receive
peers/<TOX_PUBLIC_KEY>/file-control
peers/<TOX_PUBLIC_KEY>/file-events
peers/<TOX_PUBLIC_KEY>/files/incoming/<FILE_NUMBER>/...
peers/<TOX_PUBLIC_KEY>/files/outgoing/<FILE_NUMBER>/...
```

The three ingress objects are private named pipes. The journal and projections are private regular
files/directories. File bytes do not cross any of the three FIFOs.

## 2. Non-goals

v1 does not provide:

- arbitrary streaming through `cat` into or out of a FIFO;
- a durable offline file spool;
- transfer continuation after an IoTox restart;
- path selection by the remote peer;
- overwrite of an existing destination;
- shell parsing, quoting, environment expansion, globbing, or relative paths;
- automatic execution, installation, extraction, import, or trust of received content;
- stable transfer handles after terminal cleanup;
- a complete historical transfer database;
- a claim that the mock proves real-network c-toxcore behavior.

These exclusions are product semantics, not temporary documentation omissions.

## 3. Common FIFO contract

A writer MUST issue exactly one complete record and its terminating LF in one `write(2)` call.
The LF is framing and is not part of the record. Embedded LF is not representable. NUL is rejected
by path decoding. An empty record is rejected.

IoTox opens each FIFO with mode `0600` inside a peer directory protected as `0700`. Before monitoring
a lane, the peer FIFO service checks that the configured maximum record plus LF fits the actual
`_PC_PIPE_BUF` reported for that FIFO. It refuses the lane rather than pretending multi-writer
atomicity when the platform cannot provide it.

A successful writer-side `write(2)` means only:

> The kernel admitted bytes to the FIFO.

It does not mean that IoTox parsed the record, opened a file, accepted an incoming offer, queued a
Tox control packet, transferred a byte, or completed the operation. `file-events` is the first
human-readable semantic observation surface.

Structured one-binary commands remain the escape hatch:

```text
iotox file-send FRIEND_NUMBER ABSOLUTE_PATH
iotox file-receive FRIEND_NUMBER FILE_NUMBER ABSOLUTE_PATH
iotox file-control FRIEND_NUMBER FILE_NUMBER pause|resume|cancel
```

The FIFO and structured commands converge on the same `FileTransferManager` and the same serialized
toxcore owner thread.

## 4. `file-send`

### 4.1 Grammar

```text
<absolute-source-path><LF>
```

The record may contain 1 through 4095 bytes excluding LF. The path is interpreted in the IoTox
process's mount namespace, effective-user context, and platform-native path encoding.

Example:

```sh
printf '%s\n' '/home/alice/archive.tar' > "$RUNTIME/peers/$KEY/file-send"
```

### 4.2 Admission

IoTox requires an absolute, lexically clean path. It opens the source with:

```text
O_RDONLY | O_CLOEXEC | O_NOFOLLOW
```

It then requires a finite regular file, a nonnegative size, a size no larger than the configured
finite-file limit, and a basename of 1 through toxcore's maximum filename bytes. The opened
descriptor—not a later pathname re-open—is retained for chunk service.

IoTox records the source device, inode, size, and modification time. Chunk service rejects a source
whose identity, size, or modification time changes under the transfer. This is mutation detection,
not a cryptographic content digest.

The manager asks toxcore to offer a data file, obtains the assigned friend-scoped file number and
file ID, and publishes the live outgoing projection. The accepted ingress event means:

> A finite source was opened and toxcore accepted the file offer.

It does not mean that the peer accepted the offer or received the file.

### 4.3 Remote filename

The transmitted filename is the local source basename. The remote filename is presentation data,
not a remote-controlled destination path. A receiver chooses its own absolute destination.

## 5. `file-receive`

### 5.1 Grammar

```text
<decimal-file-number><TAB><absolute-destination-path><LF>
```

The complete record may contain at most 4095 bytes excluding LF. The file number is canonical
unsigned decimal in the `uint32_t` range. Exactly one literal horizontal TAB separates it from the
path.

Example:

```sh
printf '7\t%s\n' '/home/alice/inbox/report.bin' > \
  "$RUNTIME/peers/$KEY/file-receive"
```

### 5.2 Offer gate

An incoming toxcore file request starts locally paused. IoTox records it as an `offered` transfer and
does not choose a destination. `file-control ... resume` is rejected while an offer has no admitted
destination; `file-receive` is the only v1 path admission operation.

### 5.3 Destination acquisition

IoTox requires:

- an absolute, lexically clean destination;
- an existing parent that is a real directory rather than a symlink;
- a parent owned by the IoTox effective user;
- no existing destination entry;
- an offer matching this peer and file number;
- configured receive capacity and size limits.

It creates a private temporary regular file in the destination directory, retains the descriptor,
and only then sends local `RESUME` through the toxcore owner thread.

A successful `file-receive` admission means exactly:

> IoTox acquired a private local destination and toxcore accepted the local RESUME control.

A tiny transfer may complete between that accepted control and the caller observing its result. The
manager therefore returns a frozen admission snapshot rather than converting successful admission
into a false `not found` failure.

### 5.4 Completion publication

Incoming chunks are written through the retained descriptor at the exact positions supplied by
toxcore. On terminal zero-length input, IoTox validates the final position, synchronizes the file,
closes the descriptor, and publishes without replacing an existing path:

```text
fsync(temp)
link(temp, destination)
unlink(temp)
fsync(destination parent)
```

The requested destination appearing is the authoritative ordinary-filesystem completion fact. A
journal line or a former live projection is not a substitute for that file.

If another local actor creates the destination before publication, IoTox fails closed and does not
overwrite it.

## 6. `file-control`

### 6.1 Grammar

```text
<decimal-file-number><TAB><pause|resume|cancel><LF>
```

The record may contain at most 17 bytes excluding LF. This upper bound covers the longest canonical
`uint32_t` decimal value, one TAB, and the longest action. The lane uses byte-line framing because
TAB is a required delimiter; the semantic parser still permits only decimal digits, one delimiter,
and one exact lowercase action.

Examples:

```sh
printf '7\tpause\n'  > "$RUNTIME/peers/$KEY/file-control"
printf '7\tresume\n' > "$RUNTIME/peers/$KEY/file-control"
printf '7\tcancel\n' > "$RUNTIME/peers/$KEY/file-control"
```

### 6.2 Pause truth

Tox file pause is two-sided. IoTox therefore stores:

```text
local-paused
peer-paused
```

The live state is `paused` when either bit is true and `active` only when both are false. A local
`RESUME` can clear only `local-paused`; it cannot erase a pause received from the peer. When both
parties paused, both must resume before transfer proceeds.

An unadmitted incoming offer remains `offered` even if the sender pauses or resumes it. Offer
admission and peer pause are independent facts.

The toxcore `file_recv_control` callback means a control received from the friend. A successful
local `tox_file_control()` call must not be synthesized into that callback. The exact ABI mock follows
this directionality.

### 6.3 Cancel truth

Cancellation is both a transport request and a local resource decision. Once locally requested,
IoTox releases retained descriptors and temporary files even when toxcore reports that the control
packet could not be queued. The structured caller receives the toxcore failure in that case; the
live transfer still disappears because local resources were intentionally abandoned.

## 7. File numbers and file IDs

A toxcore file number is scoped to one friend and may be reused after a transfer terminates. It is a
live control handle, not a durable object identity.

A toxcore file ID is 32 bytes and is exposed when available. Toxcore permits an application-provided
file ID to identify a transfer across restarts, but rev0013 does not persist enough live-transfer
state to resume an interrupted transfer. IoTox therefore treats the file ID as identity evidence,
not as a current restart-resume guarantee.

The pair `(peer public key, direction, file number)` identifies one live projection. Historical
systems must not key durable records by file number alone.

## 8. `file-events`

`file-events` is a bounded, append-only, human-readable journal with one previous-generation
rotation file. Its default rotation threshold is 1 MiB. It interleaves two evidence classes.

### 8.1 Local FIFO ingress

Local ingress lines include:

```text
source=local-fifo
ingress-sequence
operation
disposition=accepted|rejected
error-code
file-number
direction
state
size
position
local-paused
peer-paused
local-path
detail
```

An accepted line records the manager's exact returned snapshot. A rejected line records why bytes
accepted by the kernel did not become a file operation.

### 8.2 Toxcore/manager events

Transport lines include:

```text
source=toxcore
event
disposition=applied|rejected
friend-number
file-number
file-kind
file-size
file-position
requested-length
payload-bytes
file-control
file-id
filename
state
direction
local-paused
peer-paused
local-path
detail
```

File payload bytes are never printed. High-volume nonterminal chunk progress is intentionally kept
out of the peer journal; offers, controls, terminal indications, and manager failures are retained.
The global bounded low-level event journal samples successful nonterminal chunk metadata at most
once per 250 milliseconds. The manager still consumes every required toxcore event; failures and
terminal indications are never coalesced.

The journal is observational and disposable. It is not a signed transfer ledger and is not the
source of live state after restart.

## 9. Live `files/` projections

For every live transfer belonging to the peer, IoTox publishes one complete directory:

```text
files/incoming/<FILE_NUMBER>/
files/outgoing/<FILE_NUMBER>/
```

Fields are:

```text
direction
state
friend-number
file-number
kind
size
position
local-paused
peer-paused
file-id
filename-bytes
filename
local-path
detail
```

The `filename` file preserves raw filename bytes. Text fields escape values where necessary. Each
projection is assembled in a private temporary directory and renamed into place only after every
field exists. While bytes are flowing, the disposable progress projection is refreshed at most once
per 250 milliseconds; the structured `files` operation forces an exact manager snapshot. Terminal
transfer directories are removed; `file-events` carries bounded observational history.

An exact unchanged record whose real directory is still present is not rewritten merely because a
different transfer changed. New and changed records retain the full atomic replacement transaction;
terminal records are withdrawn immediately. This keeps concurrent transfer publication linear in
the number of actual changes rather than quadratic in the total live set.

A reader must regard disappearance as terminal/non-live truth, not necessarily as success.

## 10. Disconnect and restart

When the peer disconnects, the manager removes its live offers/transfers and releases local
resources. The v1 surface does not queue file transfer for later delivery.

On IoTox restart, live file transfers are not reconstructed. Partial private receive temporaries are
removed when known to the running manager, but crash-recovery scavenging and resumable transfer
journaling remain future work. A durable file-delivery feature must be designed as a separate
product contract rather than inferred from this façade.

## 11. Local trust boundary

The runtime tree is a same-UID operator surface. Processes able to write its FIFOs can ask IoTox to
read or create files available to the IoTox process. Private directory permissions reduce exposure
but do not isolate mutually hostile same-UID processes.

The current receive-parent validation uses pathname operations and ownership checks. A future
hardening gate should evaluate directory descriptors plus `openat2(2)`/`openat(2)` style resolution
constraints where supported, especially for privileged or container-crossing deployments.

## 12. Content and authority boundary

Tox authenticates a transport peer. The independent IoTox authority ledger governs machine
capabilities. File receipt alone grants neither.

Rev0013's ordinary file lane is operator-driven transport. It does not yet bind each file action to
an application capability or signed durable command. Before OTA, import, extraction, or physical
effect workflows exist, IoTox must add content hashes/signatures, target policy, size/storage
reservation, explicit authorization, and operation-specific completion semantics.

## 13. Evidence boundary

The owned C++ tests currently exercise:

- exact FIFO creation, modes, help, discovery, and `_PC_PIPE_BUF` gating;
- path record parsing and semantic rejection journaling;
- finite send/receive through the exact toxcore ABI mock;
- safe no-clobber publication;
- structured and FIFO control paths;
- independent local and peer pause state;
- the rule that local control success does not echo a remote-control callback;
- transfer projection publication and terminal removal;
- the separate-process one-binary lifecycle.

This proves owned semantics against the mock. It does not yet prove interoperability, timing, relay,
NAT, or real file behavior with c-toxcore 0.2.23 on a network.
