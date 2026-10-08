# replayfold audit/refactor

`replayfold.py` is the rev0054 current-path fold audit.

It checks the replay/quench/fuzzledger modules, tests, docs, fold map, fold registry, surface ledger, and the rev0053 `handlerfold` predecessor. This is the audit/refactor lane for the turn: it keeps the current revision visible while preserving the prior handler-capsule/side-effect-journal path.

The fold intentionally stays boring. It reduces amnesia risk by ensuring the new surfaces are reachable from code, tests, docs, public pointers, and revision registries.
