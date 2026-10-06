# Testing facility research pass 002

Revision: rev0028.

This pass looks at mature testing and build systems as design pressure for a
cloudtainer-only BrowserRT project. The research is not imported code; it is a
steal-bank of process ideas that must be implemented with local, dependency-free
surfaces.

## What belongs in BrowserRT's test facility

Bazel's test-contract posture argues that a test runner needs a defined
environment, sizing model, timeout expectations, and cacheability story. The
BrowserRT equivalent is `test/manifest.json`: every test gets an id, tier, lane,
size, isolation mode, estimated time, timeout, risk, input globs, and tags.

Playwright's sharding, parallelism, retries, and trace ideas reinforce that
browser tests need explicit worker/process management and artifacts. BrowserRT
should not jump directly to a browser megatest. The first browser harness should
be a managed local server plus a single Chromium/CDP session inside one command,
with screenshot/trace capture only for that command.

Nx affected and distributed-task ideas support a future where not every turn runs
every proof. Rev0005 adds a tiny conservative impact map so changed runtime files
select runtime/proof tests and changed harness files select harness checks.

Turborepo's cache idea becomes a local-only future: identify task inputs and
outputs well enough that repeated work can eventually be skipped or replayed
inside the cube without a remote cache.

Vitest, pytest-xdist, Jest, and Web Test Runner all underline that parallelism is
not free. Isolation, worker pools, order, random seeds, shared resources, and
browser contexts affect both reliability and runtime.

Chromium and Web Platform Tests reinforce the need for narrower, portable tests
and explicit flake handling. BrowserRT should track suspected flakes and avoid
allowing broad retries to hide genuine contract failures.

OpenTelemetry's trace/span vocabulary reinforces a core idea: test output should
be evidence. Runtime tests should leave traces that explain what happened, not
only pass/fail text.

## Rev0005 steal list

- Per-task size and isolation metadata.
- Affected-selection seed through input globs and an impact map.
- Timing history artifact and slowest-test analysis.
- Quarantine ledger, even while empty.
- Test surface inventory before browser/storage/GPU lanes exist.
- Process-start policy that refuses cross-turn daemon assumptions.
- Dry-run and plan commands before expensive execution.
- Future browser harness as a leased process within one test command.

## Non-import policy

No test framework, browser runner, cache service, or telemetry package is added.
The cube remains dependency-free. External systems supply vocabulary and warning
patterns only.
