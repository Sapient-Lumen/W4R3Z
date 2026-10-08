# Search refresh state-ownership audit — rev0081

Machine-readable inventory: `data/rev0081_search_rekey_state_ownership.csv`.

## Ownership rule

A response token identifies a wire-response epoch. It is not inherently the identity of the user's visible search session. State derived from the old response stream should be reset; state owned by the visible session should survive.

| State family | Owner | Ordinary same-page rekey |
|---|---|---|
| Wire token and parser admission | response epoch | replace and retire old |
| Core request object and processed term | logical search | preserve object; change key/token |
| Result rows, count, user/folder dedupe | response epoch | clear |
| Selection caches and row iterators | result model | clear before model invalidation |
| Filters, grouping, sort | visible page | preserve |
| Tab object, order, focus, undo history | visible page/container | preserve by avoiding removal |
| Room and explicit-user audience | logical request | preserve |
| Buddy audience | live configuration at send time | re-resolve |
| Wishlist ignored-user history | wishlist domain | do not change implicitly |
| Desktop search-result notification route | wishlist page | no ordinary-search alias needed |

## Partial-rekey hazards

These states must never become externally visible:

```text
new page token with the old GUI dictionary key
new core key while old parser admission remains enabled
new request token while the old token remains in _own_tokens
cleared tree model while selected row iterators remain cached
page cleared before an offline guard decides no request can be sent
old response accepted after the new generation is visible
```

The candidate orders the core map before the synchronous GUI event, updates the GUI map before mutating the page token, clears selection before the model, and sends only after both owners agree on the new token.

## Architectural consequence

A second permanent logical-search identifier is not required for this bounded ordinary-search operation. It becomes useful only if future requirements demand multiple simultaneous wire epochs, replay after reconnect, durable cross-thread transactions, or stable external/plugin handles independent of page objects.
