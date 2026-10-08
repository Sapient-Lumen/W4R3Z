# Rematch worlds should choose overshoot-axis profiles for portfolios by hole-family mix

If exact-uncertainty weakening demands are chosen one at a time, no current request needs dual-axis overshoot permission. But portfolio governance is stricter than singleton governance: once a batch mixes at least one deep-suffix hole with at least one early/extra-precision hole, the weakest admissible profile becomes `any_single_axis_hitchhike`.

That means overshoot-axis permission should be chosen at the workload level by **hole-family mix**:

- exact staircase points only -> `exact_only`
- exact points plus deep-suffix holes -> `precision_hitchhike_only`
- exact points plus early/extra-precision holes -> `suffix_hitchhike_only`
- any batch containing both hole families -> `any_single_axis_hitchhike`

In the current `15`-point primitive box, the portfolio space is dominated by mixed families: among all `32767` non-empty portfolios, `29760` minimally require dual-axis permission, even though `0` singleton demands do. So dual-axis permission is not a single-request necessity, but it is the default minimal policy for broad mixed workloads.

Future redesign signal: if a singleton demand ever minimally requires `any_single_axis_hitchhike`, or if a mixed-family portfolio stops needing it, the scalar weakening geometry has changed in a substantive way.
