# label_scoped_override_vs_workspace_baseline

This scenario exists to keep the crate honest about selection scope.

If rust-analyzer uses an override command with `{label}`, the observed run is narrower than a workspace build claim.
The bundle should freeze that comparison boundary explicitly instead of quietly implying workspace parity.
