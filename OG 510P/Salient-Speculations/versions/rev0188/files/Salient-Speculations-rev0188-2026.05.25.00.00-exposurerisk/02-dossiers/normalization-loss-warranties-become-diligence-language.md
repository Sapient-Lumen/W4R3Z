---
id: ss-migrated-normalization-loss-warranties-become-diligence-language
revision_promoted: pre-rev0182
migration_status: inferred-rev0182-targeted
title: Normalization-loss warranties become diligence language
constellation:
- managed-legibility
status: dossier
maturity: S2-artifact-emerging
confidence: medium
time_horizon: near
domain:
- standards / interoperability / conformance
- procurement / purchasing / offtake
bottleneck_type:
- interoperability translation
- recipient-scope precision
enforcement_surface:
- procurement / framework contract
- underwriting / insurance renewal
- audit / assurance engagement
artifact_type:
- correction record
- state label
lifecycle_stage:
- publish
- rely
- correct
- restate
failure_modes:
- semantic-loss
- noncomparability
source_refs:
- S1367
- S1368
- S1369
- S1370
- S1371
- S1372
- S1373
- S1374
- S1375
- S1376
- S1377
refactor_cluster:
- provenance-lineage
- exposure-liability
lineage_role: transformer-broker and verifier-relying-party
lineage_stage:
- transform
- verify
- rely
state_family:
- provenance
- exposure
state_terms:
- normalization-loss-disclosed
- transform-declared
- warranty-breached
- trigger-disputed
- indemnity-chain-mapped
consolidation_status: state-family-member
exposure_role: transformer-broker and buyer
exposure_stage:
- condition
- classify
- subrogate
---
# Normalization-loss warranties become diligence language

## Core claim

Once renewal-history brokers start converting native exception histories, audit logs, policy-exemption records, POA&M items, security findings, ticket changelogs, advisory statuses, and VEX context into buyer-facing packets, the scarce thing is no longer only the packet. It becomes the enforceable statement about **what happened during normalization**. A counterparty will not only ask, “what is the current residue history?” It will ask whether original fields were preserved, inferred, deduplicated, downgraded, widened, narrowed, omitted, or declared non-comparable. At that point, semantic-loss maps stop being internal engineering notes and become diligence schedules, indemnity carve-outs, procurement exhibits, and broker liability boundaries. In that world, **normalization-loss warranties become diligence language**.

## Why this belongs in the archive

The archive now has two adjacent layers. **Translation-loss proofs become an audit surface** explains why cross-engine policy translation needs evidence of preserved, tightened, weakened, reordered, and unresolved semantics. **Renewal-history normalization services become a quiet broker market** explains why raw renewal, extension, remediation, and exception histories need a cross-tool broker layer. The missing step is contractual: once those packets are relied on in deals, underwriting, procurement, and supervisory review, someone has to warrant the normalized representation.

The source signals are strong because multiple technical communities already treat mapping as a graded, context-dependent act rather than a neutral copy. HL7 FHIR’s ConceptMap resource describes mappings as one-way, context-dependent relationships; it says reverse mappings cannot be assumed, allows multiple possible mappings, includes a relationship element for semantic correspondence, permits `noMap`, and distinguishes ConceptMap relationship assertions from executable StructureMap transforms [S1367]. The W3C SKOS Primer similarly distinguishes exact, inexact, partial, broader, narrower, and single-to-multiple mapping cases, and notes that `skos:exactMatch` and `skos:closeMatch` separate perfect semantic equivalence from equivalence that may be acceptable only for a given application [S1368]. Those are not exotic edge cases. They are the normal structure of translation when domains do not share one ontology.

The provenance layer is also already standardized. W3C PROV frames provenance as information about entities, activities, and people involved in producing data, and says it can support assessments of quality, reliability, or trustworthiness; it also emphasizes derivation, versioning, reproducibility, and representation of procedures [S1369]. That is almost exactly the burden a normalization-loss warranty would have to carry: not merely that a packet exists, but who transformed what, using which procedure, from which source objects, into which result, and under which version.

