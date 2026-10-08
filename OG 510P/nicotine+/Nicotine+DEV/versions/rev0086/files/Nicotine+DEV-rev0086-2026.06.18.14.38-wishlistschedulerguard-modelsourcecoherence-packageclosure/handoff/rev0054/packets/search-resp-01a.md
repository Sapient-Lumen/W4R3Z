# SEARCH-RESP-01A — current-web marker capsule rev0054

## Minimum claim

For direct user searches, FileSearchResponse acceptance should require msg.username to be in the original requested user set for that token.

## Current-web observation

The current web view of _file_search_response performs token/search lookup and ignore checks, but the selected expected_users source-binding markers were not visible.

## Classification

selected marker set absent in current web snapshot

## Remaining gate

fresh checkout plus SEARCH-RESP-01A fixed-regression rerun still required before external filing

## Boundary

This capsule does not update the production report itself. It only adds a current-web marker classifier. A clean checkout and fixed-regression rerun are still required before filing.
