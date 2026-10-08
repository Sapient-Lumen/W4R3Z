# Cooperation benchmark programs should publish direct primary verify and refresh intent summaries in handoff packs

A compact-card handoff pack can already name the first verify command, the first refresh command, their retained targets, and the targets' role codes.

That still leaves one local decode step for inheritors: they must mentally combine a script name with a role code just to recover the one-line purpose of the step.

A good handoff pack should therefore publish one direct `primary_verify_intent_summary` and one direct `primary_refresh_intent_summary` witness.

Those summaries should stay tiny, deterministic, and subordinate to the retained command and target fields. They are not a second command-selection semantics; they are just the last small inheritor-facing gloss needed to read the first local step without reconstruction.
