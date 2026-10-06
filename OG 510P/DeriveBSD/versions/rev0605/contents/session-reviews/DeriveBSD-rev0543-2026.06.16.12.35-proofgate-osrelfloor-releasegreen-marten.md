# DeriveBSD-rev0543-2026.06.16.12.35-proofgate-osrelfloor-releasegreen-marten

## Intent

This revision attacks the highest-risk unfinished seam: checked-in FreeBSD host proof must not become evidence theatre while the project still lacks a non-simulated FreeBSD receipt. The pass also keeps the schema/checkset audit honest after adding release-floor proof fields.

## Changes

- Added `tools/check_freebsd_real_host_proof_theatre_gate.py` and wired it into the release-critical profile so any checked-in `proof_status = real-host-proof` object must be a FreeBSD host proof bundle that passes the default strict proof-bundle validator against its original receipt.
- Added host release-floor binding to the host-smoke runner, receipt schema, receipt validator, host-smoke checker, proof-bundle validator, examples, and docs: `host_release_floor = 14.3-RELEASE`, `host_osreldate_minimum = 1403000`, and `host_osreldate_meets_supported_floor = true` for passed receipts.
- Refreshed host-smoke validation receipts and the importable proof-bundle example for `2026-06-16r573`; the checked bundle remains `checker-simulation-non-proof`.
- Regenerated cube schema audit, schema refactor backlog, hygiene checkset manifest, hygiene run ledger, generated docs/catalogs, and current front doors. The audit now reports the host-smoke receipt schema as a new low-priority const-heavy surface rather than turning that into another immediate registry split.

## Validation

- `release-critical`: 39/39 passed.
- `schema-cube-audit`: 3/3 passed.
- Strict JSON duplicate-key scan passed after the review artifacts were added.
- Zip integrity passed after packaging.

## Not claimed

This revision still does not contain a non-simulated FreeBSD host receipt or production `real-host-proof` import. The next real milestone remains running `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` on a real supported FreeBSD host and importing that bundle.
