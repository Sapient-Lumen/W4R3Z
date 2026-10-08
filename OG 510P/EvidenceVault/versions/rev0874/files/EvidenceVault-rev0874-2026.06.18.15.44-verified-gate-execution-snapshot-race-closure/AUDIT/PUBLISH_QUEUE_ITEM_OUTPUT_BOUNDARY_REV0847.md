# Publish-queue output boundary audit — rev0847

- Status: `publish_queue_item_output_parent_and_transition_boundary_hardened`
- Revision context: `rev0847-overlay-over-rev0846-over-rev0840`
- Purpose: Prevent future rights-approved queue publication writes and transition execution from crossing archive-output symlink boundaries.
- Risk reduced: Public release snapshot/record/note writes now reject output destinations outside ROOT or through symlinked parent components, and the final transition script path is validated as an archive-local regular file before subprocess execution.

- Changed script: `scripts/publish_queue_item.py`
- SHA-256: `6b0bd322ed8655b99eb199d6007eea2d94c7792f452c4bd4222a5ee405ba8802`

## Dynamic cases

- clean no-clobber publication-output helper write still succeeds under a fixture root
- publication-output target outside the archive root is rejected before parent directories are created
- symlinked top-level output parent published/ is rejected before same-directory temporary-file creation
- symlinked nested output parent published/releases/ is rejected before bytes are written outside the archive
- symlinked scripts/transition_queue_item.py is rejected before subprocess execution
- rev0844 no-clobber/rollback validator still passes after output-boundary hardening

## Limits

- This is still a best-effort multi-file operation; it does not make queue publication crash-transactional across process kill or storage failure.
- The rights gate remains the first publication blocker; this change hardens the path that will matter only after owner-approved rights decisions exist.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_publish_queue_item_output_boundary_rev0847.py`
- Return code: `0`
- Validator SHA-256: `ab0faa236dfc1236d45873eae4884157f72b48dca1131d3f3b84a0d23103b3ad`

```text
publish-queue-item-output-boundary-rev0847: OK
```
