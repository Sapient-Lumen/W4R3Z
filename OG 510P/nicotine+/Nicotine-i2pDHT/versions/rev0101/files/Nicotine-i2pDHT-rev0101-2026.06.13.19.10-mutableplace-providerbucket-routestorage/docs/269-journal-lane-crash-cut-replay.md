# Journal lane crash-cut replay

`persistlane.py` signs whole local snapshots. `journallane.py` adds a smaller pressure surface: append-only signed entries between snapshots.

Tested risks:

- crash-cut tail bytes after a valid linked prefix;
- previous-digest mismatch;
- same-sequence fork pressure;
- rollback below local memory;
- compaction that preserves tombstones, revocations, and provider-false hard negatives.

The journal is not a disk format. It is a toy replay algebra for restart safety.
