# SEARCH-RESP-PARSE-BUDGET-A current-upstream gate

## Minimum claim

The FileSearchResponse parser should reject overlong compressed username prefixes before inflating username_len + 4 bytes solely to reach an invalid or unknown token.

## Current-source gate question

In a fresh current upstream checkout, is the selected invariant for SEARCH-RESP-PARSE-BUDGET-A already native, absent, or superseded by an equivalent fix?

## Selected marker triage set

- `pynicotine/slskmessages.py` :: `MAX_SEARCH_RESPONSE_USERNAME_LENGTH`
- `pynicotine/slskmessages.py` :: `username_len > MAX_SEARCH_RESPONSE_USERNAME_LENGTH`

Marker presence is not sufficient for filing. It only helps decide whether current source may already contain the selected invariant. Final status requires the fixed regression listed below.

```text
field capsule: handoff/rev0052/fields/search-resp-parse-budget-a.md
claim capsule: handoff/rev0050/capsules/search-resp-parse-budget-a.md
source anchor capsule: handoff/rev0051/anchors/search-resp-parse-budget-a.md
maintainer report: report_drafts/SEARCH-RESP-PARSE-BUDGET-A-PRODUCTION-READY-MAINTAINER-REPORT-REV0041.md
regression artifact(s): maintainer_artifacts/search-resp-01/test_search_response_prefix_budget_fixed_regression.py
```

## rev0053 disposition

retain production-gated packet; do not externally file until current checkout gate is answered
