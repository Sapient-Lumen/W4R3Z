# SEARCH-AGAIN-EPOCH-01B current disposition — rev0086

```text
scope: persistent WishSearchRequest result pages
status: open-native-ui-action-removal-validation
selected patch: none
security route: not applicable
```

## Correction

The open question is no longer an undifferentiated choice among Retry,
Refresh, Reset, and removal.

Source ownership and history distinguish them:

- automatic delivery uses scheduled `WishlistSearch`;
- the inherited tab action emits ordinary same-token `FileSearch`;
- `ignored_users` is durable sender-level seen state;
- **Reset Seen Results** explicitly owns destructive seen-state reset;
- **Search for Item** explicitly owns an immediate independent manual search.

The generic tab action therefore has no coherent persistent-subscription
meaning. The rev0085-origin candidate, revalidated in rev0086, hides it for `WishSearchRequest` pages and also
guards the callback, while leaving the scheduler and seen history untouched.
Manual wishlist `SearchRequest` pages retain Search Again.

This candidate still needs maintainer acceptance and native GTK3/GTK4 checks
for hidden-action behavior, accessibility, keyboard paths, and offline Retry
presentation. It is not selected.

The scheduler-at-cap problem is now tracked independently as
`WISHLIST-CAP-01`; removing a redundant manual action must not be misrepresented
as solving long-lived subscription capacity.
