# Axis hygiene audit report — rev0303

Live route records: 155

Rev0303 extends the Rev0302 hygiene gate from release-process placeholders to all remaining mature not-specific live-axis sentinels.

| Blocked or cleaned signal | Before | After |
|---|---:|---:|
| `new_calibration_file` | 0 | 0 |
| `unclassified_anti_pattern` | 0 | 0 |
| `not_remedy_specific` | 0 | 0 |
| `no_specific_floor_risk` | 31 | 0 |
| `not_market_specific` | 2 | 0 |
| `not_channel_specific` | 22 | 0 |
| `not_incidence_specific` | 33 | 0 |
| `not_rights_specific` | 18 | 0 |

| Axis | Values / singletons after |
|---|---:|
| base | 356 / 299 |
| proof_posture | 244 / 189 |
| anti_pattern | 310 / 228 |
| review_trigger | 270 / 206 |
| instrument | 344 / 266 |
| floor_risk | 132 / 74 |
| market_structure | 46 / 22 |
| delivery_channel | 67 / 42 |
| burden_mechanic | 82 / 47 |
| rights_affected | 29 / 9 |

Result: live route axes can no longer complete a record by saying the floor, market, channel, burden, right, remedy, anti-pattern, or review trigger is unspecified.
