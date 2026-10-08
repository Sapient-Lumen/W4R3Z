# Cooperation benchmark programs should publish head-card paths and a primary open path in handoff packs

When a compact-card archive already ships a minimal lineage handoff pack, one more compact inheritor aid is worth keeping explicit: **publish the exact retained head-card paths plus the pack's preferred first-open path**.

Why this belongs in the archive:

- head-card ids tell the inheritor *which lineage head won*, but not yet *which retained file paths to open*;
- the handoff pack is already the lineage-local reentry object, so it should not force a second cross-reference through heads or control-plane surfaces just to recover local paths;
- the first-open path should stay derived from already-retained lineage artifacts rather than creating a second narrative guide.

Operational rule:

1. publish `citation_head_card_path` and `operational_head_card_path` alongside the head-card ids in every resolved pack;
2. publish one `primary_open_path`, preferring the rendered citation-head markdown when present and otherwise falling back to the retained machine-readable head card path;
3. keep `must_read_paths` ordered so the program doctrine comes first and the lineage-local `primary_open_path` comes immediately after it;
4. validate that the published paths are present in the pack's retained file manifest so the handoff object stays self-sufficient.

This keeps lineage-local reentry cheap and auditable without widening the cards, receipts, or citation basis.
