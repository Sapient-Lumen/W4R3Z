# Schema Conformance, Datacube Control Stack, and Queryable Governance

## Why this file exists

`170-capacity-planning-resource-allocation-backlog-and-work-in-progress-governance.md` prevents priority from being treated as work done. That was the right next control. But it exposes a stricter failure mode: the archive can have capacity, a register, a schema, a validator, and a package manifest, while still not having a **queryable structure** that says which rows exist, which schema they satisfy, what the control stack is, which fields are actually present, which debts are still open, and what claims are still forbidden.

The immediate trigger for this revision was a concrete schema defect. `REGISTERS/schemas/capacity-allocation-record-v1.yml` requires `deferral_class`, but the rev0164 capacity record used `Deferral_class_note` instead. The old local validator still reported success because it checked package structure, expected artifacts, front-door references, file continuity, and manifest hashes, but not record conformance against declared required fields. That is exactly the archive's own warning in operational form: a tidy artifact can overstate its warrant.

This file adds a layer after capacity governance: **schema conformance, profile clarity, canonical control-stack mapping, datacube indexing, queryable observations, external-method crosswalks, and forbidden query-language control**. Its question is not only "does the release have the expected files?" but **which machine-readable rows exist, which shape do they satisfy, which controls do they instantiate, what can be queried, what cannot be inferred, and where does the archive still lack a real cube rather than prose about a cube?**

The rule is simple:

> **Do not call a register, release, control sequence, schema, source packet, or governance file datacube-ready until the archive states row type, dimensions, measures, attributes, schema profile, required-field result, control-stack position, query permission, forbidden inference, open debt, and next conformance trigger.**

## Compressed default

The archive should now say:

> **A schema is not conformance. A register is not a cube. A repeated control sequence is not a canonical control map. A successful package check is not a proof that the data layer can be queried safely.**

In shorter form:

> **Rows before rhetoric.**

And more carefully:

> **Every current release record, control artifact, validation claim, public-use boundary, source-dependent note, deployment limit, incident lesson, monitoring trigger, risk item, capacity packet, or datacube observation should state its profile, required-field status, control-stack location, observable dimensions, measured counts or states, qualifying attributes, allowed query language, forbidden inference language, and open conformance debt before it is used as machine-readable governance evidence.**

This file therefore shifts the archive from **capacity-aware execution governance** to **queryable-control governance**.

## Place in the control sequence

The intended hard-case sequence is now:

1. **Route** the case or proposed addition with `144`.
2. **Stress-test** the routed verdict with `145`.
3. **Ledger** reusable or precedent-setting cases with `146`.
4. **Propagate** accepted changes with `147`.
5. **Register terminology** with `148`.
6. **Assign commitment status** with `149`.
7. **Write the application dossier** with `150` when the result must travel.
8. **Govern reuse, transfer, appeal, and review** with `151`.
9. **Govern transmission and compression** with `152`.
10. **Audit reception and correction loops** with `153`.
11. **Gate the release and ledger maintenance state** with `154`.
12. **Record version lineage, compatibility, forks, and migration** with `155`.
13. **Record provenance, custody, build evidence, and reproducibility** with `156`.
14. **Classify review authority, audit scope, certification status, and warranted claim language** with `157`.
15. **Assign public reliance, citation, dispute, withdrawal, and retraction rules** with `158`.
16. **Assign stewardship obligations, delegated authority, and accountability** with `159`.
17. **Register operational memory and watch queues** with `160`.
18. **Validate local schemas, transcripts, invariants, and manifest structure** with `161`.
19. **Execute and record the release workflow** with `162`.
20. **Bind automation, delegated agents, scheduled checks, and tool permissions** with `163`.
21. **Audit generated and compressed outputs for semantic fidelity and warning retention** with `164`.
22. **Classify operational reliance and deployment boundaries** with `165`.
23. **Classify incidents, near misses, harms, evidence duties, containment actions, recovery paths, residual risk, and closure conditions** with `166`.
24. **Extract post-incident learning, root-cause profiles, recurrence-risk classes, corrective/preventive actions, verification tests, and learning closure conditions** with `167`.
25. **Monitor whether learned controls remain effective, whether residual risk is rising or falling, and whether controls should be renewed, escalated, migrated, sunset, or archived** with `168`.
26. **Aggregate residual risks, shared dependencies, exposure concentrations, correlated failure modes, review burdens, and treatment priorities across the portfolio** with `169`.
27. **Allocate capacity, admit or reject backlog items, limit work in progress, classify deferrals, and state resource debt** with `170` before claiming that priority items are assigned, manageable, monitored, safe to defer, or release-compatible.
28. **Validate schema conformance, canonicalize the control stack, and expose a first datacube index** with this file before claiming that the archive is queryable, cube-ready, control-map-consistent, or machine-readable in any strong sense.

