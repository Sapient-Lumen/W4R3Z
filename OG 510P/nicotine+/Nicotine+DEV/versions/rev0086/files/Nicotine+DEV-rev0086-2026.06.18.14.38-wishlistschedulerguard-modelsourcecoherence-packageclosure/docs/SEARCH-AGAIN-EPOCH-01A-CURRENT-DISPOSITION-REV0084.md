# SEARCH-AGAIN-EPOCH-01A current disposition — rev0084

## Disposition

```text
status: open-native-ui-validation
selected patch: none
security route: not applicable
severity: low product correctness / bounded local request waste
```

The same-token implementation remains nonproductive once an ordinary search
page reaches `max_displayed_results`: a click resends the old request, the still
full page rejects the first returning response, and response admission is
retired again without adding a row.

The current research candidate uses a fresh wire token while preserving the
same logical request and GUI page. It synchronously removes old response
admission, moves the core token key, rekeys the GUI lookup, clears
result-generation state, and only then sends the new request. Old parsed or
unparsed responses no longer resolve the refreshed page.

Rev0084 also removes a latent identity assumption from this path. A desktop
notification action now addresses a stable non-reused GUI page ID rather than a
wire token. Ordinary pages rarely emit result notifications, but keeping page
identity independent of the wire epoch makes the rekey contract coherent across
all refreshable `SearchRequest` pages.

## What is established

- Global, room, buddy, and user pages are normal `SearchRequest` owners.
- The result-cap dead end is reproducible on the bundled master proxy.
- A same-page fresh-token rekey has explicit core-before-GUI-before-send order.
- No old-to-new token alias registry is required.
- Repeated rekeys retain one token map entry and one logical page map entry.
- Baseline and candidate upstream unit lanes both pass `60 passed, 1 skipped`.

## What remains open

Native GTK3 and GTK4 behavior has not been executed in this environment. Focus,
active-tab identity, unread markers, filters, grouping, sort, expansion,
selection, scroll, rapid repeat, and online-to-offline transitions remain real
integration gates. The executable source is also the bundled `f4e17d5…` proxy;
current public flow was reviewed separately, not executed as an exact public
head whole tree.

Research artifact:
`maintainer_artifacts/search-rekey-01/search_again_stable_notification_rekey_rev0084.patch`.
It is not selected for upstream use.
