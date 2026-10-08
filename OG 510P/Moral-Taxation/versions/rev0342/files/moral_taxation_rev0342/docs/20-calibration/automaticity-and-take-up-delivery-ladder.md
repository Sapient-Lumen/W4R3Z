# Automaticity and take-up delivery ladder

## Question in one sentence

Given the archive's closed rule that floor-protecting relief should default toward automaticity, prefill, assisted claiming, and low-friction correction, **what is the smallest workable delivery ladder for rebates, refunds, recurring supports, and repair payments without turning administration into either a claim maze or an unreviewable auto-state?**[S4][S15][S17][S21][S22][S31][S32][S33][S64][S65][S66][S68]

## Closed rules invoked

This memo does **not** reopen the archive's constitutional waist. It relies on:

- [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md)
- [`../10-framework/regressivity-correction-and-floor-protection-routing.md`](../10-framework/regressivity-correction-and-floor-protection-routing.md)
- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/timing-and-liquidity-routing.md`](../10-framework/timing-and-liquidity-routing.md)
- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/review-triggers-and-policy-reversibility.md`](../10-framework/review-triggers-and-policy-reversibility.md)

The constitutional question is already settled: **where the state already knows enough that floor protection, routine refund, or harm repair is due, justice usually requires automatic payment, tight prefill, or similarly low-friction delivery rather than paper-only entitlement.**[S4][S21][S64][S65][S66][S68]

## Why calibration is still needed

The archive already says that high-friction relief is a design failure, but it still needs a smallest workable operating standard for real systems. A usable standard has to avoid two opposite failures at once:

1. **paper-floor failure**, where support exists in law but only the organized or well-advised actually receive it, and  
2. **over-automated brittleness**, where stale records, hidden assumptions, or digital chokepoints silently deny support with little human correction or appeal.[S31][S32][S33][S64][S65][S68]

## Small option set

### Option A — application-first by default

Require a separate full claim, annual reapplication, or stand-alone form for most rebates, refundable credits, routine refunds, and repair payments, even where the administration already holds the main eligibility facts.[S64][S65][S66]

This is too weak for the archive. It preserves non-take-up as a hidden austerity device.

### Option B — prefill everywhere, but still claimant-initiated

Provide prefilled forms or reminders, but still require the subject to discover the claim, open the process, and affirmatively request payment before any routine support is released.[S65][S66]

This is better than pure application-first design, but still too weak where eligibility is already highly legible and payment timing matters to subsistence or repair.

### Option C — tiered low-friction delivery ladder

Use a compact four-step ladder:

1. **automatic payment or enrolment** for routine over-withholding refunds, broad floor rebates, and other supports where the state already knows enough to pay safely,  
2. **prefilled one-step confirmation** where periodic change is real but ordinary, such as recurring care, disability, child, or housing-linked support,  
3. **assisted claiming with human and offline lanes** where facts are complex, disputed, or changing quickly, and  
4. **full bespoke application** only for unusual, negotiated, or privilege-like relief rather than for ordinary floor protection.[S4][S21][S31][S32][S33][S64][S65][S66][S68]

This option keeps delivery proportional to factual uncertainty instead of making every justified payment fight through the same maze.

### Option D — universal automaticity for all relief

Push nearly every tax-linked payment, offset, and repair channel into fully automatic delivery regardless of evidentiary uncertainty, household complexity, or dispute risk.[S64][S65]

This is stronger than the archive needs as a general minimum. It risks locking in stale records, overpaying where facts are genuinely unsettled, and collapsing the distinction between protected floors and negotiated privileges.

## Provisional recommendation

Adopt **Option C — the tiered low-friction delivery ladder** as the archive's default automaticity calibration.[S4][S21][S31][S32][S33][S64][S65][S66][S68]

Apply it with a simple presumption:

