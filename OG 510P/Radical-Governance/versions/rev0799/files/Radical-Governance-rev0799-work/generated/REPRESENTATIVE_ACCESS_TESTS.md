# Representative-access tests matrix

Generated for `rev0799` from `metadata/representative_access_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `appeal_and_health_information_boundary` appeal and health-information boundary | When representation touches appeals or health information, are PHI, evidence submission, hearings, expedited routes, and direct appeal rights protected? | `821`, `894`, `905` | Do not let privacy or form defects defeat appeal substance; require cure and direct-rights protections. |
| `authority_type_and_scope` authority type and scope | What kind of representative authority is claimed, and which actions, data, payments, periods, services, and decisions does it cover? | `406`, `901`, `905` | Do not accept representative action until the authority lane and scope are explicit. |
| `capacity_consent_and_wishes` capacity, consent, and wishes | Is the route based on the person’s consent, inability to act, court / legal authority, programme appointment, or support need, and are wishes and feelings preserved where possible? | `817`, `894`, `905` | Use support instead of substitution where possible and do not let capacity labels exceed the specific need. |
| `conflict_misuse_and_professional_integrity` conflict, misuse, and professional integrity | Are conflicts, misuse, professional eligibility, disqualification, fees, and unsuitable representatives visible and actionable? | `816`, `897`, `905` | Do not rely on relationship or professional status without integrity and misuse controls. |
| `cross_system_migration_and_portability` cross-system migration and portability | Do appointee, payee, POA, guardian, tax, appeal, and professional-authorisation records survive platform, programme, legal-system, or jurisdiction migration? | `884`, `887`, `901`, `905` | Do not migrate claims, accounts, or platforms until mandate records are mapped and reviewed. |
| `identity_credential_separation` identity, credential, and mandate separation | Are the representative’s identity and credential separated from the principal’s account, entitlement, and mandate? | `406`, `901`, `905` | Create a delegated route rather than requiring the principal to share credentials or codes. |
| `notice_and_deadline_routing` notice and deadline routing | Who receives notices, electronic messages, appeal documents, confirmations, and deadlines, and how is the principal protected if routing fails? | `894`, `901`, `905` | Do not let representative notice routing consume direct rights without receipt and cure safeguards. |
| `payment_fiduciary_control` payment fiduciary control | If the representative receives or controls money, does the record show beneficiary ownership, spending rule, accounting, conserved funds, misuse route, and restitution? | `897`, `905` | Do not count payment to a representative as support delivered without fiduciary records. |
| `public_metrics_and_learning` representative-access metrics and learning | Are failures, account-sharing workarounds, payment misuse, notice failures, revocations, restored direct payments, and appeal-form defects measured enough to repair the route? | `419`, `857`, `905` | Do not classify the route as mature without operational learning and repair evidence. |
| `revocation_withdrawal_and_restoration` revocation, withdrawal, and restoration | Can the principal revoke, the representative withdraw, the public body remove, or direct action resume without service interruption? | `884`, `887`, `905` | Add end-state and transition controls before treating representation as safe. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `906` | `authority_type_and_scope`, `capacity_consent_and_wishes`, `conflict_misuse_and_professional_integrity`, `payment_fiduciary_control`, `public_metrics_and_learning`, `revocation_withdrawal_and_restoration` |
| `907` | `authority_type_and_scope`, `capacity_consent_and_wishes`, `cross_system_migration_and_portability`, `identity_credential_separation`, `notice_and_deadline_routing`, `payment_fiduciary_control`, `public_metrics_and_learning`, `revocation_withdrawal_and_restoration` |
| `908` | `authority_type_and_scope`, `conflict_misuse_and_professional_integrity`, `cross_system_migration_and_portability`, `identity_credential_separation`, `notice_and_deadline_routing`, `public_metrics_and_learning`, `revocation_withdrawal_and_restoration` |
| `909` | `appeal_and_health_information_boundary`, `authority_type_and_scope`, `conflict_misuse_and_professional_integrity`, `notice_and_deadline_routing`, `public_metrics_and_learning`, `revocation_withdrawal_and_restoration` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `406` | 2 |
| `419` | 1 |
| `816` | 1 |
| `817` | 1 |
| `821` | 1 |
| `857` | 1 |
| `884` | 2 |
| `887` | 2 |
| `894` | 3 |
| `897` | 2 |
| `901` | 4 |
| `905` | 10 |

## Use rule

Run representative-access tests whenever a payee, appointee, guardian, attorney-in-fact, tax representative, professional authorisation, appeal representative, helper, caregiver, organisation, delegated account user, or informal proxy can receive notices, control money, submit claims, access records, bind filings, preserve deadlines, or speak for a person. Separate person, credential, authority, scope, capacity, wishes, revocation, fiduciary duty, payment control, and public-service outcome before accepting proxy action or denial.
