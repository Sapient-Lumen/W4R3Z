# Rev0288 remedy-profile audit report

## Remedy families

- `channel_access_and_cure` — 57
- `classification_correction` — 24
- `floor_repair_and_no_rent_relief` — 3
- `general_design_review` — 39
- `harm_repair_or_no_go` — 9
- `record_correction_and_accountable_review` — 3
- `rent_capture_with_pass_through_control` — 8
- `risk_prefunding_and_clawback` — 6
- `source_release_integrity` — 3

## Proceeds-integrity posture

- `axis_only` — 123
- `explicit_claims` — 9
- `not_applicable` — 20

## Enforcement

`tools/audit_remedy_profiles.py` now fails the release if any route lacks a profile, if explicit proceeds claims are not exposed through the profile, if source-currentness refs are not mirrored into remedy review linkage, or if a specific remedy type falls back to a generic design-review profile.
