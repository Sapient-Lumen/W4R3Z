---
id: ss-0188-indemnity-pass-through-maps
revision_promoted: rev0188
title: Indemnity pass-through maps become supply-chain risk infrastructure
constellation:
- managed-legibility
- standards-and-conformance
- market-and-state-capacity
status: dossier
maturity: S2-artifact-emerging
confidence: medium-high
time_horizon: near
domain:
- software / AI / digital products
- product identity / passports / traceability
- procurement / purchasing / offtake
- insurance / risk transfer / underwriting
bottleneck_type:
- liability allocation
- indemnity chain
- source-of-truth precedence
- underwritability
enforcement_surface:
- procurement / framework contract
- litigation / discovery
- underwriting / insurance renewal
- product liability
artifact_type:
- indemnity map
- supplier responsibility matrix
- liability pass-through exhibit
- control allocation schedule
lifecycle_stage:
- allocate
- attach
- condition
- trigger
- subrogate
- renew
failure_modes:
- orphan-risk
- nonresponsive-protection
- supplier-insolvency
- wrong-fault-class
- tail-gap
refactor_cluster:
- exposure-liability
- provenance-lineage
exposure_role: buyer-supplier-carrier chain
exposure_stage:
- allocate
- attach
- condition
- subrogate
- renew
lineage_role: verifier-relying-party and rights-holder
lineage_stage:
- identify
- transfer
- verify
- archive
state_family:
- exposure
- provenance
state_terms:
- allocated-by-contract
- indemnity-chain-mapped
- subrogation-preserved
- tail-open
- source-bound
consolidation_status: standalone-mechanism
evidence_grade: E3-artifact-live
decision_grade: DG-A
decision_total: 16
source_refs:
- S1577
- S1578
- S1582
- S1572
- S1573
---
# Indemnity pass-through maps become supply-chain risk infrastructure

## Core claim

As liability attaches to software, AI systems, digital product elements, updates, documentation, conformity evidence, and product biographies, large buyers will discover that ordinary indemnity clauses are too flat. The important question becomes **whether responsibility can be traced through the chain of suppliers, maintainers, integrators, platform operators, data providers, certifiers, and brokers whose artifacts produced the relied-on state**.

The stronger thesis is that indemnity pass-through maps become supply-chain infrastructure. A buyer will not merely ask for an indemnity. It will ask for a map of which supplier is responsible for which component, update, data source, transformation, warranty, documentation object, defect class, cybersecurity control, recall state, and proof failure.

## Why this belongs in the archive

The new EU Product Liability Directive explicitly brings digital products, software, and AI systems into the product-liability frame, includes defects that become apparent after release because of updates, upgrades, or machine-learning features, and creates evidence-access mechanisms in litigation [S1577]. That matters because software and AI products are not single-factory objects. They are layered supply chains of code, models, datasets, APIs, services, wrappers, monitoring obligations, and update flows.

The archive has already modeled source-object identity, transformation replay bundles, derived-data use rights, custody-break certificates, and product biographies. But those objects still need a financial routing layer: if the passport, model card, SBOM, credential, attestation, or update channel is wrong, who pays?

An indemnity pass-through map is the liability analogue of a dependency graph. It records not only technical dependency but contractual responsibility, insurance availability, limitations of liability, evidence duties, and tail duration.

## Map contents

A serious pass-through map includes:

- supplied component, service, model, dataset, connector, or documentation object;
- responsible legal entity and successor entity;
- contract governing the layer;
- indemnified loss classes;
- exclusions and caps;
- required insurance or financial assurance;
- warranty survival period;
- update and monitoring obligations;
- evidence retention obligation;
- source-witness and cooperation duties;
- subrogation and recovery rights;
- insolvency or nonresponsive-supplier fallback.

## Speculative consequences worth tracking

### 1. Procurement starts asking for liability topology

Buyers may require a machine-readable responsibility matrix before accepting high-risk AI, software, cyber, or product-passport systems.

### 2. Supplier caps become graph constraints

A low limitation-of-liability cap at one supplier may reduce the value of the entire upstream indemnity chain, especially if that supplier controls a high-impact proof object.

### 3. Insurance evidence becomes supplier-specific

A generic certificate of insurance will not be enough. Buyers may ask whether the relevant loss class, component, update, territory, and product generation are actually covered.

### 4. Successor maps become financial, not only technical

If a supplier is acquired, liquidated, spun out, or replatformed, the map must show whether indemnity, evidence, and cooperation duties survive.

## Abuse and burden

Pass-through maps can become a way for large buyers to push uninsurable liability onto small suppliers. They can also become fake comfort if the map records contractual promises without checking insurance, solvency, caps, and evidence-retention capability.

## Falsifiers

The thesis weakens if digital-product liability remains centered on one obvious manufacturer; if buyers keep accepting generic indemnities without component-level mapping; or if insurers refuse to underwrite based on liability topology.
