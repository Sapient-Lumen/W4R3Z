# Transferee, nominee, alter-ego, successor, and wrongful-levy ladder

Use this calibration memo when tax collection pressure moves away from the named taxpayer and toward **a third party, a third-party-held asset, a transferred asset, a successor entity, a nominee title holder, an alleged alter ego, or property that may have been wrongfully levied**.

## Companion routes

- [`../10-framework/collection-and-remittance-routing.md`](../10-framework/collection-and-remittance-routing.md)
- [`../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md`](../10-framework/beneficial-ownership-and-anti-fragmentation-routing.md)
- [`../10-framework/tax-subjecthood-and-liability-routing.md`](../10-framework/tax-subjecthood-and-liability-routing.md)
- [`../10-framework/record-asymmetry-burden-shifting-and-adverse-inference-routing.md`](../10-framework/record-asymmetry-burden-shifting-and-adverse-inference-routing.md)
- [`../../archive/193-transferee-nominee-alter-ego-successor-wrongful-levy-and-third-party-property-collection-should-not-be-turned-into-dragnet-rents-or-innocent-owner-traps.md`](../../archive/193-transferee-nominee-alter-ego-successor-wrongful-levy-and-third-party-property-collection-should-not-be-turned-into-dragnet-rents-or-innocent-owner-traps.md)

## Option scan

| Option | Description | Default judgment |
|---|---|---|
| A — named-taxpayer only | never pursue transferees, nominees, alter egos, successors, or third-party-held property.[S21][S34][S35] | Reject: invites asset stripping and sham transfers. |
| B — solvent-outsider sweep | pursue any related, branded, title-holding, payroll, banking, vendor, customer, affiliate, or successor party when the taxpayer cannot pay.[S336] | Reject: turns collection convenience into liability. |
| C — theory-specific proof ladder | require a named theory, property / value boundary, Counsel / Advisory or equivalent review where required, and a remedy path before collection shifts.[S330][S331][S332][S333][S334][S335][S338] | Adopt. |
| D — suit-first only | require judicial action before every third-party collection shift.[S330][S333] | Reject as universal rule; useful for some transferee and fraudulent-transfer cases, but too rigid for ordinary levies or clearly scoped special-condition liens. |

## Adopted ladder

1. **No third-party collection lane** — use when the outsider is merely a relative, vendor, payroll contact, bank, employer, customer, purchaser, agent, title holder, or successor brand without property, value, continuity, or identity-collapse proof.[S21][S27][S39][S336]
2. **Record-development / theory-selection lane** — use when facts suggest nominee, alter ego, transferee, successor, fiduciary, or fraudulent-transfer issues but the file has not selected one theory, identified the property, or documented approval and notice.[S331][S332][S334]
3. **Property-scoped nominee / levy-holder lane** — use when the taxpayer's beneficial interest in specific property is shown, or a third party holds wages, accounts, receivables, benefits, or other taxpayer property; limit the reach to that property and preserve return / exemption / hardship review.[S184][S331][S333][S334][S336][S337]
4. **Alter-ego / successor continuity lane** — use when the third party and taxpayer are so aligned that separate identity is not substantively real, or a successor-in-interest truly steps into the taxpayer's shoes; require identity or continuity proof, not relationship alone.[S331][S332][S334]
5. **Transferee / fraudulent-transfer lane** — use when property or value moved away from the taxpayer in a way that defeats collection; route through the available statutory assessment, suit, judgment, or lien path and cap recovery to the theory's value and timing limits.[S330][S331]
6. **Wrongful-levy return / outsider-remedy lane** — use when a non-taxpayer asserts that seized property was not the taxpayer's or was exempt, overreached, or wrongfully taken; prioritize administrative return, CAP routing, and clear proof allocation.[S333][S335][S338]
7. **Upstream-enabler / evasion lane** — reserve for organized asset-stripping, sham transfers, concealment, repeated fraudulent conveyance, or professional facilitation after civil property and liability paths are properly scoped.[S34][S35][S39][S330]

## Evidence packet before collection shift

A third-party collection-shift packet should show:

