# BrowserRT context pack — rev0005 (2026-05-24)

## Current orientation

BrowserRT is a browser userspace-kernel project. The current cube is still small:
it proves a Node/cloudtainer worker-agent slice and now adds a test observatory
for short, expensive cloudtainer windows.

## Learned from example datacubes

Keep reentry surfaces, receipts, manifests, validation indexes, context packs,
and explicit non-claims. Avoid duplicate ledgers and stale proof names. Rev0005
extends that lesson to tests: future proof cost must not become one opaque
command.

## Runtime north star

A future BrowserRT coordinates workers, memory ownership, bounded queues, storage,
GPU, rendering/media lanes, telemetry, replay, and same-origin mesh coordination.
The current code is not that runtime yet; it is a seed that must remain coherent
under validation.

## Frozen design pressures

- Control plane and data plane stay separate.
- Memory ownership is explicit.
- Queues are bounded.
- Cancellation, deadlines, and trace evidence matter.
- Capability tiers are progressive, not separate product lines.
- Browser-only features must have fallbacks or explicit non-claims.
- Tests must be decomposed before they become expensive.

## Testing facility posture

Rev0005 adds schema-2 manifest metadata, affected selection, surface inventory,
quarantine ledger, timing history, and timing analysis. The canonical surfaces are
`test/manifest.json`, `test/impact-map.json`, `test/surface-inventory.json`,
`test/quarantine.json`, `src/test-facility.mjs`, `tools/run_tests.mjs`,
`tools/plan_tests.mjs`, `tools/validate_test_surface.mjs`,
`tools/analyze_tests.mjs`, and `tools/turn_bootstrap.mjs`.

Default future first command after extraction:

```bash
make turn-start
```

The test runner supports tiers, ids, tags, deterministic weighted shards,
affected selection, bounded timeouts, per-task timing, capped auto parallelism,
dry-run plans, timing history, and JSON reports.

## Must-read set

1. `START_HERE.md`
2. `REVISION-RECEIPT.json`
3. `docs/40-validation/cloudtainer-test-economics.md`
4. `docs/40-validation/test-facility-architecture.md`
5. `docs/40-validation/process-start-policy.md`
6. `docs/40-validation/affected-selection-and-timing.md`
7. `docs/40-validation/browser-harness-plan.md`
8. `test/manifest.json`
9. `test/impact-map.json`
10. `test/surface-inventory.json`
11. `tools/run_tests.mjs`
12. `tools/plan_tests.mjs`
13. `tools/turn_bootstrap.mjs`
14. `docs/60-proof/phase-zero-executable-proof.md`
15. `src/browserrt.mjs`

## Commands

```bash
make turn-start
node tools/run_tests.mjs --list --tier release
node tools/plan_tests.mjs --tier release
node tools/plan_tests.mjs --tier release --changed src/browserrt.mjs --only-affected
node tools/run_tests.mjs --tier release --changed src/browserrt.mjs --only-affected
make proof
make lint
make package-release STAMP=YYYY.MM.DD.HH.MM SLUG=<slug>
```

## Current non-claims

- Not production-ready.
- Not browser-conformance-proven.
- Not performance-proven.
- Not a full scheduler.
- Not a browser CDP harness.
- Not an OPFS/SAB/WebGPU implementation.
- Not evidence that long-lived background processes survive across turns.
- Not a remote-cache or remote-execution system.
