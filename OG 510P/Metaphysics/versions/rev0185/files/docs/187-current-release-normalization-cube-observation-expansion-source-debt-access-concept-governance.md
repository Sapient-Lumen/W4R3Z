# Current-release normalization, cube observation expansion, source/debt/access/concept governance

Version: rev0181  
Date: 2026-05-25 21:34 UTC  
Codename: current-release-normalization-cube-observation-expansion

## Purpose

This revision repairs a release-currentness defect and turns the archive's datacube from a single conformance-heavy index into a set of local analytic datasets. The immediate problem was simple: the package had a current rev0180 validator and records, but the public front door still began with older revision language. The deeper problem was structural: the cube could show that records existed and required fields were present, but it could not yet expose debt, source freshness, access evidence, concept coverage, or current-release identity as first-class observations.

Rev0181 therefore adds `CURRENT_RELEASE.yml`, splits cube observations under `CUBE/`, adds source/debt/access/concept ledgers, adds packaging metadata boundaries, and adds current-release and stale-token checkers. The goal is not to claim standards compliance. The goal is to make the archive's own limits easier to find, query, and preserve.

## New artifacts

- `CURRENT_RELEASE.yml`
- `CUBE/datasets.yml`, `CUBE/dimensions.yml`, `CUBE/measures.yml`, `CUBE/attributes.yml`
- `CUBE/observations/artifacts.yml`, `claims.yml`, `debts.yml`, `controls.yml`, `sources.yml`, `access.yml`, `concepts.yml`
- `SOURCE_ANCHOR_LEDGER.yml`, `SOURCE_REVIEW_LEDGER.yml`
- `DEBT_TAXONOMY.yml`
- `CONCEPT_CUBE.yml`, `DISCOVERY_BACKLOG.yml`
- `ACCESSIBILITY_TEST_MATRIX.yml`, `COMPREHENSION_STUDY_PLAN.yml`, `READER_TASK_PROTOCOL.yml`, `GLOSSARY_USABILITY_LEDGER.yml`, `SCREEN_READER_SMOKE_TEST_LOG.yml`, `KEYBOARD_NAVIGATION_CHECK.yml`, `TRANSLATION_READINESS_LEDGER.yml`
- `datapackage.json`, `ro-crate-metadata.json`
- `tools/check_current_release.py`, `tools/check_stale_revision_tokens.py`, `tools/generate_debt_observations.py`

## The new rule

A current package must have a single current-release identity, and every stronger claim must route through an observation family. In rev0181, a reader should be able to ask:

- What is the current release?
- Which prior tokens are historical rather than active?
- Which debts block stronger public or conformance claims?
- Which source anchors exist, and what are they not evidence for?
- Which accessibility or comprehension tests are planned but not run?
- Which metaphysical operators have hard cases, rivals, failure modes, and missing tests?

If the answer is only hidden in prose, the archive has not yet earned the claim.

## Allowed claim

Rev0181 normalizes current-release identity, exposes expanded local cube observations, classifies source/debt/access/concept rows, and adds local structural checks.

## Forbidden claims

Rev0181 does **not** claim RDF Data Cube publication, SHACL conformance, WCAG conformance, accessibility certification, plain-language certification, RO-Crate conformance, Data Package validation, OSCAL publication, SPDX or CycloneDX SBOM publication, SLSA level, in-toto attestation, external audit, public support, legal compliance, public deployment, or philosophical completeness.

## Philosophical consequence

The archive's governance stack now reflects a philosophical thesis: access, warrant, boundary, source role, and institutional status are not afterthoughts. They affect what kind of object the archive itself is. A metaphysical archive that cannot state who can read it, what claims its rows support, what debts block public reliance, and where its concepts can fail is not yet a stable research object. Rev0181 does not solve that problem, but it makes the problem queryable.

## Reader-route repair added in rev0181

This layer also repairs the archive entrance by giving readers four paths rather than one dense governance route: beginner, research, application, and governance. The path split is not a comprehension claim; it is a navigation surface that can later be tested through reader-task observations.

## Additional controlled surfaces promoted by this layer

Rev0181 also promotes `CORE_THESIS_COMPRESSIONS.md`, `SCHEMA_CONSTRAINT_PROFILE.yml`, `EXPORT_READINESS_LEDGER.yml`, `RUNBOOKS/current-release-cube-expansion-review-v1.md`, `tools/check_expanded_cube.py`, and `tools/check_schema_constraints.py`. These are local governance and planning surfaces only. They do not imply external certification, machine-readable publication, public support, or completed user testing.

## Residual debt

- no external or independent audit
- no public endpoint or RDF publication
- no SHACL execution over a graph representation
- no completed WCAG assessment or screen-reader/keyboard test result
- no completed reader-comprehension study
- no public support process
- no signed release provenance
- no complete schema constraint migration for every historical schema
- no public catalog or repository publication evidence
