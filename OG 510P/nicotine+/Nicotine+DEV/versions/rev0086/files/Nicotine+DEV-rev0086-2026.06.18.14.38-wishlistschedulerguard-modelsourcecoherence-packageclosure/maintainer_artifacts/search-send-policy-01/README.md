# SEARCH-SEND-POLICY-01 maintainer witness

Current-behavior pytest witness for rev0028.

The test documents current behavior across the archived source lanes:

- inbound server search request handling calls the core search-response path and then emits `search_request_notification`;
- inbound distributed search request handling calls the core search-response path and then emits `distrib_search_notification`;
- the core response path calls `check_user_permission(username)` without passing a requester/source IP address;
- plugin notifications still fire when core policy rejects the request because responses are disabled, requester permission is banned, or the term is too short.

Run against one lane:

```bash
PYTHONPATH=/path/to/source-tree pytest -q test_search_send_policy_reproducer.py
```

This is not a proposed fixed-behavior test. It is a reproducible witness to guide a compatibility-preserving fix.
