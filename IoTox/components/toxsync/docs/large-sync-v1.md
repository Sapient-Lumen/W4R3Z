# Bounded v1 large-sync engine

## Two execution profiles

`toxsync-range-v1` now has two complementary implementations.

### Streaming aligned profile

Use for huge artifacts or strict memory ceilings.

- records remain encoded on disk;
- basis reuse is checked only at the target offset;
- missing ranges are coalesced within one bounded batch;
- range verification, write, and SHA-256 advance together;
- complete batches remain resumable in `.toxsync.part`;
- target size does not determine heap size.

### Adaptive/rolling profile

Use for smaller artifacts where shifted reuse is valuable.

- complete index is decoded;
- target-block lookup structures are built;
- the basis is scanned at arbitrary offsets;
- a complete plan is retained;
- memory grows with target block count.

The format is shared. A publisher does not need separate indices.

## Block-size selection

The encoded metadata is:

```text
64 + ceil(target_bytes / block_bytes) * 24
```

`choose_block_size` selects the smallest allowed block fitting the requested budget. Power-of-
two selection is the default because it simplifies batching, alignment, and scale reasoning.

A larger block reduces metadata and hash calls but makes a small modification fetch more
bytes. The metadata budget is therefore a ceiling, not necessarily the final performance
policy for every namespace.

## Working-memory accounting

`IndexFileBuildStats::peak_working_bytes` reports the project-owned data and record buffers.

`StreamingSyncStats::peak_working_bytes` reports:

```text
data batch
encoded index record batch
bit-packed reuse state
RangeRead descriptor capacity
```

It deliberately does not claim process RSS. Callers should measure process and whole-device
memory separately.

## Failure model

- malformed index headers or lengths fail before reconstruction;
- wrong block lengths fail while streaming records;
- wrong fetched bytes fail block verification;
- wrong complete output fails SHA-256 and removes the partial;
- a corrupt resume prefix is discarded;
- the final name changes only after verification and optional fsync;
- the source transport can throw/cancel without publishing an incomplete output.

## Limits

The aligned profile does not discover shifted blocks. A one-byte insertion can turn most of
the artifact into missing ranges. This is the principal v1 tradeoff and the most important
input to the v2 decision.
