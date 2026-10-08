# Cooperation benchmark programs should publish direct focus primary verify and refresh subject-role codes for compact-card reentry

A compact-card reentry surface should publish one direct `focus_primary_verify_subject_role_code` and one direct `focus_primary_refresh_subject_role_code` witness alongside the first focus commands and their retained-path targets.

Why:
- inheritors should not have to decode target tuples or scan role arrays to tell what the first focus commands are mainly about;
- the focus command subject should stay a tiny alias of the chosen focus lineage handoff pack rather than a second reentry semantics.

Operational rule:
- `focus_primary_verify_subject_role_code` and `focus_primary_refresh_subject_role_code` should match the corresponding subject-role codes from the chosen focus lineage handoff pack when one exists.
