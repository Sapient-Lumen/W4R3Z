# rust_analyzer_separate_target_dir

Positive control for P-0494.

The bundle should explicitly say that separate target dirs reduce shared-lock pressure while introducing artifact duplication.
That trade-off is not an error; it is part of the receiver-facing truth.
