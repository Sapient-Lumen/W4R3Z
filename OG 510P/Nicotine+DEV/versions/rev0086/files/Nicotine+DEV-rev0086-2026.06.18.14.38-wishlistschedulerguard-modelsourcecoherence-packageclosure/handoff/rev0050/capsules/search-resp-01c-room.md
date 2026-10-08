# SEARCH-RESP-01C-ROOM — room-mode response source snapshot when available

## Filing position

Bundle: `03-search-response-source-admission`. Production gate: rev0043. Rev0050 status: unchanged production-gated packet with claim-capsule QA.

## Minimum claim

For room-mode searches with a usable non-empty joined-room member snapshot, accepted FileSearchResponse messages can be bound to that request-time snapshot while preserving broad compatibility when no snapshot exists.

## Selected invariant / fix shape

Snapshot-bound room admission only when a local membership snapshot is available; otherwise preserve current broad compatibility.

## Evidence chain

rev0043 room-scope regression/compat smoke/source trace; rev0046 integrated stack gate.

Primary report:

```text
report_drafts/SEARCH-RESP-01C-ROOM-PRODUCTION-READY-MAINTAINER-REPORT-REV0043.md
```

Regression artifact(s):

```text
maintainer_artifacts/search-resp-01/test_search_response_room_scope_fixed_regression.py
```

## Non-claims / filing guardrails

Not empty-room crash behavior; not buddy/user mode; not parser budgets.

## Public-overlap boundary

Separate from 3.3.11 RC empty-room crash release-note item.

## Source-refresh caveat

The capsule relies on archived rev0003 source-lane evidence and the rev0046 integrated selected-patch stack gate. Refresh against a newer upstream checkout before external action.
