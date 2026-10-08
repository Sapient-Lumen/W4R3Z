# SEARCH-RESP-PARSE-BUDGET-A — current-web marker capsule rev0054

## Minimum claim

The FileSearchResponse parser should reject overlong compressed username prefixes before inflating username_len + 4 bytes to reach the token.

## Current-web observation

The selected MAX_SEARCH_RESPONSE_USERNAME_LENGTH and username_len cap markers were not visible in current master or 3.3.x raw slskmessages.py views.

## Classification

selected marker set absent in current web snapshot

## Remaining gate

fresh checkout plus SEARCH-RESP-PARSE-BUDGET-A fixed-regression rerun still required before external filing

## Boundary

This capsule does not update the production report itself. It only adds a current-web marker classifier. A clean checkout and fixed-regression rerun are still required before filing.
