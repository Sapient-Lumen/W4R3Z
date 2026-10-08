# Compact-card handoff packs should publish direct semantic target-size counts

A compact handoff pack should publish one direct `primary_verify_target_citation_entry_count` witness and one direct `primary_refresh_target_card_count` witness alongside the first machine targets.

Why: path, bytes, and sha256 tell inheritors which retained files the first commands touch, but not the logical scale of those report objects. A direct citation-entry count for the first verify target and a direct card count for the first refresh target make the first machine steps locally auditable without opening the JSON.

Operational note:

- `primary_verify_target_citation_entry_count` should be a strict alias of `artifacts/reports/cooperation_benchmark_card_citation_surface.json` → `counts.citation_entry_count`.
- `primary_refresh_target_card_count` should be a strict alias of `artifacts/reports/cooperation_benchmark_card_inventory.json` → `counts.card_count`.
- These fields are not a second sizing semantics. They are a compact semantic audit aid over the already-retained first machine targets.
