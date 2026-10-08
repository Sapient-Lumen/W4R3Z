# Rev1019 audit

Rev1019 adds one conservative causal identity continuation for regular-file rename/move. Destination File and source Tombstone publish atomically inside the replica database, the matching catalog pair publishes atomically inside the catalog database, and the existing immutable payload is reused. Restart recovers identity from ordinary retained operations. Duplicate-content ambiguity falls back to create/delete.

The adjacent audit found that the final SQLite uniqueness scan could infer uniqueness from a damaged current-visible projection if a duplicate row vanished. The same streaming scan now validates canonical rows and recomputes the complete visible-path count and accumulator digest before either operation publishes. The corruption regression deletes the duplicate row and proves fail-closed, zero-effect rejection.

This is regular-file causal continuity, not proof of a rename syscall. It does not complete directory/subtree moves, empty directories, portable metadata, conflict UX, ENOSPC, Android, retention collection, or live public Tor/I2P qualification.