- **automatic first** when the payment protects the floor and the administration already has the decisive facts,  
- **prefilled confirmable** when recurring change matters but a full reapplication would be mostly ritual,  
- **assisted claimable** when human explanation and discretionary fact correction are genuinely needed, and  
- **fully applied-for** mainly when the claimant seeks special privilege, negotiated treatment, or exceptional sector-specific relief.

That is the narrowest workable setting because it protects take-up without making automation morally unanswerable.

## Default delivery table

| Payment or relief type | Default delivery rung | Why this rung usually fits | Archive warning |
|---|---|---|---|
| routine over-withholding refund or ordinary negative-income support | automatic payment | the administration usually already sees the decisive payroll and withholding facts.[S4][S64][S65][S66] | do not hold back ordinary floor protection until an annual claim ritual is completed. |
| broad consumption rebate, energy offset, or local burden rebate | automatic payment or bill offset | compensation loses moral force when prices rise immediately but relief arrives only after separate navigation.[S3][S4][S15][S17][S68] | broad taxes become functionally regressive when offsets are slow or low-take-up. |
| recurring child, care, disability, or housing-linked support | prefilled one-step confirmation | circumstances can change, but usually not enough to justify full rediscovery each cycle.[S31][S32][S33][S64][S65] | do not let stale household defaults or inaccessible interfaces silently suppress payment. |
| AI-transition worker support or locality repair | automatic or assisted routing through payroll, benefits, and local fiscal channels | upstream AI-linked collection loses legitimacy if downstream support depends on claimant exhaustion.[S15][S17][S22][S67][S68] | controller-side automation should not be paired with downstream manual justice. |
| disputed, unusual, or negotiated privilege-like relief | full application with review | factual uncertainty or rent-seeking risk is high enough that friction is more tolerable.[S21][S27][S68] | do not equalize privilege review and floor-protection delivery. |

## Failure-mode capsule

Cube anti-pattern axes: `access_exclusion`; `claim_friction`.
Use the route profile and remedy profile for actor/remedy assignment; this memo should not maintain a second local anti-pattern taxonomy.
Source continuity: [S21][S27][S31][S32][S33][S64][S65][S66][S68]

## Recalibration trigger capsule

Cube review-trigger axes: `access_or_fallback_failure`.
Reopen the route when those triggers move materially, especially where source currentness, protected-burden evidence, proceeds integrity, or remedy access changes the practical recommendation.
Source continuity: [S16][S21][S31][S32][S64][S65][S68]

## Accountability capsule

Authoritative assignment: route `automaticity_and_take_up_delivery` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `benefit_or_tax_program_owner_controlling_prefill_auto_enrollment_and_claim_friction`.
- Rent/benefit trace: `agency_budget_saver_vendor_or_claim_intermediary_benefiting_from_non_take_up_overclaim_or_friction`.
- Bottleneck/evidence: `prefill_engine; identity_proofing_channel +2 more`; evidence starts with `eligibility_universe_take_up_gap_and_non_take_up_amount_record; prefill_match_error_identity_failure_and_notice_record +2 more`.
- Fallback duty: `public_body_must_preserve_non_digital_notice_cure_human_help_and_reissue_channel_for_missed_benefits_with_fallback_channel`.


## Source IDs only

[S3][S4][S15][S16][S17][S21][S22][S27][S31][S32][S33][S64][S65][S66][S67][S68]

[S3]: ../../SOURCES.md#S3
[S4]: ../../SOURCES.md#S4
[S15]: ../../SOURCES.md#S15
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S21]: ../../SOURCES.md#S21
[S22]: ../../SOURCES.md#S22
[S27]: ../../SOURCES.md#S27
[S31]: ../../SOURCES.md#S31
[S32]: ../../SOURCES.md#S32
[S33]: ../../SOURCES.md#S33
[S64]: ../../SOURCES.md#S64
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S67]: ../../SOURCES.md#S67
[S68]: ../../SOURCES.md#S68
