# SEARCH-RESP-PARSE-BUDGET-B — accepted result-list count budget

## Filing position

Bundle: `04-search-response-parser-budget`. Production gate: rev0042. Rev0050 status: unchanged production-gated packet with claim-capsule QA.

## Minimum claim

After token validation, FileSearchResponse parsing should bound accepted public/private result-list counts before materializing accepted result bodies.

## Selected invariant / fix shape

Apply a shared public+private result-row budget while preserving normal small responses.

## Evidence chain

rev0042 result-budget regression/source trace; rev0041 prefix regression compatibility; rev0046 integrated stack gate.

Primary report:

```text
report_drafts/SEARCH-RESP-PARSE-BUDGET-B-PRODUCTION-READY-MAINTAINER-REPORT-REV0042.md
```

Regression artifact(s):

```text
maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py
```

## Non-claims / filing guardrails

Not source admission, UI display policy, or global network-message caps.

## Public-overlap boundary

Separate from prefix-cap packet and broad uncompressed-message release-note wording.

## Source-refresh caveat

The capsule relies on archived rev0003 source-lane evidence and the rev0046 integrated selected-patch stack gate. Refresh against a newer upstream checkout before external action.
