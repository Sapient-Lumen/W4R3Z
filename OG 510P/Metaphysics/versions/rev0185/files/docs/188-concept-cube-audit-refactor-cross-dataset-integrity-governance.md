# Concept-Cube Audit, Refactor, Cross-Dataset Integrity Governance

Version: rev0182  
Date: 2026-05-25 23:32 UTC  
Boundary: local archive-governance and cube-integrity evidence only.

## Purpose

This layer turns the rev0181 ConceptCube from a small illustrative sample into a broader numbered-document concept inventory. It also adds relation observations and audit observations so the cube can ask not only whether a concept row exists, but how concept rows connect, what dataset checks have been run, and where local-only debt remains.

## What changed

rev0182 adds:

- `CONCEPT_FAMILY_MAP.yml`, a local routing map from numbered-document ranges to concept families and subfamilies.
- `CONCEPT_RELATION_MAP.yml`, a local relation map for sequential, family, and selected dependency edges.
- `CUBE_AUDIT_LEDGER.yml`, a local audit ledger for cube dataset shape, row counts, duplicate IDs, source-artifact existence, and refactor limits.
- `CUBE/observations/concept_relations.yml`, relation observations among local concept identifiers.
- `CUBE/observations/cube_audit.yml`, audit observations for each cube dataset.
- `tools/generate_concept_observations.py`, `tools/check_concept_cube_refactor.py`, and `tools/check_cube_audit.py`.

## Allowed claim language

rev0182 may claim that local concept, relation, and cube-audit observation surfaces are present and locally checked.

## Forbidden claim language

rev0182 does not claim a complete formal ontology, external philosophical review, RDF/SHACL publication, public endpoint availability, WCAG conformance, reader comprehension, legal compliance, or semantic correctness guarantee.

## Audit finding

The refactor improves coverage and queryability, but it intentionally remains a local map. Concept IDs, family assignments, and relation edges are provisional routing aids. They should be treated as reviewable hypotheses, not as settled metaphysical taxonomy.

## Next review triggers

A future revision is required if any concept-family assignment becomes a public teaching route, if relation edges are cited as formal entailments, if RDF/JSON-LD publication is attempted, if external review is performed, or if reader/comprehension tests produce evidence that changes the concept inventory.
