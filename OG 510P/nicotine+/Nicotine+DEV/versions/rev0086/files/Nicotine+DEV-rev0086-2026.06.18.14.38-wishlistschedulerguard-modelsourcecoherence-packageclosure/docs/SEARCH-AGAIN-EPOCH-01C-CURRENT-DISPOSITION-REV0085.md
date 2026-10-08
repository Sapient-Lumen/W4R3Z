# SEARCH-AGAIN-EPOCH-01C current disposition — rev0085

```text
scope: manual wishlist SearchRequest pages
status: open-native-ui-validation
selected patch: none
security route: not applicable
```

Wishlist dialog actions such as **Search for Item** create normal
`SearchRequest` objects with wishlist GUI presentation. They do not own the
persistent wish's scheduler or `ignored_users` state.

The stable logical page UUID introduced in rev0084 removes the notification
token blocker. Rev0085 preserves that design and confirms that request-class
eligibility keeps these manual pages refreshable while excluding only
`WishSearchRequest` inbox pages.

Native GTK3/GTK4, Gio desktop-shell, and Windows notification lifecycle tests
remain mandatory. No implementation is selected.
