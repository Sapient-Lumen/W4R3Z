# WAL sidecar authority-laundering reproducer

The same C++ source was linked separately against the verified rev0792 parent
and rev0796 libraries. It creates a canonical one-entry SQLite-WAL replay
snapshot, checkpoints it, records the main-file SHA-256, then places a valid
outbox-state mutation only in a sibling `-wal` file. The main database digest
remains byte-for-byte unchanged.

Parent result: restore accepted the path and copied the WAL-only `inflight`
state into the destination. Current result: capture fails before SQLite opens
the source because a snapshot is defined as one sidecar-free main file.

Source SHA-256: `521c3a63f22cfb3712b86f2003cc125b505dcdfbda9f47b20f7ade2776e323a7`

Parent log SHA-256: `efab08a06d4f3fc5ce3ca2e6f54fec3b03319da4a62cacea5fe7076abfef7ed3`

Current log SHA-256: `a1b460c9fa85a9565962e6ccec32e6b7e3a0c21ac6208f9856198af890941cd9`

No reproducer binary is packaged.
