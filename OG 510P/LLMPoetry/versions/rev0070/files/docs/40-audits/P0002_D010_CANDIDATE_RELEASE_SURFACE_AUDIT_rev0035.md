# P0002-D010 candidate and release-surface audit — rev0035

Current head: `P0002-D010`  
Status: internal anthology candidate; not admitted; not evidence-ready.  
Primary repair: release-facing descriptor freshness.

## Substantive decision

`P0002-D010` was cold-reviewed after its creation turn and moved to an internal anthology-candidate hold. No D011 was drafted. That is intentional: the riskiest failure now would be endless revision by apparatus rather than testing the first draft that can plausibly stand as a poem.

D010 is held because the source/runtime pressure is carried by the scene rather than explained by the archive: tide staff, ruler, first zero, harbor, failed value, returned water. The review records residual risk rather than hiding it: `Station Datum` may still feel imported, and no external disclosed reader judgment exists.

## Refactor/audit

This turn found a concrete drift fault: `RELEASE_MANIFEST.json` still pointed to rev0033 / `P0002-D009`, and several descriptor surfaces carried stale current-head fields. Rev0035 adds `tools/check_release_surfaces.py`, wires it into `make validate`, `make doctor`, and the Makefile, and refreshes release-facing descriptors.

The new checker verifies current revision/head/artifact agreement across:

- `RELEASE_MANIFEST.json`
- `CITATION.cff`
- `Makefile` release variables
- `registries/poem_index.json` current path fields
- `datapackage.json`
- `croissant-lite.json`
- `ro-crate-metadata.json`
- `codemeta.json`
- `VALIDATION_TOOLCHAIN_MANIFEST.json`

## Non-claims

Candidate status is an internal hold only. It is not admission, external validation, evidence-candidate status, or publication clearance. Source/runtime validation continues to prove traceability and non-overclaim only.
