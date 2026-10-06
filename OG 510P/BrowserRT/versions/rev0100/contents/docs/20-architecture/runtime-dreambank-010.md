# Runtime dreambank 010 — the browser mailbox nervous system

Revision: rev0028

## The bigger guess

The BrowserRT shared-memory lane could become the browser's local message bus,
but only if it avoids becoming one clever queue. The useful abstraction is a
mailbox provider family with explicit resource contracts.

A future app should be able to say:

```ts
const mailbox = await rt.mailbox.open('decode-to-index', {
  provider: 'sab-spsc-frame-or-transfer',
  capacityBytes: 8 * MiB,
  overflow: 'backpressure',
  producer: 'main-or-worker',
  consumer: 'worker',
  trace: true
})
```

Then BrowserRT chooses a provider based on capability, calibration, and policy.

## Provider contract sketch

```ts
type MailboxProvider = {
  id: string
  tier: 'basic' | 'workered' | 'isolated' | 'persistent' | 'mesh'
  dataPlane: 'clone' | 'transfer' | 'shared' | 'stream' | 'opfs-ref'
  producerCount: 'one' | 'many'
  consumerCount: 'one' | 'many'
  frameShape: 'object' | 'fixed-int32' | 'binary-frame' | 'object-ref'
  blockingPolicy: 'none' | 'worker-only-wait' | 'async-wait'
  overflow: 'fail' | 'wait' | 'drop-oldest' | 'drop-newest' | 'spill-to-opfs'
  traceKinds: string[]
  nonClaims: string[]
}
```

## Stolen design pressure

- From Disruptor: sequence and consumer progress are first-class; wraparound is
  evidence, not an implementation accident.
- From Aeron: buffers, flow control, and application message boundaries should
  stay distinct.
- From Reactive Streams: backpressure is part of the protocol.
- From Durable Objects: named coordination owners are valuable; BrowserRT may
  eventually have local coordination objects with private state and ordered
  methods.
- From Wasm threads: raw offsets, byte lengths, and shared memory should remain
  compatible with future Wasm adapters.

## Current provider ladder

```txt
1. clone-mailbox: structured clone, control plane only.
2. transfer-mailbox: transferable ArrayBuffer, one-owner data plane.
3. sab-spsc-int32-node: fixed Int32 ring, Node worker_threads proof.
4. sab-spsc-int32-browser-worker: fixed Int32 ring, browser Worker proof.
5. sab-spsc-frame: variable binary frames.
6. sab-mpsc-command: many producers, one owner.
7. opfs-spill-mailbox: bounded in-memory queue plus OPFS data refs.
8. mesh-mailbox: same-origin tabs and workers as a local cluster.
```

Rev0014 only reaches rung 4.

## Design rule added by rev0025

A shared-memory provider may be fast, but it must never be silent. Every mailbox
provider needs trace events for create/open/full/wait/push/pop/close/result,
plus a clear statement of whether it blocks, drops, waits, spills, or fails.

## Current concrete slice

The named testing slice for this rung is `browser:sab-ring-worker-proof`; it proves only the fixed Int32 SPSC browser Worker ring and nothing broader.
