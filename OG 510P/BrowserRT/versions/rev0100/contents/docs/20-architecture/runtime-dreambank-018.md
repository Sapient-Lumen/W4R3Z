# Runtime dreambank 018 — persisted spill recovery as a queue-kernel primitive

Revision: rev0028

BrowserRT is trying to become a browser userspace kernel. A kernel cannot simply say “the queue spilled to storage” and stop there. It must define what survives, what replays, what is pending, what is acked, what is deleted, and what remains non-claim.

## Dream

A future BrowserRT mailbox provider could expose:

```txt
enqueue(frame) -> accepted | rejected | spilled | backpressure
dequeue(consumer) -> delivery
ack(delivery)
nack(delivery)
checkpoint()
recover(manifest, journal, provider)
compact(retentionPolicy)
```

The runtime would make the following visible in traces:

```txt
queue depth
pending delivery count
acked tombstones
journal sequence
checkpoint sequence
replay count
torn-tail handling
provider block count
retention/deletion decisions
```

## New primitive in this revision

`PersistedSpillMailbox` is a fake-provider persisted mailbox. It uses a block-store provider for payloads and a metadata journal for queue operations.

It proves the baby recovery law:

```txt
After checkpoint + valid journal replay, acked messages are not redelivered, pending messages are redelivered at least once, queued messages stay ordered, corrupt tails are ignored, corrupt manifests are rejected, and recovered payloads can be ack-deleted.
```

## Recovery ladder

1. Fake provider, deterministic journal, no browser.
2. Fake provider with model-walk operation generation.
3. Node filesystem provider with explicit crash fixtures.
4. OPFS async provider.
5. OPFS sync worker provider.
6. Multi-tab storage leader with Web Locks.
7. Retention and compaction.
8. Provider health and adaptive admission integrated with replay pressure.

## Why it matters

Without this rung, future OPFS work would spend browser budget while still arguing about semantics. Rev0023 lets future sessions test recovery rules cheaply before touching real browser storage.

## Non-claims

- No OPFS durability claim.
- No browser crash or restart proof.
- No exactly-once semantics.
- No multi-consumer claiming protocol.
- No retention compaction proof.
- No performance claim.
