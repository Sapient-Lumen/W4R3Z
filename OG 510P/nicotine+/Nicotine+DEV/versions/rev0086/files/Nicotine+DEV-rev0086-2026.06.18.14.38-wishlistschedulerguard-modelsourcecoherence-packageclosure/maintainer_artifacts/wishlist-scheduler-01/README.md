# WISHLIST-SCHED-01 research packet

This packet isolates collection rotation and eligibility in
`Search._do_next_wishlist_search()` from the downstream persistent-inbox model.

- `wishlist_scheduler_model.py` contains separate current and candidate
  policies over the same bounded rotation.
- `source_witness.py` executes the same scenario matrix against a supplied
  Nicotine+ source tree.
- `test_wishlist_scheduler_model.py` checks the behavioral delta and unchanged
  enabled-item round robin.
- `test_wishlist_scheduler_source_semantics.py` binds the one-line candidate to
  the exact source method.
- `wishlist_scheduler_enabled_only_rev0086.patch` is a research-only correction.

The packet is governed by
`data/current_model_source_differential_contract.json`; model-only success is
not accepted as evidence of current product behavior.
