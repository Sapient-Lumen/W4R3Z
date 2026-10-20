# Durable command store v3

**Code:** `include/iotox/command_store.hpp`, `src/command_store.cpp`
**Magic:** `IOTXCMD3`
**Purpose:** bounded offline command admission, exact retry, and restart-safe lifecycle evidence

## Authority and integrity boundary

The stable IoTox device identity signs the canonical store. The Tox route identity does not. The
file is private, owner-checked, opened without following symlinks, bounded to 1,024 records and
8 MiB, and replaced through temporary-file `fsync`, rename, and parent-directory `fsync`.

The signature provides integrity and device binding. It does not provide confidentiality,
hardware-backed rollback resistance, multi-process writer coordination, remote consensus, or a
backup. The runtime `commands/` tree is a disposable projection; this store is authoritative.

All integers are unsigned big-endian. The 176-byte file header is:

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 8 | ASCII `IOTXCMD3` |
| 8 | 1 | format `3` |
| 9 | 1 | Ed25519 algorithm `1` |
| 10 | 2 | header bytes `176` |
| 12 | 4 | record count |
| 16 | 8 | generation |
| 24 | 8 | persistent local sender epoch |
| 32 | 4 | encoded body bytes |
| 36 | 4 | zero |
| 40 | 32 | stable device signing public key |
| 72 | 8 | clock high-water Unix milliseconds |
| 80 | 32 | zero |
| 112 | 64 | Ed25519 signature |
| 176 | variable | sorted record body |

The signature input is header bytes 0–111 followed immediately by the record body. Signature bytes
are not part of their own input.

## Durable identity and immutable intent

A local record is located by:

```text
direction
remote 32-byte Tox public key
sender epoch
message id
```

Direction prevents an incoming command from colliding with a locally originated command that has
the same wire epoch and message id. The canonical request, operation, creation time, priority,
clock requirement, and absolute expiry are immutable. Receipt, result, stable peer principal,
authority sequence, and ownership epoch become immutable when first assigned.

Each record begins with a 240-byte header:

| Offset | Bytes | Field |
|---:|---:|---|
| 0 | 4 | complete record bytes |
| 4 | 1 | record format `3` |
| 5–12 | 8 | direction, lifecycle, operation, outcome, receipt state, result state, priority, clock requirement |
| 13 | 3 | zero |
| 16 | 32 | remote Tox public key |
| 48 | 32 | stable peer principal, or zero |
| 80–144 | 9 × 8 | sender epoch, message ID, correlation ID, result message ID, ownership epoch, authority sequence, created, updated, expiry |
| 152 | 24 | request schedule |
| 176 | 24 | receipt schedule |
| 200 | 24 | result schedule |
| 224–232 | 3 × 4 | request, receipt, and result byte lengths |
| 236 | 4 | zero |
| 240 | variable | request bytes, then receipt bytes, then result bytes |

A 24-byte schedule is attempt count (4), typed error (2), zero (2), last-attempt time (8), and
next-attempt time (8). Records are strictly sorted by direction, peer key, sender epoch, and message
ID. Every embedded frame is decoded and re-encoded to prove canonical form during open and update.
Successful operation-specific evidence is also rebound during every open and mutation:
`profile.status.set` must prove the exact requested desired value, and `update.stage` must prove the
exact accepted HEAD carried by its frozen `ICQ2`. A validly signed store cannot substitute terminal
evidence from another command.

## Independent delivery lanes

Request, receipt, and result each persist:

```text
attempt count
last typed error
last attempt Unix milliseconds
next attempt Unix milliseconds
```

An attempt is committed before calling toxcore. A crash after that commit is therefore treated as
possibly peer-visible. Retries reuse the exact frozen frame bytes. Delay doubles from one second to
five minutes and adds stable 0–25% jitter derived from the durable key, lane, and attempt number.
Within a running process, due time advances from a steady-clock anchor rather than following wall
clock jumps. On an untrusted restart, that anchor resumes at the signed high-water timeline and
conservatively waits out any unproven remaining delay; trusted wall time may account for elapsed
offline time. Restart therefore cannot reset or accelerate untrusted retry state. An explicit
duplicate-request replay may bring a queued or otherwise blocked locally owned artifact back to
transport, but it never moves the already signed retry deadline backward.

Outgoing requests continue synchronizing until an exact application receipt or terminal result is
observed. A toxcore enqueue is not remote receipt. Locally owned receipt/result lanes stop automatic
retry once toxcore accepts the exact packet; an exact duplicate request is the explicit replay
trigger after that point.

## Admission, cancellation, expiry, and uncertainty

`iotox command` commits a request for an existing Tox public key even when that friend is offline.
The current protocol version is frozen in the request. The first transport attempt is delayed by
one second. During that window, and for any longer offline period, `iotox command-cancel` succeeds
only while the record is `reserved` with zero committed request attempts.

Once an attempt is committed, cancellation is refused because a crash or provider return cannot
prove that the peer did not observe the request.

Commands without expiry do not need wall-clock trust. A TTL is accepted only when the daemon was
started with `--trust-wall-clock` and the current clock has not rolled backward beyond the
configured tolerance relative to signed history. A trusted startup first checkpoints the current
time into the signed store, and monotonic elapsed time detects a backward step while the process is
running. With uncertain time:

- new local TTL admission is refused;
- existing outgoing expiring work is held without an attempt;
- incoming expiring work is durably received and acknowledged but not started;
- non-expiring work continues.

Mutating `profile.status.set` and `update.stage` records require zero expiry regardless of clock
trust. Their effect may be committed before a crash, so a later wall-clock deadline cannot produce
truthful cancellation.

With trusted time, expiry before the first attempt becomes `expired`. Expiry after any committed
attempt becomes `timed-out-unconfirmed`; IoTox does not manufacture a remote result. While retained,
an uncertain timeout may advance once to the exact authenticated peer result if it arrives late.
Cancellation and never-attempted expiry cannot. These are explicit local evidence classes, not
claims about remote cancellation.

## Scheduling and quotas

Ready work is ordered by high, normal, then low priority, followed by next-attempt time, creation
time, and durable key. Priority is local scheduling metadata and is not a wire flag.

Default unfinished limits are:

```text
256 records across the store
32 records per peer and direction
256 KiB canonical frame bytes per peer and direction
```

The absolute store limits remain 1,024 records and 8 MiB. Incoming terminal execution is still
unfinished retention work until both its receipt and result have entered the local Tox queue; it is
not prunable before then. Quotas are revalidated on open as well as mutation. Quota exhaustion and
file-write failure leave the previous signed memory/disk generation authoritative. No unfinished
record is evicted to admit new work.

## Shutdown and projection

Shutdown closes command admission before stopping local ingress and sets the event-pump stop gate
before transport teardown. No new retry is begun after that gate. Every attempt and transition was
already committed synchronously, so shutdown does not require a best-effort queue flush.

The runtime projection and `command-store`/`command-record` output expose priority, clock
requirement, expiry, every lane schedule, signed clock high-water mark, due-artifact count, and held
expiring count.

## v2 migration

On open, IoTox accepts only a correctly signed, private `IOTXCMD2` store belonging to the same
stable device identity. It strictly decodes v2 records, maps the aggregate legacy attempt evidence
conservatively into the owning delivery lane, derives expiry/clock requirement from the canonical
request, increments the generation, and atomically writes signed v3 before publishing the store or
starting transport. Migration persistence failure aborts startup. A v3 store is never silently
reinterpreted as v2.
