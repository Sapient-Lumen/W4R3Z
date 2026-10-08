# check_workspace_false_first_run_leakage

This scenario exists to keep the crate honest about startup behavior.

If policy expects package-scoped diagnostics but the first observed run still leaks broader workspace diagnostics, the bundle should not normalize that away as harmless noise.
It should freeze the mismatch as conservative or manual-review-required support truth.
