# CHANGELOG rev0311

Created: 2026-06-04T06:12:00-04:00

## Added

- Counterevidence ledger with 64 synthetic adverse operational findings.
- Full 1,056-row adjudicated local evidence sample.
- Adjudicated readiness scorecard and delta against rev0310 postclosure scores.
- Public claim gates after counterevidence.
- Evidence-packet adjudication results and negative-control packet tests.
- Operational bottleneck stress tests for alerting, evacuation, AFN transport, CRC throughput, ingestion controls, healthcare/LTC flow, and recovery/claims.
- Readiness kill-switch rules that override averages.
- Legacy universal crossproduct deprecation shim.
- Source-register consistency audit and patch through S995.
- Scoped rev0311 emergency SQLite mirror.

## Changed

- The high-scoring river fixture is intentionally reopened by counterevidence to prove score reversal works.
- The source register is synchronized with source.csv for late rev0309/rev0310 sources and new rev0311 sources.
- README, schema metadata, validation, resource manifest, table catalogs, and package integrity reports are updated to rev0311.

## Not changed

- The three 114,494-row legacy crossproduct tables are retained for compatibility.
- Site rows remain synthetic fixtures; no real-world nuclear-site readiness claim is made.
