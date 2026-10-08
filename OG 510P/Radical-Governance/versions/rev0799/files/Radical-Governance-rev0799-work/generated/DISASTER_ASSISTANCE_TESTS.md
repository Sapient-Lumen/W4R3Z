# Disaster-assistance tests matrix

Generated for `rev0799` from `metadata/disaster_assistance_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `DA-01` Declaration / household split | Does the record separate disaster declaration scope from household eligibility and assistance-category state? | `813`, `815`, `911`, `912` | Create a declaration-scope and household-status map before counting approval or denial. |
| `DA-02` Survivor proof ladder | Can identity, occupancy, ownership, disaster-causation, and loss category be cured through an ordered proof ladder? | `817`, `818`, `911`, `912` | Publish a proof ladder with substitute documents and assisted cure routes before treating missing proof as ineligibility. |
| `DA-03` Denial reason and cure packet | Does every denial or partial award identify evidence reviewed, evidence missing, substitute proof, appeal clock, and assisted route? | `404`, `821`, `911`, `912` | Replace status-only letters with denial/cure packets. |
| `DA-04` Appeal packet and clock | Are appeal receipt, evidence, clock, reinspection, outcome, overturn, and finality tracked as delivery evidence? | `404`, `816`, `821`, `911`, `912` | Add an appeal packet ledger and count appeal outcomes before scoring delivery. |
| `DA-05` Insurance and duplication separation | Does the system distinguish actual insurance payment, pending insurance, denied insurance, loan offer, charity aid, duplicate benefit, and remaining unmet need? | `814`, `818`, `897`, `911`, `912` | Build an insurance / duplication ledger before withholding or recouping aid. |
| `DA-06` Program-handoff receipt | When a survivor is sent to SBA, HUD, state, tribal, local, insurer, or nonprofit support, does the packet, deadline, and status travel? | `819`, `887`, `911`, `912` | Require handoff receipts instead of treating referrals as delivery. |
| `DA-07` Assisted and accessible route | Do language, disability, rural access, digital access, displacement, homelessness, heir-property, and representative-help constraints have measured routes? | `426`, `817`, `901`, `905`, `911`, `912` | Add assisted access and subgroup telemetry before relying on aggregate approval rates. |
| `DA-08` Fraud-control harm telemetry | Do identity, duplication, damage, and fraud screens report false-positive, delay, appeal-overturn, and valid-survivor burden? | `816`, `824`, `911`, `912` | Add survivor-harm telemetry to fraud controls before claiming integrity success. |
| `DA-09` Payment receipt and recovery outcome | Are obligation, award, issuance, receipt, use category, recoupment, and remaining recovery need separated? | `814`, `897`, `911`, `912` | Separate payment-state and recovery-outcome records before counting aid as recovery. |
| `DA-10` Fragmentation and capacity reporting | Do public reports show program fragmentation, workforce / contractor capacity, call-center performance, inspection delay, and dashboard limitations? | `815`, `816`, `818`, `910`, `911`, `912` | Add capacity and fragmentation disclosure before using national totals as a performance claim. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `912` | `DA-01`, `DA-02`, `DA-03`, `DA-04`, `DA-05`, `DA-06`, `DA-07`, `DA-08`, `DA-09`, `DA-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 2 |
| `426` | 1 |
| `813` | 1 |
| `814` | 2 |
| `815` | 2 |
| `816` | 3 |
| `817` | 2 |
| `818` | 3 |
| `819` | 1 |
| `821` | 2 |
| `824` | 1 |
| `887` | 1 |
| `897` | 2 |
| `901` | 1 |
| `905` | 1 |
| `910` | 1 |
| `911` | 10 |
| `912` | 10 |

## Use rule

Run disaster-assistance tests whenever a declared incident, emergency relief route, individual-assistance programme, household proof problem, insurance / duplication review, fraud screen, appeal, inter-program referral, recovery payment, or long-term recovery handoff can affect whether a survivor actually receives safe shelter, essential needs, repair support, or remaining-need help. Separate declaration, household eligibility, proof state, denial reason, appeal clock, handoff receipt, payment receipt, fraud-control harm, and recovery outcome before scoring aid as delivered or a case as closed.
