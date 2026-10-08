# Rematch worlds should choose width-only weakening profiles by service frontier, not the full profile menu

When the inheritor knows only batch width and wants a probabilistic admission policy, the four-profile weakening guardrail menu is larger than it needs to be.

The new service-frontier pass shows that `precision_hitchhike_only` is width-conditionally dominated by `suffix_hitchhike_only` at every width. It never covers more random portfolios of a given width, and while one-axis coverage still exists it always covers strictly less.

So the practical width-only menu collapses to three efficient choices:

- `exact_only`
- `suffix_hitchhike_only`
- `any_single_axis_hitchhike`

That collapse has a sharp policy consequence.

The best one-axis profile reaches only `11/15 ≈ 0.733` service, attained at width `1`. So any width-only service target above roughly `73%` forces dual-axis permission immediately, even for singleton workloads.

The remaining one-axis frontier is only useful for low or moderate service on tiny batches:

- `suffix_hitchhike_only` can hit `50%` service only through width `2`
- it can hit `25%` service only through width `3`
- it can hit `10%` service only through width `5`
- `exact_only` is even narrower, surviving only for very low service targets on widths `1–2`

This gives the inheritor a compact operational rule:

- if the service target is high, skip straight to dual-axis
- if the batch is tiny and the tolerated admission miss rate is large, the suffix-only profile is the only one-axis probabilistic option worth considering
- do not treat `precision_hitchhike_only` as part of the efficient width-only policy frontier unless the workload is known to be family-biased rather than width-only random

Future redesign signal: if `precision_hitchhike_only` ever becomes frontier-efficient under width-only uncertainty, or if a one-axis profile ever exceeds the current `11/15` service ceiling, the present hole-family asymmetry has changed materially.
