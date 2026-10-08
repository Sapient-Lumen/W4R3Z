# Cooperation benchmark programs should publish direct primary verify and refresh commands in handoff packs

Compact-card handoff packs already carry the exact retained files, must-read order, and full verify / refresh command arrays needed for local inheritance.

Keep one further step explicit: publish one direct `primary_verify_command` and one direct `primary_refresh_command` witness on each lineage-local pack. Those fields should be pure aliases of the first entries in `verify_commands` and `refresh_commands`, not a second command-selection semantics.

This keeps the handoff pack locally actionable as an `open this, then run this` surface without widening the retained basis or forcing inheritors to scan command arrays for the canonical first local check / rebuild step.
