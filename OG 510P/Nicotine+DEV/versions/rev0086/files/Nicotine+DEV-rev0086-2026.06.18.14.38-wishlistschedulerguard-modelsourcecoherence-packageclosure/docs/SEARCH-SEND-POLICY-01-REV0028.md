# SEARCH-SEND-POLICY-01 — rev0028

Canonical packet: **U-174 + U-247**.

Status: **verified audited backlog**, **not strict-promoted**.

## Finding summary

Inbound search requests arrive through the server/distributed search paths and can cause Nicotine+ to create and send `FileSearchResponse` objects. Across the archived source lanes, the response policy is evaluated with only the claimed requester username:

```python
permission_level, _reject_reason = core.shares.check_user_permission(username)
```

The handler then emits plugin notifications after `_process_search_request()` returns:

```python
self._process_search_request(msg.searchterm, msg.search_username, msg.token)
core.pluginhandler.search_request_notification(msg.searchterm, msg.search_username, msg.token)

self._process_search_request(msg.searchterm, msg.search_username, msg.token)
core.pluginhandler.distrib_search_notification(msg.searchterm, msg.search_username, msg.token)
```

That means two related behaviors are currently true:

1. Search-response permission/geoblock policy has no requester/source IP context at the point where `check_user_permission()` is called for search requests.
2. Plugin notifications still fire even when core search-response policy rejects the request because responses are disabled, the requester is banned, or the search term is below the configured minimum length.

## Proof status

Maintainer-style current-behavior test:

```text
maintainer_artifacts/search-send-policy-01/test_search_send_policy_reproducer.py
```

Run summary:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

The witness proves:

```text
Server search request:
  _process_search_request() calls check_user_permission(username) with ip_address omitted/None.
  A response can be sent in a witness policy that would reject the same requester if IP were bound.

Distributed search request:
  same username-only permission shape.

Core policy disabled:
  no FileSearchResponse is sent;
  search_request_notification still fires.

Core permission rejected:
  no FileSearchResponse is sent;
  search_request_notification still fires.

Core minimum-search-length rejected:
  no FileSearchResponse is sent;
  search_request_notification still fires.

Distributed policy disabled:
  no FileSearchResponse is sent;
  distrib_search_notification still fires.
```

## Impact framing

This is policy, provenance, and compatibility hardening. It is not code execution and not peer-only file disclosure.

Likely consequences:

- IP/geoblock policy is not applied to search responses unless a separate cached/resolved address policy is introduced.
- A local plugin can receive search request notifications even when the core client would not send a response under current policy.
- Search send policy is split: core and plugin surfaces do not share one decision object.

The most conservative description is:

```text
Search request policy decisions are not represented as a single authenticated/bound request context that both core response generation and plugin notifications consume.
```

## Why not strict-promoted

This packet is verified, but it does not outrank the current strict candidates:

- **U-123** has a clearer transfer-token/lifetime consequence.
- **PB-01** has a clearer connection identity/generation consequence.
- **SEARCH-RESP-01 / U-163** has a clearer accepted-response token/source/scope binding consequence.

SEARCH-SEND-POLICY-01 is lower because:

- normal server/distributed search protocol paths do not necessarily carry requester IP directly;
- a safe fix has to preserve search compatibility and avoid synchronous address-resolution fanout;
- plugin notifications are a local extension/API boundary and may need compatibility-preserving metadata rather than silent removal;
- public geoblock/search responder/plugin-notification material is adjacent.

## Fix-shape notes

Do **not** implement this as a naive synchronous IP lookup for every search request.

A coherent fix should consider:

```text
- Introduce an inbound SearchRequestContext with term, claimed username, token, origin type, source connection, cached/resolved address state, and core policy decision.
- Apply one policy decision before response generation and before plugin notification, or pass policy metadata to plugins explicitly.
- If geoblock/IP-ignore is enabled and requester IP is unknown, choose a conservative compatibility policy such as no private/trusted shares and optionally no response until a bounded async address lookup succeeds.
- Keep distributed-source IP separate from the claimed requester IP; a distributed parent is not necessarily the search requester.
- Add regression tests for responses-disabled, min-length rejection, banned requester, unknown IP with geoblock enabled, cached blocked IP, cached allowed IP, and plugin notification semantics.
```

## Evidence files

```text
evidence/rev0028-search-send-policy-pytest-run.txt
evidence/rev0028-search-send-policy-source-trace.md
evidence/rev0028-search-send-policy-source-trace.json
evidence/rev0028-web-public-overlap-search-send-policy.md
```
