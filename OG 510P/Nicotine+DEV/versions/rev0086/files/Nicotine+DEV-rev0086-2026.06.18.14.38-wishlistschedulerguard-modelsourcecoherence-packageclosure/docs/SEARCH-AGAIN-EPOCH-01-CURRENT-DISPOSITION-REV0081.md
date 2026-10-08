# SEARCH-AGAIN-EPOCH-01 current disposition — rev0081

## Decision

```text
confirmed current defect: same-token Search Again is nonproductive at the result cap
rev0080 minimum-design claim: corrected
ordinary global/room/buddy/user experiment: same-page fresh-token rekey is mechanically viable
old-token response isolation: demonstrated in parser-admission and already-parsed paths
page, tab, filter, grouping, sort, processed request, and audience identity: preserved
result-derived rows, dedupe, counters, and stale selection iterators: cleared
wishlist: deliberately excluded; seen-history policy remains unresolved
selected patch: none
status: open wishlist refresh policy and native UI validation
security route: ordinary low-severity correctness and resource-hygiene research
```

## What rev0081 corrects

Rev0080 correctly rejected clear-and-reuse of the same token and correctly identified fresh-token replacement as viable. It went too far by calling page replacement the minimum best-effort design.

The core already keeps a mutable `SearchRequest` object keyed by token, and the GUI keeps a page keyed by the same token. For an ordinary search, both keys can be changed in place while preserving the object identities that carry processed search fields, mode-specific audience, tab placement, filter widgets, grouping, and sort state.

The bounded sequence is:

```text
reject offline click before destructive work
remove old parser admission
retire old self-search suppression token
remove old core lookup key
allocate fresh token
assign fresh token to the same processed SearchRequest
insert new core lookup key
rekey the same GUI page and clear result-derived state
admit and send the new-token request
retain the existing post-send disconnect feedback check
```

This uses the same best-effort semantics as starting a normal search. It does not promise that the network thread applied or transmitted the request. The stronger acknowledgement design from rev0078–rev0079 remains relevant only if the product requires a failure-atomic refresh promise.

## Why late old responses remain bounded

There are two response stages:

1. A response not yet parsed is rejected after the old token is removed from network admission.
2. A response already parsed and queued reaches the main-thread lookup after the old key has been removed. The core cannot associate it with a current search, and it is not routed into the rekeyed page.

The prototype intentionally does not maintain an old-to-new alias table. Such a table is unnecessary for ordinary search result notifications, which are wishlist-specific, and it would create another lifetime and cleanup surface.

## Why the page can remain

The experiment changes the dictionary key while preserving insertion order and the page object. It clears only state derived from the prior result epoch:

```text
rows and tree model
stored result count
username and folder dedupe sets
selected result iterators
selected username set
```

It preserves:

```text
page/container identity and tab position
focus and existing widgets
filters and filter history
result grouping and sort state
processed search terms and exclusion/inclusion words
room and explicit-user audience
live buddy-list resolution at resend time
recently-closed history (no close/recreate path)
```

Native GTK3/GTK4 smoke testing is still required for focus, unread markers, scroll position, expansion, and any widget state not represented in the headless harness.

## Wishlist boundary

`WishSearchRequest.ignored_users` is persistent domain state, not merely row deduplication. The UI already exposes a separate **Reset Seen Results** action. Automatically preserving `ignored_users` would make Search Again a retry/merge; clearing it would make Search Again a semantically stronger reset. Either choice changes user-visible wishlist behavior.

Rev0081 therefore leaves wishlist Search Again on its existing same-token branch and does not select the broader patch. A future design should first decide one of these explicit policies:

```text
Retry wish: preserve ignored_users and existing rows
Refresh wish: fresh token, clear rows, preserve ignored_users
Reset wish: fresh token, clear rows, clear ignored_users
Remove Search Again from wish pages and rely on Reset Seen Results
```

## Disposition

The ordinary-mode prototype is strong enough to retire page replacement as the presumed minimum, but not strong enough to select an upstream implementation. The remaining work is product policy and native integration rather than core token mechanics.
