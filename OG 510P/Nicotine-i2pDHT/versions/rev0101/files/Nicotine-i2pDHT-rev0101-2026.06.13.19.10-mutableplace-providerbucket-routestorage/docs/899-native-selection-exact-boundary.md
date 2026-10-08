# Native selection exact boundary

Native selection is deliberately later than native provenance. A build can be reproducible, corpus-parity-clean, and not actively quarantined, but the runtime still needs a specific decision:

```text
component
profile
operation
request id
artifact digest
source digest
Python fallback digest
provenance report digest
corpus report digest
quarantine report digest
native-budget digest
sequence / previous digest
family and path diversity
```

`nativeselection.py` makes that local decision explicit. It rejects digest drift, replay, rollback, same-sequence forks, previous-link mismatch, missing fallback route, low diversity, unaccepted budget, unaccepted corpus, and unaccepted provenance.

The selection report can choose native, fallback, or watch/quarantine. Native remains leaf-only and dispatch remains a separate exact-boundary gate.
