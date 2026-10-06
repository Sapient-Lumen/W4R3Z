# New slice checklist

Revision: rev0028.

Use this before adding any new concrete BrowserRT slice.

## Required surfaces

Every new slice should have:

1. code surface in `src/` or `tools/`;
2. manifest task in `test/manifest.json`;
3. impact rule in `test/impact-map.json`;
4. surface inventory entry or update in `test/surface-inventory.json`;
5. validation doc in `docs/40-validation/`;
6. architecture or planning doc if it changes project meaning;
7. proof artifact under `artifacts/validation/REV####-...json` or `artifacts/audit/REV####-...json`;
8. validation-index entry if it becomes a current claim;
9. non-claims in the slice doc and receipt;
10. changelog entry.

## Required task metadata

A manifest task should name:

- `id`;
- `description`;
- `command`;
- `tiers`;
- `tags`;
- `areas`;
- `lane`;
- `parallelGroup`;
- `size`;
- `isolation`;
- `flakiness`;
- `risk`;
- `estimatedMs`;
- `timeoutMs`;
- `inputs`;
- `outputs`;
- `capabilities`;
- `cachePolicy`;
- `evidence`.

## Tier choice

Use release tier only when the slice is cheap, deterministic, and non-browser by default. Browser/CDP slices should usually be `browser` + `full`, with direct manual commands and proof artifacts.

## Non-claim pattern

Write this explicitly:

```txt
This slice proves X under Y provider with Z artifact.
It does not prove A, B, C, performance, durability, or cross-browser behavior.
```

## Before packaging

Run:

```bash
make turn-start
node tools/run_tests.mjs --tier release --changed <changed-files> --only-affected --dry-run --json artifacts/validation/REV####-AFFECTED-RUNNER-DRYRUN.json
node tools/run_tests.mjs --tier release --id <new-task-id> --jobs 1
make lint
```
