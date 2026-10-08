# 427 — Third-party model and supplier registers for public AI

## One-line thesis

If a public AI system depends on outside models, APIs, vendors, or managed services, those dependencies should be inventoried, attributable, and governable as a live public risk surface rather than hidden implementation detail.

## Why this matters

Public bodies increasingly rely on models, APIs, hosting layers, vector stores, moderation services, and other components they did not fully build themselves. That can be pragmatic, but it also creates a governance blind spot.

The public may be told that a department “uses an AI tool” without learning:

- which parts are run by a supplier,
- which model family is actually doing the work,
- which components can change without a visible procurement event,
- which datasets, embeddings, or hosted services sit in the critical path,
- which risks remain under direct public control and which are merely contractually promised away.

Current official guidance points in a stronger direction. NIST’s AI RMF Playbook says pre-trained models should be identified within the AI system inventory for risk tracking and monitored as part of third-party risk tracking. The UK AI Playbook says departments should work with commercial colleagues so responsible-AI expectations are aligned across in-house and third-party systems, and notes that contracts can require supplier transparency across the information categories used in the ATRS. UK security guidance separately says proposed and active third-party products should be routinely assessed throughout the life cycle. The UK Data and AI Ethics Framework also says third-party suppliers handling data should be vetted and comply with project security requirements.

The archive should therefore treat **dependency visibility** as core public governance. If the state cannot clearly name the external pieces it depends on, it cannot credibly govern them.

## Pattern pack

### 1. Keep a dependency register at system and component level

For every consequential public AI system, maintain a live register that names:

- the primary service owner,
- each third-party model or model family,
- each hosted API or managed AI service,
- any critical retrieval, moderation, transcription, or ranking component,
- any supplier with operational or update authority,
- the fallback or substitute path if that dependency fails or becomes unacceptable.

This register should be specific enough to support risk review rather than so generic that every entry just says “cloud AI service”.

### 2. Publish a public-facing summary for consequential systems

Not every technical dependency belongs in a public web page, but the public should still be able to see the major external dependencies behind consequential decisions or high-impact service interactions. A public summary should usually disclose:

- whether the system is fully in-house, vendor-hosted, or mixed,
- whether it relies on foundation models or pre-trained models from outside the department,
- whether data leaves the department boundary,
- who operates the critical inference path,
- which dependencies are most material to continuity, privacy, and explainability.

This keeps transparency records from implying a level of sovereign control that does not actually exist.

### 3. Require supplier explainability and artifact access up front

A public body should not procure an AI service it cannot meaningfully interrogate. Contracts and due diligence should require suppliers to explain:

- intended purpose,
- limitations and likely failure modes,
- training or adaptation assumptions where disclosable,
- update and change processes,
- evaluation evidence,
- monitoring hooks,
- data handling arrangements,
- incident escalation paths.

If the supplier cannot support the institution’s transparency, appeal, or oversight obligations, the product is not governance-ready.

### 4. Treat pre-trained and open models as dependencies, not magic raw material

Open source or downloadable models are not exempt from governance simply because they are locally deployed. If a team uses a third-party model checkpoint, embedding model, or open model repository, it should track:

- provenance,
- version,
- license,
- security review,
- known limitations,
- update cadence,
- whether downstream components depend on it implicitly.

“Self-hosted” should not be confused with “fully understood” or “fully controlled”.

### 5. Tie dependency changes to governance refresh, not just engineering release

A switch in model provider, inference host, retrieval layer, or safety service can materially change public risk. The archive should treat the following as governance events:

- moving from in-house to vendor inference,
- swapping one model family for another,
- adding a moderation or ranking layer,
- changing where data is stored or processed,
- introducing a new subcontractor into the service path.

These should trigger refreshed notices, review of the impact dossier, retraining of operators where needed, and updated public records.

### 6. Distinguish operational control from contractual assurance

A system may be contractually governed yet still operationally dependent on outside actors. Public records should distinguish between:

- controls the department can directly enforce in real time,
- assurances provided only by supplier documentation,
- controls that exist only through contract, audit, or termination rights.

This matters because oversight is weaker when the institution must ask a supplier to inspect, explain, or stop part of the system.

### 7. Test substitution before dependency stress becomes crisis

If a dependency is critical, the department should know what happens when it degrades, changes terms, fails security review, or becomes politically or legally unacceptable. That means rehearsing:

- alternate providers,
- simpler deterministic fallbacks,
- manual handling modes,
- temporary feature disablement,
- exit paths that preserve service continuity.

A dependency register is only real if it supports credible substitution planning.

## Guardrails

- Do not describe supplier dependence so vaguely that accountability disappears.
- Do not claim local control where the decisive model behavior is externally set.
- Keep public disclosures high-level where security or confidential business information requires restraint, but never so high-level that the external dependency becomes invisible.
- Reassess dependency risk whenever suppliers, model versions, or service boundaries change.
- Make sure operators know which failures require vendor escalation rather than only internal troubleshooting.

## Failure modes

- **ghost vendor**: a crucial supplier exists but is not named in public or internal governance records.
- **self-hosting theater**: a local deployment is treated as sovereign control even though the model provenance and limitations remain opaque.
- **contract-only oversight**: the institution can complain to the vendor but cannot actually inspect or control the critical behavior.
- **silent component swap**: a supplier or model changes without a refreshed assessment or public notice.
- **dependency amnesia**: teams track the main model but forget retrieval, moderation, transcription, or identity-related subcomponents.

## Practical tests

A dependency regime passes when it can answer yes to all of the following:

1. Can the institution name every material third-party model, API, and supplier in the service path?
2. Do public records make the major external dependencies legible for consequential systems?
3. Can the department obtain enough supplier information to meet transparency, appeal, and oversight duties?
4. Do supplier or model changes trigger governance refresh rather than only technical release notes?
5. Has the team rehearsed at least one substitution or degraded-mode continuity path?

## Compression rule for the archive

If an outside model or supplier can materially change outcomes, continuity, or evidence access, it is part of the **governed system**, even if the contract calls it only a service dependency.
