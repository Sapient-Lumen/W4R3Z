# Next revision queue — rev0086

## Highest-value next problem

`WISHLIST-CAP-01`: decide what a scheduled subscription should do after its
visible result batch reaches capacity. The current scheduler can continue work
that the open page cannot display. Candidate policies—pause, batch rollover, or
bounded eviction—need explicit unread-result and persistence semantics.

## Open validation lanes

`SEARCH-AGAIN-EPOCH-01A` and its related manual-wishlist case still require
native GTK/notification validation. `WISHLIST-SCHED-01` is closed as research,
but the one-line guard should still receive maintainer-authored review if ever
implemented outside this cube.

## Cube work

Keep `data/current_source_contract.json`, `data/current_candidate_artifact_contract.json`,
`data/current_model_source_differential_contract.json`, and
`data/current_contract_coherence_contract.json` synchronized. Build only through
`tools/build_current_package.py`; never hand-author a release ZIP.
