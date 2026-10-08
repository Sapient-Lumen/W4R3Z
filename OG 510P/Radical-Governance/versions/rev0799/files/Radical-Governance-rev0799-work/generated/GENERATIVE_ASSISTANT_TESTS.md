# Generative-assistant tests matrix

Generated for `rev0799` from `metadata/generative_assistant_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `accessibility_language_robustness` Accessibility and language robustness test | Does the assistant work for users with disabilities, low literacy, limited English, mobile-only access, and complex service needs without turning conversational access into misleading simplification? | `424`, `425`, `426`, `817`, `857`, `870`, `876` | Treat the assistant as optional navigation only and preserve assisted channels until subgroup reliability and comprehension are proven. |
| `answer_consistency_hallucination` Answer consistency and hallucination test | Do repeated, ambiguous, adversarial, multilingual, and high-stakes prompts produce accurate, consistent, complete, and appropriately refusing answers? | `816`, `817`, `818`, `856`, `857`, `876` | Pause or narrow the assistant, repair prompts / retrieval / corpus / guardrails, and publish correction and incident records. |
| `canonical_corpus_source_trace` Canonical corpus and source-trace test | Can the agency identify canonical pages, excluded sources, freshness cadence, retrieval trace, answer-source links, and proposition-level source support? | `818`, `856`, `857`, `859`, `876` | Downshift to ordinary search or block the answer class until corpus, source hierarchy, and traceability are reviewable. |
| `feedback_correction_clock` Feedback-to-correction clock | Are user feedback, expert review, bad-answer reports, and source-page changes tied to triage, correction, rollback, and public update clocks? | `816`, `818`, `857`, `861`, `876`, `870` | Do not count feedback as governance; create correction clocks and close the loop before scaling. |
| `human_authoritative_handoff` Human / authoritative handoff test | Can the user leave the assistant for an authoritative source page, official form, human channel, review route, or complaint path before harm? | `817`, `821`, `857`, `861`, `870`, `874`, `876` | Narrow the assistant to navigation and preserve human / official pathways until generated answers cannot trap users in non-authoritative advice. |
| `incident_disclosure_threshold` Incident disclosure threshold | When does a wrong or unsafe answer require public correction, affected-user notice, regulator / auditor notice, or service suspension? | `816`, `817`, `857`, `861`, `874`, `876` | Publish an incident threshold and pause high-stakes deployment until unsafe-answer response is not discretionary public-relations judgment. |
| `public_owner_boundary` Public-owner and boundary test | Does the assistant have a named public owner, accountable service owner, complaint route, and published answer boundary separating search, guidance, triage, compliance instruction, and decision support? | `813`, `815`, `817`, `857`, `860`, `861`, `876` | Do not launch as an official assistant; assign owner, narrow the domain, and publish the boundary before public reliance is invited. |
| `reliance_warning_boundary` Reliance-warning and harm-class boundary | Are warnings, caveats, source-check prompts, and high-stakes escalations matched to the harm class rather than treated as one generic disclaimer? | `817`, `824`, `857`, `861`, `874`, `876` | Narrow topics, add answer-level warnings and source checks, or route high-stakes users to authoritative human / form channels. |
| `supplier_model_change_record` Supplier and model-change record | Can the public authority show model, hosting, retrieval, prompt, guardrail, admin-access, support, data-use, and model-change records? | `856`, `859`, `867`, `876` | Activate supplier-dependency tests and block material expansion until public owner, audit, change, and exit controls exist. |
| `withdrawal_transition_receipt` Withdrawal / transition receipt | If the assistant is paused, retired, replaced, or expanded from beta, is there a public receipt explaining why, what was learned, what users should do, and how successor controls change? | `820`, `857`, `861`, `870`, `876` | Do not let a public assistant disappear or expand without a record; publish the transition receipt and successor-control docket. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `877` | `accessibility_language_robustness`, `answer_consistency_hallucination`, `canonical_corpus_source_trace`, `feedback_correction_clock`, `human_authoritative_handoff`, `incident_disclosure_threshold`, `public_owner_boundary`, `reliance_warning_boundary`, `supplier_model_change_record`, `withdrawal_transition_receipt` |
| `878` | `accessibility_language_robustness`, `answer_consistency_hallucination`, `canonical_corpus_source_trace`, `feedback_correction_clock`, `human_authoritative_handoff`, `incident_disclosure_threshold`, `public_owner_boundary`, `reliance_warning_boundary`, `supplier_model_change_record`, `withdrawal_transition_receipt` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 1 |
| `425` | 1 |
| `426` | 1 |
| `813` | 1 |
| `815` | 1 |
| `816` | 3 |
| `817` | 6 |
| `818` | 3 |
| `820` | 1 |
| `821` | 1 |
| `824` | 1 |
| `856` | 3 |
| `857` | 9 |
| `859` | 2 |
| `860` | 1 |
| `861` | 6 |
| `867` | 1 |
| `870` | 4 |
| `874` | 3 |
| `876` | 10 |

## Use rule

Run generative-assistant tests whenever a public chatbot, AI assistant, RAG summary, service bot, or generated guidance output may shape conduct, compliance expectations, eligibility expectations, triage, or service access without a formal decision. Separate navigation from guidance, guidance from task triage, triage from compliance instruction, instruction from legal effect, and helpful summary from authoritative law.
