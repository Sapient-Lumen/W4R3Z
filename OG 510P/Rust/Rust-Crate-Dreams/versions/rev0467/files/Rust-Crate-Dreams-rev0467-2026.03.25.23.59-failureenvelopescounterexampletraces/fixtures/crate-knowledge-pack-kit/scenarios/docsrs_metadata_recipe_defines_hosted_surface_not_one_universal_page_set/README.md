# Scenario: docs.rs metadata recipe defines a hosted surface, not one universal page set

Problem:
A crate has docs.rs metadata that changes default target, enabled features, and built targets.
A downstream tool is about to treat the hosted docs as a universal view of the crate.

What this scenario proves:
A build-surface receipt must preserve the recipe that shaped the hosted surface.

Good outcome:
The bundle records the hosted docs surface with explicit target and feature posture so later consumers can compare it against other recipes instead of over-reading it.
