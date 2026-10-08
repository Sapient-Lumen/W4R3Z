# Rematch worlds need declared anchor priorities, not hidden tie-breaks

The new publishability shortlist solved one important problem: it reduced the universe of persistent rematch delta cores to a small set of benchmark-worthy candidates. But that still does **not** guarantee a unique public anchor.

In the current leave/rematch proxy, the strict sub-`0.01` shortlist contains exactly two candidates:

- `TTTMMMMMU` on `0.00538..0.00666`, anchor `0.00602`
- `TTTMMMMUU` on `0.00667..0.00822`, anchor `0.00744`

Those two anchors encode a real scientific tradeoff.

The lower anchor (`0.00602`) is better if the archive prioritizes:

- the smallest declared practical margin,
- more panels staying in `material_leader`, and
- fewer panels remaining `undecided`.

The higher anchor (`0.00744`) is better if the archive prioritizes:

- wider cross-cap shared-core support,
- larger interior buffer to topology boundaries, and
- slightly more distance from knife-edge leader-gap deltas.

Neither candidate strictly dominates the other. So a future implementor should **not** pretend the shortlist already contains one objectively best scalar constant. The final choice is only reproducible once the archive declares its priority profile.

That is what the derived report in `artifacts/reports/rematch_proxy_delta_preference_snapshot_20260306.{md,json}` now makes explicit. It reports both Pareto nondominance and the winner under several named lexicographic priority profiles.

The implementor consequence is simple:

1. publish the strict shortlist,
2. publish the priority profile used to break ties inside that shortlist, and
3. treat any unprofiled scalar anchor as still under-specified.

This is a healthier contract than hiding the judgment step. A benchmark constant can still be singular, but only after the archive says which virtue it is optimizing for.
