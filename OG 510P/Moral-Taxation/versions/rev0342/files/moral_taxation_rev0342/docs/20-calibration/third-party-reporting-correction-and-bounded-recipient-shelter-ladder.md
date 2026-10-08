# Third-party reporting, correction, and bounded recipient-shelter ladder

## Question in one sentence

Given the archive's closed rule that **strong third-party reporters should usually carry the first correction duty for their own reporting errors and weak downstream recipients should get issue-bounded shelter while a material mismatch is live**, **what is the smallest workable ladder for deciding when a recipient only gets no-penalty treatment, when collection or denial must narrow to the disputed field, when the issuer must propagate a correction across affected records, and when repeated bad reporting should harden upstream rather than remaining a downstream cleanup burden?**[S21][S27][S39][S41][S42][S44][S65][S66][S68][S83][S89][S98]

## Companion routes

[`../10-framework/third-party-reporting-correction-and-bounded-recipient-shelter-routing.md`](../10-framework/third-party-reporting-correction-and-bounded-recipient-shelter-routing.md) · [`../10-framework/administration-explanation-and-appeal-routing.md`](../10-framework/administration-explanation-and-appeal-routing.md) · [`../10-framework/record-asymmetry-burden-shifting-and-adverse-inference-routing.md`](../10-framework/record-asymmetry-burden-shifting-and-adverse-inference-routing.md) · [`../10-framework/overcollection-return-setoff-and-refund-symmetry-routing.md`](../10-framework/overcollection-return-setoff-and-refund-symmetry-routing.md) · [`../10-framework/same-facts-reuse-portability-and-delta-update-routing.md`](../10-framework/same-facts-reuse-portability-and-delta-update-routing.md) · [`../10-framework/sanctions-culpability-and-disclosure-routing.md`](../10-framework/sanctions-culpability-and-disclosure-routing.md)

Route: tax systems may rely on strong third-party reporting for legibility and automation, but they should not convert that convenience into downstream irrebuttability. The default should be **issuer-first repair, issue-bounded recipient shelter, propagated correction, and upstream hardening when error becomes repeated or industrialized**.[S21][S27][S39][S41][S42][S44][S65][S66][S68][S83][S89][S98]

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — reporter truth by default | treat payroll feeds, platform ledgers, bank statements, meter reports, and controller-side packets as presumptively decisive unless the recipient can reconstruct the upstream books in detail.[S27][S39][S42][S68][S89] | Reject: turns record concentration into downstream vulnerability and defeats the archive's burden-shifting and parity rules. |
| B — freeze the whole case whenever a statement is contested | stop all collection, all relief, or all period-finality whenever a third-party report is materially disputed.[S39][S41][S42] | Reject: confuses issue-bounded mismatch with case-wide uncertainty and invites administrative paralysis. |
| C — issuer-first correction plus bounded recipient shelter | require the stronger reporter to correct or affirm first, protect the weaker recipient on the disputed slice while that process runs, and propagate accepted fixes where the shared fact recurs.[S21][S27][S39][S41][S42][S65][S66][S68][S83][S89] | Adopt. |
| D — symmetric burden regardless of who controls the record | split proof, cash-flow, and correction burdens equally between issuer and recipient whenever a report is challenged.[S21][S42][S83] | Reject: formal symmetry ignores real record asymmetry and usually shifts cost back onto the weaker side. |

## Five-rung ladder

1. **clerical mismatch lane** — where a duplicate, transposition, obvious attribution error, or already-known correction is visible, annotate or correct the shared record quickly and do not crystallize liability on the disputed field while that clerical repair is pending,[S27][S39][S42][S66][S68]
2. **issuer-first correction lane** — where the recipient makes a concrete counterstatement, require the employer, platform, bank, meter operator, registry custodian, or controller-side signer to affirm or amend first because that actor holds the operative books,[S21][S27][S39][S41][S42][S65][S66][S83][S89]
3. **issue-bounded shelter lane** — while a material mismatch remains genuinely live, narrow collection, denial, offset, or sanction to the contested field or amount rather than treating the full period or packet as settled against the recipient,[S39][S41][S42][S65][S66][S83]
4. **propagated correction lane** — once the reporter-side fix is accepted, reuse it across affected periods, downstream forms, or linked systems instead of forcing each recipient to relitigate the same shared fact one channel at a time,[S27][S42][S68][S89]
5. **upstream hardening lane** — when false, stale, duplicated, or selectively incomplete reporting becomes repeated or industrialized, escalate to mandatory process repair, audit focus, stronger certification or attestation duties, and sanctions on the reporting layer rather than leaving the burden on weak recipients,[S27][S39][S41][S42][S44][S68][S89][S98]

