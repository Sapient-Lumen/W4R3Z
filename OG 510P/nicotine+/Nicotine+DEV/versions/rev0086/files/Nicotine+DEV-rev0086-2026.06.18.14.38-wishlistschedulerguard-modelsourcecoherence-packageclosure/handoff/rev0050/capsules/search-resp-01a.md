# SEARCH-RESP-01A — direct user-search FileSearchResponse source binding

## Filing position

Bundle: `03-search-response-source-admission`. Production gate: rev0039. Rev0050 status: unchanged production-gated packet with claim-capsule QA.

## Minimum claim

For direct user searches, FileSearchResponse acceptance should require msg.username to be in the original requested user set for that token.

## Selected invariant / fix shape

For search.mode == user, admit only usernames in search.users.

## Evidence chain

rev0039 user-scope regression/source trace; rev0046 integrated stack gate.

Primary report:

```text
report_drafts/SEARCH-RESP-01A-PRODUCTION-READY-MAINTAINER-REPORT-REV0039.md
```

Regression artifact(s):

```text
maintainer_artifacts/search-resp-01/test_search_response_user_scope_fixed_regression.py
```

## Non-claims / filing guardrails

Not buddy/room policy, parser budget hardening, or all distributed-search behavior.

## Public-overlap boundary

Separate from broad distributed-search release-note wording.

## Source-refresh caveat

The capsule relies on archived rev0003 source-lane evidence and the rev0046 integrated selected-patch stack gate. Refresh against a newer upstream checkout before external action.
