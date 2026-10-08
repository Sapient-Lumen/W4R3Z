# SEARCH-RESP-01A current-upstream gate

## Minimum claim

For direct user searches, FileSearchResponse acceptance should require msg.username to be in the original requested user set for that token.

## Current-source gate question

In a fresh current upstream checkout, is the selected invariant for SEARCH-RESP-01A already native, absent, or superseded by an equivalent fix?

## Selected marker triage set

- `pynicotine/search.py` :: `expected_users = search.users`
- `pynicotine/search.py` :: `username not in expected_users`

Marker presence is not sufficient for filing. It only helps decide whether current source may already contain the selected invariant. Final status requires the fixed regression listed below.

```text
field capsule: handoff/rev0052/fields/search-resp-01a.md
claim capsule: handoff/rev0050/capsules/search-resp-01a.md
source anchor capsule: handoff/rev0051/anchors/search-resp-01a.md
maintainer report: report_drafts/SEARCH-RESP-01A-PRODUCTION-READY-MAINTAINER-REPORT-REV0039.md
regression artifact(s): maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py
```

## rev0053 disposition

retain production-gated packet; do not externally file until current checkout gate is answered
