# rev0089 refactor/audit note

Substantive refactor: `threat_response.annotate_threat_response_rows` now adds policy identity fields to newly generated annotated population rows through `population_replay_guard.annotate_policy_identity_rows`.

New code surface:

- `src/muc5/population_replay_guard.py`
- `scripts/run_rev0089_policy_replay_drift_guard.py`
- `tests/test_rev0089_policy_replay_guard.py`

The module reconstructs decks and replay specs from raw rows, hashes the current policy/runtime files, annotates future rows with runtime and pair digests, and performs fail-closed terminal/focus comparisons.

Audit result: the current code reproduces the sampled historical evidence exactly. The only detected issue is provenance thinness: inherited rows are name-only with respect to policy identity. That issue is now surfaced and bounded rather than silently ignored.
