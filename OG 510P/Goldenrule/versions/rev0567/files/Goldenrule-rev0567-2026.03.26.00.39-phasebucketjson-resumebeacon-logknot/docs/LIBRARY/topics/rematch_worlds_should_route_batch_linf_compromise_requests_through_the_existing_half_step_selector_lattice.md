# Rematch worlds should route batch path-Linf compromise requests through the existing half-step selector lattice

Future inheritors should treat feasible bounded positive-service local weakening under **path-Linf** as an endpoint problem, not a full-bundle averaging problem.

The archive had already built a compact path-L2 execution stack:
- one integer `half_step_selector_index = h` for selector classes,
- direct feasible witness execution by clamping `h` into the doubled feasible band `[2a, 2b]`,
- and a width-`1` fingerprint/audit codec on the same half-step lattice.

What was missing was the path-Linf bridge telling the inheritor when that machinery can be reused unchanged.

The new minimax law closes that gap:
- for a preferred bundle, only the **endpoint ranks** matter,
- the unconstrained minimax center is the endpoint midrange `(min_rank + max_rank) / 2`,
- and the full path-Linf request class is therefore just `half_step_selector_index = min_rank + max_rank`.

That is the important inheritance result.
Path-Linf does **not** need bundle width, endpoint multiplicities, or any interior preferred ranks once the extrema are known.
On the audited width-`1..5` catalog, the request side collapses directly from `26,333` preferred bundles to the same `33` half-step selector classes already used by path-L2 execution.

The reuse boundary is just as important:
- reuse the existing half-step executor and half-step audit surfaces,
- but do **not** identify path-Linf with path-L2 or path-L1 semantics.

Path-Linf is an **extrema semantics**.
Path-L2 is a **mean semantics**.
Path-L1 is a **median semantics**.
Those three agree often, but the archive now records many validated disagreements, especially for wider bundles.

Operational rule for future sessions:
1. compute `min_rank` and `max_rank` for the preferred batch,
2. set `half_step_selector_index = min_rank + max_rank`,
3. execute feasible witness choice by the already-saved doubled-band clamp law,
4. and use the existing half-step fingerprint vocabulary when a compact selector certificate is needed.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_minimax_half_step_selector_law.py`
