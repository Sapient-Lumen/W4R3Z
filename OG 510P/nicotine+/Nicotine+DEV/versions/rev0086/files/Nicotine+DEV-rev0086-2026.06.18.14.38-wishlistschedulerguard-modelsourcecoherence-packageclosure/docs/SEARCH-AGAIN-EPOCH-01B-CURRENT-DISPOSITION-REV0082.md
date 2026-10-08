# SEARCH-AGAIN-EPOCH-01B current disposition — rev0082

## Scope

Wishlist Search Again semantics, including persistent seen-user history, unread rows, notifications, scheduling, and the separate Reset Seen Results action.

## Why this is no longer part of the ordinary packet

Ordinary search deduplication is generation-owned page state. Wishlist `ignored_users` is persistent domain state: opening an unread wishlist result marks represented users as seen, and future results from those users can be discarded independently of the current rows.

A token rotation alone cannot decide what Search Again should mean:

```text
Retry wish
  preserve rows and ignored_users; resend current token or a fresh token without reset

Refresh wish
  rotate token and clear rows, but preserve ignored_users
  risk: unread rows can disappear before their users become seen

Reset wish
  rotate token, clear rows, and clear ignored_users
  risk: silently duplicates the deliberately separate Reset Seen Results command

Remove Search Again from wish pages
  retain only scheduled searches and Reset Seen Results
```

Search notifications are also wishlist-only and use the token as their activation target. Any future wishlist rekey needs an explicit policy for notifications already displayed when the token changes.

## Disposition

```text
same-token result-cap dead end: confirmed
ordinary rekey prototype applicability: explicitly excluded
product wording and seen/unseen semantics: unresolved
notification alias/expiry policy: unresolved for any future rekey
security route: not applicable; product semantics
selected patch: none
status: open wishlist product-policy research
```

No automatic clearing of `ignored_users` is selected. No ordinary-search implementation should be blocked on this separate decision.
