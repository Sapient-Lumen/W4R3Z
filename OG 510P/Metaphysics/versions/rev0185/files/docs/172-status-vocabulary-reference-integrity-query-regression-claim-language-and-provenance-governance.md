# 172. Status Vocabulary, Reference Integrity, Query Regression, Claim Language, and Provenance Governance

## Core thesis

A query that runs is not yet a query that is regression-protected. A status code that appears is not yet a controlled vocabulary. A path-like string is not yet a checked reference. A repeated warning is not yet a claim-language ledger. A manifest hash is not yet provenance.

Rev0165 made the archive more cube-like by adding a canonical control stack, a cube index, current full-profile records, and schema-conformance checks. Rev0166 adds the next layer: the vocabulary, reference, query, claim-language, and provenance controls needed for the cube to resist silent drift.

## What this release adds

Rev0166 adds five local control surfaces:

1. `STATUS_VOCABULARY.yml` names the local code families used by current governance records and forbids treating free text as a status class.
2. `REFERENCE_MAP.yml` records a local path-level reference scan for front doors, current records, and governance artifacts.
3. `QUERY_REGRESSION_SUITE.yml` states which local cube queries must continue to run and what minimal evidence they must return.
4. `CLAIM_LANGUAGE_LEDGER.yml` separates allowed local claims from forbidden upgrade claims.
5. `PROVENANCE_LEDGER.yml` records local entities, activities, agents, and relations without claiming cryptographic attestation or external supply-chain compliance.

The new rule is simple: every governance assertion should be either a checked vocabulary token, a checked reference, a queryable row, a claim-language entry, a provenance relation, or an explicitly declared debt.

## Allowed claims after rev0166

The archive may claim that the rev0166 package contains local current-record required-field conformance, control-stack continuity through step 172, current-release cube observations, a local status vocabulary, a local reference-integrity pass over declared surfaces, a local query-regression suite and report, a claim-language ledger, a provenance ledger, and a fresh-extraction validation transcript produced by the local validator.

## Forbidden upgrade claims

The archive must not claim RDF Data Cube publication, DCAT catalog publication, RO-Crate conformance, Frictionless Data Package conformance, JSON Schema conformance, SHACL validation, PROV-O compliance, SKOS publication, FAIR compliance, ISO/BFO/DOLCE/OBO conformance, SLSA level achievement, in-toto attestation, SPDX SBOM production, Datasheets or Model Cards completion, NIST AI RMF compliance, public CI, public issue tracking, public query service, source-watch automation, external audit, public monitoring, domain authority, or operational deployment readiness.

## Status-vocabulary rule

Status tokens are not ornamental. If a current record uses a token such as `CAP5`, `SC4`, `DC7`, `QRY7`, `VOC4`, `REF4`, `CL4`, or `PRV3`, the token must be listed in `STATUS_VOCABULARY.yml`. Prose may explain a status, but prose may not create a new status class.

The near-term debt is that historical records are not migrated into normalized status objects. Current records are checked; old prose is preserved.

## Reference-integrity rule

Reference integrity in rev0166 is local and path-level only. A checked reference means that a path-like string in a declared local surface resolves to a package file. It does not mean that the referenced file is semantically sufficient, externally current, or authoritative.

## Query-regression rule

A cube query is not stable unless a later release can prove that the query still runs and returns minimum expected evidence. The suite is intentionally small. It tests observations, schema, control stack, source artifacts, debt language, forbidden language, capacity status, vocabulary, references, claims, provenance, and regression reports.

## Claim-language rule

The archive now treats claim language as a governed artifact. Allowed local claims are stored separately from forbidden upgrade claims. This blocks compliance laundering, audit laundering, source-currency laundering, and deployment laundering.

## Provenance rule

The provenance ledger is local build provenance. It records source package, derived package, generated artifacts, activities, agents, and relations. It is not signed, not independently witnessed, not reproducible from a public repository, and not an in-toto, SLSA, SPDX, or PROV-O attestation.

## Open debt intentionally retained

- Status scalars are not yet normalized across all historical records.
- Reference integrity checks only declared local surfaces and local paths.
- Query regression is minimal and local.
- Provenance is unsigned local custody evidence.
- External standards are used as analogy and design pressure only.
- There is no public CI, public issue tracker, public query endpoint, public source-watch service, or independent audit.
- No script proves metaphysical truth, domain correctness, policy readiness, or operational safety.

## Next likely layer

The next durable layer should be source-evidence and claim-graph governance: claim nodes, evidence packets, source anchors, freshness windows, contradiction states, and source-withdrawal propagation. Rev0166 prepares for that by making status, reference, query, claim, and provenance claims explicit enough to be queried and contradicted.
