# DeriveBSD-rev0584-2026.06.17.21.50-hostpreflight-rootsplit-greenmarten session review

## Focus

Continue reducing the risk that the first real FreeBSD host proof run is wasted. The concrete gap found in rev0583 was a host-side privilege split: the generated `RUN_ON_FREEBSD.sh` could run collection through `sudo`, but the root-required FreeBSD preflight ran as the invoking user. That could cause a valid operator path to fail before collection, or worse, teach operators to bypass the preflight.

## Substantive changes

- Added `PREFLIGHT_ON_FREEBSD.sh` to the generated real-host proof work order.
- Refactored `RUN_ON_FREEBSD.sh` to call the standalone preflight before collection.
- Made the host preflight run directly when uid 0, or through `sudo env PYTHON=...` otherwise.
- Kept `VERIFY_WORK_ORDER.sh` as the first step so a copied kit still proves script/tool digest integrity before scarce host time is spent.
- Expanded work-order script digest binding from 3 to 4 scripts: .
- Refreshed current docs, host-smoke/proof-bundle examples, generated catalogs, and schema/cube examples for `2026-06-17r610`.
- Trimmed `docs/00-index.md` back under the front-door budget after the r610 entry pushed it over.
- Fixed stale generated-proof validation by refreshing `validation/removable-media-local-freebsd-host-proof.bundle.json` to the current cube cut.

## Audit/refactor outcome

The useful refactor was not another registry. It was a boundary cleanup around the actual operator script split: work-order verification, FreeBSD preflight, collection, sealed handoff preflight, import, audit, and status report now sit in an explicit order with the root transition isolated.

## Remaining risk

The live proof import root still has no real host proof. Current status is `blocked-no-real-host-proof-import`, `proof_complete=false`, `real_host_proof=0`, and `primary_production_real_host_proof=0`. The next actual milestone is still running the checked work order on a primary-production FreeBSD `15.1-RELEASE` host and importing the sealed handoff.

## Validation

- Release-critical hygiene: 51/51 passed; run_complete=true.
- Schema-cube-audit profile: 3/3 passed; run_complete=true.
- Work-order verifier: passed against `validation/freebsd-real-host-proof-work-order/current`.
- Proof status reporter: live import root remains blocked by absence of real proof, not by structural corruption.
