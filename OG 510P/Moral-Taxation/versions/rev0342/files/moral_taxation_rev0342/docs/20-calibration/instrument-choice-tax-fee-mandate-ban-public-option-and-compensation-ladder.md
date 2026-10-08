# Instrument-choice tax, fee, mandate, ban, public-option, and compensation ladder

## Question in one sentence

How should the archive choose the policy action when a proposal's label says one thing but its incidence, authority, public-access, or harm-repair job says another?[S573][S662][S663][S664]

## Companion routes

Use this memo with:

- [`../10-framework/instrument-choice-and-non-tax-alternatives-routing.md`](../10-framework/instrument-choice-and-non-tax-alternatives-routing.md)
- [`../10-framework/policy-action-tax-fee-mandate-ban-public-option-and-compensation-routing.md`](../10-framework/policy-action-tax-fee-mandate-ban-public-option-and-compensation-routing.md)
- [`../10-framework/remedy-traceability-and-escalation-routing.md`](../10-framework/remedy-traceability-and-escalation-routing.md)
- [`../10-framework/necessary-private-rail-and-channel-incidence-routing.md`](../10-framework/necessary-private-rail-and-channel-incidence-routing.md)
- [`../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md`](../10-framework/user-fee-service-charge-utility-and-public-access-toll-routing.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — label inherits action | the proposal says fee, tax, contribution, premium, offset, or mitigation payment and the cube accepts the label | Reject. The label is evidence, not the answer. |
| B — tax / levy | broad legislative revenue, rent capture, public-capacity finance, or compensable harm pricing | Accept when incidence, protected floors, representation, and proceeds/review rules are explicit. |
| C — user fee / service charge | charge for an identifiable special benefit, service, or resource with cost/value nexus | Accept only with access waivers, essential-service protection, cost review, and no general-revenue laundering. |
| D — duty / mandate / standard | required behavior rather than revenue because monitoring, rights, safety, or repair cannot be handled by price | Use when price would permit non-repairable harm, rights violations, labor-status evasion, or safety failure. |
| E — public option / fallback | public or no-rent channel remains available where private rails control access | Required when exit is fictitious or the private channel is necessary for filing, payment, refund, benefit, connectivity, or appeal. |
| F — no-go / veto / prohibition | harm cannot be priced or repaired adequately | Required for non-compensable, cumulative, corrupting, or catastrophic risks. |
| G — compensation / rebate / credit | relief reaches the real burden bearer | Accept only when payment timing, delivery channel, and contest rights match the burden. |

## Ten-gate ladder

1. **label gate** — record the proposal's label but do not let it decide the action family.
2. **authority gate** — ask whether the institution has tax power, fee authority, licensing power, spending power, enforcement power, or only guidance authority.
3. **benefit-nexus gate** — if the instrument is a fee, identify the special benefit, cost/value basis, and review cadence.
4. **general-public-benefit gate** — if the charge funds broad public protection, classify it as tax-like or appropriations-dependent rather than fee-like.
5. **essential-access gate** — if payment gates filing, appeal, refund, basic service, identity, mobility, care, or connectivity, require waiver, public fallback, or no-rent access.
6. **harm-compensability gate** — if harm cannot be made whole, escalate from price to duty, permit denial, siting veto, or no-go rule.
7. **incidence gate** — choose the action that reaches the real burden bearer, not the legal remitter.
8. **private-rail gate** — if a private channel controls the action, require fee caps, portability, public fallback, and no forfeiture from channel failure.
9. **proceeds/remedy gate** — if money is collected for repair, tie it to recipient, timing, anti-supplantation, and clawback.
10. **profile gate** — update `docs/00-meta/policy-action-profiles.json` and rerun `tools/audit_policy_action_profiles.py`.

## Default settings

| Parameter | Default | Redesign trigger |
|---|---|---|
| user fee | special benefit or service cost/value nexus | charge funds general public regulation, redistribution, or unrelated agency capacity |
| tax | legislative revenue/rent/harm/public-capacity instrument | label is used to sell non-compensable harm or bypass remedy floors |
| mandate | duty where price is inadequate | proposal converts a safety, labor, privacy, speech, or due-process duty into optional payment |
| public option | required for necessary private channels | bank, app, wallet, vendor, insurer, telecom, or platform is the only practical path |
| no-go | required for non-compensable harm | proposal substitutes offset, mitigation fee, or abatement for denial |
| compensation | paid to real burden bearer through workable channel | relief goes to remitter, vendor, or advantaged intermediary |

## Anti-pattern definitions

- **fee-tax laundering** — a general-revenue, broad-regulation, or public-protection charge is called a user fee without a special-benefit or cost/value nexus.
- **priced permission for non-compensable harm** — a tax, offset, or mitigation payment sells permission for harm that should be blocked.
- **mandate disguised as tax** — a rights, safety, labor, privacy, or due-process duty is recast as a revenue choice to weaken enforcement.
- **public-option erasure** — the public right is made practically dependent on a private app, bank, vendor, platform, insurer, or utility.
- **compensation-to-remitter error** — the relief follows the statutory payer while the real bearer absorbs price, denial, delay, or risk.

## Machine checkpoint

Every cube route must have a policy-action profile. The profile does not replace the `instrument` axis; it states what the instrument is allowed to do, what category error it must block, and when the route must escalate to duty, public option, compensation, no-go rule, or release block.

## Accountability capsule

Authoritative assignment: route `instrument_choice_tax_fee_mandate_ban_public_option_compensation` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `policy_owner_legislature_or_regulator_classifying_tax_fee_mandate_ban_public_option_or_compensation`.
- Rent/benefit trace: `remitter_vendor_regulated_actor_or_public_body_gaining_from_tax_fee_mandate_ban_public_option_or_compensation_category_error`.
- Bottleneck/evidence: `statutory_instrument_label; fee_schedule +3 more`; evidence starts with `instrument_authority_function_and_label_record; benefit_nexus_public_revenue_or_compensation_basis_record +2 more`.
- Fallback duty: `public_body_must_preserve category_challenge_public_option_waiver_refund_and no_go_review channel_with_fallback_channel`.


## Source IDs only

[S573][S662][S663][S664]

[S573]: ../../SOURCES.md#S573
[S662]: ../../SOURCES.md#S662
[S663]: ../../SOURCES.md#S663
[S664]: ../../SOURCES.md#S664
