# Session deep audit — rev0297

## Priority chosen

The highest remaining measured accountability debt after rev0296 was `labor_care_benefits`: 11 beneficiary placeholders and 11 generic benefit-trace evidence bundles. The family also carried several generic cube axes that hid route differences between labor classification, education debt, care floors, child benefits, long-term care, platform benefits, assessment units, privacy/data minimization, pension pass-through, and worker/member-share repair.

## Main correction

Rev0297 specializes the entire family rather than sampling it. It turns worker, household, care, child, pension, platform, education, and data routes into responsibility maps that can answer who controlled the rule, record, benefit channel, bottleneck, or rent capture and who must repair the protected floor.

## Waste corrected

The most wasteful pattern was inherited axis scaffolding. A route like `data_minimization_credential_reuse_and_sensitive_attribute_firewall` should not look like `ordinary_labor` plus `credit`; it now exposes data access, privacy burden, credential reuse, sensitive attributes, digital/offline fallback, and data-minimization remedies. Similar corrections were made for care-load, pension pass-through, and worker-benefit/member-share routes.

## Regression guard

`tools/audit_actor_accountability_profiles.py` now makes labor/care placeholder regression fatal. The family cannot return to generic beneficiary placeholders, generic benefit-trace evidence, or public-channel-only bottlenecks without failing the release.
