# Rev0996 audit

Rev0996 collapses sixteen default 4 MiB large-payload records into one authenticated 64 MiB response window while retaining one digest, one canonical content-defined manifest authority, chunk confinement, durable-prefix restart, and final whole-file SHA-256 verification. At the exact 4 TiB frontier, bounded turn arithmetic falls from 1,048,576 request/response turns to 65,536. This is exact limit arithmetic, not a measured 4 TiB transfer.

The adjacent refactor removes per-range pointer vectors from protocol validation and receiver grouping, performs one retained source-index lookup for the contiguous group, stops before opening a successor when the byte frontier is exhausted, and exposes window/range/byte counters through TLS and shipping JSON. The remaining measured boundary is resident memory: a configured 64 MiB response can exist with encoding, TLS, decode, and staging copies. Streaming or copy elimination must precede raising that frontier.

Rev0996 does not claim target-scale RSS, a completed multi-terabyte transfer, cross-file chunk discovery, Android support, rename/move identity, complete directory semantics, placeholders, quota safety, or ENOSPC qualification.