`170` asks: **can the work actually be carried?**  
`171` asks: **can the carried work be queried without laundering warrant?**

## What changes in rev0165

This revision makes nine concrete changes.

1. It repairs the rev0164 capacity-record field defect by exposing `deferral_class` as a machine-readable field while retaining a note about the repair.
2. It adds `CONTROL_STACK.yml`, the first canonical machine-readable control-stack map for steps `144` through `171`.
3. It adds `CUBE_INDEX.yml`, the first archive-local datacube index with observation families, dimensions, measures, attributes, query examples, and current-release observations.
4. It adds `EXTERNAL_CROSSWALK.yml`, a non-authoritative crosswalk to RDF Data Cube, SHACL, PROV, SKOS, FAIR, BFO, DOLCE, OBO Foundry practice, datasheets, model cards, NIST AI RMF, and Kanban/WIP practice.
5. It adds new schemas for schema-conformance, control-stack, and datacube-index records.
6. It adds a runbook for schema-conformance/datacube review.
7. It adds full-profile current-version records for validation, workflow, automation, semantic fidelity, deployment boundary, incident response, post-incident learning, effectiveness monitoring, risk portfolio, capacity allocation, schema conformance, control stack, and datacube index.
8. It strengthens `tools/validate_archive.py` so the current release records are checked against their declared required fields, and so the cube/control artifacts are checked for expected structure.
9. It preserves older compact records as historical memory while making the current release records conform to their own required-field schemas.

## Why this is a datacube revision, not just a validation revision

A validation harness can say whether files and fields exist. A datacube says what **observations** the archive is prepared to make. That distinction matters.

A release record is not only a file. It is an observation about an artifact under a version, schema, control step, status, evidence basis, debt count, and claim boundary. A capacity packet is an observation about available resource, backlog status, work-in-progress state, deferral class, scarce dependency, owner status, stop condition, and open resource debt. A semantic-fidelity record is an observation about a transformation, audience, warning-retention class, compression level, reuse permission, and known fidelity risks. A deployment-boundary record is an observation about operational context, action reliance, domain review, source-current status, override path, monitoring requirement, and forbidden actions.

The archive does not yet need a heavyweight RDF deployment. It does need the conceptual discipline of a cube:

- **dimensions** identify the row: version, file, artifact family, schema, control step, audience, use class, status family, source boundary, steward, owner, or profile;
- **measures** give the observed values: required-field count, missing-field count, open-debt count, touched-file count, observation count, validation-failure count, warning count, or review-trigger count;
- **attributes** qualify interpretation: allowed claim language, forbidden claim language, human-review boundary, source-current caveat, public-use boundary, domain boundary, profile status, and next trigger.

This revision therefore treats `CUBE_INDEX.yml` as a first local cube layer. It is not a database, public registry, RDF publication, linked-data endpoint, source-watch service, or external audit. It is a structured local row map that lets a successor ask safer questions.

## Minimum observation families

A future full cube should support at least these observation families.

### Release observation

A release observation states version identity, package name, predecessor, final numbered document, release class, validation status, manifest status, workflow status, current-record profile, open validation debt, and forbidden release claims.

### Register observation

A register observation states record file, schema file, required-field count, present-field count, missing-field count, record profile, schema-conformance status, governing control step, allowed claim language, and open record debt.

### Control-step observation

A control-step observation states step number, file, role, predecessor relation, successor relation, artifact requirements, status families introduced, validator expectations, and drift hazards.

### Source-boundary observation

A source-boundary observation states source anchor, source family, currentness status, revision note, public-use relevance, domain-sensitivity status, source-refresh trigger, and forbidden extrapolation.

### Claim-boundary observation

A claim-boundary observation states claim, artifact basis, status class, permitted audience, forbidden audience or use, required warnings, review expiry, and withdrawal trigger.

### Risk/capacity observation

