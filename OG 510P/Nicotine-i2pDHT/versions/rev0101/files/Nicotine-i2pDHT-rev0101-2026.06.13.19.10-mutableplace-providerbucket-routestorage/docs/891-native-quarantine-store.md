# Native quarantine store

`nativequarantine.py` makes failed native evidence sticky.

When provenance or corpus evidence fails, a quarantine marker binds:

```text
artifact digest
source digest
provenance digest
corpus digest
budget digest
fallback digest
reason
sequence / previous digest
family / path family
```

The marker routes calls to Python fallback and prevents a later restart from treating the same bad artifact as new. Healthy native evidence may proceed without a marker, but bad evidence without a marker becomes watch debt.
