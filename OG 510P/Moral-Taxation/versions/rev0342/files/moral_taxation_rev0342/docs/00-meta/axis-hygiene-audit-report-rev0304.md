# Axis hygiene audit report — rev0304

Live route records: 155

Rev0304 keeps the Rev0302/Rev0303 sentinel ban and adds a compression gate for the two noisiest live operational axes.

| Blocked signal | Count after |
|---|---:|
| `new_calibration_file` | 0 |
| `unclassified_anti_pattern` | 0 |
| `not_remedy_specific` | 0 |
| `no_specific_floor_risk` | 0 |
| `not_market_specific` | 0 |
| `not_channel_specific` | 0 |
| `not_incidence_specific` | 0 |
| `not_rights_specific` | 0 |

| Compression metric | Before | After |
|---|---:|---:|
| route `anti_pattern` unique values | 310 | 151 |
| route `anti_pattern` singleton values | 228 | 124 |
| declared `anti_pattern` values, including case contracts | 312 | 206 |
| route `review_trigger` unique values | 270 | 117 |
| route `review_trigger` singleton values | 206 | 93 |
| declared `review_trigger` values, including case contracts | 270 | 153 |

Result: route records keep concrete failure semantics, but repeated phrases now converge into queryable buckets rather than route-local one-offs.
