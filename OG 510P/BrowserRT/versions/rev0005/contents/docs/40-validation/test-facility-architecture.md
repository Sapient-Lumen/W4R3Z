# Test facility architecture

Revision: rev0005.

The BrowserRT test facility is a small local scheduler for validation work. It is
not a general test framework and it deliberately avoids external dependencies.
Its job is to make future expensive tests cheap to select, clear to run, and easy
to split across turns.

## Canonical surfaces

- `test/manifest.json` defines scheduleable tasks.
- `test/impact-map.json` maps changed surfaces to conservative task ids.
- `test/surface-inventory.json` lists current and future BrowserRT test surfaces.
- `test/quarantine.json` records temporary flake quarantine entries.
- `src/test-facility.mjs` implements selection, sharding, validation, and timing helpers.
- `tools/run_tests.mjs` executes selected tasks with timeouts and parallel-group guards.
- `tools/plan_tests.mjs` explains what would run before it runs.
- `tools/validate_test_surface.mjs` validates inventory and impact surfaces.
- `tools/run_tests.mjs` also turns timing reports into slowest-test and estimate-miss evidence.
- `tools/turn_bootstrap.mjs` is the first command for a future implementation turn.

## Manifest schema pressure

Every task must declare:

- stable `id`;
- `tiers`;
- `tags`;
- `areas`;
- `lane`;
- `parallelGroup` when shared resources require serialization;
- `size`;
- `isolation`;
- `flakiness`;
- `risk`;
- `estimatedMs`;
- `timeoutMs`;
- `inputs`.

The size/isolation fields may feel excessive now. They exist so that browser,
storage, GPU, and mesh tests cannot sneak in as opaque commands later.

## Runner behavior

`tools/run_tests.mjs` supports:

- `--tier`;
- `--id`;
- `--tag`;
- `--shard i/n`;
- `--jobs auto|n`;
- `--changed`;
- `--explain`;
- `--json`;
- `--history`;
- `--budget-ms`;
- `--fail-fast`.

The runner uses bounded child-process timeouts and refuses to treat test duration
as invisible. It is intentionally simple enough to audit.

## Future architecture

When browser tests arrive, they should be added as a provider under this same
manifest, not as a separate hidden framework. A browser slice should lease its
server/browser/CDP resources, emit artifacts, and release resources before the
command exits.
