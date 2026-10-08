# Rev0994 audit

Rev0994 replaces the shipping fixed-offset delta seam with one bounded content-defined implementation. A scalar allocation-free gear hash chooses canonical variable chunk boundaries between fixed minimum and maximum frontiers. One manifest is capped at 8,192 records and covers the exact 4 TiB payload frontier.

The payload store computes chunk and whole-file SHA-256 values from one descriptor-rooted observation. Reconciliation generation 6 publishes a complete manifest once to a cold receiver and exact constant-size references to valid continuations. The receiver indexes a causal predecessor by chunk digest, size, and cumulative offset, allowing unchanged chunks after an insertion or deletion to be reused at a different target offset. Every reused byte still enters the existing durable prefix and final whole-payload verification path.

The adjacent refactor removes the superseded fixed-block implementation and current assurance vocabulary instead of retaining two delta engines. Historical fixed-block design records remain provenance only. The slice remains bounded by file chunk count, not file bytes or tree size.

This revision does not claim measured multi-terabyte throughput or RSS, cross-file chunk discovery, multilevel chunking, compression, placeholders, Android support, rename/move identity, directory semantics, or ENOSPC qualification.
