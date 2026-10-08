# SEARCH-RESP-01B-BUDDY — buddy-mode response source snapshot

## Filing position

Bundle: `03-search-response-source-admission`. Production gate: rev0040. Rev0050 status: unchanged production-gated packet with claim-capsule QA.

## Minimum claim

For buddy-mode searches, accepted FileSearchResponse messages should be bound to the request-time buddy snapshot used to fan out UserSearch requests.

## Selected invariant / fix shape

Snapshot core.buddies.users at search creation, send from that snapshot, and admit responses from that snapshot.

## Evidence chain

rev0040 buddy-scope regression/source trace; rev0046 integrated stack gate.

Primary report:

```text
report_drafts/SEARCH-RESP-01B-PRODUCTION-READY-MAINTAINER-REPORT-REV0040.md
```

Regression artifact(s):

```text
maintainer_artifacts/search-resp-01/test_search_response_buddy_scope_fixed_regression.py
```

## Non-claims / filing guardrails

Not live buddy-list-at-response-time enforcement; not room membership or parser budget.

## Public-overlap boundary

Separate from direct user and room source models.

## Source-refresh caveat

The capsule relies on archived rev0003 source-lane evidence and the rev0046 integrated selected-patch stack gate. Refresh against a newer upstream checkout before external action.
