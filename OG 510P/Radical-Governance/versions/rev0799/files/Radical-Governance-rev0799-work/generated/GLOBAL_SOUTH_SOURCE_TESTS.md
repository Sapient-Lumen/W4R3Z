# Non-English / Global South official-source tests matrix

Generated for `rev0799` from `metadata/global_south_source_tests.json`.

## Tests

| Test | Question | Related notes | Repair if failed |
| --- | --- | --- | --- |
| `GSS-01` Authoritative-language and translation status | Can the packet identify the authoritative-language source and whether each translation is controlling, official courtesy, machine-generated, third-party, or archive-created? | `857`, `910`, `921`, `922` | Do not treat an English or machine-translated summary as legal or service proof until authoritative-language status is visible. |
| `GSS-02` Publication and supersession chain | Does the packet distinguish law, decree, regulation, bill, consultation, strategy, service page, FAQ, informe, portal, and local instruction, with amendment and supersession clocks? | `857`, `910`, `917`, `921`, `922` | Block source reliance where a bill, strategy, FAQ, or press release is being used as if it were the operative rule. |
| `GSS-03` Claim-class allowed by source | Is each source limited to the claim class it can support: legal authority, service route, statistics, policy intent, currentness, implementation evidence, or remedy? | `857`, `910`, `921`, `922` | Downgrade claims that ask a source to carry more authority than its publication state permits. |
| `GSS-04` Identity, credential, and document-wallet consequence | Can the packet show how CPF, gov.br level, Aadhaar, biometric / offline verification, bank validation, phone, or document wallet affects access and fallback? | `901`, `905`, `921`, `922` | Do not credit digital identity as service access until failure, recovery, and assisted routes are visible. |
| `GSS-05` Benefit and payment consequence | If a registry, data match, qualification review, or credential route can affect benefits or payment, are block, suspension, cancellation, appeal, restoration, and retroactive payment states visible? | `894`, `897`, `901`, `921`, `922` | Do not treat registry update guidance as benefit governance until payment consequences and restoration routes are explicit. |
| `GSS-06` Local and frontline implementation route | Does the official-source packet identify the local office, municipality, service counter, helpdesk, or implementing body that can actually cure the problem? | `816`, `817`, `819`, `919`, `921`, `922` | Treat national digital-service claims as incomplete until the frontline cure route is named and evidence-bearing. |
| `GSS-07` Data-protection and automated-decision boundary | Can data-protection, automated-decision review, consent, requester, and correction sources be tied to actual service consequences rather than principles alone? | `436`, `818`, `857`, `921`, `922` | Do not cite privacy or data-protection law as operational remedy without the route that a person can use. |
| `GSS-08` Notice, language, disability, assisted, and offline route | Does the packet prove that notice and cure are reachable for people facing language, disability, device, credential, literacy, or local-capacity barriers? | `424`, `425`, `426`, `894`, `901`, `921`, `922` | Do not count a digital service as inclusive until language, disability, assisted, and offline routes are operational. |
| `GSS-09` Source-health review clock | Is the review cadence proportional to volatility, and are volatile service pages, FAQs, legislative statuses, and machine-translated pages marked for periodic check? | `857`, `910`, `921`, `922` | Add source-health entries before relying on volatile service or legislative-currentness pages. |
| `GSS-10` Comparator discipline | Does the case avoid country-level flattening by saying exactly which source-state pattern transfers and which does not? | `848`, `860`, `861`, `910`, `921`, `922` | Separate the comparator or downgrade the claim if a Brazil, India, donor, or benchmark source is being generalized beyond its source state. |

## Case examples

| Case | Tests activated |
| --- | --- |
| `922` | `GSS-01`, `GSS-02`, `GSS-03`, `GSS-04`, `GSS-05`, `GSS-06`, `GSS-07`, `GSS-08`, `GSS-09`, `GSS-10` |

## Related-note recurrence

| Note | Count |
| --- | ---: |
| `424` | 1 |
| `425` | 1 |
| `426` | 1 |
| `436` | 1 |
| `816` | 1 |
| `817` | 1 |
| `818` | 1 |
| `819` | 1 |
| `848` | 1 |
| `857` | 5 |
| `860` | 1 |
| `861` | 1 |
| `894` | 2 |
| `897` | 1 |
| `901` | 3 |
| `905` | 1 |
| `910` | 5 |
| `917` | 1 |
| `919` | 1 |
| `921` | 10 |
| `922` | 10 |

## Use rule

Run non-English / Global South source tests whenever an official source, translated source, machine-translated service page, national digital ID, document-wallet route, social-benefit registry, public-service AI plan, pending AI bill, donor / benchmark summary, or country comparator is used as proof of law, service access, identity, benefit payment, notice, correction, appeal, or implementation. Separate source language, translation status, publication state, claim class, currentness, identity / benefit consequence, local implementation, and remedy before citing a summary as authority.
