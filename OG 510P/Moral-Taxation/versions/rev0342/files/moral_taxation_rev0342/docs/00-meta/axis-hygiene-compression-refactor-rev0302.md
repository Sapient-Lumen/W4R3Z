# Axis hygiene and public-finance cube compression — rev0302

Rev0302 is a substance-preserving compression pass. Rev0301 solved the actor-accountability placeholder problem, but the cube still had release-process scaffolding embedded as live semantics: 66 records used `new_calibration_file` as their review trigger, 27 public-finance-core records still used `unclassified_anti_pattern`, and all 41 public-finance-core records with a remedy axis still used `not_remedy_specific`.

## What changed

- Replaced all `review_trigger=new_calibration_file` entries with reusable substantive triggers such as channel/delivery failure, claim-split drift, controller/accountability drift, record staleness, remedy/contest failure, and threshold/sunset review.
- Cleared every public-finance-core `unclassified_anti_pattern` entry and replaced it with route-specific failure modes such as base overlap, beneficiary invisibility, channel fallback erasure, retained surplus, fiscal illusion, proxy blindness, cliff traps, and promoter opacity.
- Cleared every `remedy_type=not_remedy_specific` entry; public-finance-core routes now name concrete remedy classifiers such as claim-split correction, record correction, data minimization, capacity support, hardship relief, no-go rule, route retirement, or action reclassification.
- Removed generic public-finance-core `not_market_specific`, `not_channel_specific`, and `not_incidence_specific` sentinels. The records now expose fiscal-reporting portals, registries, public channels, private rails, bill lines, certification gates, claim-split rails, benefit accounts, burden mechanics, and remedy channels.
- Added `tools/audit_axis_hygiene.py` and wired it into `make audit` and `tools/check_archive.py`.

## Before/after signals

| Signal | Before | After |
|---|---:|---:|
| new_calibration_file | 66 | 0 |
| unclassified_anti_pattern | 27 | 0 |
| not_remedy_specific | 41 | 0 |
| public_finance_not_market_specific | 42 | 0 |
| public_finance_not_channel_specific | 41 | 0 |
| public_finance_not_incidence_specific | 40 | 0 |

## Why this matters

The high-risk failure after placeholder extinction was not another missing doctrine. It was that a route could look machine-complete while still telling the operator only that the file was new, the anti-pattern was unclassified, or the remedy was unspecified. That is dangerous because the cube becomes a filing cabinet rather than a routing engine. Rev0302 makes the public-finance waist more executable: a user can now see whether the issue is a delivery rail, claim split, netting rule, fiscal disclosure channel, registry, data wall, threshold, benefit account, or representation/remedy failure.

## Remaining risk

Axis vocabulary is still large, and singleton values remain common. This pass intentionally blocks the most misleading release-process placeholders first. The next compression pass should collapse near-duplicate singleton values where the detail is better stored in profiles or prose than as a formal axis value.

Note: after counts include executable case-contract required axes as well as live route-record axes, so this release is a hygiene refactor rather than a vocabulary-shrink release.
