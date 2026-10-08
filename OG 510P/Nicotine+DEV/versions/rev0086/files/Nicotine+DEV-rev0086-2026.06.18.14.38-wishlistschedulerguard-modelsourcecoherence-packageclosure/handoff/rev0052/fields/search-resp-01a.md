# Filing-field capsule — SEARCH-RESP-01A

Bundle: `03-search-response-source-admission`. Production gate: rev0039. Rev0052 status: unchanged production-gated packet, now filing-field-mapped.

## Minimum claim field

For direct user searches, FileSearchResponse acceptance should require msg.username to be in the original requested user set for that token.

## Reviewer question

For search.mode == user, is the response source bound to the requested user set without changing global/room/buddy behavior in this packet?

## Selected fix / invariant field

For search.mode == user, admit only usernames in search.users.

## Evidence field map

|field|artifact|
|---|---|
|Primary report|`report_drafts/SEARCH-RESP-01A-PRODUCTION-READY-MAINTAINER-REPORT-REV0039.md`|
|Fix skeleton|`report_drafts/SEARCH-RESP-01A-SELECTED-FIX-SKELETON-REV0039.md`|
|Patch/apply basis|`report_drafts/SEARCH-RESP-01A-SELECTED-PATCH-REV0039-3.3.10.diff`<br>`report_drafts/SEARCH-RESP-01A-SELECTED-PATCH-REV0039-master.diff`<br>`tools/apply_search_resp_user_scope_patch_rev0039.py`|
|Regression artifact(s)|`maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py`|
|Rerun evidence|`evidence/rev0039-search-resp-user-scope-rerun-matrix.txt`<br>`evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt`|
|Claim capsule|`handoff/rev0050/capsules/search-resp-01a.md`|
|Source-anchor capsule|`handoff/rev0051/anchors/search-resp-01a.md`|
|Anchor row count|`18`|
|Anchor files|`pynicotine/search.py`|

## Non-claim / public-overlap boundary

Not buddy/room policy, parser budget hardening, or all distributed-search behavior.

Separate from broad distributed-search release-note wording.

## Filing guardrail

This field capsule is a review map, not a new vulnerability packet and not a current-upstream proof. Use it with the rev0050 claim capsule and rev0051 archived-source anchor capsule; refresh a current upstream checkout before external filing.
