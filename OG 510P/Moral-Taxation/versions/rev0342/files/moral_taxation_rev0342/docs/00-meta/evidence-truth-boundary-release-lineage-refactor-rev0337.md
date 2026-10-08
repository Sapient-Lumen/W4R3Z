# Evidence truth boundary and release-lineage refactor — rev0337

## Judgment

The heart of this project is not “find the ideal tax.” It is **prevent a public institution from imposing a burden on the easiest visible proxy while control, benefit, rent, harm, capacity, or responsibility sits somewhere else**.

That makes Moral Taxation an **anti-category-error constitution for public burdens**. Its runtime is best understood as a public-burden compiler:

`facts → real subject/controller/beneficiary → morally relevant base → incidence and protected floors → standing/remedy → review trigger → admissible instrument → evidence needed before action`

The durable mission is constitutional and procedural. It asks who is acting, who benefits, who really pays, what cannot be bought, what remedy exists, and how a rule is corrected or unwound. Taxes, fees, mandates, bans, public options, compensation, disclosure, procurement conditions, and direct duties are outputs of that routing process—not the mission itself.

## The most serious failure found

The release machinery had crossed the exact category boundary the archive exists to defend.

`tools/build_model_input_bundle.py` generated deterministic values from case and adapter identifiers. The model-source and authority-source builders then generated locators and provenance-shaped records from those internal objects. Downstream code could label those records `implementation_grade`, treat every quantitative, floor-delivery, current-law, and jurisdiction schema as satisfied, and report **83 of 122 cases finalized**.

Those records were useful as fixtures. They were not observations, retrieved authorities, calibrated model inputs, or independent attestations. A deterministic hash can prove that an internal object is unchanged; it cannot prove that the object came from the world. SLSA provenance likewise concerns how an artifact was produced, while W3C PROV distinguishes entities, activities, and agents in a provenance account.[S681][S680] The old runtime had strong artifact lineage but no credible external evidence event. It was, in effect, **provenance laundering**: internally generated test data acquired the vocabulary of implementation evidence as it moved through enough hash-bound layers.

This was not merely an imprecise warning label. “Finalized” is a certification verb. A non-doctrine disclaimer cannot neutralize a machine status that says a case is ready after evidence was never retrieved.

### Why the prior safeguards did not save it

The safeguards mostly checked internal consistency:

- a producer identifier was registered;
- required fields existed;
- source and evidence hashes were present;
- replay returned the same result;
- the promotion packet carried non-doctrine warnings.

All of those can be true for a fictional record. The runtime did not require an externally observed origin, a verified external attestation, or a promotion-eligibility statement bound into the replay record. It also checked that a ledger hash existed without always recomputing it against the complete live record list. Consequently, a self-consistent evidence fiction could pass.

The governing distinction must be:

> **Schema-conformant is not externally observed; reproducible is not true; provenance-complete is not authority-complete; replay-clean is not implementation-ready.**

## A second serious failure: release history was self-consistent but false

The uploaded rev0336 archive said `revision: rev0336`, but both `REVISION-RECEIPT.json` and `RELEASES.json` carried a rev0335 archive root and skipped rev0335 by naming rev0334 as the previous revision. `RELEASES.json` also retained a stale creation time, and `context-pack.json` still routed readers to rev0335 reports.

The checker verified that several labels agreed with each other, but not that the lineage was arithmetically and temporally possible. This is a release-integrity analogue of the evidence problem: internally agreeing fields were accepted without checking the external semantic claim they made.

Rev0337 adds a shared lineage validator. It derives the predecessor from `VERSION`, derives the canonical zip filename from the revision, UTC creation minute, and codename, requires the exact root directory, verifies all active timestamps and source counts, and rejects stale revision labels in the current proposal/frontier routes. The same validator is used by the lineage audit, archive checker, and packager.

## What changed in rev0337

### 1. Evidence now has three non-interchangeable states

