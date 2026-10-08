---
id: ss-0182-graph-poisoning
revision_promoted: rev0182
title: Graph poisoning becomes a standing governance attack surface
constellation:
- managed-legibility
- anti-legibility
- model-governance
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- cyber / software supply chain / vulnerability governance
- organizational identity / entity resolution
- compute / AI / data centers
- procurement / purchasing / offtake
bottleneck_type:
- identity matching
- fraud resistance
- provenance / custody
- source-of-truth precedence
enforcement_surface:
- procurement / framework contract
- platform eligibility
- security scanner / admission controller
- underwriting / insurance renewal
artifact_type:
- recipient graph
- registry entry
- source snapshot
- audit log
- reason code
lifecycle_stage:
- source
- capture
- normalize / transform
- validate
- dispute
failure_modes:
- graph-poisoning
- subject-mismatch
- dependency-confusion
- synthetic-remediation
- malicious-edge-insertion
---
# Graph poisoning becomes a standing governance attack surface

## Core claim

As more institutional systems depend on entity graphs, dependency graphs, product graphs, vulnerability graphs, recipient graphs, relation graphs, address graphs, supplier graphs, knowledge graphs, and model-context graphs, attackers will stop aiming only at records. They will attack the **edges**.

That is the speculative claim: **graph poisoning becomes a standing governance attack surface**. A forged document is bad; a poisoned graph is worse because it can cause many downstream systems to make correct-looking decisions from corrupted relations. The attack may not be “make a fake supplier.” It may be “make the real supplier appear connected to the wrong product, package, facility, remediation, recall, owner, vulnerability, appeal, or credential.”

The archive already has dossiers on source-object identity warranties, identity-match appeals, amendment-recipient registries, scanner-ingestion scoreboards, public replay matrices, source hierarchies, model documentation packets, and compliance-object forgery. All of them become more fragile once relation graphs are treated as operational truth.

## Why this belongs in the archive

Security practice already treats poisoning as a real class of attack. OWASP's LLM materials name training-data poisoning, data/model poisoning, and supply-chain vulnerabilities as major risks for LLM and generative AI applications [S1506]. MITRE ATLAS catalogs adversarial threats to AI-enabled systems, including poisoning-style attacks and supply-chain manipulation [S1507]. CISA alerts around npm ecosystem and package compromises show that trusted dependency systems are practical attack surfaces, not theoretical worries [S1508][S1509].

The archive's contribution is to generalize that logic beyond AI training data and software dependencies. The same pattern appears wherever a relation graph becomes admissible evidence.

A poisoned supplier graph may misroute EUDR due-diligence obligations. A poisoned product graph may attach a clean passport to the wrong batch. A poisoned vulnerability graph may show a package lineage as fixed when it is not. A poisoned recipient graph may hide who must receive a correction. A poisoned identity graph may merge two people, two companies, two facilities, or two repair histories. A poisoned model-context graph may cause a retrieval system to cite hostile or planted material as authoritative.

## Speculative consequences worth tracking

### 1. Edge provenance becomes as important as node provenance

It will not be enough to know that a supplier, product, model, package, or credential is real. Institutions will need to know who asserted the relationship, when it was asserted, through which transform, from which source, under which confidence level, and whether that edge was inferred, imported, self-declared, certified, appealed, or manually overridden.

### 2. Graph-diff review becomes a control surface

Large changes to relation graphs may trigger review: sudden new dependencies, supplier rewiring, bulk subject merges, unexpected recipient removals, new package ancestry, new facility links, new model-data associations, or many edges added by a previously quiet actor.

### 3. Identity-match appeals become graph appeals

A person or firm may not dispute the existence of a record. They may dispute the relation: this product is not ours; this vulnerability does not apply to this fork; this credential is not for this role; this repair event is not this unit; this address is not this facility; this data source is not this model.

### 4. Poisoning creates quiet liability tails

Bad edges may remain in historical views, training sets, buyer dashboards, conformance registries, insurance applications, and platform scores long after the visible record has been fixed. Correction systems must repair both the graph and the downstream decisions that relied on the graph.

### 5. Graph firebreaks become governance tools

Systems may introduce confidence tiers, isolated staging graphs, edge quarantine, trust-bounded joins, source-specific overlays, and recipient-specific views so a poisoned edge cannot automatically infect every downstream decision.

## How this gets abused

- Competitors plant misleading relation edges to damage eligibility or increase diligence cost.
- Sellers create synthetic remediation chains that make old vulnerabilities appear fixed.
- Attackers publish packages, records, or documents that exploit automated relation inference.
- Brokers overstate confidence in inferred joins to reduce manual review cost.
- Platforms hide appealable edge logic behind proprietary ranking systems.
- Buyers use graph uncertainty to demand broader disclosures or price concessions.

## Who pays, who saves, who captures

Graph owners pay for edge provenance, anomaly detection, and appeal handling. Buyers and insurers save when graph confidence is visible enough to price risk. Vendors that can certify graph-diff hygiene and edge provenance capture value. Small actors may be harmed if they cannot see or challenge the edges that determine their score or eligibility.

## Near misses

- Bad data is not always graph poisoning. The distinctive feature is corrupted relationship structure.
- A duplicate record is not graph poisoning unless the duplicate changes a relation or downstream reliance.
- A model hallucination is not graph poisoning unless a poisoned source or relation is influencing retrieval or training.
- A supply-chain compromise is not automatically graph poisoning; it becomes graph poisoning when dependency, provenance, or trust relations are manipulated.

## Falsifiers

The thesis weakens if operational systems remain node-centric; if relation graphs are used only for internal analytics; if downstream eligibility does not depend on edges; if manual review catches most consequential joins; or if edge provenance becomes cheap, universal, and reliable enough that poisoning attempts are rapidly contained.

## Signals to watch

- Edge-level provenance fields in registries, passports, SBOM/VEX systems, and AI data documentation.
- Appeal workflows specifically for subject relationships, not only record content.
- Graph anomaly products sold into procurement, compliance, security, and underwriting.
- Contract language around inferred joins, source-declared edges, manual overrides, and graph-diff notification.
- Incident reports involving poisoned dependency, identity, supplier, or retrieval graphs.
