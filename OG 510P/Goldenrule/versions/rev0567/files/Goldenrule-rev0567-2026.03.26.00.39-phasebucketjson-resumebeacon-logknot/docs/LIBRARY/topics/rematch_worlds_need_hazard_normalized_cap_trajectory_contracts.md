# Rematch Worlds Need Hazard-Normalized Cap-Trajectory Contracts

What changed:
- Once the certified family `10/20/50/100` policy box leaves only `TTTMMMMMU` and `TTTMMMMUU`, the remaining cap-sensitive choice can be reduced to one scalar
  `rho = baseline_nonhazard_surplus / w_hazard` when `w_hazard > 0`.
- The exact cap rule is then simple: choose `TTTMMMMUU` at cap `c` iff `rho > tau(c)`, where `tau(c)` is the hazard-derived normalized threshold.

Why this matters:
- This is tighter than carrying several separate weight statements through the archive.
- It also exposes a failure mode the earlier passes did not yet state explicitly: as cap rises, some declared preferences do **not** switch winner only once.
- In the current proxy, the exact threshold curve is unimodal on checked caps `10..10000`, so there are only four structural path types:
  - always material,
  - low-cap stability then material,
  - stability then mid-cap material then tail stability,
  - always stability.

Planning consequence:
- Future inheritors should classify the declared preference by its normalized margin before narrating “what more budget does.”
- In particular, checking only one low cap and one high cap can miss a real middle-cap reversal band.
- For code paths, use exact internal threshold comparisons; rounded human-facing coefficients are good for prose but too coarse for exact transition-cap recovery.

Where to look:
- report: `artifacts/reports/rematch_proxy_delta_normalized_cap_trajectory_snapshot_20260306.md`
- builder: `scripts/report/build_rematch_proxy_delta_normalized_cap_trajectory_snapshot.py`
- validator: `scripts/test/check_rematch_delta_normalized_cap_trajectories.py`
