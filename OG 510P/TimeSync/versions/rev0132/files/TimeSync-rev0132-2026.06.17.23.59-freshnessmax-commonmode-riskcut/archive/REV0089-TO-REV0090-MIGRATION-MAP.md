# rev0089 to rev0090 migration map

## Breaking schema change

`scope-composition-guard` moves from `guard_version: rev0088` to `guard_version: rev0090` and now requires `temporal_coherence`.

## Required producer changes

Producers of current-use scope-composition guards must add:

```text
temporal_coherence.policy_version = rev0090
temporal_coherence.evaluation_window
temporal_coherence.input_observations[]
temporal_coherence.coherence_decision
temporal_coherence.non_provenance_boundary
```

Each current-use surface must have its required timestamp role and must be fresh inside the evaluation window. Stale or unchecked observations must suppress, historicize, or fail closed.

## Consumer behavior

Consumers must reject current-use guards that omit temporal coherence, contain stale/unchecked current inputs, miss required timestamp roles, place guard evaluation outside the declared window, or invert the window bounds.
