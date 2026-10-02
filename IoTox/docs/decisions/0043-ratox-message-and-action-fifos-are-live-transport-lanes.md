# ADR 0043 — Ratox-style `message` and `action` FIFOs are live transport lanes

- Status: accepted
- Revision: rev0012
- Date: 2026-08-14
- Extends ADR 0020, ADR 0021, ADR 0023, ADR 0040, and ADR 0042

## Context

Ratox makes human communication ordinary: write bytes to a peer FIFO and read an append-only peer
file. IoTox already owns the corresponding c-toxcore C++ path—normal/action sends, incoming
callbacks, outgoing message identifiers, and read receipts—but rev0011 exposed human text only
through structured one-binary commands.

The durable `command` FIFO cannot also be the human-text lane. Machine intent must be parsed,
authorized, signed, committed, deduplicated, and completed. A Tox text message is a live social
message. Treating one as the other would either grant text command authority or falsely promise
that chat is a durable execution queue.

The c-toxcore v0.2.23 text contract is bounded and precise:

```text
normal and action message kinds
1..1372 message bytes
per-friend message id; the first valid id is zero
local send-queue acceptance before delivery
friend read receipt after the remote peer receives the message
explicit errors for absent peer, disconnected peer, full send queue, empty, and too long
protocol-level human-text semantics are UTF-8 even though the current core copies bounded bytes
pending read-receipt entries are discarded when a friend disconnects
```

A named FIFO remains a byte stream. Its successful `write(2)` is not toxcore acceptance or remote
receipt. Multiple writers avoid record interleaving only when one complete record is emitted in one
write no larger than the FIFO's actual `PIPE_BUF`.

## Decision

Every projected Tox peer receives two private live text FIFOs:

```text
/run/iotox/peers/<UPPERCASE-TOX-PUBLIC-KEY>/message
/run/iotox/peers/<UPPERCASE-TOX-PUBLIC-KEY>/action
```

The lanes mean exactly:

```text
message   one c-toxcore normal text message
action    one c-toxcore action text message
```

Their record contract is:

```text
body:                  1..1372 bytes
framing delimiter:     one LF byte
recommended emission: one write containing body plus LF
atomic requirement:    body plus LF must fit the queried _PC_PIPE_BUF
adapter validation:    no UTF-8 validation; bytes are forwarded unchanged
interoperable meaning: valid UTF-8 human text under the Tox protocol
body preservation:     every non-LF byte, including NUL, CR, and high bytes
empty record:          rejected
embedded LF:           unavailable through this line-framed adapter
```

The daemon queries `_PC_PIPE_BUF` on each opened FIFO. A lane is not monitored if its complete
maximum record cannot fit one atomic write. The structured `message-stdin`, `action-stdin`,
`message-hex`, and `action-hex` commands remain the exact byte-oriented route for bodies containing
LF or for callers requiring a synchronous typed response. Their existence does not turn Tox text
into a general machine-data channel; custom packets and file transfer serve that purpose.

The generic peer FIFO service owns `command`, `message`, and `action` lanes, but lane policy remains
separate:

```text
command   printable operation record; enters the durable command engine
message   byte-preserving local line; enters live c-toxcore normal-text send
action    byte-preserving local line; enters live c-toxcore action send
```

A human-text FIFO write creates two distinct observation boundaries:

```text
message-events   transient local ingress acceptance/rejection and assigned message id
messages         transient transport journal: outgoing accepted, incoming, read receipt
```

`message-events` is evidence that the daemon framed the record and either obtained a c-toxcore
message id or received an exact typed failure. `messages` records transport lifecycle callbacks.
Neither journal is durable authority. Message id zero is represented with an explicit presence bit;
zero is never used as an “unassigned” sentinel.

The transport adapter maps c-toxcore text failures into stable IoTox status classes:

```text
FRIEND_NOT_FOUND       not_found
FRIEND_NOT_CONNECTED   unavailable
SENDQ                  resource_exhausted
NULL / TOO_LONG / EMPTY invalid_argument
unknown                library_error
```

No hidden retry is performed for live text. The caller may retry after inspecting the exact failure.
There is no offline spool, delivery timeout, application acknowledgement, or command authorization
attached to either lane. A read receipt is connection-ephemeral evidence: c-toxcore clears pending
receipt entries when the friend goes offline. IoTox clears the matching local message-kind
correlations on that callback and emits a diagnostic count rather than retaining stale state.

The FIFO service must retain the path-hardening, bounded framing, partial-record expiry, rescan, and
shutdown rules of ADR 0040. Its pre-start statistics are defined as zero for every configured lane;
observation of service state may race startup, but it must never read uninitialized lane storage.
Scan-error keys for peer directories and individual lanes are distinct so one fault cannot suppress
or overwrite another lane's evidence.

## Consequences

IoTox now has literal ordinary-write human communication without adding a second product binary or
bypassing the existing toxcore owner thread. A shell can say:

```sh
printf '%s\n' 'hello from the workshop' > peers/$PEER/message
printf '%s\n' 'waves'                   > peers/$PEER/action
```

and then inspect `message-events` and `messages` for increasingly strong evidence.

This surface deliberately does less than the durable command path. Offline or retrying human
messages require a future explicit queue contract rather than accidental FIFO buffering. Human text
never grants actuator authority, and a peer's Tox friendship never grants IoTox capabilities.

The original ratox names `text_in` and `text_out` are not adopted. `message` and `action` name the
write's semantic kind; `message-events` and `messages` distinguish local ingress from transport
lifecycle. A future compatibility view may add aliases only if it preserves these meanings.
