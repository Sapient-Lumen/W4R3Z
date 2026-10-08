# Entitlement-continuity tests matrix

Generated for `rev0799` from `metadata/entitlement_continuity_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `assisted_route_and_vulnerability_trigger` assisted route and vulnerability trigger | Do disability, illness, age, language, homelessness, digital exclusion, appointee, representative, child, or other vulnerability flags trigger concrete pre-loss assistance? | `426`, `817`, `879`, `894` | Treat vulnerability language as theater unless it changes contact, deadline, support, review, or closure rules before harm. |
| `cross_program_transition_and_third_party_reliance` cross-program transition and third-party reliance | Do downstream actors and adjacent programs receive reliable status / transition signals so that coverage, rent, work, services, and care do not fail at the boundary? | `819`, `884`, `887`, `889`, `894` | Treat referrals or data transfers as unproven until actual enrollment, service access, payment, or recognized status is shown. |
| `ex_parte_or_auto_renewal_first` ex parte / automatic renewal first | Did the authority use reliable available information to renew, carry forward, or transfer the person before demanding a form, portal action, account creation, or new claim? | `815`, `818`, `857`, `874`, `894` | Do not impose avoidable paperwork burden where reliable data already establish continuing eligibility or continuity. |
| `learning_loop_and_pause_authority` learning loop and pause authority | Can the authority pause closures, change notices, extend deadlines, adjust data rules, restore cases, or carry successful temporary flexibilities into ordinary operations? | `420`, `422`, `857`, `861`, `884`, `894` | Keep the packet open when process defects recur without a pause, repair, or long-term improvement pathway. |
| `legal_status_vs_admin_status` legal status vs administrative status | Does the record separate substantive eligibility or entitlement from administrative states such as pending, renewed, closed, not claimed, procedurally terminated, appealed, reinstated, or migrated? | `857`, `861`, `874`, `887`, `894` | Quarantine closure or loss until confirmed ineligibility is separated from nonresponse, missing paperwork, account failure, deadline failure, pending disposition, or late claim. |
| `metric_denominator_and_pending_truth` metric denominator and pending truth | Do statistics distinguish people, households, notices, renewals due, claims made, pending cases, updated dispositions, procedural closures, confirmed ineligibility, and late outcomes? | `818`, `857`, `894` | Do not use headline claim, renewal, or closure rates without denominator, pending, and late-outcome truth. |
| `notice_reach_and_comprehension` notice reach and comprehension | Did the notice reach the correct person or representative in accessible language and format, explain consequences, and include usable ways to act before loss? | `424`, `426`, `817`, `818`, `879`, `894` | Do not score nonresponse as choice until notice reach, comprehension, and representative routing are proven. |
| `payment_or_coverage_continuity` payment / coverage continuity | Does the migration or renewal preserve medicine, care, rent, food, income, premium, transport, or other real-world continuity across the administrative boundary? | `814`, `817`, `884`, `887`, `894` | Do not call a migration or renewal clean while payment, health coverage, medication, housing, or food support gaps remain unmeasured. |
| `procedural_loss_quarantine` procedural loss quarantine | Are procedural closures kept visibly separate from confirmed ineligibility and from voluntary opt-out? | `857`, `861`, `874`, `884`, `894` | Do not use procedural loss as proof of program-integrity success, fiscal repair, or reduced need. |
| `review_reinstatement_and_good_cause` review, reinstatement, and good cause | Can people contest, reopen, extend, reinstate, or recover benefits / coverage when process failure rather than ineligibility caused loss? | `425`, `816`, `821`, `861`, `894` | Provide remedy before treating closure as final where proof of ineligibility is missing or notice / assistance was defective. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `895` | `assisted_route_and_vulnerability_trigger`, `cross_program_transition_and_third_party_reliance`, `ex_parte_or_auto_renewal_first`, `learning_loop_and_pause_authority`, `legal_status_vs_admin_status`, `metric_denominator_and_pending_truth`, `notice_reach_and_comprehension`, `payment_or_coverage_continuity`, `procedural_loss_quarantine`, `review_reinstatement_and_good_cause` |
| `896` | `assisted_route_and_vulnerability_trigger`, `cross_program_transition_and_third_party_reliance`, `learning_loop_and_pause_authority`, `legal_status_vs_admin_status`, `metric_denominator_and_pending_truth`, `notice_reach_and_comprehension`, `payment_or_coverage_continuity`, `procedural_loss_quarantine`, `review_reinstatement_and_good_cause` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `420` | 1 |
| `422` | 1 |
| `424` | 1 |
| `425` | 1 |
| `426` | 2 |
| `814` | 1 |
| `815` | 1 |
| `816` | 1 |
| `817` | 3 |
| `818` | 3 |
| `819` | 1 |
| `821` | 1 |
| `857` | 5 |
| `861` | 4 |
| `874` | 3 |
| `879` | 2 |
| `884` | 4 |
| `887` | 3 |
| `889` | 1 |
| `894` | 10 |

## Use rule

Run entitlement-continuity tests whenever an existing public benefit, health coverage, income support, tax credit, status proof, housing support, disability-linked support, or service entitlement is renewed, redetermined, migrated, converted, closed, procedurally terminated, deadline-gated, or moved into a new proof / account / portal / claim route. Separate legal eligibility from administrative completion, and require notice, assistance, continuity, review, metric, and remedy proof before scoring loss as clean.
