# Filing-field capsule — SEARCH-RESP-PARSE-BUDGET-A

Bundle: `04-search-response-parser-budget`. Production gate: rev0041. Rev0052 status: unchanged production-gated packet, now filing-field-mapped.

## Minimum claim field

The FileSearchResponse parser should reject overlong compressed username prefixes before inflating username_len + 4 bytes solely to reach an invalid or unknown token.

## Reviewer question

Does parsing cap the compressed username prefix before inflating enough bytes to reach a token?

## Selected fix / invariant field

Add a local maximum username-prefix length before prefix inflation to token.

## Evidence field map

|field|artifact|
|---|---|
|Primary report|`report_drafts/SEARCH-RESP-PARSE-BUDGET-A-PRODUCTION-READY-MAINTAINER-REPORT-REV0041.md`|
|Fix skeleton|`report_drafts/SEARCH-RESP-PARSE-BUDGET-A-SELECTED-FIX-SKELETON-REV0041.md`|
|Patch/apply basis|`report_drafts/SEARCH-RESP-PARSE-BUDGET-A-SELECTED-PATCH-REV0041-3.3.10.diff`<br>`report_drafts/SEARCH-RESP-PARSE-BUDGET-A-SELECTED-PATCH-REV0041-3.3.x.diff`<br>`report_drafts/SEARCH-RESP-PARSE-BUDGET-A-SELECTED-PATCH-REV0041-master.diff`<br>`tools/apply_search_resp_prefix_budget_patch_rev0041.py`|
|Regression artifact(s)|`maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py`|
|Rerun evidence|`evidence/rev0041-search-resp-prefix-budget-rerun-matrix.txt`<br>`evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt`|
|Claim capsule|`handoff/rev0050/capsules/search-resp-parse-budget-a.md`|
|Source-anchor capsule|`handoff/rev0051/anchors/search-resp-parse-budget-a.md`|
|Anchor row count|`12`|
|Anchor files|`pynicotine/slskmessages.py`|

## Non-claim / public-overlap boundary

Not global uncompressed-message-size enforcement, result-count budget, or source admission.

Separate from broad uncompressed network-message release-note wording.

## Filing guardrail

This field capsule is a review map, not a new vulnerability packet and not a current-upstream proof. Use it with the rev0050 claim capsule and rev0051 archived-source anchor capsule; refresh a current upstream checkout before external filing.
