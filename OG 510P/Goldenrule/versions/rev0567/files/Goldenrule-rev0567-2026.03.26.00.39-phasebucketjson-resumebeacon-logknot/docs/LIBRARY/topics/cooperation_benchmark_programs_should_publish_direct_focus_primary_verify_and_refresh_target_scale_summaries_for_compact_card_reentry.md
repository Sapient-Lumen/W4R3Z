# cooperation_benchmark_programs_should_publish_direct_focus_primary_verify_and_refresh_target_scale_summaries_for_compact_card_reentry

A compact-card reentry surface should publish one direct `focus_primary_verify_target_scale_summary` and one direct `focus_primary_refresh_target_scale_summary` witness alongside the first focus-machine targets.

Those fields are not a second report family. They are compact aliases of the focus-lineage handoff-pack semantics already retained for the chosen lineage.

- `focus_primary_verify_target_scale_summary` and `focus_primary_refresh_target_scale_summary` should agree with the chosen focus-lineage handoff pack when one exists.
- inheritors should not have to open the first focus-machine report JSON or mentally combine multiple retained counts just to understand the scale of the first verify / refresh steps.
