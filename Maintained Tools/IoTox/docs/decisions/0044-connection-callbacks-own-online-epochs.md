# ADR 0044 — Required connection callbacks own online-epoch transitions

- Status: accepted
- Revision: rev0012
- Date: 2026-08-14
- Extends ADR 0015, ADR 0025, ADR 0028, and ADR 0029

## Context

IoTox has two ways to learn about a friend:

```text
list_friends() snapshot       level-triggered inventory and presentation state
friend-connection callback    required ordered transition event from tox_iterate
```

Both are collected on the serialized toxcore owner thread, but their consequences are applied by
separate IoTox workers. A local-control request can ask for a friend-list refresh while the event
pump is processing callbacks. The copied inventory snapshot can therefore be older than a callback
already queued or applied elsewhere. The pinned c-toxcore header deprecates the connection-status
getter in favor of storing callback state in the client; current `Messenger.c` also emits the
callback when its TCP/UDP presentation changes.

rev0012 testing exposed the concrete failure. An initial offline inventory snapshot and a newer
online callback raced. The stale snapshot was allowed to mark the protocol session offline after the
newer callback had opened it. The following online observation then appeared to be a second
reconnect epoch. That discarded the first epoch's frozen HELLO retry evidence and could invalidate
all transcript-, authority-, description-, and command state scoped to the real connection.

A mutex around the session registry cannot solve this semantic race. Each individual mutation can
be data-race-free while the decision itself is based on stale transport evidence.

## Decision

Only ordered `friend_connection_status` callbacks may call:

```text
PeerSessionRegistry::peer_online
PeerSessionRegistry::peer_offline
```

Friend inventory refresh is limited to:

```text
friend existence
friend-number to public-key projection
name, status message, presence, typing, and connection presentation
creation of an offline placeholder for a newly known friend
removal of sessions for friends no longer in the list
runtime publication and aggregate peer count
```

Inventory refresh must not infer an online/offline edge from its copied `connection_status` field.
The complete inventory collect/apply operation is serialized at the Agent layer so concurrent
callers cannot overwrite each other's public-key projection or remove a session from differently
aged friend lists.

The transport event queue treats friend-connection events as required semantic events. Their owner-
thread order is the epoch order. One `NONE -> TCP|UDP` callback opens exactly one new epoch. A
continuous TCP/UDP status change updates connection presentation without creating a new epoch. One
`TCP|UDP -> NONE` callback closes the epoch and clears per-epoch protocol and authority state.

“Required” is executable queue policy, not merely documentation. When the bounded event queue is
full, an incoming friend-connection edge may evict an older observational event or apply bounded
backpressure to the toxcore owner thread. It must never be counted as disposable evidence and
silently dropped. A one-slot regression keeps `friend_added` queued while the mock emits its online
callback, permits a consumer to win the scheduling race on an already-published observational
self/backend event, and then requires the connection edge to arrive before any later required friend
event. Queue scheduling is not allowed to masquerade as lifecycle order.

Tests require the first accepted friend connection to remain `online-epoch=1` while control and
event workers both refresh peer state. Injected first-HELLO `SENDQ` must remain visible as exactly two
send attempts in that same epoch: one rejected enqueue and one successful retry of the frozen record.
The separate-process fixture carries the same epoch assertion. After the correction, the exact Agent
integration shard passed 100 consecutive executions while preserving epoch one and exactly two HELLO
attempts.

## Consequences

A copied friend list remains useful for reconciliation and operator display, but it is no longer an
epoch clock. This prevents a stale level snapshot from manufacturing a reconnect and preserves the
canonical session transcript under concurrent local inspection.

The design depends on required connection-event delivery. Queue overflow, shutdown, or provider
behavior that can lose those callbacks is therefore a correctness failure, not a harmless stale
status condition. A future genuine-tox fixture must exercise rapid TCP/UDP changes, disconnect and
reconnect ordering, startup with saved friends, and list/callback disagreement.

This decision does not claim that the exact mock reproduces every c-toxcore timing. It freezes which
class of evidence is authoritative so real-provider corrections do not reintroduce snapshot-driven
epoch transitions.
