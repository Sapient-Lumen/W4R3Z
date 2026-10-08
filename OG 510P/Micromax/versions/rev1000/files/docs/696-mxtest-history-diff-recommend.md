# mxtest aggregate history, manifest diff, and chunk recommendation (rev752)

Rev748 through rev751 made long pytest runs increasingly explicit: source/package resource checks, deterministic chunks, segment/duration scheduling, and one checkpointed all-chunks manifest. Rev752 makes that manifest feed the next run instead of sitting as passive evidence.

## Boundary

A rev751 all-chunks manifest may contain per-file rows under each `chunk_results[*].files` entry when the run used `--isolate-files`. Rev750's duration scheduler only read top-level `files` rows from one selected run, so the most useful artifact in the repo could not directly become `--history` input. Rev752 changes `load_duration_history(...)` to read both shapes:

- top-level `files` rows from a single selected run
- nested `chunk_results[*].files` rows from an aggregate all-chunks run

When multiple histories mention the same file, the largest observed duration still wins. A cold, slow, or unlucky run is therefore not erased by a later warm-cache run.

## Manifest diffing

Use:

```bash
python tools/mxtest.py --diff-manifests OLD.json NEW.json
```

The diff path does not collect or run tests. It compares summary fields such as `collected`, `selected`, `strategy`, `run_chunks`, `nodeids_digest`, `status`, `complete`, and `chunk_status_counts`, then compares per-chunk `selected`, `strategy`, `first`, `last`, `nodeids_digest`, `status`, and `returncode` fields when both manifests have indexed chunk results.

Exit codes:

- `0`: no differences detected by the supported comparison
- `1`: differences detected
- `2`: malformed input or usage error

The optional `--json PATH` flag writes a machine-readable diff payload.

## Chunk recommendation

Use:

```bash
python tools/mxtest.py --recommend-chunks .artifacts/mxtest-all.json --target-seconds 300
```

The recommendation path reads observed chunk durations from `chunk_results`, estimates a future chunk count for the requested per-chunk target, and emits a copyable command. When the manifest includes per-file rows, it recommends `--strategy duration --history MANIFEST`, because that evidence can improve the next schedule.

Controls:

- `--target-seconds N`: desired maximum-ish chunk duration
- `--min-chunks N`: lower bound for the recommendation
- `--max-chunks N`: upper bound for the recommendation
- `--json PATH`: write the recommendation as JSON

## Makefile helpers

```bash
make test-recommend-chunks
make test-diff-manifests OLD=.artifacts/old.json NEW=.artifacts/new.json
```

## Trust model

Rev752 does not promise predictive runtime perfection. Chunk duration depends on host speed, cache state, random slow paths, and test ordering. It promises narrower evidence:

- aggregate all-chunks manifests can now be reused as duration history
- manifest drift can be explained without rerunning tests
- future chunk counts are derived from observed data rather than hand-waved
- recommendations say when they are using per-file history and when they are only using chunk-level durations