- the taxpayer, periods, assessed amounts, collection status, and undisputed balance;
- the proposed theory and why narrower ordinary collection is insufficient;
- the property, transferred value, account, receivable, benefit, wage stream, or successor asset at issue;
- title, possession, beneficial ownership, consideration, timing, control, use, commingling, continuity, and relationship facts;
- Counsel / Advisory review, special-condition name line, property description, and single-theory explanation where relevant;
- the affected third party's notice, CDP / CAP / equivalent appeal posture, wrongful-levy return route, hardship route, and public-record correction path.[S185][S186][S330][S331][S332][S333][S334][S335][S338]

## Defaults

- **Ordinary bank, employer, vendor, or customer served with a levy:** comply only as property holder; do not treat the recipient as tax debtor absent a separate theory.[S184][S336]
- **Family title holder with property-specific facts:** develop nominee record; limit the lien or levy to identified property until alter-ego or transferee proof exists.[S331][S332][S334]
- **Purchaser for value or genuinely separate successor:** no collection shift; use ordinary taxpayer collection unless a specific transferee or successor theory is proven.[S330][S331]
- **Rejected wrongful-levy claim:** route to CAP / suit information and preserve return-of-proceeds analysis rather than converting denial into finality by complexity.[S333][S335][S338]
- **Immediate hardship from wage or account levy:** release or narrow the levy according to hardship rules before collection destroys the floor.[S184][S337]

## Red flags requiring supervisory review

- the notice name line mixes nominee, alter ego, transferee, and successor theories without selecting one;
- the file lacks a property description or value limit for a nominee or transferee theory;
- the third party is targeted mainly because it is solvent, local, documented, family-connected, or easier to pressure;
- a wrongfully levied party cannot identify where to file, what evidence is needed, or how to appeal denial;
- a levy against wages, benefits, receivables, or accounts continues despite immediate hardship or ownership dispute;
- release or withdrawal is updated internally but not transmitted to the third party, recorder, bank, employer, platform, or agency that still holds the restraint.[S331][S333][S335][S337][S338]

## Failure-mode capsule

Axes: `asset_fire_sale`, `liability_misassignment`, `wrongful_levy`. Watch for proximity/title theories or levy custody substituting for value, control, notice, and ownership proof.

## Recalibration trigger capsule

Axes: `property_or_proceeds_contest_failure`, `remedy_or_contest_failure`, `record_or_measurement_staleness`. Reopen when wrongful levy, nominee/successor overreach, or delayed return/refund/interest repair appears.

## Accountability capsule

Authoritative assignment: route `transferee_nominee_alter_ego_successor_and_wrongful_levy` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `revenue_agency_or_claimant_controlling_transferee_nominee_alter_ego_successor_or_wrongful_levy_theory`.
- Rent/benefit trace: `revenue_agency_or_creditor_benefiting_from_reaching_third_party_property_or_successor_assets_without_proven_control_value_or_notice`.
- Bottleneck/evidence: `asset_transfer_record; nominee_or_alter_ego_theory_file +3 more`; evidence starts with `taxpayer_liability_asset_transfer_value_and_timing_record; ownership_control_beneficial_use_entity_separateness_and_successor_continuity_record +3 more`.
- Fallback duty: `public_body_must_preserve_fallback_wrongful_levy_notice_claim_release_return_interest_and_damage_repair_channel`.


## Source IDs only

[S21][S27][S34][S35][S39][S184][S185][S186][S330][S331][S332][S333][S334][S335][S336][S337][S338]

[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S34]: ../../SOURCES.md#S34
[S35]: ../../SOURCES.md#S35
[S39]: ../../SOURCES.md#S39
[S184]: ../../SOURCES.md#S184
[S185]: ../../SOURCES.md#S185
[S186]: ../../SOURCES.md#S186
[S330]: ../../SOURCES.md#S330
[S331]: ../../SOURCES.md#S331
[S332]: ../../SOURCES.md#S332
[S333]: ../../SOURCES.md#S333
[S334]: ../../SOURCES.md#S334
[S335]: ../../SOURCES.md#S335
[S336]: ../../SOURCES.md#S336
[S337]: ../../SOURCES.md#S337
[S338]: ../../SOURCES.md#S338
