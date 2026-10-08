# Filing-field capsule — SEARCH-RESP-01C-ROOM

Bundle: `03-search-response-source-admission`. Production gate: rev0043. Rev0052 status: unchanged production-gated packet, now filing-field-mapped.

## Minimum claim field

For room-mode searches with a usable non-empty joined-room member snapshot, accepted FileSearchResponse messages can be bound to that request-time snapshot while preserving broad compatibility when no snapshot exists.

## Reviewer question

When a non-empty joined-room member snapshot exists, is room response admission bound to that snapshot while broad compatibility is preserved when no usable snapshot exists?

## Selected fix / invariant field

Snapshot-bound room admission only when a local membership snapshot is available; otherwise preserve current broad compatibility.

## Evidence field map

|field|artifact|
|---|---|
|Primary report|`report_drafts/SEARCH-RESP-01C-ROOM-PRODUCTION-READY-MAINTAINER-REPORT-REV0043.md`|
|Fix skeleton|`report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-FIX-SKELETON-REV0043.md`|
|Patch/apply basis|`report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-3.3.10.diff`<br>`report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-3.3.x.diff`<br>`report_drafts/SEARCH-RESP-01C-ROOM-SELECTED-PATCH-REV0043-master.diff`<br>`tools/apply_search_resp_room_scope_patch_rev0043.py`|
|Regression artifact(s)|`maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py`|
|Rerun evidence|`evidence/rev0043-search-resp-room-scope-rerun-matrix.txt`<br>`evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt`|
|Claim capsule|`handoff/rev0050/capsules/search-resp-01c-room.md`|
|Source-anchor capsule|`handoff/rev0051/anchors/search-resp-01c-room.md`|
|Anchor row count|`18`|
|Anchor files|`pynicotine/search.py`|

## Non-claim / public-overlap boundary

Not empty-room crash behavior; not buddy/user mode; not parser budgets.

Separate from 3.3.11 RC empty-room crash release-note item.

## Filing guardrail

This field capsule is a review map, not a new vulnerability packet and not a current-upstream proof. Use it with the rev0050 claim capsule and rev0051 archived-source anchor capsule; refresh a current upstream checkout before external filing.
