# Rematch worlds should store batch L2 compromise requests as two-integer summaries

If a bounded positive-service local weakening family will be resolved under the path-`L2` compromise rule, then the full preferred local-code multiset does not need to stay in memory or in the archive once its first moment has been recorded.

On the current source-rank path, the feasible squared-distance argmin set depends only on two integers:

- the number of preferred local codes; and
- the sum of their source ranks.

Those two integers determine the arithmetic mean rank, and the mean-projection law already shows that the feasible `L2` argmin set is exactly the nearest feasible integer rank or adjacent half-step tie pair after projecting that mean onto the feasible overlap interval.

Operational consequences for inheritors:

- when only `L2` witness choice matters, cache or persist `[preferred_count, preferred_rank_sum]` instead of the expanded preferred-code multiset;
- this compresses all audited width-`1..5` multisets from `26,333` distinct bundles down to just `245` statistic classes;
- the same summary is never larger than the expanded preferred-code list on the audited width-`1..5` catalog and is strictly smaller in all but seven singleton cases;
- infeasible families still fail with the same blocker certificate from the feasibility-intersection law;
- but this compression is **not** semantics-preserving for `L1`: bundles like `['S10','S10','E5','E5']` and `['S8','S8','S8','S8']` share the same two-integer `L2` summary `[4,12]` while inducing different `L1` argmin sets on the same feasible interval.
