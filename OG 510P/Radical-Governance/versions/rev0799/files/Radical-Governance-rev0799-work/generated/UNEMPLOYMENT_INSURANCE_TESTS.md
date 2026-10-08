# Unemployment-insurance integrity and access tests matrix

Generated for `rev0799` from `metadata/unemployment_insurance_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `UI-01` Claim-state split | Does the record separate monetary eligibility, separation issue, continuing eligibility, identity status, certification, fraud suspicion, payment state, overpayment, waiver, and appeal state? | `404`, `894`, `913`, `914` | Create a claim-state map before scoring a claim as paid, denied, fraudulent, or overpaid. |
| `UI-02` Identity proofing route preservation | Can failed, pending, inconclusive, digital, in-person, and non-digital identity routes be distinguished, and does each preserve claim date, certification, appeal, and payment if eligible? | `901`, `913`, `914` | Add identity-route ledger and preserve entitlement action outside the credential provider. |
| `UI-03` Payment hold reason and cure clock | Does every payment hold identify the specific unresolved issue, evidence reviewed, missing proof, notice, cure route, clock, and appeal path? | `815`, `821`, `897`, `913`, `914` | Replace generic pending / hold status with payment-hold reason, cure, and release ledger. |
| `UI-04` Fraud-signal and false-positive telemetry | Are fraud signals, confidence, referrals, confirmed fraud, cleared flags, false positives, delay, abandonment, and eventual payment outcomes measured together? | `824`, `913`, `914` | Pair stopped-dollar metrics with valid-claimant harm and false-positive telemetry. |
| `UI-05` Employer / separation issue routing | Does the system distinguish claimant eligibility problems from employer nonresponse, separation disputes, wage-record issues, and adjudication delays? | `813`, `815`, `913`, `914` | Add employer / wage / separation issue states before treating delay as claimant ineligibility or fraud. |
| `UI-06` Overpayment classification and waiver | Can overpayments be split into fraudulent, nonfraudulent, agency-caused, claimant-caused, employer-caused, identity-theft-related, appeal-pending, waived, recovered, and outstanding states? | `814`, `821`, `897`, `913`, `914` | Do not collect or report recovery totals until fraud, nonfraud, waiver, appeal, and identity-theft states are separated. |
| `UI-07` Appeal and retroactive-payment receipt | Are redetermination, hearing, appeal, reversal, waiver, late cure, and retroactive payment outcomes treated as delivery metrics? | `404`, `821`, `913`, `914` | Add appeal and retroactive-payment receipts to the UI performance surface. |
| `UI-08` Identity-theft victim remediation | Can identity-theft victims report misuse, stop recovery, correct tax / benefit records, and preserve their own eligibility without navigating the original fraudster's claim file? | `901`, `913`, `914` | Create an identity-theft victim repair lane separate from ordinary claimant debt collection. |
| `UI-09` State IT performance and modernization evidence | Are modernization grants, pilots, standards, open-source components, and identity services tied to measured state IT performance and claimant outcomes? | `823`, `913`, `914` | Treat modernization artifacts as scaffolding until state performance and claimant outcomes are measured. |
| `UI-10` Paired integrity and access public metrics | Does public reporting pair improper-payment, fraud, recovery, and prosecution evidence with timeliness, hold reasons, access channels, appeal outcomes, false positives, and claimant-group burden? | `816`, `817`, `913`, `914` | Publish paired integrity / access metrics before claiming UI repair. |
| `UI-11` Claimant burden and non-user denominator | Does the packet measure claimant burden, abandonment, assisted-digital sufficiency, non-digital access, subgroup experience, and people who never reached the formal claim or survey surface? | `404`, `426`, `857`, `894`, `913`, `914`, `983`, `984` | Do not treat claim counts, portal completion, post-transaction surveys, or call-center dashboards as claimant access proof until non-user and burden denominators are explicit. |
| `UI-12` Remedy-completion and retroactive-payment receipt | When a valid claimant is delayed, held, denied, overpaid, identity-blocked, appealed, or waived, can the packet show completed repair rather than only remedy availability? | `404`, `719`, `720`, `821`, `857`, `894`, `913`, `914`, `983`, `984` | Do not score a waiver form, appeal right, identity-theft route, or release instruction as repair until the claimant-level money/debt/status consequence changed. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `914` | `UI-01`, `UI-02`, `UI-03`, `UI-04`, `UI-05`, `UI-06`, `UI-07`, `UI-08`, `UI-09`, `UI-10`, `UI-11`, `UI-12` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 4 |
| `426` | 1 |
| `719` | 1 |
| `720` | 1 |
| `813` | 1 |
| `814` | 1 |
| `815` | 2 |
| `816` | 1 |
| `817` | 1 |
| `821` | 4 |
| `823` | 1 |
| `824` | 1 |
| `857` | 2 |
| `894` | 3 |
| `897` | 2 |
| `901` | 2 |
| `913` | 12 |
| `914` | 12 |
| `983` | 2 |
| `984` | 2 |

## Use rule

Run unemployment-insurance tests whenever UI claims, pandemic or emergency benefit programs, identity proofing, payment holds, fraud controls, overpayment notices, waivers, appeals, recovery actions, state IT modernization, or public integrity dashboards can determine whether a valid claimant is paid or a fraudulent claim is stopped. Separate claim issue state, identity route, payment reason, fraud signal, overpayment category, waiver, appeal, recovery, and state performance before scoring blocked payment as integrity or paid benefit as success.
