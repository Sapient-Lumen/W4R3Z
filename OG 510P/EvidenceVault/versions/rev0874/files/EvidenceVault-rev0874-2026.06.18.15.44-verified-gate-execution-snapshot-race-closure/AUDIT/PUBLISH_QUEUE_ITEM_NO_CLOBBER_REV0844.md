# Publish Queue Item No Clobber Rev0844

- Status: `publish_queue_item_no_clobber_validated_refreshed_with_output_boundary_checks`
- Revision context: `rev0844-audit-refreshed-in-rev0847-overlay`
- Purpose: Harden the future rights-approved queue publisher against concurrent clobber races and rollback of outputs not created by the failing process.
- Risk reduced: Public release snapshot, JSON record, and Markdown note creation still uses no-clobber atomic hard-link commits after rev0845 path-boundary hardening; rollback only removes paths after this process successfully creates them.

- Changed script: `scripts/publish_queue_item.py`
- SHA-256: `6b0bd322ed8655b99eb199d6007eea2d94c7792f452c4bd4222a5ee405ba8802`

## Dynamic cases

- atomic helper creates new publication file with no-clobber mode and 0644 permissions
- second no-clobber write raises FileExistsError and preserves existing bytes
- overwrite=True remains available for non-publication replacement use
- simulated race after snapshot creation leaves race-owned JSON record intact while rolling back only the created snapshot
- rev0843 atomic-output rollback validator still passes after the no-clobber refactor

## Limits

- No-clobber output creation is still not a full multi-file transaction across process kill or storage failure.
- The dynamic race probe is an in-process monkeypatch fixture that exercises the exact helper and main-path rollback logic without publishing the real cube.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_publish_queue_item_no_clobber_rev0844.py`
- Return code: `0`
- Validator SHA-256: `f5a04386e7a3c89a25e4dc918ea88aea5d907bc4e630436c3d8e7295adc7a8b4`

```text
publish-queue-item-no-clobber-rev0844: OK
```
