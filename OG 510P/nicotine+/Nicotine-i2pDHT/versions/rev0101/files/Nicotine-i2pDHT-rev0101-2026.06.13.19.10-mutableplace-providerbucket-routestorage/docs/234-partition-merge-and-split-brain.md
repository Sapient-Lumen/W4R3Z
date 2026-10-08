# Partition merge and split-brain pressure

A DHT over I2P should expect intermittent reachability, stale entrances, garden caches, and asymmetric views. `splitmerge.py` models the moment after partitions begin to reconnect.

The local merge pass refuses to treat “highest sequence observed first” as truth. It checks:

- scope/purpose/authority mixing,
- signature and time-window validity,
- same-sequence forks across partitions,
- stale replay against local accepted memory,
- previous-head linkage,
- partition/source/path diversity for the newest head.

If the newest head is signed but comes from only one partition/path/source family, the decision is `watch_under_diverse_latest`, not acceptance. If the newest head skips or disagrees with local previous-head memory, the decision is quarantine/repair pressure rather than blind advance.

This keeps the mutable-head rule alive:

```text
A valid signed head is an observation; local history and path pressure decide whether it advances memory.
```
