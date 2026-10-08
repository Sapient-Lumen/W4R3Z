# Credential-access tests matrix

Generated for `rev0799` from `metadata/credential_access_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `account_recovery_and_attribute_correction` account recovery and attribute correction | Can users recover accounts and correct identity attributes before public-service harm occurs? | `815`, `818`, `901` | Treat unrecoverable accounts and wrong attributes as access incidents, not user inconvenience. |
| `assurance_level_fit` assurance-level fit | Does the chosen proofing, authentication, and federation level match the transaction risk rather than platform convenience? | `406`, `901` | Right-size assurance before launch or expansion; do not force over-proofing or under-proofing by default. |
| `delegated_authority_route` delegated-authority route | Can representatives act through explicit, scoped, revocable mandates instead of sharing credentials? | `406`, `901` | Add representation routes before forcing account fusion or password sharing. |
| `outage_fallback_deadline_protection` outage, fallback, and deadline protection | Are maintenance, incident, proofing outage, return-link, and account-lock failures connected to service-specific fallback and deadline protection? | `422`, `884`, `901` | Do not score status transparency as sufficient without affected-user and deadline receipts. |
| `privacy_biometric_supplier_boundary` privacy, biometric, and supplier boundary | Are biometric, document, device, third-party, and retention boundaries public enough to audit and contest? | `856`, `859`, `867`, `901` | Do not treat security as a sufficient privacy answer; require public-owner and supplier boundaries. |
| `proofing_route_inclusion` proofing route inclusion | Do users have realistic remote, in-person, assisted, non-biometric, language, disability, overseas, and document-light routes? | `815`, `817`, `901` | Do not credit route availability without performance and exclusion evidence. |
| `public_metrics_and_learning` public metrics and learning | Are proofing success, abandonment, recovery, lockout, complaints, exclusion, incident, and appeal patterns published enough to drive repair? | `419`, `857`, `901` | Do not treat a credential programme as mature without operational learning evidence. |
| `relying_party_owner_boundary` relying-party owner boundary | Does each service owner remain responsible for its service consequence even when a shared identity provider handles proofing? | `813`, `901` | Do not let departments or agencies outsource public-law duties to the identity provider. |
| `service_action_consequence` service action and consequence | What public action is behind the credential gate, and what harm follows if access fails? | `901`, `887`, `894`, `897` | Do not classify the system as ordinary login until every gated action is consequence-classed. |
| `standards_reapproval_clock` standards reapproval clock | Are standards, certification, assurance claims, and proofing configurations reapproved after material change? | `417`, `820`, `901` | Do not rely on stale assurance claims; require dated and scoped reapproval. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `902` | `assurance_level_fit`, `privacy_biometric_supplier_boundary`, `proofing_route_inclusion`, `public_metrics_and_learning`, `relying_party_owner_boundary`, `standards_reapproval_clock` |
| `903` | `account_recovery_and_attribute_correction`, `delegated_authority_route`, `privacy_biometric_supplier_boundary`, `proofing_route_inclusion`, `public_metrics_and_learning`, `service_action_consequence` |
| `904` | `account_recovery_and_attribute_correction`, `assurance_level_fit`, `delegated_authority_route`, `outage_fallback_deadline_protection`, `privacy_biometric_supplier_boundary`, `proofing_route_inclusion`, `public_metrics_and_learning`, `relying_party_owner_boundary`, `service_action_consequence` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `406` | 2 |
| `417` | 1 |
| `419` | 1 |
| `422` | 1 |
| `813` | 1 |
| `815` | 2 |
| `817` | 1 |
| `818` | 1 |
| `820` | 1 |
| `856` | 1 |
| `857` | 1 |
| `859` | 1 |
| `867` | 1 |
| `884` | 1 |
| `887` | 1 |
| `894` | 1 |
| `897` | 1 |
| `901` | 10 |

## Use rule

Run credential-access tests whenever a public login, account, identity-proofing route, federation layer, passkey, wallet, delegated mandate, biometric check, or shared identity provider becomes a practical gate to a public service, entitlement, payment, notice, status proof, authorisation, filing, deadline, or representative action. Separate person, credential, account, session, mandate, entitlement, fallback, and service-owner duties before scoring access or denial.
