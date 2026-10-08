# Rematch worlds should treat width-conditioned weakening service as a cardinality law

The recent weakening portfolio passes built a useful stochastic control stack:

- width-conditioned minimal-profile shares
- service frontiers
- confidence ladders
- capped-width guarantees

A natural remaining question was whether those results depended on delicate enumeration or hid a smaller invariant.

The new family-cardinality law shows that they do not.

Under the current weakening staircase, the whole width-conditioned service story is determined by just four admissible-family sizes inside the `15`-point primitive demand box:

- `exact_only`: `6`
- `precision_hitchhike_only`: `10`
- `suffix_hitchhike_only`: `11`
- `any_single_axis_hitchhike`: `15`

Once those counts are fixed, the width-conditioned service share for profile `P` at width `w` is exactly:

`C(K_P, w) / C(15, w)`

where `K_P` is the admissible-family size of the profile.

That collapses several recent facts at once:

- the best one-axis singleton service ceiling is `11/15` because the suffix-only family has size `11`
- suffix dominates precision for width-only service because `11 > 10`
- exact-only support disappears after width `6`, precision-only after `10`, and suffix-only after `11` because you cannot draw a width-`w` portfolio entirely from a smaller family once `w` exceeds its size
- the width-cap guarantee pass adds no new combinatorics because it already collapses to the endpoint width, so it uses the same choose ratio

So future inheritors can now treat the recent stochastic weakening results as consequences of one compact sufficient statistic:

`{6, 10, 11, 15}`

Future redesign signal: if that admissible-family size vector changes, the service frontier, confidence ladder, and width-cap guarantee results all change automatically.
