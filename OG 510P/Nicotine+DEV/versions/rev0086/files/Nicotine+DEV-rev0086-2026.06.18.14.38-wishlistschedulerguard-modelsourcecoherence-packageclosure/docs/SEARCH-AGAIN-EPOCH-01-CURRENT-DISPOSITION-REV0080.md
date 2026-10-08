# SEARCH-AGAIN-EPOCH-01 current disposition — rev0080

## Decision

```text
confirmed current behavior: same-token Retry/Merge
confirmed defect: Search Again is nonproductive once stored results reach the display cap
confirmed historical interaction: the original manual clear/reset path was later removed
same-token clear as epoch fix: rejected
fresh-token in-place transaction: optional high-complexity branch, not the minimum
preferred next direction: fresh-token page replacement
selected patch: none
status: open fresh-token replacement research
security route: ordinary product correctness and resource hygiene
```

Rev0080 corrects both the current product diagnosis and the cube's prior architecture claim.

## The cap dead end

The current command executes:

```python
core.search.send_search_request(self.token)
```

It does not clear stored rows or allocate a token. `send_search_request()` re-allows that token and emits the mode-specific request or fan-out.

The first response then reaches `Searches.file_search_response()`. If the existing page count is already at `max_displayed_results`, the dispatcher removes the allowed token and returns before calling the page response handler. The page remains full and unchanged.

The resulting sequence is deterministic:

```text
page count == cap
Search Again click
  re-allow unchanged token
  emit one request, or one request per buddy/user recipient
first returning response
  observe page count == cap
  retire unchanged token
  add zero rows
```

A later click repeats the same sequence. In the bounded model, 12 clicks for 32 recipients emit 384 local server-message requests and add zero display rows. This is a correctness and local resource-hygiene defect. No claim is made that it creates a practical remote denial of service or meaningful network amplification.

## Retry/Merge is also not refresh below the cap

The page accepts at most one response per username. A repeated response from a user already represented in `self.users` returns immediately. Search Again can merge newly responding users while capacity remains, but it does not refresh rows from users already present.

The label and behavior are therefore misaligned:

```text
label/user request: refresh respective search
implementation: resend same request capability and merge only previously unseen users
```

## Cross-commit cause

The Git-history provenance gate confirms this sequence from the external source bundle:

1. `d8ffe30c…` refactored search sending in preparation for Search Again.
2. `9fddad99…` added Search Again as a same-token resend. That snapshot also contained **Clear All Results**, whose handler cleared stored rows, reset the count, and re-allowed the same token.
3. `91296257…` implemented the wishlist overhaul and removed **Clear All Results** plus its handler.
4. Executable head `f4e17d59…` retains same-token Search Again and no longer has the manual reset path.

This does not prove the cap behavior was consciously intended in the first implementation. It identifies a cross-commit interaction that current-file-only review can easily miss.

## Correction to rev0078–rev0079

Those revisions correctly showed that an **in-place, failure-atomic replacement refresh** is difficult. If the visible page must remain stable while its overloaded token changes, then logical identity, token routing, complete fan-out staging, acknowledgement, disconnect, replay, and zero-result semantics matter.

That is not the only valid product definition.

If Search Again means **close one search/page lifetime and create another with a fresh token**, it can inherit the application's existing best-effort new-search semantics. It does not need to prove network output ownership before presenting the new page, because ordinary new searches do not make that promise either. Fresh-token page replacement still needs explicit rules for:

```text
filter/group/sort carry-over
selection and scroll state
tab position and focus
recently-closed/undo entries
notification and plugin-visible identity
wishlist request type, schedule, filters, and ignored users
room/user/buddy audience capture
rapid repeat and disconnect presentation
```

The old stable-identity models remain useful for the optional in-place branch, but they no longer define the minimum architecture or current open-first artifact.

## Why no patch is selected

A one-line clear before same-token resend would restore capacity but would admit delayed old responses into the cleared page and would not implement a fresh request epoch. A naive remove-then-`do_search()` sequence risks stale undo entries, tab movement, page-state loss, and incorrect wishlist handling.

The next implementation experiment should therefore be a bounded fresh-token **page replacement** prototype with explicit state carry and wishlist controls, not another queue acknowledgement layer and not a same-token clear.

## Evidence boundary

Executable tests use bundled master proxy `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`. Public master was reviewed at `a96406e7aa285a3fb2a3e35900686d164a22bf02`; the relevant GUI/core flow remains equivalent, but whole-tree exactness is not claimed for that public head.

Issue #3326 publicly framed the command as refreshing the search, and the public discussion already contains the direction to remove the current search and add a new one with a different token. Rev0080 claims no novelty for that direction. Its contributions are the cap regression proof, source-history interaction, policy split, and cube-authority correction.

All generated material remains research-only and is not upstream contribution content.
