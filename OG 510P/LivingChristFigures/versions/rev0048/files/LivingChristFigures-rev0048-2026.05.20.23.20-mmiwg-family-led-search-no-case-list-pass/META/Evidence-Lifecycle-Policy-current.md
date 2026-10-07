# Evidence Lifecycle Policy — current

Added in rev0032.

This cube now distinguishes evidence lifecycle from evidence existence. A claim can be supported enough to remain in the working cube while still being unsafe for public wording, overdue before use, or volatile enough to require a near-term refresh.

## Rule of use

Do not let a current-capacity claim ride on the same refresh cadence as a historical or interpretive claim.

## Derived labels

`META/Claim-Evidence-Strength-current.*` assigns non-final routing labels:

- `multi_source_supported_shape`
- `single_primary_or_institutional_shape`
- `single_source_supported_shape`
- `critical_counterevidence_present`
- `boundary_or_counterclaim`
- `interpretive_not_fact_claim`
- `unsupported_or_missing_source_link`

These labels are not sainthood scores, truth verdicts, or public endorsements. They are routing instructions for caution, refresh, and public wording.

## Refresh priority labels

- `now_or_before_any_public_claim` — do not use publicly without rechecking or rewriting.
- `soon_keep_near_claim` — keep the caution or counterevidence adjacent to the positive claim.
- `not_freshness_driven_but_keep_evidence_adjacent` — interpretive claim; freshness is not the main risk, evidence/proportionality is.
- `standard_refresh_cycle` — ordinary supported-shape maintenance.

## Cadence labels

- `30_days_or_before_use`
- `90_days_or_before_use`
- `180_days_or_before_use`
- `365_days_or_before_major_revision`

The cadence is deliberately conservative when the claim contains current-capacity, shelter, helpline, referral, visitation, outreach, or live-service language.

## Boundary sentence

Evidence has a lifecycle; mercy-work does not become timeless because it once appeared in a source.
