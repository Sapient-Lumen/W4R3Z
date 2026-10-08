# rev0308 controller-AI memo and trigger hygiene refactor

Rev0308 addresses two coupled risks left after rev0307: controller-AI route memos still carried long local anti-pattern/change-trigger/accountability-map sections, and actor-accountability profiles still contained the process sentinel `new_calibration_file` in profile-level review triggers.

## Memo refactor

- Rewrote 19 controller-AI `Anti-patterns` sections into cube-axis-backed `Failure-mode capsule` sections.
- Rewrote 19 controller-AI `What would change the recommendation` sections into cube-axis-backed `Recalibration trigger capsule` sections.
- Replaced 6 legacy controller-AI `Accountability map` sections with compact `Accountability capsule` sections.
- Added compact accountability capsules to 15 additional controller-AI route memos so every controller-AI route now points to its actor-accountability profile.

## Trigger hygiene

- Profile-level `new_calibration_file` review triggers before: 51.
- Profile-level `new_calibration_file` review triggers after: 0.
- Profiles touched: 51.

The replacement rule is intentionally conservative: when a profile used the process sentinel, rev0308 removes it and imports the route's already-audited cube `review_trigger` axes while preserving any route-specific profile triggers already present.

## Metrics

| Metric | Value |
|---|---:|
| Controller-AI docs touched | 21 |
| Controller route-memo bytes before | 194818 |
| Controller route-memo bytes after | 187585 |
| Controller route-memo bytes saved | 7233 |
| Legacy controller anti-pattern sections remaining | 0 |
| Legacy controller change-trigger sections remaining | 0 |
| Legacy controller accountability-map sections remaining | 0 |
| Controller failure-mode capsules | 19 |
| Controller recalibration-trigger capsules | 19 |
| Controller accountability capsules | 21 |

## Rule going forward

Controller-AI route memos should keep substantive option scans, evidence ladders, and recommendations, but repeated failure modes, reopening conditions, and accountability handoffs should point to the cube axes and actor-accountability profiles. `new_calibration_file` is not a permissible actor-profile review trigger.
