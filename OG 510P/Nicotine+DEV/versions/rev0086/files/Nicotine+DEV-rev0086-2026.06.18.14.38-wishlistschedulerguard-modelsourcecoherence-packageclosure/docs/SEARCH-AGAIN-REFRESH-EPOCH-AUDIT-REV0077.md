# Search Again refresh-epoch audit — rev0077

## Heart of the design problem

The UI label “Search Again” suggests replacement or refresh. Current master instead performs another network fan-out under the existing page token and leaves the result model intact. The page also rejects a second response from any username already present. Consequently, the command is closer to **retry missing peers and discover newly responding users** than to refreshing existing results.

That behavior may be useful, but its identity should be explicit. Clearing results without changing the wire token is unsafe as a refresh model because late replies from the old attempt are indistinguishable from replies to the new attempt.

## Executable policy models

| Policy | Existing results | Old token | Late old response | Result semantics |
|---|---|---|---|---|
| Current: same token, no clear | retained | accepted | merged subject to username dedup | retry/union; first result per username remains frozen |
| Same token, clear | removed | accepted | can win the new page | ambiguous and not a true epoch |
| New token, no clear | retained | retired | rejectable | union; existing usernames still frozen |
| New token, clear, retire old | removed | retired | rejectable | true replacement epoch |

The rev0077 pure model proves all four outcomes independently of GTK.

## Why a one-line token rotation is not selected

The current token is simultaneously used as:

- network response admission identity;
- key into `Search.searches`;
- identity carried by the result page;
- argument to `send_search_request()` and `remove_search()`;
- event/plugin-visible search identity in several paths.

Changing it on resend without coordinating those owners can orphan the page, leave an old token allowed, route new responses to no search, or make page removal retire the wrong token.

## Candidate architecture for a true refresh

A future design should separate two concepts:

```text
logical_search_id
  stable identity of the UI tab, filters, history, and plugin-visible search

wire_epoch_token
  replaceable identity of one network fan-out and its admissible responses
```

A replacement epoch would then be one transaction:

1. allocate a fresh wire token;
2. insert the new token-to-logical-search mapping;
3. allow the new response token in the network layer;
4. retire and remove the old token mapping;
5. clear the page model and its username deduplication state;
6. send the new fan-out;
7. reject late responses carrying the retired token; and
8. preserve explicit behavior for wishlist searches, buddy-list changes, plugins, page close, reconnect, and failure during the transition.

The ordering should be tested for re-entrant events and partial failure. A generation number may be clearer than mutating the page's current token in place.

## Product decision that is still missing

Before implementation, maintainers should choose and name one of these semantics:

- **Retry:** keep existing rows and ask the same logical audience again; existing users remain deduplicated.
- **Refresh:** replace visible results with a new wire epoch and reject late old replies.
- **Merge:** keep existing rows but allow a newer response from the same user to replace or merge that user's rows.

Current code implements a restricted Retry but the user-facing word “Again” can reasonably be read as Refresh. The cube does not choose product semantics on behalf of maintainers.

## Boundary with SEARCH-RESP-01B

Buddy-list mutation makes this epoch question visible in another form. The current resend resolves the live buddy list, while the historical snapshot proposal would preserve the initial audience. A true epoch design should decide whether a resend targets the current buddy set or the original set and should bind any response-admission consistency check to that same epoch decision.
