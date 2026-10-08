# Actor-accountability audit report — rev0308

Result: pass.

Actor-accountability profiles: 155.

Rev0308 adds profile-level review-trigger hygiene: actor-accountability profiles may not use `new_calibration_file` as a review trigger. The pass removed 51 such trigger entries across 51 profiles and replaced them with route-specific or cube-backed triggers. Remaining profile-level `new_calibration_file` triggers: 0.
