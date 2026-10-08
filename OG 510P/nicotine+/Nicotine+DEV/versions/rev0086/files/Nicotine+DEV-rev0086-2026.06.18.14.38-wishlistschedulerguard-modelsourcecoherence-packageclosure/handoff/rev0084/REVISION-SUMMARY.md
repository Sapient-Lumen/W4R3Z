# rev0084 handoff

## Heart of this turn

Rev0084 resolves the manual-wishlist notification counterexample at the correct
abstraction boundary. A wire token is a revocable network response capability;
it is not a suitable desktop notification identity. The candidate now gives
each GUI search page a non-reused UUID and routes notification activation
through that stable page identity to the page's current wire token.

This permits fresh-token same-page rekey for ordinary and manual-wishlist
`SearchRequest` pages. Persistent `WishSearchRequest` pages retain same-token
Retry because their durable seen-history and scheduler semantics remain a
separate product decision.

## Validation snapshot

```text
source invariants:                27/27 pass
identity/lifecycle model tests:   25/25 pass
compile checks:                   11/11 pass
baseline upstream units:          60 passed, 1 skipped
patched upstream units:           60 passed, 1 skipped
unit evidence bindings:           28/28 pass
candidate-lineage checks:         75/75 pass
candidate mutations rejected:       5/5
selected patch:                       none
```

## Cube refactor

`data/current_environment_capability_contract.json` and
`tools/audit_current_environment_capabilities.py` make native-validation scope
machine-readable. The audit records unavailable GTK/Gio/Win32 capabilities and
ensures source/model evidence is not promoted to native UI validation.

## Next

The highest-value next step is native GTK3/GTK4 and desktop-notification
integration on a suitable host. In parallel, persistent wishlist Retry versus
Refresh versus Reset policy remains open.
