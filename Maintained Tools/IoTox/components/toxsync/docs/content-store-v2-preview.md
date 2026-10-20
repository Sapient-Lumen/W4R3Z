# Content store v2 preview

## Purpose

The v1 range engine is excellent when a receiver owns a mostly aligned older artifact. It
cannot deduplicate shifted content across many revisions or reconstruct from peers that each
hold only part of the target. The v2 preview explores the casync/desync-shaped alternative
without placing it on the v1 hot path.

## Format

An artifact is streamed through a deterministic Gear content-defined chunker. Each chunk is
named by SHA-256 and published under a two-level digest path. A manifest contains a 128-byte
header and 40-byte entries:

```text
entry = artifact offset + length + SHA-256 chunk identity
```

The header authenticates the complete artifact digest and the encoded entry stream. The
manifest itself is hashed and may be inserted into the same store, allowing a mutable HEAD
to name one immutable root object.

## Bounded memory

Build, scan, and reconstruction share one reusable arena:

```text
I/O buffer + maximum chunk buffer + manifest-record buffer
```

No operation constructs a vector proportional to chunk count. Inventory invokes a callback
for missing chunks in artifact order. Reconstruction opens and verifies one chunk at a time,
streams the complete artifact hash, and publishes through a private partial file.

## Metadata auto-scaling

A flat manifest has a real scale limit. Auto mode calculates the minimum chunk size from the
*worst case* implied by the chunker minimum, not merely the expected average. It raises the
minimum/average/maximum profile by powers of two until:

```text
128 + ceil(artifact_size / min_chunk_size) * 40 <= metadata budget
```

or rejects the profile when the configured maximum cannot satisfy the budget. This keeps
memory and wire metadata predictable but can reduce deduplication granularity for enormous
artifacts.

## Deliberately unfinished

The preview does not yet provide:

- a paged/Merkle manifest;
- network availability summaries;
- multi-source scheduling;
- chunk pins, reference counting, or garbage collection;
- a crash journal for partially downloaded chunks;
- signed namespace acceptance.

Those are v2 completion work, not hidden claims of rev0007.
