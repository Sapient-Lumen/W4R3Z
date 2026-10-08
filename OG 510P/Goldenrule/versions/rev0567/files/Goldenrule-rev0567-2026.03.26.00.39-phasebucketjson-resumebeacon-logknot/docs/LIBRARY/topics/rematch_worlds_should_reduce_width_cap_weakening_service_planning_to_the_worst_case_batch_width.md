# Rematch worlds should reduce width-cap weakening service planning to the worst-case batch width

The recent weakening portfolio work already gave the inheritor a width-conditioned service frontier: if the batch width is exactly known, choose the weakest overshoot profile that clears the target admission rate at that width.

A natural remaining question was whether capped width uncertainty changes the problem. Suppose the inheritor only knows that the workload width is at most `W`, not that it is exactly `W`.

The new width-cap guarantee pass shows that, under the current weakening staircase, this adds no extra geometry.

For every efficient profile in the width-only service menu, guaranteed coverage is monotone nonincreasing in width. So the worst case inside the cap set `{1, ..., W}` is always the endpoint `W` itself.

That means robust capped-width planning is lossless:

- to guarantee service for any batch up to width `W`, evaluate the existing exact-width selector at width `W`
- there is no need to reason over the whole set of smaller widths separately
- the existing frontier already doubles as the robust guarantee frontier

The resulting operational rule is compact:

- `suffix_hitchhike_only` remains the only one-axis robust option worth considering
- it survives only through cap `5` for a `10%` guarantee, cap `3` for `25%`, and cap `2` for `50%`
- any target above `11/15 ≈ 0.733` forces dual-axis immediately, even when the cap is only `1`

So the inheritor can now treat width uncertainty in two modes:

- if exact width is known, use the width-conditioned service selector directly
- if only an upper bound is known, use the same selector at the upper bound

Future redesign signal: if any efficient profile’s guaranteed service ever stops decreasing monotonically with width cap, or if width-cap selection ever diverges from endpoint exact-width selection, the current batch-width geometry has changed materially.