A risk/capacity observation states risk cluster, portfolio status, priority treatment, capacity status, backlog class, work-in-progress class, deferral class, resource basis, owner/declined responsibility, stop condition, and open capacity debt.

### Incident/learning/monitoring observation

An incident/learning/monitoring observation states incident or near-miss class, harm severity, recovery class, learning status, root-cause profile, CAPA class, monitoring status, residual-risk trend, sunset/renewal class, and recurrence trigger.

### Derivative-output observation

A derivative-output observation states source version, output type, compression level, intended audience, semantic-fidelity status, warning-retention class, deployment status, action-reliance class, reuse permission, and correction trigger.

## Schema profile rule

Beginning with rev0165, the archive should distinguish three record profiles.

### `full_current_release`

A current-version record that the release validator checks against its schema's `required_fields`. Missing required fields are release-blocking unless explicitly waived in the validation record and not contradicted by the schema-conformance report.

### `historical_compact`

An older record retained as successor memory. It may be useful as lineage evidence even if it does not satisfy a later full-profile schema. It must not be used as proof that the historical release had full schema conformance unless a separate conformance report says so.

### `draft_or_candidate`

A proposed register, schema, query, control-stack row, or cube observation that is not yet release evidence. It should have an owner or declined responsibility, a next action, and a stop condition before it is cited as active work.

The validator now checks the current release records. It does not retroactively require every historical compact record to satisfy the stronger profile. That would make the archive less honest by rewriting all older memory as if it had always been full-profile governance.

## Schema-conformance statuses

Use these statuses when a register, schema, or report claims conformance.

### SC0 — no conformance claim

No field, shape, or checklist claim is made.

### SC1 — schema named only

A schema is named but no required-field check has been run.

### SC2 — manual field review

A human inspected required fields, but no machine-readable report exists.

### SC3 — scripted required-field check

A script checked required-field presence and non-empty values.

### SC4 — scripted profile-aware check

A script distinguished current full-profile records from historical compact records, draft records, and explicit waivers.

### SC5 — schema plus status-vocabulary check

Required fields and status vocabularies are checked. This revision does not yet claim full SC5 coverage.

### SC6 — schema plus cross-artifact reference check

Fields are checked and references to files, schemas, runbooks, control steps, and records are checked for existence.

### SC7 — query-regression checked

Representative queries are run across the cube or register set and expected rows are confirmed.

### SC8 — independently reproduced conformance

An independent environment or reviewer reproduces the checks.

### SC9 — failed, unsafe, or conformance-laundered

The artifact claims conformance while missing required fields, hiding waivers, mixing profiles, or implying authority beyond the check.

## Datacube-readiness statuses

Use these statuses when a release claims to expose a datacube.

### DC0 — no cube claim

No datacube, cube index, or observation model is claimed.

### DC1 — cube metaphor only

The archive uses cube language without a row model.

### DC2 — observation families named

Observation families are identified, but rows are not yet enumerated.

### DC3 — dimensions, measures, and attributes named

The archive distinguishes row identity, measured values, and qualifying metadata.

### DC4 — local cube index present

A local file such as `CUBE_INDEX.yml` lists observation families, dimensions, measures, attributes, and query examples.

### DC5 — current-release observations enumerated

Current release records appear as explicit observations with schema, control-step, field-count, debt-count, and claim-boundary dimensions.

### DC6 — cross-release observations enumerated

Historical releases are captured under explicit profile rules, not silently normalized into the current profile.

### DC7 — executable query harness

Representative queries are executable and regression-checked.

### DC8 — externally interoperable cube

The cube is expressible in a public standard or independently consumed format.

### DC9 — false or unsafe cube claim

Cube language is used to imply completeness, authority, source currency, public infrastructure, domain validity, or operational readiness that the rows do not support.

Rev0165 claims **DC4/DC5 locally**, not DC7/DC8.

## Control-stack statuses

Use these statuses when the archive names a governance sequence.

### CST0 — no control-stack claim

No ordered control relation is claimed.

### CST1 — prose sequence only

A sequence is described in prose and may drift across files.

### CST2 — current final step named

The final control step is named, but predecessor and successor relations are not machine-readable.

### CST3 — local control-stack artifact present

A file such as `CONTROL_STACK.yml` lists step number, file, role, predecessor/successor relation, and artifact expectations.

### CST4 — control-stack checked by validator

A local validator checks the expected structure and confirms that the final numbered document appears in the stack.

