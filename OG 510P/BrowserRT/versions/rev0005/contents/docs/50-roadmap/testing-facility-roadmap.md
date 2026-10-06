# Testing facility roadmap

Revision: rev0005.

## Already present

- Manifest-driven tests.
- Tiers, ids, tags, lanes, areas, risk, size, isolation, flake status.
- Deterministic weighted sharding.
- Bounded timeouts.
- Parallel child-process execution with serial groups.
- JSON timing reports.
- Timing history.
- Affected-selection seed.
- Surface inventory.
- Empty quarantine ledger.
- Turn-start process policy.

## Next slices

1. `browser:boot-cdp`: local server plus Chromium/CDP managed inside one command.
2. `browser:worker-basic`: page launches a module Worker and returns a report.
3. `browser:opfs-async`: async OPFS write/read/cleanup smoke.
4. `browser:isolated-sab`: COOP/COEP page confirms SAB/Atomics path.
5. `browser:webgpu-smoke`: tiny compute shader with CPU fallback and non-claim.
6. `facility:last-failed`: rerun only failed task ids from the latest report.
7. `facility:cache-proof`: local input fingerprint plus skipped task artifact.
8. `facility:trace-viewer`: static viewer for BrowserRT test traces.

## Guardrail

No future capability may enter first as a demo. It enters as a manifest task with
artifacts and a timing budget.
