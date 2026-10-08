# Rebuild Indexes Source Index Subprocess Rev0843

- Status: `source_index_refresh_subprocess_json_handoff_validated_refreshed_with_atomic_output_checks`
- Revision context: `rev0843-audit-refreshed-in-rev0847-overlay`
- Purpose: Validate that rebuild_indexes.py refreshes build_source_index.py through a subprocess and consumes SOURCE_INDEX.json as a handoff contract.
- Risk reduced: The source-index builder remains isolated from the long-lived rebuild coordinator after rev0845 symlink-boundary changes.

- Changed/rebuild script: `scripts/rebuild_indexes.py`
- SHA-256: `df31735a8f0d6bbeec632094880ed2e6f218a57f623d01c522766f2422b12477`

## Required behavior

- build_source_index.py is launched through run_material_builder_subprocess("build_source_index")
- SOURCE_INDEX.json must parse as a non-empty JSON object
- SOURCE_INDEX.md must exist and be non-empty
- Non-zero child exits fail before later material refreshes
- Python bytecode remains suppressed in fixture child runs

## Limits

- This overlay validates the handoff with fixtures. A full canonical tree should still run the normal rebuild/gate sequence after applying the patch.

## Validator

- Command: `/opt/pyvenv/bin/python3 scripts/validate_rebuild_indexes_source_index_subprocess_rev0843.py`
- Return code: `0`
- Validator SHA-256: `f29f3257b77f33b85fc6c46d23e0f8b6e37c2fa7a494d9fea5bfd9c1e7588514`

```text
rebuild-indexes: refreshing build_source_index.py
build-source-index-fixture: OK
rebuild-indexes: refreshing build_source_index.py
intentional fixture failure
rebuild-indexes: refreshing build_source_index.py
rebuild-indexes-source-index-subprocess-rev0843: OK
```
