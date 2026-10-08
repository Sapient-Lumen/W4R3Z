# Baseline-delta coherence refactor — rev0056

This refactor separates replay evidence that was easy to over-merge:

```text
current-behavior witness pass evidence
unpatched fixed-regression expected-failure evidence
patched selected-stack pass evidence
line-level source-anchor evidence
claim/field handoff capsules
fresh-current checkout filing proof
```

The important split is between archived-source replay and live-current filing readiness.

rev0056 therefore keeps the seven strict/front packets production-gated, but still not live-current filing-ready until a fresh checkout/tarball is obtained and rerun.

The search-response series also remains split. The older shared SEARCH-RESP current witness is useful baseline evidence, but it does not collapse the five production-gated search-response packets:

```text
SEARCH-RESP-01A: direct user-source binding
SEARCH-RESP-01B-BUDDY: buddy request-time source snapshot
SEARCH-RESP-01C-ROOM: room membership snapshot when available
SEARCH-RESP-PARSE-BUDGET-A: compressed username-prefix cap
SEARCH-RESP-PARSE-BUDGET-B: accepted result-list budget
```

No public path-watch row is promoted into the strict/front private packet set in this revision.
