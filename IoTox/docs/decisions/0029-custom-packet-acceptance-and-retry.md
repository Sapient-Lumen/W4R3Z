# ADR 0029: Retry only custom packets that toxcore did not accept

**Status:** accepted and implemented in rev0008

## Context

IoTox carries its machine protocol in c-toxcore lossless custom packets. The public c-toxcore
0.2.23 contract describes successful lossless packets as reliable, ordered, and packet-framed.
It also exposes distinct failures for an unknown friend, an offline friend, invalid packet
shape, an empty or oversized packet, and `TOX_ERR_FRIEND_CUSTOM_PACKET_SENDQ` when the packet
queue is full.

The distinction matters. Retrying a packet that toxcore already accepted may create an
application duplicate. Never retrying a packet that toxcore explicitly rejected can strand a
session during ordinary queue pressure or an online-state race. Handshake messages are
especially sensitive because a retry must not create a second logical transcript.

The upstream header says only that `SENDQ` means “packet queue is full.” It does not prescribe
an application retry schedule. The cadence below is therefore an IoTox policy derived from the
public success/failure boundary and must be measured against real c-toxcore later.

## Decision

IoTox assigns every custom-packet send result to one of three classes:

```text
accepted by toxcore
    true return / OK
    ownership of transport reliability passes to toxcore
    IoTox does not resend merely because no application reply has appeared

transiently not accepted
    SENDQ -> resource_exhausted
    FRIEND_NOT_CONNECTED -> unavailable
    the exact unsent protocol record may be retried while its online epoch remains valid

terminal local failure
    FRIEND_NOT_FOUND -> not_found
    NULL / INVALID / EMPTY / TOO_LONG -> invalid_argument
    unknown error -> library_error
    no automatic retry loop
```

For HELLO and CAPABILITIES, the logical record is created once per online epoch before the
first send attempt. Every transient retry reuses:

```text
the same frame bytes
the same message ID
the same correlation ID
the same sequence number
the same HELLO or confirmation payload
the same session nonce and negotiated transcript
```

A successful enqueue marks the record sent and clears the last transient error. A later lack
of peer response does not cause a timer-based retransmission. An explicit operator resend is
idempotent and still uses the frozen epoch record.

The agent services transiently failed protocol records from its normal event-pump path after
later toxcore iterations, currently on a bounded 500 ms best-effort cadence. A real offline
callback closes the epoch. Reconnection creates a new nonce, new IDs, and new canonical
records; an old record is never carried into a new epoch.

Per-peer runtime state exposes send-attempt counters and the most recent error class/message
while an error remains. Expected queue pressure stays local to the peer session and does not
masquerade as a global daemon failure. The runtime projection removes the last-error fields
after a successful enqueue but retains the attempt count as evidence of recovery.

## Consequences

IoTox has one explicit handoff point: before acceptance, IoTox may retry the frozen record;
after acceptance, toxcore owns reliable ordered delivery. This avoids both silent handshake
loss under local pressure and blind duplicate traffic above a reliable packet lane.

The exact ABI mock can reject HELLO and CAPABILITIES independently with one synthetic `SENDQ`.
The agent test requires two attempts for each record, no residual last-error field, one
accepted outgoing journal record of each type, and a final confirmed session. The transport
test separately verifies the owned `resource_exhausted` mapping.

This decision does not claim that 500 ms is the optimal real-network cadence, that every
`FRIEND_NOT_CONNECTED` result is transient, or that a real toxcore queue always drains after a
single iteration. Those are measurement questions for the source-linked and genuine-peer
fixtures. Changing the retry class or cadence after measurement requires a superseding ADR or
an explicit amendment to this one.
