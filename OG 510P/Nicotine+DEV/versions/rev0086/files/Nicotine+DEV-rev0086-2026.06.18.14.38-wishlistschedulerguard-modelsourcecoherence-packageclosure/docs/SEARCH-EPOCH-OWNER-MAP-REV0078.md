# Search identity owner map — rev0078

| Owner | Current role | Required direction |
|---|---|---|
| allocator | component token cursor | monotonic wire-token allocator |
| request/response wire format | search token | rotate per replacement epoch |
| parser admission | allowed-response token | ordered retire/add per epoch |
| core registry | `searches[token]` | stable logical registry plus token route |
| GUI registry | `pages[token]` | stable logical ID |
| page object | `page.token` | logical ID and current wire token separately |
| notification target | stringified token | stable logical ID |
| show/remove API | token argument | logical search identity |
| self-search gate | `_own_tokens` | bind and retire wire epochs |
| buddy audience | live set at send time | explicit per-epoch policy |
| network queue generation | disable/clear without acknowledgement | applied acknowledgement or reconnect reconciliation |

Machine-readable rows are in `data/rev0078_search_epoch_owner_map.csv`.

## Refactor implication

This is a bounded identity migration, not a one-line increment. The lowest-risk sequence is likely:

```text
introduce stable logical identity while preserving current behavior
migrate page/navigation/notification/show/remove owners
introduce token routing and pending epoch state
add acknowledged network application or reconciliation
only then enable replacement refresh semantics
```

That sequence permits reviewable compatibility tests at each boundary and avoids mixing identity migration with a user-visible semantic change.
