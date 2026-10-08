# Cooperation benchmark programs should publish direct primary verify and refresh outcome summaries in handoff packs

A compact handoff pack should publish one direct `primary_verify_outcome_summary` and one direct `primary_refresh_outcome_summary` witness.

Why:
- the inheritor already sees the first command, target, subject role, and intent, but still has to infer the immediate expected result;
- one short outcome sentence makes the first local check or rebuild step legible without a second report family.

Operational rule:
- these outcome summaries should remain strict aliases of the retained command target and command kind, not a second command-selection semantics.
