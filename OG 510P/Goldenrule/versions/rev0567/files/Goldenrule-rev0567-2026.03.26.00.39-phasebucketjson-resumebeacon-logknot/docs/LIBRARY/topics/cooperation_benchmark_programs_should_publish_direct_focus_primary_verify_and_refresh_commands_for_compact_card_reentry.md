# Cooperation benchmark programs should publish direct focus-primary verify and refresh commands for compact-card reentry

Once the compact-card stack already publishes a deterministic focus lineage plus a lineage-local handoff pack, keep one further step explicit on the top-level reentry surfaces: publish one direct `focus_primary_verify_command` and one direct `focus_primary_refresh_command` witness.

Those fields should be pure aliases of the chosen focus lineage's handoff-pack `primary_verify_command` and `primary_refresh_command`, not a second command-selection semantics.

This keeps the control plane, next-action witness, and typed next-action surface locally actionable as an `open this, then run this` digest without forcing inheritors to hop into the handoff pack just to recover the canonical first local check or rebuild step for the chosen lineage.
