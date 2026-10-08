# SEARCH-RESP-PARSE-BUDGET-B — current-web marker capsule rev0054

## Minimum claim

After token validation, FileSearchResponse parsing should bound accepted public/private result-list counts before materializing accepted result bodies.

## Current-web observation

The selected MAX_SEARCH_RESPONSE_RESULT_COUNT and accepted_result_count cap markers were not visible in current master or 3.3.x raw slskmessages.py views.

## Classification

selected marker set absent in current web snapshot

## Remaining gate

fresh checkout plus SEARCH-RESP-PARSE-BUDGET-B fixed-regression rerun still required before external filing

## Boundary

This capsule does not update the production report itself. It only adds a current-web marker classifier. A clean checkout and fixed-regression rerun are still required before filing.
