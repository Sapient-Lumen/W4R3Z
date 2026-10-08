# Platform-migration tests matrix

Generated for `rev0799` from `metadata/platform_migration_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `affected_user_continuity_and_assistance` affected-user continuity and assistance | Can affected people continue to receive pay, prove rights, access service, correct records, get assistance, and avoid harm while migration is in progress? | `817`, `821`, `861`, `884`, `887` | Preserve legacy or manual routes and add remedy stays where migration can cause practical loss before correction is possible. |
| `backlog_error_and_remedy_tail` backlog, error, and remedy tail | What unresolved old-system errors, backlogs, claims, appeals, compensation duties, overpayments, underpayments, proof failures, or complaints remain at migration? | `821`, `857`, `861`, `884`, `887` | Refuse replacement-as-repair where old-system errors are copied into the successor as settled truth or vanish from remedy channels. |
| `contract_supplier_exit_ledger` contract, supplier, and exit ledger | Are old and new suppliers, licences, customizations, support duties, warranties, admin access, data export, escrow, portability, and termination obligations visible? | `823`, `856`, `859`, `867`, `887` | Do not treat reprocurement as exit if old dependencies, new lock-in, custom extensions, support duties, or data-portability gaps remain unmanaged. |
| `data_identity_entitlement_mapping` data / identity / entitlement mapping | Are persons, accounts, identifiers, permissions, pay states, statuses, entitlements, records, and obligations mapped with validation, correction, and dispute status? | `818`, `821`, `857`, `887` | Quarantine uncertain records and preserve native evidence before migrated data becomes authoritative new state. |
| `interface_dependency_and_checker_map` interface, dependency, and checker map | Are upstream systems, downstream systems, staff consoles, APIs, third-party checkers, carriers, banks, departments, reports, and paper routes mapped and tested? | `819`, `856`, `859`, `887` | Do not migrate where downstream systems or checkers can make the public function fail while the central platform claims success. |
| `legacy_fallback_and_proof_tail` legacy fallback and proof tail | What legacy documents, manual channels, old portals, paper proofs, compensation routes, or evidence tails remain usable while migration defects are corrected? | `818`, `821`, `884`, `887` | Block legacy retirement when affected users may lose practical proof, pay, service, or remedy before the successor is reliable. |
| `old_new_authority_map` old/new authority map | Does the docket identify which functions, records, decisions, notices, rights, workflows, and proof routes remain with the old system, move to the new system, split, or terminate? | `813`, `818`, `884`, `887` | Do not cut over until old and new authority are visibly separated and users / staff know which state controls which function. |
| `parallel_run_reconciliation` parallel-run reconciliation | If old and new systems run in parallel, do records show representative cases, divergence taxonomy, root-cause assignment, correction responsibility, and sign-off thresholds? | `815`, `816`, `818`, `887` | A parallel run without recorded reconciliation is theater; matching a wrong old system is not proof of new-system truth. |
| `post_migration_value_and_harm_audit` post-migration value and harm audit | After live use, are cost, benefit, performance, accuracy, service standards, manual workload, user experience, harms, and complaint rates measured separately from selection and feasibility claims? | `814`, `816`, `857`, `884`, `887` | Do not claim value for money, modernization, or repair until live metrics and harm audits show the successor performs better without hidden affected-user costs. |
| `rule_process_and_configuration_readiness` rule, process, and configuration readiness | Are business rules, legal rules, process changes, configuration, custom extensions, and unsimplified complexity visible before the new platform is treated as ready? | `814`, `815`, `820`, `823`, `887` | Treat customizations and unsimplified rules as residual migration risk, not as neutral technical implementation detail. |
| `wave_cutover_and_rollback_gate` wave, cutover, and rollback gate | Who authorizes each wave or cutover, what evidence gates it, what threshold blocks it, and how can service roll back or pause if the new platform fails? | `820`, `861`, `884`, `887` | Pause cutover or preserve old/fallback routes when readiness thresholds, data quality, user continuity, or incident response are not proven. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `888` | `affected_user_continuity_and_assistance`, `backlog_error_and_remedy_tail`, `contract_supplier_exit_ledger`, `data_identity_entitlement_mapping`, `interface_dependency_and_checker_map`, `legacy_fallback_and_proof_tail`, `old_new_authority_map`, `parallel_run_reconciliation`, `post_migration_value_and_harm_audit`, `rule_process_and_configuration_readiness`, `wave_cutover_and_rollback_gate` |
| `889` | `affected_user_continuity_and_assistance`, `backlog_error_and_remedy_tail`, `data_identity_entitlement_mapping`, `interface_dependency_and_checker_map`, `legacy_fallback_and_proof_tail`, `old_new_authority_map`, `post_migration_value_and_harm_audit`, `wave_cutover_and_rollback_gate` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `813` | 1 |
| `814` | 2 |
| `815` | 2 |
| `816` | 2 |
| `817` | 1 |
| `818` | 4 |
| `819` | 1 |
| `820` | 2 |
| `821` | 4 |
| `823` | 2 |
| `856` | 2 |
| `857` | 3 |
| `859` | 2 |
| `861` | 3 |
| `867` | 1 |
| `884` | 6 |
| `887` | 11 |

## Use rule

Run platform-migration tests whenever a public platform, portal, SaaS tenant, data hub, account system, status-proof service, payroll or case-management system, identity register, or supplier-backed infrastructure is replaced, migrated, reprocured, dual-run, cut over, made digital-only, or retired. Separate selection from feasibility, readiness, cutover, affected-user continuity, legacy fallback, contract exit, residual dependency, and post-migration value.
