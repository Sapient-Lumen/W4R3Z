# Affected selection and timing

Revision: rev0005.

Rev0005 adds a conservative affected-test seed. It is intentionally simple:
changed paths are matched against task input globs and `test/impact-map.json`.

## Commands

```bash
node tools/plan_tests.mjs --changed src/browserrt.mjs 
node tools/run_tests.mjs --tier release --changed src/browserrt.mjs  --jobs auto
```

## Philosophy

Affected selection must over-select. Missing a needed test is worse than running
a few extra tasks.

## Future improvements

- file hashing;
- generated dependency graph;
- history-weighted shard bins;
- last-failed state;
- local cache of successful task outputs;
- replayable browser traces.