## Provisional recommendation

Adopt **Option C — issuer-first correction plus bounded recipient shelter** as the archive's default calibration for disputed third-party reports.[S21][S27][S39][S41][S42][S65][S66][S68][S83][S89]

Presumption:

- require a **narrow recipient counterstatement**, not a reconstruction of the whole upstream ledger,
- put the first real repair burden on the **issuer or strongest common record-holder**,
- let the clear remainder of the period or packet proceed while keeping the **disputed slice protected**,
- propagate accepted fixes by **reuse and delta update** instead of repeated downstream refiling,
- and harden mainly against **bad-reporting systems**, not only against recipients caught inside them.

That is the narrowest workable setting because it preserves the efficiency gains of third-party reporting without turning those gains into an unreviewable extraction device.

For AI-era administration, this matters anywhere controller-side packets, deployment ledgers, hosted-use meters, or platform activity feeds are reused for tax routing. If such packets are going to serve as shared tax facts, the archive should prefer signer-side correction, narrow provisional reallocation, and propagated packet repair over downstream user-side cleanup or blanket suspension.[S16][S17][S20][S27][S39][S41][S42][S44][S68][S89]

## Default context table

| Context | Default rung | Why this usually fits | Archive warning |
|---|---|---|---|
| wages, pensions, and withholding statements | issuer-first correction lane with issue-bounded shelter | employers and payers usually hold the operative payroll books and correction channels.[S21][S27][S39][S41][S65][S66][S83] | do not make the worker disprove the whole payroll system before a disputed field is sheltered. |
| platforms, marketplaces, and gross-proceeds reports | issuer-first correction, then propagated correction where the same feed populates multiple forms or dashboards | platform-side activity records are concentrated and often reused downstream.[S27][S39][S42][S68][S89] | do not let dashboard visibility masquerade as recipient control over the underlying ledger. |
| banks, payment processors, and account-linked statements | clerical-mismatch or issuer-first correction lane, with only narrow holds where identity or attribution is live | the institution usually controls the shared record and can annotate duplicates or wrong-account attributions fastest.[S27][S39][S41][S42][S68] | do not freeze the full refund or period because one attributed transaction is contested. |
| utilities, facility operators, congestion meters, or local-burden records | issue-bounded shelter plus operator-side re-check before final recovery | meters and allocation methods sit upstream with the operator rather than with households or small firms.[S39][S41][S42][S79][S83] | do not convert industrial measurement uncertainty into a forced cash-flow loan from weaker payers. |
| controller-side AI packets, registry filings, or usage feeds | issuer-first correction and propagated packet repair, escalating to upstream hardening if stale or false packets recur | packet signers and controller groups are best placed to repair shared machine-facing tax facts.[S16][S17][S20][S27][S39][S41][S42][S44][S89] | do not let packet convenience make a stale controller-side field function as final liability for weaker downstream actors. |

## Failure-mode capsule

Cube axes: anti-pattern `label_recipient_mismatch`, `record_lock_in`, `liability_misassignment`; burden mechanic `third_party_record_lock_in`, `legal_risk_transfer`. Keep route-specific exceptions in the ladder; do not rebuild a local taxonomy.

## Recalibration trigger capsule

Cube review triggers: `record_or_measurement_staleness`. Reopen only when the trigger changes incidence, proof, remedy, floor, or fallback-rail design.

## Accountability capsule

Profile route `third_party_reporting_correction_and_bounded_recipient_shelter` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json); the profile is authoritative for owner, benefit, evidence, fallback, and anti-misattribution.

## Source IDs only

[S16][S17][S20][S21][S27][S39][S41][S42][S44][S65][S66][S68][S79][S83][S89][S98]

[S16]: ../../SOURCES.md#S16
[S17]: ../../SOURCES.md#S17
[S20]: ../../SOURCES.md#S20
[S21]: ../../SOURCES.md#S21
[S27]: ../../SOURCES.md#S27
[S39]: ../../SOURCES.md#S39
[S41]: ../../SOURCES.md#S41
[S42]: ../../SOURCES.md#S42
[S44]: ../../SOURCES.md#S44
[S65]: ../../SOURCES.md#S65
[S66]: ../../SOURCES.md#S66
[S68]: ../../SOURCES.md#S68
[S79]: ../../SOURCES.md#S79
[S83]: ../../SOURCES.md#S83
[S89]: ../../SOURCES.md#S89
[S98]: ../../SOURCES.md#S98
