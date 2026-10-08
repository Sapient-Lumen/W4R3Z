# Session deep audit — rev0308

Focus: controller-AI memo compactness plus actor-profile trigger hygiene.

## What was risky

After rev0307, the archive had strong route-level accountability and compressed cube axes, but controller-AI route memos still duplicated long local failure and reopening taxonomies. More importantly, 51 actor-accountability profiles still carried `new_calibration_file` in `review_trigger`; that process label had been removed from live cube axes but not from the profile layer.

## What changed

Rev0308 converts controller-AI memo anti-pattern/change-trigger/accountability-map prose into compact capsules backed by cube axes and actor profiles. It also removes `new_calibration_file` from actor-accountability profile review triggers archive-wide by importing the corresponding route's audited cube `review_trigger` values.

## Audit/refactor performed

`tools/audit_prose_bloat.py` now has controller-AI family gates. `tools/audit_actor_accountability_profiles.py` now rejects profile-level `new_calibration_file` triggers.

## Remaining risk

The next bloat surfaces are family-specific option scans and default tables in tax-administration access and legal-enforcement memos. Those should be pruned by route semantics, preserving the actual contest/fallback/force distinctions rather than applying broad string replacement.
