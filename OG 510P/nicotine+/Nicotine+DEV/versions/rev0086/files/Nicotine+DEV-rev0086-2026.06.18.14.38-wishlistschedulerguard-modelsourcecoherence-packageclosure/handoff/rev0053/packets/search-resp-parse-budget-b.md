# SEARCH-RESP-PARSE-BUDGET-B current-upstream gate

## Minimum claim

After token validation, FileSearchResponse parsing should bound accepted public/private result-list counts before materializing accepted result bodies.

## Current-source gate question

In a fresh current upstream checkout, is the selected invariant for SEARCH-RESP-PARSE-BUDGET-B already native, absent, or superseded by an equivalent fix?

## Selected marker triage set

- `pynicotine/slskmessages.py` :: `MAX_SEARCH_RESPONSE_RESULT_COUNT`
- `pynicotine/slskmessages.py` :: `accepted_result_count > MAX_SEARCH_RESPONSE_RESULT_COUNT`
- `pynicotine/slskmessages.py` :: `max_results=MAX_SEARCH_RESPONSE_RESULT_COUNT`

Marker presence is not sufficient for filing. It only helps decide whether current source may already contain the selected invariant. Final status requires the fixed regression listed below.

```text
field capsule: handoff/rev0052/fields/search-resp-parse-budget-b.md
claim capsule: handoff/rev0050/capsules/search-resp-parse-budget-b.md
source anchor capsule: handoff/rev0051/anchors/search-resp-parse-budget-b.md
maintainer report: report_drafts/SEARCH-RESP-PARSE-BUDGET-B-PRODUCTION-READY-MAINTAINER-REPORT-REV0042.md
regression artifact(s): maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py
```

## rev0053 disposition

retain production-gated packet; do not externally file until current checkout gate is answered
