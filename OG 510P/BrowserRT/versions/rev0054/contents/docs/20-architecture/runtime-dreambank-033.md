# Runtime dreambank 033 — BrowserRT storage providers become real

Current revision: rev0054

The dream is a storage provider ladder where fake providers and real browser providers share enough contract shape that BrowserRT can move from model proofs to origin-local storage without losing testability.

## Provider ladder

```txt
memory-block-store
journaled-memory-block-store
persisted-spill-mailbox fake provider
storage-lane fake provider
opfs-async-block-store          <- rev0039 baby browser bridge
opfs-sync-worker-block-store
opfs-journaled-block-store
opfs-storage-lane-provider
opfs-spill-mailbox-provider
opfs-web-locks-coordinated-provider
```

## What must not be collapsed

- Async OPFS write/read is not sync access handle behavior.
- Page-reload readback is not crash recovery.
- Content-addressed blocks are not a journal.
- Storage estimate is not quota pressure testing.
- Temporary Chromium profile evidence is not cross-browser conformance.
- Browser provider proof is not storage-lane integration.

## Ambitious endgame

The long-term storage lane should choose a provider based on capability and policy:

```ts
const store = await rt.storage.open('workspace', {
  provider: 'opfs-preferred',
  durability: 'journaled-if-available',
  coordination: 'web-locks-if-available',
  quotaPolicy: 'admit-or-spill',
  recovery: 'manifest-plus-journal'
})
```

Rev0038 earns only the first browser block-store primitive needed for that future.
