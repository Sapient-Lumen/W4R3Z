# alltargets_false_dev_proc_macro_gap

This scenario exists to keep the crate honest about target-class coverage.

If rust-analyzer stops passing `--all-targets`, a dev-dependency proc-macro lane may never get built.
The bundle should say that the proc-macro is unavailable **because the lane was omitted**, not just emit a generic proc-macro failure story.
