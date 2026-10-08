# Search Again wishlist hybrid boundary — rev0083

Rev0082 used a two-way mental model: ordinary requests versus wishlist
requests. Source review shows three ownership shapes instead.

| Page source | Core record | GUI mode | `ignored_users` owner | Token notification | Conservative action |
|---|---|---|---|---|---|
| global/room/buddy/user search | `SearchRequest` | non-wishlist | no | no | fresh-token rekey |
| manual wishlist dialog action | `SearchRequest` | wishlist | no | yes | same-token Retry |
| scheduled wishlist result | `WishSearchRequest` | wishlist | yes | yes | same-token Retry |

The important lesson is that class hierarchy and UI semantics are not the same
ownership axis. `WishSearchRequest` identifies persistent wishlist domain state;
`mode == "wishlist"` identifies page behavior that includes token-addressed
notifications. A safe candidate must choose the axis relevant to the state being
changed.

The executable counterexample records a notification for a manual wishlist
page, applies the superseded class-only rotation policy, and then observes that
activation cannot find the old page token. The mode-owned candidate keeps that
target valid.

```text
source invariants:        19/19 pass
classified tests:         16/16 pass
compile checks:             8/8 pass
fresh baseline units:      60 passed, 1 skipped
fresh patched units:       60 passed, 1 skipped
unit evidence bindings:    28/28 pass
```
