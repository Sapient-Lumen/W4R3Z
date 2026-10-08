# Tomb repair join after prune

`tombrepairjoin.py` keeps tombstone repair from becoming an optional cleanup task.

A terminal or retry-held settlement store may still be unsafe if live tombstones, withdrawal records, compromise notices, or resurrection blocks were not carried through repair and prune evidence.

The join accepts two cases:

- no live tombstone debt is expected,
- live tombstone debt is expected and repair coverage carries all expected tombstones.

It holds missing repair and quarantines resurrection pressure. It also checks prune interaction so repair evidence is not dropped by a separate compaction lane.