Control and security-data ecosystems show why this matters in diligence. NIST’s OSCAL profile-resolution process includes explicit import, merge, and modify phases; the modify phase can set parameters and alter controls, while tools must continue processing even when certain expected targets are missing, with warnings in some cases [S1370]. AWS Security Lake requires custom sources to convert logs and events to OCSF and meet source requirements such as Parquet format, event-class consistency, partitioning, ordering, time conversion, and validation against OCSF compatibility [S1371]. AWS’s own OCSF transformation guidance then turns the mapping act into a concrete workflow: understand the schema, identify log sources, match events to categories and classes, map fields, handle unmapped objects, enrich data, test and validate, correct misalignments, and rerun until the output is valid [S1372].

Data-lineage and validation systems point in the same direction. OpenLineage facets attach contextual metadata to runs, jobs, and input/output datasets, and custom facets require versioned schema URLs that should be immutable pointers rather than branch references [S1373]. Its object model is built around observing datasets as they are created and transformed, including runtime and design-time lineage events [S1374]. JSON Schema defines assertions about what a valid JSON document must look like, while SHACL defines validation reports, conformance results, focus nodes, result paths, values, source shapes, constraint components, details, messages, and severity for RDF graph validation [S1375][S1376]. dbt’s data tests similarly frame tests as assertions about models, sources, seeds, and snapshots; failing records disprove the assertion, and custom tests can encode organization-specific business logic [S1377].

Together, these sources point to the next bottleneck: **normalization is now evidence-bearing work**. The broker can no longer plausibly say, “we mapped the histories into our schema.” It must say which mappings were exact, which were close enough for the specified reliance purpose, which were broader or narrower than the source meaning, which were inferred from comments or transitions rather than source-native states, which were dropped because there was no target field, which were preserved only as unmapped payload, which were deduplicated under a named replay rule, and which were excluded because the source retention window made the history incomplete.

That is why the thesis belongs here. The important artifact is not a nicer dashboard. It is a **loss-bearing warranty schedule**: a buyer-readable and machine-checkable statement that makes semantic loss visible enough to be priced, accepted, excluded, cured, or disputed.

## Speculative consequences worth tracking

### 1. Warranties attach to crosswalks, not just outputs

Diligence language may stop warranting only that “the attached report is accurate” and start warranting that the mapping table, transformation version, source-object joins, date handling, duplicate-suppression logic, and non-comparable-state labels are complete for the stated reliance purpose.

### 2. “Exact or stricter” becomes the safest representation

Borrowing from migration-grade logic elsewhere in the archive, parties may accept normalized packets without further waiver only when every critical field is exact, source-preserved, or stricter than the source. Weaker, inferred, close-match, or broader/narrower translations may require disclosure, buyer approval, or a price holdback.

### 3. Non-comparable becomes a negotiated category

A broker that labels a native state as non-comparable is making a consequential claim. Sellers may want non-comparable fields excluded from breach calculations. Buyers may treat them as missing evidence. Brokers may insist that non-comparability is a warranted finding, not a defect.

### 4. Source-object identity becomes the warranty core

The most valuable and dangerous representation may be that several source objects describe the same underlying obligation. If a POA&M item, Jira ticket, scanner finding, GitHub alert, cloud finding, and risk-acceptance record were wrongly joined, the normalized packet may be coherent and false. Identity-match confidence may become the warranty’s most contested schedule.

### 5. “Unmapped but retained” becomes different from “omitted”

OCSF-style unmapped objects, SKOS-style close/broad/narrow mapping, and FHIR-style `noMap` all suggest a distinction between loss that is declared and loss that is hidden. Diligence may prefer retained-but-unmapped payload over silent omission because the former can still be inspected later.

### 6. Validation reports become closing artifacts

Schema conformance, SHACL reports, data-test outputs, and transformation-run metadata may travel with the packet. A buyer may not want to rerun the whole transformation before signing, but it may want the validation results, failed-record counts, warning list, and test version as part of the file.

### 7. Transformation-code custody becomes deal hygiene

If a normalized packet is warranted, the transformation recipe matters. The code, mapping CSV, schema version, lookup table, enrichment rule, timezone policy, and replay seed may need to be deposited with the data room, retained by the broker, or escrowed so disputes can be re-run later.

### 8. Brokers start disclaiming reliance purposes

A mapping that is acceptable for dashboard triage may be unacceptable for insurance pricing, acquisition diligence, regulatory self-disclosure, or payment holdback. Warranty language may become reliance-specific: exact enough for portfolio risk scoring, not exact enough for item-level breach remedies.

### 9. Native vendors become fact witnesses

