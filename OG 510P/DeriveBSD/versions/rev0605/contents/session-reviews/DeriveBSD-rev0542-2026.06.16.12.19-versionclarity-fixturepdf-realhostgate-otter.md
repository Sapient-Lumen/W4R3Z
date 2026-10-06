# DeriveBSD-rev0542-2026.06.16.12.19-versionclarity-fixturepdf-realhostgate-otter

## Purpose

This revision intentionally spends engineering effort on the riskiest remaining lane instead of expanding doctrine: the real FreeBSD removable-media host-proof path. It does not claim a real FreeBSD proof was produced inside the Linux cloudtainer. It tightens the seam so the next real-host run has fewer ways to look fresher or more valid than it is.

## Substantive changes

- Split host-smoke version semantics: generated_for_version remains the 2026-06-05r554 runner-contract alias; runner_contract_version is explicit; cube_cut_version now carries 2026-06-16r572.
- Extended host-smoke receipt schema, validator, runner, checker, proof-bundle finalizer, proof-bundle schema, and proof-bundle validator so cube-cut / runner-contract confusion is refused.
- Replaced the weak removable-media invoice.pdf fixture with a valid visible deterministic PDF and refreshed digest-bound harness/backend/host-smoke evidence examples.
- Added executable fixture guard coverage in the host-smoke checker for PDF header/resources/font/visible text, size, symlink absence, and SHA-256.
- Refreshed current front doors, generated catalog/index/context artifacts, cube audit/backlog/checkset/ledger examples, and release docs for 2026-06-16r572.

## Risk reduced

The prior archive allowed a reader to confuse the stable host-smoke runner contract (`2026-06-05r554`) with the current cube cut. This revision makes that split explicit in receipts and proof bundles and adds negative validation against conflating the two. The prior positive PDF fixture also rendered poorly/blank; this revision replaces it with a visible deterministic PDF and binds the bytes in executable checks.

## Still missing

The missing keystone remains a non-simulated FreeBSD host proof bundle from `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh`. The checked proof-bundle example remains `checker-simulation-non-proof` by design.

## Validation

- release-critical hygiene: 38/38 passed (`{rel_ledger.as_posix()}`)
- schema-cube-audit hygiene: 3/3 passed (`{schema_ledger.as_posix()}`)
- strict duplicate-key JSON scan: 1382 JSON files scanned, passed
- PDF render verification: `fixtures/removable-media/local-fallback/exfat-card/invoice.pdf` rendered one visible page
