# SEARCH-AGAIN-EPOCH-01A current disposition — rev0083

## Scope

Search Again for pages whose GUI mode is `global`, `rooms`, `buddies`, or `user`.
Manual and scheduled wishlist pages are no longer hidden inside the word
“ordinary”; they are tracked separately because both use wishlist GUI semantics.

## Confirmed defect

The current same-token resend is nonproductive after a page reaches the display
cap. Below the cap it merges only results from usernames not already represented
on the page.

## Current research candidate

The candidate retains the same logical request and page while rotating the wire
response token. It retires old admission, rekeys the core request and GUI page
synchronously, clears result-generation state, then resends through the existing
mode-specific path.

Rev0083 does not change that ordinary-mode mechanism. It corrects who is allowed
to enter it: the core method now makes the only eligibility decision, based on
`SearchRequest.mode`. The GUI no longer maintains a second classifier.

No patch is selected for upstream use.

## Remaining evidence

```text
native GTK3 and GTK4 page behavior
focus, active tab, unread marker, filters, grouping, sort, expansion, and scroll
rapid repeat, close/reopen, and online-to-offline transitions
exact execution on a fresh current public-master whole-tree intake
measured practical resource impact before any stronger severity claim
```

## Disposition

```text
behavior: confirmed
non-wishlist candidate mechanics: source/model viable
wishlist hybrid accidentally included by prior wording: corrected
security route: not applicable; low-severity correctness/resource hygiene
selected patch: none
status: open native-UI validation
```

Executable evidence:

```text
data/rev0083_search_mode_summary.json
data/rev0083_search_mode_source_invariants.csv
data/rev0083_search_mode_test_matrix.csv
maintainer_artifacts/search-rekey-01/search_again_mode_owned_rekey_rev0083.patch
```
