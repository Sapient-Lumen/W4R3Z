# Remedy traceability, incidence escalation, and proceeds-integrity ladder

## Question in one sentence

How should a route prove that its proposed remedy follows the real incidence path and not just the statutory label?[S21][S27][S117][S118][S141][S196]

## Companion routes

Use this memo with:

- [`../10-framework/remedy-traceability-and-escalation-routing.md`](../10-framework/remedy-traceability-and-escalation-routing.md)
- [`../10-framework/incidence-and-protected-burden-routing.md`](../10-framework/incidence-and-protected-burden-routing.md)
- [`../10-framework/necessary-private-rail-and-channel-incidence-routing.md`](../10-framework/necessary-private-rail-and-channel-incidence-routing.md)
- [`../10-framework/proceeds-routing-and-fiscal-reciprocity.md`](../10-framework/proceeds-routing-and-fiscal-reciprocity.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — label remedy | the statute names a rebate, waiver, disclosure, or audit but does not trace who gets it | Insufficient. Treat as remedy theater until incidence and delivery are traced. |
| B — incidence-matched remedy | the corrective move reaches the real burden bearer with notice, timing, proof, and contestability | Default. This is the minimum for ordinary approval. |
| C — proceeds-routed repair | money is collected and explicitly routed to the harmed class, affected place, public backstop, or capacity need | Accept when anti-supplantation and clawback are enforceable. |
| D — escalation remedy | the design moves from price/rebate/disclosure to public option, injunction, no-go rule, refund reissue, or release block | Required when exit, contest, or make-whole repair fails. |
| E — no remedial fit | the harm is non-compensable or the channel cannot be made contestable | Use prohibition, denial, no-go siting, or route retirement rather than a tax label. |

## Ten-gate ladder

1. **incidence gate** — identify the real burden bearer before choosing the remedy recipient.
2. **legal-remitter split** — if the legal remitter can pass through cost, delay, denial, or proof burden, name the pass-through path.
3. **protected-floor gate** — if the burden lands on subsistence, disability, language, bankless, housing, health, family, or connectivity floors, use rebate, waiver, direct support, or fallback before revenue.
4. **contest gate** — provide a human-understandable basis, correction path, and independent review where the state or its vendor asserts facts.
5. **timing gate** — match refund, waiver, hardship, and reissue timing to actual need; delayed relief is not full relief when the floor is at risk.
6. **channel gate** — if a private rail is necessary, require public fallback, fee controls, portability, and no forfeiture from rail failure.
7. **proceeds gate** — classify collected money as general revenue, repair, reserve, rebate, local benefit, or public-upside recapture; do not leave proceeds morally anonymous.
8. **anti-supplantation gate** — if proceeds are promised to repair, require a maintenance-of-effort or clawback rule.
9. **escalation gate** — move from price/disclosure to stronger remedies when harm is non-compensable, exit is unreal, or correction authority is missing.
10. **profile gate** — update `docs/00-meta/remedy-profiles.json` and rerun `tools/audit_remedy_profiles.py`.

## Default settings

| Parameter | Default | Redesign trigger |
|---|---|---|
| remedy profile | one per cube route record | route has `remedy_type` but no default/blocked/escalation statement |
| protected floor | relief before collection or immediate no-rent cure | relief requires a private toll, long delay, or impossible proof |
| proceeds | recipient, route, and anti-supplantation stated | route says public capacity or local repair but money can vanish into the general fund |
| review | appeal/correction authority can change the result | review is decorative, advisory, or locked behind the same failed rail |
| escalation | public option, injunction, no-go, refund reissue, release block, or retirement | the lighter remedy cannot make the affected party whole |

## Anti-pattern definitions

- **remedy theater** — the archive names a remedy word but cannot say who receives what, by when, through which channel, and with what contest right.
- **relief through the same failed rail** — a taxpayer, worker, tenant, ratepayer, or claimant must use the bottleneck that caused the injury to obtain relief.
- **proceeds laundering** — a charge justified as repair, affordability, resilience, or local benefit becomes general revenue without an anti-supplantation rule.
- **escalation blindness** — the design keeps offering price, disclosure, or waiver after exit, contest, or make-whole repair has failed.
- **label-recipient mismatch** — the legal remitter gets the remedy while the real burden bearer absorbs cost, delay, or risk.

## Machine checkpoint

Every route record must have one remedy profile. The profile must name a remedy family, default move, blocked move, guardrails, escalation trigger, and proceeds-integrity posture. Routes with `proceeds_claims` must expose those claims in the remedy profile, and routes with source-currentness refs must link remedy review to currentness review.

## Accountability capsule

Authoritative assignment: route `remedy_traceability_incidence_escalation_proceeds_integrity` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `remedy_owner_revenue_agency_or_appellate_body_controlling_incidence_remedy_proceeds_and_escalation`.
- Rent/benefit trace: `failed_rail_operator_collecting_body_or_fund_manager_using_remedy_theater_proceeds_laundering_or_escalation_delay`.
- Bottleneck/evidence: `remedy_profile; appeals_queue +3 more`; evidence starts with `incidence_target_and_actual_recipient_record; remedy_channel_failure_reissue_and_accessibility_record +2 more`.
- Fallback duty: `public_body_must_preserve alternate_remedy_channel_refund_reissue_independent_review_and proceeds_ledger_access_with_fallback_channel`.


## Source IDs only

[S21][S27][S117][S118][S141][S196]

[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S117]: ../../SOURCES.md#S117
[S118]: ../../SOURCES.md#S118
[S141]: ../../SOURCES.md#S141
[S196]: ../../SOURCES.md#S196
