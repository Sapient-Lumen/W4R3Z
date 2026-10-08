# SEARCH-AGAIN-SELF-01 current disposition — rev0077

## Decision

The master-line Search Again flow contains a confirmed low-severity correctness defect in self-user searches. When an older search is resent after a newer search has advanced the component-wide allocator token, Nicotine+ sends the older search's token on the wire but records the newer allocator token in `_own_tokens`.

The selected **research-only** correction is:

```diff
-                self._own_tokens.add(self.token)
+                self._own_tokens.add(search.token)
```

This aligns the local authorization record with the token already placed in `UserSearch`. It does not select a broader Search Again refresh design and is not upstream contribution material.

## Exact failing sequence

Let search tab **A** own token `700001`. A later unrelated search advances `Search.token` to **B**, `700099`.

```text
1. Search Again invokes send_search_request(A).
2. The stored SearchRequest for A is selected.
3. UserSearch(..., A, ...) is sent.
4. Current code records B in _own_tokens.
5. The local looped-back request arrives with A.
6. _process_search_request() cannot find A and suppresses the response.
7. B remains authorized until consumed or cleared on disconnect.
```

The stale B entry can also cause one later self-originated request carrying B to be treated as intentionally authorized even though that request was not the older resend. The demonstrated consequence is local result suppression and state misclassification, not a remote privilege boundary failure.

## Why first-send testing missed it

On an initial search, the allocator token and the new `SearchRequest.token` are the same value. The old and corrected expressions therefore behave identically. Divergence requires all of these conditions:

1. a user-mode search targeting the local username;
2. another search that advances the component allocator;
3. Search Again on the older tab; and
4. processing of the looped-back request token.

The rev0077 matrix includes this interleaving, an initial-send compatibility control, and a non-self control.

## Provenance

The token mismatch was introduced as a stale ownership reference during commit `d8ffe30c773ab059899b825eeeb5c073833e6f3d` on 2025-05-02. That refactor changed request senders to receive a stored `search` and changed the wire token from `self.token` to `search.token`, but the adjacent `_own_tokens.add(self.token)` expression retained its pre-refactor owner.

`git blame` at executable proxy `f4e17d59783dbc48ea31d2e899a681e2dd1ed500` confirms the split provenance: the wire-token line belongs to the Search Again refactor, while the authorization write still traces to 2024.

## Source scope

```text
visible public master head: a96406e7aa285a3fb2a3e35900686d164a22bf02
bundled executable proxy:   f4e17d59783dbc48ea31d2e899a681e2dd1ed500
proxy distance:             6 commits / 8 changed files overall
```

The current public source still contains the exact relevant flow: `send_search_request()` resolves a stored request, `_send_peer_search_request()` records `self.token` while sending `search.token`, and `_process_search_request()` checks and consumes the incoming token. The executable result is from the bundled proxy, not a claim that the whole source tree exactly equals the visible head.

## Validation result

```text
source invariants:                 12/12 pass
classified expectations:          26/26 pass
compile checks:                    14/14 pass
baseline upstream units:           60 passed, 1 skipped
selected upstream units:           60 passed, 1 skipped
patch dry-run/application:          pass/pass
```

`test_i18n.py` was explicitly excluded in both unit states because `msgfmt` is unavailable.

## Disposition

```text
behavior:       confirmed
impact:         low-severity correctness and state accounting
selected scope: one-line self-user token binding repair
security route: not applicable on current evidence
broader epoch:  unresolved and intentionally unselected
```

The packet is closed as a research disposition because the narrow repair is mechanically supported. The separate refresh-epoch design remains open.
