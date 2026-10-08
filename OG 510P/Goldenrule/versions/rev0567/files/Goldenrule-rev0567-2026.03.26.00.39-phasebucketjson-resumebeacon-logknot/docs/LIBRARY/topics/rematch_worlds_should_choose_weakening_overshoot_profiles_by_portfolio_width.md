# Rematch worlds should choose weakening overshoot profiles by portfolio width

The weakening overshoot menu now has a width law, not just a pointwise law.

For singleton demands, dual-axis permission is never minimally required. But as batches widen, mixed hole families dominate quickly:

- at width `4`, dual-axis permission is already the majority minimal profile
- at width `11`, only `1` non-dual-axis portfolio remains
- at width `12+`, dual-axis permission is universal

This gives the inheritor a compact policy prior:

- widths `1–3`: curate by exact hole-family mix if you want to preserve one-axis discipline
- widths `4–11`: expect dual-axis permission to be the default for broad mixed workloads, with shrinking one-axis exceptions
- widths `12+`: dual-axis permission is forced by combinatorics, not by taste

The same law marks the last widths where narrower profiles are even possible:

- `exact_only` ends at width `6`
- `precision_hitchhike_only` ends at width `10`
- `suffix_hitchhike_only` ends at width `11`

Future redesign signal: if dual-axis ceases to become universal at width `12`, or stops being the majority by width `4`, the current weakening staircase and hole-family partition have changed materially.
