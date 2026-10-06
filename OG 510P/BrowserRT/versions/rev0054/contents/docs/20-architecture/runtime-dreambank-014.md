# Runtime dreambank 014 — spill-aware flow-control kernel

Revision: rev0028

## Dream

BrowserRT should eventually make this a normal runtime operation:

```ts
const mailbox = await rt.mailbox.frameStream({
  memoryBytes: 8 * MiB,
  spill: 'opfs-or-fake',
  highWatermarkBytes: 6 * MiB,
  lowWatermarkBytes: 2 * MiB,
  retention: 'ack-delete',
  delivery: 'at-least-once-until-ack'
})
```

An app should not invent its own “buffer, maybe write files, maybe retry, maybe delete” loop every time it needs bounded flow. BrowserRT should own that policy surface.

## New runtime noun

```txt
SpillFrameMailbox
```

A `SpillFrameMailbox` is a bounded frame queue with two tiers:

1. **hot memory tier** for low-latency small backlog;
2. **cold provider tier** for overflow frames.

The provider tier can initially be fake memory, then OPFS, then journaled OPFS, then maybe mesh/network providers.

## Provider ladder

```txt
fake-memory-provider
node-fs-provider
opfs-async-provider
opfs-sync-worker-provider
journaled-opfs-provider
mesh-provider
```

The runtime-facing contract should stay stable while providers change.

## Snapshot shape

A mailbox snapshot should eventually include:

```ts
{
  queueDepth,
  pendingCount,
  memoryUsed,
  memoryCapacityBytes,
  spillBytes,
  spillBlockCount,
  highWatermarkCrossed,
  providerHealth,
  oldestPendingAgeMs,
  stats
}
```

This is scheduling data, not just debugging output.

## Trace shape

rev0025 introduces trace pressure around:

```txt
mailbox:spill-create
mailbox:enqueue-memory
mailbox:spill-write
mailbox:spill-reject
mailbox:dequeue
mailbox:ack
mailbox:pending-reclaim
```

Future revisions should add watermarks, replay, compaction, expiration, and provider health events.

## Why this belongs in BrowserRT

Spill mailboxes cross the exact boundaries BrowserRT is supposed to coordinate:

- IPC/data-plane objects;
- storage provider admission;
- backpressure and rejection;
- trace evidence;
- scheduler pressure;
- replay and recovery semantics.

That makes them runtime infrastructure, not app glue.

## Non-goal for this revision

No OPFS implementation enters here. The fake-provider proof is the semantic scaffold.
