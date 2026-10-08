# Software failure field sketch

Rev0010 does not introduce a separate schema file yet; software/IT records remain `ENG` records with a `software_failure_fields` object inside `type_payload`.

Recommended fields:

- `change_surface`
- `latent_code_path`
- `validation_boundary`
- `warning_surface`
- `monitoring_dependency`
- `asset_or_dependency_visibility`
- `blast_radius`
- `privilege_level`
- `rollback_or_stop_authority`
- `recovery_friction`
- `source_provenance_class`
- `non_equivalence_warning`

Required guardrail: never collapse vulnerability, exploit, breach, outage, deployment error, and postmortem into one undifferentiated “software failure” label.
