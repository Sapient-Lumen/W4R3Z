# SEARCH-RESP-01A user-scope production gate — rev0039

## Lead decision

Promote the narrow user-scoped part of SEARCH-RESP-01 as **SEARCH-RESP-01A / U-163A**: a `FileSearchResponse` for a user search should be accepted only from a peer named in the original `SearchRequest.users` set.

This revision intentionally does **not** promote the full rev0013 bundle as one report. Room/buddy membership and parser-budget/materialization behavior remain real hardening targets, but mixing them with the direct user-source gate made the report harder to verify and risked over-claiming compatibility details.

## Current behavior reproduced

The rev0013 current-behavior witness still passes on unpatched archived source:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

The new fixed-behavior regression fails on unpatched archived source in the two expected user-scope cases:

```text
github-tag-3.3.10:   2 failed / 5 passed
github-branch-3.3.x: 2 failed / 5 passed
github-branch-master: 2 failed / 5 passed
```

Those two failures are:

1. a user-scoped response from `unexpected_peer` is not rejected when the original search targeted `expected_peer`;
2. a malformed/empty user-scoped request state fails open instead of closed.

## Selected fix shape

The selected patch is deliberately small:

```python
if search.mode == "user":
    expected_users = search.users or ()

    if username not in expected_users:
        msg.token = None
        return
```

Placement differs slightly by source lane:

- 3.3.10 / 3.3.x: after the token/search lookup and before network-filter checks;
- master: after the `search is None` guard and before wishlist ignore/network-filter checks.

## Patch gate

```text
selected user-scope patch + rev0039 fixed regression:
  github-tag-3.3.10:   7 passed
  github-branch-3.3.x: 7 passed
  github-branch-master: 7 passed

selected user-scope patch + old rev0013 current witness:
  github-tag-3.3.10:   1 failed / 5 passed
  github-branch-3.3.x: 1 failed / 5 passed
  github-branch-master: 1 failed / 5 passed
```

The old witness failure is the expected inversion of `test_user_scoped_file_search_response_from_unrequested_peer_is_accepted`. The room-scoped acceptance, token-shape, private-list materialization, invalid-token prefix decompression, and full-list materialization witnesses remain true under the narrow patch and are therefore split to backlog.

## Boundaries

This packet is about peer-result **source admission** for direct user searches. It is not code execution, not standalone file disclosure, and not a claim that every search token is easily guessed in every deployment. It also does not attempt to solve room membership freshness or parser-budget behavior.

## Maintainer files

```text
maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py
report_drafts/SEARCH-RESP-01A-PRODUCTION-READY-MAINTAINER-REPORT-REV0039.md
report_drafts/SEARCH-RESP-01A-SELECTED-FIX-SKELETON-REV0039.md
report_drafts/SEARCH-RESP-01A-SELECTED-PATCH-REV0039-3.3.10.diff
report_drafts/SEARCH-RESP-01A-SELECTED-PATCH-REV0039-master.diff
tools/apply_search_resp_user_scope_patch_rev0039.py
```
