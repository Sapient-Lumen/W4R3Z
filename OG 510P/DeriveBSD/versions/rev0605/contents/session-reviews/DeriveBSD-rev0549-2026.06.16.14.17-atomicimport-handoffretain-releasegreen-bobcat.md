# DeriveBSD-rev0549-2026.06.16.14.17-atomicimport-handoffretain-releasegreen-bobcat

## Mission focus

This pass targeted the next fragile point in the real FreeBSD proof lane: after a scarce host run succeeds, the cube must not lose the finite handoff or publish a half-imported proof directory when import/audit fails. The work deliberately tightened existing proof-path scripts and checks instead of adding another doctrine or registry surface.

## Changes made

- Hardened `tools/freebsd/import_removable_media_local_fallback_host_proof_handoff.py` with staging-directory publication: copy the handoff, reverify it, write `import.receipt.json`, then atomically rename into the digest-named import path.
- Changed replacement semantics so an existing digest import is preserved until a complete replacement is ready to publish. The release-critical importer checker now proves duplicate refusals leave the existing import untouched and deliberate replacement leaves no backup/staging residue.
- Fixed the strict collect/import wrapper’s evidence-retention risk: auto-created handoff directories are deleted only after full collect/import/audit success; failures preserve the handoff for inspection or re-import.
- Extended `tools/check_removable_media_local_fallback_freebsd_host_proof_importer.py` and `tools/check_removable_media_local_fallback_freebsd_host_proof_collect_import.py` rather than creating a new registry family.
- Refreshed the current front doors, generated docs/catalogs, cube schema audit/backlog/checkset artifacts, host-smoke and proof-bundle examples, and the canonical release-critical ledger for `2026-06-16r579`.

## Validation

- `release-critical`: passed 45/45.
- `schema-cube-audit`: passed 3/3.
- Strict duplicate-key guard: passed on 1404 JSON files before adding this session review set.
- The checked proof bundle remains `checker-simulation-non-proof`; no real FreeBSD host proof is claimed in this revision.

## Next highest-risk step

Run `tools/freebsd/collect_import_removable_media_local_fallback_host_proof.sh` on a supported real FreeBSD host. If any import or audit step fails, the auto-created handoff should now remain available instead of being deleted, making the run recoverable.
