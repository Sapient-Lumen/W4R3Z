# STRICT-BUNDLE filing-series refactor — rev0046

## Refactor result

rev0046 changes the handoff model from seven flat packets to four filing bundles.

| Filing bundle | Packets | Reason |
|---|---|---|
| Transfer-session identity | U-123 | Independent download-side active-owner collision invariant. |
| Peer primary election | PB-01 | Independent compatibility-sensitive peer connection election invariant. |
| FileSearchResponse source admission | SEARCH-RESP-01A, SEARCH-RESP-01B-BUDDY, SEARCH-RESP-01C-ROOM | These all touch `search.py` and stack through the rev0043 source-set patch. |
| FileSearchResponse parser budget | SEARCH-RESP-PARSE-BUDGET-A, SEARCH-RESP-PARSE-BUDGET-B | These both touch `slskmessages.py` and stack through the rev0042 parser-budget patch. |

## Important non-merge boundaries

Do not merge the parser-budget packets into the source-admission packets merely because all five involve `FileSearchResponse`. They protect different invariants:

```text
source-admission: should this response source be accepted for this token/mode?
parser budget: how much compressed or accepted result payload may be materialized?
```

Do not merge U-123 with release-note upload-spoofing language unless a future source trace proves the same download-side active-owner collision invariant. rev0046 still treats that overlap as broad adjacency, not a duplicate.

Do not merge PB-01 with general username-identity release-note language. PB-01 is about established primary connection replacement and secondary promotion.

## Practical filing order

```text
1. U-123
2. PB-01
3. SEARCH-RESP source-admission series
4. SEARCH-RESP parser-budget series
```

This order minimizes reviewer context switches and preserves the patch topology proven by the rev0046 integrated stack run.
