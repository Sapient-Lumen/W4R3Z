# CHANGELOG rev0371

## Added

- Response-intake contract for incoming records, public-meeting artifacts, docket releases, no-record replies, and redacted productions.
- Fixture-safe response-intake CLI and executed fixture ledger.
- Response lockbox builder with sidecar, hash-ledger, adjudication, nonresponse, redaction, and follow-up templates.
- Docket/release watch for NRC APS/PDR, EOF/LER disposition, FEMA final report timing, and records-route follow-up.
- Response-to-proofcut map and blocker-saturation validator.
- Pruned rev0371 hotpath source list, rebuilt SQLite, rebuilt capsule, and prune audit.

## Changed

- The active hotpath no longer carries both rev0369 and rev0370 duplicate aliases for the same request/proofchain controls.
- README, manifest, validation rules, resource manifest, index/file catalogs, and validation reports advanced to rev0371.

## Claim state

No real BVPS exercise packet has been imported and no records requests were sent from this static package. Response templates, lockboxes, routes, watches, and fixture ledgers are acquisition controls only.
