# EvidenceVault rev0845 session review: release boundary and symlink hardening

Created: 2026-06-13T04:21:40+00:00

Scope: targeted overlay work over rev0844. This revision stays focused on concrete failure modes around archive boundaries, symlink traversal, and malformed publication metadata rather than adding new registry surfaces.

## Substantive changes

### rev0845-w01-rights-gate-symlink-boundary-and-html-rst-coverage

Risk: the fresh publication rights scan was release-critical but still trusted ordinary file reads and local target resolution enough that an archive-internal symlink could make the scan read/hash host or cloudtainer content, and HTML/reStructuredText local rights links were still parser blind spots.

Change: publication_rights_gate.py now rejects symlinked scan inputs and symlinked local rights targets, adds HTML href and reStructuredText link/reference scanning, and ignores in-document #license anchors rather than treating them as missing files.

Status: `validated_with_symlink_missing_resolved_and_parser_fixtures`

Evidence:
- `scripts/publication_rights_gate.py`
- `scripts/validate_publication_rights_gate_symlink_boundary_rev0845.py`
- `AUDIT/PUBLICATION_RIGHTS_GATE_SYMLINK_BOUNDARY_REV0845.json`
- `AUDIT/PUBLICATION_RIGHTS_GATE_FRESH_REFERENCE_SCAN_REV0842.json`
- `AUDIT/PUBLICATION_RIGHTS_GATE_MARKDOWN_REFERENCE_FORMS_REV0844.json`

### rev0845-w02-publish-queue-release-boundary-validation

Risk: a future rights-approved queue item could carry malformed date/path/decision metadata or a PUBLIC_SURFACE entry that uses parent traversal or a symlink, causing the publisher to read outside the archive or emit misleading public records.

Change: publish_queue_item.py now validates date and identifier shapes, checks decision_id equality, constrains public_paths and snapshot paths to clean archive-relative POSIX paths, and reads PUBLIC_SURFACE payloads only through regular non-symlink archive paths.

Status: `validated_with_clean_traversal_symlink_and_mismatch_fixtures`

Evidence:
- `scripts/publish_queue_item.py`
- `scripts/validate_publish_queue_item_release_boundary_rev0845.py`
- `AUDIT/PUBLISH_QUEUE_ITEM_RELEASE_BOUNDARY_REV0845.json`
- `AUDIT/PUBLISH_QUEUE_ITEM_NO_CLOBBER_REV0844.json`
- `AUDIT/PUBLISH_QUEUE_ITEM_ATOMIC_OUTPUTS_REV0843.json`

### rev0845-w03-rebuild-indexes-symlink-boundary-refactor

Risk: release-critical INDEX/MANIFEST/RO-Crate digest refreshes used file walkers and hash helpers that could follow symlinked files, silently digesting mutable host/cloudtainer targets under archive-relative names.

Change: rebuild_indexes.py now collects regular archive files through a symlink-rejecting os.walk, uses that collection for final index/manifest emission, and makes sha256_file/RO-Crate digest refreshes require regular files.

Status: `validated_with_clean_symlink_file_and_symlink_directory_fixtures`

Evidence:
- `scripts/rebuild_indexes.py`
- `scripts/validate_rebuild_indexes_symlink_boundary_rev0845.py`
- `AUDIT/REBUILD_INDEXES_SYMLINK_BOUNDARY_REV0845.json`
- `AUDIT/REBUILD_INDEXES_SOURCE_INDEX_SUBPROCESS_REV0843.json`

## Targeted validation
- `python3 -m py_compile scripts/*.py`
- `python3 scripts/build_rebuild_indexes_subprocess_refresh_audit_rev0839.py`
- `python3 scripts/build_publication_preflight_dry_run_safety_audit_rev0840.py`
- `python3 scripts/validate_publication_rights_gate_fresh_scan_rev0842.py`
- `python3 scripts/validate_publication_rights_gate_markdown_reference_forms_rev0844.py`
- `python3 scripts/validate_publication_rights_gate_symlink_boundary_rev0845.py`
- `python3 scripts/validate_publish_queue_item_atomic_outputs_rev0843.py`
- `python3 scripts/validate_publish_queue_item_no_clobber_rev0844.py`
- `python3 scripts/validate_publish_queue_item_release_boundary_rev0845.py`
- `python3 scripts/validate_rebuild_indexes_source_index_subprocess_rev0843.py`
- `python3 scripts/validate_rebuild_indexes_symlink_boundary_rev0845.py`
- `python3 scripts/validate_publication_preflight_dry_run_safety_rev0840.py`
- `python3 scripts/publication_rights_gate.py --context rev0845-overlay-probe (expected refusal)`

## Remaining risk
- Publication remains blocked pending owner-approved root/component LICENSE/NOTICE decisions and rights-ledger refresh.
- The overlay validators use controlled fixtures and do not replace a full canonical make rebuild-indexes / make gate run after applying the overlay patch.
- No-clobber output creation and rollback still are not a durable multi-file transaction against process kill or storage failure.
- The fresh license-reference scan checks local reference integrity and parser coverage; it does not infer license compatibility or legal sufficiency.

## Next practical move

After applying this overlay to the full canonical tree, run the full canonical rebuild/gate and check the symlink-boundary behavior against the actual corpus. The next rights move remains owner-approved licensing/notice content, followed by one canonical refresh of the rights ledger, SPDX, RO-Crate, and publication gate.
