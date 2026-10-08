# Transition-receipt tests matrix

Generated for `rev0799` from `metadata/transition_receipt_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `affected_user_and_remedy_tail` affected-user and remedy tail | Can the authority identify who used, relied on, was excluded by, delayed by, misinformed by, or harmed by the old system and what notice, correction, refund, complaint, or remedy tail remains? | `817`, `821`, `857`, `874`, `876`, `884` | Keep the transition open until affected-user and remedy tails are either served or explicitly justified as unavailable. |
| `cost_benefit_separation` cost and benefit separation | Are final cost, residual cost, successor budget, benefit claims, and emergency / pilot-period expenses separated so that current utility does not launder prior management failure? | `814`, `857`, `861`, `867`, `884` | Do not use successor performance claims as proof that the original build, procurement, or emergency period delivered value for money. |
| `data_closeout_and_purpose_separation` data closeout and purpose separation | Does the transition show what personal, operational, health, customs, model, profile, or case data was migrated, deleted, corrected, retained, or repurposed? | `818`, `856`, `857`, `859`, `867`, `875`, `884` | Pause successor use of data until emergency, pilot, and ordinary-service purposes are separated and documented. |
| `incident_defect_lessons_ledger` incident / defect / lessons ledger | Does the transition preserve and classify defects, incidents, false guidance, wrong instructions, outage, bias, accessibility, security, testing, or release failures and assign them to future gates? | `816`, `857`, `876`, `879`, `884` | Treat closure as incomplete until incidents are translated into reusable launch, testing, monitoring, and escalation gates. |
| `procurement_contract_closeout` procurement and contract closeout | Can the authority close or continue supplier relationships with traceable contracts, amendments, task authorizations, invoices, deliverables, subcontract roles, service levels, warranties, and exit obligations? | `823`, `856`, `859`, `867`, `884` | Separate supplier closeout from product closeout; preserve contract evidence and test residual dependency before renewal or conversion. |
| `record_preservation_and_audit_tail` record preservation and audit tail | Are logs, versions, prompts, decisions, contracts, invoices, task authorizations, defect reports, meeting records, and audit evidence preserved long enough for oversight, complaints, litigation, and future design? | `818`, `816`, `857`, `867`, `876`, `879`, `884` | Do not decommission or migrate in a way that destroys the evidence needed to assess the old system. |
| `relaunch_expansion_gate` relaunch / renewal / expansion gate | What evidence is required before the same function returns, expands, renews, or is embedded in a successor platform or department? | `820`, `857`, `861`, `867`, `876`, `879`, `884` | No relaunch, renewal, or successor expansion until the closure record’s failure lessons are converted into entry gates. |
| `residual_dependency_and_operating_risk` residual dependency and operating risk | After the transition, what supplier, cloud, data, staffing, maintenance, security, model, dashboard, or operational dependency remains? | `856`, `859`, `867`, `884` | Refuse transition closure when the visible tool ends but the hidden waist or supplier dependency persists unmanaged. |
| `successor_function_map` successor function map | Does the receipt show what function moved, vanished, stayed, or changed owner rather than relying on a rename, redirect, or modernization label? | `856`, `860`, `861`, `870`, `871`, `884` | Publish a successor map before claiming repair, modernization, reorganization, or closure. |
| `terminal_event_and_status` terminal event and status | Can the public authority identify what ended, paused, converted, migrated, became optional, or survived, with date, decision-maker, and legal / administrative status? | `857`, `861`, `868`, `870`, `876`, `879`, `884` | Do not mark the transition complete until the terminal event and surviving functions are explicitly mapped. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `885` | `affected_user_and_remedy_tail`, `cost_benefit_separation`, `data_closeout_and_purpose_separation`, `incident_defect_lessons_ledger`, `procurement_contract_closeout`, `record_preservation_and_audit_tail`, `relaunch_expansion_gate`, `residual_dependency_and_operating_risk`, `successor_function_map`, `terminal_event_and_status` |
| `886` | `affected_user_and_remedy_tail`, `incident_defect_lessons_ledger`, `record_preservation_and_audit_tail`, `relaunch_expansion_gate`, `successor_function_map`, `terminal_event_and_status` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `814` | 1 |
| `816` | 2 |
| `817` | 1 |
| `818` | 2 |
| `820` | 1 |
| `821` | 1 |
| `823` | 1 |
| `856` | 4 |
| `857` | 7 |
| `859` | 3 |
| `860` | 1 |
| `861` | 4 |
| `867` | 6 |
| `868` | 1 |
| `870` | 2 |
| `871` | 1 |
| `874` | 1 |
| `875` | 1 |
| `876` | 5 |
| `879` | 4 |
| `884` | 10 |

## Use rule

Run transition-receipt tests whenever a public tool, platform, pilot, authority, supplier arrangement, emergency measure, database, AI system, or coordination body is ended, converted, absorbed, migrated, paused, made optional, relaunched, renewed, or replaced. Separate terminal status from successor ownership, defect learning, affected-user tail, record preservation, data closeout, procurement / contract closeout, costs, residual dependency, and relaunch gates.
