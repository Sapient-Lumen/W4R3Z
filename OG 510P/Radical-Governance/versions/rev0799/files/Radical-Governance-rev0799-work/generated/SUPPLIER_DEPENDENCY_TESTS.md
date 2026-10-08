# Supplier dependency tests matrix

Generated for `rev0799` from `metadata/supplier_dependency_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `authority_owner` Public authority owner test | Can the docket identify the public function, public owner, statutory or administrative authority, accountable officer or board, and the decision the supplier must not make? | `439`, `544`, `856`, `857`, `859`, `866`, `867` | Treat the system as capture-prone or unlawful delegation risk until the public owner and supplier boundary are explicit. |
| `benefit_claim` Benefit-claim evidence test | Can each public benefit claim be tied to a method, baseline, comparator, confidence label, rival explanation, correction route, and decision consequence? | `421`, `457`, `458`, `484`, `857`, `859`, `866`, `867` | Treat the claim as promotional or hypothesis-level until the method and rival explanations are recorded. |
| `confidence_separation` Confidence separation test | Are procurement, security, privacy, performance, benefit, trust, and exit confidence separately evidenced rather than collapsed into one assurance story? | `421`, `452`, `484`, `856`, `857`, `859`, `866`, `867` | Label the missing confidence lane and block the claim from being used as a settled holding until repaired. |
| `exit_rehearsal` Exit rehearsal and portability test | Can the public authority demonstrate export, migration, step-in, replacement, deletion / return, records preservation, and continuity under termination or supplier failure? | `408`, `420`, `441`, `443`, `856`, `859`, `861`, `866`, `867` | Declare a fragile or capture-prone dependency and require migration / fallback repair before renewal or expansion. |
| `opposition_trust` Opposition and trust evidence test | Does the docket preserve serious patient, user, staff, professional, local-body, public, or legislative opposition with a response, falsifier, and decision consequence? | `843`, `844`, `856`, `857`, `859`, `866`, `867` | Do not treat communications or engagement as trust; add a decision record that shows how opposition affects risk, adoption, data quality, and continuity. |
| `privileged_access` Privileged access and admin-session test | Can privileged supplier, support, emergency, and administrator access be reconstructed by person, role, purpose, approval, time, data class, action, and review? | `416`, `422`, `444`, `856`, `859`, `866`, `867` | Block or narrow privileged access, add logging and review, or move the platform to fragile dependency status. |
| `processor_boundary` Processor / sub-processor boundary test | Are controller, joint-controller, processor, sub-processor, integrator, support, and model-provider roles named for each product, dataset, instance, or service? | `431`, `559`, `856`, `859`, `866`, `867` | Pause expansion or downgrade confidence if legal role labels are generic, stale, or not product-specific. |
| `product_purpose_gate` Product / use-case purpose gate | Does each product or use case have a named purpose, legal basis, data category, affected-party map, DPIA / impact review, launch date, and review clock? | `410`, `421`, `429`, `433`, `459`, `856`, `859`, `866`, `867` | Do not let generic platform approval authorize the new product; require product-level review before use. |
| `public_redress` Public redress over private help-desk test | Can affected people challenge supplier-shaped errors, data misuse, workflow harm, model output, or access denial through a public route backed by reconstructable records? | `404`, `425`, `494`, `554`, `559`, `856`, `859`, `866`, `867` | Add public redress and evidence packet requirements before relying on the supplier-shaped process. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `866` | `authority_owner`, `benefit_claim`, `confidence_separation`, `exit_rehearsal`, `opposition_trust`, `privileged_access`, `processor_boundary`, `product_purpose_gate`, `public_redress` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `404` | 1 |
| `408` | 1 |
| `410` | 1 |
| `416` | 1 |
| `420` | 1 |
| `421` | 3 |
| `422` | 1 |
| `425` | 1 |
| `429` | 1 |
| `431` | 1 |
| `433` | 1 |
| `439` | 1 |
| `441` | 1 |
| `443` | 1 |
| `444` | 1 |
| `452` | 1 |
| `457` | 1 |
| `458` | 1 |
| `459` | 1 |
| `484` | 2 |
| `494` | 1 |
| `544` | 1 |
| `554` | 1 |
| `559` | 2 |
| `843` | 1 |
| `844` | 1 |
| `856` | 8 |
| `857` | 4 |
| `859` | 9 |
| `861` | 1 |
| `866` | 9 |
| `867` | 9 |

## Use rule

Run supplier-dependency tests whenever a public function relies on cloud, SaaS, AI models, identity providers, analytics platforms, managed support, data platforms, or procurement vehicles. Passing procurement, security, or privacy review is not enough unless authority ownership, privileged access, product purpose, benefit claims, public redress, opposition, fallback, and exit can also be reconstructed.
