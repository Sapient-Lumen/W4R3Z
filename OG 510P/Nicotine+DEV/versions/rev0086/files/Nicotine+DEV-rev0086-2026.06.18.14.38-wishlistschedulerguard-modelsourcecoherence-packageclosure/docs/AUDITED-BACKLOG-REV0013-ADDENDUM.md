# Audited backlog addendum — rev0013

## Strict promotion

- SEARCH-RESP-01 / U-163 promoted as the third strict report-candidate.

## Proved but not separately promoted

- U-262: private result rows are parser-materialized before private-result display policy.
- U-267: invalid-token rejection decompresses a peer-controlled username prefix far enough to read the token.
- U-266: accepted responses can materialize full public result lists before visible-result caps.

## Public-overlap caution

Search-result performance, max-result-limit, and private-result visibility have public overlap. The new strict wording must therefore stay narrow: user/room search-response source/scope binding, not generic search-result performance.

## Next target

Move to **FOLDER-RESP-01**, led by U-167 if source tracing confirms the request-token mismatch; use U-255/U-260/U-268 only as parser-ordering/support checks unless one becomes a separate coherent root.
