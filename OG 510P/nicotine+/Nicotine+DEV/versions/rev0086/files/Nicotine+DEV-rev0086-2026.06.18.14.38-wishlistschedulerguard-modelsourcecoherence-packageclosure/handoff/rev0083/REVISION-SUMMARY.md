# rev0083 revision summary

Rev0083 identifies a third Search Again ownership shape and corrects a prototype
and cube-governance defect.

## Research result

Manual wishlist dialog actions create `SearchRequest(mode="wishlist")` records,
not persistent `WishSearchRequest` records. They do not own `ignored_users`, but
their GUI pages still emit token-addressed wishlist notifications and read wish
filters by term. A request-class-only rekey can therefore strand an existing
notification on a dead token.

The current research candidate centralizes eligibility in the core method:
non-wishlist page modes rekey; every wishlist-mode page retains same-token Retry.
This is conservative and leaves manual and persistent wishlist semantics in
separate policy packets. No patch is selected.

## Validation

```text
source invariants:          19/19 pass
source/model/core tests:    16/16 pass
compile checks:               8/8 pass
baseline upstream units:     60 passed, 1 skipped
patched upstream units:      60 passed, 1 skipped
unit evidence bindings:      28/28 pass
```

## Cube correction

The old candidate remains immutable because rev0081/rev0082 evidence binds its
path and digest. The changed hypothesis has a revision-qualified filename and a
machine-readable lineage contract. Five contract mutations are expected to be
rejected, preventing historical evidence from being silently rebound to changed
bytes.
