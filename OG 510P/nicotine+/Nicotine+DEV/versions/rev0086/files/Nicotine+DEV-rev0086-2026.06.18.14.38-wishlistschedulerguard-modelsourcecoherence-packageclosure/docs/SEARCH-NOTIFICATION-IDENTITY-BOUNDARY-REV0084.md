# Search notification identity boundary — rev0084

## The mistake

The current flow uses one integer token for three different jobs:

1. network response admission;
2. core and GUI search lookup;
3. a desktop notification action target.

The first job is intentionally epoch-scoped. Search Again needs to revoke it.
The third job can outlive that epoch—and, on Gio desktops, can outlive the
process. Treating the wire token as notification identity makes safe refresh
appear impossible or requires an unbounded alias history.

## Revised ownership model

| Identity | Owner | Lifetime | Revocation |
|---|---|---|---|
| Wire token | core/network | one request epoch | remove allowed response and token map entry |
| Logical page UUID | GUI | one page lifetime | remove page-ID map entry on close |
| Gio notification ID | application/desktop shell | current notification for one page | replace by same ID; withdraw on close/shutdown |
| Win32 balloon target | current tray balloon | current displayed/queued balloon | withdraw only matching action and target |

A UUID rather than a process-local counter is important because Gio
notifications may persist after process exit. A counter reused on the next
launch could route an old action to an unrelated new page. A stale UUID instead
fails closed.

## Why no token alias registry

An alias map would retain every previous wire token so old notification actions
could find the current page. That mixes revoked network capabilities back into
long-lived GUI identity, grows with every refresh, and complicates close and
restart behavior. Stable page identity avoids all three problems:

```text
notification target -> logical page -> current wire token
```

## Platform lifecycle

Gio supports an application-supplied notification ID. Reusing the ID replaces
the prior notification, and the same ID can be withdrawn. Current source passes
`id=None`, making replacement and withdrawal impossible. The prototype uses
`search-<page-UUID>` only for search-result notifications; other notification
classes retain current behavior.

The existing Windows tray implementation owns one current click action and
target. The prototype clears a balloon only when both match the closing page,
then sends an empty `szInfo` with `NIM_MODIFY`, matching the documented Win32
removal mechanism.

## Failure boundaries retained

- This design does not prove notification delivery or desktop-shell display.
- A crash can leave a Gio notification, but its random page target will not map
  in a later process.
- Persistent wishlist refresh semantics remain unresolved independently of
  notification identity.
- Native platform tests remain mandatory before selecting a patch.
