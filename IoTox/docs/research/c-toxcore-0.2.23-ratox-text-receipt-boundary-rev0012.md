# Research note — c-toxcore text, ratox ordinary write, and receipt boundaries, rev0012

Date: 2026-08-14

## Question

How should a modern ratox successor expose ordinary per-peer human text while preserving exact
c-toxcore semantics, local path safety, and the distinction between chat, transport evidence, and
durable machine commands?

## Primary sources reviewed

Pinned official c-toxcore v0.2.23:

- public API header:
  <https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h>
- public wrapper implementation:
  <https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.c>
- messenger implementation:
  <https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/Messenger.c>
- protocol specification:
  <https://toktok.ltd/spec.html>

Ratox and Unix behavior:

- ratox source:
  <https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c>
- ratox README:
  <https://git.2f30.org/ratox/file/README.html>
- Linux `fifo(7)` and `pipe(7)`:
  <https://man7.org/linux/man-pages/man7/fifo.7.html> and
  <https://man7.org/linux/man-pages/man7/pipe.7.html>
- POSIX `write(3p)` and `fpathconf(3p)` as published by man7.org:
  <https://man7.org/linux/man-pages/man3/write.3p.html> and
  <https://man7.org/linux/man-pages/man3/fpathconf.3p.html>

These URLs preserve provenance. The pinned official source is the normative external target. No real
c-toxcore library or public Tox route was available in this cloudtainer during rev0012.

## Public text-send contract

The v0.2.23 header defines normal and action messages and a maximum body length of 1372 bytes.
`tox_friend_send_message` rejects:

```text
null input
missing friend
disconnected friend
full local send queue
oversized body
empty body
```

A successful call means the message was accepted into c-toxcore's local send queue. It is not remote
delivery, display, application processing, or IoTox authority.

The return value is a per-friend 32-bit message id. The documented first valid id is zero and later
ids increment with wraparound. Zero is therefore data, not an error or “unassigned” sentinel. A
separate friend-read-receipt callback reports receipt of the matching text message by the remote Tox
friend.

The same header requires serialized access to a `Tox*`. rev0012 keeps all message/action sends on the
existing owner thread; the FIFO worker never calls toxcore.

## Byte behavior and UTF-8 honesty

Two layers must not be conflated.

At the consumed C ABI, a message is a pointer plus explicit length. The v0.2.23 wrapper checks null,
empty, and size conditions, then delegates the span. The messenger implementation copies the bytes
into its packet; it does not validate UTF-8 before enqueueing. The rev0012 adapter is therefore
byte-preserving and need not rely on NUL termination.

At the protocol/product layer, Tox normal and action messages are human text and the protocol
specification describes them as UTF-8 byte strings. Interoperable IoTox human messages should be
valid UTF-8 even though the current core does not enforce that property. NUL, lone continuation
bytes, malformed UTF-8, or arbitrary binary may pass through the exact mock and current core path,
but behavior across real c-toxcore builds and other clients is not claimed until measured.

The product rule is consequently:

```text
local framing adapter: preserve every non-LF byte and report exact length
normal interoperability: emit valid UTF-8 human text
machine/binary data: use IoTox lossless custom packets or Tox file transfer
```

The stdin and hex client entrances remain useful for exact adapter tests, embedded LF, and typed
errors. They do not redefine Tox text as a general binary transport.

## Read-receipt lifetime ends at disconnect

The v0.2.23 messenger implementation retains outgoing text receipt records per friend while that
friend is online. When the friend connection leaves the online state, it clears the pending receipt
list. A later reconnect cannot produce those old receipt callbacks.

This matters because IoTox stores the normal/action kind keyed by:

```text
friend number + c-toxcore message id
```

The kind is needed to render a typed receipt event. Retaining this map across disconnect would leak
stale entries and could mis-correlate a future wrapped/reused message id. rev0012 now mirrors the
upstream lifetime:

```text
friend connection callback becomes NONE
    -> erase every pending text receipt-kind correlation for that friend
    -> emit one diagnostic with the abandoned count
    -> publish the ordinary friend-disconnected event
```

Friend deletion uses the same erasure helper. The exact ABI mock has a deterministic
`IOTOX_MOCK_TEXT_DISCONNECTS_BEFORE_RECEIPT` fault. The regression test sends a normal message,
delivers the incoming echo, disconnects before the receipt callback, clears the mock's pending
receipt list as upstream does, observes the IoTox diagnostic, and proves no receipt appears.

A missing receipt remains ambiguous. It can mean disconnect before receipt, process death, event
loss outside the required-event boundary, or simply that no receipt has arrived yet. It never means
that a machine command failed; text has no effect authority.

## Ratox findings

Ratox exposes a per-friend `text_in` FIFO and appends human-readable records to `text_out`. Its README
shows the intended experience directly:

```sh
echo yo dude > text_in
```

The source reads from `text_in`, removes a trailing LF in its usual path, sends a normal Tox message,
and immediately writes the local body to `text_out` with a `me` label. That immediate append is
elegant operator feedback, but it is not a remote receipt and does not preserve a typed send failure
as a separate event. Ratox does not project a distinct action-write lane.

