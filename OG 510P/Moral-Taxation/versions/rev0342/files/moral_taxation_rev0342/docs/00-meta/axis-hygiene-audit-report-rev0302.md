# Axis hygiene audit report — rev0302

Live route records: 155

The audit now fails release-process placeholders in live route axes and fails generic public-finance-core market/channel/burden sentinels.

| Blocked or cleaned signal | Before | After |
|---|---:|---:|
| new_calibration_file | 66 | 0 |
| unclassified_anti_pattern | 27 | 0 |
| not_remedy_specific | 41 | 0 |
| public_finance_not_market_specific | 42 | 0 |
| public_finance_not_channel_specific | 41 | 0 |
| public_finance_not_incidence_specific | 40 | 0 |

| Axis | Values / singletons before | Values / singletons after |
|---|---:|---:|
| base | 286 / 231 | 356 / 299 |
| proof_posture | 210 / 165 | 244 / 189 |
| anti_pattern | 297 / 255 | 310 / 228 |
| review_trigger | 254 / 206 | 270 / 206 |
| instrument | 323 / 270 | 344 / 266 |
| market_structure | 43 / 25 | 46 / 22 |
| delivery_channel | 49 / 35 | 50 / 28 |
| burden_mechanic | 58 / 35 | 58 / 26 |
| remedy_type | 68 / 34 | 69 / 30 |

Result: `new_calibration_file`, `unclassified_anti_pattern`, and `not_remedy_specific` are no longer valid live-axis shortcuts. Public-finance-core records must expose a concrete market structure, delivery channel, burden mechanic, and remedy classifier.

Note: after counts include executable case-contract required axes as well as live route-record axes, so this release is a hygiene refactor rather than a vocabulary-shrink release.
