# SEARCH-AGAIN-EPOCH-01C current disposition — rev0084

## Disposition

```text
status: open-native-ui-validation
selected patch: none
security route: not applicable
severity: low product correctness
```

Manual **Search for Item** and **Set Custom Filters** actions create ordinary
`SearchRequest` objects with `mode="wishlist"`. They do not own the persistent
wish scheduler or `ignored_users`, but their GUI pages use wishlist importance,
filters, and desktop notifications.

Rev0083 correctly found that rotating only the wire token could strand an
already displayed notification, because activation stored that exact token.
Rev0084 resolves the underlying identity error instead of retaining the broken
same-token behavior:

```text
wire token
  lifetime: one response epoch
  owner: core/network admission
  may rotate: yes

logical search page ID
  lifetime: one GUI page
  owner: GUI page registry
  may rotate with wire token: no

application notification ID
  lifetime: one page's current notification
  owner: desktop-shell integration
  value: search-<logical-page-UUID>
```

The page ID is generated once with a non-reused UUID, remains stable through
wire-token changes, and is removed when the page closes. Notification
activation resolves the page ID to the page's **current** token. Repeated Gio
notifications for the same page replace one another; close and clean shutdown
withdraw them. On Windows, withdrawal is allowed only when both the current
action and target match, so closing page A cannot dismiss a newer page B
balloon.

## Established by rev0084

- Manual wishlist pages can mechanically use fresh-token same-page rekey.
- A notification emitted before rekey still opens the same page afterward.
- Old wire tokens are not retained as aliases.
- Closed-page and cross-process stale action targets do not resolve a later
  page, assuming non-reused UUIDs.
- Logical mapping size is bounded by open pages, not by rekey count.
- Twenty-five identity/lifecycle tests, twenty-seven source invariants, eleven
  compile checks, and both upstream unit lanes pass.

## Remaining gate

The environment lacks PyGObject/GTK runtimes, so native GTK3, GTK4, Gio desktop
shell, and Windows balloon behavior has not been executed. The prototype remains
research-only and unselected until those integrations are exercised.
