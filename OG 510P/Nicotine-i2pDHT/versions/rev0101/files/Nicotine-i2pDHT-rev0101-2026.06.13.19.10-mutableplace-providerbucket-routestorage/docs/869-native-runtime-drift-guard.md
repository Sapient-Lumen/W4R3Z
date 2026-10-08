# Native runtime drift guard

`nativeruntime.py` turns native selection into local evidence instead of a global toggle. A runtime stamp carries the parity report digest, ABI report digest, fallback-seal digest, object digest, source digest, compiler-flag digest, sequence, previous digest, family hints, and whether native/fallback paths are selected.

It rejects:

```text
seal component digest drift
runtime stamp digest drift
native selected without fallback
rollback / replay
same-sequence fork
previous-link mismatch
low family/path diversity
```

Accepted runtime states are still not permission to call native code. They are only inputs to the dispatch seal.