1. `reference_fixture` — examples and interface demonstrations;
2. `strict_schema_test_fixture` — full-chain conformance and replay testing;
3. `implementation_grade` — evidence supplied by an external process and explicitly eligible for promotion.

Archive builders may emit the first two. They now **refuse to manufacture the third**.

Every evidence record carries four truth-boundary fields:

- `strict_schema_test_fixture`;
- `evidence_origin`;
- `external_source_attestation_status`;
- `promotion_eligible`.

Production execution requires `evidence_origin: external_observed`, `external_source_attestation_status: verified_external_attestation`, and `promotion_eligible: true`. Authority records must additionally be primary-authority-backed and use non-fixture locators. Those fields are necessary but not self-authenticating: rev0337 has no trusted signature or credential verifier, so promotion adds a global fail-closed hold even when a caller supplies the expected strings. Flipping one flag is also insufficient because the fields are bound into an `evidence_truth_boundary_hash` and into the complete ledger hash.

### 2. Built-in audits test every interface without certifying any case

The built-in strict-schema bundle still exercises all **1,724 adapter records** across **122 cases**:

- 419 quantitative-model adapters;
- 388 protected-floor delivery adapters;
- 52 no-go threshold adapters;
- 295 current-law refresh adapters;
- 570 jurisdiction-scope adapters.

The schema executor reaches 1,672 satisfied records and 52 intentional no-go blocks, reproducing the former 83/39 structural split. But the promotion layer now sees:

- 1,724 strict-schema fixtures;
- 0 externally observed records;
- 0 verified external attestations;
- 0 promotion-eligible records;
- trusted external-attestation verifier status: `not_configured_fail_closed`;
- 0 promoted/finalized cases;
- 122 held cases.

This is the correct distinction: the archive can prove that the plumbing works while making no claim that the world has supplied the facts.

### 3. Replay and promotion bind evidence origin, not only payload shape

The replay ledger now hashes the truth-boundary fields for every record. Promotion recomputes both the per-record truth-boundary hash and the top-level ledger hash. It also refuses to promote on a self-declared attestation status: until a trusted verifier is wired in, every case receives the global `trusted_external_attestation_verifier_not_configured` hold. Tampering with evidence still produces 5,172 ordinary replay mismatches; flipping fixture promotion flags produces 12,016 mismatches across origin, eligibility, execution, finalization, trace, and result fields.

### 4. Release lineage is now a semantic gate

`tools/release_lineage.py` is the single derivation point for:

- active and previous revision;
- canonical archive root;
- canonical output filename;
- current input revision;
- creation timestamp agreement;
- source-count agreement;
- active context-route revision.

`tools/audit_release_lineage.py`, `tools/check_archive.py`, and `tools/package_release.py` all call the same validator rather than maintaining three partly overlapping label checks.

### 5. The heaviest audits no longer rebuild the same graph needlessly

Before this refactor, one promotion/output audit peaked near 400 MB RSS, and the Makefile executed replay, promotion, and output audits once inside the semantic suite and then again as separate Python processes. The revised suite:

- runs those audits once, inside `tools/run_semantic_audits.py`;
- reuses one answer-packet cache;
- writes one deterministic temporary strict-evidence bundle and reuses it across replay, promotion, and output audits;
- deletes temporary cache and bytecode artifacts before packaging.

This removes avoidable graph construction and process duplication. It does **not** yet solve the underlying memory shape: the runtime still materializes a 122-case/1,724-record graph and several deep-copy tamper variants. The next performance step should stream records case-by-case and mutate one probe record at a time rather than cloning whole bundles.

## What is missing now

### A. A genuine external evidence ingress

Rev0337 deliberately creates no positive implementation-grade fixture and configures no trusted external-attestation verifier. A caller cannot unlock promotion merely by writing `verified_external_attestation`; the project now needs an ingress and verification contract that an outside retriever or model runner can satisfy without the archive inventing or self-certifying the result. At minimum it should bind:

