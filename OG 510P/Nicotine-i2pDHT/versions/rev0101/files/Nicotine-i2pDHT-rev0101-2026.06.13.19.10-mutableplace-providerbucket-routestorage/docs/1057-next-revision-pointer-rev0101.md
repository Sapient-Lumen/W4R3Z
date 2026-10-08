# Next revision pointer rev0101

Suggested rev0102 direction: `replicaplan-mutablewatch-bucketsweep`.

Go one seam past placement:

- mutable placement -> replica/watch planning
- provider bucket -> bucket sweep / region reprovide planning
- route storage -> route refresh / stale contact eviction transcript
- audit/refactor: make substrate spine less hand-edited as it grows
