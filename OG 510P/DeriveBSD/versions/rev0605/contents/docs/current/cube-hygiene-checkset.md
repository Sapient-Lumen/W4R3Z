# Current cube hygiene checkset

The live hygiene checkset is `cube.hygiene.checkset.manifest` for 2026-06-18r630. It keeps the full `tools/hygiene.py` inventory visible while allowing focused profiles for release work, including release-critical, post-detach, generated-surface, and schema-cube-audit slices. r630 keeps the executable runtime golden-thread smoke release-critical and now requires repository-snapshot admission before catalog projection: consumed fixture package bytes, admitted snapshot rows, and catalog projections must agree before runtime evidence can claim a closed dependency set.

Current counts:

- top_level_check_scripts: 385
- hygiene_referenced_check_scripts: 385
- non_check_validators_in_hygiene: 2
- release_critical_count: 52
- post_detach_focus_count: 39
- generated_surface_count: 2
- schema_cube_audit_count: 3
- deep_contract_count: 291
- missing_from_hygiene_count: 0
- stale_hygiene_reference_count: 0
- duplicates_count: 0
- shards_total: 5

Release-critical remains the practical gate for cuts; deep-contract remains the broader audit surface.

Schema and canonical example:

- `spec/cube.hygiene.checkset.manifest.schema.json`
- `spec/examples/cube.hygiene.checkset.manifest.json`

Checker: `tools/check_cube_hygiene_checkset_manifest.py`

Last updated: 2026-06-18r630