### CST5 — control-stack drives artifact checks

The validator derives expected artifacts from the stack rather than maintaining duplicate hard-coded logic.

### CST6 — control-stack drift regression

The archive detects when a prose sequence, index, runbook, or record diverges from the canonical stack.

### CST7 — external or independent control-stack review

An independent reviewer confirms stack completeness and applicability.

### CST8 — multi-custodian control-stack governance

The stack is maintained by multiple accountable custodians with public change control.

### CST9 — false or unsafe control-stack claim

A canonical sequence is claimed while artifacts, records, or required checks are missing or contradicted.

Rev0165 claims **CST3/CST4 locally**, not CST5+.

## Query-permission classes

Use these classes when deciding what a user or successor may ask the cube.

### QRY0 — no query claim

No reliable query may be inferred.

### QRY1 — artifact lookup

The user may ask whether a file, register, schema, or runbook exists.

### QRY2 — current required-field query

The user may ask whether current release records contain their required fields.

### QRY3 — current status/debt query

The user may ask which current records state open debt, allowed claim language, forbidden claim language, or next triggers.

### QRY4 — control-stack query

The user may ask which control step governs a record, file, status family, or artifact requirement.

### QRY5 — local source-boundary query

The user may ask which external anchors are named and what they are used for inside the archive.

### QRY6 — cross-release lineage query

The user may ask how historical releases changed, but only under explicit profile differences and historical caveats.

### QRY7 — executable regression query

The query is executed by a maintained harness with expected-result tests.

### QRY8 — public/interoperable query

The cube is public, stable, and externally consumable under a stated interface.

### QRY9 — unsafe query or forbidden inference

The query asks the cube to prove metaphysical truth, source currency, domain applicability, legal/clinical/engineering/financial advice, public monitoring, independent certification, or operational readiness.

Rev0165 permits QRY1–QRY4 locally, and QRY5 as a source-anchor lookup. It does not permit QRY7/QRY8.

## External crosswalk: borrow the discipline, not the authority

This revision adds non-authoritative source anchors because the archive is moving from prose governance toward row governance. The anchors do not certify the archive. They supply design analogies and naming pressure.

- **RDF Data Cube Vocabulary**: borrow the distinction among dimensions, measures, attributes, observations, and datasets. Do not claim that this archive is an RDF Data Cube publication.
- **SHACL**: borrow the distinction between data being checked and shapes used to check it. Do not claim that the YAML schemas are SHACL shapes.
- **PROV-O / PROV-DM**: borrow the entity/activity/agent pattern for provenance. Do not claim external provenance validation.
- **SKOS**: borrow concept-scheme discipline for operator families, terminology registers, aliases, source terms, and unsafe shortcuts. Do not claim public linked-data vocabulary governance.
- **FAIR**: borrow findable, accessible, interoperable, reusable pressure for digital assets, tools, workflows, and records. Do not claim FAIR compliance.
- **BFO, DOLCE, and OBO Foundry practice**: borrow top-level ontology and ontology-engineering comparison pressure. Do not claim conformance to BFO, DOLCE, ISO/IEC 21838, or OBO Foundry principles.
- **Datasheets for Datasets and Model Cards**: borrow structured documentation of motivation, composition, intended use, performance/evaluation, limitations, and maintenance. Do not claim that the archive is a dataset datasheet or model card.
- **NIST AI RMF**: borrow the separation of governance, mapping, measuring, and managing as a risk-control analogy. Do not claim AI RMF compliance.
- **Kanban/WIP practice**: borrow WIP-limit and flow-control discipline. Do not claim public project-management infrastructure, staffing, or service-level support.

The rule for external anchors is: **analogy may improve local discipline, but it must not import external authority by name-dropping.**

## Missing conceptual modules exposed by the cube

The cube layer makes several absences easier to see. These are not rev0165 release blockers, but they are strong candidates for future conceptual expansion.

### Formal ontology crosswalk

The archive needs a dedicated file comparing Layered Process Realism with BFO, DOLCE, SKOS, RDF/OWL/SHACL-style shape governance, and OBO-style ontology-engineering principles. The point would not be to force the archive into one framework. It would be to distinguish philosophical theory, reference ontology, concept scheme, decision grammar, and machine-readable governance layer.

### Physics ontology front

