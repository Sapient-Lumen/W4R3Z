# Strict/front report sequencing — rev0035

## Current queue

1. **U-123** — duplicate transfer-token stale-timeout F-session orphan.
2. **PB-01** — peer primary-election/generation binding across direct PeerInit, PierceFireWall, and secondary post-init promotion.
3. **SEARCH-RESP-01** — search response token/source/scope acceptance and parser materialization order.

## Next production-draft packet: U-123

Draft title:

```text
Duplicate peer-supplied download transfer tokens can orphan an active F-connection transfer session
```

Required fixed-behavior regression:

```text
Given two same-user/same-token transfer activations where the second reaches F-connection state,
when the first transfer's stale request timer fires,
then the active map for the second transfer/session remains intact,
and later progress/close callbacks for the second socket/file session are still routed.
```

Required fix constraints:

```text
- Do not key destructive deactivation only by username+token.
- Either reject duplicate same-user/same-token activation while active, or allocate a local generation/session identity.
- Bind timeout/deactivation and F-connection callbacks to the expected transfer object/session.
- Preserve legitimate queued/retry/re-request behavior.
```

## PB-01 hold condition

PB-01 should not become production text until the report has a compatibility section covering:

```text
- first direct PeerInit acceptance;
- valid indirect PierceFireWall with no direct primary;
- valid indirect replacement of an unestablished direct attempt;
- rejection or demotion of later direct replacement and secondary post-init promotion without breaking fallback.
```

## SEARCH-RESP-01 hold condition

SEARCH-RESP-01 should not become production text until the report separates:

```text
- user/room/buddy source-scope binding expectations;
- global/wishlist broad-source compatibility;
- pre-materialization budget/private-result parse-order hardening.
```
