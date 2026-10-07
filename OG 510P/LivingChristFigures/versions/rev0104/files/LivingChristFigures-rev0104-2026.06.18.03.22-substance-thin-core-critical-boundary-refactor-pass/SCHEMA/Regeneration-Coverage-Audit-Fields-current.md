# Regeneration-Coverage-Audit Field Schema — current

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| coverage_id | yes | regen_cov_NNNN | Stable row identifier. |
| surface_path | yes | package-relative path or . | Surface or package summary row being checked. |
| surface_kind | yes | root_current_csv|meta_current_csv|schema_current_csv|governance_current_csv|public_current_csv|generated_primary_artifact|regeneration_output|package_summary | Kind of surface/output under coverage review. |
| coverage_class | yes | slug | Regeneration/provenance/seed/late-closure classification. |
| generator_or_owner | recommended | tools/*.py or owner label | Tool or deliberate owner responsible for the surface. |
| in_generated_provenance | yes | yes|no | Whether the surface is listed in Generated-Artifact-Provenance primary artifact specs. |
| in_regeneration_plan | yes | yes|no | Whether the surface is declared as an output in the regeneration sequence plan. |
| in_report_contract | yes | yes|no | Whether the surface is covered by the report-contract registry. |
| severity | yes | high|info | Release-blocking severity classification. |
| status | yes | pass|fail | Check outcome. |
| note | yes | free text | Reason for the classification or remediation detail. |
