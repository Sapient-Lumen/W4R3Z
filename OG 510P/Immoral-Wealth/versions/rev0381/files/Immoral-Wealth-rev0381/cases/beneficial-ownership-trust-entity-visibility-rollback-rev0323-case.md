---
status: active_case
claim_kind: case_memo
route_role: dynastic_opacity_core
canonical_anchor: false
route_refs:
- dynastic_opacity_core
- intergenerational_transfer_core
- ownership_visibility_core
- anti_avoidance_core
- case_calibration_core
supersedes: null
depends_on:
- beneficial-ownership-trust-entity-visibility-rollback-rev0323-scoreboard.json
source_refresh_due: 2026-09-30
case_pressure: rev0325_substance_hardening
---

# Beneficial-ownership visibility rollback, trusts, and domestic entity reporting gaps — active case memo

## Current holding

This case is now an active current-law volatility case. The BOI perimeter cannot be treated as a generic ownership-transparency improvement because the cited FinCEN materials describe a narrowed reporting perimeter in which domestic reporting companies and U.S. persons are outside the current BOI reporting obligation, while foreign reporting companies remain the central covered class. [S431] [S169] [S433]

The archive therefore treats BOI visibility as a perimeter map, not a slogan. A case that says “beneficial ownership is reported” must specify entity type, domestic or foreign status, trust/legal-arrangement role, verification mechanism, competent-authority access, and the rulemaking/litigation date.

## Unit of analysis

- **Jurisdiction:** U.S. BOI reporting perimeter, with FATF legal-arrangement standards used as a transparency comparator.
- **Subsystem:** `beneficial_ownership_visibility_rollback_case`.
- **Dominant breach:** anti-avoidance, sanctions, procurement, tax, and claimant remedies can overstate ownership visibility when domestic entities, trusts, control-party roles, or legal arrangements fall outside the reported perimeter.
- **Fastest washout:** current-law changes, interim/final rulemaking, litigation, domestic-entity exemptions, foreign-registration limits, and trust-control separation can change who is visible before enforcement attaches.
- **Verdict:** `correction_required` with `medium` confidence.

## Minimum evidence package

The case now requires an entity-perimeter table: domestic entity, foreign registered entity, trust/legal arrangement, U.S. person, foreign beneficial owner, applicant/formation actor, competent authority, verification status, and reporting deadline. It must also identify the current rule date and next refresh date.

## Correction path

The correction is to maintain a living BOI perimeter map. Domestic-entity exemption, trust beneficial ownership, and legal-arrangement control information must be separately scored. A pass on one lane cannot substitute for the others.

## What would change the verdict

A softer verdict would require stable, verified, adequate, accurate, and up-to-date control-party information across domestic entities and trusts, not merely foreign-company reporting. A harder verdict would be justified if the final rule or litigation leaves a durable domestic-entity opacity gap while high-wealth planning continues to route control through trusts, LLCs, foundations, or nominee/control-party structures.

## Limits

This case does not evaluate criminal liability or compliance burden. It evaluates whether the archive can safely claim ownership visibility for wealth-control vehicles under the current BOI perimeter.

## Rev0362 related BOI perimeter note

Rev0362 migrates the overlapping U.S. BOI perimeter proof burden in `united-states-beneficial-ownership-reversal-rev0309-claim-packet.json`. This trust/legal-arrangement case should not inherit certification from those edges: domestic entity and U.S.-person reporting gaps are now better proved, but trust-control visibility and alternative rails remain open. [S169] [S433] [S491]
