---
id: ss-0187-provenance-diff-services
revision_promoted: rev0187
title: Provenance-diff services become diligence infrastructure
constellation:
- managed-legibility
- standards-and-conformance
- operational-resilience
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- product identity / passports / traceability
- AI / model governance / automated decisions
- cybersecurity / software supply chain
- procurement / purchasing / offtake
bottleneck_type:
- change detection
- provenance / custody
- replayability / reconstructability
- state freshness
- fraud resistance
enforcement_surface:
- procurement / framework contract
- audit / attestation / assurance
- platform eligibility / ranking
- customs / market surveillance
artifact_type:
- provenance diff
- manifest diff
- lineage delta
- change receipt
lifecycle_stage:
- diff
- verify
- rely
- dispute
- correct
failure_modes:
- silent-mutation
- manifest-drift
- resolver-drift
- field-drop
- semantics-change
refactor_cluster:
- provenance-lineage
lineage_role: auditor-regulator and verifier-relying-party
lineage_stage:
- diff
- verify
- dispute
- correct
state_family:
- provenance
- freshness
state_terms:
- transform-declared
- normalization-loss-disclosed
- resolver-suspect
- provenance-disputed
consolidation_status: standalone-mechanism
evidence_grade: E2-signal-cluster
decision_grade: DG-B
decision_total: 15
source_refs:
- S1565
- S1568
- S1569
- S1567
- S1572
- S1574
---
# Provenance-diff services become diligence infrastructure

## Core claim

A provenance record is not enough if no one can tell what changed. As proof systems mature, buyers, auditors, regulators, platforms, insurers, and courts will ask not only for the current manifest, passport, BOM, content credential, model card, or data lineage record, but for a structured difference from the prior relied-on state.

**Provenance-diff services become diligence infrastructure** when change detection between evidence states becomes a paid and relied-on service: what source changed, what transform changed, what redaction changed, what signature changed, what resolver response changed, what field disappeared, what dependency was added, and what reliance consequence follows.

## Why this belongs in the archive

OpenLineage distinguishes runtime and design-time lineage events and supports extensible facets [S1568][S1569]. C2PA gives media content a manifest-like history of origin and edits [S1567]. SPDX provides a standard way to communicate BOM and provenance-related metadata [S1572]. GS1 resolver material shows that default links, linksets, identifier granularity, and resolver behavior can change over time [S1574][S1575].

Those systems generate histories. The missing market object is the diff: the intelligible change summary that tells a relying party whether the change matters.

## Speculative consequences worth tracking

### 1. Diligence moves from snapshots to deltas

Instead of reviewing a full new packet every time, counterparties may ask for a certified delta: no material source change, transform version changed, field dropped, resolver default changed, signature chain rotated, redaction expanded, or replay grade downgraded.

### 2. Diff thresholds become contract terms

Contracts may define materiality thresholds for provenance changes. A model-documentation change may trigger review if training data class changes, but not if a contact field changes. A product passport change may trigger resale notice if recall or repairability state changes, but not if consumer-facing language changes.

### 3. Silent mutation becomes a fraud pattern

Actors can keep an identifier stable while changing the underlying manifest, linkset, data source, model file, evidence schedule, or human-readable rendering. Provenance-diff services make silent mutation visible.

### 4. Diff tools become neutral witnesses

A diff service may become a broker between source issuers and relying parties, especially where the source system is opaque or where multiple parties disagree about what changed.

## Abuse and burden

Diff services can over-notify, creating alert fatigue and unnecessary review. They can also under-classify material semantic changes as minor field changes. Their own mapping logic becomes a new trust surface.

## Falsifiers

The thesis weakens if proof systems remain mostly static; if users rely on whole-document re-review rather than deltas; or if existing version-control, BOM, and registry systems provide enough change semantics without a specialized diligence layer.
