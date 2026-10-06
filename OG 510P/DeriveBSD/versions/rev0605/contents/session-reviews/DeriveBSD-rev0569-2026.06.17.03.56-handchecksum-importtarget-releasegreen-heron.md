# DeriveBSD-rev0569-2026.06.17.03.56-handchecksum-importtarget-releasegreen-heron

## Focus

This cut keeps pressure on the riskiest unfinished lane: scarce real FreeBSD host proof. Instead of adding a new registry surface, it hardens the small handoff/import path that a real operator will actually use.

## Substantive changes

- Added a shared handoff checksum policy in `tools/freebsd/host_proof_contract.py`: required checksum members are `receipt.json` and `bundle.json`; optional checksum members currently include `README.import.txt`; allowed checksum rows are the union of those sets.
- Hardened `tools/freebsd/verify_removable_media_local_fallback_host_proof_handoff.py` so `SHA256SUMS` must cover every present optional handoff member, including `README.import.txt`, and stale optional rows for absent files fail closed.
- Preserved `host_target_matrix_id` and `host_target_tier` through `import.receipt.json` receipt and bundle summaries after loose or sealed import, then extended the import auditor to reject mismatches.
- Refactored loose/sealed/import/audit checker handoff builders so optional README evidence is written before checksums and therefore cannot accidentally sit outside the digest envelope.
- Refreshed host-smoke/proof-bundle examples, README, CHANGELOG, current proof docs, current generated-summary docs, and generated cube surfaces to `2026-06-17r597`.

## Why this matters

The previous handoff shape could include a useful operator README while only checksum-binding `receipt.json` and `bundle.json`. That is small, but it is exactly the sort of loose optional evidence that can become confusing during a one-shot real-host run. r597 makes optional evidence either checksum-bound or rejected.

The import receipt target-tier preservation also keeps host-target context visible after transport. A real proof imported from a legacy-floor host should remain visibly different from a `primary-production` 15.1 host.

## Validation

- release-critical profile: 49/49 passed, failed=0, timed_out=0, run_complete=true
- schema-cube-audit profile: 3/3 passed, failed=0, timed_out=0, run_complete=true
- spec examples: 469 validated
- schemas total: 457
- strict JSON duplicate-key scan: 1443 JSON files scanned
- hygiene-referenced check scripts: 382
- deep-contract checks: 291

## Remaining hard thing

This still does not include a non-simulated FreeBSD host receipt. The next true milestone remains running the operator packet on a real `15.1-RELEASE` host, sealing/importing the handoff, and letting the strict proof-theatre gate reject anything simulated.
