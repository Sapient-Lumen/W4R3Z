# DeriveBSD-rev0573-2026.06.17.05.33-symlinkancestor-pathguard-releasegreen-falcon

## Focus

Rev0573 keeps the work on the riskiest incomplete lane: the first non-simulated FreeBSD host-proof run and the strict import path that will receive it. The concrete hazard addressed here is that final-path symlink refusals were not enough: an existing symlink ancestor such as `/media/link/handoff` could still redirect scarce host-proof bytes before later verification caught the final path.

## Substantive changes

- Added `OPERATOR_PATH_SYMLINK_ANCESTOR_POLICY` and shared `first_existing_symlink_component` / `require_no_existing_symlink_component` helpers in `tools/freebsd/host_proof_contract.py`.
- Wired the shared ancestor guard into the FreeBSD host-proof collector, strict collect/import wrapper, loose importer, deterministic sealer, safe unsealer, and collect/import run-receipt writer.
- Removed duplicated final-path-only assumptions from proof/import call sites by routing operator-path policy through the shared contract.
- Extended release-critical importer, sealer/unsealer, sealed-importer, and collect/import checks with symlink-ancestor regressions, including target-directory non-mutation assertions.
- Updated operator docs and current proof docs so handoff, import-root, archive, unseal-output, and run-receipt paths must not be symlinks and must not pass through existing symlink ancestors.
- Refreshed r601 generated/current surfaces, host-smoke/proof-bundle examples, schema/checkset artifacts, README, CHANGELOG, and hygiene ledger evidence.

## Audit/refactor notes

The audit found a path-hardening seam that cut across shell and Python tools. Rather than adding one-off checks at each site, rev0573 centralizes the policy in `host_proof_contract.py` and makes the wrappers use that contract before proof collection, seal/unseal, import, or receipt writes. This is a practical refactor: it shrinks semantic drift risk without adding a new registry family.

The front-door index exceeded its byte/line ratchet after the r601 release note. The fix was to compress existing front-door prose and combine two discovery lines, not to raise the budget.

## Validation

- Release-critical profile: 49/49 passed; failed=0; timed_out=0.
- Schema-cube-audit profile: 3/3 passed; failed=0; timed_out=0.
- Spec examples validated: 469.
- Schemas total: 457.
- Hygiene-referenced check scripts: 382.
- Deep-contract checks: 291.
- Strict JSON duplicate-key scan: 1455 JSON files scanned.
- Empty `validation/freebsd-host-proof-imports/` root preserved for future checked-in real-host proof imports.

## Caveat

This revision still does not contain a non-simulated FreeBSD host receipt. The true milestone remains a real `15.1-RELEASE` host run, returned handoff, strict import, and audit as `real-host-proof` with `primary-production` target-tier evidence.
