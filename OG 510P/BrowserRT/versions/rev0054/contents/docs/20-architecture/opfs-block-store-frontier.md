# OPFS async block-store frontier

Current revision: rev0054

`OpfsAsyncBlockStore` is a browser-window async OPFS content-addressed block-store provider.

## Earned in rev0039

- `put(bytes)` stores a block at a SHA-256-derived OPFS path.
- Duplicate puts are detected and traced.
- `get(ref)` reads the file and verifies the checksum.
- `has(ref)`, `verify(ref)`, and `delete(ref)` exist.
- `estimate()` records the browser storage estimate if available.
- `cleanupForTest()` removes the test prefix.
- The browser proof does page-reload readback in one temporary Chromium profile.

## Provider contract shape

```txt
content bytes -> sha256 digest -> block ref -> OPFS path
```

The provider emits trace events:

```txt
storage:opfs-blockstore-create
storage:opfs-blockstore-open
storage:opfs-block-put
storage:opfs-block-get
storage:opfs-block-has
storage:opfs-block-delete
storage:opfs-block-estimate
storage:opfs-block-cleanup
```

## Why this exists now

The cube has many fake-provider storage/scheduler/resilience proofs. This slice prevents the project from becoming purely theoretical while preserving the fake-provider-first testing strategy.

## Non-claims

- Not a durability claim.
- Not an fsync/flush guarantee.
- Not a quota pressure or eviction proof.
- Not a crash-recovery or browser restart proof.
- Not a multi-tab concurrency proof.
- Not an OPFS sync access handle proof.
- Not storage-lane provider integration.
- Not a throughput or latency benchmark.

Current proof id: `browser:opfs-block-store-proof`.
