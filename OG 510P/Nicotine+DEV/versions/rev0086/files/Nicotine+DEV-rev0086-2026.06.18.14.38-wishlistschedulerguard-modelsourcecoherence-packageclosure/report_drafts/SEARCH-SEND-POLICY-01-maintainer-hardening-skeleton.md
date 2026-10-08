# SEARCH-SEND-POLICY-01 maintainer hardening skeleton

## Summary

Inbound server/distributed search request handling currently has two related policy-shape behaviors:

1. Response permission checking calls `check_user_permission(username)` without requester/source IP context.
2. Plugin notifications are emitted after the core path returns even when the core path rejects the request under local response policy.

## Current-behavior witness

```bash
PYTHONPATH=/path/to/source-tree pytest -q \
  maintainer_artifacts/search-send-policy-01/test_search_send_policy_reproducer.py
```

Expected current behavior in archived lanes:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

## Suggested fixed-behavior goals

```text
- Represent inbound search request handling as a SearchRequestContext.
- Include term, claimed username, token, origin type, source connection, cached/resolved address state, and core policy decision.
- Do not treat distributed parent socket IP as the actual requester IP.
- Do not do unbounded synchronous GetPeerAddress fanout in the search hot path.
- Either gate plugin notifications on the same core policy decision, or pass policy metadata so plugins can decide intentionally.
- Add tests for disabled responses, banned requester, short term, geoblock with unknown IP, geoblock with cached blocked IP, geoblock with cached allowed IP, and plugin notification compatibility.
```

## Non-goals

```text
- No claim of code execution.
- No claim that all search requests can carry a trustworthy IP address.
- No PR patch included.
- No recommendation to break existing plugins silently.
```
