# Docs.rs Build Parity & Evidence Kit fixtures

These fixtures are for **docs.rs parity** artifacts, not general project support contracts.
They should answer “what docs.rs-facing configuration and hosted constraints mattered, and how did a local attempt drift?”

Scenario families in this pass:
- `default_targets_shift_after_2025_change/`
- `docsrs_cfg_only_final_rustdoc/`
- `readonly_fs_requires_out_dir/`
- `too_many_targets_limit/`
- `network_blocked_but_local_preflight_green/`
- `missing_native_dependency_in_docsrs_env/`
- `build_log_truncation_masks_root_cause/`
