# Filing-field capsule — SEARCH-RESP-PARSE-BUDGET-B

Bundle: `04-search-response-parser-budget`. Production gate: rev0042. Rev0052 status: unchanged production-gated packet, now filing-field-mapped.

## Minimum claim field

After token validation, FileSearchResponse parsing should bound accepted public/private result-list counts before materializing accepted result bodies.

## Reviewer question

Does accepted-response parsing reject over-budget public/private result counts before materializing the full body?

## Selected fix / invariant field

Apply a shared public+private result-row budget while preserving normal small responses.

## Evidence field map

|field|artifact|
|---|---|
|Primary report|`report_drafts/SEARCH-RESP-PARSE-BUDGET-B-PRODUCTION-READY-MAINTAINER-REPORT-REV0042.md`|
|Fix skeleton|`report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-FIX-SKELETON-REV0042.md`|
|Patch/apply basis|`report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-3.3.10.diff`<br>`report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-3.3.x.diff`<br>`report_drafts/SEARCH-RESP-PARSE-BUDGET-B-SELECTED-PATCH-REV0042-master.diff`<br>`tools/apply_search_resp_result_budget_patch_rev0042.py`|
|Regression artifact(s)|`maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py`|
|Rerun evidence|`evidence/rev0042-search-resp-result-budget-rerun-matrix.txt`<br>`evidence/rev0046-strict-bundle-integrated-rerun-matrix.txt`|
|Claim capsule|`handoff/rev0050/capsules/search-resp-parse-budget-b.md`|
|Source-anchor capsule|`handoff/rev0051/anchors/search-resp-parse-budget-b.md`|
|Anchor row count|`15`|
|Anchor files|`pynicotine/slskmessages.py`|

## Non-claim / public-overlap boundary

Not source admission, UI display policy, or global network-message caps.

Separate from prefix-cap packet and broad uncompressed-message release-note wording.

## Filing guardrail

This field capsule is a review map, not a new vulnerability packet and not a current-upstream proof. Use it with the rev0050 claim capsule and rev0051 archived-source anchor capsule; refresh a current upstream checkout before external filing.
