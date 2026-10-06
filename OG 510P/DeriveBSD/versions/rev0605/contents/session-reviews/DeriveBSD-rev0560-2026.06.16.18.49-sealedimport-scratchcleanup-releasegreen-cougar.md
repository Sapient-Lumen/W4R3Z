# DeriveBSD rev0560 Session Review

## Cut

- Release name: `DeriveBSD-rev0560-2026.06.16.18.49-sealedimport-scratchcleanup-releasegreen-cougar`
- Cube cut: `2026-06-16r589`
- Focus: collapse the real FreeBSD host-proof sealed handoff into one strict cloudtainer-side import command.

## Risk focus

The riskiest unfinished path remains the scarce real FreeBSD `real-host-proof` import. Prior cuts made sealed handoff transport safer, but the receiving side still required a manually ordered sequence: validate archive, unseal, verify handoff, import, audit, and clean scratch state. That left too much room for operator drift during the only step this Linux cloudtainer cannot perform itself.

This cut reduces that risk by adding a single strict sealed-import tool for the cloudtainer receive side.

## Priority changes

- Added `tools/freebsd/import_sealed_removable_media_local_fallback_host_proof_handoff.py`.
- The sealed importer validates a deterministic sealed archive, unseals into scratch, verifies the handoff, imports through the full-digest importer, audits the import root, and removes scratch state.
- Default mode accepts only real host proof receipts; checker simulations require explicit `--allow-checker-simulation`.
- Added `tools/check_removable_media_local_fallback_freebsd_host_proof_sealed_importer.py` as a release-critical regression guard.
- Bound the sealed importer into `tools/freebsd/host_proof_contract.py`, raising proof bundles to exactly 17 proof-tool digest rows.
- Updated the real-host operator packet so the preferred cloudtainer receive path is the one-command sealed importer, while the split verify/import/audit path remains available for diagnosis.
- Regenerated host-smoke receipts, proof-bundle fixtures, generated docs, schema audit artifacts, refactor backlog artifacts, hygiene checkset, and the release-critical run ledger for `2026-06-16r589`.

## Audit and refactor work

The refactor target was the FreeBSD host-proof contract rather than another prose registry. The sealed importer path now lives in the shared contract beside the verifier, sealer, unsealer, importer, auditor, checked-import gate, preflight, collect/import runner, operator packet, and theatre gate. That makes proof-bundle row counts executable instead of document-local.

The audit target was receive-side failure behavior. The new release-critical checker exercises default real-proof refusal for checker simulations, explicit simulation override, compressed archive rejection, symlinked archive rejection, duplicate import refusal, replacement import, full-digest import directory naming, post-import audit, and scratch cleanup.

## Validation

- `release-critical`: 48 / 48 passed.
- `schema-cube-audit`: 3 / 3 passed.
- `validate_spec_examples.py`: 469 examples validated.
- `check_cube_hygiene_run_ledger.py`: passed after the final non-`-S` release-critical ledger run.
- `check_generated_docs.py`: passed.
- `check_frontdoor_budget.py`: passed without raising the budget; older front-door sediment was pruned.

## Remaining caveat

This remains a Linux cloudtainer pass. It materially reduces the risk around receiving and importing the scarce FreeBSD handoff, but it does not include a non-simulated FreeBSD `real-host-proof` import.

## Recommended next pass

The next high-value pass should continue converting scarce-host choreography into checked execution. Good targets are either a sealed-import receipt summarizer for fast operator triage, or a stricter real-host proof freshness gate that rejects stale proof imports before any release claim can cite them.
