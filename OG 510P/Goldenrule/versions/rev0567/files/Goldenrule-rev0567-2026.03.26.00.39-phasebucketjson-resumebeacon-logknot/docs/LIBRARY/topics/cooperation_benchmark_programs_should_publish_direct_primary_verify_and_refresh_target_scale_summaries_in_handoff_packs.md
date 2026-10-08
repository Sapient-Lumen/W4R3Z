# cooperation_benchmark_programs_should_publish_direct_primary_verify_and_refresh_target_scale_summaries_in_handoff_packs

A compact handoff pack should publish one direct `primary_verify_target_scale_summary` and one direct `primary_refresh_target_scale_summary` witness alongside the first machine targets.

Those fields are not a second report family. They are compact aliases over retained report counts that keep the first machine step locally interpretable.

- `primary_verify_target_scale_summary` should be a strict alias of the retained citation-surface counts already carried by `artifacts/reports/cooperation_benchmark_card_citation_surface.json`.
- `primary_refresh_target_scale_summary` should be a strict alias of the retained inventory counts already carried by `artifacts/reports/cooperation_benchmark_card_inventory.json`.
- inheritors should not have to open the report JSON or mentally combine multiple count witnesses just to understand the scale of the first verify / refresh targets.