- producer identity and software/build identity;
- retrieval or model-run activity;
- source entity and exact locator;
- observation time, jurisdiction, effective date, and freshness policy;
- input dataset/model/parameter hashes;
- claim or output fields;
- attestation signature or independently verifiable credential;
- conflict review and human reviewer where judgment is unavoidable;
- revocation/review status.

OpenFisca is a useful architectural comparator because it separates coded legal rules from the situation supplied as input and treats formulas, variables, parameters, and tests as explicit components.[S675] PolicyEngine exposes the additional quantitative pieces this archive lacks: data pipelines, calibration, validation, behavioral responses, and reform simulations.[S676] Moral routing should consume outputs from such systems; it should not synthesize their empirical inputs from adapter identifiers.

### B. A real quantitative policy plane

The route graph can say *which* burden and model question matters. It still cannot credibly estimate revenue, distribution, behavioral response, administrative cost, take-up, error, or uncertainty. The correct architecture is two-plane:

- a **normative routing plane** that preserves floors, no-go duties, incidence questions, standing, remedies, and precedence;
- an **empirical evaluation plane** that supplies observed data and calibrated counterfactuals.

The normative plane may veto a modeled option; the model may inform magnitude and trade-offs; neither should impersonate the other.

### C. Lifecycle evaluation rather than one-time certification

The UK Green Book treats appraisal as objective analysis of costs, benefits, risks, and options rather than as the policy decision itself.[S677] The Magenta Book treats evaluation as a lifecycle activity whose evidence should support continuation, improvement, expansion, or stopping.[S678] The archive has many review triggers, but it lacks a compact executable evaluation contract tying each implemented rule to outcomes, data owners, cadence, thresholds, sunset/scale decisions, and public reporting.

A future case should not end at “finalized.” It should move through `proposed → appraised → authorized → implemented → observed → evaluated → continued/changed/stopped`.

### D. A normalized canonical graph

The current cube contains 23 axes, 155 routes, and parallel remedy, policy-action, accountability, case, and profile-index views. Many values are route- or case-specific, and substantial information is repeated across generated-looking JSON surfaces. The W3C Data Cube vocabulary centers an observation model with dimensions and measures; this repository is primarily an ontology and routing graph, not yet an observational cube.[S679]

The likely long-run correction is:

1. one canonical route/obligation graph;
2. normalized entities for actors, burdens, rights, evidence duties, remedies, and review triggers;
3. generated remedy/action/accountability/index views;
4. a separate observation cube for rates, revenue, distribution, delivery, harm, and uncertainty;
5. raw user vocabulary kept outside canonical axis vocabularies.

This would reduce drift and make diffs meaningful. It would also clarify that “datacube” names the workspace, not the present statistical data model.

### E. A positive-control implementation test

The new default correctly holds everything. That creates a new risk: the positive path could silently become impossible. The suite needs a verifier interface plus one sealed integration test using a small, explicitly test-only external attestation fixture signed by a test key. It should prove that the verifier—not an input status string—authorizes the test record, while ensuring that the test key and namespace are categorically rejected in production mode.

### F. A human-governance boundary

Current-law conflicts, jurisdiction scope, protected-floor sufficiency, and catastrophic/no-go thresholds often require contestable judgment. The machine schema should name who decides, who may challenge, what evidence is visible, what explanation is owed, and how a decision is stayed or reversed. The archive is strongest when it treats administration and remedy as substantive; that same discipline must govern its own runtime.

## What should change next

### Immediate: make external evidence possible but difficult

Define a signed external-evidence envelope, a trusted verifier interface, and a producer registry containing verifiable agent identities, allowed adapter types, build identities, attestation methods, freshness windows, and revocation status. Add one positive test namespace and keep all archive-generated data non-promotable. The verifier result—not a producer-authored status field—must be bound into the promotion decision.

### Near term: connect, do not imitate, quantitative engines