Source platforms may be pulled into disputes over what their native states meant at the time of export. If the broker mapped “dismissed,” “accepted risk,” “false positive,” “superseded,” or “expired” more harshly than the native vendor’s UI implied, the vendor’s documentation, audit logs, and support statements may become evidence.

## Likely artifact shape

The mature artifact probably looks like a **normalization-loss warranty schedule** attached to a normalized renewal-history packet. A minimum useful schedule would include:

- **Reliance purpose** — procurement, insurance, lending, M&A diligence, supervisory review, internal audit, payment holdback, or remediation covenant monitoring.
- **Source inventory** — each native system, endpoint, table, export, report, schema version, retention window, and extraction timestamp used.
- **Source-object identity matrix** — source identifiers, join keys, confidence levels, collision handling, split/merge rules, and records intentionally not joined.
- **Field-preservation table** — exact, exact-but-renamed, normalized-format-only, unit-converted, timezone-converted, retained-as-unmapped, omitted, or not available.
- **Semantic-equivalence map** — exact, close, broader, narrower, stricter, weaker, inferred, source-only, non-comparable, and no-map labels for each material state.
- **Inference register** — every normalized fact derived from comments, ticket transitions, timestamps, labels, repeated identifiers, or absence of a target record rather than a native source field.
- **Duplicate and replay policy** — how repeated events, at-least-once delivery, backfilled rows, late-arriving updates, and event-order conflicts were handled.
- **Retention-loss disclosure** — oldest queryable event, oldest still-verifiable source artifact, known gaps, expired retention windows, and history asserted from secondary evidence.
- **Validation packet** — schema checks, SHACL or equivalent reports, data-test results, failed-record counts, warnings, and accepted exceptions to validation.
- **Transformation recipe** — mapping files, code version, configuration, schema version, enrichment sources, clock policy, and reproducible run metadata.
- **Materiality threshold** — which losses are immaterial, which trigger buyer notice, which require approval, and which invalidate the packet for a specific reliance purpose.
- **Warranty and carve-out text** — what the broker, seller, auditor, or operator warrants; what is merely represented based on supplied source data; and what is expressly excluded.
- **Cure path** — how a disputed mapping is challenged, who re-runs it, whether source-native evidence overrides normalized evidence, and whether revised packets retroactively affect pricing or eligibility.

This artifact matters because it turns normalization from a hidden ETL step into a negotiable institutional object. It lets a buyer accept a packet without pretending that semantic loss disappeared. It lets a seller disclose hard-to-map states without conceding that every non-comparable field is a breach. And it lets the broker define its liability around the actual transformation performed rather than around a vague claim of comparability.

## What could falsify or weaken the thesis

- Buyers continue accepting simple dashboards, screenshots, current-state attestations, or aggregate scores without asking how normalized fields were created.
- Native platforms converge fast enough on shared state taxonomies that lossy crosswalks become rare.
- Brokers absorb loss internally and refuse to publish loss schedules because doing so increases liability more than it increases trust.
- Legal teams treat normalization as background analytics rather than as a representation on which contracts, holdbacks, insurance pricing, or procurement eligibility depend.
- Source-system export limits, retention windows, and license restrictions prevent enough replay to make warranties meaningful.
- Standards bodies define strict canonical mappings for the important fields, leaving little room for negotiated warranties.
- The market values speed and cheapness over defensible comparability, keeping normalization-loss disclosures as premium artifacts rather than default diligence language.

## Research queue

- Which buyer asks for normalization-loss schedules first: cyber insurers, acquirers, banks, government procurement offices, prime contractors, or auditors?
- Which field produces the first serious warranty dispute: reopened versus duplicate, risk accepted versus false positive, due-date edit versus extension, closure versus supersession, or unmapped retained payload versus omission?
- Does the warranty attach to the broker, the seller, the source-system vendor, the auditor, or the operator that supplied the native export?
- Which equivalence labels become standard enough for deal language: exact, close, broader, narrower, stricter, weaker, inferred, non-comparable, retained-unmapped, and omitted?
- Do validation reports become enough, or do buyers demand transformation-code custody and replay rights?
- How do warranties treat retention gaps: as known limitations, seller breaches, broker carve-outs, or price haircuts?
- Do brokers publish conservative mappings to reduce liability, or buyer-friendly mappings to win trust even when they upset source vendors?
