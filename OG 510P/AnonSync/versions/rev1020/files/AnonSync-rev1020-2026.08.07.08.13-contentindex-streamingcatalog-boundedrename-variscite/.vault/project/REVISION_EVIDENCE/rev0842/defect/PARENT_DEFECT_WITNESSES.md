# rev0841 parent defect witnesses

The witness files are line-numbered excerpts from the sealed rev0841 parent whose archive
SHA-256 is recorded in `LINEAGE.json`.

- `parent_local_jsonl_quadratic_batch_copy.txt` shows every staged row copying the entire
  `canonical_lines` vector before batch commit. This is the direct O(N^2) copy path removed
  in rev0842.
- `parent_snapshot_manifest_live_json.txt` shows signing input, trust checks, and snapshot
  comparisons traversing the broad parsed JSON payload rather than one frozen owner.
- `parent_runner_local_reader.txt` shows a separate `ifstream`-based bounded reader. It
  capped bytes but did not establish the stronger opened-object, special-file,
  final-symlink, mutation, or single-link properties now shared by the production readers.

These excerpts establish the parent shapes; they are not synthetic benchmark results.
No compiled executable or generated binary is packaged.
