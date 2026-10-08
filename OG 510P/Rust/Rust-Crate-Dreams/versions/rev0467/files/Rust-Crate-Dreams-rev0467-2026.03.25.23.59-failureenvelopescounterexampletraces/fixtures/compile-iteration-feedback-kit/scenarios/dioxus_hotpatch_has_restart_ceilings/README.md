# Dioxus hotpatch still has restart ceilings

This scenario exists to force **P-0537** to export restart ceilings instead of only celebrating fast feedback.

Dioxus documents that several edit classes still require a full rebuild unless hotpatching is enabled, and that even with hotpatching there are limitations around globals, static initializers, and dependency/workspace edits.
