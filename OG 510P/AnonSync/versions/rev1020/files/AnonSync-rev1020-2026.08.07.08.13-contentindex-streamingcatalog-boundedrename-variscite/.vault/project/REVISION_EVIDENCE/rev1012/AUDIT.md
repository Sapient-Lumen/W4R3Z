# Rev1012 audit

Rev1012 replaces the completed source cache's string-backed generation-9 manifest and separate offset vector with one 40-byte cumulative-end/fixed-digest record per chunk. At the 8,192-chunk frontier, retained allocation shape falls from 8,194 requests / 925,704 requested bytes to one 327,680-byte vector allocation. Exact generation-9 wire materialization remains transient and byte-equivalent.

The adjacent review also removed per-range diagnostic-string construction from valid numeric chunk lookup. The maximum numeric lookup sweep performs zero allocations while retaining exact boundary semantics. Successful chunk-parameter validation likewise constructs diagnostics only on failure.

This is one-source O(chunk count) cache compaction, not solved whole-process multi-terabyte RSS, cold hashing, page-cache pressure, global indexing, Android, rename/move identity, directory semantics, conflicts, ENOSPC policy, retention collection, or public Tor/I2P qualification.
