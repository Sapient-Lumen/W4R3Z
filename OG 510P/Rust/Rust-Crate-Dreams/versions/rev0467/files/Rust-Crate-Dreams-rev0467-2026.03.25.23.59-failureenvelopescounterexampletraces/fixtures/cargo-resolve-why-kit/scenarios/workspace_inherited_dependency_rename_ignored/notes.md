# Scenario: workspace-inherited dependency rename is ignored

Why this matters: a workspace member may try to write `package = "itoa"` on an inherited dependency to rename it locally, but current Cargo behavior can ignore that key. A receiver-facing resolver bundle should preserve that the rename intent existed, that it did not take effect, and that another person should not trust the member-local alias as real.
