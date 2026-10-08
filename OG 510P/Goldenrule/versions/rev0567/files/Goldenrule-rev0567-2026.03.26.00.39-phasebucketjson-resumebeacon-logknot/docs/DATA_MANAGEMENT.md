# Data Management

## Artifact Classes

- `goldens/`: committed reference baselines.
- `artifacts/`: ephemeral outputs from checks/runs.
- `runs/`: experiment-run outputs.

## Retention

- Use `make clean-test-artifacts` (dry-run default) to prune stale files.
- Keep golden baselines small, textual, and reviewable.
- When `artifacts/reports` is the main retained growth surface, build `examples/snapshots/archive_report_hotspot_receipt.json` and compact the ranked hotspot families before adding new report fanout nearby.
- Before touching any specific hotspot family, build `examples/snapshots/archive_report_compaction_candidate_receipt.json` so compaction starts from citation-backed candidates instead of archive archaeology.
- Before deciding that a hotspot family needs a brand-new durable note, build `examples/snapshots/archive_report_semantic_handle_receipt.json` so archive shaping first reuses existing semantic handles that literal family-name matching may have missed; treat that receipt as a buffered hotspot scan that should also cover the one-trim-ahead rehearsal frontier.
- If the top hotspot table still contains large families with zero durable non-report handles even after that semantic-handle pass, build `examples/snapshots/archive_report_compaction_gap_receipt.json` so the next small retained addition unlocks future compaction instead of widening report fanout again; if that receipt is empty, treat the current hotspot surface as fully handle-covered and reuse existing citation handles rather than minting a new note.
- Once the current hotspot surface is handle-covered and you actually need bytes back, build `examples/snapshots/archive_report_compaction_manifest_receipt.json` so trimming happens from one exact file list with cited handles instead of hand-selecting report paths.
- Before removing the manifest paths, build `examples/snapshots/archive_report_compaction_rehearsal_receipt.json` so the first trim is rehearsed once: projected bytes reclaimed, projected leading remaining hotspot, and projected second-wave handle coverage should all be visible before any retained report files leave the tree; if that projected frontier is already fully handle-covered, future sessions can execute the cited first trim without minting another note first.
- Before any retained report path actually leaves the archive, build `examples/snapshots/archive_report_compaction_stage_receipt.json` so the cited manifest can be staged reversibly under `examples/scratch/archive_report_compaction_stage`, validated on the trimmed tree, and only then deleted; do not carry staged scratch across a revision zip.
- After a cited canonical trim actually executes, build `examples/snapshots/archive_report_compaction_execution_receipt.json` so the archive keeps one compact proof of which exact report frontier left the tree, how much net space was reclaimed after the pass's new control surfaces landed, and what refreshed frontier replaced it; start any later byte-saving from the refreshed manifest / rehearsal / stage receipts, and only mint another durable note if the refreshed gap or rehearsal receipts stop being fully handle-covered.

## Provenance

- Keep all claims linked to hashed artifacts and definitions.
- Export public bundles via redaction workflows.
