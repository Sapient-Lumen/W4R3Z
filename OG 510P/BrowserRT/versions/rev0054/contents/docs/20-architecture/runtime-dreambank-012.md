# Runtime dreambank 012: BrowserRT as a model-oracled provider kernel

Revision: rev0028

The "one runtime" dream gets more plausible if each provider grows beside an executable model. BrowserRT should not merely provide fast paths; it should provide a way to know whether a fast path still means the same thing after optimization.

## Provider + model + history

A future BrowserRT provider should be describable like this:

```ts
type ProviderContract = {
  name: string
  provider: unknown
  referenceModel: unknown
  commandGenerator: unknown
  historySchema: unknown
  checker: unknown
  traceProjection: unknown
}
```

The point is not to create a giant testing framework immediately. The point is to make each subsystem ask:

```txt
what is the small model?
what are the commands?
what are the invariants?
what is a useful counterexample?
what trace events prove the path taken?
```

## Mailbox command vocabulary

The new manifest slice is `ipc:sab-frame-model-proof`. The SPSC frame ring now has an initial command vocabulary:

```txt
push(payload)
pop()
oversizePush(payload)
snapshot()
close()
pushAfterClose(payload)
drainAfterClose()
```

The real implementation has byte padding, wrap sentinels, counters, and shared-memory data. The model has a FIFO list. Agreement means:

- accepted push appends exactly one model frame;
- rejected push does not mutate model length or ring counts;
- pop returns the oldest accepted frame;
- empty pop never invents a frame;
- close prevents later push;
- close still allows draining pending frames;
- final state has no pending bytes.

## Why this belongs in the architecture

BrowserRT wants to coordinate storage, memory, workers, GPU, render, media, and cross-tab agents. That means the architecture will be full of provider variants and fallback paths. If there is no executable reference model, fallbacks can subtly diverge.

The long-term ambition is:

```txt
fast provider implementation
  must behave like
small reference model
  under
seeded commands + selected interleavings + trace history checks
```

## Future model labs

Potential model labs:

- `model:bounded-channel`: overflow policy and wait queues.
- `model:sab-frame-ring`: SPSC FIFO frame semantics.
- `model:journal-store`: checkpoint/replay/torn-tail behavior.
- `model:storage-leader`: Web Locks ownership and failover.
- `model:scheduler`: priority, deadlines, cancellation, resource leases.
- `model:supervisor`: restart limits and pending-call failure.
- `model:gpu-fallback`: CPU/GPU provider choice without semantic drift.

## Non-claims

The current model walk is deterministic and single-threaded. It does not explore all possible interleavings, browser Worker behavior, memory-model reorderings, MPSC/MPMC algorithms, or performance. It is the cheap semantic guardrail before those more expensive proofs.
