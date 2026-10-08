# Cooperation benchmark programs should publish role-annotated entry targets in handoff packs

When a compact-card handoff pack already publishes one lineage-local `primary_open_path` plus exact head-card paths, one more compact inheritor aid is worth keeping explicit: **publish a tiny ordered `entry_targets` family that reuses those same retained paths but adds small role codes explaining why each file belongs in the local handoff reentry set**.

The doctrine is:

1. keep the family lineage-local and tiny, using only already-retained paths that the pack already points at directly (for example the primary rendered markdown, head card, and verified freeze receipt);
2. keep the order stable and reentry-first, starting with the published `primary_open_path`;
3. attach only a small deduplicated `role_codes` set per path, so the inheritor can tell whether a file is the primary open target, a head card, or the verified freeze receipt without guessing from suffixes or scanning the broader file manifest;
4. require the target paths to remain members of both the pack manifest and the local `must_read_paths` sequence, so the helper stays a compact annotation of retained evidence rather than a second browsing semantics.

This keeps lineage-local handoff reentry self-sufficient without widening the benchmark card, citation surface, or file manifest.
