# Rev1013 audit

Rev1013 removes the cache-cold generation-9 manifest's remaining per-digest heap ownership. Protocol, compact cache, and durable checkpoint now share one strict 32-byte `Sha256DigestValue`; each maximum 8,192-chunk receive, compact construction, compact copy, and wire materialization performs one 327,680-byte vector allocation. Compared with rev1012's cache-cold publication shape, that removes 8,192 allocator calls and 532,480 requested bytes while preserving exact generation-9 wire bytes and checkpoint-v2 durable bytes.

The adjacent refactor deleted three separately maintained digest validators and made malformed text construction or assignment fail without changing an existing value. The integration review also corrected two service call sites that had relied on implicit string conversion and replaced a stale historical lexical audit with the actual allocation-free comparison boundary.

This is a bounded one-manifest allocation-shape correction. It does not remove the remaining 327,680-byte O(chunk-count) sequence, reduce cold source hashing, prove whole-process multi-terabyte RSS, solve page-cache or allocator fragmentation, add a global or multi-source chunk index, settle ENOSPC, or complete Android, rename/move, directory, conflict, placeholder, or live-route qualification work.
