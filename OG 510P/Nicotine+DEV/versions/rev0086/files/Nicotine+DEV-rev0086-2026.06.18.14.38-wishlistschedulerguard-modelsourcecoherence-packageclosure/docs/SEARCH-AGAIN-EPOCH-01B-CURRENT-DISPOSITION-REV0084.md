# SEARCH-AGAIN-EPOCH-01B current disposition — rev0084

## Disposition

```text
status: open-persistent-wishlist-product-policy-research
selected patch: none
security route: not applicable
```

Persistent wishlist pages are owned by `WishSearchRequest`. Unlike ordinary and
manual-wishlist pages, this object owns durable `ignored_users`, scheduler
state, custom filters, and the distinction between unread and already-seen
results. The current same-token Retry still reaches the display-cap dead end,
but rotating its token and clearing its page would silently choose product
semantics the code does not currently define.

Rev0084 gives every wishlist result page a stable notification identity. This
solves notification replacement, activation, withdrawal, and cross-token page
routing as an identity problem; it does **not** answer what a persistent wish
refresh should do with durable state.

The research candidate therefore retains same-token Retry for
`WishSearchRequest` while allowing normal `SearchRequest` pages—including
manual wishlist pages—to rekey.

## Required product decisions

A maintainer decision is still needed among at least these meanings:

- **Retry:** keep rows, `ignored_users`, and token; only resend.
- **Refresh:** rotate the wire epoch and replace displayed results, while
  specifying whether seen-user history survives.
- **Reset:** clear both page rows and durable seen-user history, overlapping the
  separate Reset Seen Results command.
- **Remove Search Again:** avoid presenting a command whose semantics differ
  materially from ordinary searches.

Any true persistent-wish refresh also needs scheduler/reconnect behavior and a
rule for unread rows that disappear during replacement.