The rev0012 inheritance keeps the ordinary write and strengthens the evidence model:

```text
message/action FIFO write
        -> local ingress acceptance or exact rejection
        -> c-toxcore local queue acceptance with exact message id
        -> optional remote read receipt before disconnect
```

It also keeps human text separate from the durable command path.

## FIFO findings

A FIFO pathname names a kernel pipe; bytes do not live in the filesystem. Read boundaries do not
retain writer boundaries. A complete record from one writer is protected against interleaving only
when it is emitted in one write no larger than `PIPE_BUF`.

rev0012 does not assume Linux's commonly observed 4096-byte value. After opening each FIFO, it
queries `_PC_PIPE_BUF` and refuses to monitor a lane unless 1373 bytes—the largest Tox text body plus
LF—fit atomically. This makes the writer rule executable rather than prose-only.

LF is the local adapter delimiter, not part of the message body. Every other byte is preserved at the
local framing and c-toxcore ABI boundaries. Structured stdin and hex commands remain available when
the body itself contains LF.

## Implementation consequences

```text
message and action are live lanes, not durable command lanes
no Tox text grants IoTox authority
no hidden offline retry exists
successful FIFO write is the weakest observation
message id zero has an explicit presence bit
exact toxcore failure classes survive into local evidence
receipt correlation is abandoned at friend disconnect
valid UTF-8 is the interoperable human-text contract
same C++ send path serves FIFO and structured client callers
```

The exact ABI mock also provides deterministic one-shot disconnected and SENDQ failures. The owned
test proves `not_found`, `unavailable`, `resource_exhausted`, and `invalid_argument` mappings and
proves that two failed sends do not consume the first valid message id zero.

## Defect found while generalizing the FIFO service

The status/event thread can observe the peer FIFO service pointer before `PeerFifoServer::start()`
finishes. The generalized three-lane service initially allocated per-lane counters only during
`start()`. A rapid repeated process run therefore found an out-of-bounds pre-start statistics read.

The correction establishes an explicit invariant:

```text
per-lane statistics storage exists from construction
pre-start count for every configured lane is zero
stats access remains bounds-checked
start resets counts but does not create their shape
```

A regression test calls aggregate and per-lane statistics before start. Twenty consecutive GCC
process starts/pings/stops and the separate-process lifecycle then passed. This is evidence for the
fix, not a claim that all concurrency faults are absent.

A second correctness cleanup gives peer-directory scan errors their own key instead of sharing lane
zero's key. Missing or repaired paths clear stale fingerprints. This prevents one structural fault
from suppressing a distinct lane error.

## Connection callback versus inventory snapshot

The final scheduling audit exposed a state-machine boundary adjacent to text receipt handling.
`tox_self_get_friend_list` answers which friend records exist; IoTox's transport adapter also retains
the most recently observed connection value for presentation. That copied list is level-triggered.
The friend-connection callback is the ordered transition evidence delivered from `tox_iterate`.

The public header says the connection getter equals the last callback value, deprecates that getter,
and directs clients to use the event and store the status. The current messenger implementation
compares its last TCP/UDP value with the newly observed value and emits the registered connection
callback when that presentation changes. IoTox therefore preserves a continuous nonzero connection
as one protocol epoch while updating its transport presentation.

The event pump and local-control server can both request a refresh. Before correction, each refresh
could apply the copied connection field to the session registry. One worker could collect `NONE`, a
newer callback could open the real epoch, and the first worker could then apply its old snapshot and
close it. The next online observation appeared to be a second epoch even though the mock emitted one
connection callback. Every individual container was mutex-protected; the semantic decision was
still stale.

The corrected division is:

```text
friend list snapshot     existence, key mapping, profile/presentation reconciliation
connection callback      sole online/offline epoch transition authority
```

Inventory collect/apply is serialized, but the stronger rule is that it never calls the session
registry's online/offline transitions. The exact integration and process fixtures require one
initial callback to remain epoch one under concurrent local inspection and injected HELLO queue
pressure. The exact Agent integration shard passed 100 consecutive executions after the correction.
The final queue-policy audit then found a second half of the same invariant: the bounded transport
queue had still listed `friend_connection` among observational events that may be discarded under
pressure. That was corrected so the edge is required and backpressured. A one-slot transport test
holds `friend_added` in the only slot and proves the online callback survives as the next event.
Real c-toxcore work must verify callback ordering across startup, TCP/UDP changes, rapid
disconnect/reconnect, saved friends, and simultaneous list requests. ADR 0044 freezes this evidence
hierarchy.

## Remaining research seam

Real c-toxcore must still verify:

```text
official-header source-linked compilation
valid UTF-8 and adversarial-byte behavior against real peers
message-id assignment and wrap behavior
receipt ordering and disconnect clearing
actual disconnected and SENDQ failures
reconnects and event ordering
native-route delivery and timing
cross-client normal/action rendering
```

The next ratox surface should use the same principle: preserve the ordinary operation, expose exact
evidence, mirror upstream lifetimes, and never imply stronger semantics than the underlying system
provides.
