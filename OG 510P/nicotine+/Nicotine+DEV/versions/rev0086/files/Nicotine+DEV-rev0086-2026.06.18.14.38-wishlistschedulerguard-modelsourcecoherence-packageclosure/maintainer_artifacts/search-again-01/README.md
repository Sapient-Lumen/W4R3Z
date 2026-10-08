# SEARCH-AGAIN-SELF-01 research packet

This packet isolates a master-only correctness defect in repeated self-user searches.

Current `Search._send_peer_search_request()` sends `search.token` on the wire but records `self.token` in `_own_tokens`. Those values match on the first search. They diverge when **Search Again** resends an older tab after a newer search has advanced the component-wide token. The incoming self-request gate checks the wire token, does not find it, and suppresses the local response.

The selected research correction is the one-line `self._own_tokens.add(search.token)` patch. It aligns the local gate with the token already sent in `UserSearch`; it does not change ordinary first-send behavior or non-self searches.

The epoch files deliberately do not select a broader Search Again redesign. Current Search Again reuses the page token without clearing results, while the result page rejects a second response from a username already present. A true refresh needs a policy for wire-token rotation, old-token retirement, clearing versus union, late responses, page re-keying, wishlist behavior, and plugin-visible identity.

## Roles

```text
search_again_harness.py
  shared real-component and pure-epoch harness

test_search_again_self_token_current_behavior.py
  current defect witnesses and first-send compatibility control

test_search_again_self_token_selected_policy.py
  selected one-line policy expectations

test_search_again_epoch_source_semantics.py
  AST witnesses for same-token/no-clear/per-user-dedup behavior

test_search_again_epoch_models.py
  policy countermodels; no production implementation selected

master-search-again-self-token.patch
  research-only one-line correction
```

All files are research-only and must not be copied into an upstream contribution.
