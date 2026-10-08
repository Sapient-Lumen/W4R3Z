# EvidenceVault rev0844 session review: no-clobber publication outputs and rights-gate Markdown coverage

Created: 2026-06-13T02:07:04+00:00

Scope: targeted overlay work over rev0843. This revision intentionally avoids broad registry expansion and focuses on two concrete release-safety seams that could matter after rights are eventually resolved.

## Substantive changes

### rev0844-w01-publish-queue-no-clobber-precise-rollback

Risk: rev0843 made the public release snapshot, JSON record, and Markdown note atomic, but the final commit still used `os.replace`. A concurrent publisher could create a release path after the pre-existence check and before the replace. Rollback also listed all intended outputs before knowing which files this process had actually created.

Change: `scripts/publish_queue_item.py` now creates publication outputs with `overwrite=False` through a same-directory temporary file and atomic hard-link commit. The helper fsyncs file bytes, sets a stable `0644` mode, fsyncs the parent directory where supported, and raises `FileExistsError` instead of overwriting a concurrent path. Rollback appends paths only after successful creation.

Status: `validated_with_helper_and_race_fixture`

Evidence:

- `scripts/publish_queue_item.py`
- `scripts/validate_publish_queue_item_no_clobber_rev0844.py`
- `AUDIT/PUBLISH_QUEUE_ITEM_NO_CLOBBER_REV0844.json`
- `AUDIT/PUBLISH_QUEUE_ITEM_ATOMIC_OUTPUTS_REV0843.json`

### rev0844-w02-rights-gate-markdown-reference-forms

Risk: the rev0842 fresh rights scan is release-critical, but its inline Markdown regex could miss common forms such as links with titles and reference-style definitions. That is exactly the kind of small parser blind spot that could become dangerous when the ledger eventually changes from blocked to ready.

Change: `scripts/publication_rights_gate.py` now recognizes inline Markdown links with optional titles, angle-wrapped targets, and Markdown reference definitions when they point at local `LICENSE`, `COPYING`, or `NOTICE`-like targets.

Status: `validated_with_missing_and_resolved_rights_ready_fixtures`

Evidence:

- `scripts/publication_rights_gate.py`
- `scripts/validate_publication_rights_gate_markdown_reference_forms_rev0844.py`
- `AUDIT/PUBLICATION_RIGHTS_GATE_MARKDOWN_REFERENCE_FORMS_REV0844.json`
- `AUDIT/PUBLICATION_RIGHTS_GATE_FRESH_REFERENCE_SCAN_REV0842.json`

### rev0844-w03-safety-audit-refresh

Risk: carried-forward safety audits would be misleading if their helper/script hashes and static snippets stayed at rev0843 after code changes.

Change: refreshed affected carried-forward audits and added a rev0844 targeted validation log.

Status: `targeted_audits_refreshed`

Evidence:

- `AUDIT/PUBLICATION_PREFLIGHT_DRY_RUN_SAFETY_REV0840.json`
- `AUDIT/PUBLICATION_RIGHTS_GATE_FRESH_REFERENCE_SCAN_REV0842.json`
- `AUDIT/PUBLISH_QUEUE_ITEM_ATOMIC_OUTPUTS_REV0843.json`
- `VALIDATION/rev0844_targeted_validation.txt`

## Targeted validation

- `python3 -m py_compile scripts/*.py`
- `python3 scripts/build_rebuild_indexes_subprocess_refresh_audit_rev0839.py`
- `python3 scripts/build_publication_preflight_dry_run_safety_audit_rev0840.py`
- `python3 scripts/validate_rebuild_indexes_source_index_subprocess_rev0843.py`
- `python3 scripts/validate_publication_preflight_dry_run_safety_rev0840.py`
- `python3 scripts/validate_publication_rights_gate_fresh_scan_rev0842.py`
- `python3 scripts/validate_publication_rights_gate_markdown_reference_forms_rev0844.py`
- `python3 scripts/validate_publish_queue_item_atomic_outputs_rev0843.py`
- `python3 scripts/validate_publish_queue_item_no_clobber_rev0844.py`
- `python3 scripts/publication_rights_gate.py --context rev0844-overlay-probe` — expected refusal

## Remaining risk

- Publication remains blocked pending owner/upstream rights decisions and root/component `LICENSE`/`NOTICE` material.
- The overlay validator fixtures do not replace a full canonical `make rebuild-indexes` / `make gate` run after patch application.
- No-clobber creation is not a durable multi-file transaction against process kill or storage failure.
- The fresh local-reference scan checks reference integrity only; it does not infer legal sufficiency.

## Next practical move

After applying this overlay to the full canonical tree, run the full canonical rebuild/gate. The next rights move is still owner-approved licensing/notice content, not more registry scaffolding.
