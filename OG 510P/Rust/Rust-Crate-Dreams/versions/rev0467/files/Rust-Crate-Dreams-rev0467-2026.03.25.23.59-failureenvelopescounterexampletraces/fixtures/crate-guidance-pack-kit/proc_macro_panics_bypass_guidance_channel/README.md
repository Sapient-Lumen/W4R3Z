# Scenario — proc-macro panics bypass the guidance channel

A proc-macro crate documents a structured error path via `proc-macro-error2`, but one misuse case still panics before the expected diagnostic is emitted.

Why it matters:
- a maintainer may believe the crate has a structured proc-macro guidance surface,
- but `proc-macro-error2` explicitly warns that panics do not display those errors,
- so channel truth must distinguish supported emission paths from panic-only failure.
