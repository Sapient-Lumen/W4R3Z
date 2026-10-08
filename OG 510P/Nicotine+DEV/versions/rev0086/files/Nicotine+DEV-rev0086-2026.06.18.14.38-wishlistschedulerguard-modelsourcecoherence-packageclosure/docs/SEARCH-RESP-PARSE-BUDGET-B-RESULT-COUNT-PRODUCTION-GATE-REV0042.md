# SEARCH-RESP-PARSE-BUDGET-B — accepted result-list count production gate (rev0042)

## Promoted packet

`SEARCH-RESP-PARSE-BUDGET-B` is promoted as a production-gated maintainer packet. It covers accepted `FileSearchResponse` parser materialization after the response token has been accepted.

## Current behavior witness

The current parser first validates the token, then inflates the accepted response body and walks the public result list count. If private results are present, it then walks the private result list count as a separate list. The source has UI/display policy caps, but the parser materializes the accepted rows before those UI policies can limit display.

The rev0042 fixed-behavior regression captures three desired invariants:

1. an over-budget public result count is rejected before the full accepted result body is inflated;
2. an over-budget private result count is rejected without materializing the advertised private rows;
3. public and private lists share a single parser-row budget.

Small normal public/private responses continue to parse.

## Selected fix shape

The selected patch stacks on top of rev0041's username-prefix cap and adds:

```text
MAX_SEARCH_RESPONSE_RESULT_COUNT = 10000
```

The constant is intentionally conservative: it is above the default `max_displayed_results` setting of 2500 and above the default sent-search-result setting of 300 in the archived source. Maintainers can tune the constant, but the invariant is that the parser has an explicit accepted-row budget independent of UI display policy.

The patch then:

```text
- reads four decompressed bytes for the accepted public-list count after token validation;
- rejects counts above MAX_SEARCH_RESPONSE_RESULT_COUNT before inflating the rest of the accepted body;
- parses the public list with the same cap;
- parses the private list with the remaining shared budget;
- clears list/privatelist and marks token rejected when either list exceeds budget.
```

## Verification

```text
current source + rev0042 fixed regression: 3 failed / 1 passed on all three lanes
selected patch + rev0042 fixed regression: 4 passed on all three lanes
selected patch + rev0041 prefix regression: 4 passed on all three lanes
```

The old rev0013 current-behavior witness has one expected inverted assertion under the selected stacked patch: the invalid-token prefix-materialization assertion from rev0041.

## Production status

Production-gated maintainer packet: yes.
Production-ready report draft in cube: yes.
External filing status: not filed from this cube.