Add connector contracts for current-law rules engines, microsimulation, distribution tables, administrative-cost models, delivery/take-up models, and no-go review. The connector should return evidence plus uncertainty and provenance; the moral router should return the consequence for route selection and finalization.

### Near term: split universal gates from route modules

The scorecard and adapter layer have become comprehensive enough to be expensive and difficult to interpret. Preserve a small universal constitutional kernel—subject/base, incidence, floor, standing/remedy, source freshness, and review—then load domain-specific modules only for relevant routes.

### Medium term: stream and normalize

Process one case or adapter record at a time, persist only hashes and compact summaries in the release audit, and generate denormalized profile views from one canonical graph. Historical audit reports should be compacted into a ledger plus exceptional narrative reports rather than multiplied every revision.

### Medium term: add outcome feedback

Every implemented instrument should carry an evaluation contract and produce new observation records. Failed delivery, shifted incidence, stale law, excessive burden, or threshold breach should reopen routing automatically.

## Speculation: where this project can become unusually valuable

The most valuable future is not a universal tax recommender. It is a **public-burden constitutional middleware layer** between a proposal and the systems that calculate, administer, and review it.

That layer could accept a policy idea or real dispute and return:

- the real subjects, controllers, beneficiaries, and burden bearers;
- the morally relevant base and disallowed proxies;
- protected floors and no-go conditions;
- required current-law, jurisdiction, quantitative, and delivery evidence;
- who owes which default or remedy;
- what can be automated and what requires accountable judgment;
- why the case is held;
- what event would reopen, sunset, or reverse the decision.

OECD Tax Administration 3.0 is oriented toward increasingly seamless administration.[S674] This archive can contribute a necessary counterweight: seamless service should not mean invisible contest, irreversible automation, or burdens optimized around administrative convenience. The distinctive mission is to make friction low for legitimate access and correction while making unjustified burden imposition hard.

A clearer public name for the machine layer may eventually be **Moral Fiscal Router** or **Public Burden Router**, while *Moral Taxation* remains the project and constitutional tradition. The name change is optional; the evidence boundary is not.

## Current honest status

Rev0337 is a strong routing and conformance system with a repaired truth boundary. It can generate candidate routes, profiles, claims, precedence, dispositions, adapter requirements, evidence work orders, schema-conformance evidence, replay ledgers, promotion decisions, and held output packets. It can demonstrate that all 1,724 adapter interfaces are wired.

It cannot yet claim that current law was retrieved, jurisdiction was resolved, a fiscal model was calibrated or run on real inputs, a protected floor will be delivered, a no-go judgment was made by an authorized reviewer, or any case is implementation-ready. It also cannot authenticate a future producer’s attestation because no trusted verifier is configured. Accordingly, the built-in release audit finalizes **zero** cases and the promotion gate remains globally fail-closed. That is not a regression. It is the first release in this chain whose machine status matches its evidence.

[S674]: <https://www.oecd.org/en/publications/tax-administration-3-0-the-digital-transformation-of-tax-administration_ca274cc5-en.html> "OECD — Tax Administration 3.0"
[S675]: <https://openfisca.org/doc/index.html> "OpenFisca — Documentation"
[S676]: <https://www.policyengine.org/us> "PolicyEngine — Open-source tax and benefit analysis"
[S677]: <https://www.gov.uk/government/publications/the-green-book-appraisal-and-evaluation-in-central-government> "HM Treasury — The Green Book"
[S678]: <https://www.gov.uk/government/publications/the-magenta-book/magenta-book-central-government-guidance-on-evaluation-html> "HM Treasury and Evaluation Task Force — Magenta Book"
[S679]: <https://www.w3.org/TR/vocab-data-cube/> "W3C — The RDF Data Cube Vocabulary"
[S680]: <https://www.w3.org/TR/prov-o/> "W3C — PROV-O"
[S681]: <https://slsa.dev/spec/v1.2/provenance> "SLSA — Provenance v1.2"
