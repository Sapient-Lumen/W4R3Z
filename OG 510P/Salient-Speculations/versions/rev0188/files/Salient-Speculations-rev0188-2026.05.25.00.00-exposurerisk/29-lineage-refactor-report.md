# Lineage Refactor Report

rev0187 audits and refactors the cube's provenance, custody, transformation, resolver, traceability, and lineage layer.

## Audit target

The target cluster included dossiers that used any of the following as central mechanisms:

- source-object identity;
- source snapshots and witness availability;
- transformation-code escrow;
- normalization loss and semantic translation;
- report signatures and trust chains;
- hybrid wrappers and authoritative renderings;
- redaction-boundary ledgers;
- resolvers and product-passport routing;
- product biographies and traceability;
- delivery, legacy-status, and reliance-grade attestations;
- content provenance nonparticipation labels;
- replay quality and history-retention floors;
- compliance-object forgery and graph poisoning.

## Existing dossiers tagged

The audit tagged the core family with `refactor_cluster: provenance-lineage` and added `lineage_role`, `lineage_stage`, and `state_family: provenance` metadata.

The most important existing members are:

- `source-object-identity-warranties-become-broker-liability-caps.md`
- `source-snapshot-escrow-becomes-liability-tail-infrastructure.md`
- `transformation-code-escrow-becomes-packet-custody.md`
- `normalization-loss-warranties-become-diligence-language.md`
- `renewal-history-normalization-services-become-a-quiet-broker-market.md`
- `extension-lineage-disclosures-become-diligence-exhibits.md`
- `report-signature-trust-chains-become-interoperability-bottlenecks.md`
- `hybrid-wrapper-formats-become-durable-compromise-objects.md`
- `authoritative-rendering-services-become-evidentiary-choke-points.md`
- `resolver-capture-becomes-a-hidden-passport-bottleneck.md`
- `redaction-boundary-ledgers-become-ai-assurance-controls.md`
- `objects-acquire-governed-biographies.md`
- `provenance-nonparticipation-labels-become-media-trust-infrastructure.md`
- `measurement-traceability-becomes-governance-infrastructure.md`
- `reliance-grade-source-attestations-become-a-service-tier.md`
- `source-witness-nonresponse-defaults-become-broker-policy.md`
- `compliance-object-forgery-becomes-organized-fraud-infrastructure.md`

## What the audit found

### 1. Provenance was being used at three levels at once

Some dossiers meant provenance as **origin**. Others meant **transformation history**. Others meant **custody and routing**. Still others meant **public trust marker**. The refactor separates those into lifecycle stages.

### 2. Resolver governance was under-modeled

`resolver-capture` correctly named the hidden bottleneck, but not the continuity machinery that follows: successor maps, fallback resolvers, service-provider insolvency, default-link takeover, serial/batch granularity, archived linksets, and historical view obligations.

### 3. Replay sufficiency was implicit

The archive had source snapshots and transformation-code escrow, but it lacked a dossier for the actual audit object: a replay bundle sufficient to reconstruct a relied-on state.

### 4. Rights travel through lineage

AI documentation, data spaces, content credentials, product passports, and supplier evidence all reveal the same problem: the question is not merely what data exists, but what derived data may be used for after transformation, aggregation, redaction, or model training.

### 5. Custody breaks need a name

Many proof systems will have gaps: human rekeying, missing logs, broken signature chains, outsourced conversion, unverifiable source-state retention, redaction without boundary evidence, resolver migration, or service-provider failure. Treating these as generic caveats hides the important thing. A custody break should become a typed evidence state.

## New dossiers added because of the audit

### 1. Resolver-successor maps

Existing resolver dossiers explained capture. The new dossier explains continuity after vendor failure, acquisition, registry migration, domain loss, service-provider certification change, issuer exit, or default-link takeover.

### 2. Transformation-replay bundles

Existing dossiers captured source snapshots and code escrow. The new dossier models the complete replay package: inputs, transforms, environment, parameters, mappings, outputs, logs, and sufficiency grade.

### 3. Derived-data use rights

Existing AI and data-space dossiers documented governance packets. The new dossier adds the contractual object that says what derived datasets, embeddings, model weights, features, outputs, summaries, and redacted forms may be used for.

### 4. Provenance-diff services

Existing lineage files were mostly static. The new dossier models diffing between manifests, source states, resolver responses, product passports, C2PA assertions, BOMs, or model documentation versions.

### 5. Custody-break certificates

Existing dossiers often treated custody gaps as failure. The new dossier treats declared break state as an artifact: a certificate that says what broke, what remains trustworthy, what reliance class is prohibited, and what remedy is available.

## Consolidation decisions

- Do **not** merge source-object identity, source-snapshot escrow, transformation-code escrow, normalization-loss warranties, and resolver capture. They are different lifecycle stages.
- Do merge future narrow examples into the lineage lifecycle unless they introduce a new subject-binding, transform, resolver, redaction, replay, or custody-break mechanism.
- Treat `provenance` as too broad for unqualified use. Future dossiers should specify origin, custody, transform, route, signature, redaction, diff, replay, or archive.
- Treat `traceability` as insufficient unless the trace affects market access, liability, audit, repair, resale, customs, procurement, litigation, or scientific reproducibility.

## Metadata changes

Affected dossiers now use:

- `refactor_cluster: provenance-lineage`
- `lineage_role`
- `lineage_stage`
- `state_family: provenance`
- `state_terms`

This allows the index to answer questions such as:

- Which dossiers concern source capture?
- Which concern transformation and normalization loss?
- Which concern resolver routing and successor state?
- Which concern redaction and minimization?
- Which concern replay sufficiency?
- Which provenance failures are also remedy failures?
- Which provenance failures are also freshness or authority failures?

## Anti-overfit warning

Do not promote every new C2PA implementation, product-passport pilot, SBOM field, dataset-card field, or QR-code resolver into a dossier. The cube should promote only the bottleneck:

- who controls the source state;
- what transformation happened;
- whether a verifier can replay it;
- how a resolver or wrapper can misroute or diverge;
- what was redacted or withheld;
- which rights survived derivation;
- how custody breaks are disclosed and priced.

## Next refactor candidates

After lineage, the next overloaded clusters appear to be:

1. **scope / comparability / translation** — semantic equivalence, taxonomy mapping, mutual recognition, and not-quite-the-same states;
2. **fallback / graceful degradation** — when live checks fail and institutions must decide whether to stop, cache, accept paper, or proceed under risk;
3. **small-actor burden** — when evidence requirements exclude small suppliers, households, informal workers, and local agencies;
4. **issuer / registry governance** — who is allowed to publish, revoke, suspend, canonicalize, or certify proof objects.
