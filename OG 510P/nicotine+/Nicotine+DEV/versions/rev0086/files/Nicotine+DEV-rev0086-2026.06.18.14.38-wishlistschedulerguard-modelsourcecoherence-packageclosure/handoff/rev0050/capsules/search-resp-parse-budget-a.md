# SEARCH-RESP-PARSE-BUDGET-A — compressed username-prefix cap before token reachability

## Filing position

Bundle: `04-search-response-parser-budget`. Production gate: rev0041. Rev0050 status: unchanged production-gated packet with claim-capsule QA.

## Minimum claim

The FileSearchResponse parser should reject overlong compressed username prefixes before inflating username_len + 4 bytes solely to reach an invalid or unknown token.

## Selected invariant / fix shape

Add a local maximum username-prefix length before prefix inflation to token.

## Evidence chain

rev0041 prefix-budget regression/source trace; rev0046 integrated stack gate.

Primary report:

```text
report_drafts/SEARCH-RESP-PARSE-BUDGET-A-PRODUCTION-READY-MAINTAINER-REPORT-REV0041.md
```

Regression artifact(s):

```text
maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py
```

## Non-claims / filing guardrails

Not global uncompressed-message-size enforcement, result-count budget, or source admission.

## Public-overlap boundary

Separate from broad uncompressed network-message release-note wording.

## Source-refresh caveat

The capsule relies on archived rev0003 source-lane evidence and the rev0046 integrated selected-patch stack gate. Refresh against a newer upstream checkout before external action.
