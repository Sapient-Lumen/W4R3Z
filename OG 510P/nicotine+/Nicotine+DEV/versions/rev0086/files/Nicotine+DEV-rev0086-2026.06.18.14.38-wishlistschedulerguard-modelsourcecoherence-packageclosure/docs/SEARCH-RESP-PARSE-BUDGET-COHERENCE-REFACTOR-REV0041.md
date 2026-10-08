# SEARCH-RESP parser-budget coherence refactor — rev0041

## Refactor outcome

The search-response cluster now separates four concerns:

```text
SEARCH-RESP-01A / U-163A
  direct user-search response source binding — production-gated in rev0039

SEARCH-RESP-01B-BUDDY / U-163B
  buddy-search request-time source snapshot binding — production-gated in rev0040

SEARCH-RESP-PARSE-BUDGET-A / U-267A
  compressed FileSearchResponse pre-token username-prefix cap — production-gated in rev0041

SEARCH-RESP-PARSE-BUDGET-B
  accepted public/private result-list materialization limits — held

SEARCH-RESP-01C-ROOM
  room membership/freshness source model — held
```

## Guardrail

Do not merge parser-budget evidence into source-admission claims. The rev0041 prefix cap is a parser-local hardening point that runs before token lookup. The rev0039/rev0040 source-set guards are admission policies after a token maps to an outstanding search.

Do not merge accepted result-list materialization into the prefix cap. The prefix cap bounds how much compressed output is produced before the token is reached. Accepted result-list and private-list caps require separate policy and UI compatibility analysis.

Do not merge room membership into buddy source sets. Buddy search has a concrete local request-time snapshot; room search is server-mediated and needs freshness/membership modeling.

## Audit note

The requested refactor/audit pass also checked for misleading future-named room-source prototype files in the active tool lane. No rev0041 room-source patch is promoted; room-source work remains held until a dedicated compatibility packet is built.
