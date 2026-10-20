# v2: content-defined and content-addressed

The v2 direction borrows the useful *system shape* of casync/desync: canonical artifacts are split with content-defined chunking, chunks are addressed by cryptographic digest, and a compact manifest reconstructs a revision.

Planned components:

```text
Chunker          rolling content-defined boundaries
ChunkDigest      SHA-256 or BLAKE3 content identity
ChunkStore       bounded local hash-addressed cache
Manifest         canonical ordered artifact recipe
Availability     compact peer/chunk summary
Scheduler        one-to-few bounded sources, retries, deadlines
GarbageCollector pin current/baseline/recent revisions under a byte budget
```

The v1 `RangeSource` remains useful for fetching manifests, complete small artifacts, and fallback repair. The public control plane still says: authenticated mutable head -> immutable revision description -> verified staging -> atomic activation.

v2 is warranted when artifacts are large, many revisions coexist, peers hold different subsets, moved data should deduplicate across revision boundaries, or true multi-source transfer materially improves completion time. Small configuration, chat-feed, and firmware-control namespaces should remain on the simpler v1 path unless measurements prove otherwise.
