# Runtime dreambank 007 — storage nucleus and object-substrate ambition

Revision: rev0028

## Dream statement

BrowserRT should treat storage as a runtime lane with object identity, provider boundaries, verifiable bytes, and explicit consistency claims.

The current browser proofs show OPFS can be reached. The missing piece is the runtime storage vocabulary that keeps OPFS, fake storage, Node filesystem tests, future journals, and future manifests coherent.

## New primitive pressure

This pass makes content-addressed block refs with explicit corruption detection the storage nucleus for cheap fake-provider tests and future OPFS provider proofs.


### Block ref

```ts
type RtBlockRef = {
  kind: 'block'
  id: string
  provider: string
  algorithm: 'sha256'
  digest: string
  bytes: number
  label: string
  createdAt: string
}
```

The block ref is the smallest durable-ish data-plane noun. It does not mean the bytes are actually durable. It means the bytes have a verifiable identity and a provider route.

### Storage provider

```ts
type RtStorageProvider = {
  id: string
  putBlock(key, bytes, metadata): Promise<PutResult>
  getBlock(key): Promise<Uint8Array>
  hasBlock(key): Promise<boolean>
  deleteBlock?(key): Promise<boolean>
  snapshot?(): ProviderSnapshot
}
```

Providers are not trusted. The block store verifies length and digest on read.

### Fake provider

The fake provider is not a toy. It is the first serious testing provider. It can inject failures, corrupt blocks, expose operation history, and act as the model-test target before OPFS work grows expensive.

## One-to-rule-them-all frontier

If BrowserRT eventually becomes the browser userspace kernel, storage is where everything meets:

- task outputs;
- trace recordings;
- replay fixtures;
- media frames;
- local app state;
- cache entries;
- vector/table segments;
- plugin artifacts;
- cross-tab coordination state.

That does not mean BrowserRT becomes all those products. It means BrowserRT owns the byte substrate underneath them.

## Design constraints

- Blocks are immutable from the runtime API's point of view.
- Every read of a block can verify digest and byte length.
- Provider failures are surfaced as provider failures, not swallowed.
- Durable claims wait for journal and recovery slices.
- Quota claims wait for quota-pressure slices.
- Cross-tab claims wait for Web Locks and multi-tab fixtures.
- OPFS sync-handle claims remain worker-scope only until handle pools and leader election are tested.

## Rev0011 concrete step

`storage:fake-block-store-proof` proves:

- same bytes produce the same block ref;
- read-after-write works in the fake provider;
- a deterministic command sequence matches a simple model;
- corrupt stored bytes are detected by digest verification;
- injected provider write failure is observable;
- provider operations and trace events are recorded.
