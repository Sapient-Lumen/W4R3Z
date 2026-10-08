# SEARCH-RESP result-budget coherence refactor — rev0042

Rev0042 separates the accepted result-list parser budget from adjacent search-response rows.

| Row | Status after rev0042 | Boundary |
| --- | --- | --- |
| SEARCH-RESP-01A / U-163A | production-gated rev0039 | direct user-search response source binding |
| SEARCH-RESP-01B-BUDDY / U-163B | production-gated rev0040 | buddy-search request-time source snapshot |
| SEARCH-RESP-PARSE-BUDGET-A | production-gated rev0041 | compressed username-prefix cap before token validation |
| SEARCH-RESP-PARSE-BUDGET-B | production-gated rev0042 | accepted public/private result-row materialization budget after token validation |
| SEARCH-RESP-01C-ROOM | held | room membership/freshness compatibility model |
| U-138 | deferred | general ID3v2 advertised-frame materialization |

The result-list packet is intentionally not framed as a source-admission bug. It assumes an accepted token and handles how many rows the accepted response can force into parser-owned Python objects.

The packet is also separate from UI display limits. UI limits are useful user-interface policy, but they run after the network parser has already allocated and sorted result rows. The rev0042 invariant belongs at the parser boundary.
