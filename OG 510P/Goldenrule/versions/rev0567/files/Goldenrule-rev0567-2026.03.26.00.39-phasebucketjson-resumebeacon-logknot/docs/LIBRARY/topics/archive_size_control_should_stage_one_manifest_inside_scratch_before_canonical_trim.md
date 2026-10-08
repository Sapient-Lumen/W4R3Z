# Archive size control should stage one manifest inside scratch before canonical trim

When the archive finally needs to reclaim bytes from a cited exact-file compaction manifest, the inheritor should first stage those report paths under one temporary `examples/scratch/archive_report_compaction_stage` mirror, validate the trimmed tree, and only then delete the staged scratch copy.

Why:
- staging keeps the first trim reversible while the inheritor rebuilds the hotspot and package receipts on the post-manifest tree,
- the stage mirror can preserve exact per-file hashes and restore paths without retaining another bulky report family,
- and the package boundary still remains strict because staged scratch must be deleted before the next revision zip is cut.

Operational rule:
1. cite the durable handles already attached to the manifest,
2. move the exact report paths into the scratch-stage mirror,
3. rebuild the archive-size receipts on the trimmed tree,
4. confirm the trimmed tree is still semantically handle-covered and package-ready,
5. then delete the staged scratch copy and return to a scratch-free package boundary.

Use `examples/snapshots/archive_report_compaction_stage_receipt.json` as the compact retained receipt for that reversible staging plan.
