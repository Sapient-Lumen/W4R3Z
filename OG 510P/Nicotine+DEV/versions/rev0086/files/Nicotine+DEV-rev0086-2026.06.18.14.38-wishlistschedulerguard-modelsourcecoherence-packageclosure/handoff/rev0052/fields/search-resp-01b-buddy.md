# Filing-field capsule — SEARCH-RESP-01B-BUDDY

Bundle: `03-search-response-source-admission`. Production gate: rev0040. Rev0052 status: unchanged production-gated packet, now filing-field-mapped.

## Minimum claim field

For buddy-mode searches, accepted FileSearchResponse messages should be bound to the request-time buddy snapshot used to fan out UserSearch requests.

## Reviewer question

Is buddy fanout and response admission bound to the same request-time buddy snapshot, not to a later live buddy list?

## Selected fix / invariant field

Snapshot core.buddies.users at search creation, send from that snapshot, and admit responses from that snapshot.

## Evidence field map

|field|artifact|
|---|---|
|Primary report|`report_drafts/SEARCH-RESP-01B-PRODUCTION-READY-MAINTAINER-REPORT-REV0040.md`|
|Fix skeleton|`report_drafts/SEARCH-RESP-01B-SELECTED-FIX-SKELETON-REV0040.md`|
|Patch/apply basis|`report_drafts/SEARCH-RESP-01B-SELECTED-PATCH-REV0040-3.3.10.diff`<br>`report_drafts/SEARCH-RESP-01B-SELECTED-PATCH-REV0040-3.3.x.diff`<br>`report_drafts/SEARCH-RESP-01B-SELECTED-PATCH-REV0040-master.diff`<br>`tools/apply_search_resp_buddy_source_patch_rev0040.py`|
|Regression artifact(s)|`maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py`|
|Rerun evidence|`evidence/rev0040-search-resp-buddy-scope-rerun-matrix.txt`<br>`evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt`|
|Claim capsule|`handoff/rev0050/capsules/search-resp-01b-buddy.md`|
|Source-anchor capsule|`handoff/rev0051/anchors/search-resp-01b-buddy.md`|
|Anchor row count|`18`|
|Anchor files|`pynicotine/search.py`|

## Non-claim / public-overlap boundary

Not live buddy-list-at-response-time enforcement; not room membership or parser budget.

Separate from direct user and room source models.

## Filing guardrail

This field capsule is a review map, not a new vulnerability packet and not a current-upstream proof. Use it with the rev0050 claim capsule and rev0051 archived-source anchor capsule; refresh a current upstream checkout before external filing.
