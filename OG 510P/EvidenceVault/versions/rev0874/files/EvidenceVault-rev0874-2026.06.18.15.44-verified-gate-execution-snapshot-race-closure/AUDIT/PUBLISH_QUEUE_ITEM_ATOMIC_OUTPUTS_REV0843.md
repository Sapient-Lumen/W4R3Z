# Publish Queue Item Atomic Outputs Rev0843

- Status: `publish_queue_item_atomic_outputs_validated_refreshed_with_output_boundary_checks`
- Revision context: `rev0843-audit-refreshed-in-rev0847-overlay`
- Purpose: Validate atomic public-release output writes and rollback behavior in publish_queue_item.py.
- Risk reduced: Future publication writes still use fsynced temporary files, no-clobber commits for publication outputs, and rollback of only successfully created outputs after rev0845 path-boundary hardening.

- Changed script: `scripts/publish_queue_item.py`
- SHA-256: `6b0bd322ed8655b99eb199d6007eea2d94c7792f452c4bd4222a5ee405ba8802`

## Dynamic cases

- failing transition rolls back created snapshot/record/note outputs
- successful transition emits snapshot/record/note outputs
- fixtures emit no Python bytecode

## Limits

- The rollback is not crash-proof; it covers ordinary subprocess failure after output writes.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_publish_queue_item_atomic_outputs_rev0843.py`
- Return code: `0`
- Validator SHA-256: `e37dca6aaf5d9d1ad9c7af7ee128f36fde0fd639a611fa8465928b2695c87b24`

```text
publish-queue-item-atomic-outputs-rev0843: OK
```
