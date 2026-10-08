# SEARCH-AGAIN-EPOCH-01C current disposition — rev0083

## Scope

Manual wishlist query pages created by **Search for Item** or **Set Custom
Filters…** in the wishlist dialog.

## Hybrid ownership finding

These pages are not persistent `WishSearchRequest` records. Both actions call
`do_search(..., mode="wishlist")`, and `do_search()` creates a normal
`SearchRequest`. Consequently, the page does not own persistent
`ignored_users`; `on_read_changed()` refuses to update the persistent wish when
the page token differs.

At the GUI boundary, however, the page is fully wishlist-mode:

```text
wishlist filters are resolved by term
wishlist result importance and title behavior apply
desktop notifications carry str(page.token)
notification activation performs an exact token lookup
```

This makes request class an unsafe rekey predicate. The superseded prototype's
core guard excluded only `WishSearchRequest`, while its GUI separately excluded
all `mode == "wishlist"` pages. A future direct core caller or refactor could
therefore rotate a manual page and strand an already displayed notification on
the old token.

## Current correction

The rev0083 research candidate centralizes the decision in
`Search.repeat_search()` and treats every wishlist-mode page as a stable-token
Retry. The GUI delegates without duplicating the policy branch.

This is a conservative boundary, not a complete user-facing solution. Manual
wishlist pages do not have the persistent seen-history problem, so a future
fresh-token refresh could be designed if notification expiry or aliasing and
filter semantics are specified explicitly.

## Disposition

```text
hybrid request/page provenance: confirmed
class-only rekey notification counterexample: confirmed
current candidate action: same-token Retry
fresh-token manual-wishlist policy: unresolved
security route: not applicable; product correctness
selected patch: none
status: open manual-wishlist hybrid-policy research
```
