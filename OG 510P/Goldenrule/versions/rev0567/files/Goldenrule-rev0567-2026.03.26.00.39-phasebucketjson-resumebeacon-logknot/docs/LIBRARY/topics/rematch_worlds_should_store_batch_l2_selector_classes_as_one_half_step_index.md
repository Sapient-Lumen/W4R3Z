# Rematch worlds should store batch L2 selector classes as one half-step index

Once path-`L2` compromise requests have already been reduced to selector classes, the archive no longer needs two integers to represent them.

A selector singleton `[k, k]` and an adjacent tie selector `[k, k+1]` both sit on the same half-step lattice. The class can therefore be keyed by one integer

`half_step_selector_index = selector_lower_rank + selector_upper_rank`.

This makes the encoding bijective on the current `17`-state path:
- even indices `2k` decode to singleton selectors `[k, k]`;
- odd indices `2k+1` decode to adjacent tie selectors `[k, k+1]`;
- the full path therefore uses exactly the `33` integers `0..32`.

Practical consequence for inheritors:
- if only feasible `L2` witness choice matters, cache the selector class as one scalar `half_step_selector_index` instead of a two-integer selector interval;
- decode that scalar back to a selector interval only at witness-selection time, then project onto the feasible overlap interval as before;
- across the audited width-`1..5` catalog, the scalar code preserves all `24,633` validated reduced-mean selections and all direct rational `L2` argmins exactly;
- the `33` scalar classes remain behaviorally irreducible over the full realized interval catalog, so this re-encoding is compact but not lossy;
- the `16` adjacent feasible intervals `[0,1]` through `[15,16]` already form a complete separating regression basis for those `33` classes, and omitting any one of them merges at least one class pair;
- their fingerprints are monotone ternary words: singleton classes are `R^kL^(16-k)` and tie classes are `R^kBL^(15-k)`, where `R` picks the upper endpoint, `L` the lower endpoint, and `B` both endpoints.

Do **not** use the scalar index to recover exact mean magnitude, bundle width, or any non-`L2` downstream quantity.
