# DeriveBSD-rev0571-2026.06.17.04.44-primarytarget-checksumcanon-releasegreen-kestrel

## Focus

This revision keeps the work on the riskiest incomplete lane: scarce FreeBSD host proof. It avoids adding a new evidence family and instead tightens the proof import path where a first real host run could be made ambiguous or downgraded.

## Substantive changes

- `SHA256SUMS` parsing now rejects non-canonical digest text: lowercase hex64 is required before any digest comparison. Uppercase digest rows no longer pass by being normalized in memory.
- The import auditor has a checked-in release-evidence mode, `--require-primary-target`, that rejects `real-host-proof` imports unless receipt and bundle summaries preserve the current host target matrix id and `primary-production` target tier.
- The live checked-in import-root gate now calls the auditor with `require_primary_target=True`, so future checked-in proof from only the legacy floor cannot look release-green by default.
- Copied handoff snapshot identity was refactored into `tools/freebsd/host_proof_contract.py` through `copied_handoff_snapshot()`, `handoff_file_rows()`, and `sha256_file()`, reducing duplicated importer/auditor/checker digest policy.
- Current docs, generated docs, host-smoke/proof-bundle examples, cube schema audit/backlog/checkset examples, README, CHANGELOG, and the canonical hygiene ledger example were refreshed to `2026-06-17r599`.

## Validation

- release-critical profile: 49/49 passed; result `passed`; run_complete `true`.
- schema-cube-audit profile: 3/3 passed; result `passed`.
- spec examples: 469 validated.
- strict JSON duplicate-key scan: 1448 JSON files scanned.
- schema count: 457 schemas, 469 examples.
- hygiene checkset: 382 hygiene-referenced checks, 291 deep-contract checks, 49 release-critical checks.

## Remaining caveat

This still does not include non-simulated FreeBSD host proof. The next true milestone remains a real `15.1-RELEASE` host run, returned handoff, strict import, and audit as `real-host-proof`.
