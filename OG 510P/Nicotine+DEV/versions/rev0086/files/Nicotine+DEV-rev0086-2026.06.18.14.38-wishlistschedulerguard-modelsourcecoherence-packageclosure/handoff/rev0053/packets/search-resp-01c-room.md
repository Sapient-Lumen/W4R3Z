# SEARCH-RESP-01C-ROOM current-upstream gate

## Minimum claim

For room-mode searches with a usable non-empty joined-room member snapshot, accepted FileSearchResponse messages can be bound to that request-time snapshot while preserving broad compatibility when no snapshot exists.

## Current-source gate question

In a fresh current upstream checkout, is the selected invariant for SEARCH-RESP-01C-ROOM already native, absent, or superseded by an equivalent fix?

## Selected marker triage set

- `pynicotine/search.py` :: `room_obj = getattr`
- `pynicotine/search.py` :: `search.mode == "rooms" and search.users is not None`

Marker presence is not sufficient for filing. It only helps decide whether current source may already contain the selected invariant. Final status requires the fixed regression listed below.

```text
field capsule: handoff/rev0052/fields/search-resp-01c-room.md
claim capsule: handoff/rev0050/capsules/search-resp-01c-room.md
source anchor capsule: handoff/rev0051/anchors/search-resp-01c-room.md
maintainer report: report_drafts/SEARCH-RESP-01C-ROOM-PRODUCTION-READY-MAINTAINER-REPORT-REV0043.md
regression artifact(s): maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py
```

## rev0053 disposition

retain production-gated packet; do not externally file until current checkout gate is answered
