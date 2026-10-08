# Compact-card reentry should publish direct semantic target-size counts for first focus commands

A compact-card reentry surface should publish one direct `focus_primary_verify_target_citation_entry_count` witness and one direct `focus_primary_refresh_target_card_count` witness alongside the first focus-machine targets.

Why: path, bytes, and sha256 tell inheritors which retained files the first focus commands touch, but not the logical scale of those report objects. A direct citation-entry count for the first focus verify target and a direct card count for the first focus refresh target make the first machine steps locally auditable without opening the JSON.

Operational note:

- `focus_primary_verify_target_citation_entry_count` and `focus_primary_refresh_target_card_count` should agree with the chosen focus-lineage handoff pack when one exists.
- These fields are not a second sizing semantics. They are a compact semantic audit aid over the already-retained first focus-machine targets.
