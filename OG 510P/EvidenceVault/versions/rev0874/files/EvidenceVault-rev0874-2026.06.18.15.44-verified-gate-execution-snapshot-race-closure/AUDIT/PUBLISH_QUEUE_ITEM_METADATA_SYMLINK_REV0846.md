# Publish Queue Item Metadata Symlink Rev0846

- Status: `publish_queue_item_queue_metadata_symlink_boundary_validated_refreshed_with_output_boundary_checks`
- Revision context: `rev0846-audit-refreshed-in-rev0847-overlay`
- Purpose: Prevent future publication queue metadata, decision JSON, and revision-source reads from crossing symlink boundaries before publication records are emitted.
- Risk reduced: A future rights-approved publisher cannot read a queue item, decision file, CHANGELOG, or hashed publication input through an archive-internal symlink that points to mutable host/cloudtainer data.

- Changed script: `scripts/publish_queue_item.py`
- SHA-256: `6b0bd322ed8655b99eb199d6007eea2d94c7792f452c4bd4222a5ee405ba8802`

## Dynamic cases

- clean queue item lookup by item_id still succeeds
- symlinked queue state item JSON is rejected without reading target bytes
- symlinked queue state directory is rejected
- symlinked decision JSON is rejected
- symlinked CHANGELOG.md is rejected before deriving the release revision

## Limits

- This hardens local metadata reads; it does not make the multi-file publish operation crash-transactional.
- The script still depends on transition_queue_item.py in the complete canonical tree for the final state move.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_publish_queue_item_metadata_symlink_rev0846.py`
- Return code: `0`
- Validator SHA-256: `d4ba226566469939b3f3303e5f6428a472487f427c2c004cff527c20cb2cac35`

```text
publish-queue-item-metadata-symlink-rev0846: OK
```
