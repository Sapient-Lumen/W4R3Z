# Axis hygiene audit report — rev0305

Live route records: 155

Rev0305 keeps the Rev0302/Rev0303 sentinel ban, the Rev0304 anti-pattern/review-trigger compression gate, and adds compression gates for the live `base`, `instrument`, and `proof_posture` axes.

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

| Route axis | Unique before | Unique after | Singletons before | Singletons after | Changed records |
|---|---:|---:|---:|---:|---:|
| `base` | 356 | 20 | 299 | 0 | 155 |
| `instrument` | 344 | 21 | 266 | 0 | 155 |
| `proof_posture` | 244 | 29 | 189 | 0 | 124 |
| `anti_pattern` | 151 | 151 | 124 | 124 | 0 |
| `review_trigger` | 117 | 117 | 93 | 93 | 0 |

Declared values after preserving case-contract vocabulary: `base` 104, `instrument` 37, `proof_posture` 80, `anti_pattern` 206, `review_trigger` 153.

Result: live route semantics now use controlled buckets for the highest-noise descriptive axes, while case contracts retain sharper scenario values for regression tests.
