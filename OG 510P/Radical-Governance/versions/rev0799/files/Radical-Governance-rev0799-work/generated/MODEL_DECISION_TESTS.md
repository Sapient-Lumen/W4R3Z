# Model-decision tests matrix

Generated for `rev0799` from `metadata/model_decision_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `algorithm_business_rule_scrutiny` Algorithm / business-rule scrutiny | Are business rules, algorithms, decision lists, assumptions, thresholds, and use of ADM disclosed enough for expert, legal, ombuds, parliamentary, or public scrutiny? | `410`, `421`, `430`, `433`, `857`, `874`, `875` | Downgrade confidence and require disclosure / independent scrutiny before expansion, renewal, or reliance. |
| `burden_of_proof_floor` Burden-of-proof floor | Does the workflow preserve the public authority’s burden rather than shifting proof to the person through non-response, portal design, missing records, or collection pressure? | `424`, `425`, `426`, `817`, `857`, `874`, `875` | Remove hidden adverse inferences, add assistance and evidence-gathering duties, and pause recovery while proof is incomplete. |
| `data_lineage_periodization` Data-lineage and periodization test | Can the agency trace data source, time period, transformation, model / rule version, and statutory reporting period before legal effect? | `431`, `441`, `443`, `818`, `857`, `874`, `875` | Prevent legal effect from transformed or period-mismatched data until lineage and statutory fit are proven. |
| `evidentiary_proxy_ban` Evidentiary-proxy ban | Is a signal, data match, average, score, model output, or assumption being used as legal proof rather than as a lead for inquiry? | `404`, `421`, `430`, `857`, `861`, `874`, `875` | Treat the output as a lead only; suspend debt, sanction, or adverse effect until lawful evidence exists. |
| `human_determination_not_rubber_stamp` Human determination, not rubber stamp | Can the human reviewer inspect evidence, test legality, depart from the output, record reasons, and escalate systemic defects? | `416`, `421`, `434`, `442`, `857`, `874`, `875` | Do not call the system human-reviewed; redesign the review role or restrict the output to triage. |
| `legal_authority_gate` Legal-authority gate | Does the statute, delegation, rule, or lawful policy expressly authorize the automated or model-mediated step and the legal consequence attached to it? | `404`, `439`, `857`, `860`, `861`, `874`, `875` | Block legal effect or downshift to inquiry-support until authority is explicit and reviewable. |
| `notice_explanation_packet` Notice and explanation packet | Does the affected person receive the legal basis, proposed effect, evidence, assumptions, proof status, assistance route, stay route, and review path in intelligible form? | `424`, `425`, `426`, `430`, `451`, `857`, `874`, `875` | Replace generic letters or portal prompts with an appeal-ready explanation packet before adverse effect. |
| `remediation_learning_loop` Remediation and learning loop | If the system fails, are refunds, zeroing, compensation, apology, legal advice, class remediation, record correction, and future-guardrail changes linked to root causes? | `422`, `857`, `861`, `874`, `875` | Do not close the incident; keep a remediation docket until money, records, law, notice, review, and future safeguards are repaired. |
| `review_and_stay_route` Review and stay-of-effect route | Can the person seek internal, merits, ombuds, court, or other review, and is adverse effect or collection restrained while plausible review is live? | `404`, `422`, `425`, `817`, `821`, `824`, `857`, `874`, `875` | Pause effect, preserve the appeal packet, and repair review routing before collection or sanction continues. |
| `vulnerability_assisted_channel` Vulnerability and assisted-channel gate | Does the workflow identify people who may be unable to engage digitally or evidentially, and provide assisted, accessible, advocate, interpreter, hardship, and trauma-aware channels? | `426`, `817`, `857`, `870`, `874`, `875` | Block digital-only adverse effect and add assisted channels, outreach, and vulnerability safeguards. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `875` | `algorithm_business_rule_scrutiny`, `burden_of_proof_floor`, `data_lineage_periodization`, `evidentiary_proxy_ban`, `human_determination_not_rubber_stamp`, `legal_authority_gate`, `notice_explanation_packet`, `remediation_learning_loop`, `review_and_stay_route`, `vulnerability_assisted_channel` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 3 |
| `410` | 1 |
| `416` | 1 |
| `421` | 3 |
| `422` | 2 |
| `424` | 2 |
| `425` | 3 |
| `426` | 3 |
| `430` | 3 |
| `431` | 1 |
| `433` | 1 |
| `434` | 1 |
| `439` | 1 |
| `441` | 1 |
| `442` | 1 |
| `443` | 1 |
| `451` | 1 |
| `817` | 3 |
| `818` | 1 |
| `821` | 1 |
| `824` | 1 |
| `857` | 10 |
| `860` | 1 |
| `861` | 3 |
| `870` | 1 |
| `874` | 10 |
| `875` | 10 |

## Use rule

Run model-decision tests whenever a data match, model output, risk score, rule engine, calculator, automated workflow, or AI-assisted recommendation may produce legal or similarly significant public effect. The core discipline is to separate signal from evidence, evidence from determined fact, determined fact from debt or sanction, human review from rubber stamp, and refund or settlement from institutional repair.
