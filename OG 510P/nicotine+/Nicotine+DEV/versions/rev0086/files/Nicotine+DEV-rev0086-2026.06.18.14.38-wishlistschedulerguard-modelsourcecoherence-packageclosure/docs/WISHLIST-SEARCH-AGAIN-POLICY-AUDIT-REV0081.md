# Wishlist Search Again policy audit — rev0081

## Result

The ordinary-search fresh-token rekey must not be extended to wishlist pages by default.

Wishlist has a persistent seen-user mechanism, not merely an in-page deduplication set:

```text
WishSearchRequest.ignored_users is serialized
incoming wishlist results from ignored users are rejected in core
users become seen when an unread wishlist result tab is opened
Reset Seen Results explicitly clears ignored_users
```

This matches the public wishlist design: previously seen results are discarded, results become seen only when the unread tab is opened, and a separate reset command permits all results again.

## Counterexamples

### Fresh token, clear rows, preserve `ignored_users`

If the page contains unread results, those usernames have intentionally not yet entered `ignored_users`. Clearing the page can destroy results the user never saw. A new search does not guarantee the same peers will respond again, so this is potential user-visible loss rather than a harmless repaint.

### Fresh token, clear rows and `ignored_users`

This silently performs the separately named Reset Seen Results operation. It re-admits previously seen users, changes persisted wishlist history, and makes a generic Search Again click destructive.

### Keep the current same-token Retry/Merge

This preserves unread rows and seen history, but inherits the confirmed display-cap dead end and cannot isolate delayed old responses. It is nevertheless safer than an implicit destructive refresh until wording and policy are chosen.

## Coherent product choices

```text
retain Retry/Merge for wishlist and leave Reset Seen Results separate
rename the wishlist command to clarify that it only requests more results
hide Search Again on wishlist pages
add an explicit destructive Refresh with unread-result and seen-history semantics
```

A destructive refresh would still need a decision about whether to preserve or reset seen history and what to do with unread rows. No wishlist patch is selected.
