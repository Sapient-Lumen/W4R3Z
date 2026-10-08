# nativeselectionfold audit/refactor

`nativeselectionfold.py` pins rev0086 through source, tests, docs, public pointers, head registry, fold map, fold registry, active surface ledger, and the rev0085 `nativeprovenancefold` predecessor.

This fold also keeps the native branch from sprawling. The current active path is:

```text
nativeprovenance/nativecorpus/nativequarantine
  -> nativeselection/fallbackjournal/nativepromotion
```

Python remains the oracle and the semantic owner.
