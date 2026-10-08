# SEARCH-AGAIN-EPOCH-01B current disposition — rev0083

## Scope

Scheduled and persistent wishlist searches backed by `WishSearchRequest`.

These records own scheduling state, custom filters, `is_ignored`, persistent
`ignored_users`, and the token used by a result page and desktop notification.

## Confirmed behavior and unresolved policy

The same-token display-cap dead end is confirmed. A destructive refresh cannot
be selected mechanically because it must define what happens to:

```text
unread rows
persistent seen-user history
already displayed notification action targets
scheduled-search state
Reset Seen Results as a deliberately separate command
```

The rev0083 candidate preserves the current same-token Retry behavior for this
packet. That does not solve the cap dead end; it prevents an ordinary-mode fix
from silently choosing wishlist product semantics.

## Disposition

```text
same-token cap dead end: confirmed
persistent state ownership: confirmed
fresh-token refresh semantics: unresolved
security route: not applicable; product semantics
selected patch: none
status: open persistent-wishlist product-policy research
```
