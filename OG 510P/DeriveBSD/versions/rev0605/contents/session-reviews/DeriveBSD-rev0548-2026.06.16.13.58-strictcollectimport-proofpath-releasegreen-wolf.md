# DeriveBSD-rev0548-2026.06.16.13.58-strictcollectimport-proofpath-releasegreen-wolf

## Mission focus

This pass stayed on the riskiest unfinished DeriveBSD seam: turning the future real FreeBSD removable-media proof from a multi-command choreography into one strict operator path. The cube still does not claim non-simulated host proof, but it now has a safer way to collect, verify, import, and audit that proof once a supported FreeBSD host is available.

## Substantive changes

- Added `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh` as the preferred real-host operator entry point.
- Added release-critical `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py`.
- The one-shot wrapper runs collector -> handoff verifier -> importer -> import-root auditor, all in default real-proof mode.
- The wrapper exposes safe `--help`, supports explicit import-root/handoff env knobs, preserves optional handoff material when requested, and contains no checker-simulation/refusal/failed flags.
- Bound the wrapper into `tools/freebsd/host_proof_contract.py`; proof bundles now bind exactly 12 FreeBSD proof-tool digest rows.
- Preflight now checks that the strict collect/import wrapper exists and that its help path works before mutable host authority is used.
- Refactored a small hygiene wart by removing duplicate proof-gate stems while keeping the new guard in the bounded release-critical profile.
- Refreshed host-smoke/proof-bundle examples, schema constants, generated cube audit/backlog/checkset artifacts, current docs, generated docs/catalogs, and the canonical release-critical ledger for `2026-06-16r578`.

## Validation

- `python3 -B tools/hygiene.py --profile release-critical --ledger-json spec/examples/cube.hygiene.run.ledger.json --timeout-seconds 30`: passed 45/45.
- `python3 -B tools/hygiene.py --profile schema-cube-audit --ledger-json /mnt/data/derivebsd_rev0548_schema-cube-audit-ledger.json --timeout-seconds 30`: passed 3/3.
- `python3 -B -S tools/check_json_duplicate_key_rejection.py`: passed before session-review artifacts were added, scanning 1401 JSON files.

## Boundary

No real FreeBSD host proof is claimed in this revision. The checked proof bundle remains checker-simulation non-proof material; the next real milestone is still to run the strict collect/import wrapper on a supported FreeBSD host and commit only the resulting default-audited import.