The archive has pieces on fields, structure, symmetry, probability, measurement, laws, processes, and emergence, but it lacks a concentrated treatment of quantum ontology, field ontology, spacetime ontology, gauge redundancy, measurement, effective theories, and symmetry-breaking. A process-realist theory should eventually face that front directly.

### Computation, software, and digital artifacts

The archive now governs generated outputs, validators, manifests, automation, scripts, schemas, packages, and handoffs. It needs a first-order ontology of code, datasets, models, simulations, prompts, agents, pipelines, platformed objects, digital copies, execution traces, and computational artifacts.

### Information, statistics, and thermodynamic structure

The archive uses entropy-like and information-like ideas throughout: compression, irreversibility, noise, attenuation, bottlenecks, throughput, accumulation, depletion, hysteresis, and coarse-graining. It needs a central file on information, statistical ensembles, entropy, compression, uncertainty, measurement, coarse-grained state, and thermodynamic constraint.

### Axiology and value ontology

Normativity and reasons are represented, but goods, harms, value, welfare, legitimacy, justice, public accountability, and remedial responsibility are not yet cleanly distinguished from deontic structure. The governance stack now talks about harm, incidents, public reliance, and stewardship; value ontology should eventually become first-order.

### Authority, delegation, and institutional power

Social ontology is present, but the archive needs a more explicit account of authority, standing, delegation, certification, public warrant, uptake, contestation, withdrawal, retraction, and accountability as social-power structures. Without it, public-use governance remains operationally careful but conceptually under-described.

## Failure modes

### Schema theater

A schema exists, but records are not checked against it. Rev0164 exhibited this in miniature.

### Profile ambiguity

A record is historical, compact, draft, or current-full-profile, but the archive does not say which. Users then treat all records as equally conformant.

### Cube laundering

The archive uses datacube language to imply a queryable database, public linked-data endpoint, external interoperability, or complete observation layer that does not exist.

### Control-sequence drift

The same 27- or 28-step sequence is repeated across files, but one copy changes while another does not. A canonical `CONTROL_STACK.yml` reduces the drift surface.

### Status-code prose blending

A field stores a code and an explanatory sentence in one scalar. That is readable, but it makes machine validation weaker. Future revisions should separate code, supporting code, and note.

### Query overreach

A user asks the cube for metaphysical truth, source currency, public reliability, domain safety, legal/clinical/engineering/financial suitability, or operational readiness. Those are forbidden inferences unless separate authority exists.

### External-analogy laundering

The archive cites SHACL, RDF Data Cube, FAIR, BFO, DOLCE, OBO, model cards, NIST AI RMF, or Kanban to borrow discipline, then implies compliance. Rev0165 explicitly forbids that upgrade.

### Row invisibility

A governance claim exists in prose but not as a row, field, observation, query target, or validation condition. Successors cannot reliably find or test it.

## Rev0165 local conformance packet

**Schema-conformance status:** SC4 locally. Current full-profile release records were generated with required fields and the validator now checks those fields. Historical compact records remain historical memory and are not silently upgraded.

**Datacube status:** DC4/DC5 locally. `CUBE_INDEX.yml` names observation families, dimensions, measures, attributes, query examples, and current-release observations. It is not an executable query engine or public RDF cube.

**Control-stack status:** CST3/CST4 locally. `CONTROL_STACK.yml` names the stack from `144` through `171`, and the validator checks expected structure.

**Query permission:** QRY1–QRY4 locally, QRY5 as source-anchor lookup. No public query service, scheduled monitor, external source watch, or independent audit is created.

**Allowed claim:** `rev0165` adds local schema-conformance checking for current release records, a canonical control-stack artifact, a first local datacube index, source-analogy crosswalks, current full-profile records, and validator checks for the new artifacts.

**Forbidden claim:** do not say the archive now has RDF publication, SHACL validation, FAIR compliance, BFO/DOLCE/OBO conformance, public linked data, public issue tracking, public monitoring, source-watch automation, independent audit, domain certification, operational deployment authority, or executable public query service.

**Open debt:** no public query service and no query-regression suite, no status-vocabulary validation, no cross-reference validation for every field, no RDF/JSON-LD publication, no independent reproduction, no public registry, no historical full-profile normalization, no current-source watch, no domain review, and no complete conceptual modules for formal ontology crosswalk, physics ontology, software/digital artifacts, information/statistics/thermodynamics, axiology, or authority/power.
