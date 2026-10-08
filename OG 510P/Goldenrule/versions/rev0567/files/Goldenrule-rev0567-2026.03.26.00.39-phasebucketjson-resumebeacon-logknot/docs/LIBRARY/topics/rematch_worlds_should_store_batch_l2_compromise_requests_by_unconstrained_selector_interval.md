# Rematch worlds should store batch L2 compromise requests by unconstrained selector interval

If a bounded positive-service local weakening family will be resolved under the path-`L2` compromise rule, then even the canonical reduced mean still keeps more information than witness selection needs.

The only remaining quantity that matters is the unconstrained nearest-integer argmin interval on the full source-rank path. That selector interval is always either a singleton rank `[k, k]` or one adjacent tie pair `[k, k+1]`. Once it is known, every feasible family is resolved by projecting that selector interval onto the feasible overlap interval.

Practical consequence for inheritors:
- when only `L2` witness choice matters, cache or persist the selector interval `[selector_lower_rank, selector_upper_rank]` instead of the exact reduced mean;
- on the audited width-`1..5` catalog, this collapses `161` canonical reduced-mean classes to just `33` selector classes, for an additional `4.878788x` cache reduction;
- the `33` classes are exactly `17` singleton selectors and `16` adjacent tie selectors along the `17`-state path;
- every singleton selector is shared by widths `1..5`, every tie selector is shared by widths `2` and `4`, and all selector classes are therefore cross-width reusable on the audited catalog;
- boundary singleton selectors aggregate `5` reduced-mean classes, interior singleton selectors aggregate `9`, and each tie selector aggregates exactly one reduced mean (the corresponding half-integer);
- do **not** reuse this summary for reconstructing exact mean magnitude, bundle width, or any non-`L2` downstream quantity.
