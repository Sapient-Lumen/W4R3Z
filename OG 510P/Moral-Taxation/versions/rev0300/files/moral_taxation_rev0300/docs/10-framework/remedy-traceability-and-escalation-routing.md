# Remedy traceability and escalation routing

## Question in one sentence

When a route identifies a morally relevant burden, how do we know the archive has named the corrective move, the blocked move, the escalation trigger, and the proceeds or repair rule rather than merely labeling the problem?[S21][S27][S117][S118][S141][S196]

## Rule

A `remedy_type` axis value is not yet a remedy. It becomes a remedy only when the route can answer four questions:

1. **Default move** — what should the designer do first if the incidence story is true?
2. **Blocked move** — what superficially plausible response must not be accepted?
3. **Escalation trigger** — what fact turns a price, rebate, waiver, or disclosure into a stronger remedy such as public option, injunction, no-go rule, refund reissue, independent review, or release block?
4. **Proceeds integrity** — if money is collected, who receives repair, how is anti-supplantation enforced, and what happens if the route cannot be traced?

The Taxpayer Bill of Rights supplies the narrow administrative prototype: the taxpayer must be able to pay no more than the correct amount, challenge the position and be heard, appeal in an independent forum, receive finality, and have privacy/confidentiality respected. Those rights generalize into the cube as a remedy spine: correction, contest, timely return, non-excessive proof, and accountable channel access.[S117][S118][S141][S196]

## Ordering rule

Use this pass after incidence and private-rail classification but before rate, threshold, or proceeds design. If the legal remitter is not the real burden bearer, or if a necessary channel controls access, the remedy must attach to the real burden path, not merely to the statutory label.

## Remedy families

| Family | Use when | Default move | Blocked move |
|---|---|---|---|
| channel_access_and_cure | filing, refund, payment, appeal, benefit, or proof runs through a channel | preserve public/assisted fallback, notice, cure, no-rent timing, and hardship escalation | treating a private rail, app, bank, or vendor account as the public right itself |
| record_correction_and_accountable_review | data, model, third-party report, prefill, or enforcement record drives the result | provide correction, independent review, audit trail, and issue-scoped finality | making the affected person disprove an opaque or official-looking record without authority to fix it |
| floor_repair_and_no_rent_relief | a charge or tax collides with subsistence, disability, family, housing, health, connectivity, or care floors | rebate, waiver, benefit account, direct support, or protected access | funding the public claim by charging the protected floor |
| rent_capture_with_pass_through_control | scarce location, monopoly, platform, finance, IP, or natural-resource rent is the target | tax or recapture residual rent upstream while guarding tenants, workers, consumers, and small suppliers | taxing a pass-through channel and calling it rent capture |
| harm_repair_or_no_go | pollution, addiction, congestion, cybersecurity, safety, or cumulative burden is the target | repair, mitigation, exposure reduction, bond, reserve, or no-go gate before revenue | selling permission to cause non-compensable harm |
| risk_prefunding_and_clawback | insurance, guarantee, bank, disaster, or systemic backstop is involved | prefund reserves, price risk, claw back private upside, and protect policyholder/depositor floors | socializing loss while privatizing upside |
| public_upside_and_anti_supplantation | subsidy, procurement, research, public input, or public capacity creates value | condition support, retain public upside, claw back failure, and prevent budget substitution | allowing public funds to become private rent without reciprocal duty |
| classification_correction | legal status or paper role hides control, benefit, or burden | route to the substance, allow contest, and document bounded imputation | treating the label as the moral answer |
| source_release_integrity | currentness, source hierarchy, scorecard, manifest, or cube coverage controls the answer | block release, refresh source, regenerate surface, and rerun golden cases | shipping a clean-looking release with stale or drifting machine surfaces |
| general_design_review | no specific remedial channel is yet known | keep the issue in design review and require explicit remedy before approval | letting a general tax-design label pass as operational justice |

## Escalation rule

A lighter remedy is adequate only while the harmed party can actually exit, understand, contest, and be made whole. Escalate when delay threatens a protected floor, when a private rail captures tolls, when disclosure is suppressed, when a record cannot be corrected, when a backstop becomes recurring subsidy, when cumulative burden is non-compensable, or when proceeds cannot be traced to repair.

## Machine surface

The companion machine layer is [`../00-meta/remedy-profiles.json`](../00-meta/remedy-profiles.json), validated by [`../../tools/audit_remedy_profiles.py`](../../tools/audit_remedy_profiles.py). Each route record must have one remedy profile stating the remedy family, default move, blocked move, guardrails, escalation trigger, and proceeds-integrity posture.

## Source IDs only

[S21][S27][S117][S118][S141][S196]

[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S117]: ../../SOURCES.md#S117
[S118]: ../../SOURCES.md#S118
[S141]: ../../SOURCES.md#S141
[S196]: ../../SOURCES.md#S196
