# rebuild_indexes material-builder subprocess boundary

- Revision: `rev0848`
- Created: `2026-06-13T12:31:00Z`
- Target: `scripts/rebuild_indexes.py`
- Status: `passed_after_targeted_validation`

## Risk reduced

The rebuild coordinator had moved material builders to subprocesses, but the subprocess target path itself was not yet symlink/root-boundary hardened.

## Changes observed

- Adds archive_python_script_path() with Python-module-name shape checking.
- Rejects symlinked builder scripts and symlinked scripts/ directories before subprocess execution.
- Rejects missing/non-regular material builders before invoking Python.

## Validator

- `scripts/validate_rebuild_indexes_material_builder_boundary_rev0848.py`

## Validator assertions

- regular builder path passes
- unsafe module names fail closed
- symlinked builder file fails before execution
- symlinked scripts directory fails before execution
- missing builder fails before execution

## Publication rights effect

None. Publication remains blocked pending owner-approved rights files and component license conclusions.
