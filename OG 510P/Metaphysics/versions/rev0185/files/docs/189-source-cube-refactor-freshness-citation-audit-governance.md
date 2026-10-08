# Source-Cube Refactor, Freshness, Citation, and Audit Governance

Version: rev0184  
Date: 2026-05-26 01:08 UTC  
Boundary: local archive-governance, source-normalization, and cube-audit evidence only.

## Purpose

This layer audits and refactors the SourceCube. The prior cube exposed only a small set of source-anchor rows even though the archive already contained a much larger external crosswalk and a long source-citation document. Rev0183 therefore promotes source anchoring into a fuller local observation layer.

## What changed

rev0184 adds:

- `SOURCE_CROSSWALK_NORMALIZED.yml`, a normalized view of `EXTERNAL_CROSSWALK.yml` anchors.
- `SOURCE_CITATION_INDEX.yml`, a parsed local index of source-citation rows from `docs/05-source-citations.md`.
- `SOURCE_FAMILY_MAP.yml`, a count and examples map for source families.
- `SOURCE_RELATION_MAP.yml`, a local relation map for source-family membership, source-artifact anchoring, and repeated URL observations.
- `SOURCE_AUDIT_LEDGER.yml`, an audit surface for SourceCube row counts, missing URLs, repeated URLs, family coverage, and claim-boundary coverage.
- `CUBE/observations/source_relations.yml`, relation observations among local source identifiers, source families, and source artifacts.
- `CUBE/observations/source_audit.yml`, source-audit observations.
- `tools/generate_source_observations.py`, `tools/check_source_cube_refactor.py`, and `tools/check_source_audit.py`.

## Audit finding

The source layer had a representational mismatch: rich source evidence was present in the archive, but the cube-level source observations were under-specified. Rev0183 reduces that mismatch by making crosswalk anchors and source-citation rows queryable as local observations.

## Allowed claim language

rev0184 may claim that local source crosswalk, citation-index, source-family, source-relation, and source-audit surfaces are present and locally checked.

## Forbidden claim language

rev0184 does not claim source-currentness, live URL validation, legal citation sufficiency, external standards compliance, RDF publication, SHACL validation, WCAG conformance, FAIR compliance, source review by domain experts, or philosophical-source completeness.

## Remaining debt

The normalized source rows remain local metadata. The archive still lacks live source-watch automation, external domain review, citation-quality scoring, formal bibliography export, persistent identifiers for every source, and source-to-claim warrant grading.

## Next review triggers

A future revision is required if source rows are used as public bibliography claims, if any source is treated as conformance evidence, if live URL checking is added, if RDF/JSON-LD export is attempted, if source freshness becomes claim-critical, or if a source-to-claim warrant score is introduced.
