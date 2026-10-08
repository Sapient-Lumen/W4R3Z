# Deep cube schema-validation and weight audit

## Status

rev0315 is an archive-control repair, not a scientific promotion. It makes schema contracts executable, records a weight/waste finding, and opens one active followthrough item for authority-graph compaction.

## Severe issue found

`make lint` passed in rev0314, but direct JSON Schema instance validation failed across registered ledger/schema pairs. That meant the archive had schemas as durable surfaces, but the default lint path was not actually using those schemas as executable instance contracts.

The failure mode was systematic type drift: several schemas declared a field as `string` where the ledger had arrays, one schema declared an array where the ledger used an object, and `CLAIM-ROUTE-BINDING-LEDGER.json` mixed string and array encodings for claim-language fields.

## Corrected in rev0315

- Added `tools/validate_registered_json_schemas.py`.
- Wired registered JSON Schema instance validation into `make lint`.
- Repaired schema/data type drift for candidate-route state, public-record carrier, acquisition protocol, claim-route binding, epistemic defeater, credit allocation, contrast class, likelihood update, and transportability surfaces.
- Normalized `allowed_claim_language` and `forbidden_claim_language` in `CLAIM-ROUTE-BINDING-LEDGER.json` to arrays.
- Collapsed one multi-entry `rollback_if_missing` list to the schema's string representation.
- Corrected the stale `SURFACE-STATUS.json` latest revision note.

## Waste finding

`AUTHORITY-DEPENDENCY-GRAPH.json` is an expanded edge table with 51,599 edge rows and is roughly two thirds of the uncompressed archive. It is useful as a generated audit surface, but wasteful as a default release payload in its current expanded JSON form.

The repair target is not to delete graph authority. The repair target is to make graph authority reconstructable and verifiable from ledgers while the release carries a compact manifest, digest, summary, or columnar/delta representation instead of a large expanded table.

## Missing external interoperability layer

The cube has strong internal discipline but weak external packaging semantics. Future revisions should consider adding a minimal research-object/provenance/software-supply-chain layer:

- RO-Crate-style metadata for the cube as a research object.
- PROV-style entity/activity/agent provenance for generated surfaces.
- SBOM or build-provenance metadata for release scripts and tool dependencies.
- A small source-freshness watchlist for volatile external scientific data releases.

## Active followthrough

`FT-0315-001` keeps authority-graph compaction live until a later revision proves that `make index`, `make lint`, and `make package` can reconstruct or verify all authority edges without requiring the expanded 27 MB graph as the largest default text artifact.
