# Staff-copilot tests matrix

Generated for `rev0799` from `metadata/staff_copilot_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `human_review_quality_gate` meaningful human review quality gate | Is human review specific enough to catch false, incomplete, biased, out-of-scope, or overconfident AI outputs before public action? | `844`, `857`, `861`, `874`, `876`, `879` | Treat human review as theater and pause higher-risk use until reviewers have time, source access, authority, and feedback channels. |
| `input_source_lineage` input / source / case-file lineage | Can reviewers reconstruct which documents, letters, policies, scanned images, briefing packs, or case files shaped the output? | `450`, `856`, `857`, `874`, `876`, `879` | Disable public-action use of outputs until source lineage is preserved and reviewable. |
| `model_supplier_change_record` model, supplier, admin, and change record | Can the agency show which model, supplier, hosting route, prompt, retrieval method, and admin-support path shaped output at the time of use? | `859`, `867`, `874`, `876`, `879` | Require change-control and audit records before relying on tool outputs across time or across departments. |
| `output_record_capture` output / draft / field record capture | Are drafts, summaries, extracted fields, labels, reports, edits, final outputs, and model / prompt versions captured when the output reaches official action? | `450`, `856`, `857`, `874`, `879` | Require an output-capture policy before generated text or fields can become official correspondence, case records, reports, or queue triggers. |
| `performance_bias_error_feedback_loop` performance, bias, error, and feedback loop | Do staff corrections, citizen corrections, false positives, false negatives, topic errors, subgroup risks, and incident reports change the system or governance route? | `844`, `857`, `861`, `874`, `876`, `879` | Treat performance claims as incomplete until errors feed into retraining, tuning, process repair, user notice, or suspension. |
| `public_communication_release_gate` public communication release gate | Before AI-shaped text leaves the agency, is there a release gate linking sources, human edits, final wording, and correction route? | `857`, `874`, `876`, `879` | Prevent AI-shaped correspondence or guidance from being sent until source support, QA, and correction routes are documented. |
| `public_owner_and_task_boundary` public owner and task boundary | Can the agency identify the public owner, service owner, task, users, public-action boundary, and prohibited uses for the staff-facing AI system? | `856`, `857`, `859`, `861`, `867`, `874`, `876`, `879` | Freeze expansion or downshift to personal productivity until owner, task, and prohibited-use records are explicit. |
| `queue_priority_service_speed_effect` queue, priority, and service-speed effect | Does the system change allocation, queue, urgency, support routing, response speed, inspection scope, or case readiness before full human review? | `856`, `857`, `861`, `870`, `872`, `874`, `879` | Separate clerical acceleration from public service effect; add queue audits and fallback channels for missed cases. |
| `sensitive_data_privilege_boundary` sensitive-data and privilege boundary | Are official-sensitive material, personal data, vulnerable-person data, legal privilege, safeguarding information, and admin access governed separately from output reliability? | `859`, `867`, `874`, `876`, `879` | Do not treat secure hosting as substantive accuracy proof; add data-boundary and support-access records. |
| `use_case_register_and_scope_gate` use-case register and prohibited-use gate | Does each practical use case have a scope gate rather than relying on one platform-level approval? | `857`, `859`, `861`, `867`, `874`, `879` | Create per-use-case review before allowing outputs to enter public records, correspondence, reports, queues, or decisions. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `880` | `human_review_quality_gate`, `model_supplier_change_record`, `public_owner_and_task_boundary`, `sensitive_data_privilege_boundary`, `use_case_register_and_scope_gate` |
| `881` | `human_review_quality_gate`, `input_source_lineage`, `model_supplier_change_record`, `output_record_capture`, `performance_bias_error_feedback_loop`, `public_communication_release_gate`, `public_owner_and_task_boundary` |
| `882` | `human_review_quality_gate`, `input_source_lineage`, `model_supplier_change_record`, `output_record_capture`, `performance_bias_error_feedback_loop`, `queue_priority_service_speed_effect` |
| `883` | `human_review_quality_gate`, `input_source_lineage`, `model_supplier_change_record`, `output_record_capture`, `performance_bias_error_feedback_loop`, `queue_priority_service_speed_effect`, `sensitive_data_privilege_boundary` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `450` | 2 |
| `844` | 2 |
| `856` | 4 |
| `857` | 8 |
| `859` | 4 |
| `861` | 5 |
| `867` | 4 |
| `870` | 1 |
| `872` | 1 |
| `874` | 10 |
| `876` | 7 |
| `879` | 10 |

## Use rule

Run staff-copilot tests whenever an internal AI tool used by officials drafts, summarizes, classifies, routes, creates case records, flags vulnerability, prepopulates fields, writes report sections, or otherwise shapes public action without speaking directly to the public. Separate personal productivity from official record creation, record creation from queue or priority effect, and staff assistance from legal or similarly significant decisions.
