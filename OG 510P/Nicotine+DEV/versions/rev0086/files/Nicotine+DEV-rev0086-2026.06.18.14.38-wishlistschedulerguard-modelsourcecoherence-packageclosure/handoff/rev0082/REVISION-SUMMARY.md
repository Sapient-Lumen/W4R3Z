# rev0082 revision summary

Rev0082 resolves the remaining supported token-consumer question around the ordinary Search Again rekey prototype and splits wishlist semantics into their own packet.

## Research result

`Events.emit()` is synchronous. The candidate changes the core request key, synchronously changes the GUI page key, resets generation-owned state, and only then sends with the new token. A delayed old response cannot repopulate the page: unparsed responses lose admission, queued responses cannot find the old core key, and a response event cannot be interrupted between core and GUI callbacks by a user action.

Token-addressed result notifications are emitted only for wishlist pages. Supported plugin hooks do not expose a token. Recently closed tabs store logical search arguments, and closing a rekeyed page uses its current token. The former plugin-consumer blocker is therefore closed for the in-tree and supported API surface.

The disposition is now:

```text
SEARCH-AGAIN-EPOCH-01A ordinary searches
  source/model viable, no selected patch, open native GTK validation

SEARCH-AGAIN-EPOCH-01B wishlist
  product semantics unresolved, no selected patch
```

## Validation

```text
source invariants:              31/31 pass
consumer tests:                 29/29 pass
compile checks:                  6/6 pass
unit evidence reuse checks:     17/17 pass
prior upstream units:           60 passed, 1 skipped in each state
avoided redundant test runs:       122
```

## Cube corrections

A digest-bound evidence-reuse contract prevents repeated execution from masquerading as new evidence. ZIP creation is now deterministic and fail-closed for duplicate, colliding, unsafe, symlink, metadata, and order defects. The ZIP builder self-test passes 10/10 checks and rejects 4/4 malformed mutation archives.

Final package validation adds a two-build byte-identity check, filesystem-to-ZIP digest comparison, clean extraction, and rerun of current package authority from that extraction.
