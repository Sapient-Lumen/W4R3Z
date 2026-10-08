# Assessment-unit and care-load ladder

## Question in one sentence

Given the archive's closed rule that ordinary human earnings and civic standing should stay **person-first** while care and dependency are recognized directly, **what is the smallest workable ladder for deciding when tax design should remain individual, when it should add direct care-side support, when narrow shared-resource tests are justified, and when grouping belongs only to anti-avoidance rather than to ordinary household life?**[S2][S18][S31][S32][S33][S64][S65][S66][S161][S162][S164][S165][S166][S167]

## Closed rules invoked

This memo does **not** reopen the archive's constitutional waist. It relies on:

- [`../10-framework/assessment-units-care-and-dependency-routing.md`](../10-framework/assessment-units-care-and-dependency-routing.md)
- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/anti-discrimination-and-status-proxy-routing.md`](../10-framework/anti-discrimination-and-status-proxy-routing.md)
- [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md)
- [`../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md`](../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md)

The constitutional question is already settled: **default ordinary human earnings liability to the individual person; recognize care, disability, and dependency explicitly; use household facts only where they are doing real support or delivery work; and reserve group aggregation for anti-avoidance or concentrated-wealth problems rather than for routine earnings taxation.**[S2][S18][S31][S32][S33]

## Why calibration is still needed

The closed rule settles the direction but not yet the smallest usable operating ladder. A workable calibration has to avoid five different failures at once:

1. **second-earner traps** created by household-based rate schedules, spouse allowances, or family-income phase-outs,[S32][S33]
2. **household shadowing** where one adult's notice, refund, or filing identity disappears into another adult's account or return,[S18][S32][S64]
3. **care blindness** where taxes see earnings but not childcare, disability, elder care, or intermittent work constraints,[S31][S32][S33]
4. **stale shared-resource tests** that misclassify separated, abused, informally housed, or unstable households,[S18][S64][S65][S66]
5. and **anti-avoidance creep** where rules meant for trusts, shell chains, or dynastic wealth are used to justify routine household fusion instead.[S2][S18][S31]

## Small option set

### Option A — person-only everywhere

Use only the individual person and ignore household, care-load, and shared-resource facts almost entirely. This preserves standing, but it misses real dependency and care burdens and can under-target floor protection where resource sharing does matter.[S18][S31][S32]

### Option B — person-first filing plus direct care-side recognition

Keep ordinary earnings, notice, withholding, refunds, and standing attached to the **individual person**, but add child, disability, caregiver, or dependent recognition through direct transfers, services, refundable credits, or similarly explicit support channels.[S31][S32][S33][S64]

This is the cleanest default for most wage and self-employment taxation because it preserves personhood while treating care load as something to be recognized directly rather than by silently merging adults into one tax identity.

### Option C — bounded shared-resource test for means-tested floor protection

Keep person-first filing, but allow a **narrow, rebuttable shared-resource test** where means-tested support genuinely requires it. Use the shortest workable household definition, direct payment to the entitled person where possible, and override lanes for separation, coercion, unstable housing, and informal care arrangements.[S31][S32][S64][S65][S66]

This option is appropriate for negative-tax delivery, recurring supports, and some low-income transfers where actual resource sharing matters, but it should remain a bounded support rule rather than a general theory of household personhood.

### Option D — elective joint smoothing only under strict conditions

Permit a **voluntary** joint or transferable adjustment only when all four conditions hold:

1. it is elective rather than compulsory,
2. each adult retains separate notice, filing visibility, and refund rights,
3. the rule clearly reduces volatility or care-related timing strain rather than rewarding dependency,
4. and the election is easy to exit when circumstances change.[S18][S31][S32][S33]

This is a narrow lane for unusual smoothing problems, not a justification for household taxation by default. It also requires a person-level unwind lane: spouse relief, injured-spouse allocation, and dependency / separated-household correction should be no-rent and issue-bounded where the joint fact no longer tracks separate responsibility.[S161][S162][S164][S165][S166][S167]

### Option E — anti-avoidance grouping outside ordinary earnings

Use beneficial-ownership or related-party grouping for trusts, shell chains, closely held vehicles, family wealth structures, or deliberate threshold fragmentation. Do **not** let that anti-avoidance logic swallow ordinary labor income or the civic standing of co-resident adults.[S2][S31][S34][S35]

## Provisional recommendation

Adopt a **four-step practical ladder**:

| Stage | When it should apply | Assessment-unit answer | Main guardrail |
|---|---|---|---|
| 0. ordinary earnings default | most wages, salaries, routine self-employment, notice, refunds, withholding | **individual person only** | no compulsory jointness or spouse-default filing |
| 1. care-load recognition | children, disability, elder care, unpaid care, disrupted work continuity | **individual person plus direct care-side support** | support should track care or dependency, not marital status alone |
| 2. floor-protection means test | negative-tax delivery, recurring supports, some low-income transfers | **narrow rebuttable shared-resource test** | pay the entitled person directly where possible; preserve override lanes |
| 2.5. household-status correction | spouse debt, joint refund allocation, dependent conflict, custody / separation facts, spouse-liability relief | **person-level allocation or correction delta** | no paid-help requirement; no adverse-household cooperation as the entry fee |
| 3. anti-avoidance / wealth grouping | trusts, shell chains, dynastic wealth, threshold gaming, closely coordinated ownership | **beneficial-ownership or related-party grouping** | do not export this grouping logic back into routine human earnings taxation |

The archive's provisional setting is therefore **B + C + E, with D available only as a tightly constrained elective lane**.[S2][S18][S31][S32][S33][S64][S65][S66]

That is the narrowest workable recommendation because it preserves ordinary civic standing, recognizes care explicitly, keeps shared-resource testing bounded to cases where it is morally doing work, and prevents anti-fragmentation logic from becoming a disguised household-fusion regime.

## Failure-mode capsule

Axes: `captive_household_unit`, `marriage_penalty`, `opacity_or_erasure`, `trapdoor_or_cliff`. Block compulsory household fusion that erases person-level notice, refund, standing, or care claims.

## Recalibration trigger capsule

Triggers: `protected_floor_or_incidence_shift`, `record_or_measurement_staleness`, `second_earner_effective_rate_spike`. Reopen on care-record change, exclusion by household tests, joint-rule penalties, or anti-avoidance creep.

## Accountability capsule
Authoritative assignment: route `assessment_unit_and_care_load` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `assessment_unit_rule_designer_and_dependency_record_holder`.
- Rent/benefit trace: `household_grouping_arbitrage_claimant_or_budget_actor_using_care_load_invisibility_to_deny_direct_support`.
- Bottleneck/evidence: `filing_status_dependency_and_shared_resource_record_gate; care_load_verification_channel +1 more`; evidence starts with `individual_income_liability_and_notice_records; dependency_care_hours_and_shared_resource_records +3 more`.
- Fallback duty: `fallback_public_body_must_preserve_person_first_liability_individual_notice_direct_care_support_and_no_captive_household_forfeiture`.


## Source IDs only

[S2][S18][S31][S32][S33][S34][S35][S64][S65][S66][S161][S162][S164][S165][S166][S167]

[S2]: ../../SOURCES.md#S2
[S18]: ../../SOURCES.md#S18
[S31]: ../../SOURCES.md#S31
[S32]: ../../SOURCES.md#S32
[S33]: ../../SOURCES.md#S33
[S34]: ../../SOURCES.md#S34
[S35]: ../../SOURCES.md#S35
[S64]: ../../SOURCES.md#S64
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S161]: ../../SOURCES.md#S161
[S162]: ../../SOURCES.md#S162
[S164]: ../../SOURCES.md#S164
[S165]: ../../SOURCES.md#S165
[S166]: ../../SOURCES.md#S166
[S167]: ../../SOURCES.md#S167
