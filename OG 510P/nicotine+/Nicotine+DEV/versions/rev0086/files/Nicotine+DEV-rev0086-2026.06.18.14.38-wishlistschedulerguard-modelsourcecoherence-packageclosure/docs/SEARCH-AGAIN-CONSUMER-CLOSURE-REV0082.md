# Search Again token-consumer closure — rev0082

The rev0081 queue listed plugin/event consumers as an unresolved risk. Rev0082 replaces that broad concern with a bounded inventory and a precise support boundary.

## Inventory result

```text
classified consumers: 13
nonblocking or closed: 11
open boundaries:       2
```

The two open rows are native GTK state and wishlist product policy. They are not hidden token owners.

| Consumer | Token role | Result |
|---|---|---|
| parser admission | response capability | old removed; new added before send |
| core `searches` | request lookup key | same object moved to new key |
| `_own_tokens` | self-search admission | old discarded; send binds new |
| GUI `pages` | page lookup key | same page moved without reordering |
| queued responses | message lookup | old token becomes unresolvable |
| notifications | action target | wishlist-only; ordinary candidate excluded |
| supported plugin hooks | none | no token parameter; processed request reused |
| built-in plugins | none | same token-free hook surface |
| recently closed tabs | none | logical args only; restore creates new search |
| page close | current page token | removes new key after rekey |

## Ordering proof

```text
main-thread Search Again callback
  1. retire old core admissions
  2. move core request to new token
  3. synchronous rekey-search callback moves GUI page
  4. reset result-derived page state
  5. return from event callback
  6. send request using new token
```

There is no asynchronous queue between steps 3 and 6. Likewise, one incoming response event cannot be interrupted between its core and GUI callbacks by a Search Again click.

## Compatibility boundary

This audit covers the application tree, built-in plugins, and supported plugin callback signatures. It does not promise compatibility for extensions that reach into undocumented internal dictionaries or attach directly to internal event names.

## Executable checks

```text
source invariants:          31/31 pass
source/model tests:         29/29 pass
compile checks:              6/6 pass
prior unit evidence reuse:  17/17 digest checks pass
avoided redundant tests:       122 executions
```
