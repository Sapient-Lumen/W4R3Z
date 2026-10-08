# Search Again same-page fresh-token prototype — rev0081

## Disposition

The patch under `maintainer_artifacts/search-rekey-01/` is an executable research hypothesis. It is not selected, production-ready, or upstream contribution material.

For ordinary global, room, buddy, and explicit-user searches, the minimum coherent refresh does not require replacing the page or creating a permanent logical-search registry. The existing request and page can be re-keyed to a fresh response token while retaining their logical identity.

## Exact transition

For token `A`, the prototype performs:

```text
remove parser admission for A
remove A from self-search suppression
remove core.searches[A]
allocate fresh token B
set the same SearchRequest.token to B
store the same request at core.searches[B]
synchronously re-key the same GUI page A -> B
clear state derived from the A response generation
add parser admission for B through the existing send path
dispatch the mode-specific request or fan-out with B
```

The old token is therefore absent from both parser admission and core lookup before the new request is sent. An unparsed old response loses admission; an already-parsed old response cannot resolve the deleted core key.

## Identity retained

```text
same processed SearchRequest object
same GUI page and notebook container
same tab position, focus intent, and recently-closed history
same search text and plugin-processed term fields
same filter widgets and values
same grouping and sorting controls
same room or explicit-user audience
live buddy audience is deliberately re-resolved at send time
```

## Generation state reset

```text
visible and stored result rows
result count and display-cap consumption
username and folder deduplication sets
row model and iterators
selected result and selected-user caches
prior-attempt error presentation
```

Selection caches must be cleared before the tree model because they can hold iterators that become invalid when the model is reset.

## Rejected variants

**Clear and retain the token.** It restores capacity but cannot distinguish a delayed pre-clear response from a response caused by the new click.

**Replace the page.** Viable, but unnecessarily migrates focus, tab placement, undo history, widgets, and plugin-visible identity.

**Keep an old-token alias table.** Not needed for ordinary result routing and introduces cleanup and generation ambiguity.

**Automatically re-key wishlist searches.** Rejected for this prototype. Wishlist seen-user history and unread-row handling have independent product semantics.

**Wait for a network acknowledgement.** Necessary only for a stronger failure-atomic promise, not for the application's existing best-effort new-search semantics.

## Executable evidence

```text
7 model tests
13 source and GUI-contract tests
8 native core/network integration tests
baseline upstream units: 60 passed, 1 skipped
patched upstream units:  60 passed, 1 skipped
```

`test_i18n.py` is explicitly excluded because `msgfmt` is unavailable; it is not counted as passing.

## Remaining native checks

A maintainer-directed GTK3/GTK4 smoke pass still needs to inspect focus, active tab, unread marker, filters, grouping, sort, expansion, scroll, rapid repeat, online-to-offline transitions, and plugin consumers that may treat a wire token as permanent page identity.
