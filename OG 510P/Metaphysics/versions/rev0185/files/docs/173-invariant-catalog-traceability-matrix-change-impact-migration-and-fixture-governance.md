# 173. Invariant Catalog, Traceability Matrix, Change-Impact, Migration, and Fixture Governance

## Core thesis

A release can pass a validator and still become fragile if nobody can say which invariant was protected, which artifact satisfied which requirement, which downstream surface was affected by a change, which migration rule applies, or which negative case would have failed if the check were real.

Rev0166 made the local datacube harder to silently drift by adding a status vocabulary, local path-reference checks, query regression, claim-language governance, and unsigned local provenance. Rev0167 adds the next layer: invariant cataloging, traceability rows, change-impact assessment, migration/deprecation semantics, and fixture-based negative testing. The purpose is to make governance breakages visible before they become memory.

## What this release adds

Rev0167 adds five control surfaces:

1. `INVARIANT_CATALOG.yml` lists the local invariants a release must preserve and states the check surface for each.
2. `TRACEABILITY_MATRIX.yml` maps requirements to docs, artifacts, records, checks, query names, and status tokens.
3. `CHANGE_IMPACT_MATRIX.yml` records what changed in this release and which downstream surfaces were touched.
4. `MIGRATION_LEDGER.yml` records the rev0166 to rev0167 transition, compatibility class, deprecation state, rollback target, and forbidden migration claims.
5. `FIXTURE_CORPUS.yml` lists positive and negative fixture cases used to check that the validator fails in expected classes, not merely on the happy path.

These artifacts are deliberately local. They are not a public issue tracker, public CI, formal methods system, semantic theorem prover, reproducible build attestation, external audit, or operational safety case.

## Invariant rule

An invariant is not a vibe, motto, or prose habit. In this archive it must have an identifier, severity, checked surface, expected result, failure consequence, and source artifacts. An invariant may be only locally checkable, but if it is called an invariant, the limits of the check must be named.

## Traceability rule

A governance requirement is not traceable merely because it is mentioned in a document. It must be connected to controlling text, package artifacts, current records, executable or review checks, query names, status tokens, and where possible, negative fixtures. Traceability remains local and intra-package unless an external evidence system is actually supplied.

## Change-impact rule

Every structural addition should say what it changes, what it touches downstream, what compatibility class it has, what validates it, and how it would be rolled back. This blocks a common release failure: adding a new governance surface without updating the cube, records, validator, queries, front doors, and claim-language boundaries.

## Migration and deprecation rule

A migration is not the same as a copy. The migration ledger distinguishes backward-compatible governance extension, breaking schema change, deprecation without removal, removal, replacement, and rollback. Rev0167 is classified as a backward-compatible local governance extension: rev0166 material is retained, rev0167 current records are added, existing query names are preserved, and new query names are added.

## Fixture rule

A validator that never sees a negative case can become a ceremony. Rev0167 therefore adds a fixture corpus with a local runner. The runner mutates temporary copies of the package and confirms that representative failures are blocked: missing required field, undefined status token, missing local reference, broken control successor, missing cube source artifact, query-regression failure, and manifest mismatch. This is still local fixture pressure, not independent quality assurance.

## Allowed claims after rev0167

The package may claim that it includes a local invariant catalog, local traceability matrix, local change-impact matrix, local migration ledger, local fixture corpus, local fixture runner, local invariant checker, local traceability checker, current-record required-field checks, current status-token checks, local reference-integrity checks, local query regression, local unsigned provenance rows, and fresh-extraction validation.

## Forbidden upgrade claims

The package must not claim formal verification, model checking, theorem proving, complete semantic validation, external QA, public CI, public issue tracking, source-watch automation, public query service, OpenLineage emission, Great Expectations deployment, Semantic Versioning compliance, ODRL policy publication, reproducible supply-chain attestation, domain review, public safety case, legal/medical/financial/engineering authority, or operational deployment readiness.

## Open debt retained

- Historical records are not normalized into full traceability rows.
- Fixture cases are representative, not exhaustive.
- Negative tests check validator failure classes, not metaphysical truth.
- Migration/deprecation semantics are local archive semantics, not SemVer compliance.
- Traceability is intra-package only.
- Change-impact rows are local release rows, not a public dependency graph.
- No public CI or external reviewer independently re-ran the suite.

## Next likely layer

The next durable layer should be claim-graph and evidence-packet governance: claim nodes, warrant edges, source anchors, contradiction states, freshness windows, evidence withdrawal, and propagation of defeated claims. Rev0167 prepares for that by forcing every new governance surface to be traceable, invariant-bound, migration-classified, and fixture-pressured.
