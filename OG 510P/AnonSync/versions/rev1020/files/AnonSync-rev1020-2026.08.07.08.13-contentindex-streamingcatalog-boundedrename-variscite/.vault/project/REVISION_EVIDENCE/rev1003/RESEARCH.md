# Rev1003 research notes

The immediate multi-terabyte risk was not the size of the retained chunk manifest but the synchronous same-path predecessor discovery path: one reconciliation apply could hash the complete old file before reusing any chunk. Rev1003 reuses the existing bounded content-defined projection machinery and retains only a process-local partial digest/offset index. This keeps the shipping change narrow and avoids introducing a second chunk grammar.

A restart-durable terminal-verification continuation remains open work. Persisting provider-specific SHA state next to a pathname is insufficient: the record must be checksum-framed, tied to the exact payload-store identity and inode observation, bounded, canonical, invalidated by any byte or metadata drift, and reconciled with final publication after crashes. Until that design exists, exact whole-target SHA-256 remains intentionally complete and non-resumable.

The next useful performance experiment is a durable, identity-bound chunk-manifest/index layer that can serve both predecessor and cross-file reuse after restart while remaining memory-bounded for multi-terabyte trees. It must preserve the current payload-before-metadata and terminal digest fences.
