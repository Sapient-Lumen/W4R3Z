# SEARCH-AGAIN-EPOCH-01A current disposition — rev0082

## Scope

Ordinary global, room, buddy, and user Search Again behavior on the master line.
Wishlist behavior is now a separate packet, `SEARCH-AGAIN-EPOCH-01B`.

## Confirmed defect

The current same-token resend is nonproductive once the page reaches the display cap. It also behaves as a merge below the cap because a username already represented on the page is not admitted again.

## Narrow candidate

The rev0081/rev0082 research prototype keeps the same logical search and GUI page while rotating only the wire-response token. It:

```text
removes old response admission and old self-search bookkeeping
moves the same SearchRequest to a fresh core key
synchronously rekeys the same GUI page in its existing tab position
clears rows, counters, dedupe sets, and stale selection iterators
sends through the existing mode-specific request path
```

No patch is selected for upstream use.

## Consumer closure

Rev0082 closes the previously listed plugin-consumer uncertainty for the supported in-tree surface.

### Event ordering

`Events.emit()` invokes callbacks synchronously in registration order. `Search.repeat_search()` changes the core key, emits `rekey-search`, and only then calls `send_search_request(new_token)`. Therefore the GUI page key is changed before a new-token response can be caused by the resend.

An old response cannot interleave between core and GUI callbacks of one event: the callback loop is synchronous. If an old response is still queued when Search Again runs, the later core lookup finds no old request and sets `msg.token` to `None`; the GUI then has no old page key either.

### Notifications

Search-result desktop notifications carry a token action target, but the GUI emits them only inside the wishlist branch. Ordinary searches do not create a notification token that needs aliasing, and the candidate explicitly excludes wishlist pages.

### Plugins

The supported outgoing search plugin hooks accept search text and, where applicable, room or user audience. They do not receive the wire token. Search Again reuses the already processed `SearchRequest`, matching the legacy resend behavior rather than rerunning plugin transformation hooks.

This conclusion is scoped to the documented/in-tree plugin surface. Third-party code that imports internal dictionaries is not enumerable and receives no compatibility guarantee here.

### Closing and reopening

Closing a page calls `remove_search(self.token)`, so a rekeyed page removes its current core key. Recently closed search tabs store logical search arguments—term, mode, room, and users—not the wire token. Restoring a tab calls `do_search()` and creates a new epoch.

## Remaining evidence

```text
native GTK3 and GTK4 smoke validation
focus, active-tab, unread-marker, expansion, and scroll checks
rapid-repeat and online-to-offline native lifecycle checks
exact whole-tree execution on the observed public master head
measured practical resource impact before any stronger severity claim
```

The six public commits between the bundled executable proxy and observed master head do not touch the relevant search files. Current public `search.py` and `pluginsystem.py` retain the reviewed flow, but this is flow confirmation rather than exact whole-tree execution.

## Disposition

```text
behavior: confirmed
candidate mechanics: source/model viable
supported token consumers: classified and closed
wishlist semantics: moved to SEARCH-AGAIN-EPOCH-01B
security route: not applicable; low-severity product correctness/resource hygiene
selected patch: none
status: open native-UI validation
```

Executable evidence:

```text
data/rev0082_search_consumer_summary.json
data/rev0082_search_consumer_source_invariants.csv
data/rev0082_search_consumer_inventory.csv
data/rev0082_search_consumer_test_matrix.csv
maintainer_artifacts/search-rekey-01/search_again_fresh_token_rekey.patch
```
