# Runtime dreambank 006 — the storage gatekeeper and the local kernel fantasy

Revision: rev0028

## New dream

BrowserRT becomes the **storage gatekeeper** for heavy browser apps. Apps do not
spray writes directly across IndexedDB, OPFS async streams, OPFS sync handles,
Cache Storage, Storage Buckets, or future providers. They ask BrowserRT for a
provider, a lease, a bounded channel, and a traceable object ref.

The absurd endgame is:

```txt
BrowserRT storage lane
  accepts request records
  routes to async OPFS / sync worker OPFS / memory / future bucket / future user-file provider
  leases exclusive handles
  emits completion records
  tracks quota and cleanup
  journals manifests
  coordinates tabs through locks
  replays traces in fake-provider simulation
```

That sounds too large for rev0025. The rev0025 move is tiny: prove the worker-only
sync handle surface and document how it should fit.

## What the one-to-rule-them-all runtime could become

### 1. Provider matrix

A future runtime could expose:

```ts
const provider = await rt.storage.provider('opfs-sync-worker', {
  durability: 'best-effort',
  access: 'exclusive-lease',
  quotaClass: 'origin-private'
})
```

Providers describe capabilities instead of forcing every app to hand-code
feature detection.

### 2. Request/completion queues

Storage work becomes a lane with records:

```txt
request: put block X at path P, bytes B, deadline D
completion: wrote N bytes, flushed yes/no, digest H, ref R
```

This is the browser-kernel version of asynchronous I/O: explicit request,
explicit completion, bounded queue, and trace.

### 3. Leased sync handles

Sync access handles should never leak into arbitrary app code. The future shape:

```ts
await rt.storage.withExclusiveFile(path, async (lease) => {
  lease.write(bytes, { at: 0 })
  lease.flush()
})
```

The runtime owns open/close, timeout, cancellation, trace, and cleanup policy.

### 4. Durable-ish local actors

BrowserRT could eventually host local actors with private OPFS-backed state:

```txt
actor id -> activation -> private state provider -> serial turns -> trace -> hibernate
```

This steals from Durable Objects, Orleans, Dapr Actors, and Durable Task without
pretending that a browser tab is a cloud cluster.

### 5. Fake-provider simulation before browser complexity

Before multi-tab storage and recovery get real, BrowserRT should create fake
providers that can deterministically reorder completions, inject failures, deny
flushes, drop locks, and simulate quota pressure. This is the browser-scale
version of the FoundationDB/Antithesis lesson: test the model before trusting the
real substrate.

## Ambition fences

- OPFS sync handle proof is not a block store.
- OPFS sync handle proof is not a durability proof.
- OPFS sync handle proof is not a performance proof.
- OPFS sync handle proof is not cross-browser conformance.
- Storage buckets, Web Locks, multi-tab coordination, and journal recovery remain
  separate future slices.

## New primitive pressure

Rev0010 adds pressure for these eventual primitives:

```txt
RtStorageProvider
RtStorageRequest
RtStorageCompletion
RtFileLease
RtDurabilityClaim
RtQuotaObservation
RtStorageCleanupPolicy
RtStorageSimulationProvider
```

Do not build all of them yet. Name them now so future work lands in coherent
places.

## Provider variant pressure

The OPFS sync Worker proof should be treated as one provider variant, not the storage lane itself. Future variants include async OPFS, sync-worker OPFS, memory fake-provider, journaled block provider, quota-pressure fake-provider, and cross-tab lock provider. The current manifest task is `browser:opfs-sync-worker-proof`.
