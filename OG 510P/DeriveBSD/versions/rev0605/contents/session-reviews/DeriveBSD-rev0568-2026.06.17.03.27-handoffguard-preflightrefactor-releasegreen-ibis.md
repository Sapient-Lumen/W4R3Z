# DeriveBSD rev0568 session review: handoff guard + preflight refactor

Version: 2026-06-17r596
Archive filename: DeriveBSD-rev0568-2026.06.17.03.27-handoffguard-preflightrefactor-releasegreen-ibis.zip

## Mission focus

This turn deliberately stayed on the riskiest unfinished lane: scarce real FreeBSD host proof. The work does not add another receipt family. It turns a practical first-run hazard into an executable refusal and simplifies the shell preflight contract surface that every real host operator must cross.

## Substantive changes

- `tools/freebsd/collect_removable_media_local_fallback_host_proof.sh` now refuses to reuse a handoff directory that already contains `receipt.json`, `bundle.json`, `SHA256SUMS`, or `README.import.txt` before FreeBSD/root preflight unless `DERIVEBSD_HOST_PROOF_HANDOFF_REPLACE=1` is set for deliberate replacement.
- `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` now regression-tests that the overwrite guard fires before non-FreeBSD refusal and that the old handoff bytes remain unchanged.
- `tools/freebsd/preflight_removable_media_local_fallback_host_proof.sh` now imports `tools/freebsd/host_proof_contract.py` once into `CONTRACT_VALUES`, removing repeated Python contract reads in the shell boundary.
- `tools/freebsd/host_proof_contract.py` carries the r596 handoff replacement environment and overwrite policy strings so collector, packet, docs, and checks do not fork the wording.
- The operator packet and collect/import wrapper now expose the deliberate-replacement environment variable instead of leaving reuse behavior implicit.
- The generated/current summary surfaces were refreshed to `2026-06-17r596` without increasing the front-door budget; `docs/00-index.md` stayed at its byte ceiling by shortening the new release anchor and pruning older whitespace rather than raising the budget.
- `validation/freebsd-host-proof-imports/` is present again so the live checked-in import-root gate audits the strict default path even when no real imported proof has landed yet.

## Audit/refactor note

The refactor target was the FreeBSD preflight contract read. Before r596, the shell wrapper repeatedly spawned Python to read adjacent constants. That was not conceptually wrong, but it was brittle at exactly the boundary operators must run on a real host. r596 collapses those reads into one contract import and binds that path with `tools/check_removable_media_local_fallback_freebsd_host_proof_preflight.py`.

## Validation summary

- release-critical profile: 49/49 passed
- schema-cube-audit profile: 3/3 passed
- spec examples: 469 validated
- schemas total: 457
- hygiene-referenced check scripts: 382
- deep-contract checks: 291
- strict JSON duplicate-key scan: 1439 JSON files scanned
- generated docs: passed
- generated artifact version ids: passed
- current generated surface sync: passed
- zip integrity: checked after packaging

## Caveat

This still does not contain a non-simulated FreeBSD host receipt. The true milestone remains collecting a primary-production `15.1-RELEASE` handoff on real hardware or a real FreeBSD host, sealing/importing it, and letting the existing theatre gate reject simulated substitutes.
