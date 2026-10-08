# Scenario: edited manifest not preserved

The caller provides an edited manifest representation that removes some workspace members for a per-package resolution experiment.
The command path re-reads manifests from disk, so the resulting receipt must say the edited intent was **not** consumed directly.
