# rev0090 audit — temporal-coherence refactor

## Risk addressed

The riskiest open gap from rev0089 was stale mixed-scope composition. rev0088 guarded against category upgrades, but a current-use guard could still be made from inputs observed at incompatible times. That is a correctness bug because old lifecycle, revocation, discovery, or transparency-policy state can look safe when validated independently.

## What changed

- Added `temporal_coherence` to the scope-composition guard schema.
- Added required observation roles for each current-use surface.
- Added an evaluation window and semantic ordering checks.
- Added stale/unchecked input semantics that must suppress, historicize, or fail closed instead of staying current.
- Added `tools/temporal_coherence.py` to pull timestamp-window logic out of the main validator.
- Added negative tests for stale-current reuse and inverted evaluation-window bounds.

## Refactor note

This is intentionally a narrow helper extraction rather than a large validator rewrite. The validator is still too large, but the most failure-prone timestamp logic now has a dedicated module that can be reused by aggregate lifecycle, discovery, and replay-transparency checks in later revisions.

## Remaining risk

The digest layer still uses Python canonicalization helpers for synthetic digest checks. A later revision should either adopt a true RFC 8785/JCS implementation or constrain digestable inputs enough that the current helper is provably equivalent for all in-corpus objects.

## Next target

Generalize temporal-coherence helpers beyond scope composition: aggregate artifact creation times, lifecycle status checks, policy-reference observations, notification observations, and replay anchor evaluations should share the same bounded-window machinery.
