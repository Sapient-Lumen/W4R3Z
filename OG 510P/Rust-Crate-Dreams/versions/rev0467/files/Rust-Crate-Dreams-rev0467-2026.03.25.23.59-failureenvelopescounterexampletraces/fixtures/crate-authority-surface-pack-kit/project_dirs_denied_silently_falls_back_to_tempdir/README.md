# project_dirs_denied_silently_falls_back_to_tempdir

This scenario exists to keep **P-0519** honest about **refusal posture**.

The crate advertises an `offline_readonly` or `sandbox_ready` profile, but on denied project-directory discovery it silently falls back to an ambient temp directory.

A worthy authority-surface crate should not summarize this as “works without project dirs”.
It should say that denial causes a **silent fallback** that widens authority and changes persistence semantics.
