# SEARCH-RESP-01B-BUDDY current-upstream gate

## Minimum claim

For buddy-mode searches, accepted FileSearchResponse messages should be bound to the request-time buddy snapshot used to fan out UserSearch requests.

## Current-source gate question

In a fresh current upstream checkout, is the selected invariant for SEARCH-RESP-01B-BUDDY already native, absent, or superseded by an equivalent fix?

## Selected marker triage set

- `pynicotine/search.py` :: `users = tuple(core.buddies.users)`
- `pynicotine/search.py` :: `search.mode == "buddies" and search.users is not None`

Marker presence is not sufficient for filing. It only helps decide whether current source may already contain the selected invariant. Final status requires the fixed regression listed below.

```text
field capsule: handoff/rev0052/fields/search-resp-01b-buddy.md
claim capsule: handoff/rev0050/capsules/search-resp-01b-buddy.md
source anchor capsule: handoff/rev0051/anchors/search-resp-01b-buddy.md
maintainer report: report_drafts/SEARCH-RESP-01B-PRODUCTION-READY-MAINTAINER-REPORT-REV0040.md
regression artifact(s): maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py
```

## rev0053 disposition

retain production-gated packet; do not externally file until current checkout gate is answered
