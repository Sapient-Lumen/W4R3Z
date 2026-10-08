# Maintainer report draft — FileSearchResponse accepted result-list count budget

## Summary

Accepted `FileSearchResponse` messages can currently force the parser to materialize public and private result rows according to peer-advertised counts. UI/search display limits are enforced later, after the parser has already constructed the lists. A local parser budget should bound accepted public+private result row materialization.

## Affected parser

`pynicotine/slskmessages.py::FileSearchResponse`

Verified on archived lanes:

```text
github-tag-3.3.10
github-branch-3.3.x
github-branch-master
```

## Reproducer

`maintainer_artifacts/search-resp-01/test_search_response_result_budget_fixed_regression.py`

Current behavior:

```text
3 failed / 1 passed on all three archived lanes
```

Selected patch behavior:

```text
4 passed on all three archived lanes
```

## Suggested invariant

After a response token is accepted, the parser should apply an explicit maximum accepted result-row count before allocating public/private result-row objects. Public and private lists should share that budget.

## Suggested fix shape

- Add a parser-side constant such as `MAX_SEARCH_RESPONSE_RESULT_COUNT`.
- After token validation, read only the four-byte public result count from the compressed stream.
- Reject counts above the cap before inflating the accepted body.
- Parse the public list with the cap and the private list with the remaining cap.
- Treat over-budget accepted bodies as rejected/empty responses.

## Compatibility note

The selected constant is deliberately above the default UI display limit. The exact value is maintainer-tunable; the important part is the parser-boundary invariant.
