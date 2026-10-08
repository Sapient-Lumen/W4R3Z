# Audited backlog addendum — rev0028

## SEARCH-SEND-POLICY-01 / U-174 + U-247

Decision: **verified audited backlog; not strict-promoted**.

Run summary:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

What was verified:

```text
U-174:
  server and distributed search request response policy calls check_user_permission(username)
  without requester/source IP context.

U-247:
  search_request_notification/distrib_search_notification are emitted after the core path returns,
  even when the core path rejects due disabled search responses, banned requester, or min-search-length policy.
```

Why backlog rather than strict:

```text
- policy/API behavior, not code execution;
- server/distributed request boundary with compatibility constraints;
- plugin notifications are local extension surfaces;
- public geoblock/search responder/plugin-notification context exists;
- lower value than U-123, PB-01, and SEARCH-RESP-01.
```

Next target: **FILE-ATTRIBUTE-BUDGET-01 / U-199**, unless a later re-score indicates a higher-risk untouched row.
