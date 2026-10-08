# Rematch worlds need budget-family delta cores, not one-cap anchors

The new derived report in `artifacts/reports/rematch_proxy_delta_persistence_snapshot_20260306.{md,json}` asks a narrower implementor question than the earlier admissibility and topology passes: **does a published delta anchor survive if the benchmark owner modestly relaxes or tightens the extra-budget cap?**

A single cap-specific admissible band is not enough. Even a topology-stable interior anchor can still be too local if the benchmark’s effective budget family is really “something like cap 10 through cap 100” rather than exactly one operational line in the sand.

In the current leave/rematch proxy, two low-delta cap-10 cores survive unchanged through caps `10, 20, 50, 100`:

- a **material-core** region (`TTTMMMMMU`) on `0.00538..0.00666`, and
- a **practical-tie** region (`TTTMMMMUU`) on `0.00667..0.00822`.

Those are much better public-anchor candidates than a cap-local boundary point because they remain scientifically consistent across a realistic budget family.

But persistence alone is still not enough. One topology (`TTTMMUMUU`) also persists from cap `10` upward, yet only at the single grid point `0.00823`. So the archive now has a sharper rule:

1. choose anchors from a **declared family of budget caps**,
2. require a **non-trivial shared-core width** across that family,
3. and publish an **exact discrete-center anchor contract** instead of a rounded arithmetic midpoint when the shared core has an even number of grid points.

That last clause matters because midpoint rounding can manufacture fake half-step anchors or make a one-point survivor look broader than it really is. Future rematch benchmarks should therefore publish both the cap family and the resulting shared-core interval whenever they elevate one delta into a named benchmark constant.
