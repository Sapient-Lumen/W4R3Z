# Rev1001 audit

Rev1001 replaces whole-candidate cross-file hashing in one reconciliation turn with a bounded, resumable content-defined projection. Each projection step drops its descriptor, then the next step reopens and re-proves the exact payload observation before continuing. Complete chunks become independently reusable before the candidate whole-file manifest is complete, while final target SHA-256 remains publication authority.

The adjacent refactor replaces per-chunk sorted insertion with append-then-sort once per bounded step and makes the service header declare its own algorithm dependency. The implementation does not introduce a durable unbounded chunk database or claim cross-process negative-cache invalidation.
