# Cooperation benchmark programs should publish direct primary verify and refresh subject-role codes in handoff packs

A compact handoff pack should publish one direct `primary_verify_subject_role_code` and one direct `primary_refresh_subject_role_code` witness alongside the first verify / refresh commands and their retained-path targets.

Why:
- inheritors should not have to scan `role_codes` arrays just to recover the main subject of the first local check or rebuild step;
- the command's main subject should remain a tiny alias of the already-retained target roles, not a second command-selection semantics.

Operational rule:
- `primary_verify_subject_role_code` and `primary_refresh_subject_role_code` should equal the non-primary subject role from `primary_verify_target.role_codes` and `primary_refresh_target.role_codes` respectively.
