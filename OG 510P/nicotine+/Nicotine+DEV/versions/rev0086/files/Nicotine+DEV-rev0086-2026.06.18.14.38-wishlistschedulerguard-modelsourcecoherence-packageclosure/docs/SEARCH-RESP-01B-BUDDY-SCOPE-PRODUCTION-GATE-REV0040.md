# SEARCH-RESP-01B buddy-scope production gate — rev0040

## Lead decision

Promote the buddy-mode part of the rev0039 held SEARCH-RESP-01B row as **SEARCH-RESP-01B-BUDDY / U-163B**: a `FileSearchResponse` for a buddy search should be accepted only from the request-time buddy source snapshot.

This is intentionally narrower than “all room/buddy source binding.” Room searches are server-mediated through `RoomSearch`; the local client may not have a complete, fresh, protocol-authenticated room source set at response time. Buddy searches are different: Nicotine+ issues `UserSearch` messages to the local buddy list, so a snapshot is available without changing global or room compatibility.

## Current behavior reproduced

The historical rev0013 SEARCH-RESP-01 witness still passes on unpatched archived source:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

The new rev0040 buddy fixed-behavior regression fails on unpatched archived source in four expected places:

```text
github-tag-3.3.10:   4 failed / 4 passed
github-branch-3.3.x: 4 failed / 4 passed
github-branch-master: 4 failed / 4 passed
```

Those failures prove that current source:

1. accepts a buddy-scoped response from `not_a_buddy` when the request snapshot contains only `buddy_a` and `buddy_b`;
2. fails open when a buddy-mode `SearchRequest` lacks a source snapshot;
3. creates a buddy search without storing the buddy source snapshot in `SearchRequest.users`;
4. accepts a response from a user added after the snapshot rather than the request-time source set.

## Selected fix shape

The selected patch is a source-set binding, not a broad-mode ban:

```python
# request side
users = tuple(core.buddies.users)

# send side
users = search.users if search.users is not None else tuple(core.buddies.users)
for username in users:
    core.send_message_to_server(UserSearch(username, search.token, search.term_transmitted))

# response side
if search.mode == "user":
    expected_users = search.users or ()

    if username not in expected_users:
        msg.token = None
        return

elif search.mode == "buddies" and search.users is not None:
    if username not in search.users:
        msg.token = None
        return
```

The same response guard also preserves the rev0039 direct user-source fix. Patch placement differs slightly between the 3.3.10/3.3.x lanes and master because master routes outgoing searches through `send_search_request()`.

## Patch gate

```text
selected source-set patch + rev0040 buddy fixed regression:
  github-tag-3.3.10:   8 passed
  github-branch-3.3.x: 8 passed
  github-branch-master: 8 passed

selected source-set patch + old rev0013 current witness:
  github-tag-3.3.10:   1 failed / 5 passed
  github-branch-3.3.x: 1 failed / 5 passed
  github-branch-master: 1 failed / 5 passed
```

The old witness failure is the expected inversion of the direct user-source acceptance assertion from rev0039. The old room-scoped acceptance and parser-materialization witnesses remain true under the selected patch and therefore stay split to backlog.

## Boundaries

This packet is about peer-result **source admission** for buddy searches. It is not code execution, not standalone file disclosure, and not a claim that every search token is easily guessed in every deployment. It does not attempt to solve room membership freshness or parser-budget behavior.

## Maintainer files

```text
maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py
report_drafts/SEARCH-RESP-01B-PRODUCTION-READY-MAINTAINER-REPORT-REV0040.md
report_drafts/SEARCH-RESP-01B-SELECTED-FIX-SKELETON-REV0040.md
report_drafts/SEARCH-RESP-01B-SELECTED-PATCH-REV0040-3.3.10.diff
report_drafts/SEARCH-RESP-01B-SELECTED-PATCH-REV0040-3.3.x.diff
report_drafts/SEARCH-RESP-01B-SELECTED-PATCH-REV0040-master.diff
tools/apply_search_resp_buddy_source_patch_rev0040.py
```
