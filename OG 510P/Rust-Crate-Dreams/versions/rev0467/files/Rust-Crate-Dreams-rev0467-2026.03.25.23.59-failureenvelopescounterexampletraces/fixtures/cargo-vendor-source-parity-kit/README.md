# Cargo Vendor & Source Parity Kit fixtures

Current bundle spine:
- `source-origin.receipt.json`
- `source-parity.lock`
- `source-coverage.report.json`
- `vendor-parity.report.json`
- optional `source-replacement.diff.json`

Current scenario lanes:
- clean registry-to-vendored parity
- `[patch]` overlay changing the effective source graph
- git dependency blocking honest offline-readiness claims
- missing vendored member or checksum/content drift
- multi-registry alias split where distinct logical source IDs collapse onto one vendored directory
- git workspace dependency where replacement still needs git-style history
- path dependency outside the vendored boundary
- sparse/git protocol alias where one protocol is canonical but source identity still matters
- external mirror verification present while path dependencies still sit outside the covered boundary
