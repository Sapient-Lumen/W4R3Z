# Model-assisted tax administration minimum standard

## Question in one sentence

Given the archive's closed rule that tax administration must remain explainable, reconstructible, correctable, and appealable, **what is the smallest workable disclosure-and-review standard for model-assisted tax administration without turning ordinary filing into a litigation-grade replay exercise?**[S1][S16][S17][S23][S25][S27][S44][S660]

## Closed rules invoked

This memo does **not** reopen the archive's constitutional waist. It relies on:

- [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md)
- [`../10-framework/measurement-valuation-and-proxy-routing.md`](../10-framework/measurement-valuation-and-proxy-routing.md)
- [`../10-framework/standing-representation-and-remedy-routing.md`](../10-framework/standing-representation-and-remedy-routing.md)
- [`../10-framework/review-triggers-and-policy-reversibility.md`](../10-framework/review-triggers-and-policy-reversibility.md)
- [`../10-framework/automaticity-and-claim-friction-routing.md`](../10-framework/automaticity-and-claim-friction-routing.md)

The constitutional question is already settled: **serious tax liabilities and denials should not depend on proprietary black boxes that cannot be reconstructed, explained, corrected, or appealed by ordinary subjects and reviewers.**[S1][S16][S17][S23][S25][S27][S44]

## Why calibration is still needed

Rev0286 AI-governance source note: agency use, procurement, and monitoring of AI now has a current IRS internal-governance anchor, so model-assisted administration should classify governance records separately from taxpayer-side AI advice.[S660]

The archive already says what administration may **not** become, but it still needs the narrowest workable operating standard for live model-assisted systems. A usable standard has to avoid two opposite failures at once:

1. **black-box extraction**, where notices, denials, or escalations arrive with only a result and no usable reconstruction path, and  
2. **full-forensic overload**, where every automated assist is treated as if it requires courtroom-grade replay, long evidentiary packets, and expert reconstruction before ordinary administration can function at all.[S1][S16][S17][S23][S25][S27]

## Small option set

### Option A — result-only opacity

Allow model-assisted administration to issue adverse notices, audit escalations, or benefit denials with only the bottom-line amount or status plus a generic reason code. Internal features, proxy ladders, versioning, and review thresholds remain effectively hidden.[S16][S17][S27]

This is too weak for the archive. It makes correction and appeal mostly formal.

### Option B — summary explanation only

Require a short human-readable explanation such as "income mismatch" or "risk inconsistency," but do not require a stable rule-version identifier, named proxy family, input-category list, or a replayable correction packet.[S1][S16][S23]

This is better than pure opacity, but still too weak where the system is doing more than nudging clerical sorting.

### Option C — minimum auditable packet

Require every **material adverse administrative action** to travel with a compact packet containing at least:

1. a stable **rule or model version identifier**,  
2. the **tax period, action type, and legal basis** being applied,  
3. the main **data-source categories** used,  
4. any **proxy, safe harbor, or estimation ladder** actually used,  
5. the main **delta or trigger** that produced the action,  
6. a plain-language statement of what the subject can **correct, contest, or supplement**,  
7. a named **deadline and review lane**, including how to reach a human reviewer when the action is adverse, and  
8. retention and audit information sufficient for later supervisory review without requiring ordinary taxpayers to reconstruct the whole model from scratch.[S1][S16][S17][S23][S25][S27][S44]

This option still allows automation, triage, and prefilling, but it blocks unreviewable black-box dependence.

### Option D — full evidentiary replay for every affected case

Require the administration to expose a near-complete model trace, feature weighting logic, and full evidentiary replay for every automated or model-assisted step, even for minor or low-stakes cases.[S16][S17][S27]

This is stronger than the archive needs as a general minimum. It risks turning ordinary administration into an expensive expert contest and may reduce usable automation that would otherwise help with prefilling, early correction, and low-friction relief.[S1][S25][S64][S65]

## Provisional recommendation

Adopt **Option C — the minimum auditable packet** as the archive's default operating standard for model-assisted tax administration.[S1][S16][S17][S23][S25][S27][S44]

Use a **tiered application** of that standard:

- **informational nudges, prefill suggestions, and low-stakes routing** may use lighter explanation,  
- **material adverse actions** should always carry the full minimum packet,  
- and **high-stakes escalations** such as large reassessments, frozen refunds, enforcement referrals, or repeated adverse scoring should also trigger earlier human review and stronger supervisory logging.[S16][S17][S23][S25][S27]

That is the narrowest workable setting because it preserves three things at once:

- usable automation for clerical speed and take-up improvement,  
- human-auditable reconstruction for material liability or denial,  
- and a correction / appeal path ordinary subjects can actually use without expert reverse engineering.

## Default delivery-and-review table

| Case type | Minimum explanation standard | Human review requirement | Archive stance |
|---|---|---|---|
| low-stakes prefill or reminder | short explanation plus visible correction path | on request | allowed if no adverse effect is locked in yet.[S25][S64][S65] |
| ordinary discrepancy notice or adjustment proposal | minimum auditable packet | available before finalization | default standard.[S1][S16][S23] |
| frozen refund, denied relief, audit escalation, or sizable reassessment | minimum auditable packet plus stronger logging and supervisor visibility | proactive or immediate on request | should not depend on hidden model logic alone.[S16][S17][S27][S44] |
| enforcement referral or repeated high-risk flagging | packet plus explicit review record and retained challenge path | required before coercive action | tax administration may use models for triage, not for unreviewable coercion.[S17][S27][S44] |

## Failure-mode capsule

Cube anti-pattern axes: `classification_or_label_arbitrage`; `model_score_finality`; `opacity_or_erasure`.
Use this controlled axis packet instead of a second local anti-pattern taxonomy; add only route-specific exceptions in the ladder or recommendation text.
Source continuity: [S1][S16][S17][S23][S25][S27][S44]

## Recalibration trigger capsule

Cube review-trigger axes: `generic_notice_only`; `model_or_evidence_drift`.
Reopen the route when those triggers materially change controller identity, control evidence, protected burden, contest access, or fallback duty.
Source continuity: [S1][S16][S17][S23][S25][S27][S44]

## Accountability capsule

Profile: `model_assisted_tax_administration_minimum` in `docs/00-meta/actor-accountability-profiles.json`. Duty owner: `revenue_agency_model_owner_and_decision_official_for_material_adverse_action`. Benefit/rent trace: `agency_or_vendor_benefiting_from_black_box_administration_cost_shift_or_unreviewable_automation`.
Bottleneck/evidence start: `model_assisted_notice_pipeline`; `case_selection_or_adjustment_queue`; `human_review_and_correction_channel`; `model_or_rule_version_and_action_type_record`; `data_source_category_proxy_and_trigger_delta_record`; `legal_basis_issue_category_and_tax_period_record`. Fallback: `public_body_must_preserve_no_rent_fallback_notice_cure_and_nonforfeiture_for_model_assisted_tax_administration`.
Source continuity: [S16][S17][S27][S44][S660]

## Source IDs only

[S1][S16][S17][S23][S25][S27][S44][S64][S65][S660]

[S1]: ../../SOURCES.md#S1
[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S23]: ../../SOURCES.md#S23
[S25]: ../../SOURCES.md#S25
[S27]: ../../SOURCES.md#S27
[S44]: ../../SOURCES.md#S44
[S64]: ../../SOURCES.md#S64
[S65]: ../../SOURCES.md#S65
[S660]: ../../SOURCES.md#S660
