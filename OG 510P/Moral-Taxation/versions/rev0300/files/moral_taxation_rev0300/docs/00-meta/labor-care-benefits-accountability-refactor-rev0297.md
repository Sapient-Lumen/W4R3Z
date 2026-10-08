# Labor/care/benefits accountability refactor — rev0297

Rev0297 clears the `labor_care_benefits` accountability debt. Before this pass, all 11 profiles in the family still used `beneficiary_or_rent_recipient_to_trace` and the generic `benefit_or_rent_trace` evidence bundle. Several route records also inherited generic cube defaults such as `new_calibration_file`, `ordinary_labor`, `credit`, `public_channel`, and `classification_safe_harbor`, which made care-load, data-minimization, pension-pass-through, and worker-benefit routes look interchangeable.

## What changed

- All 11 labor/care profiles now identify concrete accountable actors, beneficiaries, burden bearers, bottlenecks, non-responsible actors, default moves, fallback duties, evidence packets, and review triggers.
- The audit now rejects labor/care profiles that keep generic beneficiary placeholders, generic `benefit_or_rent_trace`, public-channel-only bottlenecks, or too-thin responsibility bases.
- Four inherited-template cube records were refactored deeply: `assessment_unit_and_care_load`, `data_minimization_credential_reuse_and_sensitive_attribute_firewall`, `pension_pass_through_incidence_and_proceeds`, and `worker_benefit_pay_hours_member_share_and_local_repair`.
- Six additional labor/care records received targeted axis correction so education finance, retirement, child/family benefits, long-term care, labor-tax wedge, and platform-worker routes no longer all report the same market/channel/burden/remedy shape.

## Accountability clusters

### Work classification and portable benefits

Responsibility follows the actor with practical control over price, dispatch, deactivation, hours, wage records, payroll/social-insurance contributions, contribution bases, and benefit ledgers. Contract label, customer proximity, payment-interface status, or benefit-account branding is not enough.

### Care, household, child, and long-term-care floors

Responsibility follows the actor that controls assessment units, dependency records, care-hour recognition, tapers, recertification, provider capacity, asset tests, estate recovery, and home/community-care access. The caregiver, child, disabled person, older person, or second earner is not the accountable actor merely because they are visible in the household file.

### Education, retirement, and pension pass-through

Responsibility follows control over price, quality, credential access, servicing records, plan access, fees, account wrappers, subsidy caps, and proceeds ledgers. The profile must distinguish real student/worker/retiree repair from low-value credentials, upside shelters, fee leakage, and paper pass-through claims.

### Data minimization and credential reuse

Responsibility follows control over data fields, purpose, reuse, matching, sensitive-attribute storage, deletion, denial triggers, and fallback channels. A claimant with mismatched records is not the accountable actor when the system over-collects, reuses, or mis-matches data beyond what the rule morally needs.

## Remaining debt

After rev0297, the largest remaining placeholder cluster is `environment_climate_commons`, followed by `social_floor_public_services`, `cross_border_reporting`, `regulated_networks_platforms`, and `release_integrity_currentness`. The next substantive pass should probably choose environment/climate/commons because generic accountability there can understate non-compensable harm, public-trust duties, and sacrifice-zone risk.
