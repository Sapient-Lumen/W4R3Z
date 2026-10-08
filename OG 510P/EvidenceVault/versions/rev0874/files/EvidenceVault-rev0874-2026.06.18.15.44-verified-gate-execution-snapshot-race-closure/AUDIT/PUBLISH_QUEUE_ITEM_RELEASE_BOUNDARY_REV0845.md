# Publish Queue Item Release Boundary Rev0845

- Status: `publish_queue_item_release_boundary_validated_refreshed_with_output_boundary_checks`
- Revision context: `rev0845-audit-refreshed-in-rev0847-overlay`
- Purpose: Constrain publish_queue_item.py release IDs, queue metadata, public paths, and public-surface entry reads to clean archive-relative regular files.
- Risk reduced: A malformed queue item, decision, or PUBLIC_SURFACE entry can no longer cause path traversal, symlink reads outside the archive, or mismatch between queued decision identity and the decision file used to publish.

- Changed script: `scripts/publish_queue_item.py`
- SHA-256: `6b0bd322ed8655b99eb199d6007eea2d94c7792f452c4bd4222a5ee405ba8802`

## Dynamic cases

- clean PUBLIC_SURFACE fixture still builds a dry-run snapshot object
- PUBLIC_SURFACE entry path with parent traversal fails closed before reading payload bytes
- PUBLIC_SURFACE entry path that is a symlink to an outside file fails closed
- queue item date must be YYYY-MM-DD
- decision public_paths reject parent traversal
- decision_id mismatch between queue item and decision file fails closed

## Limits

- This validates path/identity boundaries; it does not make publication legal while the rights gate remains blocked.
- No-clobber creation remains a best-effort multi-file sequence rather than a crash-proof transaction.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_publish_queue_item_release_boundary_rev0845.py`
- Return code: `0`
- Validator SHA-256: `2c1a0be57267ea21ff954326ec6ec1dd5974aeff5324422aac5bfe4de944e10d`

```text
publish-queue-item-release-boundary-rev0845: OK
```
