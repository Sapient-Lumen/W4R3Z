# Rematch worlds should store batch L2 compromise requests by canonical reduced mean

If a bounded positive-service local weakening family will be resolved under the path-`L2` compromise rule, then even the two-integer summary `[preferred_count, preferred_rank_sum]` still carries one redundant degree of freedom.

The only quantity that controls feasible squared-distance witness choice is the arithmetic mean rank itself. Once that mean is reduced to coprime integers `[reduced_mean_numerator, reduced_mean_denominator]`, the same mean-projection law applies without needing bundle width or unreduced rank sum.

Practical consequence for inheritors:
- when only `L2` witness choice matters, canonicalize `[preferred_count, preferred_rank_sum]` to the reduced mean fraction and cache by that canonical key;
- on the audited width-`1..5` catalog, this collapses `245` width-dependent two-integer classes to `161` canonical reduced-mean classes;
- all `84` removed duplicates come from cross-width reuse of the same integer means (`17` of them, shared by widths `1..5`) and the same half-integer means (`16` of them, shared by widths `2` and `4`);
- reduced denominators `3`, `4`, and `5` are width-unique on the current audit, so only integers and half-integers create cross-width cache collisions;
- do **not** reuse this summary for `L1` semantics or for any downstream step that must recover original bundle cardinality.
