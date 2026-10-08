# publish_queue_item public_paths consistency

- Revision: `rev0848`
- Created: `2026-06-13T12:31:00Z`
- Target: `scripts/publish_queue_item.py`
- Status: `passed_after_targeted_validation`
- Last overlay refresh: `rev0849` / `2026-06-13T14:21:00Z`

## Risk reduced

A future rights-approved release record could claim paths that were not actually snapshotted/digested in published/PUBLIC_SURFACE.json.

## Changes observed

- Requires decision.public_paths to be a non-empty duplicate-free list for publication.
- Checks decision-declared public paths against the built PUBLIC_SURFACE snapshot and its source manifest.
- Rejects duplicate PUBLIC_SURFACE entry paths before release records are emitted.
- rev0849 refresh: rejects PUBLIC_SURFACE snapshot entry points that are not explicitly authorized by decision.public_paths.

## Validator

- `scripts/validate_publish_queue_item_public_path_consistency_rev0848.py`

## Validator assertions

- declared PUBLIC_SURFACE entry points pass when all are authorized
- declared path absent from PUBLIC_SURFACE fails closed
- empty/duplicate decision public_paths fail closed
- duplicate PUBLIC_SURFACE entry paths fail closed

## Publication rights effect

None. Publication remains blocked pending owner-approved rights files and component license conclusions.
